"""
Instructa-Gotchi UNIHIKER M10 Pure Character Living Screen (240x320)
Renders ONLY the character living, animating, and working in its workshop.
No menus, no HUD, no buttons, no status overlays.
The UNIHIKER display is 100% the living companion actively working in its home.
"""
import time
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import DISPLAY_WIDTH, DISPLAY_HEIGHT, ASSETS_DIR


# Maps mood evaluator outputs -> static fallback scene file names
MOOD_TO_SCENE = {
    "idle":        "scene_working",  # Maker companion defaults to working instead of standing idle
    "happy":       "scene_happy",
    "excited":     "scene_excited",
    "curious":     "scene_thinking",
    "surprised":   "scene_excited",
    "bored":       "scene_working",
    "sleepy":      "scene_sleepy",
    "frustrated":  "scene_sad",
    "proud":       "scene_celebrating",
    "thinking":    "scene_thinking",
    "sad":         "scene_sad",
    "focused":     "scene_working",
    "laughing":    "scene_happy",
    "confused":    "scene_thinking",
    "celebrating": "scene_celebrating",
}

# Maps operating modes -> static fallback scene file names
MODE_TO_SCENE = {
    "sleep":     "scene_sleep",
    "music":     "scene_music",
    "workshop":  "scene_working",
    "focus":     "scene_focused",
    "study":     "scene_thinking",
    "game":      "scene_excited",
    "companion": "scene_happy",
}

# Maps care actions -> reaction scene + duration
CARE_REACTIONS = {
    "feed":  ("scene_happy",       3.0),
    "clean": ("scene_excited",     2.5),
    "play":  ("scene_celebrating", 3.5),
    "rest":  ("scene_sleepy",      3.0),
    "pet":   ("scene_celebrating", 2.5),
}


