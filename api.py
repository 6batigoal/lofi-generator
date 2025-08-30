from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.responses import FileResponse
from audiocraft.models import MusicGen
import torch
import os
import numpy as np
from scipy.io.wavfile import write as wav_write
import time
import re
from pathlib import Path
from google.cloud import storage

app = FastAPI()

# --- Device setup ---
if not torch.cuda.is_available():
    raise RuntimeError("❌ GPU not available. Please deploy with GPU enabled (NVIDIA L4).")
DEVICE = "cuda"
print(f"🚀 Using device: {DEVICE}")

# --- GCS checkpoint info ---
BUCKET_NAME = "lewagon-lofi-generator"
CHECKPOINT_BLOB = "lm_final.pt"
LOCAL_CHECKPOINT = "/tmp/lm_final.pt"  # Cloud Run allows writing to /tmp

# --- Global model variable ---
model = None

def download_checkpoint():
    """Download model checkpoint from GCS if not already cached in /tmp"""
    if not os.path.exists(LOCAL_CHECKPOINT):
        print("⬇️ Downloading checkpoint from GCS...")
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(CHECKPOINT_BLOB)
        blob.download_to_filename(LOCAL_CHECKPOINT)
        print("✅ Checkpoint download complete.")
    else:
        print("✔️ Checkpoint already present in /tmp, skipping download.")

def load_model():
    """Lazy-load MusicGen model and checkpoint"""
    global model
    if model is None:
        print("⬇️ Loading MusicGen model...")
        model = MusicGen.get_pretrained("medium", device=DEVICE)
        download_checkpoint()
        state_dict = torch.load(LOCAL_CHECKPOINT, map_location=DEVICE)
        model.lm.load_state_dict(state_dict)
        print("✅ Model loaded successfully!")

# --- Utility to sanitize prompt for filenames ---
def sanitize_prompt(prompt: str):
    return "_".join(re.findall(r'\w+', prompt.lower()))

# --- Generate music and save to WAV ---
def generate_music_file(prompt: str, duration: int = 10):
    load_model()  # ensure model is loaded

    sample_rate = 32000
    full_prompt = prompt

    # Adjusted generation params
    duration = int(duration * 1.2)
    model.set_generation_params(
        duration=duration,
        top_k=200,
        top_p=0.97,
        temperature=1.0,
        cfg_coef=2.5,
        two_step_cfg=True
    )

    print(f"🎵 Generating music for: '{full_prompt}' ({duration}s)")

    with torch.no_grad():
        audio = model.generate([full_prompt], progress=True)

    decoded_audio = audio.cpu().numpy().squeeze()

    # Normalize with soft clipping
    decoded_audio = decoded_audio / max(np.max(np.abs(decoded_audio)), 1e-5)
    decoded_audio = np.tanh(decoded_audio)

    # Dithering for 16-bit WAV
    dither = np.random.uniform(-1.0 / 32767, 1.0 / 32767, decoded_audio.shape)
    decoded_audio = np.clip(decoded_audio + dither, -1.0, 1.0)
    int_audio = (decoded_audio * 32767).astype(np.int16)

    timestamp = time.strftime("%Y%m%dT%H%M%S")
    keywords = f"{fixed_keywords}_{sanitize_prompt(prompt)}"
    output_dir = Path("generated")
    output_dir.mkdir(exist_ok=True)
    file_name = f"{timestamp}_{keywords}.wav"
    file_path = output_dir / file_name

    wav_write(str(file_path), sample_rate, int_audio)

    del audio, decoded_audio, int_audio, dither
    torch.cuda.synchronize()
    torch.cuda.empty_cache()

    return str(file_path)

# --- API endpoint ---
@app.get("/generate_music")
def generate_music_endpoint(
    prompt: str = Query(..., description="Music prompt/description"),
    duration: int = Query(10, description="Duration in seconds"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    audio_file = generate_music_file(prompt, duration)
    background_tasks.add_task(os.remove, audio_file)
    return FileResponse(audio_file, media_type="audio/wav", filename=os.path.basename(audio_file))