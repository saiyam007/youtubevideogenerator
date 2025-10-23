import subprocess
import sys
from pathlib import Path
import time
import textwrap

# Agent script paths
AGENTS_DIR = Path("agents")
SCRIPT_AGENT = AGENTS_DIR / "script_agent.py"
TTS_AGENT = AGENTS_DIR / "tts_agent.py"
IMAGE_AGENT = AGENTS_DIR / "image_agent.py"
VIDEO_AGENT = AGENTS_DIR / "video_agent.py"

def run_step(name: str, script_path: Path, extra_args=None):
    """
    Runs each agent as a subprocess and exits if any step fails.
    """
    print(f"\n🚀 Running {name} ...")
    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ {name} failed. Stopping pipeline.")
        sys.exit(1)

    print(f"✅ {name} completed.\n")


def main():
    if len(sys.argv) < 2:
        print(textwrap.dedent("""
        ❌ Missing story prompt.

        👉 Example usage:
           python generate_full_story.py "grandmother telling a story of Arjun and Karna fight"
        """))
        sys.exit(1)

    story_prompt = sys.argv[1]

    # ⏳ Create unique base folder
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    base_output_dir = Path(f"output/generated_videos/{timestamp}")
    base_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📁 Base output folder created: {base_output_dir}")

    # ✅ Run pipeline steps in order
    try:
        run_step("Script Agent", SCRIPT_AGENT, [story_prompt, str(base_output_dir)])
        run_step("TTS Agent", TTS_AGENT, [str(base_output_dir)])
        run_step("Image Agent", IMAGE_AGENT, [str(base_output_dir)])
        run_step("Video Agent", VIDEO_AGENT, [str(base_output_dir)])
    except KeyboardInterrupt:
        print("🛑 Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

    print("\n✨ ✅ Full pipeline completed successfully.")
    print(f"📽️ Final video saved at: {base_output_dir}/final_story.mp4")


if __name__ == "__main__":
    main()
