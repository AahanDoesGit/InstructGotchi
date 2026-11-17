"""
Instructa-Gotchi Device Screens (UNIHIKER M10 240x320 Portrait)
Engineered to precisely match the Stitch Design System:
- Graphite chassis background (#242522)
- Speech bubble card in Warm Ivory (#FFF9EF)
- Center 3D mascot avatar with active project progress bar
- 4-stat telemetry grid (⚡ Energy, 💚 Happy, 💧 Clean, 🍗 Hunger)
- Complete touch targets for all 10 device screens.
"""
from pathlib import Path
from typing import Dict, Any, Callable
from config.settings import DISPLAY_WIDTH, DISPLAY_HEIGHT, ASSETS_DIR, WEB_PORT

class ScreenManager:
    def __init__(self, renderer, pet_manager, anim_controller):
        self.renderer = renderer
        self.pet_manager = pet_manager
        self.anim = anim_controller

    def render_boot_screen(self):
        """1. Boot Screen (Stitch style)."""
        self.renderer.clear(color=(36, 37, 34))
        # 3D mascot center
        char_path = ASSETS_DIR / "characters" / "master_character.png"
        self.renderer.draw_image(50, 60, char_path, 140, 140)

        # Title & version
        self.renderer.draw_text(38, 215, "INSTRUCTA-GOTCHI", size=14, color="#FFC928")
        self.renderer.draw_text(60, 240, "TINKO M10 Edition", size=11, color="#F28B24")
        self.renderer.draw_text(75, 270, "Starting system...", size=10, color="#38BDF8")

    def render_home_screen(self, state: Dict[str, Any]):
        """2. Home Screen (Exact Stitch 240x320 layout)."""
        # Outer screen background in graphite
        self.renderer.clear(color=(36, 37, 34))

        # Speech bubble
        speech = state.get("speech", "Ready to build together?")
        self.renderer.draw_rect(10, 28, 220, 32, fill="#FFF9EF", radius=8)
        self.renderer.draw_text(18, 36, speech[:34], size=10, color="#242522")

        # Center Avatar Box (100x100)
        self.renderer.draw_rect(65, 66, 110, 110, fill="#3A2C18", radius=12)
        # Mascot image
        char_frame = self.anim.get_current_frame_path(state.get("mood", "idle"))
        self.renderer.draw_image(70, 70, char_frame, 100, 100)
        # Touch to play
        self.renderer.register_touch_target(65, 66, 110, 110, lambda: self.pet_manager.perform_care("play"))

        # Activity Subtitle & Project Progress
        activity = state.get("activity", "soldering_circuit").replace("_", " ").title()
        self.renderer.draw_rect(65, 156, 110, 18, fill="#1C1D1F", radius=4)
        self.renderer.draw_text(72, 160, activity[:18], size=8, color="#FFC928")

        # Project Progress Bar
        self.renderer.draw_text(12, 182, "Repairing gadget", size=9, color="#FFF9EF")
        self.renderer.draw_text(198, 182, "72%", size=9, color="#F28B24")
        self.renderer.draw_rect(10, 196, 220, 8, fill="#1C1D1F", radius=4)
        self.renderer.draw_rect(10, 196, 158, 8, fill="#F28B24", radius=4)

        # 4-Stat Telemetry Grid
        stats = [
            ("⚡", f"{state.get('energy', 80)}%", "Energy", "#38BDF8"),
            ("💚", f"{state.get('happiness', 90)}%", "Happy", "#83A978"),
            ("💧", f"{state.get('cleanliness', 95)}%", "Clean", "#38BDF8"),
            ("🍗", f"{state.get('hunger', 85)}%", "Battery", "#F28B24")
        ]
        gx = 10
        for icon, val_str, label, col in stats:
            self.renderer.draw_rect(gx, 212, 52, 48, fill="#1C1D1F", radius=6)
            self.renderer.draw_text(gx + 6, 218, f"{icon} {val_str}", size=9, color=col)
            self.renderer.draw_text(gx + 8, 238, label, size=8, color="#879099")
            gx += 56

    def render_care_screen(self, state: Dict[str, Any]):
        """3. Care Screen (Stitch actions: Recharge, Tune-up, Minigame, Sleep)."""
        self.renderer.clear(color=(36, 37, 34))
        self.renderer.draw_text(16, 32, "MAKER CARE ACTIONS", size=13, color="#FFC928")

        # 4 Large Care Action Cards
        actions = [
            ("🔋 Recharge", "feed", 14, 60, "#F28B24", "+30 Battery Power"),
            ("🔧 Tune-up", "clean", 124, 60, "#83A978", "Clean & Polish Gears"),
            ("🎮 Minigame", "play", 14, 150, "#FFC928", "Play Maker Game"),
            ("💤 Sleep", "rest", 124, 150, "#38BDF8", "Low Power Sleep")
        ]
        for title, act, ax, ay, col, desc in actions:
            self.renderer.draw_rect(ax, ay, 102, 78, fill="#1C1D1F", radius=8)
            self.renderer.draw_rect(ax, ay, 102, 4, fill=col, radius=2)
            self.renderer.draw_text(ax + 8, ay + 16, title, size=11, color="#FFFFFF")
            self.renderer.draw_text(ax + 8, ay + 42, desc[:16], size=8, color="#879099")
            self.renderer.register_touch_target(ax, ay, 102, 78, lambda a=act: self.pet_manager.perform_care(a))

        # Health Diagnostic
        health = state.get("health", 100)
        self.renderer.draw_rect(14, 240, 212, 34, fill="#1C1D1F", radius=6)
        self.renderer.draw_text(24, 250, f"Diagnostics: System Health {health}%", size=10, color="#83A978")

    def render_workshop_screen(self, state: Dict[str, Any]):
        """4. Workshop Screen."""
        self.renderer.clear(color=(36, 37, 34))
        self.renderer.draw_text(16, 32, "TINKO WORKSHOP", size=13, color="#FFC928")

        # Active project card
        self.renderer.draw_rect(12, 58, 216, 68, fill="#1C1D1F", radius=8)
        act = state.get("activity", "soldering_circuit").replace("_", " ").title()
        self.renderer.draw_text(20, 68, "Active Build:", size=9, color="#879099")
        self.renderer.draw_text(20, 84, act[:24], size=12, color="#FFC928")
        self.renderer.draw_rect(20, 108, 200, 6, fill="#302D28", radius=3)
        self.renderer.draw_rect(20, 108, 140, 6, fill="#F28B24", radius=3)

        # Workshop Mascot
        char_frame = ASSETS_DIR / "characters" / "master_character.png"
        self.renderer.draw_image(70, 136, char_frame, 100, 100)

        # Start Experiment Button
        self.renderer.draw_rect(16, 244, 208, 32, fill="#F28B24", radius=6)
        self.renderer.draw_text(52, 254, "RUN EXPERIMENT (+20 XP)", size=10, color="#FFFFFF")
        self.renderer.register_touch_target(16, 244, 208, 32, lambda: self.pet_manager.add_xp(20, "Manual Experiment"))

    def render_modes_screen(self, state: Dict[str, Any]):
        """5. Modes Screen: 8 operating modes selector."""
        self.renderer.clear(color=(36, 37, 34))
        self.renderer.draw_text(16, 32, "8 OPERATING MODES", size=13, color="#FFC928")

        modes = [
            ("auto", "Auto"),
            ("workshop", "Workshop"),
            ("music", "Music"),
            ("game", "Game"),
            ("study", "Study"),
            ("focus", "Focus"),
            ("companion", "Companion"),
            ("sleep", "Sleep")
        ]

        active_mode = state.get("mode", "auto")
        col_w, row_h = 100, 44
        for i, (m_id, m_label) in enumerate(modes):
            col = i % 2
            row = i // 2
            bx = 14 + col * 112
            by = 56 + row * 48

            is_selected = (m_id == active_mode)
            bg_col = "#F28B24" if is_selected else "#1C1D1F"
            self.renderer.draw_rect(bx, by, col_w, row_h, fill=bg_col, radius=6)
            self.renderer.draw_text(bx + 16, by + 16, m_label, size=11, color="#FFFFFF")
            self.renderer.register_touch_target(bx, by, col_w, row_h, lambda m=m_id: self.pet_manager.set_mode(m))

    def render_music_screen(self, state: Dict[str, Any]):
        """6. Music Screen."""
        self.renderer.clear(color=(36, 37, 34))
        self.renderer.draw_text(16, 32, "MUSIC & RHYTHM", size=13, color="#38BDF8")
        char_frame = ASSETS_DIR / "characters" / "master_character.png"
        self.renderer.draw_image(50, 75, char_frame, 140, 140)
        self.renderer.draw_rect(14, 230, 212, 38, fill="#1C1D1F", radius=6)
        self.renderer.draw_text(24, 238, "Oscillator Beat Active", size=10, color="#38BDF8")
        self.renderer.draw_text(24, 252, "Tuned to companion audio stream", size=8, color="#879099")

    def render_games_screen(self):
        """7. Games Screen."""
        self.renderer.clear(color=(36, 37, 34))
        self.renderer.draw_text(16, 32, "MAKER MINI-GAMES", size=13, color="#FFC928")
        games = [
            ("Wire Puzzle", "Connect circuit paths", 60),
            ("Gear Match", "Align brass reduction gears", 118),
            ("Frequency Tap", "Tap in rhythm to calibrate", 176)
        ]
        for title, desc, gy in games:
            self.renderer.draw_rect(14, gy, 212, 48, fill="#1C1D1F", radius=6)
            self.renderer.draw_text(24, gy + 10, title, size=11, color="#FFFFFF")
            self.renderer.draw_text(24, gy + 28, desc, size=8, color="#879099")
            self.renderer.draw_rect(160, gy + 12, 54, 24, fill="#F28B24", radius=4)
            self.renderer.draw_text(174, gy + 18, "PLAY", size=9, color="#FFFFFF")
            self.renderer.register_touch_target(160, gy + 12, 54, 24, lambda: self.pet_manager.add_xp(15, "Mini-game won!"))

    def render_profile_screen(self, state: Dict[str, Any]):
        """8. Profile Screen."""
        self.renderer.clear(color=(36, 37, 34))
        self.renderer.draw_text(16, 32, "MAKER PROFILE", size=13, color="#FFC928")
        self.renderer.draw_rect(14, 60, 212, 80, fill="#1C1D1F", radius=8)
        char_frame = ASSETS_DIR / "characters" / "master_character.png"
        self.renderer.draw_image(22, 68, char_frame, 64, 64)

        level = state.get("level", 1)
        xp = state.get("xp", 0)
        xp_next = state.get("xp_next", 100)
        self.renderer.draw_text(96, 72, state.get("name", "TINKO"), size=13, color="#FFC928")
        self.renderer.draw_text(96, 92, f"Level {level} Builder", size=10, color="#F28B24")
        self.renderer.draw_text(96, 110, f"{xp} / {xp_next} XP", size=9, color="#879099")

    def render_settings_screen(self):
        """9. Settings Screen (More tab)."""
        self.renderer.clear(color=(36, 37, 34))
        self.renderer.draw_text(16, 32, "MORE & SETTINGS", size=13, color="#FFC928")

        info_items = [
            ("Phone App URL", f"http://<IP>:{WEB_PORT}", 60),
            ("Hardware Target", "UNIHIKER M10 (240x320)", 106),
            ("Mascot Profile", "TINKO (Maker Robot)", 152),
            ("System Storage", "Debian Linux / SQLite WAL", 198)
        ]
        for label, val, iy in info_items:
            self.renderer.draw_rect(14, iy, 212, 38, fill="#1C1D1F", radius=6)
            self.renderer.draw_text(22, iy + 6, label, size=8, color="#879099")
            self.renderer.draw_text(22, iy + 20, val, size=9, color="#FFFFFF")

        # Backup Button
        self.renderer.draw_rect(14, 246, 212, 30, fill="#83A978", radius=6)
        self.renderer.draw_text(60, 254, "SNAPSHOT BACKUP NOW", size=9, color="#FFFFFF")
        from storage.backup import create_backup
        self.renderer.register_touch_target(14, 246, 212, 30, lambda: create_backup("manual"))

    def render_notifications_screen(self):
        """10. Notifications Screen."""
        self.renderer.clear(color=(36, 37, 34))
        self.renderer.draw_text(16, 32, "NOTIFICATIONS", size=13, color="#FFC928")
        notes = [
            ("Live Sync Connected", "Phone companion app paired", "#83A978", 60),
            ("Autonomous Task", "Tinkering with electronics", "#F28B24", 116),
            ("Backup Ready", "Daily database snapshot verified", "#38BDF8", 172)
        ]
        for title, desc, col, ny in notes:
            self.renderer.draw_rect(14, ny, 212, 46, fill="#1C1D1F", radius=6)
            self.renderer.draw_rect(14, ny, 4, 46, fill=col, radius=2)
            self.renderer.draw_text(26, ny + 8, title, size=11, color="#FFFFFF")
            self.renderer.draw_text(26, ny + 24, desc[:30], size=8, color="#879099")
