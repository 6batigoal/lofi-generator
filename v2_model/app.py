import streamlit as st
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from datetime import datetime
import os
import torch

st.title("🎵 Lofi Music Generator")

# --- Create output folder ---
OUTPUT_FOLDER = "generated_music"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Load model once ---
@st.cache_resource
def load_model():
    return MusicGen.get_pretrained("facebook/musicgen-small")

model = load_model()
st.text("✅ Lofi-generator loaded, time to spin!")

# --- User inputs ---
fixed_keyword = "lofi"
available_keywords = ["chill", "study", "rain", "coffee", "night", "zen", "jazz", "forest", "ocean"]
selected_keywords = st.multiselect("Choose additional keywords:", options=available_keywords)

# --- Updated duration options ---
duration_map = {"5 seconds": 5, "10 seconds": 10, "30 seconds": 30, "60 seconds": 60}
duration_choice = st.selectbox("Select music duration:", list(duration_map.keys()))
duration = duration_map[duration_choice]

# --- Estimated waiting times (15s per 5s of music) ---
waiting_time_map = {str(sec) + " seconds": int(sec / 5 * 15) for sec in duration_map.values()}

# --- Helper to generate filename ---
def generate_filename(prompt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = prompt.replace(" ", "_")
    return f"{timestamp}_{safe_prompt}"

# --- Generate music ---
est_time = waiting_time_map[duration_choice]
button_label = f"Generate Music (⏳Wait time ~{est_time}s)"

if st.button(button_label):
    if not selected_keywords:
        st.error("Please choose at least one additional keyword.")
    else:
        keywords = [fixed_keyword] + selected_keywords
        prompt = " ".join(keywords)
        st.text(f"Generating {duration}s music for: {prompt}")
        st.info(f"⏳ Estimated waiting time: ~{est_time} seconds")

        with st.spinner("Generating music..."):
            model.set_generation_params(duration=duration)
            audio = model.generate([prompt])

        # Save audio
        filename = generate_filename(prompt)
        output_base = os.path.join(OUTPUT_FOLDER, filename)
        audio_write(output_base, audio[0].cpu(), model.sample_rate, strategy="loudness")
        wav_path = f"{output_base}.wav"

        # Play and download
        st.success("✅ Music generated!")
        st.audio(wav_path)
        with open(wav_path, "rb") as f:
            st.download_button(
                label="⬇️ Download your track",
                data=f,
                file_name=os.path.basename(wav_path),
                mime="audio/wav"
            )
