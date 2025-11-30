# Chromium Video Player - Quick Start Guide

## Installation (One Command)

```bash
cd /home/pi/DTC_RPI && chmod +x setup_chromium_player.sh && ./setup_chromium_player.sh
```

Then reboot when prompted.

## Service Management

```bash
# Start service
sudo systemctl start chromium-kiosk

# Stop service
sudo systemctl stop chromium-kiosk

# Restart service
sudo systemctl restart chromium-kiosk

# Check status
sudo systemctl status chromium-kiosk

# View logs
journalctl -u chromium-kiosk -f

# Enable auto-start on boot
sudo systemctl enable chromium-kiosk

# Disable auto-start on boot
sudo systemctl disable chromium-kiosk
```

## Testing

### 1. Check Service is Running
```bash
sudo systemctl status chromium-kiosk
```
Look for: `active (running)`

### 2. Check Chromium Process
```bash
ps aux | grep chromium-browser
```
Should show chromium running with `--kiosk` flag

### 3. Test API
```bash
# Get API token first
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password": "your-password"}' | jq -r '.token')

# Get status
curl -H "AUTH: $TOKEN" http://localhost:8000/status

# List videos
curl -H "AUTH: $TOKEN" http://localhost:8000/videos
```

### 4. Upload and Play Video
```bash
# Upload a video (you'll need both original and compressed)
curl -X POST http://localhost:8000/upload \
  -H "AUTH: $TOKEN" \
  -F "original_file=@video.mp4" \
  -F "compressed_file=@video.mp4"

# Play the video
curl -X POST http://localhost:8000/play \
  -H "AUTH: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"video_name": "video.mp4"}'
```

## File Locations

```
/home/pi/DTC_RPI/
├── server/
│   ├── server_chromium.py          # Main server (Chromium version)
│   ├── server.py                   # Original server (VLC version)
│   ├── src/
│   │   ├── chromium_video_manager.py  # New Chromium manager
│   │   └── video_manager.py           # Original VLC manager
│   ├── web/
│   │   └── video_player.html       # HTML5 video player
│   └── uploaded_videos/            # Video storage
├── scripts/
│   └── start_chromium_kiosk.sh     # Launcher script
└── systemd/
    └── chromium-kiosk.service      # Systemd service
```

## Troubleshooting Quick Fixes

### Black Screen
```bash
# Check X server
DISPLAY=:0 xset q

# Restart service
sudo systemctl restart chromium-kiosk
```

### Chromium Won't Start
```bash
# Kill all Chromium processes
pkill -9 chromium-browser

# Clear Chromium cache
rm -rf ~/.config/chromium/

# Restart service
sudo systemctl restart chromium-kiosk
```

### WebSocket Issues
```bash
# Check server logs
journalctl -u chromium-kiosk -f | grep -i websocket

# Restart server
sudo systemctl restart chromium-kiosk
```

### Video Won't Play
```bash
# Check video file exists
ls -la /home/pi/DTC_RPI/server/uploaded_videos/

# Check video format
ffmpeg -i /home/pi/DTC_RPI/server/uploaded_videos/your_video.mp4

# Re-encode to H.264 if needed
ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4
```

## Configuration Files

### GPU Memory (/boot/config.txt)
```bash
gpu_mem=256
dtoverlay=vc4-kms-v3d
```

### Auto-Login (/etc/systemd/system/getty@tty1.service.d/autologin.conf)
```ini
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM
```

## Network Access

Once running, access from other devices:

```
http://<raspberry-pi-ip>:8000
```

Find your Pi's IP:
```bash
hostname -I
```

## Default Ports

- FastAPI Server: `8000`
- WebSocket: `8000/ws/video`
- Video Player: `8000/player`

## Performance Tips

1. **Use H.264 encoded videos** for best compatibility
2. **Keep videos under 1080p** for smooth playback
3. **Ensure GPU memory is 256MB** in /boot/config.txt
4. **Close other applications** to free up resources
5. **Use wired Ethernet** for better streaming stability

## Remote Debugging

Enable remote Chrome DevTools (add to chromium_video_manager.py):
```python
"--remote-debugging-port=9222",
```

Then from another computer:
```
chrome://inspect
```

## Maintenance

### Clear Cache
```bash
sudo systemctl stop chromium-kiosk
rm -rf ~/.cache/chromium/
sudo systemctl start chromium-kiosk
```

### Update System
```bash
sudo apt-get update
sudo apt-get upgrade
sudo reboot
```

### Backup Videos
```bash
tar -czf videos_backup.tar.gz /home/pi/DTC_RPI/server/uploaded_videos/
```

## Getting Help

1. Check service status: `sudo systemctl status chromium-kiosk`
2. View full logs: `journalctl -u chromium-kiosk -n 100`
3. Check Chromium process: `ps aux | grep chromium`
4. Test API endpoints with curl
5. Check disk space: `df -h`
6. Check memory: `free -h`

## Switching Back to VLC

If you need to use VLC instead:

```bash
# Stop Chromium service
sudo systemctl stop chromium-kiosk
sudo systemctl disable chromium-kiosk

# Start VLC-based server manually
cd /home/pi/DTC_RPI/server
source venv/bin/activate
python server.py
```

## Support Video Formats

HTML5 supports:
- ✅ MP4 (H.264 + AAC)
- ✅ WebM (VP8/VP9 + Vorbis/Opus)
- ❌ MKV (requires conversion)
- ❌ AVI (requires conversion)

Convert unsupported formats:
```bash
ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4
```
