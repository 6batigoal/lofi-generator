import streamlit as st
import requests
from datetime import datetime
import os

# Read backend URL
with open("backend_url.txt", "r") as f:
    API_URL = f.read().strip() + "/generate_music"

st.set_page_config(page_title="Lofi Music Generator", page_icon="🎵", layout="centered")
st.title("🎶 Lofi Music Generator")

# Ensure generated folder exists
os.makedirs("generated", exist_ok=True)

# Primary Lo-Fi subgenres
primary_subgenres = [
    "Hip-Hop", "Chillhop", "Jazz", "House", "Vaporwave",
    "Ambient", "Synthwave", "Indie Rock", "Japan"
]

# Secondary tags
mood_keywords = ["study", "workout", "relax", "focus", "chill"]
atmosphere_keywords = ["cafe", "forest", "rain", "beach", "mountains", "city", "space"]

# UI selections
selected_subgenre = st.selectbox("🎵 Primary Lo-Fi Subgenre", options=primary_subgenres)
selected_mood = st.multiselect("🎯 Mood", options=mood_keywords)
selected_atmosphere = st.multiselect("🌌 Atmosphere", options=atmosphere_keywords)

all_keywords = selected_mood + selected_atmosphere
fixed_keyword = "lofi"

duration_map = {
    "5 seconds": 5,
    "10 seconds": 10,
    "30 seconds": 30,
    "1 minute": 60
}
duration_choice = st.selectbox("Select music duration:", list(duration_map.keys()))
duration = duration_map[duration_choice]

def generate_filename(prompt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = prompt.replace(", ", "_")
    return f"generated/{timestamp}_{safe_prompt}.wav"

button_label = f"Generate Music (⏳ ~{int(duration*3)}s)"
if st.button(button_label):
    if not selected_subgenre:
        st.error("Please select a primary Lo-Fi subgenre.")
    else:
        prompt_parts = [fixed_keyword, selected_subgenre] + all_keywords
        prompt = ", ".join(prompt_parts)
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
            output_file = generate_filename(prompt)
            with open(output_file, "wb") as f:
                f.write(response.content)
            st.success("✅ Music generated!")
            st.audio(output_file, format="audio/wav")
            with open(output_file, "rb") as f:
                st.download_button("⬇️ Download your track", f, file_name=os.path.basename(output_file))
        elif response:
            st.error(f"❌ Failed to generate music. Status code: {response.status_code}")