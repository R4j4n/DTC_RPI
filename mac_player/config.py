import json
from pathlib import Path

APP_DIR = Path.home() / ".dtc_mac_player"
CONFIG_PATH = APP_DIR / "config.json"
PROCESSED_DIR = APP_DIR / "processed"

DEFAULTS = {
    "video_path": None,
    "processed_path": None,
    "schedule_enabled": True,
    "weekday_start": "08:00",
    "weekday_end": "20:00",
    "weekend_start": "08:00",
    "weekend_end": "22:00",
}


def load():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text())
        return {**DEFAULTS, **data}
    return dict(DEFAULTS)


def save(cfg):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
