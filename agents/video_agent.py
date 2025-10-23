"""
Final video rendering agent:
- Adds smooth fade transitions between scenes (video only)
- Keeps narration audio clean and sequential
- Supports background music
"""

import os
import sys
from pathlib import Path

# 👇 Pillow >= 10 fix for ANTIALIAS
import PIL.Image
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import moviepy.editor as mpy


def create_multiscene_video(
    image_paths: list,
    audio_paths: list,
    output_path: Path,
    bg_music_path: str = "assets/bg_music.mp3",
    bg_music_volume: float = 0.15,
    fade_duration: float = 1.0,  # seconds for smooth visual transition
    fps: int = 24,
    height: int = 720
) -> Path:
    """
    Combines scene images and audio segments into one final video with smooth transitions.
    """
    if len(image_paths) != len(audio_paths):
        raise ValueError("❌ Number of images and audio segments must match.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene_clips = []

    for idx, (img, aud) in enumerate(zip(image_paths, audio_paths), 1):
        audio_clip = mpy.AudioFileClip(str(aud))
        img_clip = mpy.ImageClip(str(img)).set_duration(audio_clip.duration).resize(height=height)
        clip = img_clip.set_audio(audio_clip)

        # ✅ Visual fade only — no audio overlap
        if idx > 1:
            clip = clip.fadein(fade_duration)
        if idx < len(audio_paths):
            clip = clip.fadeout(fade_duration)

        scene_clips.append(clip)
        print(f"🎬 Added scene {idx}: {img} + {aud} ({audio_clip.duration:.2f}s)")

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

    temp_audiofile = output_path.parent / "_temp_audio.m4a"

    final_clip.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        temp_audiofile=str(temp_audiofile),
        remove_temp=True
    )

    print(f"✅ Final video created with smooth visual transitions (no audio overlap): {output_path}")
    return output_path


def process_video_creation(base_output_dir: Path):
    """
    Reads images and audio_segments from the given base output directory,
    then generates the final video file.
    """
    image_dir = base_output_dir / "images"
    audio_dir = base_output_dir / "audio_segments"
    output_video_path = base_output_dir / "final_story.mp4"

    image_paths = sorted(image_dir.glob("scene_*.jpg"))
    audio_paths = sorted(audio_dir.glob("scene_*.mp3"))

    if not image_paths or not audio_paths:
        print("❌ No images or audio segments found. Make sure previous steps were run.")
        return

    create_multiscene_video(
        image_paths=image_paths,
        audio_paths=audio_paths,
        output_path=output_video_path,
        bg_music_path="assets/bg_music.mp3",
        bg_music_volume=0.18,
        fade_duration=1.0
    )


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        base_output_dir = Path(sys.argv[1])
    else:
        # fallback for manual testing
        base_output_dir = Path("output/manual_test")
        base_output_dir.mkdir(parents=True, exist_ok=True)

    process_video_creation(base_output_dir)
    print("✅ Final video rendering completed.")