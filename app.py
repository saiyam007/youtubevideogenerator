import streamlit as st
import subprocess
import sys
from pathlib import Path
import shutil
import time

# ✅ UI Elements
st.set_page_config(page_title="AI Story Generator 🎥", layout="centered")

st.title("🎬 AI Storytelling Video Generator")

prompt = st.text_area("📝 Enter your story idea", placeholder="e.g., Grandmother telling a story of Arjun and Karna...")
genre = st.selectbox("📚 Choose genre", ["Adventure", "Fantasy", "Mythology", "Comedy", "Sci-Fi"])
length = st.select_slider("⏳ Select desired video length (minutes)", options=[1, 2, 3, 5, 10], value=2)

if st.button("🚀 Generate Story Video"):
    if not prompt.strip():
        st.warning("Please enter a story idea!")
    else:
        # Unique folder per run
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_folder = Path(f"output/generated_videos/{timestamp}")
        output_folder.mkdir(parents=True, exist_ok=True)

        st.info("⏳ Generating your story... This may take a few minutes.")

        # Run the full story generation with extra parameters
        cmd = [
            sys.executable,
            "generate_full_story.py",
            f"{prompt} in {genre} genre, make it approximately {length} minute story"
        ]
        subprocess.run(cmd, check=True)

        # Move final video to unique folder
        final_video = Path("output/video/final_story.mp4")
        if final_video.exists():
            shutil.copy(final_video, output_folder / "final_story.mp4")
            st.success("✅ Video generated successfully!")
            st.video(str(output_folder / "final_story.mp4"))
            with open(output_folder / "final_story.mp4", "rb") as f:
                st.download_button(
                    label="⬇️ Download Video",
                    data=f,
                    file_name=f"story_{timestamp}.mp4",
                    mime="video/mp4"
                )
        else:
            st.error("❌ Something went wrong. No video file found.")
