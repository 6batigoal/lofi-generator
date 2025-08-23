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

app = FastAPI()

# Device setup
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading MusicGen pretrained model (small)...")
model = MusicGen.get_pretrained("small", device=DEVICE)
print("Model loaded successfully!")

def sanitize_prompt(prompt: str):
    return "_".join(re.findall(r'\w+', prompt.lower()))

def generate_music_file(prompt: str, duration: int = 10, seed: int = None):
    sample_rate = 48000
    fixed_keywords = "lo-fi"
    adjusted_duration = int(duration * 1.5)
    full_prompt = f"{fixed_keywords} {prompt}"

    # Set seeds for reproducibility
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)

    model.set_generation_params(duration=adjusted_duration)
    print(f"Generating music for: '{full_prompt}' ({adjusted_duration}s), seed={seed}")
    
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
    return str(file_path)

@app.get("/generate_music")
def generate_music_endpoint(
    prompt: str = Query(..., description="Music prompt/description"),
    duration: int = Query(10, description="Duration in seconds"),
    seed: int = Query(None, description="Optional seed for reproducible generation"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    audio_file = generate_music_file(prompt, duration, seed)
    background_tasks.add_task(os.remove, audio_file)
    return FileResponse(audio_file, media_type="audio/wav", filename=os.path.basename(audio_file))
