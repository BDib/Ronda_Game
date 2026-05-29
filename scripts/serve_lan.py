import socket
import subprocess
import os
import sys

def get_local_ip():
    try:
        # Create a dummy socket to detect the preferred outbound IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def serve():
    local_ip = get_local_ip()
    port = 8550

    print("=" * 50)
    print("RONDA LAN SERVER")
    print("=" * 50)
    print(f"Local IP detected: {local_ip}")
    print(f"Server URL: http://{local_ip}:{port}")
    print("-" * 50)
    print("Instructions for players:")
    print(f"1. Open a browser and go to http://{local_ip}:{port}")
    print("2. One player creates a room and shares the code.")
    print("3. Others join using that code.")
    print("=" * 50)
    print("\nStarting server... Press Ctrl+C to stop.")

    # Ensure we are in the root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    try:
        # Launch flet run --web
        # We use sys.executable to ensure we use the same python interpreter
        cmd = [
            "flet", "run",
            "--web",
            "--port", str(port),
            "ui/main.py"
        ]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    serve()
