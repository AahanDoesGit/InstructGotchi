"""
Instructa-Gotchi SQLite Storage Layer
Single source of truth for UNIHIKER device and phone companion app.
Uses Write-Ahead Logging (WAL) and mutex locking for safe concurrent access.
"""
import sqlite3
import threading
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from config.settings import DB_PATH

_db_lock = threading.Lock()

def get_connection():
    """Returns a SQLite connection with row factory and WAL mode enabled."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    """Initializes tables and inserts default initial pet state if not present."""
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Pet State Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pet (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT NOT NULL DEFAULT 'Instructa-Gotchi',
            level INTEGER NOT NULL DEFAULT 1,
            xp INTEGER NOT NULL DEFAULT 0,
            xp_next INTEGER NOT NULL DEFAULT 100,
            hunger INTEGER NOT NULL DEFAULT 85,
            happiness INTEGER NOT NULL DEFAULT 90,
            energy INTEGER NOT NULL DEFAULT 80,
            cleanliness INTEGER NOT NULL DEFAULT 95,
            health INTEGER NOT NULL DEFAULT 100,
            mood TEXT NOT NULL DEFAULT 'happy',
            mode TEXT NOT NULL DEFAULT 'auto',
            activity TEXT NOT NULL DEFAULT 'observing',
            speech TEXT NOT NULL DEFAULT 'Hello! Ready to build?',
            equipped_hat TEXT,
            equipped_skin TEXT DEFAULT 'maker_yellow',
            last_updated REAL NOT NULL
        );
        """)

        # 2. Activity History Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            activity_type TEXT NOT NULL,
            mode TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            xp_gained INTEGER DEFAULT 0
        );
        """)

        # 3. Missions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS missions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            target INTEGER NOT NULL DEFAULT 1,
            progress INTEGER NOT NULL DEFAULT 0,
            completed INTEGER NOT NULL DEFAULT 0,
            xp_reward INTEGER NOT NULL DEFAULT 50,
            reward_item TEXT
        );
        """)

        # 4. Inventory Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            icon TEXT NOT NULL,
            unlocked INTEGER NOT NULL DEFAULT 0,
            is_equipped INTEGER NOT NULL DEFAULT 0
        );
        """)

        # 5. Achievements Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            badge_icon TEXT NOT NULL,
            unlocked_at REAL
        );
        """)

        # 6. Settings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)

        # 7. Paired Devices Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paired_devices (
            device_token TEXT PRIMARY KEY,
            device_name TEXT,
            last_seen REAL NOT NULL
        );
        """)

        # 8. Maker Parts Inventory Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS maker_parts (
            part_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            icon TEXT NOT NULL,
            description TEXT
        );
        """)

        # Upgrade pet table schema if missing robot columns
        cursor.execute("PRAGMA table_info(pet);")
        pet_cols = [row["name"] for row in cursor.fetchall()]
        if "charging" not in pet_cols:
            cursor.execute("ALTER TABLE pet ADD COLUMN charging INTEGER DEFAULT 0;")
        if "temperature" not in pet_cols:
            cursor.execute("ALTER TABLE pet ADD COLUMN temperature REAL DEFAULT 36.5;")
        if "fan_active" not in pet_cols:
            cursor.execute("ALTER TABLE pet ADD COLUMN fan_active INTEGER DEFAULT 0;")
        if "voltage" not in pet_cols:
            cursor.execute("ALTER TABLE pet ADD COLUMN voltage REAL DEFAULT 4.10;")
        if "firmware_version" not in pet_cols:
            cursor.execute("ALTER TABLE pet ADD COLUMN firmware_version TEXT DEFAULT 'v1.0.4';")

        # Insert initial row in pet table if empty
        cursor.execute("SELECT COUNT(*) as count FROM pet;")
        if cursor.fetchone()["count"] == 0:
            cursor.execute("""
            INSERT INTO pet (id, name, last_updated)
            VALUES (1, 'Instructa-Gotchi', ?);
            """, (time.time(),))

        # Insert default missions
        default_missions = [
            ("m_workshop_1", "Workshop Apprentice", "Complete 3 workshop activities", "daily", 3, 0, 0, 50, "goggles"),
            ("m_care_1", "Maker Maintenance", "Feed and clean your maker robot", "daily", 2, 0, 0, 30, None),
            ("m_focus_1", "Deep Focus", "Complete one 10-minute Focus session", "daily", 1, 0, 0, 40, "focus_badge"),
            ("m_music_1", "Jam Session", "Listen to a song in Music mode", "daily", 1, 0, 0, 25, "headphones")
        ]
        for m in default_missions:
            cursor.execute("""
            INSERT OR IGNORE INTO missions (id, title, description, category, target, progress, completed, xp_reward, reward_item)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, m)

        # Insert default inventory accessories
        default_items = [
            ("skin_maker_yellow", "Classic Maker Yellow", "skin", "master_character", 1, 1),
            ("skin_signal_orange", "Signal Orange Edition", "skin", "master_character", 0, 0),
            ("goggles", "Maker Safety Goggles", "hat", "goggles", 0, 0),
            ("headphones", "Studio Audio Cans", "hat", "mode_music", 0, 0),
            ("toolbelt_deluxe", "Titanium Toolbelt", "accessory", "mode_workshop", 0, 0)
        ]
        for itm in default_items:
            cursor.execute("""
            INSERT OR IGNORE INTO inventory (item_id, name, category, icon, unlocked, is_equipped)
            VALUES (?, ?, ?, ?, ?, ?);
            """, itm)

        # Insert default achievements
        default_achievements = [
            ("first_spark", "First Spark", "Booted up Instructa-Gotchi for the very first time", "mode_auto", time.time()),
            ("tinker_master", "Tinker Master", "Complete 10 workshop activities", "mode_workshop", None),
            ("audio_pilot", "Audio Pilot", "Spend 30 minutes in Music mode", "mode_music", None),
            ("level_five", "Master Builder", "Reach Level 5", "mode_game", None)
        ]
        for ach in default_achievements:
            cursor.execute("""
            INSERT OR IGNORE INTO achievements (id, title, description, badge_icon, unlocked_at)
            VALUES (?, ?, ?, ?, ?);
            """, ach)

        # Insert default maker parts
        default_parts = [
            ("resistor", "10kΩ Resistors", 8, "⚡", "Standard current limiting resistors"),
            ("led", "RGB Micro LEDs", 6, "💡", "High-efficiency breadboard LEDs"),
            ("gear", "Brass Servo Gears", 5, "⚙️", "Precision tooth mechanical gears"),
            ("solder_wire", "Rosin Solder Wire", 12, "🧵", "60/40 lead-free rosin core wire"),
            ("timer_555", "555 Timer IC", 3, "🔲", "Classic precision timer microchip"),
            ("copper_coil", "Induction Coils", 4, "🌀", "Copper electromagnetic coil")
        ]
        for part in default_parts:
            cursor.execute("""
            INSERT OR IGNORE INTO maker_parts (part_id, name, count, icon, description)
            VALUES (?, ?, ?, ?, ?);
            """, part)

        conn.commit()
        conn.close()

def get_pet_state() -> Dict[str, Any]:
    """Fetches the latest pet state row as a dictionary."""
    with _db_lock:
        conn = get_connection()
        row = conn.execute("SELECT * FROM pet WHERE id = 1;").fetchone()
        conn.close()
        return dict(row) if row else {}

PET_COLUMNS = {
    "id", "name", "level", "xp", "xp_next", "hunger", "happiness", "energy",
    "cleanliness", "health", "mood", "mode", "activity", "speech",
    "equipped_hat", "equipped_skin", "last_updated",
    "charging", "temperature", "fan_active", "voltage", "firmware_version"
}

def update_pet_state(updates: Dict[str, Any]):
    """Safely updates specified fields in pet state, filtering out transient runtime attributes."""
    valid_updates = {k: v for k, v in updates.items() if k in PET_COLUMNS and k != "id"}
    valid_updates["last_updated"] = time.time()
    fields = [f"{k} = ?" for k in valid_updates.keys()]
    values = list(valid_updates.values())
    query = f"UPDATE pet SET {', '.join(fields)} WHERE id = 1;"

    with _db_lock:
        conn = get_connection()
        conn.execute(query, values)
        conn.commit()
        conn.close()

def log_activity(activity_type: str, mode: str, title: str, description: str = "", xp_gained: int = 0):
    """Logs an event into activity_history."""
    with _db_lock:
        conn = get_connection()
        conn.execute("""
        INSERT INTO activity_history (timestamp, activity_type, mode, title, description, xp_gained)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (time.time(), activity_type, mode, title, description, xp_gained))
        conn.commit()
        conn.close()

