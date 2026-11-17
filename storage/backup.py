"""
Instructa-Gotchi Backup & Integrity Management
Creates atomic SQLite backups, performs integrity checks, manages retention cycles,
and exports/imports backup ZIP archives.
"""
import os
import shutil
import sqlite3
import hashlib
import zipfile
import time
from typing import Optional, List, Dict, Any
from pathlib import Path
from config.settings import DB_PATH, BACKUP_DIR, DATA_DIR

def calculate_checksum(file_path: Path) -> str:
    """Computes SHA-256 checksum of a file."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()

def verify_database_integrity(db_file: Path) -> bool:
    """Runs PRAGMA integrity_check on SQLite database."""
    try:
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        res = cursor.fetchone()
        conn.close()
        return res is not None and res[0] == "ok"
    except Exception as e:
        print(f"Integrity check failed: {e}")
        return False

def create_backup(tag: str = "auto") -> Optional[Path]:
    """
    Creates an atomic backup using SQLite online backup API.
    Verifies integrity before rotating old copies.
    """
    if not DB_PATH.exists():
        return None

    timestamp = int(time.time())
    temp_target = BACKUP_DIR / f"temp_backup_{timestamp}.db"
    final_target = BACKUP_DIR / f"instructgotchi_{tag}_{timestamp}.db"

    try:
        # Online SQLite backup
        src_conn = sqlite3.connect(str(DB_PATH))
        dst_conn = sqlite3.connect(str(temp_target))
        with dst_conn:
            src_conn.backup(dst_conn, pages=100)
        dst_conn.close()
        src_conn.close()

        # Check integrity
        if not verify_database_integrity(temp_target):
            if temp_target.exists():
                temp_target.unlink()
            raise RuntimeError("Database backup failed SQLite integrity check.")

        # Atomic rename
        temp_target.rename(final_target)

        # Cleanup old backups (keep 10 most recent)
        rotate_backups(max_keep=10)
        return final_target

    except Exception as e:
        print(f"Failed to create backup: {e}")
        if temp_target.exists():
            temp_target.unlink()
        return None

def rotate_backups(max_keep: int = 10):
    """Enforces backup retention limit."""
    backups = sorted(BACKUP_DIR.glob("instructgotchi_*.db"), key=os.path.getmtime)
    if len(backups) > max_keep:
        for old_b in backups[:-max_keep]:
            try:
                old_b.unlink()
            except Exception:
                pass

def export_zip(output_path: Path) -> Path:
    """Packages the database and settings manifest into an exportable ZIP file."""
    # Ensure fresh backup
    backup_file = create_backup("export")
    if not backup_file:
        raise RuntimeError("Could not create snapshot for export.")

    checksum = calculate_checksum(backup_file)
    manifest = {
        "project": "Instructa-Gotchi",
        "exported_at": time.time(),
        "checksum": checksum,
        "db_filename": backup_file.name
    }

    manifest_path = BACKUP_DIR / "manifest.json"
    import json
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(backup_file, arcname="instructgotchi.db")
        z.write(manifest_path, arcname="manifest.json")

    if manifest_path.exists():
        manifest_path.unlink()

    return output_path
