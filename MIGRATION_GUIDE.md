# Migration Guide: VLC to Chromium Video Player

## Overview

This guide explains the migration from VLC-based video playback to Chromium-based HTML video playback.

## What Changed

### Before (VLC)
- Videos played directly through VLC player
- Required `python-vlc` library
- Used VLC's fullscreen mode
- Direct video rendering

### After (Chromium)
- Videos play in HTML5 `<video>` tag
- Chromium browser displays fullscreen
- Server streams video files via HTTP
- Better integration with web technologies

## Key Differences

| Feature | VLC | Chromium |
|---------|-----|----------|
| **Player** | VLC Media Player | Chromium Browser |
| **Display** | Direct video output | HTML page with `<video>` tag |
| **Control** | Python VLC bindings | State file + HTTP polling |
| **Dependencies** | `python-vlc`, VLC | X Server, Chromium |
| **Resource Usage** | Lower | Slightly higher |
| **Customization** | Limited | Full HTML/CSS/JS |

## File Changes

### New Files Created

1. **[server/src/chromium_video_manager.py](server/src/chromium_video_manager.py)**
   - New video manager class
   - Manages Chromium browser lifecycle
   - Handles player state synchronization

2. **[server/templates/video_player.html](server/templates/video_player.html)**
   - HTML video player interface
   - JavaScript for state polling
   - Responsive video container

3. **[CHROMIUM_SETUP.md](CHROMIUM_SETUP.md)**
   - Setup instructions
   - Troubleshooting guide

4. **[setup_chromium.sh](setup_chromium.sh)**
   - Automated installation script

### Modified Files

1. **[server/server.py](server/server.py)**
   - Import changed: `from src.chromium_video_manager import ...`
   - Added `/player` endpoint (HTML page)
   - Added `/api/player/state` endpoint (state API)
   - Added `/videos` static file mount

2. **[server/src/tv_controller.py](server/src/tv_controller.py)**
   - Import changed: `from src.chromium_video_manager import video_manager`

3. **[server/src/routers/video_manager.py](server/src/routers/video_manager.py)**
   - Import changed: `from src.chromium_video_manager import PlayerState`

### Unchanged Files

- All API endpoint logic remains the same
- HDMI-CEC controller unchanged
- TV scheduler logic unchanged
- Video compression unchanged
- Authentication unchanged

## API Compatibility

**All existing API endpoints work exactly the same:**

```python
# These calls work identically with both VLC and Chromium
POST /play
POST /pause
POST /stop
POST /resume
GET /status
POST /upload
DELETE /video/{name}
```

**Response formats are identical:**

```json
// GET /status response (same for both)
{
  "current_video": "example.mp4",
  "is_playing": true,
  "is_paused": false,
  "is_looping": true,
  "available_videos": ["example.mp4"],
  "date_uploaded": ["10:30 AM Nov 30 2025"]
}
```

## Architecture Changes

### VLC Architecture
```
API Request → VideoManager → VLC Player → HDMI Output
```

### Chromium Architecture
```
API Request → ChromiumVideoManager → State File
                                          ↓
                                     HTML Player (polls state)
                                          ↓
                                     <video> tag → HDMI Output
```

## State Management

### VLC (Direct Control)
```python
# Direct control of player
video_manager.play()  # Immediately plays video
video_manager.pause() # Immediately pauses
```

### Chromium (State-Based)
```python
# Updates state file
video_manager.play()  # Sets is_playing=True in state
                      # HTML player polls and sees change
                      # Starts playback

video_manager.pause() # Sets is_paused=True in state
                      # HTML player polls and sees change
                      # Pauses playback
```

**State synchronization happens every 2 seconds** via JavaScript polling.

## Code Comparison

### Loading and Playing Video

**VLC:**
```python
def play(self):
    self.list_player.play()
    self.is_playing = True
```

**Chromium:**
```python
def play(self):
    self._start_chromium()  # Launch browser if needed
    self.is_playing = True
    self._save_player_state()  # Save state for HTML player
```

### Stopping Video

**VLC:**
```python
def stop(self):
    self.list_player.stop()
    self.is_playing = False
```

**Chromium:**
```python
def stop(self):
    self.is_playing = False
    self._save_player_state()
    self._stop_chromium()  # Close browser
```

## Deployment Checklist

### On Raspberry Pi

1. **Backup current installation**
   ```bash
   cd /Users/Rajan/Documents/GitHub/DTC_RPI
   git stash  # If you have local changes
   ```

