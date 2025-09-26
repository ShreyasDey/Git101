import network
import socket
import time

# === Default Wi-Fi AP Config ===
SSID = "QuadDrive"
PASSWORD = "39250000"

# These will be set by your main script
on_data_received = None  # callback: def func(gx, gy, gz)

def setup_ap(ssid=SSID, password=PASSWORD, channel=6):
    """Setup Pico W as Access Point."""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password, channel=channel)
    print(f"Starting AP: {ssid}")
    while not ap.active():
        time.sleep(1)
    print("AP active. IP:", ap.ifconfig()[0])
    return ap.ifconfig()[0]

def start_server(port=80):
    """Start TCP server and listen for incoming gx, gy, gz data."""
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Listening on", addr)

    while True:
        cl, addr = s.accept()
        data = cl.recv(1024).decode().strip()
        if data:
            try:
                parts = [p.strip() for p in data.split(",")]
                if len(parts) >= 3:
                    gx = float(parts[0])
                    gy = float(parts[1])
                    gz = float(parts[2])
                    print(f"Received: gx={gx}, gy={gy}, gz={gz}")
                    if on_data_received:
                        on_data_received(gx, gy, gz)
            except Exception as e:
                print("Parse error:", e)
        cl.close()