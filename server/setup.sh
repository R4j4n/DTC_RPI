#!/bin/bash

#############################################
# DTC_RPI Server Setup Script
# This script will:
# - Install system dependencies
# - Install Python dependencies
# - Configure WiFi credentials
# - Set up the server for first run
#############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

#############################################
# Helper Functions
#############################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root or with sudo"
        print_info "The script will ask for sudo password when needed"
        exit 1
    fi
}

#############################################
# System Information
#############################################

print_header "DTC_RPI Server Setup"

print_info "Detecting system information..."
echo "Hostname: $(hostname)"
echo "OS: $(uname -s)"
echo "Architecture: $(uname -m)"
echo "Current User: $(whoami)"
echo "Script Directory: $SCRIPT_DIR"
echo ""

check_root

#############################################
# Update System
#############################################

print_header "Updating System Packages"

print_info "Updating package lists..."
sudo apt-get update || {
    print_error "Failed to update package lists"
    exit 1
}

print_success "Package lists updated"

#############################################
# Install System Dependencies
#############################################

print_header "Installing System Dependencies"

SYSTEM_PACKAGES=(
    "python3"
    "python3-pip"
    "python3-venv"
    "network-manager"
    "vlc"
    "libcec-dev"
    "cec-utils"
    "ffmpeg"
    "git"
)

print_info "The following packages will be installed:"
printf '%s\n' "${SYSTEM_PACKAGES[@]}"
echo ""

read -p "Continue with installation? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Installation cancelled by user"
    exit 0
fi

for package in "${SYSTEM_PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $package "; then
        print_info "$package is already installed"
    else
        print_info "Installing $package..."
        sudo apt-get install -y "$package" || {
            print_error "Failed to install $package"
            exit 1
        }
        print_success "$package installed"
    fi
done

#############################################
# Enable and Start NetworkManager
#############################################

print_header "Configuring NetworkManager"

print_info "Enabling NetworkManager service..."
sudo systemctl enable NetworkManager || print_warning "Could not enable NetworkManager"

print_info "Starting NetworkManager service..."
sudo systemctl start NetworkManager || print_warning "Could not start NetworkManager"

sleep 2

if systemctl is-active --quiet NetworkManager; then
    print_success "NetworkManager is running"
else
    print_warning "NetworkManager may not be running properly"
    print_info "You may need to reboot and run this script again"
fi

#############################################
# Create Python Virtual Environment
#############################################

print_header "Setting Up Python Virtual Environment"

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing virtual environment..."
        rm -rf venv
        print_info "Creating new virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
else
    print_info "Creating virtual environment..."
    python3 -m venv venv || {
        print_error "Failed to create virtual environment"
        exit 1
    }
    print_success "Virtual environment created"
fi

#############################################
# Install Python Dependencies
#############################################

print_header "Installing Python Dependencies"

print_info "Activating virtual environment..."
source venv/bin/activate || {
    print_error "Failed to activate virtual environment"
    exit 1
}

print_info "Upgrading pip..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    print_info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt || {
        print_error "Failed to install Python dependencies"
        exit 1
    }
    print_success "Python dependencies installed"
else
    print_warning "requirements.txt not found"
    print_info "Installing common dependencies..."
    pip install fastapi uvicorn python-vlc zeroconf netifaces pycec || {
        print_error "Failed to install dependencies"
        exit 1
    }
fi

#############################################
# WiFi Configuration
#############################################

print_header "WiFi Configuration"

print_info "This setup will configure WiFi networks for automatic connection"
echo ""

# Check if wifi_config.json already exists
if [ -f "wifi_config.json" ]; then
    print_warning "WiFi configuration file already exists"
    read -p "Do you want to reconfigure WiFi? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Keeping existing WiFi configuration"
        SKIP_WIFI_CONFIG=true
    fi
fi

if [ "$SKIP_WIFI_CONFIG" != true ]; then
    # Array to store network configurations
    declare -a NETWORKS

    # Ask how many networks to configure
    echo -e "${BLUE}How many WiFi networks do you want to configure?${NC}"
    read -p "Enter number (1-5, default: 1): " NUM_NETWORKS
    NUM_NETWORKS=${NUM_NETWORKS:-1}

    # Validate input
    if ! [[ "$NUM_NETWORKS" =~ ^[1-5]$ ]]; then
        print_warning "Invalid number, using default (1)"
        NUM_NETWORKS=1
    fi

    echo ""

    # Collect network information
    for i in $(seq 1 $NUM_NETWORKS); do
        print_info "Configuring Network #$i"
        echo ""

        # Get SSID
        read -p "  WiFi SSID (network name): " SSID
        while [ -z "$SSID" ]; do
            print_warning "SSID cannot be empty"
            read -p "  WiFi SSID (network name): " SSID
        done

        # Get Password (hidden input)
        read -s -p "  WiFi Password: " PASSWORD
        echo ""
        while [ -z "$PASSWORD" ]; do
            print_warning "Password cannot be empty"
            read -s -p "  WiFi Password: " PASSWORD
            echo ""
        done

        # Get Priority
        read -p "  Priority (1=highest, default: $i): " PRIORITY
        PRIORITY=${PRIORITY:-$i}

        # Store network info
        NETWORKS+=("{\"ssid\": \"$SSID\", \"password\": \"$PASSWORD\", \"priority\": $PRIORITY}")

        echo ""
        print_success "Network #$i configured: $SSID (Priority: $PRIORITY)"
        echo ""
    done

    # Create JSON configuration
    print_info "Creating wifi_config.json..."

    # Join array elements with commas
    NETWORKS_JSON=$(IFS=,; echo "${NETWORKS[*]}")

    # Write JSON file
    cat > wifi_config.json << EOF
{
  "networks": [
    $NETWORKS_JSON
  ]
}
EOF

    # Secure the file
    chmod 600 wifi_config.json

    print_success "WiFi configuration saved to wifi_config.json"
    print_info "File permissions set to 600 (owner read/write only)"

    # Test if we can connect to any configured network
    echo ""
    read -p "Do you want to test WiFi connection now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Testing WiFi connection..."

        # Get first network
        FIRST_SSID=$(echo "$SSID" | head -1)

        print_info "Checking current WiFi status..."
        CURRENT_SSID=$(iwgetid -r 2>/dev/null || echo "")

        if [ -n "$CURRENT_SSID" ]; then
            print_success "Already connected to: $CURRENT_SSID"
        else
            print_warning "Not currently connected to WiFi"
            print_info "WiFi manager will handle connection when server starts"
        fi
    fi
