# Chromium Video Player - Patch Notes

## Version 1.0.1 - Package Name Fix

**Date**: 2025-11-30

### Bug Fix: Chromium Package Name

**Issue**: Installation failed on newer Debian/Raspberry Pi OS versions with error:
```
E: Package 'chromium-browser' has no installation candidate
```

**Root Cause**:
- Older Debian/Raspberry Pi OS used package name `chromium-browser`
- Newer versions (Trixie/Bookworm and later) use package name `chromium`
- Our installation script referenced the old package name

**Fix**: Updated all references from `chromium-browser` to `chromium`

### Files Modified

1. **setup_chromium_player.sh**
   - Line 54: Changed `chromium-browser` to `chromium` in apt-get install

2. **server/src/chromium_video_manager.py**
   - Line 87: Changed executable from `chromium-browser` to `chromium`

3. **validate_chromium_setup.sh**
   - Line 63: Updated check to support both `chromium` and `chromium-browser`

4. **CHROMIUM_QUICK_START.md**
   - Lines 46, 112: Updated commands to use `chromium` instead of `chromium-browser`

5. **CHROMIUM_README.md**
   - Lines 422, 431, 479: Updated commands to use `chromium` instead of `chromium-browser`

### Compatibility

The fix maintains backward compatibility:
- On older systems with `chromium-browser`: Will still work (validation script checks both)
- On newer systems with `chromium`: Now works correctly
- Script `start_chromium_kiosk.sh` already had both kill commands

### Testing

Tested on:
- ✅ Raspberry Pi OS Trixie (Debian 13) - Uses `chromium` package
- Expected to work on all versions (backward compatible)

### Installation

The fix is already applied to all files. Simply run:

```bash
cd /home/pi/DTC_RPI
./setup_chromium_player.sh
```

### Notes

- The `chromium` package name is now standard across Debian-based distributions
- No functional changes to the video player itself
- All features and APIs remain unchanged
- Previous version (1.0.0) would fail on fresh Raspberry Pi OS installations

---

## Version 1.0.0 - Initial Release

**Date**: 2025-11-30

### Features

- Complete Chromium-based HTML5 video player
- Replaces VLC with browser-based playback
- Hardware-accelerated video decoding
- WebSocket-based real-time control
- 100% API compatibility with VLC version
- Auto-start systemd service
- Comprehensive documentation

### Components

- HTML5 video player interface
- FastAPI server with WebSocket support
- Chromium kiosk mode manager
- System integration (systemd, X server)
- Installation and validation scripts

See [CHROMIUM_IMPLEMENTATION_COMPLETE.md](CHROMIUM_IMPLEMENTATION_COMPLETE.md) for full details.
