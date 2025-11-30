# Migration Guide: VLC to Chromium Video Player

This guide explains how to migrate from VLC-based video playback to the new Chromium-based HTML5 video player.

## Overview

The new system replaces VLC with a Chromium browser running in kiosk mode, displaying an HTML5 video player. This provides:

- Better hardware acceleration on Raspberry Pi
- More reliable playback
- Web-based controls via WebSocket
- Same API endpoints (backward compatible)
- Modern HTML5 video features

## Architecture Changes

### Old System (VLC)
```
FastAPI Server → VLC Python Bindings → VLC Player → HDMI Output
```

### New System (Chromium)
```
FastAPI Server → WebSocket → Chromium Browser → HTML5 Video → HDMI Output
```

## Files Structure

### New Files Created

1. **server/src/chromium_video_manager.py**
   - Replacement for VLC video manager
   - Maintains same interface as original VideoManager
   - Controls Chromium via WebSocket

2. **server/web/video_player.html**
   - HTML5 video player interface
   - WebSocket client for command reception
   - Automatic reconnection logic

3. **server/server_chromium.py**
   - FastAPI server with WebSocket support
   - Static file serving for videos
   - Player HTML endpoint

4. **scripts/start_chromium_kiosk.sh**
   - Launcher script for Chromium kiosk mode
   - X server management
   - Server startup

5. **systemd/chromium-kiosk.service**
   - Systemd service for auto-start
   - Automatic restart on failure

6. **setup_chromium_player.sh**
   - Complete installation script
   - System dependencies
   - Configuration

## Installation Steps

### Step 1: Run Setup Script

```bash
cd /home/pi/DTC_RPI
chmod +x setup_chromium_player.sh
./setup_chromium_player.sh
```

The script will:
- Install Chromium and X server packages
- Configure hardware video acceleration
- Set up Python virtual environment
- Install dependencies
- Configure systemd service
- Set up auto-login and auto-start

### Step 2: Reboot

```bash
sudo reboot
```

After reboot, the system will:
1. Auto-login as user 'pi'
2. Start X server
3. Launch FastAPI server with ChromiumVideoManager
4. Open Chromium in kiosk mode to display video player
5. Load and play the last played video (if any)

## API Compatibility

All existing API endpoints remain unchanged:

### Video Control Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/upload` | POST | Upload video files | ✅ Compatible |
| `/play` | POST | Play a video | ✅ Compatible |
| `/pause` | POST | Pause playback | ✅ Compatible |
| `/stop` | POST | Stop playback | ✅ Compatible |
| `/resume` | POST | Resume playback | ✅ Compatible |
| `/status` | GET | Get player status | ✅ Compatible |
| `/videos` | GET | List videos | ✅ Compatible |
| `/preview` | GET | Get compressed preview | ✅ Compatible |
| `/video/{name}` | DELETE | Delete video | ✅ Compatible |

### New Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/player` | GET | Video player HTML page |
| `/ws/video` | WebSocket | Video control WebSocket |
| `/videos/{filename}` | GET | Static video file serving |

## Testing the Migration

### 1. Check Service Status

```bash
sudo systemctl status chromium-kiosk
```

Should show "active (running)"

### 2. View Logs

```bash
journalctl -u chromium-kiosk -f
```

Look for:
- "Chromium started in kiosk mode"
- "WebSocket connection registered"
- "Video loaded successfully"

### 3. Test API Endpoints

```bash
# Get status
curl -H "AUTH: your-api-token" http://localhost:8000/status

# List videos
curl -H "AUTH: your-api-token" http://localhost:8000/videos

# Play a video
curl -X POST -H "AUTH: your-api-token" \
  -H "Content-Type: application/json" \
  -d '{"video_name": "your_video.mp4"}' \
  http://localhost:8000/play
```

### 4. Check Chromium Process

```bash
ps aux | grep chromium
```

Should show chromium-browser running with kiosk flags

### 5. Check WebSocket Connection

```bash
# Check server logs for WebSocket messages
journalctl -u chromium-kiosk -f | grep -i websocket
```

## Switching Between VLC and Chromium

### To Use Chromium (New System)

Edit `/etc/systemd/system/chromium-kiosk.service`:
```bash
ExecStart=/bin/bash /home/pi/DTC_RPI/scripts/start_chromium_kiosk.sh
```

Ensure `server_chromium.py` imports from `chromium_video_manager`

### To Revert to VLC (Old System)

If needed, change the server to use the original VLC manager:

1. Stop the chromium service:
```bash
sudo systemctl stop chromium-kiosk
sudo systemctl disable chromium-kiosk
```

