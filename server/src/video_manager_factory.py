"""
Video Manager Factory

This module provides a factory to switch between VLC and Chromium video managers
based on configuration. This allows easy switching between the two implementations.
"""

import os
from enum import Enum


class VideoBackend(str, Enum):
    VLC = "vlc"
    CHROMIUM = "chromium"


def get_video_manager():
    """
    Factory function to get the appropriate video manager based on environment
    or configuration.

    Returns:
        VideoManager instance (either VLC or Chromium based)
    """
    # Check environment variable
    backend = os.getenv("VIDEO_BACKEND", "chromium").lower()

    if backend == VideoBackend.VLC:
        try:
            from src.video_manager import video_manager
            print("Using VLC video backend")
            return video_manager
        except ImportError as e:
            print(f"Failed to import VLC video manager: {e}")
            print("Falling back to Chromium video manager")
            from src.chromium_video_manager import video_manager
            return video_manager

    elif backend == VideoBackend.CHROMIUM:
        try:
            from src.chromium_video_manager import video_manager
            print("Using Chromium video backend")
            return video_manager
        except ImportError as e:
            print(f"Failed to import Chromium video manager: {e}")
            print("Falling back to VLC video manager")
            from src.video_manager import video_manager
            return video_manager

    else:
        raise ValueError(f"Unknown video backend: {backend}. Use 'vlc' or 'chromium'")


# Export for convenience
__all__ = ["get_video_manager", "VideoBackend"]