def get_activity_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves recent activities."""
    with _db_lock:
        conn = get_connection()
        rows = conn.execute("""
        SELECT * FROM activity_history ORDER BY timestamp DESC LIMIT ?;
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

def get_missions() -> List[Dict[str, Any]]:
    with _db_lock:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM missions ORDER BY completed ASC, id ASC;").fetchall()
        conn.close()
        return [dict(r) for r in rows]

def get_inventory() -> List[Dict[str, Any]]:
    with _db_lock:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM inventory;").fetchall()
        conn.close()
        return [dict(r) for r in rows]

def get_achievements() -> List[Dict[str, Any]]:
    with _db_lock:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM achievements;").fetchall()
        conn.close()
        return [dict(r) for r in rows]

def get_maker_parts() -> List[Dict[str, Any]]:
    """Retrieves all craftable maker parts and their inventory counts."""
    with _db_lock:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM maker_parts ORDER BY count DESC;").fetchall()
        conn.close()
        return [dict(r) for r in rows]

def add_maker_part(part_id: str, count: int = 1):
    """Increments a maker part count."""
    with _db_lock:
        conn = get_connection()
        conn.execute("UPDATE maker_parts SET count = count + ? WHERE part_id = ?;", (count, part_id))
        conn.commit()
        conn.close()

def consume_maker_parts(requirements: Dict[str, int]) -> bool:
    """Checks and deducts parts if all requirements are met."""
    with _db_lock:
        conn = get_connection()
        # Verify all available
        for pid, req in requirements.items():
            row = conn.execute("SELECT count FROM maker_parts WHERE part_id = ?;", (pid,)).fetchone()
            if not row or row["count"] < req:
                conn.close()
                return False
        # Deduct
        for pid, req in requirements.items():
            conn.execute("UPDATE maker_parts SET count = count - ? WHERE part_id = ?;", (req, pid))
        conn.commit()
        conn.close()
        return True

# Initialize schema on module load
init_db()

