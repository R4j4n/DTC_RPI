# Headless Raspberry Pi Kiosk Setup Guide

## Quick Setup (Automated)

Run the automated setup script:

```bash
cd /Users/Rajan/Documents/GitHub/DTC_RPI/server
./setup_headless_kiosk.sh
```

Then reboot:
```bash
sudo reboot
```

**Done!** The kiosk will auto-start on boot.

---

## Manual Setup (Step-by-Step)

### 1. Install Required Packages

```bash
sudo apt-get update
sudo apt-get install -y chromium-browser xserver-xorg x11-xserver-utils xinit openbox unclutter
```

### 2. Configure X Server

Create `~/.xinitrc`:
```bash
nano ~/.xinitrc
```

Add this content:
```bash
#!/bin/bash
xset s off
xset -dpms
xset s noblank
unclutter -idle 0.1 -root &
sleep 3
~/Documents/GitHub/DTC_RPI/server/launch_kiosk.sh &
exec openbox-session
```

Make it executable:
```bash
chmod +x ~/.xinitrc
```

### 3. Create Systemd Service for X Server

```bash
sudo nano /etc/systemd/system/kiosk-x.service
```

Add:
```ini
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
```

### 4. Create Systemd Service for DTC Server

```bash
sudo nano /etc/systemd/system/dtc-server.service
```

Add (adjust path if needed):
```ini
[Unit]
Description=DTC Trampoline Park Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Documents/GitHub/DTC_RPI/server
ExecStart=/usr/bin/python3 /home/pi/Documents/GitHub/DTC_RPI/server/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Enable Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable kiosk-x.service
sudo systemctl enable dtc-server.service
```

### 6. Reboot

```bash
sudo reboot
```

---

## What Happens on Boot

1. **System boots** → Headless mode (no desktop)
2. **X server starts** → Creates HDMI display output
3. **DTC server starts** → Runs on port 8000
4. **Kiosk launches** → Chromium opens fullscreen on HDMI
5. **Display shows** → Video + wristband schedule

---

## Management Commands

### Check Service Status

```bash
# X server status
sudo systemctl status kiosk-x.service

# DTC server status
sudo systemctl status dtc-server.service
```

### View Logs

```bash
# X server logs (live)
journalctl -u kiosk-x.service -f

# DTC server logs (live)
journalctl -u dtc-server.service -f

# Recent X server logs
journalctl -u kiosk-x.service -n 50

# Recent DTC server logs
journalctl -u dtc-server.service -n 50
```

### Restart Services

```bash
# Restart X server (will restart kiosk)
sudo systemctl restart kiosk-x.service

# Restart DTC server only
sudo systemctl restart dtc-server.service

# Restart both
sudo systemctl restart kiosk-x.service dtc-server.service
```

### Stop Services

```bash
# Stop X server
sudo systemctl stop kiosk-x.service

# Stop DTC server
sudo systemctl stop dtc-server.service
```

### Disable Auto-Start

```bash
# Disable X server
sudo systemctl disable kiosk-x.service

# Disable DTC server
sudo systemctl disable dtc-server.service
```

---

## Troubleshooting

### Kiosk Not Showing on HDMI

**Check X server is running:**
```bash
sudo systemctl status kiosk-x.service
ps aux | grep X
```

**Check logs:**
```bash
journalctl -u kiosk-x.service -n 50
```

**Common issues:**
- HDMI cable not connected during boot
- Wrong DISPLAY variable
- X server failed to start

**Solutions:**
```bash
# Restart X server
sudo systemctl restart kiosk-x.service

# Check HDMI connection
tvservice -s

# Force HDMI mode in /boot/config.txt
sudo nano /boot/config.txt
# Add: hdmi_force_hotplug=1
# Add: hdmi_drive=2
```

### DTC Server Not Starting

**Check status:**
```bash
sudo systemctl status dtc-server.service
journalctl -u dtc-server.service -n 50
```

**Common issues:**
- Python dependencies missing
- Port 8000 already in use
- Permission errors

