"""
Instructa-Gotchi Central Pet State Manager
Unified business logic coordinating needs decay, mood, leveling, autonomous activities,
and synchronizing with the SQLite database.
"""
import time
from typing import Dict, Any, List
from storage.database import get_pet_state, update_pet_state, log_activity
from core.needs import calculate_decay, apply_care_action
from core.mood import evaluate_mood
from core.personality import get_contextual_speech
from core.activity_engine import ActivityEngine

class PetStateManager:
    def __init__(self):
        self.activity_engine = ActivityEngine()
        self._cached_state = get_pet_state()
        if self._cached_state.get("activity") in (None, "", "observing", "idle"):
            self._cached_state["activity"] = "soldering_circuit"
            update_pet_state(self._cached_state)
        self._last_tick_time = time.time()

    def get_state(self) -> Dict[str, Any]:
        """Returns the current validated pet state."""
        return self._cached_state

    def tick(self) -> Dict[str, Any]:
        """
        Periodic update loop (runs once per second in main process).
        Performs needs decay, evaluates mood, checks autonomous activity changes.
        """
        now = time.time()
        elapsed = now - self._last_tick_time
        self._last_tick_time = now

        # 1. Calculate needs decay
        decayed_needs = calculate_decay(self._cached_state, elapsed)
        self._cached_state.update(decayed_needs)

        # 2. Check autonomous activity engine
        act_update = self.activity_engine.evaluate_next_activity(self._cached_state)
        if act_update:
            self._cached_state["activity"] = act_update["activity"]
            if "animation" in act_update:
                self._cached_state["animation"] = act_update["animation"]
            if "speech" in act_update:
                self._cached_state["speech"] = act_update["speech"]
            if "xp_gain" in act_update:
                self.add_xp(act_update["xp_gain"], f"Autonomous {act_update.get('title', 'Tinkering')}")
            if "title" in act_update:
                log_activity("workshop", self._cached_state["mode"], act_update["title"], act_update.get("description", ""))

        # 3. Evaluate mood
        new_mood = evaluate_mood(self._cached_state)
        self._cached_state["mood"] = new_mood

        # 4. Save periodically
        update_pet_state(self._cached_state)
        return self._cached_state

    def add_xp(self, amount: int, reason: str = ""):
        """Adds XP and handles level progression."""
        current_xp = self._cached_state.get("xp", 0) + amount
        level = self._cached_state.get("level", 1)
        xp_next = self._cached_state.get("xp_next", 100)

        # Level up condition
        if current_xp >= xp_next:
            current_xp -= xp_next
            level += 1
            xp_next = int(xp_next * 1.5)
            self._cached_state["level"] = level
            self._cached_state["xp_next"] = xp_next
            self._cached_state["speech"] = f"Level Up! Now Level {level} Master Builder!"
            log_activity("achievement", self._cached_state["mode"], f"Reached Level {level}!", f"Unlocked at {current_xp} XP", xp_gained=amount)
        else:
            if reason:
                log_activity("experience", self._cached_state["mode"], f"+{amount} XP: {reason}", xp_gained=amount)

        self._cached_state["xp"] = current_xp
        update_pet_state(self._cached_state)

    def set_mode(self, new_mode: str) -> bool:
        """Switches operating mode (auto, workshop, music, game, study, focus, companion, sleep)."""
        valid_modes = ["auto", "workshop", "music", "game", "study", "focus", "companion", "sleep"]
        if new_mode not in valid_modes:
            return False

        self._cached_state["mode"] = new_mode
        self._cached_state["mood"] = evaluate_mood(self._cached_state)
        self._cached_state["speech"] = get_contextual_speech(self._cached_state["mood"], new_mode, self._cached_state.get("activity", ""))
        update_pet_state(self._cached_state)
        log_activity("mode_change", new_mode, f"Switched to {new_mode.capitalize()} Mode")
        return True

    def perform_care(self, action: str) -> Dict[str, Any]:
        """Handles feed, clean, play, rest, heal care interactions."""
        res = apply_care_action(action, self._cached_state)
        if "updates" in res:
            self._cached_state.update(res["updates"])
        if "speech" in res and res["speech"]:
            self._cached_state["speech"] = res["speech"]
        if "xp_gain" in res and res["xp_gain"] > 0:
            self.add_xp(res["xp_gain"], f"Care action: {action}")

        self._cached_state["mood"] = evaluate_mood(self._cached_state)
        update_pet_state(self._cached_state)
        log_activity("care", self._cached_state["mode"], f"Care Action: {action.capitalize()}", res.get("speech", ""))
        return self._cached_state

