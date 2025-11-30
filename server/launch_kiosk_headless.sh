#!/bin/bash
# Kiosk Mode Launcher for Raspberry Pi OS Lite
# This script starts X11 server and launches Chromium in kiosk mode

# Configuration
KIOSK_URL="http://localhost:8000/kiosk"

# Wait for server to be ready
echo "Waiting for server to start..."
for i in {1..30}; do
    if curl -s "$KIOSK_URL" > /dev/null 2>&1; then
        echo "Server is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

# Kill any existing X or Chromium instances
echo "Cleaning up old instances..."
pkill -f chromium 2>/dev/null || true
pkill -f openbox 2>/dev/null || true
sleep 1

# Create temporary directory for X11
mkdir -p /tmp/.kiosk

# Detect chromium binary (could be 'chromium' or 'chromium-browser')
CHROMIUM_BIN=$(which chromium 2>/dev/null || which chromium-browser 2>/dev/null || echo "/usr/bin/chromium")

# Start X server with Openbox and Chromium
echo "Starting X11 server and kiosk display using $CHROMIUM_BIN..."
startx $CHROMIUM_BIN \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-session-crashed-bubble \
    --disable-component-update \
    --start-fullscreen \
    --autoplay-policy=no-user-gesture-required \
    --disable-features=TranslateUI \
    --check-for-update-interval=31536000 \
    --window-position=0,0 \
    --user-data-dir=/tmp/.kiosk \
    "$KIOSK_URL" -- :0 vt1 &

# Wait a bit for X to start
sleep 3

# Disable screen blanking (after X starts)
DISPLAY=:0 xset s off 2>/dev/null || true
DISPLAY=:0 xset -dpms 2>/dev/null || true
DISPLAY=:0 xset s noblank 2>/dev/null || true

# Hide cursor
DISPLAY=:0 unclutter -idle 0.1 -root &

echo "Kiosk launched successfully!"
echo "Video should now be visible on HDMI display"
