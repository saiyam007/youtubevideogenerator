# agents/image_agent.py
import os
import json
import base64
import requests
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure root directory (project base) is in sys.path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# ✅ Use shared logging utilities
from utils.log_utils import safe_print, log_step, log_success, log_error
from utils.log_utils import safe_print, log_step, log_success, log_error, log_warn

load_dotenv()
EURON_API_KEY = os.getenv("EURON_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not EURON_API_KEY and not GROQ_API_KEY:
    raise ValueError("No image API keys provided (EURON or GROQ).")

EURON_IMAGE_URL = "https://api.euron.one/api/v1/euri/images/generations"
EURON_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

GROQ_IMAGE_URL = "https://api.groq.com/openai/v1/images/generations"
GROQ_IMAGE_MODEL = "flux-1-schnell"  # adjust per Groq console

TIMEOUT = 120


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


def _save_image_bytes(img_bytes: bytes, img_path: Path):
    with open(img_path, "wb") as f:
        f.write(img_bytes)
    log_success(f"Saved image: {img_path}")


def generate_scene_image_euron(prompt: str, size: str = "1024x1024"):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {EURON_API_KEY}"}
    payload = {"model": EURON_IMAGE_MODEL, "prompt": prompt, "size": size}
    r = requests.post(EURON_IMAGE_URL, headers=headers, json=payload, timeout=TIMEOUT)
    if r.status_code == 403:
        raise PermissionError("Euron image quota reached (403).")
    r.raise_for_status()
    return r.json()


def generate_scene_image_groq(prompt: str, size: str = "1024x1024"):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {"model": GROQ_IMAGE_MODEL, "prompt": prompt, "size": size}
    r = requests.post(GROQ_IMAGE_URL, headers=headers, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def extract_image_bytes_from_response(data: dict):
    # supports keys: url, b64_json, image
    if "data" in data and len(data["data"]) > 0:
        item = data["data"][0]
        if "url" in item:
            r = requests.get(item["url"], timeout=TIMEOUT)
            r.raise_for_status()
            return r.content
        for k in ("b64_json", "image"):
            if k in item:
                return base64.b64decode(item[k])
    raise ValueError("No image bytes found in response.")


def generate_scene_image(prompt: str, scene_number: int, image_dir: Path):
    log_step(f"Generating image for scene {scene_number}")
    # Try Euron
    data = None
    try:
        if EURON_API_KEY:
            resp = generate_scene_image_euron(prompt)
            data = resp
    except Exception as e:
        log_warn(f"Euron image generation failed: {e}")

    # Fallback Groq
    if data is None and GROQ_API_KEY:
        try:
            resp = generate_scene_image_groq(prompt)
            data = resp
        except Exception as e:
            log_error(f"Groq image generation failed: {e}")

    if data is None:
        raise RuntimeError("Both Euron and Groq image generation failed.")

    img_bytes = extract_image_bytes_from_response(data)
    img_path = image_dir / f"scene_{scene_number}.jpg"
    _save_image_bytes(img_bytes, img_path)
    return img_path


def process_story_script(base_output_dir: Path):
    log_step("Image generation step")
    script_path = base_output_dir / "script" / "story.json"
    scenes = load_script_json(script_path)

    image_dir = base_output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    for scene in scenes:
        if not isinstance(scene, dict):
            log_warn(f"Skipping invalid scene: {scene}")
            continue
        prompt = scene.get("image_prompt") or scene.get("narration") or "illustration"
        scene_number = scene.get("scene_number")
        try:
            generate_scene_image(prompt, scene_number, image_dir)
        except Exception as e:
            log_error(f"Failed to generate image for scene {scene_number}: {e}")

    log_success("Image generation completed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agents/image_agent.py <base_output_dir>")
        sys.exit(1)
    base_output_dir = Path(sys.argv[1])
    process_story_script(base_output_dir)
