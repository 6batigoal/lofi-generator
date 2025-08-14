import streamlit as st
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from datetime import datetime
import os

st.title("🎵 Lofi Music Generator")

# --- Create output folder ---
OUTPUT_FOLDER = "generated_music"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Load model once ---
@st.cache_resource
def load_model():
    return MusicGen.get_pretrained("facebook/musicgen-small")

model = load_model()
st.text("✅ MusicGen model loaded")

# --- User inputs ---
fixed_keyword = "lofi"
available_keywords = ["chill", "study", "rain", "coffee", "night", "zen", "jazz", "forest", "ocean"]
selected_keywords = st.multiselect("Choose additional keywords:", options=available_keywords)

duration_map = {"5 seconds": 5, "10 seconds": 10, "15 seconds": 15}
duration_choice = st.selectbox("Select music duration:", list(duration_map.keys()))

# --- Generate music ---
if st.button("Generate Music"):
    if not selected_keywords:
        st.error("Please choose at least one additional keyword.")
    else:
        keywords = [fixed_keyword] + selected_keywords
        duration = duration_map[duration_choice]
        prompt = " ".join(keywords)
        st.text(f"Generating {duration}s music for: {prompt}")

        # Set generation params
        model.set_generation_params(duration=duration)

        # Generate audio
        audio = model.generate([prompt])

        # Save audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = prompt.replace(" ", "_")
        filename = f"{timestamp}_{safe_prompt}.wav"
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        audio_write(output_path, audio[0].cpu(), model.sample_rate, strategy="loudness")

        # Play audio
        st.success("✅ Music generated!")
        st.audio(output_path)
        st.markdown(f"[⬇️ Download your track]({output_path})")
