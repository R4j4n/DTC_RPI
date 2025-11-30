#!/bin/bash

# Chromium Video Player Setup Script for Raspberry Pi OS 64-bit
# This script installs and configures everything needed for HTML5 video playback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration - Use current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$SCRIPT_DIR"
SERVER_DIR="$INSTALL_DIR/server"
SCRIPTS_DIR="$INSTALL_DIR/scripts"
CURRENT_USER="$(whoami)"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}==>${NC} $1\n"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please run this script as a regular user, not as root"
    log_info "Use: ./setup_chromium_player.sh"
    exit 1
fi

log_info "Running as user: $CURRENT_USER"
log_info "Install directory: $INSTALL_DIR"

log_step "Chromium Video Player Setup for Raspberry Pi"

# Update package lists
log_step "Step 1: Updating package lists"
sudo apt-get update

# Install required system packages
log_step "Step 2: Installing system packages"
log_info "Installing Chromium browser, X server, and utilities..."

sudo apt-get install -y \
    chromium \
    xserver-xorg \
    xinit \
    x11-xserver-utils \
    unclutter \
    python3-pip \
    python3-venv \
    python3-dev \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libasound2

log_info "System packages installed successfully"

# Enable hardware video acceleration
log_step "Step 3: Configuring hardware video acceleration"

# Check if in video group
if ! groups | grep -q video; then
    log_info "Adding user to video group for hardware acceleration..."
    sudo usermod -a -G video $USER
    log_warn "You will need to log out and back in for group changes to take effect"
fi

# Configure GPU memory
log_info "Checking GPU memory allocation..."
if ! grep -q "gpu_mem=256" /boot/config.txt 2>/dev/null; then
    log_info "Setting GPU memory to 256MB..."
    echo "gpu_mem=256" | sudo tee -a /boot/config.txt
fi

# Enable OpenGL driver
if ! grep -q "dtoverlay=vc4-kms-v3d" /boot/config.txt 2>/dev/null; then
    log_info "Enabling OpenGL driver..."
    echo "dtoverlay=vc4-kms-v3d" | sudo tee -a /boot/config.txt
fi

# Create Python virtual environment
log_step "Step 4: Setting up Python environment"

if [ ! -d "$SERVER_DIR/venv" ]; then
    log_info "Creating Python virtual environment..."
    cd "$SERVER_DIR"
    python3 -m venv venv
    log_info "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

# Install Python dependencies
log_info "Installing Python dependencies..."
source "$SERVER_DIR/venv/bin/activate"

# Install FastAPI and dependencies
pip install --upgrade pip
pip install fastapi uvicorn websockets python-multipart aiofiles

# Check if requirements.txt exists and install
if [ -f "$SERVER_DIR/requirements.txt" ]; then
    log_info "Installing from requirements.txt..."
    pip install -r "$SERVER_DIR/requirements.txt"
fi

deactivate

# Configure X server auto-start
log_step "Step 5: Configuring X server"

# Create .xinitrc if it doesn't exist
if [ ! -f "$HOME/.xinitrc" ]; then
    log_info "Creating .xinitrc for auto-start..."
    cat > "$HOME/.xinitrc" << 'EOF'
#!/bin/bash

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Hide mouse cursor
unclutter -idle 1 -root &

# Execute window manager (lightweight)
exec openbox-session
EOF
    chmod +x "$HOME/.xinitrc"
fi

# Configure auto-login (if not already configured)
log_step "Step 6: Configuring auto-login to desktop"

if [ -f "/etc/systemd/system/getty@tty1.service.d/autologin.conf" ]; then
    log_info "Auto-login already configured"
else
    log_info "Setting up auto-login..."
    sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
    sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $CURRENT_USER --noclear %I \$TERM
EOF
fi

# Install and configure systemd service
log_step "Step 7: Installing systemd service"

# Make launcher script executable
chmod +x "$SCRIPTS_DIR/start_chromium_kiosk.sh"

# Create systemd service file dynamically
log_info "Creating systemd service..."
sudo tee /etc/systemd/system/chromium-kiosk.service > /dev/null << EOF
[Unit]
Description=Chromium Kiosk Mode Digital Signage Server
After=network.target graphical.target
Wants=graphical.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$SERVER_DIR
Environment="DISPLAY=:0"
Environment="XAUTHORITY=$HOME/.Xauthority"
Environment="HOME=$HOME"
ExecStartPre=/bin/sleep 10
ExecStart=/bin/bash $SCRIPTS_DIR/start_chromium_kiosk.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=graphical.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable the service
log_info "Enabling chromium-kiosk service..."
sudo systemctl enable chromium-kiosk.service

log_info "Service installed and enabled"

# Create directories for videos
log_step "Step 8: Creating video directories"

mkdir -p "$SERVER_DIR/uploaded_videos"
mkdir -p "$SERVER_DIR/uploaded_videos/compressed"
mkdir -p "$SERVER_DIR/web"

log_info "Video directories created"

# Set up HDMI-CEC (if not already done)
log_step "Step 9: Checking HDMI-CEC configuration"

if ! command -v cec-client &> /dev/null; then
    log_info "Installing cec-utils for TV control..."
    sudo apt-get install -y cec-utils
fi

# Test CEC
log_info "Testing HDMI-CEC connection..."
if timeout 3 echo 'scan' | cec-client -s -d 1 &>/dev/null; then
    log_info "HDMI-CEC is working"
else
    log_warn "HDMI-CEC might not be configured correctly"
    log_warn "Make sure your TV supports CEC and it's enabled in TV settings"
fi

# Display summary
log_step "Installation Complete!"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Server directory: ${BLUE}$SERVER_DIR${NC}"
echo -e "Scripts directory: ${BLUE}$SCRIPTS_DIR${NC}"
echo -e "Video upload directory: ${BLUE}$SERVER_DIR/uploaded_videos${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "1. ${GREEN}Reboot${NC} your Raspberry Pi to apply all changes:"
echo -e "   ${BLUE}sudo reboot${NC}"
echo ""
echo -e "2. After reboot, the service will start automatically"
echo ""
echo -e "3. Access the server at: ${BLUE}http://$(hostname -I | awk '{print $1}'):8000${NC}"
echo ""
echo -e "4. To manually control the service:"
echo -e "   Start:   ${BLUE}sudo systemctl start chromium-kiosk${NC}"
echo -e "   Stop:    ${BLUE}sudo systemctl stop chromium-kiosk${NC}"
echo -e "   Status:  ${BLUE}sudo systemctl status chromium-kiosk${NC}"
echo -e "   Logs:    ${BLUE}journalctl -u chromium-kiosk -f${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"

log_warn "A reboot is required to complete the setup!"
echo ""
read -p "Would you like to reboot now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Rebooting..."
    sudo reboot
else
    log_info "Please reboot manually when ready: sudo reboot"
fi
