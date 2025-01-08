import socket

def get_local_ipv4():
    try:
        # Create a dummy socket and connect to an external server to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # 8.8.8.8 is a public DNS server (Google)
            local_ip = s.getsockname()[0]  # Get the IP address of the socket
        return local_ip
    except Exception as e:
        return f"Error: {e}"

HOST = "192.168.2.153"
PORT = 5555