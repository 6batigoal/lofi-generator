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


# --- Load base model ---
print("Loading MusicGen base model (medium)...")
model = MusicGen.get_pretrained("medium", device=DEVICE)

# --- Download + load improved checkpoint ---
download_checkpoint()
print("Loading custom checkpoint weights...")
state_dict = torch.load(LOCAL_CHECKPOINT, map_location=DEVICE)
model.lm.load_state_dict(state_dict)
print("✅ Custom medium model loaded successfully!")


# --- Utility to sanitize prompt for filenames ---
def sanitize_prompt(prompt: str):
    return "_".join(re.findall(r'\w+', prompt.lower()))


# --- Generate music and save to WAV (optimized for GPU memory & best parameters) ---
def generate_music_file(prompt: str, duration: int = 10):
    sample_rate = 32000  # Use your preferred sample rate
    full_prompt = prompt

    # Set generation parameters using your optimal local values
    model.set_generation_params(
        duration=int(duration * 1.5),
        top_k=250,
        top_p=0.95,
        temperature=1.0,
        cfg_coef=3.0,
        two_step_cfg=False
    )

    print(f"🎵 Generating music for: '{full_prompt}' ({duration}s)")

    with torch.no_grad():
        audio = model.generate([full_prompt], progress=True)

    decoded_audio = audio.cpu().numpy().squeeze()
    decoded_audio = decoded_audio / np.max(np.abs(decoded_audio))

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

    # Cleanup to free GPU memory
    del audio, decoded_audio, int_audio, dither
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