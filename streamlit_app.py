import streamlit as st
import requests
from datetime import datetime
import os

# Read backend URL
with open("backend_url.txt", "r") as f:
    API_URL = f.read().strip() + "/generate_music"

st.set_page_config(page_title="AI Music Generator", page_icon="🎵", layout="centered")
st.title("🎶 AI Music Generator")

# Ensure generated folder exists
os.makedirs("generated", exist_ok=True)

# Keyword categories
mood_keywords = ["study","workout","relax","focus","chill"]
atmosphere_keywords = ["cafe","forest","rain","beach","mountains","city","space"]
style_keywords = ["cyberpunk","japanese","piano only","jazz","ambient","retro","flute"]

selected_mood = st.multiselect("🎯 Mood", options=mood_keywords)
selected_atmosphere = st.multiselect("🌌 Atmosphere", options=atmosphere_keywords)
selected_style = st.multiselect("🎼 Style", options=style_keywords)

all_keywords = selected_mood + selected_atmosphere + selected_style
fixed_keyword = "lo-fi"

duration_map = { "5 seconds": 5, "10 seconds": 10, "30 seconds": 30, "60 seconds": 60 }
duration_choice = st.selectbox("Select music duration:", list(duration_map.keys()))
duration = duration_map[duration_choice]

waiting_time_map = {str(sec) + " seconds": int(sec/5*15) for sec in duration_map.values()}
est_time = waiting_time_map[duration_choice]

def generate_filename(prompt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = prompt.replace(", ", "_")
    return f"generated/{timestamp}_{safe_prompt}.wav"

button_label = f"Generate Music (⏳ ~{est_time}s)"
if st.button(button_label):
    if not all_keywords:
        st.error("Please select at least one keyword from Mood, Atmosphere, or Style.")
    else:
        prompt = ", ".join([fixed_keyword] + all_keywords)
        st.text(f"Generating {duration}s music for: {prompt}")
        st.info(f"⏳ Estimated waiting time: ~{est_time} seconds")

        with st.spinner("Generating music..."):
            try:
                params = { "prompt": prompt, "duration": duration }
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
