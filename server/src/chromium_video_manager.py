import json
import logging
import subprocess
import time
import signal
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

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
    Video manager that uses Chromium browser to display videos in an HTML div.
    Compatible with Raspberry Pi OS Lite 64-bit.
    """

    def __init__(self, server_port: int = 8000):
        self.upload_dir = Path("uploaded_videos")
        self.compressed_dir = self.upload_dir / "compressed"
        self.upload_dir.mkdir(exist_ok=True)
        self.compressed_dir.mkdir(exist_ok=True)
        self.last_played_file = Path("last_played.json")
        self.state_file = Path("player_state.json")

        self.error_count = 0
        self.max_retry_attempts = 3
        self.retry_delay = 1
        self.current_video = None
        self.is_playing = False
        self.is_paused = False
        self.chromium_process: Optional[subprocess.Popen] = None
        self.server_port = server_port

        self.compressor = VideoCompressor(target_resolution=240, target_fps=10)

        # Initialize player state
        self.load_last_played()

        logger.info("Chromium Video Manager initialized")

    def _get_chromium_command(self) -> list:
        """
        Get the Chromium command for Raspberry Pi OS Lite.
        Returns command as a list for subprocess.
        """
        player_url = f"http://localhost:{self.server_port}/player"

        # Chromium command for kiosk mode on Raspberry Pi
        # Using 'chromium' (standard on Raspberry Pi OS)
        command = [
            "chromium",
            "--kiosk",  # Fullscreen kiosk mode
            "--noerrdialogs",  # Suppress error dialogs
            "--disable-infobars",  # Disable info bars
            "--no-first-run",  # Skip first run wizards
            "--disable-session-crashed-bubble",  # Disable crash bubble
            "--disable-features=TranslateUI",  # Disable translate
            "--disable-component-update",  # Disable component updates
            "--autoplay-policy=no-user-gesture-required",  # Allow autoplay
            "--start-fullscreen",  # Start in fullscreen
            "--window-position=0,0",  # Position at top-left
            "--disable-gpu",  # Disable GPU acceleration (safer for headless)
            "--no-sandbox",  # Required for some Raspberry Pi setups
            player_url
        ]

        return command

    def _start_chromium(self):
        """Start Chromium browser in kiosk mode"""
        if self.chromium_process and self.chromium_process.poll() is None:
            logger.info("Chromium is already running")
            return

        try:
            # Set DISPLAY environment variable for X11
            env = {
                "DISPLAY": ":0",
                "XAUTHORITY": "/home/pi/.Xauthority"  # Adjust if different user
            }

            command = self._get_chromium_command()
            logger.info(f"Starting Chromium with command: {' '.join(command)}")

            self.chromium_process = subprocess.Popen(
                command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
            )

            # Wait a moment for Chromium to start
            time.sleep(2)

            if self.chromium_process.poll() is None:
                logger.info(f"Chromium started successfully (PID: {self.chromium_process.pid})")
            else:
                raise RuntimeError("Chromium process terminated immediately")

        except Exception as e:
            logger.error(f"Failed to start Chromium: {e}")
            raise RuntimeError(f"Failed to start Chromium browser: {e}")

    def _stop_chromium(self):
        """Stop Chromium browser"""
        if self.chromium_process and self.chromium_process.poll() is None:
            try:
                logger.info("Stopping Chromium...")
                self.chromium_process.terminate()

                # Wait for graceful shutdown
                try:
                    self.chromium_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Chromium didn't terminate gracefully, forcing...")
                    self.chromium_process.kill()
                    self.chromium_process.wait()

                logger.info("Chromium stopped successfully")
                self.chromium_process = None

            except Exception as e:
                logger.error(f"Error stopping Chromium: {e}")

    def _save_player_state(self):
        """Save current player state to file for HTML player to read"""
        try:
            state = {
                "video_path": f"/videos/{Path(self.current_video).name}" if self.current_video else None,
                "should_play": self.is_playing and not self.is_paused,
                "muted": False,
                "timestamp": time.time()
            }

            with open(self.state_file, "w") as f:
                json.dump(state, f)

            logger.debug(f"Player state saved: {state}")

        except Exception as e:
            logger.error(f"Failed to save player state: {e}")

    def get_player_state(self) -> Dict:
        """Get current player state for the HTML player to consume"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read player state: {e}")

        # Return default state
        return {
            "video_path": None,
            "should_play": False,
            "muted": False,
            "timestamp": time.time()
        }

    def validate_video(self, video_path: str) -> bool:
        """Validate video file before playing"""
        try:
            path = Path(video_path)

            if not path.exists():
                logger.error(f"Video file not found: {video_path}")
                return False

            if not path.is_file():
                logger.error(f"Path is not a file: {video_path}")
                return False

            # Check file size
            if path.stat().st_size == 0:
                logger.error(f"Video file is empty: {video_path}")
                return False

            # Check file extension
            allowed_extensions = {".mp4", ".avi", ".mkv", ".mov", ".webm"}
            if path.suffix.lower() not in allowed_extensions:
                logger.error(f"Unsupported video format: {path.suffix}")
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
            self.error_count = 0
            self.current_video = video_path
            self.is_paused = False

            # Update player state
            self._save_player_state()

            # Save as last played
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
            # Start Chromium if not already running
            self._start_chromium()

            self.is_playing = True
            self.is_paused = False

            # Update player state
            self._save_player_state()

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
                    self._start_chromium()
                    self.is_playing = True
                    self.is_paused = False
                    self._save_player_state()
                    logger.info("Playback recovery successful")
                except Exception as retry_error:
                    logger.error(f"Recovery failed: {retry_error}")
                    raise
            else:
                raise RuntimeError("Max retry attempts reached")

    def pause(self):
        """Pause video playback"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            self.is_paused = True
            self._save_player_state()

            logger.info("Video paused successfully")

        except Exception as e:
            logger.error(f"Failed to pause video: {e}")
            raise

    def stop(self):
        """Stop video playback and close browser"""
        try:
            self.is_playing = False
            self.is_paused = False
            self._save_player_state()

            # Stop Chromium browser
            self._stop_chromium()

            self.error_count = 0
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
            # Determine player state
            if self.is_paused:
                status = PlayerState.PAUSED
            elif self.is_playing:
                status = PlayerState.PLAYING
            else:
                status = PlayerState.STOPPED

            return {
                "current_video": Path(self.current_video).name,
                "status": status,
                "is_playing": self.is_playing,
                "is_looping": True,
                "error_count": self.error_count,
                "volume": 100,
                "browser_running": self.chromium_process is not None and self.chromium_process.poll() is None
            }

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"status": PlayerState.ERROR, "error": str(e)}

    def load_last_played(self):
        """Load and play the last played video"""
        try:
            if self.last_played_file.exists():
                with open(self.last_played_file, "r") as f:
                    data = json.load(f)
                    if "last_video" in data:
                        video_path = self.upload_dir / data["last_video"]
                        if video_path.exists():
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

    def cleanup(self):
        """Cleanup resources on shutdown"""
        logger.info("Cleaning up Chromium Video Manager...")
        self._stop_chromium()


# Create global video manager instance
video_manager = ChromiumVideoManager()
