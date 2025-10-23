import os
from pathlib import Path

# --- Define folder structure ---
FOLDERS = [
    "agents",
    "utils",
    "assets",
    "output/audio",
    "output/audio_segments",
    "output/images",
    "output/video"
]

# --- Define base files with default content ---
FILES = {
    ".env.example": "EURON_API_KEY=your_euron_api_key_here\n",
    "requirements.txt": """requests
python-dotenv
moviepy
pydub
google-api-python-client
google-auth
google-auth-oauthlib
""",
    ".gitignore": """__pycache__/
.env
output/
*.mp4
*.mp3
*.jpg
*.png
client_secret.json
""",
    "main.py": '''"""
Main entrypoint for YouTube AI Agent.
This orchestrates: Script -> Audio -> Image -> Video -> Upload
"""
print("✅ YouTube Agent Project Initialized. Add logic to main.py next!")''',
}

# --- Define modular agent files (initial boilerplate) ---
AGENT_FILES = {
    "agents/script_agent.py": '"""Generates storytelling script using Euron API."""\n',
    "agents/tts_agent.py": '"""Converts text to speech using PlayAI TTS."""\n',
    "agents/image_agent.py": '"""Generates scene images using FLUX Schnell."""\n',
    "agents/audio_split_agent.py": '"""Splits full audio narration into smaller scene audio clips."""\n',
    "agents/video_agent.py": '"""Creates final multi-scene video using MoviePy."""\n',
    "agents/youtube_agent.py": '"""Handles YouTube upload using YouTube Data API."""\n',
}

# --- Define utils files ---
UTIL_FILES = {
    "utils/text_splitter.py": '"""Splits story text into meaningful scenes for video rendering."""\n',
    "utils/file_utils.py": '"""Helper utilities for file management and duration estimation."""\n',
}

def create_folders(base_path="."):
    for folder in FOLDERS:
        path = Path(base_path) / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created folder: {path}")

def create_files(base_path="."):
    # Base files like .env.example, main.py, etc.
    for filename, content in FILES.items():
        file_path = Path(base_path) / filename
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            print(f"📝 Created file: {file_path}")
        else:
            print(f"⚙️ Skipped (exists): {file_path}")

    # Agent files
    for filename, content in {**AGENT_FILES, **UTIL_FILES}.items():
        file_path = Path(base_path) / filename
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            print(f"🧩 Created file: {file_path}")
        else:
            print(f"⚙️ Skipped (exists): {file_path}")

def main():
    print("🚀 Setting up YouTube Agent folder structure...\n")
    create_folders()
    create_files()
    print("\n✅ Project structure created successfully!")
    print("👉 Next: Add your logic step-by-step into each agent file.")

if __name__ == "__main__":
    main()
