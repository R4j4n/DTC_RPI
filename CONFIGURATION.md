# DTC_RPI Server Configuration Guide

## Overview

The DTC_RPI server now supports environment variable configuration, making it easy to customize without modifying code.

---

## Quick Start

### Default Configuration (No Changes Required)

The server works out of the box with sensible defaults:

```bash
cd server
python server.py
```

Server will start on `http://0.0.0.0:8000`

---

## Environment Variables

### Server Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DTC_HOST` | `0.0.0.0` | Server bind address |
| `DTC_PORT` | `8000` | Server port |
| `DTC_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DTC_LOG_FILE` | `None` | Optional log file path |

**Example:**
```bash
export DTC_HOST=127.0.0.1
export DTC_PORT=8080
export DTC_LOG_LEVEL=DEBUG
```

---

### Video Player Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DTC_MAX_RETRY` | `3` | Max retry attempts for playback |
| `DTC_RETRY_DELAY` | `1.0` | Delay between retries (seconds) |
| `DTC_VLC_VOLUME` | `100` | VLC volume (0-100) |

**Example:**
```bash
export DTC_MAX_RETRY=5
export DTC_RETRY_DELAY=2.0
export DTC_VLC_VOLUME=80
```

---

### Video Compression Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DTC_COMPRESS_RES` | `240` | Compression resolution (240, 480, 720) |
| `DTC_COMPRESS_FPS` | `10` | Compression framerate |
| `DTC_COMPRESS_CRF` | `28` | FFmpeg CRF quality (18-28, lower = better) |

**Example:**
```bash
export DTC_COMPRESS_RES=480
export DTC_COMPRESS_FPS=15
export DTC_COMPRESS_CRF=23
```

---

### HDMI/CEC Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DTC_CEC_TIMEOUT` | `10` | CEC command timeout (seconds) |
| `DTC_CEC_RETRY` | `3` | CEC command retry attempts |
| `DTC_TV_WAIT` | `3` | Wait time for TV to be ready (seconds) |
| `DTC_HDMI_MIN` | `1` | Minimum HDMI port number |
| `DTC_HDMI_MAX` | `4` | Maximum HDMI port number |

**Example:**
```bash
export DTC_CEC_TIMEOUT=15
export DTC_TV_WAIT=5
```

---

### Scheduler Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DTC_SCHEDULER_INTERVAL` | `30` | Schedule check interval (seconds) |

**Example:**
```bash
export DTC_SCHEDULER_INTERVAL=60
```

---

### Directory Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DTC_UPLOAD_DIR` | `uploaded_videos` | Video upload directory |
| `DTC_AUTH_DIR` | `auth` | Authentication files directory |

**Example:**
```bash
export DTC_UPLOAD_DIR=/mnt/videos
```

---

### File Paths

| Variable | Default | Description |
|----------|---------|-------------|
| `DTC_SCHEDULE_FILE` | `schedule.json` | TV schedule file |
| `DTC_LAST_PLAYED_FILE` | `last_played.json` | Last played video file |
| `DTC_HDMI_DEVICES_FILE` | `hdmi_devices.json` | HDMI device mapping |
| `DTC_CURRENT_INPUT_FILE` | `current_input.json` | Current HDMI input |

---

### Service Discovery

| Variable | Default | Description |
|----------|---------|-------------|
| `DTC_SERVICE_NAME` | `_pivideo._tcp.local.` | Zeroconf service name |
| `DTC_ZEROCONF_TIMEOUT` | `60` | Timeout for getting valid IP |

---

## Configuration Methods

### Method 1: Export in Shell

```bash
export DTC_PORT=8080
export DTC_VLC_VOLUME=80
cd server
python server.py
```

### Method 2: Inline with Command

```bash
cd server
DTC_PORT=8080 DTC_VLC_VOLUME=80 python server.py
```

### Method 3: .env File (Recommended for Production)

Create a file named `.env` in the server directory:

```bash
# Server Configuration
DTC_HOST=0.0.0.0
DTC_PORT=8080
DTC_LOG_LEVEL=INFO

# Video Settings
DTC_VLC_VOLUME=80
DTC_MAX_RETRY=5

# CEC Settings
DTC_TV_WAIT=5
DTC_CEC_TIMEOUT=15
```

Then load it before starting:

```bash
cd server
source .env  # Or use a tool like python-dotenv
python server.py
```

### Method 4: Systemd Service File

For production deployments using systemd:

```ini
[Unit]
Description=DTC_RPI Video Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/DTC_RPI/server
Environment="DTC_PORT=8080"
Environment="DTC_VLC_VOLUME=80"
Environment="DTC_LOG_LEVEL=INFO"
ExecStart=/home/pi/DTC_RPI/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Common Configuration Scenarios

### Scenario 1: Debugging Issues

```bash
export DTC_LOG_LEVEL=DEBUG
export DTC_LOG_FILE=server.log
cd server
python server.py
```

Check `server.log` for detailed information.

---

### Scenario 2: Performance Tuning

For slower Raspberry Pi models:

```bash
export DTC_COMPRESS_RES=240     # Lower resolution
export DTC_COMPRESS_FPS=10      # Lower framerate
export DTC_MAX_RETRY=5          # More retries
export DTC_RETRY_DELAY=2.0      # Longer delays
```

For faster devices:

```bash
export DTC_COMPRESS_RES=720     # Higher resolution
export DTC_COMPRESS_FPS=30      # Higher framerate
```

---

### Scenario 3: Multiple Servers on Same Network

```bash
# Server 1
export DTC_PORT=8000
export DTC_SERVICE_NAME="_pivideo1._tcp.local."