**Solutions:**
```bash
# Install dependencies
cd ~/Documents/GitHub/DTC_RPI/server
pip3 install -r requirements.txt

# Check port
sudo netstat -tulpn | grep 8000

# Fix permissions
chmod +x ~/Documents/GitHub/DTC_RPI/server/server.py
```

### Chromium Not Launching

**Check if Chromium is installed:**
```bash
which chromium-browser
```

**Test manual launch:**
```bash
DISPLAY=:0 chromium-browser http://localhost:8000/kiosk &
```

**Check logs:**
```bash
journalctl -u kiosk-x.service | grep chromium
```

### Display on Wrong Screen

If you have multiple displays and kiosk shows on wrong one:

```bash
# List displays
DISPLAY=:0 xrandr

# Set primary display (in .xinitrc)
xrandr --output HDMI-1 --primary
```

### Network Issues

If kiosk launches but can't connect to server:

```bash
# Wait for network
sudo systemctl edit dtc-server.service
```

Add:
```ini
[Unit]
After=network-online.target
Wants=network-online.target
```

---

## Testing Without Reboot

### Test X Server

```bash
# Stop service if running
sudo systemctl stop kiosk-x.service

# Run X manually
startx
```

### Test Kiosk Script

```bash
# Ensure DISPLAY is set
export DISPLAY=:0

# Run kiosk script
cd ~/Documents/GitHub/DTC_RPI/server
./launch_kiosk.sh
```

### Test DTC Server

```bash
# Run server manually
cd ~/Documents/GitHub/DTC_RPI/server
python3 server.py
```

---

## SSH Access While Running

You can still SSH into the Pi while the kiosk is running:

```bash
ssh pi@raspberrypi.local
```

The kiosk will continue running on the HDMI display while you work via SSH.

---

## Remote Access to Kiosk

From another computer on the same network:

```bash
# Access the kiosk page
http://raspberrypi.local:8000/kiosk

# Access API
http://raspberrypi.local:8000/status
```

---

## Performance Tips

### Reduce Memory Usage

Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add:
```
# Reduce GPU memory if not needed
gpu_mem=128

# Or increase if video is laggy
gpu_mem=256
```

### Disable Unnecessary Services

```bash
# Disable Bluetooth (if not needed)
sudo systemctl disable bluetooth.service

# Disable WiFi (if using Ethernet)
sudo systemctl disable wpa_supplicant.service
```

### Monitor Resources

```bash
# CPU and memory
htop

# Chromium usage
top -p $(pgrep chromium)
```

---

## Recovery Mode

If something goes wrong and you need to disable auto-start:

### Method 1: SSH In

```bash
ssh pi@raspberrypi.local
sudo systemctl stop kiosk-x.service
sudo systemctl disable kiosk-x.service
```

### Method 2: Edit Boot

Connect keyboard to Pi, then at boot:

1. Press `Ctrl+Alt+F2` to switch to TTY2
2. Login
3. Run: `sudo systemctl stop kiosk-x.service`

---

## Uninstall

To remove auto-start:

```bash
# Disable services
sudo systemctl disable kiosk-x.service
sudo systemctl disable dtc-server.service

# Remove service files
sudo rm /etc/systemd/system/kiosk-x.service
sudo rm /etc/systemd/system/dtc-server.service

# Reload systemd
sudo systemctl daemon-reload

# Remove .xinitrc
rm ~/.xinitrc
```

---

## Summary

**Automated Setup:**
```bash
./setup_headless_kiosk.sh
sudo reboot
```

**Check Status:**
```bash
sudo systemctl status kiosk-x.service dtc-server.service
```

**View Logs:**
```bash
journalctl -u kiosk-x.service -f
journalctl -u dtc-server.service -f
```

**Restart:**
```bash
sudo systemctl restart kiosk-x.service dtc-server.service
```

✅ **Done! Your headless Raspberry Pi will now show the kiosk on HDMI automatically on every boot.**
