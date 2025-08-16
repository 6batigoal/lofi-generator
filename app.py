import streamlit as st
from audiocraft.models import MusicGen
from datetime import datetime
import torch
import io
import soundfile as sf

st.title("🎵 Lofi Music Generator")

# --- Load model once ---
@st.cache_resource
def load_model():
    return MusicGen.get_pretrained("facebook/musicgen-small")

model = load_model()
st.text("✅ Lofi-generator loaded, time to spin!")

# --- User inputs ---
fixed_keyword = "lofi"

# --- Keyword categories ---
mood_keywords = ["study", "workout", "relax", "focus", "chill"]
atmosphere_keywords = ["cafe", "forest", "rain", "beach", "mountains", "city"]
style_keywords = ["cyberpunk", "japanese", "piano only", "jazz", "ambient", "retro"]

# --- User selects from each category ---
selected_mood = st.multiselect(
    "🎯 Mood",
    options=mood_keywords,
    help="Pick the vibe you want to capture."
)
selected_atmosphere = st.multiselect(
    "🌌 Atmosphere",
    options=atmosphere_keywords,
    help="Pick the environment or ambiance."
)
selected_style = st.multiselect(
    "🎼 Style",
    options=style_keywords,
    help="Pick the musical style or influence."
)

# --- Combine all selected keywords ---
all_selected_keywords = selected_mood + selected_atmosphere + selected_style

st.markdown("---")

# --- Duration options ---
duration_map = {"5 seconds": 5, "10 seconds": 10, "30 seconds": 30, "60 seconds": 60}
duration_choice = st.selectbox("Select music duration:", list(duration_map.keys()))
duration = duration_map[duration_choice]

# --- Estimated waiting times (15s per 5s of music) ---
waiting_time_map = {str(sec) + " seconds": int(sec / 5 * 15) for sec in duration_map.values()}

# --- Helper to generate filename ---
def generate_filename(prompt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = prompt.replace(" ", "_")
    return f"{timestamp}_{safe_prompt}.wav"

# --- Generate music ---
est_time = waiting_time_map[duration_choice]
button_label = f"Generate Music (⏳Wait time ~{est_time}s)"

if st.button(button_label):
    if not all_selected_keywords:
        st.error("Please choose at least one keyword from Mood, Atmosphere, or Style.")
    else:
        keywords = [fixed_keyword] + all_selected_keywords
        prompt = ", ".join(keywords)  # comma-separated for better AI interpretation
        st.text(f"Generating {duration}s music for: {prompt}")
        st.info(f"⏳ Estimated waiting time: ~{est_time} seconds")

        with st.spinner("Generating music..."):
            model.set_generation_params(duration=duration)
            audio = model.generate([prompt])

        # Save audio to memory instead of disk
        wav_io = io.BytesIO()
        sf.write(wav_io, audio[0].cpu().numpy().T, model.sample_rate, format="WAV")
        wav_io.seek(0)

        # Play and download from memory
        st.success("✅ Music generated!")
        st.audio(wav_io, format="audio/wav")
        st.download_button(
            label="⬇️ Download your track",
            data=wav_io,
            file_name=generate_filename(prompt),
            mime="audio/wav"
        )
