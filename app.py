# app.py

import streamlit as st
import subprocess
import sys
from pathlib import Path
import time

# Ensure root directory (project base) is in sys.path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# ✅ Use shared logging utilities
from utils.log_utils import safe_print, log_step, log_success, log_error
# === Streamlit UI Setup ===
st.set_page_config(page_title="AI Story Generator 🎥", layout="centered")
st.title("🎬 AI Storytelling Video Generator")

prompt = st.text_area(
    "📝 Enter your story idea",
    placeholder="e.g., Grandmother telling a story of Arjun and Karna...",
)

genre = st.selectbox(
    "📚 Choose genre", ["Adventure", "Fantasy", "Mythology", "Comedy", "Sci-Fi"]
)

length = st.select_slider(
    "⏳ Select desired video length (minutes)", options=[1, 2, 3, 5, 10], value=3
)

if st.button("🚀 Generate Story Video"):
    if not prompt.strip():
        st.warning("Please enter a story idea!")
        st.stop()

    # === Unique output folder per generation ===
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_folder = Path(f"output/generated_videos/{timestamp}")
    output_folder.mkdir(parents=True, exist_ok=True)

    progress = st.progress(0)
    status = st.empty()

    st.info("⏳ Generating your AI story video... This may take several minutes.")
    st.text("You can relax while your story is being crafted 🎨")

    # === Sequential Agent Steps ===
    steps = [
        ("🧠 Generating Story Script", "Script Agent"),
        ("🎙️ Generating Voice Narration", "TTS Agent"),
        ("🎨 Creating Scene Images", "Image Agent"),
        ("🎬 Compiling Final Video", "Video Agent"),
    ]

    total_steps = len(steps)
    success = True

    for idx, (desc, agent_name) in enumerate(steps, start=1):
        status.info(f"{desc} ...")
        progress.progress((idx - 1) / total_steps)

        cmd = [
            sys.executable,
            "generate_full_story.py" if agent_name == "Script Agent" else f"agents/{agent_name.lower().replace(' ', '_')}.py",
            f"{prompt} in {genre} genre, make it approximately {length} minute story"
            if agent_name == "Script Agent"
            else str(output_folder),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            st.error(f"❌ {agent_name} failed!")
            st.text("---- STDERR ----")
            st.code(result.stderr)
            st.stop()
            success = False
            break

        log_success(f"{agent_name} completed successfully.")
        progress.progress(idx / total_steps)

    if success:
        progress.progress(1.0)
        status.success("✅ All steps completed!")

    # === Locate final video ===
    possible_videos = list(output_folder.rglob("final_story.mp4"))
    if not possible_videos:
        possible_videos = list(Path("output").rglob("final_story.mp4"))

    if possible_videos:
        final_video = possible_videos[0]
        st.success("✅ Video generated successfully!")
        st.video(str(final_video))

        with open(final_video, "rb") as f:
            st.download_button(
                label="⬇️ Download Video",
                data=f,
                file_name=f"story_{timestamp}.mp4",
                mime="video/mp4",
            )

        log_success(f"Video ready for download: {final_video}")
    else:
        st.error("❌ Something went wrong — no video file found.")
        st.text("Debug logs:")
        st.code(result.stdout + "\n" + result.stderr)
        log_error("No video file found after pipeline execution.")
