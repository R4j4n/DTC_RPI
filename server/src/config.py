"""
Configuration management for DTC_RPI Server.
Centralizes all configurable parameters with environment variable support.
"""

import os
from pathlib import Path
from typing import Optional


class ServerConfig:
    """Server configuration with environment variable support"""

    # Server Settings
    HOST: str = os.getenv("DTC_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("DTC_PORT", "8000"))

    # Directory Settings
    UPLOAD_DIR: Path = Path(os.getenv("DTC_UPLOAD_DIR", "uploaded_videos"))
    COMPRESSED_DIR: Path = UPLOAD_DIR / "compressed"

    # Video Player Settings
    MAX_RETRY_ATTEMPTS: int = int(os.getenv("DTC_MAX_RETRY", "3"))
    RETRY_DELAY: float = float(os.getenv("DTC_RETRY_DELAY", "1.0"))
    VLC_VOLUME: int = int(os.getenv("DTC_VLC_VOLUME", "100"))

    # Video Compression Settings
    COMPRESS_RESOLUTION: int = int(os.getenv("DTC_COMPRESS_RES", "240"))
    COMPRESS_FPS: int = int(os.getenv("DTC_COMPRESS_FPS", "10"))
    COMPRESS_CRF: int = int(os.getenv("DTC_COMPRESS_CRF", "28"))

    # HDMI/CEC Settings
    CEC_TIMEOUT: int = int(os.getenv("DTC_CEC_TIMEOUT", "10"))
    CEC_RETRY_COUNT: int = int(os.getenv("DTC_CEC_RETRY", "3"))
    TV_READY_WAIT: int = int(os.getenv("DTC_TV_WAIT", "3"))
    HDMI_MIN_PORT: int = int(os.getenv("DTC_HDMI_MIN", "1"))
    HDMI_MAX_PORT: int = int(os.getenv("DTC_HDMI_MAX", "4"))

    # Scheduler Settings
    SCHEDULER_CHECK_INTERVAL: int = int(os.getenv("DTC_SCHEDULER_INTERVAL", "30"))

    # File Paths
    SCHEDULE_FILE: Path = Path(os.getenv("DTC_SCHEDULE_FILE", "schedule.json"))
    LAST_PLAYED_FILE: Path = Path(os.getenv("DTC_LAST_PLAYED_FILE", "last_played.json"))
    HDMI_DEVICES_FILE: Path = Path(os.getenv("DTC_HDMI_DEVICES_FILE", "hdmi_devices.json"))
    CURRENT_INPUT_FILE: Path = Path(os.getenv("DTC_CURRENT_INPUT_FILE", "current_input.json"))

    # Authentication Settings
    AUTH_DIR: Path = Path(os.getenv("DTC_AUTH_DIR", "auth"))
    AUTH_FILE: Path = AUTH_DIR / "auth.txt"
    KEY_FILE: Path = AUTH_DIR / "key.txt"

    # Logging Settings
    LOG_LEVEL: str = os.getenv("DTC_LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("DTC_LOG_FILE", None)

    # Service Discovery Settings
    ZEROCONF_SERVICE_NAME: str = os.getenv("DTC_SERVICE_NAME", "_pivideo._tcp.local.")
    ZEROCONF_TIMEOUT: int = int(os.getenv("DTC_ZEROCONF_TIMEOUT", "60"))

    # WiFi Management Settings
    WIFI_CONFIG_FILE: Path = Path(os.getenv("DTC_WIFI_CONFIG", "wifi_config.json"))
    WIFI_CHECK_INTERVAL: int = int(os.getenv("DTC_WIFI_CHECK_INTERVAL", "30"))
    WIFI_RECONNECT_TIMEOUT: int = int(os.getenv("DTC_WIFI_RECONNECT_TIMEOUT", "120"))
    WIFI_MONITORING_ENABLED: bool = os.getenv("DTC_WIFI_MONITORING", "true").lower() == "true"

    # Allowed Video Extensions
    ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".avi", ".mkv", ".mov"}

    @classmethod
    def init_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.COMPRESSED_DIR.mkdir(exist_ok=True)
        cls.AUTH_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_config_summary(cls) -> dict:
        """Get a summary of current configuration (for debugging)"""
        return {
            "server": {"host": cls.HOST, "port": cls.PORT},
            "video": {
                "max_retry": cls.MAX_RETRY_ATTEMPTS,
                "retry_delay": cls.RETRY_DELAY,
                "volume": cls.VLC_VOLUME,
            },
            "compression": {
                "resolution": cls.COMPRESS_RESOLUTION,
                "fps": cls.COMPRESS_FPS,
                "crf": cls.COMPRESS_CRF,
            },
            "cec": {
                "timeout": cls.CEC_TIMEOUT,
                "retry_count": cls.CEC_RETRY_COUNT,
                "tv_ready_wait": cls.TV_READY_WAIT,
            },
            "scheduler": {"check_interval": cls.SCHEDULER_CHECK_INTERVAL},
        }


# Initialize directories on module import
ServerConfig.init_directories()
