import socket

def port_is_busy(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)  # Set a timeout for the connection
        result = sock.connect_ex((host, int(port)))
        return result == 0  # If result is 0, the port is busy
