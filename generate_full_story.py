# generate_full_story.py

import subprocess
import sys
from pathlib import Path
import time
import textwrap

# Ensure root directory (project base) is in sys.path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# ✅ Use shared logging utilities
from utils.log_utils import safe_print, log_step, log_success, log_error


# === Agent script paths ===
AGENTS_DIR = Path("agents")
SCRIPT_AGENT = AGENTS_DIR / "script_agent.py"
TTS_AGENT = AGENTS_DIR / "tts_agent.py"
IMAGE_AGENT = AGENTS_DIR / "image_agent.py"
VIDEO_AGENT = AGENTS_DIR / "video_agent.py"


def run_step(name: str, script_path: Path, extra_args=None):
    """Run each agent as a subprocess and exit if any step fails."""
    log_step(f"Running {name}")
    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd)
    if result.returncode != 0:
        log_error(f"{name} failed. Stopping pipeline.")
        sys.exit(1)

    log_success(f"{name} completed.")


def main():
    if len(sys.argv) < 2:
        safe_print(textwrap.dedent("""
        ❌ Missing story prompt.

        👉 Example usage:
           python generate_full_story.py "grandmother telling a story of Arjun and Karna fight"
        """))
        sys.exit(1)

    story_prompt = sys.argv[1]

    # Create unique folder
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    base_output_dir = Path(f"output/generated_videos/{timestamp}")
    base_output_dir.mkdir(parents=True, exist_ok=True)

    log_step(f"Base output folder created: {base_output_dir}")

    # Sequentially run the agents
    try:
        run_step("Script Agent", SCRIPT_AGENT, [story_prompt, str(base_output_dir)])
        run_step("TTS Agent", TTS_AGENT, [str(base_output_dir)])
        run_step("Image Agent", IMAGE_AGENT, [str(base_output_dir)])
        run_step("Video Agent", VIDEO_AGENT, [str(base_output_dir)])
    except KeyboardInterrupt:
        log_error("🛑 Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        sys.exit(1)

    safe_print("\n✨ ✅ Full pipeline completed successfully.")
    log_success(f"Final video saved at: {base_output_dir}/video/final_story.mp4")


if __name__ == "__main__":
    main()
