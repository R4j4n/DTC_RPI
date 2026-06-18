import hashlib
import shutil
import subprocess
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from config import PROCESSED_DIR

# Cracked-screen calibration: right/bottom edge of the 1920x1080 panel is
# unusable, so the source is scaled down and pinned to the top-left corner,
# padded with black on the right/bottom to land in the visible region.
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
SAFE_WIDTH = 1410
SAFE_HEIGHT = 1050

SCALE_FILTER = (
    f"scale={SAFE_WIDTH}:{SAFE_HEIGHT}:force_original_aspect_ratio=decrease,"
    f"pad={TARGET_WIDTH}:{TARGET_HEIGHT}:0:0:black"
)

# A double-clicked .app launches without the user's shell PATH, so plain
# "ffmpeg" can resolve to nothing even though it works fine from a terminal.
_FFMPEG_FALLBACKS = ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]


def _ffmpeg_binary() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in _FFMPEG_FALLBACKS:
        if Path(candidate).exists():
            return candidate
    raise RuntimeError(
        "ffmpeg not found. Install it with 'brew install ffmpeg' or "
        "ensure it is on PATH."
    )


def _cache_key(src: Path) -> str:
    stat = src.stat()
    raw = f"{src.resolve()}|{stat.st_size}|{stat.st_mtime}"
    return hashlib.sha1(raw.encode()).hexdigest()


def processed_path_for(src: Path) -> Path:
    return PROCESSED_DIR / f"{_cache_key(src)}.mp4"


def process_video(src_path: str) -> Path:
    src = Path(src_path)
    dest = processed_path_for(src)
    if dest.exists():
        return dest

    cmd = [
        _ffmpeg_binary(),
        "-i", str(src),
        "-vf", SCALE_FILTER,
        "-c:a", "copy",
        "-y",
        str(dest),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-2000:]}")
    return dest


class ProcessWorker(QThread):
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, src_path: str):
        super().__init__()
        self.src_path = src_path

    def run(self):
        try:
            dest = process_video(self.src_path)
            self.finished_ok.emit(str(dest))
        except Exception as exc:
            self.failed.emit(str(exc))
