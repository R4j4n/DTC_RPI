# Quick Start Guide - Wristband Display Feature

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies (Raspberry Pi)
```bash
sudo apt-get update
sudo apt-get install -y chromium-browser unclutter xdotool
```

### Step 2: Configure Server Mode
Edit `server/config.py`:
```python
VIDEO_PLAYER_MODE = VideoPlayerMode.WEB  # ✅ Enable web mode
```

### Step 3: Start Server
```bash
cd server
python server.py
```

**That's it!** The kiosk display will auto-launch in fullscreen showing:
- ✅ Video player (looping your uploaded videos)
- ✅ Wristband schedule with live countdowns
- ✅ Company colors integrated

---

## 📱 What You'll See

```
┌────────────────────────────────────────────┐
│                                            │
│         VIDEO PLAYING HERE                 │
│         (Fullscreen, Looping)              │
│                                            │
└────────────────────────────────────────────┘
┌────────────────────────────────────────────┐
│ 10:30   10:45   11:00  │ NOW JUMPING │ 🏢 │
│ Pink    Yellow  Orange │  11:15      │    │
│ (past)  (past)  (past) │  GREEN      │    │
│                        │  Ends: 12:34│    │
├────────────────────────┴─────────────┴────┤
│                    NEXT     UPCOMING      │
│                  11:30 Aqua  11:45 Silver │
│                  in 14:23    in 29:23     │
└────────────────────────────────────────────┘
```

---

## 🎨 Customization

### Add Your Logo
1. Save logo as `server/static/logo.png`
2. Edit `server/static/kiosk.html` (line ~157):
   ```html
   <img id="logo" src="/static/logo.png" alt="Logo">
   ```

### Modify Schedule Times
Edit `server/src/wristband_schedule.py`:
```python
SCHEDULE = [
    {"time": "10:30", "color": "pink", "hex": "#FF69B4"},
    {"time": "10:45", "color": "yellow", "hex": "#FFD700"},
    # ... add your times
]
```

### Company Colors (Already Applied)
- Primary: `#ff1152` (Red)
- Secondary: `#26f434` (Green)
- Accent: `#caff1a` (Lime)

---

## 🔧 Configuration Options

In `server/config.py`:

```python
class Config:
    # Video player mode
    VIDEO_PLAYER_MODE = VideoPlayerMode.WEB  # or VideoPlayerMode.VLC

    # Auto-launch kiosk on startup
    KIOSK_AUTO_LAUNCH = True  # Set False to launch manually

    # Server settings
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000
```

---

## 🎯 Key Features

✅ **Seamless Integration** - Works with existing APIs
✅ **Auto Schedule** - Wristband times update automatically
✅ **TV Scheduling** - Existing TV on/off schedule still works
✅ **Countdown Timers** - Live countdown to next wristband change
✅ **Fullscreen Kiosk** - No browser UI, just content
✅ **Color Coded** - Each wristband shows in its actual color
✅ **Auto-Play** - Videos loop continuously
✅ **Backward Compatible** - Can switch back to VLC anytime

---

## 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /kiosk` | Kiosk display page |
| `GET /wristband/schedule/status` | Current schedule status |
| `GET /stream/current` | Stream current video |
| `POST /play` | Play specific video |
| `POST /pause` | Pause video |
| `POST /stop` | Stop video |

All existing video management APIs still work!

---

## 🐛 Troubleshooting

### Kiosk doesn't launch?
```bash
# Check Chromium is installed
which chromium-browser

# Launch manually
cd server
./launch_kiosk.sh
```

### Video not playing?
- Ensure video is MP4 format
- Check `/status` endpoint shows `is_playing: true`
- Open browser console (F12) to see errors

### Schedule not updating?
- Visit `http://localhost:8000/wristband/schedule/status` to test API
- Check browser console for JavaScript errors

### Switch back to VLC?
```python
# In config.py
VIDEO_PLAYER_MODE = VideoPlayerMode.VLC
```

---

## 📖 Full Documentation

See [WRISTBAND_FEATURE.md](WRISTBAND_FEATURE.md) for complete documentation.

---

## 🎉 You're Done!

Your trampoline park display is now showing:
1. ✅ Promotional videos in fullscreen
2. ✅ Live wristband jump schedule
3. ✅ Countdown timers for customers
4. ✅ Your company branding colors

The system will automatically:
- Turn TV on/off per schedule
- Load and play videos
- Update wristband times every second
- Loop videos continuously

Enjoy! 🎪