2. Start the original server:
```bash
cd /home/pi/DTC_RPI/server
source venv/bin/activate
python server.py
```

## Troubleshooting

### Chromium Won't Start

**Problem**: Chromium process not running

**Solutions**:
1. Check X server is running:
   ```bash
   DISPLAY=:0 xset q
   ```

2. Check display permissions:
   ```bash
   xhost +local:
   ```

3. Check Chromium logs:
   ```bash
   journalctl -u chromium-kiosk | grep chromium
   ```

### Black Screen on HDMI

**Problem**: Display shows black screen

**Solutions**:
1. Check GPU memory allocation:
   ```bash
   grep gpu_mem /boot/config.txt
   ```
   Should be at least 256

2. Check video file path is accessible:
   ```bash
   ls -la /home/pi/DTC_RPI/server/uploaded_videos/
   ```

3. Check browser console (requires SSH with X forwarding)

### WebSocket Not Connecting

**Problem**: Player can't connect to server

**Solutions**:
1. Check server is running:
   ```bash
   curl http://localhost:8000/player
   ```

2. Check WebSocket endpoint:
   ```bash
   curl -i -N \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: test" \
     http://localhost:8000/ws/video
   ```

3. Check firewall rules:
   ```bash
   sudo iptables -L -n
   ```

### Video Won't Play

**Problem**: Video file loads but doesn't play

**Solutions**:
1. Check video codec compatibility:
   ```bash
   ffmpeg -i your_video.mp4
   ```
   HTML5 supports: H.264, VP8, VP9

2. Re-encode if needed:
   ```bash
   ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4
   ```

3. Check browser autoplay policies:
   - Chromium flags should include `--autoplay-policy=no-user-gesture-required`

### High CPU Usage

**Problem**: Chromium using too much CPU

**Solutions**:
1. Enable hardware acceleration flags in `chromium_video_manager.py`:
   - `--enable-features=VaapiVideoDecoder`
   - `--use-gl=egl`

2. Check GPU rendering:
   ```bash
   DISPLAY=:0 chromium-browser --enable-logging chrome://gpu
   ```

3. Lower video resolution/bitrate

## Performance Optimization

### Hardware Acceleration

Ensure these are enabled in `/boot/config.txt`:
```
gpu_mem=256
dtoverlay=vc4-kms-v3d
```

### Video Encoding

For best performance, encode videos as:
- Codec: H.264
- Resolution: 1920x1080 or lower
- Framerate: 30fps or lower
- Bitrate: 5-10 Mbps

Example FFmpeg command:
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -maxrate 8M \
  -bufsize 16M \
  -c:a aac \
  -b:a 192k \
  output.mp4
```

### Chromium Flags

Additional flags for performance (edit `chromium_video_manager.py`):
```python
"--disable-gpu-vsync",  # Reduce GPU overhead
"--disable-software-rasterizer",  # Force hardware rendering
"--ignore-gpu-blocklist",  # Override GPU blocklist
```

## Rollback Plan

If you need to completely rollback:

1. Stop and disable Chromium service:
```bash
sudo systemctl stop chromium-kiosk
sudo systemctl disable chromium-kiosk
```

2. Restore original server.py imports:
```python
from src.video_manager import PlayerState, logger, video_manager
```

3. Install VLC if removed:
```bash
sudo apt-get install vlc python3-vlc
```

4. Restart with original server:
```bash
cd /home/pi/DTC_RPI/server
source venv/bin/activate
python server.py
```

## Benefits of Chromium Approach

1. **Better Hardware Acceleration**: Modern browsers have better GPU integration
2. **Format Support**: HTML5 supports more formats natively
3. **Debugging**: Browser dev tools for troubleshooting
4. **Web Standards**: Uses standard web technologies
5. **Remote Debugging**: Can debug remotely via Chrome DevTools
6. **Updates**: Chromium receives regular security updates

## Known Limitations

1. **Startup Time**: Chromium takes 3-5 seconds to launch (vs VLC instant)
2. **Memory Usage**: Chromium uses more RAM (~150MB vs VLC ~50MB)
3. **Codec Support**: Limited to browser-supported codecs (H.264, VP8, VP9)
4. **Dependencies**: Requires X server (headless mode not suitable)

## Support

For issues or questions:
- Check logs: `journalctl -u chromium-kiosk -f`
- Test endpoints with curl
- Verify WebSocket connection
- Check Chromium process status

## Additional Resources

- [Raspberry Pi Video Acceleration](https://www.raspberrypi.org/documentation/configuration/config-txt/video.md)
- [Chromium Command Line Switches](https://peter.sh/experiments/chromium-command-line-switches/)
- [HTML5 Video API](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
