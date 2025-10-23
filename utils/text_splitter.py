"""Splits story text into meaningful scenes for video rendering."""
"""
Splits the storytelling script into smaller, meaningful scene segments.
This helps us create synchronized visuals and audio for each scene.
"""

import re
from typing import List

def split_script_into_scenes(script: str, max_chars: int = 250) -> List[str]:
    """
    Splits a storytelling script into smaller scenes without breaking sentences abruptly.

    Args:
        script (str): The full storytelling script.
        max_chars (int): Approximate max number of characters per scene.

    Returns:
        List[str]: A list of scene text segments.
    """

    # Clean script and normalize spacing
    script = script.replace("\n", " ").strip()
    script = re.sub(r'\s+', ' ', script)

    # Split by sentence delimiters
    sentences = re.split(r'(?<=[.!?])\s+', script)
    scenes = []
    current_scene = ""

    for sentence in sentences:
        # If adding this sentence stays within the limit, append
        if len(current_scene) + len(sentence) + 1 <= max_chars:
            current_scene += sentence + " "
        else:
            # Close current scene and start a new one
            if current_scene.strip():
                scenes.append(current_scene.strip())
            current_scene = sentence + " "

    # Append any remaining text
    if current_scene.strip():
        scenes.append(current_scene.strip())

    return scenes


# Optional: test script splitting directly
if __name__ == "__main__":
    test_script = """
    Once upon a time in a quiet forest, a little fox named Lila gazed at the night sky.
    She noticed a single bright star twinkling softly. Every night, she watched it shine.
    One evening, she decided to follow the star through the forest. She crossed rivers and hills.
    Finally, she reached a glowing lake, where the star’s reflection sparkled like magic.
    Lila smiled, realizing the star had guided her home to a place of wonder and peace.
    """

    scenes = split_script_into_scenes(test_script, max_chars=180)
    print(f"🧠 Total scenes: {len(scenes)}\n")
    for idx, s in enumerate(scenes, 1):
        print(f"Scene {idx}: {s}\n")
