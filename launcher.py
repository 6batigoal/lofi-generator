import subprocess
import sys
import time
from pyngrok import ngrok

STREAMLIT_PORT = 8501

# Start Streamlit locally
print("Starting Streamlit front-end...")
streamlit_proc = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
    "--server.port", str(STREAMLIT_PORT),
    "--server.address", "0.0.0.0"
])

# Give Streamlit a few seconds to start
time.sleep(5)

# Open ngrok tunnel for Streamlit
public_url = ngrok.connect(STREAMLIT_PORT)
print(f"✅ Streamlit public URL: {public_url}")
print("Press CTRL+C to stop")

# Keep the script running until user interrupts
try:
    streamlit_proc.wait()
except KeyboardInterrupt:
    print("Stopping Streamlit and ngrok...")
    streamlit_proc.terminate()
    ngrok.kill()