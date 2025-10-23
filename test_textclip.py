"""
Video rendering agent (stable version, no subtitles):
✅ Multi-scene support
🌊 Smooth fade transitions between scenes
🎼 Optional background music
📽️ Exports YouTube-ready MP4
"""

import os
from pathlib import Path
import PIL.Image

# 🛡 Pillow fix for older MoviePy versions
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import moviepy.editor as mpy


def create_multiscene_video(
    image_paths: list,
    audio_paths: list,
    output_path: str = "output/video/final_story.mp4",
    bg_music_path: str = "assets/bg_music.mp3",
    bg_music_volume: float = 0.15,
    fade_duration: float = 1.0,
    fps: int = 24,
    height: int = 720
) -> str:
    """
    Create final video with:
    - image clips
    - audio narration
    - smooth fade transitions
    - optional background music
    """

    # ✅ Validation
    if not (len(image_paths) == len(audio_paths)):
        raise ValueError("❌ image_paths and audio_paths lengths must match.")

    # Ensure output directory exists
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)

    scene_clips = []

    for idx, (img_path, aud_path) in enumerate(zip(image_paths, audio_paths), 1):
        # 🖼 Load image & audio
        audio_clip = mpy.AudioFileClip(aud_path)
        img_clip = mpy.ImageClip(img_path).set_duration(audio_clip.duration).resize(height=height)

        # 🪄 Combine image + audio
        composite_clip = img_clip.set_audio(audio_clip)

        # 🌊 Smooth fade transitions (only visual)
        if idx > 1:
            composite_clip = composite_clip.fadein(fade_duration)
        if idx < len(audio_paths):
            composite_clip = composite_clip.fadeout(fade_duration)

        scene_clips.append(composite_clip)
        print(f"🎬 Scene {idx} added — duration: {audio_clip.duration:.2f}s")

    # 📽️ Concatenate scenes
    final_clip = mpy.concatenate_videoclips(scene_clips, method="compose")

    # 🎼 Optional background music
    if bg_music_path and os.path.exists(bg_music_path):
        try:
            bg_music = mpy.AudioFileClip(bg_music_path).volumex(bg_music_volume)
            bg_music = bg_music.set_duration(final_clip.duration)
            combined_audio = mpy.CompositeAudioClip([final_clip.audio, bg_music])
            final_clip = final_clip.set_audio(combined_audio)
            print(f"🎼 Background music added: {bg_music_path}")
        except Exception as e:
            print(f"⚠️ Could not add background music: {e}")

    # 🧾 Export final video
    final_clip.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        temp_audiofile="output/video/_temp_audio.m4a",
        remove_temp=True
    )

    print(f"✅ Final video created (no subtitles): {output_path}")
    return output_path


# 🧪 Standalone Test Example
if __name__ == "__main__":
    test_images = [
        "output/images/scene_1.jpg",
        "output/images/scene_2.jpg",
        "output/images/scene_3.jpg",
    ]
    test_audio = [
        "output/audio_segments/scene_1.mp3",
        "output/audio_segments/scene_2.mp3",
        "output/audio_segments/scene_3.mp3",
    ]

    create_multiscene_video(
        image_paths=test_images,
        audio_paths=test_audio,
        bg_music_path="assets/bg_music.mp3",
        bg_music_volume=0.18,
        fade_duration=1.0
    )
