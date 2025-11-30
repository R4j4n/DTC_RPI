"""
Configuration settings for DTC_RPI Server
"""
from enum import Enum


class VideoPlayerMode(str, Enum):
    """Video player mode options"""
    VLC = "vlc"  # Traditional VLC player
    WEB = "web"  # Browser-based HTML5 player with wristband schedule


class Config:
    """Application configuration"""

    # Video Player Configuration
    # Set to VideoPlayerMode.WEB to use the new browser-based player with wristband display
    # Set to VideoPlayerMode.VLC to use traditional VLC player
    VIDEO_PLAYER_MODE = VideoPlayerMode.WEB

    # Server Configuration
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000

    # Authentication
    USE_AUTHENTICATION = True

    # Kiosk Configuration
    KIOSK_AUTO_LAUNCH = True  # Auto-launch kiosk on server start (web mode only)

    # Video Storage
    VIDEO_UPLOAD_DIR = "uploaded_videos"
    VIDEO_COMPRESSED_DIR = "uploaded_videos/compressed"

    # Schedule
    SCHEDULE_FILE = "schedule.json"

    # Wristband Schedule
    WRISTBAND_SCHEDULE_UPDATE_INTERVAL = 1  # seconds


config = Config()
