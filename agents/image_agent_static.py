"""Generates scene images using FLUX Schnell."""
"""
Generates scene images using FLUX Schnell model via Euron API.
Each scene text segment gets its own AI illustration.
"""

"""
Generates scene images using FLUX.1 Schnell model (Black Forest Labs) via Euron API.
Each scene text segment gets its own AI illustration.
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load API key
load_dotenv()
EURON_API_KEY = os.getenv("EURON_API_KEY")

# Euron Image Generation Endpoint
EURON_IMAGE_URL = "https://api.euron.one/api/v1/euri/images/generations"


def generate_scene_image(
    scene_text: str,
    scene_index: int,
    output_dir: str = "output/images",
    model: str = "black-forest-labs/FLUX.1-schnell",
    size: str = "1024x576"
) -> str:
    """
    Generate an image for a given scene using FLUX.1 Schnell model.

    Args:
        scene_text (str): The text of the scene.
        scene_index (int): Index of the scene (for file naming).
        output_dir (str): Where to save the generated image.
        model (str): The image generation model ID.
        size (str): Image size.

    Returns:
        str: Path to the saved image file.
    """
    if not EURON_API_KEY:
        raise ValueError("❌ EURON_API_KEY not found in environment variables.")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {EURON_API_KEY}"
    }

    # 🪄 Refined prompt for storytelling illustration
    prompt = (
        f"Children's storybook illustration. "
        f"Vibrant colors, soft lighting, magical and whimsical atmosphere. "
        f"Scene description: {scene_text}"
    )

    payload = {
        "prompt": prompt,
        "model": model,
        "size": size
    }

    try:
        response = requests.post(EURON_IMAGE_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        image_url = data["data"][0]["url"]
        img_data = requests.get(image_url).content

        image_path = os.path.join(output_dir, f"scene_{scene_index}.jpg")
        with open(image_path, "wb") as f:
            f.write(img_data)

        print(f"🖼 Image generated for scene {scene_index}: {image_path}")
        return image_path

    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling FLUX.1 Schnell API: {e}")
        print(f"Response: {getattr(e.response, 'text', 'No response')}")
        raise
    except KeyError:
        print(f"❌ Unexpected API response format: {response.text}")
        raise


# Optional: standalone test
if __name__ == "__main__":
    test_scene = "Lila the fox gazed at the starry night sky, feeling a warm glow around her."
    generate_scene_image(test_scene, scene_index=1)
