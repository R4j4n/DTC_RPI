#!/bin/bash
# Kiosk Mode Launcher for Trampoline Park Display
# This script launches Chromium in fullscreen kiosk mode

# Configuration
KIOSK_URL="http://localhost:8000/kiosk"
DISPLAY=:0

# Wait for server to be ready
echo "Waiting for server to start..."
for i in {1..30}; do
    if curl -s "$KIOSK_URL" > /dev/null; then
        echo "Server is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

# Disable screen blanking and power saving
xset s off
xset -dpms
xset s noblank

# Hide cursor after inactivity
unclutter -idle 0.1 &

# Launch Chromium in kiosk mode
chromium-browser \
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
    "$KIOSK_URL"
