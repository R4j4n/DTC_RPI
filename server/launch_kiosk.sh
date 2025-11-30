#!/bin/bash
# Kiosk Mode Launcher for Trampoline Park Display
# This script launches Chromium in fullscreen kiosk mode

# Configuration
KIOSK_URL="http://localhost:8000/kiosk"

# Set DISPLAY environment variable for HDMI output
export DISPLAY=:0

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

# Kill any existing Chromium instances
echo "Cleaning up old browser instances..."
pkill -f chromium-browser 2>/dev/null || true
sleep 1

# Disable screen blanking and power saving
echo "Configuring display settings..."
DISPLAY=:0 xset s off 2>/dev/null || true
DISPLAY=:0 xset -dpms 2>/dev/null || true
DISPLAY=:0 xset s noblank 2>/dev/null || true

# Hide cursor after inactivity
unclutter -idle 0.1 &

# Launch Chromium in kiosk mode on HDMI display
echo "Launching kiosk display on HDMI..."
DISPLAY=:0 chromium-browser \
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
    "$KIOSK_URL" &

echo "Kiosk launched successfully!"