fi

#############################################
# Create Authentication
#############################################

print_header "Authentication Setup"

if [ -d "auth" ] && [ -f "auth/auth.txt" ]; then
    print_info "Authentication already configured"
else
    print_info "Setting up authentication..."

    read -s -p "Enter server password: " SERVER_PASSWORD
    echo ""

    if [ -n "$SERVER_PASSWORD" ]; then
        mkdir -p auth
        python3 create_pass.py "$SERVER_PASSWORD" 2>/dev/null || {
            print_warning "Could not run create_pass.py automatically"
            print_info "Please run: python3 create_pass.py after setup"
        }
        print_success "Authentication configured"
    else
        print_warning "No password set, skipping authentication setup"
        print_info "You can run 'python3 create_pass.py' later to set up authentication"
    fi
fi

#############################################
# Create Required Directories
#############################################

print_header "Creating Required Directories"

DIRECTORIES=(
    "uploaded_videos"
    "uploaded_videos/compressed"
    "auth"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_success "Created directory: $dir"
    else
        print_info "Directory already exists: $dir"
    fi
done

#############################################
# Configure Systemd Service (Optional)
#############################################

print_header "Systemd Service Setup (Optional)"

echo "Would you like to set up the server to start automatically on boot?"
read -p "Configure systemd service? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Creating systemd service file..."

    SERVICE_FILE="/etc/systemd/system/dtc-rpi.service"

    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=DTC RPI Video Server with WiFi Management
After=network.target NetworkManager.service
Wants=NetworkManager.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$SCRIPT_DIR
Environment="DTC_WIFI_MONITORING=true"
Environment="PATH=$SCRIPT_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    sudo chmod 644 "$SERVICE_FILE"

    print_success "Service file created at $SERVICE_FILE"

    print_info "Reloading systemd daemon..."
    sudo systemctl daemon-reload

    print_info "Enabling service..."
    sudo systemctl enable dtc-rpi.service

    print_success "Service enabled - will start on boot"

    echo ""
    read -p "Start the service now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Starting service..."
        sudo systemctl start dtc-rpi.service
        sleep 2

        if systemctl is-active --quiet dtc-rpi.service; then
            print_success "Service is running!"
            print_info "View logs with: sudo journalctl -u dtc-rpi.service -f"
        else
            print_error "Service failed to start"
            print_info "Check logs with: sudo journalctl -u dtc-rpi.service -n 50"
        fi
    fi
else
    print_info "Skipping systemd service setup"
fi

#############################################
# WiFi Power Management (Optional)
#############################################

print_header "WiFi Power Management (Optional)"

echo "Disable WiFi power saving to prevent disconnections?"
print_warning "This may increase power consumption slightly"
read -p "Disable WiFi power saving? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Disabling WiFi power management..."

    # Create a script to disable power management
    sudo tee /etc/NetworkManager/conf.d/default-wifi-powersave-off.conf > /dev/null << EOF
[connection]
wifi.powersave = 2
EOF

    print_success "WiFi power saving disabled"
    print_info "Restart NetworkManager for changes to take effect"

    read -p "Restart NetworkManager now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl restart NetworkManager
        print_success "NetworkManager restarted"
    fi
fi

#############################################
# Setup Complete
#############################################

print_header "Setup Complete!"

echo -e "${GREEN}✓ System dependencies installed${NC}"
echo -e "${GREEN}✓ Python virtual environment created${NC}"
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo -e "${GREEN}✓ WiFi configuration saved${NC}"
echo -e "${GREEN}✓ Required directories created${NC}"
echo ""

print_info "Configuration Summary:"
echo "  - Server directory: $SCRIPT_DIR"
echo "  - WiFi config: $SCRIPT_DIR/wifi_config.json"
echo "  - Python venv: $SCRIPT_DIR/venv"
echo ""

print_header "Next Steps"

echo "1. To start the server manually:"
echo "   ${BLUE}cd $SCRIPT_DIR${NC}"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo "   ${BLUE}python3 server.py${NC}"
echo ""

echo "2. To check WiFi status:"
echo "   ${BLUE}iwgetid -r${NC}  (shows current SSID)"
echo "   ${BLUE}ip addr show wlan0${NC}  (shows WiFi interface)"
echo ""

echo "3. To view server logs (if using systemd):"
echo "   ${BLUE}sudo journalctl -u dtc-rpi.service -f${NC}"
echo ""

echo "4. To manage the service (if configured):"
echo "   ${BLUE}sudo systemctl status dtc-rpi.service${NC}  (check status)"
echo "   ${BLUE}sudo systemctl start dtc-rpi.service${NC}   (start service)"
echo "   ${BLUE}sudo systemctl stop dtc-rpi.service${NC}    (stop service)"
echo "   ${BLUE}sudo systemctl restart dtc-rpi.service${NC} (restart service)"
echo ""

print_info "For more information, see WIFI_SETUP.md"

print_success "Setup completed successfully!"

deactivate 2>/dev/null || true