2. **Pull latest changes**
   ```bash
   git pull origin main
   ```

3. **Run setup script**
   ```bash
   chmod +x setup_chromium.sh
   ./setup_chromium.sh
   ```

4. **Reboot**
   ```bash
   sudo reboot
   ```

5. **Verify services**
   ```bash
   sudo systemctl status xserver.service
   sudo systemctl status video-server.service
   ```

6. **Test API**
   ```bash
   # Check status
   curl -H "AUTH: your-key" http://localhost:8000/status

   # Play a video
   curl -X POST -H "AUTH: your-key" \
     -H "Content-Type: application/json" \
     -d '{"video_name": "test.mp4"}' \
     http://localhost:8000/play
   ```

## Rollback Plan

If you need to revert to VLC:

1. **Update imports in 3 files:**

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

2. **Restart service:**
   ```bash
   sudo systemctl restart video-server.service
   ```

3. **VLC will work immediately** (no X Server needed)

## Troubleshooting

### Issue: "Module not found: chromium_video_manager"

**Cause:** Import error

**Fix:**
```bash
cd /Users/Rajan/Documents/GitHub/DTC_RPI/server
python3 -c "import src.chromium_video_manager"
```

If error persists, check file exists:
```bash
ls -la src/chromium_video_manager.py
```

### Issue: Chromium won't start

**Check X Server:**
```bash
ps aux | grep X
echo $DISPLAY  # Should be :0
```

**Verify Chromium is installed:**
```bash
which chromium
chromium --version
```

**Start X Server manually:**
```bash
startx &
```

### Issue: Black screen on HDMI

**Test Chromium manually:**
```bash
DISPLAY=:0 chromium --kiosk http://localhost:8000/player
```

**Check HDMI:**
```bash
tvservice -s
```

### Issue: Video doesn't load

**Check video file serving:**
```bash
curl http://localhost:8000/videos/example.mp4 -I
# Should return: HTTP/1.1 200 OK
```

**Check player state:**
```bash
curl http://localhost:8000/api/player/state
```

## Performance Considerations

### Resource Usage

**VLC:**
- RAM: ~50-100 MB
- CPU: 5-15%
- Startup: <1 second

**Chromium:**
- RAM: ~150-250 MB
- CPU: 10-20%
- Startup: 2-3 seconds

### Optimization Tips

1. **Use H.264 videos** (hardware accelerated on Pi)
2. **Limit resolution** to 1080p or lower
3. **Close unnecessary browser tabs** (Chromium runs single page)
4. **Disable Chromium GPU** (already configured)

## Benefits of Chromium Approach

1. **Web Integration**: Easy to add overlays, text, graphics
2. **Remote Debugging**: Can inspect with Chrome DevTools
3. **Modern Format Support**: WebM, MP4, etc.
4. **Customization**: Full HTML/CSS control
5. **Future Expandability**: Can add playlists, subtitles, etc.

## Limitations

1. **Higher Resource Usage**: Chromium uses more RAM than VLC
2. **X Server Required**: Needs graphical environment
3. **Slower Startup**: 2-3 second delay vs instant VLC
4. **Network Dependency**: Video served over HTTP (localhost)

## Testing Matrix

| Test Case | VLC | Chromium | Status |
|-----------|-----|----------|--------|
| Play video | ✓ | ✓ | ✓ |
| Pause video | ✓ | ✓ | ✓ |
| Stop video | ✓ | ✓ | ✓ |
| Resume video | ✓ | ✓ | ✓ |
| Loop mode | ✓ | ✓ | ✓ |
| Upload video | ✓ | ✓ | ✓ |
| Delete video | ✓ | ✓ | ✓ |
| TV scheduling | ✓ | ✓ | ✓ |
| HDMI-CEC control | ✓ | ✓ | ✓ |
| Auto-resume on boot | ✓ | ✓ | ✓ |

## Support

For issues:
1. Check [CHROMIUM_SETUP.md](CHROMIUM_SETUP.md) troubleshooting section
2. Review server logs: `journalctl -u video-server.service -f`
3. Check X Server logs: `journalctl -u xserver.service -f`
4. Verify Chromium: `DISPLAY=:0 chromium --version`

## Conclusion

The migration maintains **100% API compatibility** while switching the underlying video playback mechanism. All existing clients and integrations continue to work without modification.
