"""
Instructa-Gotchi Configuration and System Settings
Handles path discovery (eMMC vs microSD), networking, audio, and device parameters.
"""
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Discover persistent microSD or fallback to local directory
SD_CANDIDATE_PATHS = [
    Path("/media/sdcard/instructgotchi"),
    Path("/media/card/instructgotchi"),
    Path("/mnt/sdcard/instructgotchi"),
    BASE_DIR / "data"
]

def get_data_dir() -> Path:
    """Finds writable data directory, preferring external microSD card when mounted."""
    for path in SD_CANDIDATE_PATHS:
        try:
            if path.exists() and os.access(str(path), os.W_OK):
                return path
        except Exception:
            continue
    fallback = BASE_DIR / "data"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback

DATA_DIR = get_data_dir()
DB_PATH = DATA_DIR / "instructgotchi.db"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = BASE_DIR / "assets"

# Network settings
WEB_HOST = "0.0.0.0"
WEB_PORT = int(os.environ.get("INSTRUCTGOTCHI_PORT", 8088))

# UNIHIKER Display Settings
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
DISPLAY_FPS = 12

# Load design tokens
with open(BASE_DIR / "config" / "design_tokens.json", "r", encoding="utf-8") as f:
    TOKENS = json.load(f)

