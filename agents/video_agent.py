# agents/video_agent.py
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
    
from utils.log_utils import safe_print, log_step, log_success, log_error, log_warn
import PIL.Image
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import moviepy.editor as mpy

def create_multiscene_video(image_paths, audio_paths, output_path, bg_music_path=None,
                            bg_music_volume=0.15, fade_duration=1.0, fps=24, height=720):
    if not image_paths or not audio_paths:
        raise ValueError("No image or audio files provided.")

    # align lengths: choose min to ensure no index error
    n = min(len(image_paths), len(audio_paths))
    if len(image_paths) != len(audio_paths):
        log_warn(f"Image/audio count mismatch. Trimming to {n} scenes.")

    scene_clips = []
    for idx in range(n):
        img = image_paths[idx]
        aud = audio_paths[idx]
        audio_clip = mpy.AudioFileClip(aud)
        img_clip = mpy.ImageClip(img).set_duration(audio_clip.duration).resize(height=height)
        clip = img_clip.set_audio(audio_clip)
        if idx > 0:
            clip = clip.fadein(fade_duration)
        if idx < n - 1:
            clip = clip.fadeout(fade_duration)
        scene_clips.append(clip)
        safe_print(f"Added scene {idx+1}: {img} + {aud} ({audio_clip.duration:.2f}s)")

    final_clip = mpy.concatenate_videoclips(scene_clips, method="compose")

    # optional background music
    if bg_music_path and os.path.exists(bg_music_path):
        try:
            bg = mpy.AudioFileClip(bg_music_path).volumex(bg_music_volume).set_duration(final_clip.duration)
            final_clip = final_clip.set_audio(mpy.CompositeAudioClip([final_clip.audio, bg]))
            safe_print(f"Background music added: {bg_music_path}")
        except Exception as e:
            log_warn(f"Could not add background music: {e}")

    # ensure output dir
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    final_clip.write_videofile(
        output_path, fps=fps, codec="libx264", audio_codec="aac",
        threads=4, preset="medium", temp_audiofile=str(Path(output_path).with_name("_temp_audio.m4a")),
        remove_temp=True
    )
    log_success(f"Final video created: {output_path}")
    return output_path


def get_scene_files(base_output_dir: Path):
    image_dir = base_output_dir / "images"
    audio_dir = base_output_dir / "audio_segments"
    if not image_dir.exists() or not audio_dir.exists():
        raise FileNotFoundError("Missing images or audio_segments directory.")

    # scene_1.jpg, scene_2.jpg ... ; scene_1.mp3 ...
    image_files = sorted(image_dir.glob("scene_*.jpg"), key=lambda p: int(p.stem.split("_")[-1]))
    audio_files = sorted(audio_dir.glob("scene_*.mp3"), key=lambda p: int(p.stem.split("_")[-1]))
    return [str(p) for p in image_files], [str(p) for p in audio_files]


def process_video_creation(base_output_dir: Path):
    log_step("Video creation step")
    image_paths, audio_paths = get_scene_files(base_output_dir)
    output_video = base_output_dir / "video" / "final_story.mp4"
    create_multiscene_video(image_paths, audio_paths, str(output_video),
                            bg_music_path="assets/bg_music.mp3", bg_music_volume=0.18,
                            fade_duration=1.0, fps=24, height=720)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agents/video_agent.py <base_output_dir>")
        sys.exit(1)
    base_output_dir = Path(sys.argv[1])
    process_video_creation(base_output_dir)
