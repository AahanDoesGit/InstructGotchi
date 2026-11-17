"""
Instructa-Gotchi Autonomous Activity Engine
Directs Tinko's live autonomous behavior loop:
Every few seconds, Tinko transitions on his own between:
- Soldering and building circuits (moving hands, micro-sparks)
- Listening to music / dancing in the workshop (grooving to the beat)
- Designing & analyzing schematics (blueprints, idea bulb)
- Assembling gears & mechanical repair
- Celebrating completed builds (waving arms, stars)
- Short workbench breaks / power naps
"""
import random
import time
from typing import Dict, Any, List

AUTONOMOUS_WORKSHOP_CYCLE = [
    {
        "name": "soldering_circuit",
        "title": "Soldering Micro-Circuit",
        "desc": "Soldering LED resistors onto the board with sparks",
        "animation": "working_soldering",
        "duration": (8.0, 14.0),
        "mood": "focused",
        "weight": 35
    },
    {
        "name": "workshop_jam",
        "title": "Jamming to Music",
        "desc": "Workshop radio turned on! Vibing to maker beats",
        "animation": "music_dancing",
        "duration": (6.0, 10.0),
        "mood": "happy",
        "weight": 25
    },
    {
        "name": "sketching_blueprints",
        "title": "Drafting Blueprints",
        "desc": "Designing the next mechanical project",
        "animation": "thinking",
        "duration": (6.0, 10.0),
        "mood": "curious",
        "weight": 20
    },
    {
        "name": "gear_assembly",
        "title": "Assembling Brass Gears",
        "desc": "Aligning gear teeth and tightening screws",
        "animation": "working_soldering",
        "duration": (8.0, 12.0),
        "mood": "focused",
        "weight": 25
    },
    {
        "name": "milestone_celebration",
        "title": "Project Finished!",
        "desc": "Circuits tested and working! Celebrating victory",
        "animation": "celebrating",
        "duration": (5.0, 8.0),
        "mood": "celebrating",
        "weight": 15
    },
    {
        "name": "workbench_breather",
        "title": "Workshop Breather",
        "desc": "Satisfied look around the clean workshop",
        "animation": "idle",
        "duration": (5.0, 8.0),
        "mood": "happy",
        "weight": 10
    }
]

class ActivityEngine:
    def __init__(self):
        self.last_transition_time = 0.0
        self.current_duration = 8.0  # seconds until next autonomous change
        self.current_activity_index = 0
        self.last_activity_name = ""

    def evaluate_next_activity(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Autonomously steps Tinko through lively workshop behaviors every few seconds.
        """
        now = time.time()
        mode = current_state.get("mode", "auto")
        energy = current_state.get("energy", 80)

        # 1. Hard overrides: Sleep mode or extreme exhaustion (<15%)
        if energy < 15 or mode == "sleep":
            if current_state.get("activity") != "power_nap":
                self.last_transition_time = now
                self.current_duration = 15.0
                return {
                    "activity": "power_nap",
                    "title": "Cozy Power Nap",
                    "speech": "Zzz... recharging battery.",
                    "animation": "sleeping",
                    "mood": "sleepy"
                }
            return {}

        # 2. Hard override: Music mode locked
        if mode == "music":
            if current_state.get("activity") != "workshop_jam":
                self.last_transition_time = now
                self.current_duration = 15.0
                return {
                    "activity": "workshop_jam",
                    "title": "Nonstop Workshop Jam",
                    "speech": "Grooving to the music!",
                    "animation": "music_dancing",
                    "mood": "happy"
                }
            return {}

        # 3. Check autonomous timer (Every 6 to 14 seconds)
        if now - self.last_transition_time < self.current_duration:
            return {}

        # Transition to next dynamic behavior
        candidates = [act for act in AUTONOMOUS_WORKSHOP_CYCLE if act["name"] != self.last_activity_name]
        weights = [act["weight"] for act in candidates]
        chosen = random.choices(candidates, weights=weights, k=1)[0]

        self.last_activity_name = chosen["name"]
        self.last_transition_time = now
        min_d, max_d = chosen["duration"]
        self.current_duration = random.uniform(min_d, max_d)

        xp_gain = 5 if "celebration" in chosen["name"] else 2

        return {
            "activity": chosen["name"],
            "title": chosen["title"],
            "description": chosen["desc"],
            "animation": chosen["animation"],
            "mood": chosen["mood"],
            "xp_gain": xp_gain
        }
