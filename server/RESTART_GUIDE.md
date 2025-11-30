# How to Restart and See the Kiosk Display

## Issue Fixed

The TV controller was using the old VLC video manager instead of the web video manager. This has been fixed.

## Quick Restart Steps

### 1. Stop the Current Server

Press `Ctrl+C` in the terminal where `server.py` is running.

Or kill it manually:
```bash
pkill -f "python.*server.py"
pkill -f chromium-browser
```

### 2. Restart the Server

```bash
cd /Users/Rajan/Documents/GitHub/DTC_RPI/server
python server.py
```

**You should now see:**
```
Starting DTC_RPI Server in WEB mode
INFO:     Uvicorn running on http://0.0.0.0:8000
Launching kiosk display...
Server is ready!
Launching kiosk display on HDMI...
Kiosk launched successfully!
```

### 3. Verify the Kiosk Display

The kiosk should now appear on your HDMI-connected screen showing:
- ✅ Fullscreen video
- ✅ Bottom timing bar with wristband schedule
- ✅ Live countdown timers

## What Was Fixed

1. **[tv_controller.py](src/tv_controller.py)** - Now uses web_video_manager in WEB mode
2. **[launch_kiosk.sh](launch_kiosk.sh)** - Properly exports DISPLAY=:0 for HDMI
3. **TV turn on/off** - Launches/closes kiosk instead of VLC

## Testing the Display

### Option A: Wait for Scheduled TV Turn-On
If you have a TV schedule set, wait for the scheduled turn-on time.
The system will automatically:
1. Turn on TV via CEC
2. Switch HDMI input
3. Launch kiosk display

### Option B: Manual Test via API

```bash
# Test TV turn on (this will launch kiosk)
curl -X POST http://localhost:8000/tv/test_tv \
  -H "Content-Type: application/json" \
  -H "AUTH: your_token" \
  -d '{"action": "on"}'
```

### Option C: Launch Kiosk Manually

```bash
cd /Users/Rajan/Documents/GitHub/DTC_RPI/server
./launch_kiosk.sh
```

## Troubleshooting

### Still Not Showing on HDMI?

1. **Check X server is running:**
   ```bash
   ps aux | grep X
   ```

2. **Verify DISPLAY variable:**
   ```bash
   echo $DISPLAY  # Should be :0
   ```

3. **Test if Chromium can launch:**
   ```bash
   DISPLAY=:0 chromium-browser http://localhost:8000/kiosk &
   ```

4. **Check if running via SSH:**
   If you're SSH'd into the Pi, the display will show on the Pi's HDMI, not your SSH client.

5. **Ensure X session is active:**
   You may need to be logged in to the GUI on the Raspberry Pi for DISPLAY=:0 to work.

### Video Playing via VLC Instead?

If you still see VLC:
1. Stop the server
2. Check `config.py` has `VIDEO_PLAYER_MODE = VideoPlayerMode.WEB`
3. Delete `last_played.json` (forces fresh start)
4. Restart server

### Kiosk Shows But No Video?

1. **Check video is uploaded:**
   ```bash
   ls /Users/Rajan/Documents/GitHub/DTC_RPI/server/uploaded_videos/
   ```

2. **Upload a test video if needed** via your admin interface

3. **Check video status:**
   ```bash
   curl http://localhost:8000/status
   ```

## Expected Behavior

### On Server Start (KIOSK_AUTO_LAUNCH=True)
1. Server starts
2. Waits 3 seconds
3. Launches kiosk automatically
4. Kiosk appears on HDMI screen

### On TV Scheduled Turn-On
1. CEC command sent to turn on TV
2. Wait 3 seconds for TV readiness
3. Switch to configured HDMI input
4. Launch kiosk display
5. Load and play last video
6. Show wristband schedule

### On TV Scheduled Turn-Off
1. Stop video playback
2. Close kiosk browser
3. CEC command sent to turn off TV

## Manual Control

### Launch Kiosk
```bash
./launch_kiosk.sh
```

### Close Kiosk
```bash
pkill -f chromium-browser
```

### View Kiosk in Browser (for testing)
```
http://localhost:8000/kiosk
```

### Check Schedule API
```bash
curl http://localhost:8000/wristband/schedule/status
```

## Next Steps

Once the kiosk is showing on HDMI:

1. ✅ **Verify schedule display** - Check timing bar at bottom
2. ✅ **Check countdown** - Should update every second
3. ✅ **Test video playback** - Should loop continuously
4. ✅ **Verify colors** - Wristband dots should match actual colors
5. ✅ **Check layout** - Clean minimal design with 100px bottom bar

## Success Indicators

You'll know it's working when you see:

```
┌──────────────────────────────────────────┐
│                                          │
│         YOUR VIDEO PLAYING               │
│                                          │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│ Jump Time Over │ 3:45 ● AQUA │ Upcoming │
│                │     14:23   │ 4:00 ●   │
└──────────────────────────────────────────┘
```

**On your HDMI-connected TV/monitor!**

---

*If issues persist, check server logs and browser console for errors.*