class LivingScreenManager:
    def __init__(self, renderer, pet_manager, anim_controller):
        self.renderer = renderer
        self.pet_manager = pet_manager
        self.anim = anim_controller

        # Ephemeral reaction state (when touched on UNIHIKER or commanded via Phone Web UI)
        self.reaction_until = 0.0
        self.reaction_scene = "scene_happy"

        self.scenes_dir = ASSETS_DIR / "scenes"
        self._available_scenes = set()
        self._scan_available_scenes()

    def _scan_available_scenes(self):
        """Scan the scenes directory to know which files are available."""
        if self.scenes_dir.exists():
            for f in self.scenes_dir.iterdir():
                if f.suffix == ".png" and f.stem.startswith("scene_"):
                    self._available_scenes.add(f.stem)

    def _resolve_scene_file(self, scene_name: str) -> Path:
        """Get the scene file path, with cascading fallback."""
        if scene_name in self._available_scenes:
            return self.scenes_dir / f"{scene_name}.png"

        fallbacks = {
            "scene_excited":     "scene_happy",
            "scene_celebrating": "scene_happy",
            "scene_laughing":    "scene_happy",
            "scene_proud":       "scene_happy",
            "scene_curious":     "scene_thinking",
            "scene_confused":    "scene_thinking",
            "scene_frustrated":  "scene_sad",
            "scene_bored":       "scene_working",
            "scene_sleepy":      "scene_sleep",
            "scene_surprised":   "scene_excited",
            "scene_focused":     "scene_working",
            "scene_music":       "scene_happy",
            "scene_idle":        "scene_working",
        }

        fallback = fallbacks.get(scene_name)
        if fallback and fallback in self._available_scenes:
            return self.scenes_dir / f"{fallback}.png"

        return self.scenes_dir / "scene_working.png"

    def trigger_reaction(self, action_or_mood: str, speech: str = "", duration: float = 0.0):
        """Called when user executes a care action on phone or taps UNIHIKER screen."""
        if action_or_mood in CARE_REACTIONS:
            scene, default_dur = CARE_REACTIONS[action_or_mood]
        elif action_or_mood in MOOD_TO_SCENE:
            scene = MOOD_TO_SCENE[action_or_mood]
            default_dur = 2.5
        elif f"scene_{action_or_mood}" in self._available_scenes:
            scene = f"scene_{action_or_mood}"
            default_dur = 2.5
        else:
            scene = "scene_happy"
            default_dur = 2.5

        self.reaction_until = time.time() + (duration or default_dur)
        self.reaction_scene = scene

    def get_current_animation_sequence(self, state: Dict[str, Any]) -> Optional[str]:
        """
        Determines the active multi-frame animated sequence based on mood, mode, and activity.
        Animates Tinko actively working, moving hands, soldering, dancing, or sleeping.
        """
        now = time.time()

        # 1. Ephemeral reaction (e.g. petting or phone care)
        if now < self.reaction_until:
            if self.reaction_scene in ("scene_happy", "scene_celebrating", "scene_excited"):
                return "celebrating"
            elif self.reaction_scene in ("scene_sleep", "scene_sleepy"):
                return "sleeping"

        mode = state.get("mode", "auto")

        # 2. Operating mode specific animations
        if mode == "music":
            return "music_dancing"
        if mode == "sleep":
            return "sleeping"

        # 3. Direct animation tag from autonomous activity engine
        anim_tag = state.get("animation")
        if anim_tag == "music_dancing":
            return "music_dancing"
        elif anim_tag == "celebrating":
            return "celebrating"
        elif anim_tag == "sleeping":
            return "sleeping"
        elif anim_tag == "working_soldering":
            return "working_soldering"
        elif anim_tag == "thinking":
            return "thinking"
        elif anim_tag == "idle":
            return None

        # 4. Energy check: if exhausted, Tinko naps
        energy = state.get("energy", 80)
        if energy < 20:
            return "sleeping"

        # 5. Activity-driven animated motion
        activity = state.get("activity", "soldering_circuit")
        if "jam" in activity or "music" in activity or "dance" in activity:
            return "music_dancing"
        if "celebrat" in activity:
            return "celebrating"
        if "sleep" in activity or "nap" in activity:
            return "sleeping"
        if "sketch" in activity or "blueprint" in activity or "think" in activity:
            return "thinking"
        if "breather" in activity:
            return None
        if any(kw in activity for kw in ("soldering", "repair", "gear", "circuit", "build", "assembl", "print")):
            return "working_soldering"

        # 6. Mood-driven animations
        mood = state.get("mood", "happy")
        if mood in ("celebrating", "excited"):
            return "celebrating"
        if mood in ("thinking", "curious"):
            return "thinking"
        if mood in ("sleepy", "sleep"):
            return "sleeping"

        # Active default: soldering at workbench with moving hands
        return "working_soldering"

    def get_current_scene_name(self, state: Dict[str, Any]) -> str:
        """Determines the static fallback workshop scene based on mode, activity, mood, and reactions."""
        now = time.time()
        if now < self.reaction_until:
            return self.reaction_scene

        mode = state.get("mode", "auto")
        if mode in MODE_TO_SCENE:
            return MODE_TO_SCENE[mode]

        activity = state.get("activity", "soldering_circuit")
        if "jam" in activity or "dance" in activity:
            return "scene_music"
        if "celebrat" in activity:
            return "scene_celebrating"
        if "sleep" in activity or "nap" in activity:
            return "scene_sleep"
        if any(kw in activity for kw in ("repair", "soldering", "gear", "circuit", "build", "assembl")):
            return "scene_working"
        if any(kw in activity for kw in ("design", "sketch", "blueprint", "plan")):
            return "scene_thinking"
        if any(kw in activity for kw in ("breather", "idle")):
            return "scene_idle"
        if any(kw in activity for kw in ("test", "debug", "inspect")):
            return "scene_focused"

        mood = state.get("mood", "happy")
        return MOOD_TO_SCENE.get(mood, "scene_working")

    def render_living_workshop(self, state: Dict[str, Any]):
        """
        Renders the pure 240x320 living scene onto the UNIHIKER screen:
        - Multi-frame animated working sequence (moving hands, soldering, sparks, smoke, dancing, sleeping)
        - Zero text overlays, zero buttons, zero HUD
        - Entire screen touch interaction for gentle petting
        """
        anim_seq = self.get_current_animation_sequence(state)
        frame_file = None
        if anim_seq:
            frame_file = self.anim.get_sequence_frame(anim_seq)

        if not frame_file or not frame_file.exists():
            scene_name = self.get_current_scene_name(state)
            frame_file = self._resolve_scene_file(scene_name)

        # Draw full-bleed 240x320 scene
        self.renderer.draw_image(0, 0, frame_file, DISPLAY_WIDTH, DISPLAY_HEIGHT)

        # Register screen touch: tapping pet triggers an affectionate acknowledgement without derailing workflow
        self.renderer.register_touch_target(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, self.on_screen_tapped)

    def on_screen_tapped(self):
        """Physical touch on UNIHIKER screen: character perks up, celebrates, and gains small XP."""
        self.pet_manager.perform_care("pet")
        self.trigger_reaction("pet", duration=2.5)
