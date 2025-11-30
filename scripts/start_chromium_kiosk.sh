#!/bin/bash

# Chromium Kiosk Mode Launcher for Digital Signage
# This script sets up the X environment and launches the server

set -e

# Configuration
DISPLAY=:0
SERVER_DIR="/home/pi/DTC_RPI/server"
PYTHON_VENV="$SERVER_DIR/venv/bin/python"
SERVER_SCRIPT="$SERVER_DIR/server_chromium.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as the correct user
if [ "$USER" != "pi" ]; then
    log_warn "This script should be run as the 'pi' user"
fi

# Export display
export DISPLAY=$DISPLAY

# Kill any existing instances
log_info "Stopping existing Chromium instances..."
pkill -9 chromium-browser || true
pkill -9 chromium || true

# Wait a moment for cleanup
sleep 2

# Check if X server is running
if ! xset q &>/dev/null; then
    log_error "X server is not running on display $DISPLAY"
    log_info "Starting X server..."

    # Start X server if not running
    startx &
    sleep 5

    # Check again
    if ! xset q &>/dev/null; then
        log_error "Failed to start X server"
        exit 1
    fi
fi

log_info "X server is running on display $DISPLAY"

# Disable screen blanking and power management
log_info "Disabling screen saver and power management..."
xset s off
xset -dpms
xset s noblank

# Hide cursor after 1 second of inactivity
command -v unclutter &>/dev/null && unclutter -idle 1 -root &

# Set environment variables for the server
export SERVER_HOST="localhost"
export SERVER_PORT="8000"

# Change to server directory
cd "$SERVER_DIR"

# Activate virtual environment and start server
log_info "Starting FastAPI server with Chromium video manager..."

if [ -f "$PYTHON_VENV" ]; then
    $PYTHON_VENV "$SERVER_SCRIPT" &
    SERVER_PID=$!
    log_info "Server started with PID: $SERVER_PID"
else
    log_error "Python virtual environment not found at $PYTHON_VENV"
    log_error "Please create a virtual environment and install dependencies"
    exit 1
fi

# Wait for server to start
log_info "Waiting for server to initialize..."
sleep 5

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    log_error "Server failed to start"
    exit 1
fi

log_info "Chromium kiosk mode setup complete!"
log_info "Server PID: $SERVER_PID"
log_info "Player URL: http://localhost:8000/player"

# Keep script running and monitor server
while kill -0 $SERVER_PID 2>/dev/null; do
    sleep 10
done

log_error "Server process died unexpectedly"
exit 1
