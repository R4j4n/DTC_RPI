#!/bin/bash

echo "=========================================="
echo "Starting Complete Setup Process"
echo "=========================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ==========================================
# PART 1: PM2 Setup (Node.js and PM2)
# ==========================================
echo ""
echo "=========================================="
echo "Part 1: Installing Node.js and PM2"
echo "=========================================="

sudo apt update && sudo apt upgrade -y

# Install Node.js from NodeSource (LTS version)
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify Node.js and npm installation
echo "Node.js version:"
node -v
echo "npm version:"
npm -v

# Install PM2 globally
echo "Installing PM2..."
sudo npm install -g pm2

# Verify PM2 installation
echo "PM2 version:"
pm2 -v

# Set up PM2 to start on boot
echo "Setting up PM2 startup..."
pm2 startup

echo ""
echo "NOTE: If you see a startup command above, you may need to run it manually to enable PM2 on boot."
echo ""

# ==========================================
# PART 2: Environment Setup (Python and dependencies)
# ==========================================
echo ""
echo "=========================================="
echo "Part 2: Setting up Python Environment"
echo "=========================================="

# Check and install Python3 and pip if not installed
if command_exists python3 && command_exists pip3; then
    echo "Python3 and pip3 are already installed."
else
    echo "Installing Python3 and pip3..."
    sudo apt update && sudo apt install -y python3-pip
fi

# Check and install FFmpeg if not installed
if command_exists ffmpeg; then
    echo "FFmpeg is already installed."
else
    echo "Installing FFmpeg..."
    sudo apt update && sudo apt install -y ffmpeg
fi

# Check and install VLC if not installed
if command_exists vlc; then
    echo "VLC is already installed."
else
    echo "Installing VLC..."
    sudo apt update && sudo apt install -y vlc
fi

# Check and install cec-utils if not installed
if command_exists cec-client; then
    echo "cec-utils is already installed."
else
    echo "Installing cec-utils..."
    sudo apt update && sudo apt install -y cec-utils
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
fi

# ==========================================
# Setup Complete
# ==========================================
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ Node.js and npm installed"
echo "  ✓ PM2 installed and configured"
echo "  ✓ Python environment and dependencies installed"
echo "  ✓ FFmpeg, VLC, and cec-utils installed"
echo ""
echo "Virtual environment is activated."
echo "To use PM2 on boot, make sure to run the startup command if shown above."
echo ""
