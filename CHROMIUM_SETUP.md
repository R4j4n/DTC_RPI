# Chromium Video Player Setup Guide

This guide helps you set up the Chromium-based video player on Raspberry Pi OS Lite 64-bit.

## Overview

The system has been updated to use **Chromium browser in kiosk mode** instead of VLC for video playback. Videos are displayed in an HTML div through a fullscreen browser window on the HDMI output.

## Prerequisites

### 1. Install X Server (Required for Chromium)

Since you're using Raspberry Pi OS Lite, you need a minimal X server installation:

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox
```

### 2. Install Chromium Browser

```bash
sudo apt-get install -y chromium
```

### 3. Verify Installation

```bash
chromium --version
```

## System Configuration

### 1. Auto-start X Server on Boot

Create a systemd service to start X server automatically:

```bash
sudo nano /etc/systemd/system/xserver.service
```

Add the following content:

```ini
[Unit]
Description=X Server
After=network.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
ExecStart=/usr/bin/startx
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable xserver.service
sudo systemctl start xserver.service
```

### 2. Configure X Server to Start Openbox

Create or edit `~/.xinitrc`:

```bash
nano ~/.xinitrc
```

Add:

```bash
#!/bin/bash
xset -dpms      # Disable DPMS (Energy Star) features
xset s off      # Disable screen saver
xset s noblank  # Don't blank the video device
openbox-session
```

Make it executable:

```bash
chmod +x ~/.xinitrc
```

### 3. Disable Screen Blanking (Optional but Recommended)

Edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

Add at the end:

```
# Disable screen blanking
hdmi_blanking=1
```

### 4. Python Dependencies

The system should already have FastAPI and other dependencies. If not:

```bash
pip3 install fastapi uvicorn python-multipart
```

## How It Works

### Architecture

1. **FastAPI Server** (Port 8000)
   - Serves HTML video player at `/player`
   - Provides video files at `/videos/<filename>`
   - Exposes player state API at `/api/player/state`
   - All existing REST endpoints remain unchanged

2. **Chromium Browser**
   - Launched in kiosk mode (fullscreen, no UI)
   - Displays HTML page from `http://localhost:8000/player`
   - JavaScript polls server for video state changes
   - HTML5 `<video>` tag handles actual playback

3. **Video Flow**
   ```
   API Call (/play) → Update State → Chromium Polls State → Load Video → Display on HDMI
   ```

### File Structure

```
server/
├── templates/
│   └── video_player.html          # HTML video player interface
├── src/
│   ├── chromium_video_manager.py  # New Chromium-based manager
│   ├── video_manager.py           # Old VLC manager (not used)
│   └── routers/
│       └── video_manager.py       # API routes (unchanged)
├── uploaded_videos/               # Video storage
│   └── compressed/                # Compressed previews
└── server.py                      # Main FastAPI app
```

## Usage

### Starting the Server

```bash
cd /Users/Rajan/Documents/GitHub/DTC_RPI/server
python3 server.py
```

The server will:
1. Start FastAPI on port 8000
2. Initialize the ChromiumVideoManager
3. Load the last played video (if any)
4. Launch Chromium in kiosk mode when video playback starts

### API Endpoints (Unchanged)

All existing endpoints work exactly the same:

- `POST /play` - Play a video
- `POST /pause` - Pause playback
- `POST /stop` - Stop playback (closes browser)
- `POST /resume` - Resume paused video
- `GET /status` - Get player status
- `POST /upload` - Upload videos
- `DELETE /video/{name}` - Delete video

### Example Usage

```bash
# Play a video
curl -X POST http://localhost:8000/play \
  -H "AUTH: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"video_name": "example.mp4"}'

# Check status
curl http://localhost:8000/status \
  -H "AUTH: your-api-key"

# Pause
curl -X POST http://localhost:8000/pause \
  -H "AUTH: your-api-key"
```

## Troubleshooting

### Issue: Chromium doesn't start

