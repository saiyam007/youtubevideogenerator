import os
import json
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load API key from .env file
load_dotenv()
EURON_API_KEY = os.getenv("EURON_API_KEY")
if not EURON_API_KEY:
    raise ValueError("❌ EURON_API_KEY not found in .env file!")

EURON_API_URL = "https://api.euron.one/api/v1/euri/chat/completions"
MODEL = "gpt-4.1-nano"  # You can adjust model name if needed


def generate_story_script(prompt: str, num_scenes: int = 3) -> dict:
    """
    Calls Euron API to generate structured story script with scenes.
    """
    system_prompt = f"""
You are a storytelling assistant.
Generate a {num_scenes}-scene story based on the user's prompt.
Each scene must include:
- "scene_number": number of the scene
- "narration": the narration text for voiceover
- "image_prompt": a short visual description to generate an image.
Return the result as a valid JSON array.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {EURON_API_KEY}"
    }

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "model": MODEL,
        "max_tokens": 1500,
        "temperature": 0.8
    }

    response = requests.post(EURON_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    content = data["choices"][0]["message"]["content"]
    print("🧠 Raw LLM output:\n", content)

    try:
        script_data = json.loads(content)
        return script_data
    except json.JSONDecodeError:
        print("⚠️ Failed to parse JSON from LLM. Check the output format.")
        raise


def save_script(script_data: dict, base_output_dir: Path, filename: str = "story.json"):
    """
    Save generated story script to a unique subfolder under base_output_dir/script
    """
    script_dir = base_output_dir / "script"
    script_dir.mkdir(parents=True, exist_ok=True)

    file_path = script_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Script saved: {file_path}")


if __name__ == "__main__":
    # If run from CLI with args
    if len(sys.argv) >= 3:
        user_prompt = sys.argv[1]
        base_output_dir = Path(sys.argv[2])
    else:
        # Fallback for manual testing
        user_prompt = input("📝 Enter your story idea: ")
        base_output_dir = Path("output/manual_test")
        base_output_dir.mkdir(parents=True, exist_ok=True)

    story_script = generate_story_script(user_prompt, num_scenes=3)
    save_script(story_script, base_output_dir)