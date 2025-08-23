import threading
import subprocess
import time
import socket
import sys
import os
from pyngrok import ngrok

def wait_for_port(host: str, port: int, timeout_sec: int = 60):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            if time.time() - start_time > timeout_sec:
                raise TimeoutError(f"Port {port} not ready after {timeout_sec}s")
            time.sleep(0.5)

# Start local FastAPI backend
def run_api():
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000)

threading.Thread(target=run_api, daemon=True).start()

# Wait for API
print("Waiting for backend API...")
wait_for_port("127.0.0.1", 8000)

# Expose backend via ngrok for Streamlit
api_tunnel = ngrok.connect(8000)
with open("backend_url.txt", "w") as f:
    f.write(api_tunnel.public_url)
print("✅ Backend API ready at:", api_tunnel.public_url + "/generate_music")

# Start Streamlit
def run_streamlit():
    python_exe = sys.executable
    subprocess.run([
        python_exe,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])

threading.Thread(target=run_streamlit, daemon=True).start()

print("Waiting for Streamlit frontend...")
wait_for_port("127.0.0.1", 8501)
streamlit_tunnel = ngrok.connect(8501)
print("✅ Streamlit ready at:", streamlit_tunnel.public_url)

# Keep running
try:
    while True:
        time.sleep(9999)
except KeyboardInterrupt:
    print("Shutting down...")
    ngrok.kill()