**Check X Server is running:**
```bash
echo $DISPLAY
# Should output: :0

ps aux | grep X
# Should show Xorg process
```

**Test Chromium manually:**
```bash
DISPLAY=:0 chromium --version
```

### Issue: Black screen on HDMI

**Check HDMI output:**
```bash
tvservice -s
# Should show current HDMI mode
```

**Force HDMI output** in `/boot/config.txt`:
```
hdmi_force_hotplug=1
hdmi_drive=2
```

### Issue: Video doesn't autoplay

Modern browsers require user interaction for autoplay. The HTML player is configured with:
- `autoplay` attribute
- `--autoplay-policy=no-user-gesture-required` Chromium flag

If it still doesn't work, check browser console:
```bash
# Run Chromium with console output
DISPLAY=:0 chromium --kiosk http://localhost:8000/player
```

### Issue: Browser crashes or closes unexpectedly

Check logs:
```bash
journalctl -u xserver.service -f
```

The ChromiumVideoManager will attempt to restart Chromium automatically.

### Issue: Permission denied for /home/pi/.Xauthority

Run as the correct user (usually `pi`):
```bash
whoami  # Should output: pi
```

Or update the `XAUTHORITY` path in [chromium_video_manager.py](server/src/chromium_video_manager.py:56):
```python
env = {
    "DISPLAY": ":0",
    "XAUTHORITY": "/home/YOUR_USERNAME/.Xauthority"
}
```

## Performance Optimization

### 1. Reduce Memory Usage

In [chromium_video_manager.py](server/src/chromium_video_manager.py), the Chromium command includes:
- `--disable-gpu` - Saves memory on headless systems
- `--no-sandbox` - Reduces overhead (already included)

### 2. Video Format Recommendations

For best performance on Raspberry Pi:
- **Codec**: H.264
- **Resolution**: 1080p or lower
- **Bitrate**: 5-10 Mbps
- **Container**: MP4

Convert videos with FFmpeg:
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k output.mp4
```

### 3. Disable Unnecessary Services

```bash
sudo systemctl disable bluetooth
sudo systemctl disable wifi
```

## Reverting to VLC

If you need to switch back to VLC:

1. Update [server.py](server/server.py:20):
   ```python
   from src.video_manager import PlayerState, logger, video_manager
   ```

2. Update [tv_controller.py](server/src/tv_controller.py:16):
   ```python
   from src.video_manager import video_manager
   ```

3. Update [routers/video_manager.py](server/src/routers/video_manager.py:18):
   ```python
   from src.video_manager import PlayerState
   ```

4. Restart the server

## Systemd Service for Auto-Start

Create a systemd service for the video server:

```bash
sudo nano /etc/systemd/system/video-server.service
```

Add:

```ini
[Unit]
Description=Video Server
After=network.target xserver.service
Requires=xserver.service

[Service]
Type=simple
User=pi
WorkingDirectory=/Users/Rajan/Documents/GitHub/DTC_RPI/server
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 /Users/Rajan/Documents/GitHub/DTC_RPI/server/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl enable video-server.service
sudo systemctl start video-server.service
```

## Additional Notes

### Scheduled TV Control

The TV scheduling functionality works exactly the same. The [tv_controller.py](server/src/tv_controller.py) will:
1. Turn on TV via HDMI-CEC
2. Switch to correct HDMI input
3. Load last played video
4. Launch Chromium automatically

### Remote Management

Access the API from any device on the network:
```
http://<raspberry-pi-ip>:8000/status
```

### Video Upload

Upload works the same - videos are stored in `uploaded_videos/` and served via the `/videos` static endpoint.

## Testing Checklist

- [ ] X Server starts on boot
- [ ] Chromium launches in kiosk mode
- [ ] Video loads and plays automatically
- [ ] Loop mode works correctly
- [ ] Pause/resume functionality works
- [ ] TV scheduling triggers video playback
- [ ] HDMI output displays video correctly
- [ ] All API endpoints respond correctly
