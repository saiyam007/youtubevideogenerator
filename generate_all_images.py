from agents.image_agent import generate_scene_image
from utils.text_splitter import split_script_into_scenes
from agents.script_agent import generate_script

# 1. Generate story (or you can hardcode your own text)
story_text = generate_script("The Little Fox and the Star")

# 2. Split into scenes
scenes = split_script_into_scenes(story_text, max_chars=220)

# 3. Generate one image per scene
image_paths = []
for idx, scene in enumerate(scenes, start=1):
    img_path = generate_scene_image(scene_text=scene, scene_index=idx)
    image_paths.append(img_path)

print("\n✅ Image generation complete!")
for path in image_paths:
    print(f"🖼 {path}")
