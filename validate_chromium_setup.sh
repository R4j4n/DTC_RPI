#!/bin/bash

# Validation Script for Chromium Video Player Setup
# This script checks if all components are properly installed

set +e  # Don't exit on errors, we want to check everything

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS="${GREEN}✓${NC}"
FAIL="${RED}✗${NC}"
WARN="${YELLOW}⚠${NC}"

INSTALL_DIR="/home/pi/DTC_RPI"
SERVER_DIR="$INSTALL_DIR/server"

errors=0
warnings=0
passes=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Chromium Video Player Setup Validation${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to check and report
check() {
    local test_name="$1"
    local command="$2"

    if eval "$command" &>/dev/null; then
        echo -e "$PASS $test_name"
        ((passes++))
        return 0
    else
        echo -e "$FAIL $test_name"
        ((errors++))
        return 1
    fi
}

check_warn() {
    local test_name="$1"
    local command="$2"

    if eval "$command" &>/dev/null; then
        echo -e "$PASS $test_name"
        ((passes++))
        return 0
    else
        echo -e "$WARN $test_name (optional)"
        ((warnings++))
        return 1
    fi
}

# Check system packages
echo -e "${BLUE}System Packages${NC}"
check "Chromium browser installed" "command -v chromium-browser"
check "X server installed" "command -v X"
check "xinit installed" "command -v xinit"
check "xset installed" "command -v xset"
check_warn "unclutter installed" "command -v unclutter"
check "Python 3 installed" "command -v python3"
check "pip installed" "command -v pip3"
echo ""

# Check HDMI-CEC
echo -e "${BLUE}HDMI-CEC${NC}"
check "cec-client installed" "command -v cec-client"
check_warn "CEC device available" "test -e /dev/cec0 || ls /dev/vchiq"
echo ""

# Check file structure
echo -e "${BLUE}File Structure${NC}"
check "Main directory exists" "test -d $INSTALL_DIR"
check "Server directory exists" "test -d $SERVER_DIR"
check "Scripts directory exists" "test -d $INSTALL_DIR/scripts"
check "Systemd directory exists" "test -d $INSTALL_DIR/systemd"
check "Video upload directory exists" "test -d $SERVER_DIR/uploaded_videos"
check "Compressed video directory exists" "test -d $SERVER_DIR/uploaded_videos/compressed"
check "Web directory exists" "test -d $SERVER_DIR/web"
echo ""

# Check key files
echo -e "${BLUE}Key Files${NC}"
check "Chromium video manager exists" "test -f $SERVER_DIR/src/chromium_video_manager.py"
check "HTML video player exists" "test -f $SERVER_DIR/web/video_player.html"
check "Server (Chromium) exists" "test -f $SERVER_DIR/server_chromium.py"
check "Launcher script exists" "test -f $INSTALL_DIR/scripts/start_chromium_kiosk.sh"
check "Launcher script is executable" "test -x $INSTALL_DIR/scripts/start_chromium_kiosk.sh"
check "Systemd service file exists" "test -f $INSTALL_DIR/systemd/chromium-kiosk.service"
echo ""

# Check Python environment
echo -e "${BLUE}Python Environment${NC}"
check "Virtual environment exists" "test -d $SERVER_DIR/venv"
if [ -f "$SERVER_DIR/venv/bin/python" ]; then
    echo -e "$PASS Virtual environment Python exists"
    ((passes++))

    # Check Python packages
    source "$SERVER_DIR/venv/bin/activate" 2>/dev/null
    check "FastAPI installed" "python -c 'import fastapi' 2>/dev/null"
    check "Uvicorn installed" "python -c 'import uvicorn' 2>/dev/null"
    check "WebSockets installed" "python -c 'import websockets' 2>/dev/null"
    check_warn "Aiofiles installed" "python -c 'import aiofiles' 2>/dev/null"
    deactivate 2>/dev/null
else
    echo -e "$FAIL Virtual environment Python exists"
    ((errors++))
fi
echo ""

# Check systemd service
echo -e "${BLUE}Systemd Service${NC}"
check "Service file installed" "test -f /etc/systemd/system/chromium-kiosk.service"
if systemctl list-unit-files | grep -q chromium-kiosk.service; then
    echo -e "$PASS Service registered with systemd"
    ((passes++))

    if systemctl is-enabled chromium-kiosk.service &>/dev/null; then
        echo -e "$PASS Service enabled for auto-start"
        ((passes++))
    else
        echo -e "$WARN Service not enabled (run: sudo systemctl enable chromium-kiosk)"
        ((warnings++))
    fi

    if systemctl is-active chromium-kiosk.service &>/dev/null; then
        echo -e "$PASS Service is currently running"
        ((passes++))
    else
        echo -e "$WARN Service not running (run: sudo systemctl start chromium-kiosk)"
        ((warnings++))
    fi
else
    echo -e "$FAIL Service registered with systemd"
    ((errors++))
fi
echo ""

# Check GPU configuration
echo -e "${BLUE}GPU Configuration${NC}"
if [ -f /boot/config.txt ]; then
    if grep -q "gpu_mem" /boot/config.txt; then
        gpu_mem=$(grep gpu_mem /boot/config.txt | tail -1 | cut -d= -f2)
        if [ "$gpu_mem" -ge 256 ]; then
            echo -e "$PASS GPU memory allocated: ${gpu_mem}MB"
            ((passes++))
        else
            echo -e "$WARN GPU memory: ${gpu_mem}MB (recommended: 256MB+)"
            ((warnings++))
        fi
    else
        echo -e "$WARN GPU memory not configured in /boot/config.txt"
        ((warnings++))
    fi

    if grep -q "vc4-kms-v3d" /boot/config.txt; then
        echo -e "$PASS OpenGL driver enabled (vc4-kms-v3d)"
        ((passes++))
    else
        echo -e "$WARN OpenGL driver not enabled in /boot/config.txt"
        ((warnings++))
    fi
else
    echo -e "$FAIL /boot/config.txt not found"
    ((errors++))
fi
echo ""

# Check user permissions
echo -e "${BLUE}User Permissions${NC}"
if groups | grep -q video; then
    echo -e "$PASS User in 'video' group"
    ((passes++))
else
    echo -e "$WARN User not in 'video' group (run: sudo usermod -a -G video \$USER)"
    ((warnings++))
fi
echo ""

# Check X server
echo -e "${BLUE}X Server${NC}"
if xset q &>/dev/null; then
    echo -e "$PASS X server is running"
    ((passes++))
else
    echo -e "$WARN X server not running (normal if not in graphical mode)"
    ((warnings++))
fi
echo ""

# Check network
echo -e "${BLUE}Network${NC}"
check "Network interface available" "ip link show | grep -q 'state UP'"
if command -v hostname &>/dev/null; then
    ip_addr=$(hostname -I | awk '{print $1}')
    if [ -n "$ip_addr" ]; then
        echo -e "$PASS IP Address: $ip_addr"
        ((passes++))
    else
        echo -e "$WARN No IP address assigned"
        ((warnings++))
    fi
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "Passed:   ${GREEN}$passes${NC}"
echo -e "Warnings: ${YELLOW}$warnings${NC}"
echo -e "Errors:   ${RED}$errors${NC}"
echo ""

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! System is ready.${NC}"
    exit_code=0
elif [ $errors -eq 0 ]; then
    echo -e "${YELLOW}⚠ Some optional components are missing.${NC}"
    echo -e "${YELLOW}  System should work but may have reduced functionality.${NC}"
    exit_code=0
else
    echo -e "${RED}✗ Critical errors found. Please fix before proceeding.${NC}"
    exit_code=1
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
if [ $errors -gt 0 ]; then
    echo "1. Fix the errors listed above"
    echo "2. Run this validation script again"
    echo "3. Review the installation guide if needed"
elif ! systemctl is-active chromium-kiosk.service &>/dev/null; then
    echo "1. Start the service: sudo systemctl start chromium-kiosk"
    echo "2. Check status: sudo systemctl status chromium-kiosk"
    echo "3. View logs: journalctl -u chromium-kiosk -f"
else
    echo "1. System is running!"
    echo "2. Access server at: http://$ip_addr:8000"
    echo "3. View logs: journalctl -u chromium-kiosk -f"
fi

exit $exit_code
