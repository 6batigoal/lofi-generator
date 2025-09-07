import streamlit as st
import requests
from datetime import datetime
import os
from pydub import AudioSegment  # NEW

API_URL = st.secrets["backend"]["url"] + "/generate_music"

st.set_page_config(page_title="Lofi Music Generator", page_icon="🎵", layout="centered")
st.title("🎶 Lofi Music Generator")
st.subheader("Restricting music generation to 30 seconds to avoid backend errors")

# Ensure generated folder exists
os.makedirs("generated", exist_ok=True)

# --- Primary Lo-Fi subgenres ---
primary_subgenres = [
    "Chillhop", "Hip-Hop", "Jazz", "House", "Vaporwave",
    "Ambient", "Synthwave", "Indie Rock", "Japan",
    "Funk", "Neo-Soul", "Trip-Hop", "Downtempo",
    "Lounge", "Classical", "Piano", "Bossa Nova",
    "Jazz Fusion", "Electronic", "IDM", "Retro Synth", "Dream Pop"
]

# --- Secondary tags ---
mood_keywords = [
    "evening vibes", "morning vibes", "night vibes", "sunset",
    "study", "workout", "relax", "focus", "chill", "cozy",
    "sleep", "dreamy", "nostalgic", "melancholic", "uplifting",
    "playful", "romantic", "sad", "meditative", "energetic",
    "moody", "warm", "reflective"
]

atmosphere_keywords = [
    "cafe", "forest", "rain", "mountains", "city",
    "space", "train", "subway", "station", "library", "study room",
    "snow", "winter", "ocean", "river", "twilight", "sunrise",
    "sunset", "night", "cozy room", "vintage", "retro", "vinyl",
    "storm", "wind", "fireplace", "park", "street", "neon lights",
    "coffee shop", "campfire", "desert", "tropical", "loft", "attic"
]

# --- Preset prompts ---
preset_prompts = [
    "Chillhop, focus, library",
    "Jazz, lounge, night",
    "Ambient, calm, forest",
    "Funk, relaxed, cozy room",
    "Synthwave, reflective, neon lights",
    "Piano, dreamy, night",
    "Trip-Hop, moody, subway",
    "Downtempo, chill, mountains",
    "Hip-Hop, energetic, New York City",
    "House, upbeat, street",
    "Neo-Soul, lively, cafe",
    "Bossa Nova, romantic, beach",
    "Synthwave, dreamy, space",
    "Vaporwave, chill, retro loft"
]

# --- Duration choices ---
duration_map = {
    "10 seconds": 10,
    "20 seconds": 20,
    "30 seconds": 30,
    "60 seconds (looped)": 60,  # NEW
}
duration_choice = st.selectbox("Select music duration:", list(duration_map.keys()))
duration = duration_map[duration_choice]

# --- Preset or manual selection ---
use_preset = st.checkbox("🪄 Use a preset prompt instead of manual selection")

# --- Fixed parameters ---
fixed_keyword = "lofi"

# --- Prompt selection ---
if use_preset:
    selected_preset = st.selectbox("Pick a preset:", options=preset_prompts)
    prompt = f"{fixed_keyword}, {selected_preset}"
else:
    selected_subgenre = st.selectbox("🎵 Primary Lo-Fi Subgenre", options=primary_subgenres)
    selected_mood = st.multiselect("🎯 Mood", options=mood_keywords)
    selected_atmosphere = st.multiselect("🌌 Atmosphere", options=atmosphere_keywords)
    all_keywords = selected_mood + selected_atmosphere
    prompt_parts = [fixed_keyword, selected_subgenre] + all_keywords
    prompt = ", ".join(prompt_parts)

# --- Generate filename ---
def generate_filename(prompt, suffix=""):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = prompt.replace(", ", "_").replace(" ", "_")
    return f"generated/{timestamp}_{safe_prompt}{suffix}.wav"

# --- Helper to loop audio ---
def make_looped_version(file_path, repeat=2):
    audio = AudioSegment.from_wav(file_path)
    looped = audio * repeat
    looped_file = file_path.replace(".wav", f"_looped.wav")
    looped.export(looped_file, format="wav")
    return looped_file

# --- Generate music button ---
button_label = f"Generate Music (⏳ ~{int(duration*3)}s)"
if st.button(button_label):
    if not prompt:
        st.error("Please select a prompt or preset.")
    else:
        # Always request max 30s from backend
        backend_duration = min(duration, 30)

        st.text(f"Generating {backend_duration}s music for: {prompt}")
        st.info(f"⏳ Estimated waiting time: ~{int(backend_duration*3)} seconds")

        with st.spinner("Generating music..."):
            try:
                params = {"prompt": prompt, "duration": backend_duration}
                response = requests.get(API_URL, params=params)
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Request failed: {e}")
                response = None

        if response and response.status_code == 200:
            output_file = generate_filename(prompt)
            with open(output_file, "wb") as f:
                f.write(response.content)

            # Loop if user asked for 60s
            if duration == 60:
                output_file = make_looped_version(output_file, repeat=2)

            st.success("✅ Music generated!")
            st.audio(output_file, format="audio/wav")

            with open(output_file, "rb") as f:
                st.download_button("⬇️ Download your track", f, file_name=os.path.basename(output_file))
        elif response:
            st.error(f"❌ Failed to generate music. Status code: {response.status_code}")