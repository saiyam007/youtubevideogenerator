# agents/tts_agent.py
import os
import json
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
    
from utils.log_utils import safe_print, log_step, log_success, log_error, log_warn

load_dotenv()
EURON_API_KEY = os.getenv("EURON_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not EURON_API_KEY and not GROQ_API_KEY:
    raise ValueError("No TTS API keys provided (EURON or GROQ).")

# Euron TTS
EURON_TTS_URL = "https://api.euron.one/api/v1/euri/audio/speech"
EURON_TTS_MODEL = "playai-tts"

# Groq TTS fallback
GROQ_TTS_URL = "https://api.groq.com/openai/v1/audio/speech"
GROQ_TTS_MODEL = "playai-tts"  # adjust if Groq provides a different id

TIMEOUT = 120


def generate_tts_euron(text: str) -> bytes:
    headers = {"Authorization": f"Bearer {EURON_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": EURON_TTS_MODEL, "input": text}
    r = requests.post(EURON_TTS_URL, headers=headers, json=payload, timeout=TIMEOUT)
    if r.status_code == 403:
        raise PermissionError("Euron TTS quota reached (403).")
    r.raise_for_status()
    return r.content


def generate_tts_groq(text: str) -> bytes:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": GROQ_TTS_MODEL, "input": text}
    r = requests.post(GROQ_TTS_URL, headers=headers, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.content


def load_script_json(script_path: Path):
    if not script_path.exists():
        raise FileNotFoundError(f"Script file not found: {script_path}")
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, str):
        safe_print("Detected stringified JSON in script. Reparsing.")
        data = json.loads(data)
    if not isinstance(data, list):
        raise ValueError("Invalid script.json structure: expected list.")
    return data


def process_story_script(base_output_dir: Path):
    log_step("TTS generation step")
    script_path = base_output_dir / "script" / "story.json"
    scenes = load_script_json(script_path)

    audio_dir = base_output_dir / "audio_segments"
    audio_dir.mkdir(parents=True, exist_ok=True)

    for scene in scenes:
        if not isinstance(scene, dict):
            log_warn(f"Skipping invalid scene: {scene}")
            continue
        scene_number = scene.get("scene_number")
        narration = scene.get("narration")
        if not narration:
            log_warn(f"Scene {scene_number} missing narration, skipping.")
            continue

        audio_bytes = None
        # Try Euron first
        if EURON_API_KEY:
            try:
                audio_bytes = generate_tts_euron(narration)
                audio_path = audio_dir / f"scene_{scene_number}.mp3"
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
                log_success(f"Euron TTS saved: {audio_path}")
            except Exception as e:
                log_warn(f"Euron TTS failed for scene {scene_number}: {e}")

        # If no audio, try Groq
        if audio_bytes is None and GROQ_API_KEY:
            try:
                audio_bytes = generate_tts_groq(narration)
                audio_path = audio_dir / f"scene_{scene_number}.mp3"
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
                log_success(f"Groq TTS saved: {audio_path}")
            except Exception as e:
                log_error(f"Groq TTS failed for scene {scene_number}: {e}")

        if audio_bytes is None:
            log_warn(f"Skipping scene {scene_number}; no TTS produced.")

    log_success("TTS generation completed.")


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        base_output_dir = Path(sys.argv[1])
    else:
        base_output_dir = Path("output/manual_test")
        base_output_dir.mkdir(parents=True, exist_ok=True)
    process_story_script(base_output_dir)
