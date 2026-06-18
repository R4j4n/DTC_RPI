# DTC Mac Player

PyQt6 + VLC desktop player for macOS. Packaged into a standalone `.app` with PyInstaller.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (`brew install uv`)
- [VLC.app](https://www.videolan.org/vlc/) installed in `/Applications` — `python-vlc` loads VLC's `libvlc` at runtime, it is not bundled into the app.

## Setup

```bash
cd mac_player
uv sync
```

This creates `.venv` and installs all dependencies (including `pyinstaller`) from `pyproject.toml` / `uv.lock`.

## Run from source

```bash
uv run python main.py
```

## Build the .app

```bash
uv run pyinstaller --clean --noconfirm "DTC Mac Player.spec"
```

Output: `dist/DTC Mac Player.app`. Build on the same CPU architecture as the target Mac (Apple Silicon vs Intel) — PyInstaller does not cross-compile architectures. `.venv`, `build/`, and `dist/` are gitignored; rebuild locally on each machine instead of committing artifacts.

## Notes

- App is ad-hoc signed (no Apple Developer cert). First launch on another Mac needs right-click → Open to bypass Gatekeeper, or `xattr -cr "DTC Mac Player.app"` if quarantined after download/transfer.
