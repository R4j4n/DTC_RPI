"""
Web-based Video Manager
Replaces VLC with browser-based HTML5 video playback
"""
import json
import logging
import subprocess
import signal
import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Export logger for compatibility with video_manager router
__all__ = ['WebVideoManager', 'web_video_manager', 'PlayerState', 'logger']


class PlayerState(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    NO_MEDIA = "no_media"


class WebVideoManager:
    """
    Manages video playback through web browser in kiosk mode
    Compatible with existing VideoManager API
    """

    def __init__(self):
        self.upload_dir = Path("uploaded_videos")
        self.compressed_dir = self.upload_dir / "compressed"
        self.upload_dir.mkdir(exist_ok=True)
        self.compressed_dir.mkdir(exist_ok=True)
        self.last_played_file = Path("last_played.json")
        self.current_video = None
        self.is_playing = False
        self.kiosk_process = None

        self.load_last_played()
        logger.info("Web Video Manager initialized")

    def load_video(self, video_path: str):
        """Load a video (just updates the state, browser will fetch it)"""
        if not Path(video_path).is_file():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        self.current_video = video_path
        self.save_last_played()
        logger.info(f"Video loaded: {video_path}")

    def play(self):
        """Start video playback"""
        if not self.current_video:
            raise ValueError("No video loaded")

        self.is_playing = True
        logger.info("Video playback started (web mode)")

    def pause(self):
        """Pause video playback"""
        if not self.current_video:
            raise ValueError("No video loaded")

        self.is_playing = False
        logger.info("Video paused (web mode)")

    def stop(self):
        """Stop video playback"""
        if not self.current_video:
            raise ValueError("No video loaded")

        self.is_playing = False
        logger.info("Video stopped (web mode)")

    def get_status(self) -> Dict:
        """Get player status"""
        if not self.current_video:
            return {
                "current_video": None,
                "status": PlayerState.NO_MEDIA,
                "is_playing": False,
                "is_looping": True,
                "error_count": 0,
                "volume": 100,
            }

        status = PlayerState.PLAYING if self.is_playing else PlayerState.STOPPED

        return {
            "current_video": Path(self.current_video).name,
            "status": status,
            "is_playing": self.is_playing,
            "is_looping": True,
            "error_count": 0,
            "volume": 100,
        }

    def load_last_played(self):
        """Load the last played video on startup"""
        try:
            if self.last_played_file.exists():
                with open(self.last_played_file, "r") as f:
                    data = json.load(f)
                    if "last_video" in data:
                        video_path = self.upload_dir / data["last_video"]
                        if video_path.exists():
                            self.load_video(str(video_path))
                            self.play()
                            logger.info(f"Loaded last video: {data['last_video']}")
        except Exception as e:
            logger.error(f"Error loading last played video: {e}")

    def save_last_played(self):
        """Save the currently playing video"""
        try:
            with open(self.last_played_file, "w") as f:
                json.dump({"last_video": Path(self.current_video).name}, f)
            logger.info(f"Saved last played video: {Path(self.current_video).name}")
        except Exception as e:
            logger.error(f"Error saving last played video: {e}")

    def launch_kiosk(self):
        """Launch the kiosk display in Chromium"""
        try:
            # Kill any existing Chromium processes
            subprocess.run(["pkill", "-f", "chromium"], check=False)

            # Launch kiosk mode
            script_path = Path(__file__).parent.parent / "launch_kiosk.sh"
            if script_path.exists():
                self.kiosk_process = subprocess.Popen(
                    [str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                logger.info("Kiosk display launched")
            else:
                logger.error(f"Kiosk launch script not found: {script_path}")
        except Exception as e:
            logger.error(f"Failed to launch kiosk: {e}")

    def close_kiosk(self):
        """Close the kiosk display"""
        try:
            if self.kiosk_process:
                self.kiosk_process.terminate()
                self.kiosk_process.wait(timeout=5)
                self.kiosk_process = None

            # Fallback: kill Chromium
            subprocess.run(["pkill", "-f", "chromium"], check=False)
            logger.info("Kiosk display closed")
        except Exception as e:
            logger.error(f"Failed to close kiosk: {e}")


# Create global web video manager instance
web_video_manager = WebVideoManager()
