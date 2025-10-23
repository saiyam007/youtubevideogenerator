"""Converts text to speech using PlayAI TTS."""
"""
Converts full storytelling script into audio narration using PlayAI TTS via Euron API.
The output is a single MP3 file that will be later split per scene.
"""

"""
Converts full storytelling script into audio narration using PlayAI TTS via Euron API.
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()
EURON_API_KEY = os.getenv("EURON_API_KEY")

# ✅ Corrected endpoint
EURON_TTS_URL = "https://api.euron.one/api/v1/euri/audio/speech"


def text_to_speech(
    text: str,
    output_file: str = "output/audio/full_story.mp3",
    model: str = "playai-tts",
    voice: str = "alloy",
    format: str = "mp3"
) -> str:
    """
    Converts text to speech using PlayAI TTS model from Euron API.

    Args:
        text (str): The input text to convert.
        output_file (str): File path to save the audio file.
        model (str): TTS model (default: 'playai-tts').
        voice (str): Voice ID or name (e.g., 'alloy', 'en-US-1').
        format (str): Output audio format.

    Returns:
        str: Path to the generated audio file.
    """
    if not EURON_API_KEY:
        raise ValueError("❌ EURON_API_KEY not found in environment variables.")

    Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {EURON_API_KEY}"
    }

    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "format": format
    }

    try:
        response = requests.post(EURON_TTS_URL, headers=headers, json=payload)
        response.raise_for_status()

        with open(output_file, "wb") as f:
            f.write(response.content)

        print(f"🎧 Audio generated successfully: {output_file}")
        return output_file

    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling PlayAI TTS API: {e}")
        print(f"Response text: {getattr(e.response, 'text', 'No response')}")
        raise


# Optional: standalone test
if __name__ == "__main__":
    test_text = (
        "Once upon a time in a quiet forest, "
        "a little fox named Lila gazed at the stars. "
        "She decided to follow one bright star on an adventure."
    )
    text_to_speech(test_text)