# Server 2
export DTC_PORT=8001
export DTC_SERVICE_NAME="_pivideo2._tcp.local."
```

---

### Scenario 4: Custom File Locations

```bash
export DTC_UPLOAD_DIR=/mnt/usb/videos
export DTC_SCHEDULE_FILE=/etc/dtc/schedule.json
export DTC_LAST_PLAYED_FILE=/var/lib/dtc/last_played.json
```

---

### Scenario 5: TV with Slow HDMI-CEC Response

```bash
export DTC_TV_WAIT=10           # Wait longer for TV
export DTC_CEC_TIMEOUT=20       # Longer timeout
export DTC_CEC_RETRY=5          # More retries
```

---

## Verifying Configuration

To see your active configuration, the server logs it on startup:

```bash
python server.py
```

Look for:
```
INFO - Starting DTC_RPI Server...
INFO - Configuration: {'server': {'host': '0.0.0.0', 'port': 8080}, ...}
```

---

## Configuration Best Practices

### 1. **Use .env Files for Production**
Keep configuration separate from code.

### 2. **Start with Defaults**
Only override what you need to change.

### 3. **Log Configuration on Startup**
The server automatically logs configuration - review it.

### 4. **Document Your Changes**
Keep track of non-default values.

### 5. **Test After Changes**
Verify the server works with new settings.

---

## Troubleshooting Configuration

### Issue: Configuration Not Applied

**Check:**
1. Environment variables are exported in the same shell
2. Variable names are spelled correctly (case-sensitive)
3. Values are valid (e.g., PORT must be a number)

**Verify:**
```bash
echo $DTC_PORT
```

### Issue: Server Won't Start

**Common Causes:**
- Port already in use
- Invalid log level
- Directory doesn't exist

**Solution:**
```bash
# Check port availability
netstat -tuln | grep 8000

# Verify directories exist
ls -la uploaded_videos/
```

### Issue: Changes Not Taking Effect

**Solution:**
Restart the server completely:
```bash
# Kill existing process
pkill -f server.py

# Start with new config
export DTC_PORT=8080
python server.py
```

---

## Default Values Reference

All defaults are defined in `server/src/config.py`:

```python
class ServerConfig:
    HOST: str = os.getenv("DTC_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("DTC_PORT", "8000"))
    # ... more settings
```

You can review this file to see all available options.

---

## Security Considerations

### Binding Address

- `0.0.0.0` - Listen on all interfaces (default, accessible from network)
- `127.0.0.1` - Listen only locally (more secure, local access only)

**Recommendation:** Use `127.0.0.1` if not accessing from other devices.

### Port Selection

- Ports 1-1024 require root privileges
- Use ports 8000-9000 for user services
- Ensure firewall allows the port if needed

---

## PM2 Integration

If using PM2 for process management:

### ecosystem.config.js

```javascript
module.exports = {
  apps: [{
    name: 'dtc-rpi-server',
    script: 'server.py',
    interpreter: 'python3',
    cwd: '/home/pi/DTC_RPI/server',
    env: {
      DTC_PORT: 8080,
      DTC_VLC_VOLUME: 80,
      DTC_LOG_LEVEL: 'INFO',
      DTC_TV_WAIT: 5
    }
  }]
}
```

Start with:
```bash
pm2 start ecosystem.config.js
```

---

## Examples

### Example 1: Basic Custom Config

```bash
#!/bin/bash
# start-server.sh

export DTC_PORT=8080
export DTC_LOG_LEVEL=INFO
export DTC_VLC_VOLUME=80

cd /home/pi/DTC_RPI/server
python server.py
```

### Example 2: Production Config

```bash
#!/bin/bash
# production-server.sh

# Server
export DTC_HOST=0.0.0.0
export DTC_PORT=8000
export DTC_LOG_LEVEL=WARNING
export DTC_LOG_FILE=/var/log/dtc-rpi/server.log

# Performance
export DTC_COMPRESS_RES=240
export DTC_COMPRESS_FPS=10
export DTC_MAX_RETRY=5
export DTC_RETRY_DELAY=2.0

# CEC
export DTC_TV_WAIT=5
export DTC_CEC_TIMEOUT=15

# Files
export DTC_UPLOAD_DIR=/mnt/videos
export DTC_SCHEDULE_FILE=/etc/dtc/schedule.json

cd /home/pi/DTC_RPI/server
python server.py
```

---

## Support

For questions about configuration:
1. Check this guide
2. Review `server/src/config.py` for all options
3. Check logs for configuration issues
4. Refer to CHANGELOG.md for recent changes

---

**Last Updated:** 2025-12-09
**Version:** 2.0.0
