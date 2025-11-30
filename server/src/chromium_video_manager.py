import asyncio
import json
import logging
import os
import signal
import subprocess
import time
from collections import deque
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from fastapi import WebSocket

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from src.video_compressor import VideoCompressor


class PlayerState(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    NO_MEDIA = "no_media"


class ChromiumVideoManager:
    """
    Video manager that uses Chromium browser to play videos via HTML5
    Maintains the same interface as VLC-based VideoManager for compatibility
    """

    def __init__(self):
        self.upload_dir = Path("uploaded_videos")
        self.compressed_dir = self.upload_dir / "compressed"
        self.upload_dir.mkdir(exist_ok=True)
        self.compressed_dir.mkdir(exist_ok=True)
        self.last_played_file = Path("last_played.json")
        self.error_count = 0
        self.max_retry_attempts = 3
        self.retry_delay = 1
        self.current_video = None
        self.is_playing = False
        self.is_paused = False

        # Chromium process management
        self.chromium_process = None
        self.display = ":0"  # X display

        # WebSocket connections for controlling the video player
        self.ws_connections = set()

        # Command queue for handling commands before WebSocket is ready
        self.command_queue = deque()
        self.queue_processing = False

        # Player status from browser
        self.player_status = {
            "current_time": 0,
            "duration": 0,
            "volume": 100,
            "ready_state": 0
        }

        self.compressor = VideoCompressor(target_resolution=240, target_fps=10)

        # Start Chromium in kiosk mode
        self.start_chromium()

        # Load last played video
        self.load_last_played()

    def start_chromium(self):
        """Start Chromium browser in kiosk mode"""
        try:
            # Kill any existing Chromium instances
            self.stop_chromium()

            # Get the server host and port from environment or use defaults
            host = os.getenv("SERVER_HOST", "localhost")
            port = os.getenv("SERVER_PORT", "8000")

            # URL to the HTML video player
            player_url = f"http://{host}:{port}/player"

            chromium_args = [
                "chromium",
                "--kiosk",  # Fullscreen kiosk mode
                "--noerrdialogs",  # No error dialogs
                "--disable-infobars",  # No info bars
                "--no-first-run",  # Skip first run wizards
                "--disable-session-crashed-bubble",  # No crash bubble
                "--disable-features=TranslateUI",  # Disable translate
                "--disable-notifications",  # No notifications
                "--autoplay-policy=no-user-gesture-required",  # Allow autoplay
                "--start-fullscreen",  # Start in fullscreen
                "--window-position=0,0",  # Position at top-left
                "--disable-pinch",  # Disable pinch zoom
                "--overscroll-history-navigation=0",  # Disable swipe navigation
                "--enable-features=VaapiVideoDecoder",  # Hardware acceleration
                "--use-gl=egl",  # Use EGL for hardware acceleration
                f"--display={self.display}",  # X display
                player_url
            ]

            # Set environment for hardware acceleration
            env = os.environ.copy()
            env["DISPLAY"] = self.display

            self.chromium_process = subprocess.Popen(
                chromium_args,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )

            logger.info(f"Chromium started in kiosk mode (PID: {self.chromium_process.pid})")

            # Wait a bit for Chromium to start
            time.sleep(3)

        except Exception as e:
            logger.error(f"Failed to start Chromium: {e}")
            raise RuntimeError(f"Failed to initialize Chromium browser: {e}")

    def stop_chromium(self):
        """Stop Chromium browser"""
        try:
            # Kill our process if it exists
            if self.chromium_process:
                try:
                    os.killpg(os.getpgid(self.chromium_process.pid), signal.SIGTERM)
                    self.chromium_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.chromium_process.pid), signal.SIGKILL)
                except Exception as e:
                    logger.warning(f"Error killing Chromium process: {e}")

                self.chromium_process = None

            # Also kill any stray chromium processes
            subprocess.run(
                ["pkill", "-9", "chromium"],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )

            logger.info("Chromium stopped")

        except Exception as e:
            logger.error(f"Error stopping Chromium: {e}")

    async def register_websocket(self, websocket: WebSocket):
        """Register a WebSocket connection from the video player"""
        self.ws_connections.add(websocket)
        logger.info("WebSocket connection registered")

        # Process any queued commands
        if self.command_queue:
            logger.info(f"Processing {len(self.command_queue)} queued commands")
            await self._process_command_queue()

    async def unregister_websocket(self, websocket: WebSocket):
        """Unregister a WebSocket connection"""
        self.ws_connections.discard(websocket)
        logger.info("WebSocket connection unregistered")

    async def send_command(self, command: str, data: dict = None):
        """Send a command to the video player via WebSocket"""
        message = {
            "command": command,
            "data": data or {}
        }

        if not self.ws_connections:
            # Queue the command if no WebSocket connection is available
            logger.warning(f"No WebSocket connections available, queuing command: {command}")
            self.command_queue.append(message)
            return False

        disconnected = set()
        for ws in self.ws_connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send command via WebSocket: {e}")
                disconnected.add(ws)

        # Clean up disconnected websockets
        for ws in disconnected:
            self.ws_connections.discard(ws)

        return len(self.ws_connections) > 0

    async def _process_command_queue(self):
        """Process all queued commands"""
        if self.queue_processing:
            return  # Prevent duplicate processing

        self.queue_processing = True
        try:
            while self.command_queue and self.ws_connections:
                message = self.command_queue.popleft()
                logger.info(f"Sending queued command: {message['command']}")

                disconnected = set()
                for ws in self.ws_connections:
                    try:
                        await ws.send_json(message)
                    except Exception as e:
                        logger.error(f"Failed to send queued command: {e}")
                        disconnected.add(ws)

                # Clean up disconnected websockets
                for ws in disconnected:
                    self.ws_connections.discard(ws)

                # Small delay between commands
                await asyncio.sleep(0.1)
        finally:
            self.queue_processing = False

    def validate_video(self, video_path: str) -> bool:
        """Validate video file before playing"""
        try:
            # Check if file exists
            path = Path(video_path)
            if not path.exists():
                logger.error(f"Video file not found: {video_path}")
                return False

            # Check if file is readable
            with open(video_path, "rb") as f:
                # Read first few bytes to verify it's accessible
                f.read(1024)

            # Check file size
            if path.stat().st_size == 0:
                logger.error(f"Video file is empty: {video_path}")
                return False

            logger.info(f"Video validation successful: {video_path}")
            return True

        except Exception as e:
            logger.error(f"Video validation failed: {e}")
            return False

    def load_video(self, video_path: str):
        """Load a video for playback"""
        if not Path(video_path).is_file():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not self.validate_video(video_path):
            raise ValueError("Invalid video file")

        try:
            # Convert to URL path that browser can access
            video_filename = Path(video_path).name
            video_url = f"/videos/{video_filename}"

            # Send load command to browser
            asyncio.create_task(self.send_command("load", {"path": video_url}))

            self.error_count = 0
            self.current_video = video_path
            self.is_paused = False
            self.save_last_played()
            logger.info(f"Video loaded successfully: {video_path}")

        except Exception as e:
            logger.error(f"Failed to load video: {e}")
            self.error_count += 1
            raise

    def play(self):
        """Play video with error recovery"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            asyncio.create_task(self.send_command("play"))
            self.is_playing = True
            self.is_paused = False
            logger.info("Video playback started")

        except Exception as e:
            logger.error(f"Playback error: {e}")
            if self.error_count < self.max_retry_attempts:
                logger.info("Attempting playback recovery...")
                self.error_count += 1
                time.sleep(self.retry_delay)
                try:
                    # Reload video and try again
                    self.load_video(self.current_video)
                    asyncio.create_task(self.send_command("play"))
                    self.is_playing = True
                    self.is_paused = False
                    logger.info("Playback recovery successful")
                except Exception as retry_error:
                    logger.error(f"Recovery failed: {retry_error}")
                    raise
            else:
                raise RuntimeError("Max retry attempts reached")

    def pause(self):
        """Pause video with state verification"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            asyncio.create_task(self.send_command("pause"))
            self.is_playing = False
            self.is_paused = True
            logger.info("Video paused successfully")

        except Exception as e:
            logger.error(f"Failed to pause video: {e}")
            raise

    def stop(self):
        """Stop video with cleanup"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            asyncio.create_task(self.send_command("stop"))
            self.is_playing = False
            self.is_paused = False
            self.error_count = 0  # Reset error count
            logger.info("Video stopped successfully")

        except Exception as e:
            logger.error(f"Failed to stop video: {e}")
            raise

    def get_status(self) -> Dict:
        """Get comprehensive player status"""
        if not self.current_video:
            return {
                "current_video": None,
                "status": PlayerState.NO_MEDIA,
                "is_playing": False,
                "is_looping": True,
                "error_count": self.error_count,
                "volume": 100,
            }

        try:
            # Determine status based on state
            if self.is_playing:
                status = PlayerState.PLAYING
            elif self.is_paused:
                status = PlayerState.PAUSED
            else:
                status = PlayerState.STOPPED

            result = {
                "current_video": Path(self.current_video).name,
                "status": status,
                "is_playing": self.is_playing,
                "is_looping": True,
                "error_count": self.error_count,
                "volume": self.player_status.get("volume", 100),
            }

            # Add position info if playing
            if self.is_playing:
                result["position"] = (
                    self.player_status.get("current_time", 0) /
                    max(self.player_status.get("duration", 1), 1)
                )
                result["time"] = self.player_status.get("current_time", 0) * 1000  # Convert to ms

            return result

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"status": PlayerState.ERROR, "error": str(e)}

    def update_player_status(self, status_data: dict):
        """Update player status from WebSocket message"""
        self.player_status.update(status_data)

        # Update our internal state based on browser feedback
        self.is_playing = status_data.get("is_playing", False)
        self.is_paused = status_data.get("is_paused", False)

    def load_last_played(self):
        """Load and play the last played video on startup"""
        try:
            if self.last_played_file.exists():
                with open(self.last_played_file, "r") as f:
                    data = json.load(f)
                    if "last_video" in data:
                        video_path = self.upload_dir / data["last_video"]
                        if video_path.exists():
                            # Wait a bit for Chromium to be ready
                            time.sleep(2)
                            self.load_video(str(video_path))
                            self.play()
                            logger.info(
                                f"Loaded and started playing last video: {data['last_video']}"
                            )
        except Exception as e:
            logger.error(f"Error loading last played video: {e}")

    def save_last_played(self):
        """Save the current video as last played"""
        try:
            with open(self.last_played_file, "w") as f:
                json.dump({"last_video": Path(self.current_video).name}, f)
            logger.info(f"Saved last played video: {Path(self.current_video).name}")
        except Exception as e:
            logger.error(f"Error saving last played video: {e}")

    def __del__(self):
        """Cleanup on deletion"""
        self.stop_chromium()


# Create global video manager instance
video_manager = ChromiumVideoManager()
