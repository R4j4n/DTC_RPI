#!/bin/bash

# Chromium Video Player Setup Script for Raspberry Pi OS Lite
# This script installs and configures all dependencies for the Chromium-based video player

set -e  # Exit on error

echo "=========================================="
echo "Chromium Video Player Setup"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install X Server (minimal)
echo ""
echo "Installing X Server..."
sudo apt-get install -y --no-install-recommends \
    xserver-xorg \
    x11-xserver-utils \
    xinit \
    openbox

# Install Chromium
echo ""
echo "Installing Chromium browser..."
sudo apt-get install -y chromium

# Verify Chromium installation
echo ""
echo "Verifying Chromium installation..."
if command -v chromium &> /dev/null; then
    CHROMIUM_VERSION=$(chromium --version)
    echo "✓ Chromium installed: $CHROMIUM_VERSION"
else
    echo "✗ Chromium installation failed"
    exit 1
fi

# Configure X Server auto-start
echo ""
echo "Configuring X Server auto-start..."

sudo tee /etc/systemd/system/xserver.service > /dev/null <<EOF
[Unit]
Description=X Server
After=network.target

[Service]
Type=simple
User=$USER
Environment=DISPLAY=:0
ExecStart=/usr/bin/startx
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable X Server service
sudo systemctl enable xserver.service

# Configure .xinitrc
echo ""
echo "Configuring .xinitrc..."

cat > ~/.xinitrc <<EOF
#!/bin/bash
xset -dpms      # Disable DPMS (Energy Star) features
xset s off      # Disable screen saver
xset s noblank  # Don't blank the video device
openbox-session
EOF

chmod +x ~/.xinitrc

# Configure HDMI settings
echo ""
echo "Configuring HDMI settings..."

if ! grep -q "hdmi_blanking" /boot/config.txt; then
    sudo bash -c 'cat >> /boot/config.txt <<EOF

# Video player settings (added by setup script)
hdmi_blanking=1
hdmi_force_hotplug=1
hdmi_drive=2
EOF'
    echo "✓ HDMI settings added to /boot/config.txt"
else
    echo "✓ HDMI settings already configured"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."

pip3 install --upgrade fastapi uvicorn python-multipart

# Create templates directory
echo ""
echo "Creating required directories..."

cd "$(dirname "$0")/server"
mkdir -p templates
mkdir -p uploaded_videos/compressed
mkdir -p auth

echo "✓ Directories created"

# Create systemd service for video server
echo ""
echo "Creating systemd service for video server..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

sudo tee /etc/systemd/system/video-server.service > /dev/null <<EOF
[Unit]
Description=Video Server
After=network.target xserver.service
Requires=xserver.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR/server
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 $SCRIPT_DIR/server/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable video server service
sudo systemctl enable video-server.service

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Installed components:"
echo "  ✓ X Server (minimal)"
echo "  ✓ Chromium Browser"
echo "  ✓ Python dependencies"
echo "  ✓ Systemd services configured"
echo ""
echo "Services:"
echo "  - xserver.service (X Server)"
echo "  - video-server.service (FastAPI server)"
echo ""
echo "Next steps:"
echo "  1. Reboot your Raspberry Pi:"
echo "     sudo reboot"
echo ""
echo "  2. After reboot, check service status:"
echo "     sudo systemctl status xserver.service"
echo "     sudo systemctl status video-server.service"
echo ""
echo "  3. Test the API:"
echo "     curl http://localhost:8000/status"
echo ""
echo "  4. View logs:"
echo "     journalctl -u video-server.service -f"
echo ""
echo "For troubleshooting, see: CHROMIUM_SETUP.md"
echo ""
