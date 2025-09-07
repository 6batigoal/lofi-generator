import streamlit as st
import requests
from datetime import datetime
import os
from pydub import AudioSegment  # Required for looping, normalization, and crossfades

API_URL = st.secrets["backend"]["url"] + "/generate_music"

st.set_page_config(page_title="Lofi Music Generator", page_icon="🎵", layout="centered")
st.title("🎶 Lofi Music Generator")
st.subheader("Some keywords do not work well together ...")
st.subheader("Have fun trying to get the best mix!")

# Ensure generated folder exists
os.makedirs("generated", exist_ok=True)

# --- Primary Subgenres (refined for AI-friendly generation) ---
primary_subgenres = [
    "Chillhop", "Hip-Hop", "Jazz", "Chill Jazz", 
    "House", "Vaporwave", "Ambient", "Synthwave", "Dreamy Synth",
    "Indie Rock", "Funk", "Neo-Soul", "Trip-Hop", "Downtempo",
    "Lounge", "Classical", "Piano", "Bossa Nova", "Jazz Fusion", 
    "Electronic", "Tropical House", "Smooth R&B", "Dream Pop"
]

# --- Mood Keywords (refined for AI-friendly generation) ---
mood_keywords = [
    "calm", "soothing", "dreamy", "relaxing", "chill", "cozy",
    "nostalgic", "melancholy", "uplifted", "romantic", "playful",
    "energetic", "meditative", "focused", "ambient", "evening vibes",
    "morning vibes", "night vibes", "sunset", "sunrise"
]

# --- Atmosphere Keywords (refined for AI-friendly generation) ---
atmosphere_keywords = [
    "cafe", "library", "study room", "bedroom", "forest", "rain",
    "mountains", "ocean", "river", "city streets", "neon lights",
    "train", "subway", "street", "coffee shop", "campfire",
    "vintage", "retro", "vinyl crackle", "lofi bedroom", "cityscape at night",
    "twilight", "cozy room", "desert", "tropical", "loft", "attic"
]

# --- Preset Prompts (optimized for high-quality AI music generation) ---
preset_prompts = [
    "Chillhop, focus, library",
    "Jazz, lounge, night",
    "Ambient, calm, forest",
    "Funk, relaxed, cozy room",
    "Synthwave, reflective, neon lights",
    "Piano, dreamy, night",
    "Trip-Hop, moody, subway",
    "Downtempo, chill, mountains",
    "Hip-Hop, energetic, city streets",
    "House, upbeat, festival vibes",
    "Neo-Soul, lively, cafe",
    "Bossa Nova, romantic, beach",
    "Synthwave, dreamy, space",
    "Vaporwave, chill, retro loft",
    "Hip-Hop, calm, bedroom",
    "Chill Jazz, soothing, evening",
    "Ambient, ethereal, river",
    "Dreamy Synth, relaxing, neon city",
    "Hip-Hop, meditative, study room"
]

# --- Duration choices (added longer loop options) ---
duration_map = {
    "10 seconds": 10,
    "20 seconds": 20,
    "30 seconds": 30,
    "1 minute": 60,
    "1.5 minute": 90,  # 30s * 3
    "3 minutes": 180     # 30s * 6
}
duration_choice = st.selectbox("Select music duration:", list(duration_map.keys()))
duration = duration_map[duration_choice]

# --- Preset or manual selection ---
use_preset = st.checkbox("🪄 Use a preset prompt instead of manual selection")

# --- Fixed parameters ---
fixed_keyword = "lo-fi"

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

# --- Helper to loop & normalize audio (UPDATED: added crossfade for smoother loops) ---
def make_looped_version(file_path, repeat=1, normalize=False, crossfade_ms=500):
    audio = AudioSegment.from_wav(file_path)
    final_audio = audio
    for _ in range(repeat - 1):
        # Append with crossfade to smooth transition
        final_audio = final_audio.append(audio, crossfade=crossfade_ms)
    if normalize:
        final_audio = final_audio.normalize(headroom=5.0)  # Reduce very loud peaks
    looped_file = file_path.replace(".wav", f"_looped.wav")
    final_audio.export(looped_file, format="wav")
    return looped_file

# --- Generate music button ---
button_label = f"Generate Music (⏳ ~{int(min(duration,30)*3)}s)"
if st.button(button_label):
    if not prompt:
        st.error("Please select a prompt or preset.")
    else:
        # Always request max 30s from backend
        backend_duration = min(duration, 30)

        st.text(f"Generating {duration} seconds music for: {prompt}")
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

            # Determine how many times to loop
            if duration > 30:
                repeat_count = duration // 30  # e.g., 90s -> repeat 3 times
                output_file = make_looped_version(output_file, repeat=repeat_count, normalize=True, crossfade_ms=500)
                st.info(f"🎵 Generated track length: ~{duration} seconds")
            else:
                # Normalize even for single 30s clip
                audio = AudioSegment.from_wav(output_file).normalize(headroom=5.0)
                audio.export(output_file, format="wav")
                st.info(f"🎵 Generated track length: {duration} seconds")

            st.success("✅ Music generated!")
            st.audio(output_file, format="audio/wav")

            with open(output_file, "rb") as f:
                st.download_button("⬇️ Download your track", f, file_name=os.path.basename(output_file))
        elif response:
            st.error(f"❌ Failed to generate music. Status code: {response.status_code}")
