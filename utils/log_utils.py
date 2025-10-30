# utils/log_utils.py
"""
Cross-platform safe logging utilities.
Prevents UnicodeEncodeError (emojis) on Windows and provides simple helpers.
"""

import sys
import datetime

def safe_print(*args, sep=" ", end="\n", file=sys.stdout, flush=True):
    """Print safely — if UnicodeEncodeError occurs, strip non-ascii chars."""
    try:
        print(*args, sep=sep, end=end, file=file, flush=flush)
    except UnicodeEncodeError:
        try:
            text = sep.join(str(a) for a in args)
            text_clean = text.encode("ascii", "ignore").decode("ascii", "ignore")
            print(text_clean, end=end, file=file, flush=flush)
        except Exception:
            print("[LOG_ERROR] (could not print line safely)", file=file, flush=flush)


def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_step(step_name: str, emoji: str = "🚀"):
    ts = timestamp()
    try:
        print(f"{emoji} [{ts}] {step_name}")
    except UnicodeEncodeError:
        print(f"[{ts}] {step_name}")


def log_success(msg: str):
    ts = timestamp()
    safe_print(f"✅ [{ts}] {msg}")


def log_error(msg: str):
    ts = timestamp()
    safe_print(f"❌ [{ts}] {msg}")


def log_warn(msg: str):
    ts = timestamp()
    safe_print(f"⚠️ [{ts}] {msg}")
