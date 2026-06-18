# DTC Mac Player

Two PyQt6 apps for macOS, packaged into standalone `.app` bundles with PyInstaller:

- **DTC Mac Player** (`main.py`) — VLC-based video player. Loops one video fullscreen in the 1410x1050 safe zone (the cracked screen's right/bottom edge is avoided), with a schedule (Mon-Thu / Fri-Sun on/off windows) and an on-screen control panel placed in the dead zone.
- **DTC Chrome Kiosk** (`web_window.py`) — embedded-Chromium kiosk. Shows one site in the same 1410x1050 safe zone, no window chrome at all (no close/minimize buttons), with a Quit button in the dead zone. Login/cookies persist across launches.

Both share the same safe-zone geometry from `ffmpeg_processor.py` (`SAFE_WIDTH`/`SAFE_HEIGHT` = 1410x1050, calibrated against a 1920x1080 target screen).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (`brew install uv`)
- [VLC.app](https://www.videolan.org/vlc/) installed in `/Applications` — `python-vlc` loads VLC's `libvlc` at runtime, it is not bundled into the app. Only needed for the player, not the Chrome kiosk.

## Setup

```bash
cd mac_player
uv sync
```

Creates `.venv` and installs everything from `pyproject.toml` / `uv.lock`, including `PyQt6-WebEngine` (Chrome kiosk) and `pyinstaller` (both builds).

## Run from source

```bash
uv run python main.py            # video player
uv run python web_window.py      # Chrome kiosk
```

---

## DTC Mac Player — build

### Icon

`AppIcon.icns` is already in the repo (a generated placeholder: dark rounded square + white play triangle) and is referenced by `DTC Mac Player.spec`. To swap it for a different icon, replace `AppIcon.icns` with your own `.icns` file (same name) and rebuild — or regenerate the placeholder:

```bash
mkdir -p AppIcon.iconset
uv run --with pillow python - <<'EOF'
from PIL import Image, ImageDraw

SIZE = 1024
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
margin = 60
draw.rounded_rectangle([margin, margin, SIZE - margin, SIZE - margin], radius=180, fill=(28, 28, 30, 255))
cx, cy = SIZE / 2, SIZE / 2
tri_w, tri_h = 320, 380
points = [
    (cx - tri_w * 0.35, cy - tri_h / 2),
    (cx - tri_w * 0.35, cy + tri_h / 2),
    (cx + tri_w * 0.65, cy),
]
draw.polygon(points, fill=(255, 255, 255, 255))

mapping = [
    (16, "icon_16x16.png"), (32, "icon_16x16@2x.png"), (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"), (128, "icon_128x128.png"), (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"), (512, "icon_256x256@2x.png"), (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
]
for size, name in mapping:
    img.resize((size, size), Image.LANCZOS).save(f"AppIcon.iconset/{name}")
EOF
iconutil -c icns AppIcon.iconset -o AppIcon.icns
```

To use a custom source image instead, drop it in as `AppIcon.iconset/icon_512x512@2x.png` (1024x1024 PNG) and run only the `iconutil` line — or just hand any square PNG/JPG to an icon-generator tool and save the result as `AppIcon.icns`.

### Build

```bash
uv run pyinstaller --clean --noconfirm "DTC Mac Player.spec"
```

Output: `dist/DTC Mac Player.app`.

If you ever need to regenerate the spec from scratch (e.g. after deleting it):

```bash
uv run pyinstaller --windowed --name "DTC Mac Player" \
  --osx-bundle-identifier com.dtc.macplayer \
  --icon AppIcon.icns --noconfirm main.py
```

---

## DTC Chrome Kiosk — build

### Icon

`ChromeIcon.icns` is Google Chrome's own icon, copied from the installed app (one-time, only needed if the file is missing or you want to refresh it):

```bash
cp "/Applications/Google Chrome.app/Contents/Resources/app.icns" ChromeIcon.icns
```

### Build

```bash
uv run pyinstaller --clean --noconfirm "DTC Chrome Kiosk.spec"
```

Output: `dist/DTC Chrome Kiosk.app`.

If you ever need to regenerate the spec from scratch:

```bash
uv run pyinstaller --windowed --name "DTC Chrome Kiosk" \
  --osx-bundle-identifier com.dtc.chromekiosk \
  --icon ChromeIcon.icns --noconfirm web_window.py
```

To change the target URL, edit `URL` near the top of `web_window.py`, then rebuild.

---

## Notes

- Build on the same CPU architecture as the target Mac (Apple Silicon vs Intel) — PyInstaller does not cross-compile. `.venv`, `build/`, and `dist/` are gitignored; rebuild locally on each machine instead of committing artifacts.
- Both apps are ad-hoc signed (no Apple Developer cert). First launch on another Mac needs right-click → Open to bypass Gatekeeper, or `xattr -cr "<app name>.app"` if quarantined after download/transfer.
- Both windows are frameless and sized to the full screen via `show()`, not `showFullScreen()` — macOS's native fullscreen opens a separate Space, which this avoids while still covering the whole screen.
