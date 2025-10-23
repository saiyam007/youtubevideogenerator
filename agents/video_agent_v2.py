import os
from pathlib import Path
import PIL.Image
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import moviepy.editor as mpy


def add_subtitle(clip: mpy.VideoClip, text: str, fontsize: int = 40) -> mpy.VideoClip:
    """
    Creates a subtitle overlay using TextClip with Pillow (no ImageMagick needed).
    """
    if not text.strip():
        return clip

    txt_clip = mpy.TextClip(
        text,
        fontsize=fontsize,
        color='white',
        stroke_color='black',
        stroke_width=2,
        size=(clip.w * 0.9, None),
        method="caption",  # ✅ avoids ImageMagick
    ).set_position(('center', 'bottom')).set_duration(clip.duration)

    return mpy.CompositeVideoClip([clip, txt_clip])


def create_multiscene_video(
    image_paths: list,
    audio_paths: list,
    subtitles: list = None,
    output_path: str = "output/video/final_story.mp4",
    bg_music_path: str = "assets/bg_music.mp3",
    bg_music_volume: float = 0.15,
    fade_duration: float = 1.0,
    fps: int = 24,
    height: int = 720
) -> str:
    if len(image_paths) != len(audio_paths):
        raise ValueError("❌ Number of images and audio segments must match.")
    if subtitles and len(subtitles) != len(image_paths):
        raise ValueError("❌ Number of subtitles must match scenes.")

    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    scene_clips = []

    for idx, (img, aud) in enumerate(zip(image_paths, audio_paths), 1):
        audio_clip = mpy.AudioFileClip(aud)
        img_clip = mpy.ImageClip(img).set_duration(audio_clip.duration).resize(height=height)
        clip = img_clip.set_audio(audio_clip)

        # ✅ Fade in/out video only
        if idx > 1:
            clip = clip.fadein(fade_duration)
        if idx < len(audio_paths):
            clip = clip.fadeout(fade_duration)

        # 📝 Add subtitle if available
        if subtitles:
            clip = add_subtitle(clip, subtitles[idx - 1])

        scene_clips.append(clip)
        print(f"🎬 Added scene {idx} with subtitle: {subtitles[idx - 1] if subtitles else '—'}")

    final_clip = mpy.concatenate_videoclips(scene_clips, method="compose")

    if bg_music_path and os.path.exists(bg_music_path):
        try:
            bg_music = mpy.AudioFileClip(bg_music_path).volumex(bg_music_volume)
            bg_music = bg_music.set_duration(final_clip.duration)
            combined_audio = mpy.CompositeAudioClip([final_clip.audio, bg_music])
            final_clip = final_clip.set_audio(combined_audio)
            print(f"🎼 Background music added: {bg_music_path}")
        except Exception as e:
            print(f"⚠️ Could not add background music: {e}")

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

    print(f"✅ Final video with subtitles created: {output_path}")
    return output_path


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
    test_subtitles = [
        "Once upon a time, in a magical forest...",
        "A curious fox began a brave adventure.",
        "And from that day, everything changed."
    ]

    create_multiscene_video(
        image_paths=test_images,
        audio_paths=test_audio,
        subtitles=test_subtitles,
        fade_duration=1.0,
        bg_music_path="assets/bg_music.mp3",
        bg_music_volume=0.18
    )
