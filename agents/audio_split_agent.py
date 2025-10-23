"""Splits full audio narration into smaller scene audio clips."""
"""
Splits the full narration audio into multiple scene segments based on text length proportion.
Each scene's audio is exported separately, matching the image sequence.
"""

import os
from pydub import AudioSegment
from pathlib import Path

# 🪄 Tell pydub exactly where ffmpeg is
AudioSegment.converter = r"C:\\ffmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\\ffmpeg\bin\\ffprobe.exe"


def estimate_scene_durations(scenes, total_audio_duration):
    """
    Estimate scene durations based on word count ratio.

    Args:
        scenes (list[str]): List of scene texts.
        total_audio_duration (float): Total audio duration in seconds.

    Returns:
        list[float]: Estimated durations per scene in seconds.
    """
    total_words = sum(len(scene.split()) for scene in scenes)
    durations = []

    for scene in scenes:
        word_count = len(scene.split())
        ratio = word_count / total_words
        durations.append(total_audio_duration * ratio)

    return durations


def split_audio_by_scenes(
    audio_path: str,
    scenes: list[str],
    output_dir: str = "output/audio_segments"
) -> list[str]:
    """
    Splits a narration audio file into segments for each scene.

    Args:
        audio_path (str): Path to the full narration audio file.
        scenes (list[str]): List of scene texts.
        output_dir (str): Directory to save audio segments.

    Returns:
        list[str]: Paths of generated audio segment files.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load the full audio
    audio = AudioSegment.from_file(audio_path)
    total_duration_ms = len(audio)  # total in ms
    total_duration_s = total_duration_ms / 1000.0

    # Estimate duration for each scene
    scene_durations = estimate_scene_durations(scenes, total_duration_s)

    segment_paths = []
    cursor = 0  # track start position in ms

    for idx, duration in enumerate(scene_durations, 1):
        end_time = cursor + (duration * 1000)
        segment = audio[cursor:end_time]

        seg_file = os.path.join(output_dir, f"scene_{idx}.mp3")
        segment.export(seg_file, format="mp3")
        segment_paths.append(seg_file)

        print(f"🎧 Scene {idx} audio segment saved ({duration:.2f}s): {seg_file}")
        cursor = end_time

    return segment_paths


# Optional: Standalone test
if __name__ == "__main__":
    dummy_scenes = [
        "Once upon a time in a quiet forest, a little fox gazed at the stars.",
        "She followed a bright star through the woods.",
        "Finally, she found a magical lake glowing under the night sky."
    ]
    test_audio_path = "D:\\Personal Learning\\YoutubeAgent\output\\audio\\full_story.mp3"  # must exist
    split_audio_by_scenes(test_audio_path, dummy_scenes)
