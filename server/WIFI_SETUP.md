# WiFi Management Setup Guide

The DTC_RPI server now includes automatic WiFi connection management to ensure your Raspberry Pi stays connected to WiFi at all times.

## Features

- **Automatic Reconnection**: Monitors WiFi connectivity every 30 seconds and automatically reconnects if connection is lost
- **Multiple Network Support**: Configure multiple WiFi networks with priority levels
- **Gateway Health Check**: Verifies actual internet connectivity, not just interface status
- **Seamless Integration**: Runs as a background thread, doesn't interfere with server operation
- **Initial Connection**: Attempts to connect to WiFi on server startup if not already connected

## Prerequisites

The WiFi manager requires NetworkManager to be installed on your Raspberry Pi:

```bash
sudo apt-get update
sudo apt-get install network-manager
```

## Configuration

### 1. Edit WiFi Credentials

Edit the `wifi_config.json` file in the server directory:

```json
{
  "networks": [
    {
      "ssid": "YourHomeWiFi",
      "password": "your_wifi_password",
      "priority": 1
    },
    {
      "ssid": "YourBackupWiFi",
      "password": "backup_password",
      "priority": 2
    }
  ]
}
```

**Notes:**
- Lower priority number = higher priority (1 is highest)
- The system will try to connect to networks in priority order
- You can add as many networks as needed
- Keep this file secure as it contains WiFi passwords

### 2. Environment Variables (Optional)

You can customize WiFi manager behavior using environment variables:

```bash
# Enable/disable WiFi monitoring (default: true)
export DTC_WIFI_MONITORING=true

# Path to WiFi config file (default: wifi_config.json)
export DTC_WIFI_CONFIG=/path/to/your/wifi_config.json

# Check interval in seconds (default: 30)
export DTC_WIFI_CHECK_INTERVAL=30

# Reconnection timeout in seconds (default: 120)
export DTC_WIFI_RECONNECT_TIMEOUT=120
```

## How It Works

1. **On Startup**:
   - The server checks if WiFi is connected
   - If not, it attempts to connect using configured networks (in priority order)
   - Starts background monitoring thread

2. **During Operation**:
   - Every 30 seconds (configurable), checks WiFi connectivity
   - Verifies both interface status and gateway reachability
   - If disconnected, automatically tries to reconnect to configured networks

3. **Reconnection Process**:
   - Sorts networks by priority
   - Attempts connection to each network in order
   - Stops when successful connection is established
   - Logs all connection attempts

## Logs

The WiFi manager logs all activity. Check your server logs for:

```
INFO - WiFi connected to YourHomeWiFi
WARNING - WiFi disconnected (failure #1)
INFO - Attempting to connect to YourHomeWiFi...
INFO - Successfully connected to YourHomeWiFi
```

## Disabling WiFi Management

If you want to disable automatic WiFi management:

1. Set environment variable:
   ```bash
   export DTC_WIFI_MONITORING=false
   ```

2. Or remove/rename `wifi_config.json`

## Troubleshooting

### WiFi manager not starting

**Error**: `nmcli not found`
- **Solution**: Install NetworkManager: `sudo apt-get install network-manager`

### Cannot connect to WiFi

1. **Check credentials**: Verify SSID and password in `wifi_config.json`
2. **Check WiFi interface**: Run `ip addr show wlan0` to ensure WiFi adapter is detected
3. **Check NetworkManager status**: Run `sudo systemctl status NetworkManager`
4. **Manual test**: Try manually connecting: `sudo nmcli device wifi connect "YourSSID" password "YourPassword"`

### WiFi keeps disconnecting

1. **Check signal strength**: Poor signal can cause frequent disconnections
2. **Increase check interval**: Set `DTC_WIFI_CHECK_INTERVAL=60` for less frequent checks
3. **Check power management**: Disable WiFi power saving:
   ```bash
   sudo iw dev wlan0 set power_save off
   ```

### Server not accessible when WiFi is down

The server will still run on localhost (127.0.0.1) when WiFi is down. You can:
- Connect via Ethernet if available
- Access directly from the Pi (SSH via local connection)
- Wait for WiFi manager to reconnect

## Security Recommendations

1. **Protect config file**:
   ```bash
   chmod 600 wifi_config.json
   ```

2. **Don't commit credentials**: Add to `.gitignore`:
   ```
   wifi_config.json
   ```

3. **Use environment variables** for production deployments instead of storing passwords in files

## Advanced Configuration

### Running as System Service

To ensure WiFi management starts on boot, you can create a systemd service:

```bash
sudo nano /etc/systemd/system/dtc-rpi.service
```

```ini
[Unit]
Description=DTC RPI Video Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/DTC_RPI/server
Environment="DTC_WIFI_MONITORING=true"
ExecStart=/usr/bin/python3 /home/pi/DTC_RPI/server/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable dtc-rpi.service
sudo systemctl start dtc-rpi.service
```

## API Monitoring

The WiFi manager status is not currently exposed via API, but you can check logs or add an endpoint if needed.
