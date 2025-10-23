import os
import json
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load API key from .env
load_dotenv()
EURON_API_KEY = os.getenv("EURON_API_KEY")
if not EURON_API_KEY:
    raise ValueError("❌ EURON_API_KEY not found in .env file!")

TTS_MODEL = "playai-tts"
TTS_URL = "https://api.euron.one/api/v1/euri/audio/speech"  # ✅ Correct TTS endpoint


def generate_tts(text: str, scene_number: int, audio_dir: Path) -> Path:
    """
    Calls TTS API to generate audio file for a scene narration.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {EURON_API_KEY}"
    }

    payload = {
        "model": TTS_MODEL,
        "input": text,
        # Optional fields if needed:
        # "voice": "alloy",
        # "language": "en",
        # "speed": 1.0
    }

    response = requests.post(TTS_URL, headers=headers, json=payload)
    response.raise_for_status()

    audio_path = audio_dir / f"scene_{scene_number}.mp3"
    with open(audio_path, "wb") as f:
        f.write(response.content)

    print(f"🔊 Scene {scene_number} audio saved: {audio_path}")
    return audio_path


def process_story_script(base_output_dir: Path):
    """
    Reads story.json from script subfolder and generates TTS for each scene.
    """
    script_file = base_output_dir / "script" / "story.json"
    if not script_file.exists():
        print(f"❌ No story script found at {script_file}. Run script_agent.py first.")
        return

    # 🎧 Create audio_segments subfolder
    audio_dir = base_output_dir / "audio_segments"
    audio_dir.mkdir(parents=True, exist_ok=True)

    with open(script_file, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    for scene in scenes:
        scene_number = scene["scene_number"]
        narration = scene["narration"]
        generate_tts(narration, scene_number, audio_dir)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        base_output_dir = Path(sys.argv[1])
    else:
        # fallback for manual testing
        base_output_dir = Path("output/manual_test")
        base_output_dir.mkdir(parents=True, exist_ok=True)

    process_story_script(base_output_dir)
    print("✅ TTS generation completed.")