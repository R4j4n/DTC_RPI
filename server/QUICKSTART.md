# Quick Start Guide

Get your DTC_RPI server up and running with WiFi management in just a few steps!

## One-Command Setup

On your Raspberry Pi, run:

```bash
cd /path/to/DTC_RPI/server
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Install all system dependencies (NetworkManager, VLC, FFmpeg, etc.)
- ✅ Create Python virtual environment
- ✅ Install Python packages
- ✅ Configure WiFi credentials interactively
- ✅ Set up directories and authentication
- ✅ Optionally configure systemd service for auto-start

## What You'll Be Asked

The script will ask you:

1. **Confirm package installation** - System dependencies to install
2. **Number of WiFi networks** - Configure 1-5 networks (primary + backups)
3. **For each network:**
   - WiFi SSID (network name)
   - WiFi Password (hidden input)
   - Priority (1 = highest priority)
4. **Server password** - For API authentication
5. **Systemd service** - Auto-start on boot (optional)
6. **WiFi power saving** - Disable for better reliability (optional)

## Example WiFi Configuration

During setup:
```
How many WiFi networks do you want to configure? 2

Configuring Network #1
  WiFi SSID: HomeWiFi
  WiFi Password: ********
  Priority: 1

Configuring Network #2
  WiFi SSID: MobileHotspot
  WiFi Password: ********
  Priority: 2
```

This creates a configuration where:
- The Pi will prefer "HomeWiFi"
- If "HomeWiFi" is unavailable, it will connect to "MobileHotspot"
- If both are available, it will always choose "HomeWiFi" (priority 1)

## After Setup

### Manual Start
```bash
cd /path/to/DTC_RPI/server
source venv/bin/activate
python3 server.py
```

### With Systemd (if configured)
```bash
sudo systemctl status dtc-rpi.service   # Check status
sudo systemctl start dtc-rpi.service    # Start server
sudo systemctl stop dtc-rpi.service     # Stop server
sudo journalctl -u dtc-rpi.service -f   # View logs
```

## Verify WiFi Connection

```bash
iwgetid -r                    # Shows current WiFi network
ip addr show wlan0            # Shows WiFi interface and IP
ping -c 3 8.8.8.8            # Test internet connectivity
```

## Accessing the Server

Once running, the server is accessible at:
- **Local**: `http://localhost:8000`
- **Network**: `http://<raspberry-pi-ip>:8000`
- **Docs**: `http://<raspberry-pi-ip>:8000/docs`

To find your Raspberry Pi's IP:
```bash
hostname -I
```

## Troubleshooting

### NetworkManager not starting
```bash
sudo systemctl status NetworkManager
sudo systemctl start NetworkManager
```

### WiFi not connecting
```bash
# Check available networks
nmcli device wifi list

# Try manual connection
sudo nmcli device wifi connect "YourSSID" password "YourPassword"

# Check WiFi interface
ip link show wlan0
```

### Service not starting
```bash
# Check service logs
sudo journalctl -u dtc-rpi.service -n 50

# Check if ports are in use
sudo netstat -tulpn | grep 8000
```

### Python dependencies failing
```bash
# Make sure you're in the venv
source venv/bin/activate

# Manually install dependencies
pip install -r requirements.txt
```

## Manual WiFi Configuration

If you need to reconfigure WiFi after setup, edit:

```bash
nano wifi_config.json
```

Example format:
```json
{
  "networks": [
    {
      "ssid": "YourWiFi",
      "password": "YourPassword",
      "priority": 1
    }
  ]
}
```

Then secure the file:
```bash
chmod 600 wifi_config.json
```

## Environment Variables

You can customize behavior with environment variables:

```bash
# Disable WiFi monitoring
export DTC_WIFI_MONITORING=false

# Change check interval (seconds)
export DTC_WIFI_CHECK_INTERVAL=60

# Change server port
export DTC_PORT=8080

# Set log level
export DTC_LOG_LEVEL=DEBUG
```

## Uninstall

To remove the systemd service:
```bash
sudo systemctl stop dtc-rpi.service
sudo systemctl disable dtc-rpi.service
sudo rm /etc/systemd/system/dtc-rpi.service
sudo systemctl daemon-reload
```

To remove installed packages (careful!):
```bash
sudo apt-get remove --purge network-manager vlc ffmpeg
sudo apt-get autoremove
```

## Need Help?

- See [WIFI_SETUP.md](WIFI_SETUP.md) for detailed WiFi configuration
- Check logs: `sudo journalctl -u dtc-rpi.service -f`
- Test WiFi manager: The server logs will show WiFi connection attempts
- Report issues on GitHub

## Tips

1. **Set static IP** for easier access (optional):
   ```bash
   # Edit NetworkManager connection
   sudo nmcli connection modify "YourSSID" ipv4.method manual ipv4.addresses 192.168.1.100/24 ipv4.gateway 192.168.1.1 ipv4.dns "8.8.8.8,8.8.4.4"
   ```

2. **Enable SSH** for remote access:
   ```bash
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

3. **Find your Pi** on the network using Zeroconf:
   ```bash
   # From another computer
   ping raspberrypi.local
   ```

4. **Monitor WiFi strength**:
   ```bash
   watch -n 1 'iwconfig wlan0 | grep Quality'
   ```

That's it! Your DTC_RPI server with automatic WiFi management is ready to use.
