import os
import json
import sys
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load API Key
load_dotenv()
EURON_API_KEY = os.getenv("EURON_API_KEY")
if not EURON_API_KEY:
    raise ValueError("❌ EURON_API_KEY not found in .env file!")

IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
IMAGE_URL = "https://api.euron.one/api/v1/euri/images/generations"


def generate_scene_image(prompt: str, scene_number: int, image_dir: Path):
    """
    Calls Euron image generation API to generate an image for each scene.
    Handles both base64 and URL-based responses.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {EURON_API_KEY}"
    }

    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "size": "1024x1024"
    }

    response = requests.post(IMAGE_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    img_path = image_dir / f"scene_{scene_number}.jpg"
    img_data = None

    if "data" in data and len(data["data"]) > 0:
        entry = data["data"][0]
        if "url" in entry:
            # 🌐 Download the image from URL
            img_url = entry["url"]
            img_resp = requests.get(img_url)
            img_resp.raise_for_status()
            img_data = img_resp.content
        elif "b64_json" in entry:
            img_data = base64.b64decode(entry["b64_json"])
        elif "image" in entry:
            img_data = base64.b64decode(entry["image"])
        else:
            raise ValueError(f"❌ Unexpected image format: {data}")
    else:
        raise ValueError(f"❌ No image data returned: {data}")

    with open(img_path, "wb") as f:
        f.write(img_data)

    print(f"🖼️ Scene {scene_number} image saved: {img_path}")
    return img_path


def process_story_script(base_output_dir: Path):
    """
    Reads story.json and generates an image per scene in its own subfolder.
    """
    script_file = base_output_dir / "script" / "story.json"
    if not script_file.exists():
        print(f"❌ No story script found at {script_file}. Run script_agent.py first.")
        return

    image_dir = base_output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    with open(script_file, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    for scene in scenes:
        generate_scene_image(scene["image_prompt"], scene["scene_number"], image_dir)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        base_output_dir = Path(sys.argv[1])
    else:
        # fallback for manual testing
        base_output_dir = Path("output/manual_test")
        base_output_dir.mkdir(parents=True, exist_ok=True)

    process_story_script(base_output_dir)
    print("✅ All scene images generated.")