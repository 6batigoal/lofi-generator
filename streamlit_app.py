import streamlit as st
import random
import requests
from datetime import datetime
import os

API_URL = st.secrets["backend"]["url"] + "/generate_music"

st.set_page_config(page_title="Lofi Music Generator", page_icon="🎵", layout="centered")
st.title("🎶 Lofi Music Generator")

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
    "cafe", "forest", "rain", "beach", "mountains", "city",
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
    "5 seconds": 5,
    "10 seconds": 10,
    "30 seconds": 30,
    "1 minute": 60
}
duration_choice = st.selectbox("Select music duration:", list(duration_map.keys()))
duration = duration_map[duration_choice]

# --- Preset or manual selection ---
use_preset = st.checkbox("🪄 Use a preset prompt instead of manual selection")

# --- Fixed parameters ---
fixed_keyword = "lofi"

# random tempo
def get_random_tempo():
    # Common lofi tempos
    possible_bpms = [70, 72, 75, 78, 80]
    return f"{random.choice(possible_bpms)} BPM"

# --- Prompt selection ---
if use_preset:
    selected_preset = st.selectbox("Pick a preset:", options=preset_prompts)
    fixed_tempo = get_random_tempo()
    prompt = f"{fixed_keyword}, {fixed_tempo}, {selected_preset}"
else:
    selected_subgenre = st.selectbox("🎵 Primary Lo-Fi Subgenre", options=primary_subgenres)
    selected_mood = st.multiselect("🎯 Mood", options=mood_keywords)
    selected_atmosphere = st.multiselect("🌌 Atmosphere", options=atmosphere_keywords)
    all_keywords = selected_mood + selected_atmosphere
    fixed_tempo = get_random_tempo()
    prompt_parts = [fixed_keyword, fixed_tempo, selected_subgenre] + all_keywords
    prompt = ", ".join(prompt_parts)

# --- Generate filename ---
def generate_filename(prompt, exclude_tempo=True):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    safe_prompt = prompt
    if exclude_tempo:
        # Remove the fixed tempo from the filename
        safe_prompt = safe_prompt.replace(f"{fixed_tempo}, ", "")
        safe_prompt = safe_prompt.replace(f", {fixed_tempo}", "")
    
    # Replace commas and spaces with underscores
    safe_prompt = safe_prompt.replace(", ", "_").replace(" ", "_")
    return f"generated/{timestamp}_{safe_prompt}.wav"

# --- Generate music button ---
button_label = f"Generate Music (⏳ ~{int(duration*3)}s)"
if st.button(button_label):
    if not prompt:
        st.error("Please select a prompt or preset.")
    else:
        st.text(f"Generating {duration}s music for: {prompt}")
        st.info(f"⏳ Estimated waiting time: ~{int(duration*3)} seconds")

        with st.spinner("Generating music..."):
            try:
                params = {"prompt": prompt, "duration": duration}
                response = requests.get(API_URL, params=params)
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Request failed: {e}")
                response = None

        if response and response.status_code == 200:
            output_file = generate_filename(prompt, exclude_tempo=True)
            with open(output_file, "wb") as f:
                f.write(response.content)
            st.success("✅ Music generated!")
            st.audio(output_file, format="audio/wav")
            with open(output_file, "rb") as f:
                st.download_button("⬇️ Download your track", f, file_name=os.path.basename(output_file))
        elif response:
            st.error(f"❌ Failed to generate music. Status code: {response.status_code}")