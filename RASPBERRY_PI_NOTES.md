# Raspberry Pi Specific Notes

## Chromium Package Name

On Raspberry Pi OS, the Chromium package is named `chromium`, not `chromium-browser`.

### Correct Commands

```bash
# Install
sudo apt-get install -y chromium

# Check version
chromium --version

# Run with display
DISPLAY=:0 chromium --version

# Launch in kiosk mode
DISPLAY=:0 chromium --kiosk http://localhost:8000/player
```

### Incorrect Commands (Don't Use)

```bash
# This will FAIL on Raspberry Pi OS
sudo apt-get install -y chromium-browser  # ❌ Package not found

chromium-browser --version  # ❌ Command not found
```

## Package Verification

```bash
# Check if chromium is installed
dpkg -l | grep chromium

# Output should show:
# ii  chromium  1:142.0.7444.175-1~deb13u1+rpt1  arm64  Chromium web browser
```

## Environment Setup

The system uses these environment variables for X Server:

```bash
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority  # Adjust username if different
```

## User Configuration

If you're not using the default `pi` user, update the `XAUTHORITY` path in:

**[server/src/chromium_video_manager.py](server/src/chromium_video_manager.py:95-98)**

```python
env = {
    "DISPLAY": ":0",
    "XAUTHORITY": "/home/YOUR_USERNAME/.Xauthority"  # Change this
}
```

## Testing Chromium Installation

```bash
# 1. Check installation
which chromium
# Output: /usr/bin/chromium

# 2. Verify version
chromium --version
# Output: Chromium 142.0.7444.175

# 3. Test with X Server
DISPLAY=:0 chromium --version
# Should show same version

# 4. Test kiosk mode (with X running)
DISPLAY=:0 chromium --kiosk --app=http://localhost:8000/player
```

## Common Issues

### Issue: "chromium-browser: command not found"

**Solution:** Use `chromium` instead of `chromium-browser`

```bash
# Wrong
chromium-browser --version  # ❌

# Correct
chromium --version  # ✅
```

### Issue: "Package chromium-browser has no installation candidate"

**Solution:** Install `chromium` package

```bash
# Wrong
sudo apt-get install chromium-browser  # ❌

# Correct
sudo apt-get install chromium  # ✅
```

### Issue: "Error: no DISPLAY environment variable specified"

**Solution:** Set DISPLAY variable

```bash
export DISPLAY=:0
chromium --version
```

Or run with inline environment:

```bash
DISPLAY=:0 chromium --version
```

## Systemd Service Configuration

The video server service automatically sets the DISPLAY variable:

```ini
[Service]
Environment=DISPLAY=:0
```

This is configured in `/etc/systemd/system/video-server.service`

## X Server Check

Verify X Server is running:

```bash
# Check process
ps aux | grep X
# Should show: /usr/lib/xorg/Xorg :0

# Check display
echo $DISPLAY
# Should show: :0

# Check X authority
ls -la ~/.Xauthority
# Should exist and be readable
```

## Raspberry Pi OS Version

This setup is tested on:
- **Raspberry Pi OS Lite 64-bit**
- **Debian version:** 13 (bookworm)
- **Chromium version:** 142.x

Verify your version:

```bash
cat /etc/os-release
# PRETTY_NAME="Debian GNU/Linux 13 (bookworm)"
```

## Performance Tips

### 1. Disable Unnecessary Services

```bash
sudo systemctl disable bluetooth
sudo systemctl disable cups  # If you don't need printing
```

### 2. Reduce Chromium Memory Usage

The configuration already includes:
- `--disable-gpu` - Saves memory
- `--no-sandbox` - Reduces overhead
- `--disable-features=TranslateUI` - Removes unneeded features

### 3. Video Optimization

For best performance on Raspberry Pi:
- **Format:** MP4 (H.264)
- **Resolution:** 1080p or lower
- **Bitrate:** 5-10 Mbps
- **FPS:** 30 or lower

## Debugging

### Enable Chromium Debug Output

Modify the chromium command in `chromium_video_manager.py`:

```python
command = [
    "chromium",
    "--kiosk",
    "--enable-logging",  # Add this
    "--v=1",  # Add this for verbose logging
    # ... rest of flags
    player_url
]
```

### View Chromium Logs

```bash
# Check system logs
journalctl -u video-server.service -f

# Check X Server logs
cat ~/.xsession-errors

# Check Chromium debug output
tail -f ~/.config/chromium/chrome_debug.log
```

## Quick Verification Script

Create a test script to verify everything:

```bash
#!/bin/bash
echo "=== Chromium Video Player Verification ==="
echo ""

echo "1. Checking Chromium installation..."
if command -v chromium &> /dev/null; then
    echo "   ✓ Chromium found: $(chromium --version)"
else
    echo "   ✗ Chromium not found"
fi

echo ""
echo "2. Checking X Server..."
if ps aux | grep -v grep | grep Xorg > /dev/null; then
    echo "   ✓ X Server running"
else
    echo "   ✗ X Server not running"
fi

echo ""
echo "3. Checking DISPLAY variable..."
if [ -n "$DISPLAY" ]; then
    echo "   ✓ DISPLAY=$DISPLAY"
else
    echo "   ✗ DISPLAY not set"
fi

echo ""
echo "4. Checking video server..."
if systemctl is-active --quiet video-server.service; then
    echo "   ✓ Video server running"
else
    echo "   ✗ Video server not running"
fi

echo ""
echo "5. Testing API..."
if curl -s http://localhost:8000/api/player/state > /dev/null; then
    echo "   ✓ API responding"
else
    echo "   ✗ API not responding"
fi

echo ""
echo "=== Verification Complete ==="
```

Save as `verify.sh`, make executable, and run:

```bash
chmod +x verify.sh
./verify.sh
```

## Summary

**Key Points:**
- ✅ Use `chromium` (not `chromium-browser`)
- ✅ Set `DISPLAY=:0` for X Server
- ✅ Run as the user who owns the X session (typically `pi`)
- ✅ Verify with `which chromium` and `chromium --version`

**All code has been updated to use the correct `chromium` command.**
