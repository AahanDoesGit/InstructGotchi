"""
Renders preview PNGs of all 10 UNIHIKER screens to test/previews/ for visual inspection.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from display.renderer import ScreenRenderer
from display.screens import ScreenManager
from display.navigation import NavigationController
from core.pet_state import PetStateManager
from core.animation_controller import AnimationController

from display.living_screen import LivingScreenManager, MOOD_TO_SCENE, MODE_TO_SCENE

def main():
    out_dir = PROJECT_ROOT / "tests" / "previews"
    out_dir.mkdir(parents=True, exist_ok=True)

    renderer = ScreenRenderer()
    pet_mgr = PetStateManager()
    anim = AnimationController()
    living = LivingScreenManager(renderer, pet_mgr, anim)

    # Render all Living Workshop character scenes
    print("--- Rendering UNIHIKER M10 Living Character Scenes (240x320) ---")
    scenes_to_test = [
        ("living_idle", {"mode": "auto", "mood": "idle", "activity": "observing"}),
        ("living_working", {"mode": "workshop", "mood": "focused", "activity": "soldering"}),
        ("living_happy", {"mode": "auto", "mood": "happy", "activity": "playing"}),
        ("living_celebrating", {"mode": "auto", "mood": "celebrating", "activity": "party"}),
        ("living_excited", {"mode": "auto", "mood": "excited", "activity": "jumping"}),
        ("living_thinking", {"mode": "study", "mood": "thinking", "activity": "design"}),
        ("living_sleep", {"mode": "sleep", "mood": "sleepy", "activity": "resting"}),
        ("living_music", {"mode": "music", "mood": "happy", "activity": "grooving"}),
        ("living_sad", {"mode": "auto", "mood": "sad", "activity": "lonely"}),
    ]

    for name, state in scenes_to_test:
        living.render_living_workshop(state)
        img_path = out_dir / f"{name}_240x320.png"
        renderer.save_debug_screenshot(img_path)
        print(f"Rendered: {img_path.name}")

if __name__ == "__main__":
    main()

