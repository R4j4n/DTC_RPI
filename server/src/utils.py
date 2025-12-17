import socket
import time

import netifaces
from zeroconf import ServiceInfo, Zeroconf


def get_ip_address() -> str:
    """Get the IP address of the first available network interface."""
    try:
        interfaces = [i for i in netifaces.interfaces() if i != "lo"]

        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]["addr"]

        return "127.0.0.1"
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return "127.0.0.1"


def wait_for_valid_ip(timeout=60):
    """Wait for a valid IP address, checking every second."""
    print("Waiting for a valid network IP...")
    start_time = time.time()
    retry_count = 0
    while time.time() - start_time < timeout:
        ip = get_ip_address()
        if ip != "127.0.0.1":
            print(f"Found valid IP address: {ip}")
            return ip

        retry_count += 1
        if retry_count % 10 == 0:
            print(f"Still waiting for network connection... ({retry_count}s elapsed)")

        time.sleep(1)

    print("WARNING: Timeout waiting for network IP, using localhost")
    return "127.0.0.1"


def register_service() -> Zeroconf:
    """Register the video server service using Zeroconf."""
    try:
        ip = wait_for_valid_ip()
        hostname = socket.gethostname()

        print(f"Registering service with IP: {ip}")

        info = ServiceInfo(
            "_pivideo._tcp.local.",
            f"{hostname}._pivideo._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=5000,
            properties={"hostname": hostname},
        )

        zeroconf = Zeroconf()
        zeroconf.register_service(info)
        return zeroconf
    except Exception as e:
        print(f"Error registering service: {e}")
        raise
