"""
WiFi Connection Manager for Raspberry Pi
Monitors WiFi connectivity and automatically reconnects if connection is lost.
"""

import logging
import subprocess
import time
import threading
from typing import List, Optional, Dict
from pathlib import Path
import json


class WiFiManager:
    """Manages WiFi connectivity with automatic reconnection"""

    def __init__(
        self,
        config_file: Path,
        check_interval: int = 30,
        reconnect_timeout: int = 120,
    ):
        """
        Initialize WiFi Manager

        Args:
            config_file: Path to WiFi configuration JSON file
            check_interval: Seconds between connectivity checks
            reconnect_timeout: Timeout for reconnection attempts
        """
        self.config_file = config_file
        self.check_interval = check_interval
        self.reconnect_timeout = reconnect_timeout
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.networks: List[Dict[str, str]] = []
        self._load_networks()

    def _load_networks(self):
        """Load WiFi networks from configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.networks = data.get('networks', [])
                    if self.networks:
                        self.logger.info(f"Loaded {len(self.networks)} WiFi network(s)")
                    else:
                        self.logger.warning("No WiFi networks configured")
            else:
                self.logger.warning(f"WiFi config file not found: {self.config_file}")
                self._create_default_config()
        except Exception as e:
            self.logger.error(f"Error loading WiFi config: {e}")
            self.networks = []

    def _create_default_config(self):
        """Create a default WiFi configuration file template"""
        try:
            default_config = {
                "networks": [
                    {
                        "ssid": "YOUR_WIFI_SSID",
                        "password": "YOUR_WIFI_PASSWORD",
                        "priority": 1
                    }
                ]
            }
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            self.logger.info(f"Created default WiFi config at {self.config_file}")
            self.logger.info("Please edit the config file with your WiFi credentials")
        except Exception as e:
            self.logger.error(f"Error creating default config: {e}")

    def is_connected(self) -> bool:
        """Check if currently connected to WiFi"""
        try:
            # Check if wlan0 interface is up and has an IP
            result = subprocess.run(
                ['ip', 'addr', 'show', 'wlan0'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False

            # Check for valid IP address (not 127.0.0.1)
            output = result.stdout
            if 'inet ' in output and '127.0.0.1' not in output:
                # Also check if we can reach gateway
                return self._check_gateway_connectivity()

            return False
        except Exception as e:
            self.logger.error(f"Error checking WiFi connection: {e}")
            return False

    def _check_gateway_connectivity(self) -> bool:
        """Check if we can reach the gateway"""
        try:
            # Get default gateway
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False

            # Extract gateway IP
            output = result.stdout
            if 'via' in output:
                gateway = output.split('via')[1].split()[0]
                # Ping gateway with 1 packet and 2 second timeout
                ping_result = subprocess.run(
                    ['ping', '-c', '1', '-W', '2', gateway],
                    capture_output=True,
                    timeout=5
                )
                return ping_result.returncode == 0

            return False
        except Exception as e:
            self.logger.debug(f"Gateway check failed: {e}")
            return False

    def get_current_ssid(self) -> Optional[str]:
        """Get the SSID of currently connected network"""
        try:
            result = subprocess.run(
                ['iwgetid', '-r'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except Exception as e:
            self.logger.debug(f"Error getting current SSID: {e}")
            return None

    def connect_to_network(self, ssid: str, password: str) -> bool:
        """
        Connect to a WiFi network using nmcli

        Args:
            ssid: Network SSID
            password: Network password

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Attempting to connect to {ssid}...")

            # Try to connect using nmcli
            result = subprocess.run(
                ['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.info(f"Successfully connected to {ssid}")
                time.sleep(3)  # Wait for connection to stabilize
                return self.is_connected()
            else:
                # Network might be already configured, try to activate
                self.logger.debug(f"Direct connection failed, trying to activate existing connection")
                activate_result = subprocess.run(
                    ['nmcli', 'connection', 'up', ssid],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if activate_result.returncode == 0:
                    self.logger.info(f"Activated existing connection to {ssid}")
                    time.sleep(3)
                    return self.is_connected()

                self.logger.warning(f"Failed to connect to {ssid}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout connecting to {ssid}")
            return False
        except Exception as e:
            self.logger.error(f"Error connecting to {ssid}: {e}")
            return False

    def attempt_reconnection(self) -> bool:
        """Attempt to reconnect to configured WiFi networks"""
        if not self.networks:
            self.logger.warning("No WiFi networks configured for reconnection")
            return False

        # Sort networks by priority (lower number = higher priority)
        sorted_networks = sorted(self.networks, key=lambda x: x.get('priority', 999))

        for network in sorted_networks:
            ssid = network.get('ssid')
            password = network.get('password')

            if not ssid or not password:
                continue

            if ssid == "YOUR_WIFI_SSID":
                self.logger.warning("Default WiFi config detected. Please update wifi_config.json")
                continue

            self.logger.info(f"Trying to connect to {ssid} (priority {network.get('priority', 'N/A')})")

            if self.connect_to_network(ssid, password):
                return True

            time.sleep(5)  # Wait between connection attempts

        return False

    def _monitor_loop(self):
        """Main monitoring loop that runs in background thread"""
        self.logger.info("WiFi monitoring started")
        consecutive_failures = 0

        while self.monitoring:
            try:
                if self.is_connected():
                    consecutive_failures = 0
                    current_ssid = self.get_current_ssid()
                    if current_ssid:
                        self.logger.debug(f"WiFi connected to {current_ssid}")
                else:
                    consecutive_failures += 1
                    self.logger.warning(f"WiFi disconnected (failure #{consecutive_failures})")

                    # Try to reconnect
                    if self.attempt_reconnection():
                        self.logger.info("WiFi reconnection successful")
                        consecutive_failures = 0
                    else:
                        self.logger.error("WiFi reconnection failed")

                # Wait before next check
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in WiFi monitoring loop: {e}")
                time.sleep(self.check_interval)

        self.logger.info("WiFi monitoring stopped")

    def start_monitoring(self):
        """Start WiFi monitoring in background thread"""
        if self.monitoring:
            self.logger.warning("WiFi monitoring already running")
            return

        if not self.networks:
            self.logger.warning("No WiFi networks configured. Monitoring not started.")
            self.logger.info(f"Please configure networks in {self.config_file}")
            return

        # Check if nmcli is available
        try:
            subprocess.run(['which', 'nmcli'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.logger.error("nmcli not found. Please install NetworkManager: sudo apt-get install network-manager")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("WiFi monitoring thread started")

    def stop_monitoring(self):
        """Stop WiFi monitoring"""
        if not self.monitoring:
            return

        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("WiFi monitoring stopped")

    def get_status(self) -> dict:
        """Get current WiFi status"""
        connected = self.is_connected()
        current_ssid = self.get_current_ssid() if connected else None

        return {
            "connected": connected,
            "ssid": current_ssid,
            "monitoring": self.monitoring,
            "configured_networks": len(self.networks)
        }
