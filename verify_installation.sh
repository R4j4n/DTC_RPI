#!/bin/bash

# Verification Script for Chromium Video Player Installation
# Run this after installation to verify everything is working

set -e

echo "=========================================="
echo "Chromium Video Player - Installation Verification"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# 1. Check Chromium installation
echo "1. Checking Chromium installation..."
if command -v chromium &> /dev/null; then
    VERSION=$(chromium --version 2>/dev/null || echo "unknown")
    check_pass "Chromium installed: $VERSION"
else
    check_fail "Chromium not found. Run: sudo apt-get install -y chromium"
fi
echo ""

# 2. Check X Server
echo "2. Checking X Server..."
if ps aux | grep -v grep | grep Xorg > /dev/null; then
    check_pass "X Server running"
else
    check_warn "X Server not running. It should start automatically on boot."
    check_warn "Start manually: sudo systemctl start xserver.service"
fi

if [ -n "$DISPLAY" ]; then
    check_pass "DISPLAY environment variable set: $DISPLAY"
else
    check_warn "DISPLAY not set (normal if not in X session)"
fi
echo ""

# 3. Check X Server service
echo "3. Checking X Server systemd service..."
if systemctl list-unit-files | grep -q xserver.service; then
    if systemctl is-enabled --quiet xserver.service; then
        check_pass "X Server service enabled"
    else
        check_warn "X Server service not enabled. Enable with: sudo systemctl enable xserver.service"
    fi
else
    check_warn "X Server service not found (may need to be created)"
fi
echo ""

# 4. Check video server service
echo "4. Checking video server service..."
if systemctl list-unit-files | grep -q video-server.service; then
    check_pass "Video server service installed"

    if systemctl is-enabled --quiet video-server.service; then
        check_pass "Video server service enabled"
    else
        check_warn "Video server service not enabled. Enable with: sudo systemctl enable video-server.service"
    fi

    if systemctl is-active --quiet video-server.service; then
        check_pass "Video server service running"
    else
        check_warn "Video server service not running. Start with: sudo systemctl start video-server.service"
    fi
else
    check_fail "Video server service not installed"
fi
echo ""

# 5. Check Python dependencies
echo "5. Checking Python dependencies..."
if python3 -c "import fastapi" 2>/dev/null; then
    check_pass "FastAPI installed"
else
    check_fail "FastAPI not found. Install with: pip3 install fastapi"
fi

if python3 -c "import uvicorn" 2>/dev/null; then
    check_pass "Uvicorn installed"
else
    check_fail "Uvicorn not found. Install with: pip3 install uvicorn"
fi
echo ""

# 6. Check project structure
echo "6. Checking project structure..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$SCRIPT_DIR/server/server.py" ]; then
    check_pass "server.py found"
else
    check_fail "server.py not found at $SCRIPT_DIR/server/server.py"
fi

if [ -f "$SCRIPT_DIR/server/src/chromium_video_manager.py" ]; then
    check_pass "chromium_video_manager.py found"
else
    check_fail "chromium_video_manager.py not found"
fi

if [ -f "$SCRIPT_DIR/server/templates/video_player.html" ]; then
    check_pass "video_player.html found"
else
    check_fail "video_player.html not found"
fi

if [ -d "$SCRIPT_DIR/server/uploaded_videos" ]; then
    check_pass "uploaded_videos directory exists"
else
    check_warn "uploaded_videos directory not found (will be created on first run)"
fi
echo ""

# 7. Check API availability
echo "7. Checking API availability..."
if curl -s http://localhost:8000/api/player/state > /dev/null 2>&1; then
    check_pass "API responding at http://localhost:8000"
else
    check_warn "API not responding (server may not be running)"
fi
echo ""

# 8. Check HDMI configuration
echo "8. Checking HDMI configuration..."
if grep -q "hdmi_blanking" /boot/config.txt 2>/dev/null; then
    check_pass "HDMI settings configured in /boot/config.txt"
else
    check_warn "HDMI settings not found in /boot/config.txt (optional)"
fi
echo ""

# 9. Check .xinitrc
echo "9. Checking X initialization..."
if [ -f "$HOME/.xinitrc" ]; then
    check_pass ".xinitrc exists"
    if [ -x "$HOME/.xinitrc" ]; then
        check_pass ".xinitrc is executable"
    else
        check_warn ".xinitrc is not executable. Fix with: chmod +x ~/.xinitrc"
    fi
else
    check_warn ".xinitrc not found (should be created during setup)"
fi
echo ""

# 10. Quick functionality test
echo "10. Running quick functionality test..."
cd "$SCRIPT_DIR/server" 2>/dev/null

if python3 -c "from src.chromium_video_manager import ChromiumVideoManager" 2>/dev/null; then
    check_pass "ChromiumVideoManager can be imported"
else
    check_fail "Cannot import ChromiumVideoManager"
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Your system is ready to use."
    echo ""
    echo "Next steps:"
    echo "  1. Upload a video via the API"
    echo "  2. Play it with: curl -X POST -H 'AUTH: your-key' http://localhost:8000/play"
    echo "  3. Check HDMI output"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo "System should work, but check the warnings above."
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    fi
    echo ""
    echo "Please fix the errors above before proceeding."
    echo "Refer to CHROMIUM_SETUP.md for detailed instructions."
fi

echo ""
echo "For troubleshooting, see:"
echo "  - CHROMIUM_SETUP.md"
echo "  - RASPBERRY_PI_NOTES.md"
echo "  - Check logs: journalctl -u video-server.service -f"
echo ""

exit 0
