# agents/script_agent.py
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

EURON_API_URL = "https://api.euron.one/api/v1/euri/chat/completions"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL = "gpt-4.1-nano"
GROQ_MODEL = "llama-3.3-70b"  # change per your Groq availability


def call_euron(prompt: str, num_scenes: int):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {EURON_API_KEY}"}
    payload = {
        "messages": [
            {"role": "system", "content": f"You are a storytelling assistant. Return ONLY a valid JSON array. Each scene must be an object with scene_number, narration, image_prompt."},
            {"role": "user", "content": prompt}
        ],
        "model": MODEL,
        "max_tokens": 1500,
        "temperature": 0.8
    }
    return requests.post(EURON_API_URL, headers=headers, json=payload, timeout=120)


def call_groq(prompt: str, num_scenes: int):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "messages": [
            {"role": "system", "content": f"You are a storytelling assistant. Return ONLY a valid JSON array. Each scene must be an object with scene_number, narration, image_prompt."},
            {"role": "user", "content": prompt}
        ],
        "model": GROQ_MODEL,
        "temperature": 0.8
    }
    return requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=120)


def clean_model_output(text: str) -> str:
    """Remove common markdown fences and whitespace that can wrap JSON."""
    s = text.strip()
    # remove triple-backtick blocks
    if s.startswith("```") and s.endswith("```"):
        # remove fence and optional language marker
        lines = s.splitlines()
        if len(lines) >= 2:
            # drop first and last line
            s = "\n".join(lines[1:-1]).strip()
    # remove inline code fences
    s = s.strip("` \n")
    return s


def parse_script_content(content: str):
    """Try to decode content which might be JSON or stringified JSON."""
    content = clean_model_output(content)
    try:
        parsed = json.loads(content)
        # If parsed still a string, parse again
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
    except json.JSONDecodeError:
        # try one more manual cleanup and parse
        cleaned = content.replace('\n', '').strip()
        parsed = json.loads(cleaned)  # let exception propagate if truly broken
    if not isinstance(parsed, list):
        raise ValueError("Model output parsed but is not a JSON list.")
    return parsed


def generate_story_script(prompt: str, num_scenes: int = 3) -> list:
    log_step("Generating story script (Euron primary, Groq fallback)")
    # Try Euron first if key present
    if EURON_API_KEY:
        try:
            resp = call_euron(prompt, num_scenes)
            if resp.status_code in (401, 403):
                log_warn(f"Euron responded {resp.status_code}. Will try Groq fallback.")
                raise RuntimeError(f"Euron HTTP {resp.status_code}")
            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            safe_print("Raw output (Euron):")
            safe_print(content)
            return parse_script_content(content)
        except Exception as e:
            log_warn(f"Euron failed: {e}")
    # Fallback to Groq
    if GROQ_API_KEY:
        log_step("Using Groq fallback for story generation")
        resp = call_groq(prompt, num_scenes)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        safe_print("Raw output (Groq):")
        safe_print(content)
        return parse_script_content(content)
    raise RuntimeError("No working LLM API key available (Euron/Groq).")


def save_script(script_data: list, base_output_dir: Path, filename: str = "story.json"):
    script_dir = base_output_dir / "script"
    script_dir.mkdir(parents=True, exist_ok=True)
    path = script_dir / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    log_success(f"Script saved: {path}")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        user_prompt = sys.argv[1]
        base_output_dir = Path(sys.argv[2])
    else:
        user_prompt = input("Enter story idea: ")
        base_output_dir = Path("output/manual_test")
        base_output_dir.mkdir(parents=True, exist_ok=True)

    script = generate_story_script(user_prompt, num_scenes=3)
    save_script(script, base_output_dir)
