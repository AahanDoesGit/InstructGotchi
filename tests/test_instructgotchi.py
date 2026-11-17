"""
Instructa-Gotchi Test Suite
Tests SQLite persistence, needs decay, mood evaluation, activity engine,
backup integrity, API request dispatcher, and device UI screen rendering.
"""
import sys
import unittest
from pathlib import Path

# Add doc/instructgotchi to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from storage.database import get_pet_state, update_pet_state, init_db, log_activity, get_activity_history
from storage.backup import create_backup, verify_database_integrity
from core.needs import calculate_decay, apply_care_action
from core.mood import evaluate_mood
from core.activity_engine import ActivityEngine
from core.animation_controller import AnimationController
from display.renderer import ScreenRenderer
from display.screens import ScreenManager
from core.pet_state import PetStateManager
from web.routes import handle_api_request

class TestInstructaGotchi(unittest.TestCase):

    def setUp(self):
        init_db()

    def test_database_initialization(self):
        state = get_pet_state()
        self.assertIsNotNone(state)
        self.assertEqual(state["id"], 1)
        self.assertIn("hunger", state)
        self.assertIn("happiness", state)

    def test_needs_decay_and_care(self):
        initial = {"hunger": 50, "happiness": 50, "energy": 50, "cleanliness": 50, "health": 100, "mode": "auto"}
        decayed = calculate_decay(initial, elapsed_seconds=3600)
        self.assertLess(decayed["hunger"], 50)
        self.assertLess(decayed["energy"], 50)

        care_res = apply_care_action("feed", initial)
        self.assertIn("updates", care_res)
        self.assertGreater(care_res["updates"]["hunger"], 50)

    def test_mood_evaluation(self):
        # High stats -> happy or excited
        happy_state = {"mode": "auto", "energy": 90, "hunger": 90, "happiness": 90, "cleanliness": 90}
        self.assertEqual(evaluate_mood(happy_state), "excited")

        # Sleep mode -> sleepy
        sleep_state = {"mode": "sleep", "energy": 80, "hunger": 80, "happiness": 80}
        self.assertEqual(evaluate_mood(sleep_state), "sleepy")

        # Low hunger -> frustrated
        hungry_state = {"mode": "auto", "energy": 80, "hunger": 10, "happiness": 80, "cleanliness": 80}
        self.assertEqual(evaluate_mood(hungry_state), "frustrated")

    def test_backup_and_integrity(self):
        backup_path = create_backup("unittest")
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        self.assertTrue(verify_database_integrity(backup_path))
        # Cleanup test backup
        backup_path.unlink()

    def test_all_10_device_screens_render(self):
        """Renders every single device screen to virtual buffer to ensure zero asset or layout exceptions."""
        renderer = ScreenRenderer()
        pet_mgr = PetStateManager()
        anim = AnimationController()
        mgr = ScreenManager(renderer, pet_mgr, anim)
        state = pet_mgr.get_state()

        # 1. Boot
        mgr.render_boot_screen()
        # 2. Home
        mgr.render_home_screen(state)
        # 3. Care
        mgr.render_care_screen(state)
        # 4. Workshop
        mgr.render_workshop_screen(state)
        # 5. Modes
        mgr.render_modes_screen(state)
        # 6. Music
        mgr.render_music_screen(state)
        # 7. Games
        mgr.render_games_screen()
        # 8. Profile
        mgr.render_profile_screen(state)
        # 9. Settings
        mgr.render_settings_screen()
        # 10. Notifications
        mgr.render_notifications_screen()

        # Verify buffer dimensions
        self.assertEqual(renderer.framebuffer.size, (240, 320))

    def test_living_workshop_scenes(self):
        """Validates that the pure character living screen renders all 15 moods/modes at 240x320."""
        from display.living_screen import LivingScreenManager, MOOD_TO_SCENE, MODE_TO_SCENE
        renderer = ScreenRenderer()
        pet_mgr = PetStateManager()
        anim = AnimationController()
        living = LivingScreenManager(renderer, pet_mgr, anim)

        # Test all moods
        for mood in MOOD_TO_SCENE.keys():
            state = {"mode": "auto", "mood": mood, "activity": "tinkering"}
            living.render_living_workshop(state)
            self.assertEqual(renderer.framebuffer.size, (240, 320))

        # Test all modes
        for mode in MODE_TO_SCENE.keys():
            state = {"mode": mode, "mood": "idle", "activity": "workshop"}
            living.render_living_workshop(state)
            self.assertEqual(renderer.framebuffer.size, (240, 320))

        # Test touch reaction
        living.trigger_reaction("pet", duration=2.0)
        living.render_living_workshop({"mode": "auto", "mood": "idle"})
        self.assertEqual(living.get_current_scene_name({"mode": "auto"}), "scene_celebrating")

    def test_api_dispatcher(self):
        state_resp = handle_api_request("/api/state", "GET")
        self.assertEqual(state_resp["status"], "ok")
        self.assertIn("state", state_resp)
        self.assertIn("voltage", state_resp["state"])

        care_resp = handle_api_request("/api/care", "POST", {"action": "clean"})
        self.assertEqual(care_resp["status"], "ok")
        self.assertEqual(care_resp["state"]["cleanliness"], 100)

        # Robot Charging Dock Toggle
        dock_resp = handle_api_request("/api/charge", "POST", {"action": "dock_toggle"})
        self.assertEqual(dock_resp["status"], "ok")

        # Maker Parts Retrieval
        parts_resp = handle_api_request("/api/parts", "GET")
        self.assertEqual(parts_resp["status"], "ok")
        self.assertTrue(len(parts_resp["parts"]) > 0)

        # Minigame Win & Parts Drop
        game_resp = handle_api_request("/api/minigame", "POST", {"game": "wire_fixer", "score": 150})
        self.assertEqual(game_resp["status"], "ok")
        self.assertIn("drop", game_resp)

        # Remote UNIHIKER Command
        cmd_resp = handle_api_request("/api/command", "POST", {"command": "solder"})
        self.assertEqual(cmd_resp["status"], "ok")
        self.assertEqual(cmd_resp["state"]["activity"], "soldering_circuit")

if __name__ == "__main__":
    unittest.main()

