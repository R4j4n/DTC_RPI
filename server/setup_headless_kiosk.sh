#!/bin/bash
# Setup Script for Headless Raspberry Pi Kiosk Display

echo "=================================="
echo "Headless Kiosk Setup for Raspberry Pi"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run as regular user (not sudo)"
    exit 1
fi

echo "📦 Step 1: Installing packages..."
sudo apt-get update
sudo apt-get install -y \
    chromium-browser \
    xserver-xorg \
    x11-xserver-utils \
    xinit \
    openbox \
    unclutter \
    xdotool \
    curl

echo ""
echo "✅ Packages installed"
echo ""

echo "📝 Step 2: Creating X configuration..."

# Create .xinitrc
cat > ~/.xinitrc << 'EOF'
#!/bin/bash

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Hide cursor
unclutter -idle 0.1 -root &

# Wait a bit for everything to stabilize
sleep 3

# Launch kiosk (if server is running)
if [ -f "$HOME/Documents/GitHub/DTC_RPI/server/launch_kiosk.sh" ]; then
    $HOME/Documents/GitHub/DTC_RPI/server/launch_kiosk.sh &
fi

# Keep X running
exec openbox-session
EOF

chmod +x ~/.xinitrc

echo "✅ X configuration created"
echo ""

echo "📝 Step 3: Creating systemd services..."

# Create X server service
sudo tee /etc/systemd/system/kiosk-x.service > /dev/null << 'EOF'
[Unit]
Description=X Server for Kiosk Display
After=multi-user.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
ExecStart=/usr/bin/xinit /home/pi/.xinitrc -- :0 vt7 -nocursor
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Create DTC server service
SCRIPT_DIR="$HOME/Documents/GitHub/DTC_RPI/server"
sudo tee /etc/systemd/system/dtc-server.service > /dev/null << EOF
[Unit]
Description=DTC Trampoline Park Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd services created"
echo ""

echo "🔄 Step 4: Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable kiosk-x.service
sudo systemctl enable dtc-server.service

echo "✅ Services enabled"
echo ""

echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Reboot your Raspberry Pi:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, the system will:"
echo "   - Start X server on HDMI"
echo "   - Start DTC server automatically"
echo "   - Launch kiosk display in Chromium"
echo ""
echo "📊 Useful Commands:"
echo ""
echo "Check X server status:"
echo "  sudo systemctl status kiosk-x.service"
echo ""
echo "Check DTC server status:"
echo "  sudo systemctl status dtc-server.service"
echo ""
echo "View X server logs:"
echo "  journalctl -u kiosk-x.service -f"
echo ""
echo "View DTC server logs:"
echo "  journalctl -u dtc-server.service -f"
echo ""
echo "Restart services:"
echo "  sudo systemctl restart kiosk-x.service"
echo "  sudo systemctl restart dtc-server.service"
echo ""
echo "=================================="
