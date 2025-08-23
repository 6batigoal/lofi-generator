import threading
import subprocess
import time
import socket
import sys
import os
from pyngrok import ngrok

# Function to wait until a local port is ready
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

# Detect if running on Cloud Run or locally
IS_CLOUD_RUN = "K_SERVICE" in os.environ

# Start FastAPI backend
def run_api():
    import uvicorn

    port = int(os.environ.get("PORT", 8080))  # Cloud Run provides PORT
    print(f"Starting FastAPI on port {port}...")
    uvicorn.run("api:app", host="0.0.0.0", port=port)

threading.Thread(target=run_api, daemon=True).start()

# Wait for FastAPI port
backend_port = int(os.environ.get("PORT", 8080))
print("Waiting for backend API...")
wait_for_port("127.0.0.1", backend_port, timeout_sec=60)

# Write backend URL to file
backend_url = f"http://127.0.0.1:{backend_port}" if IS_CLOUD_RUN else ngrok.connect(backend_port).public_url
with open("backend_url.txt", "w") as f:
    f.write(backend_url)
print("✅ Backend API ready at:", backend_url + "/generate_music")

# Start Streamlit only when running locally
if not IS_CLOUD_RUN:
    def run_streamlit():
        python_exe = sys.executable  # ensures same venv
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

    # Wait until Streamlit port is ready
    print("Waiting for Streamlit frontend...")
    wait_for_port("127.0.0.1", 8501, timeout_sec=120)

    # Expose Streamlit via ngrok
    streamlit_tunnel = ngrok.connect(8501)
    print("✅ Streamlit ready at:", streamlit_tunnel.public_url)

# Keep the script running
try:
    while True:
        time.sleep(9999)
except KeyboardInterrupt:
    print("Shutting down...")
    ngrok.kill()

