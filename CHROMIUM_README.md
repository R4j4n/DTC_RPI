# Chromium-Based Video Player Implementation

## Quick Start

### What Was Done

Replaced VLC-based video playback with **Chromium browser displaying videos in HTML**.

### Installation

```bash
cd /Users/Rajan/Documents/GitHub/DTC_RPI
chmod +x setup_chromium.sh
./setup_chromium.sh
sudo reboot
```

### Key Features

✅ **100% API Compatible** - All existing endpoints work unchanged
✅ **HDMI Output** - Fullscreen Chromium kiosk mode
✅ **Auto-Loop** - Videos loop seamlessly
✅ **TV Scheduling** - Works with existing scheduler
✅ **State Persistence** - Resumes last video on boot

## Architecture

```
FastAPI (Port 8000)
    ↓
Chromium Kiosk Mode → HDMI Display
    ↓
HTML5 Video Player
    ↓
Local Video Files
```

## Files Created

| File | Purpose |
|------|---------|
| [chromium_video_manager.py](server/src/chromium_video_manager.py) | Main video manager (replaces VLC) |
| [video_player.html](server/templates/video_player.html) | HTML video player interface |
| [setup_chromium.sh](setup_chromium.sh) | Automated setup script |
| [CHROMIUM_SETUP.md](CHROMIUM_SETUP.md) | Detailed setup guide |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Migration documentation |

## Files Modified

| File | Change |
|------|--------|
| [server.py](server/server.py) | Import `chromium_video_manager` + add `/player` endpoint |
| [tv_controller.py](server/src/tv_controller.py) | Import from `chromium_video_manager` |
| [routers/video_manager.py](server/src/routers/video_manager.py) | Import `PlayerState` from chromium manager |

## API Endpoints (Unchanged)

All existing endpoints work identically:

```bash
# Play video
POST /play
{"video_name": "example.mp4"}

# Pause
POST /pause

# Resume
POST /resume

# Stop
POST /stop

# Status
GET /status

# Upload
POST /upload

# Delete
DELETE /video/{name}
```

## How It Works

1. **API receives play request** → Updates state file
2. **Chromium polls state** (every 2 seconds)
3. **HTML player updates** → Loads new video
4. **Video displays** on HDMI via fullscreen browser

## System Requirements

- Raspberry Pi OS Lite 64-bit
- X Server (minimal)
- Chromium Browser
- Python 3.7+
- FastAPI & Uvicorn

## Dependencies Installed by Script

```bash
# System packages
xserver-xorg
xinit
openbox
chromium

# Python packages
fastapi
uvicorn
python-multipart
```

## Comparison: VLC vs Chromium

| Aspect | VLC | Chromium |
|--------|-----|----------|
| API Compatibility | ✓ | ✓ (100%) |
| Resource Usage | Lower | Moderate |
| Startup Time | <1s | 2-3s |
| Customization | Limited | Full HTML/CSS |
| Web Integration | ✗ | ✓ |
| X Server Required | ✗ | ✓ |

## Testing

After installation:

```bash
# Check services
sudo systemctl status xserver.service
sudo systemctl status video-server.service

# Test API
curl http://localhost:8000/status

# View logs
journalctl -u video-server.service -f

# Test browser directly
DISPLAY=:0 chromium --kiosk http://localhost:8000/player
```

## Troubleshooting

### Chromium won't start
```bash
# Check X Server
echo $DISPLAY  # Should be :0
ps aux | grep X
```

### Black screen
```bash
# Check HDMI
tvservice -s

# Test manually
DISPLAY=:0 chromium --version
```

### Video won't play
```bash
# Check video serving
curl http://localhost:8000/videos/your-video.mp4 -I

# Check player state
curl http://localhost:8000/api/player/state
```

See [CHROMIUM_SETUP.md](CHROMIUM_SETUP.md) for detailed troubleshooting.

## Rollback to VLC

If needed, revert these 3 imports:

**server/server.py:**
```python
from src.video_manager import PlayerState, logger, video_manager
```

**server/src/tv_controller.py:**
```python
from src.video_manager import video_manager
```

**server/src/routers/video_manager.py:**
```python
from src.video_manager import PlayerState
```

Then restart:
```bash
sudo systemctl restart video-server.service
```

## Benefits

1. **Web-based UI** - Full HTML/CSS/JS control
2. **Easy customization** - Add overlays, text, graphics
3. **Modern formats** - WebM, MP4, etc.
4. **Remote debugging** - Chrome DevTools support
5. **Future expansion** - Playlists, subtitles, etc.

## Documentation

- **Setup Guide**: [CHROMIUM_SETUP.md](CHROMIUM_SETUP.md)
- **Migration Guide**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Original Architecture**: Architecture Overview (in prompt)

## Support

1. Review troubleshooting guides
2. Check service logs
3. Test components individually
4. Verify X Server and Chromium

---

**Status**: ✅ Implementation Complete
**API Compatibility**: ✅ 100%
**Testing**: Ready for deployment
**Documentation**: Complete
