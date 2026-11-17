"""
Instructa-Gotchi Personality and Voice Engine
Generates concise maker-themed contextual speech lines based on pet mood, activity, and mode.
"""
import random
from typing import Dict, Any

CONTEXTUAL_LINES = {
    "workshop": [
        "Hmm. I have an idea.",
        "Let's take this apart.",
        "That actually worked!",
        "Tightening the chassis bolts.",
        "Soldering iron is ready.",
        "Back to the workshop.",
        "New project unlocked!"
    ],
    "curious": [
        "What happens if we wire this up?",
        "One more experiment?",
        "Reading the schematics...",
        "I wonder how this sensor works."
    ],
    "excited": [
        "Invention complete!",
        "All systems humming at 100%!",
        "Check out this blueprint!",
        "Level up incoming!"
    ],
    "sleepy": [
        "I need a tiny break.",
        "Powering down auxiliary circuits...",
        "Zzz... dreaming of gears...",
        "Low battery, rest time."
    ],
    "music": [
        "Rhythm detected! Oscillating to the beat.",
        "Great audio track playing.",
        "Antenna tuned to the groove."
    ],
    "focus": [
        "Quiet time. Maker focus mode on.",
        "Timer running. Let's make progress.",
        "Deep concentration active."
    ],
    "frustrated": [
        "Well... that was unexpected.",
        "A screw just fell under the bench.",
        "Short circuit detected! Need a tweak."
    ],
    "default": [
        "Ready to build together?",
        "Workshop is warm and clean.",
        "Tinkering is the best part of the day."
    ]
}

def get_contextual_speech(mood: str, mode: str, activity: str) -> str:
    """Returns a character speech line based on current conditions."""
    if mode == "sleep" or mood == "sleepy":
        return random.choice(CONTEXTUAL_LINES["sleepy"])
    if mode == "focus":
        return random.choice(CONTEXTUAL_LINES["focus"])
    if mode == "music":
        return random.choice(CONTEXTUAL_LINES["music"])
    if mode == "workshop":
        return random.choice(CONTEXTUAL_LINES["workshop"])
    if mood in CONTEXTUAL_LINES:
        return random.choice(CONTEXTUAL_LINES[mood])
    return random.choice(CONTEXTUAL_LINES["default"])

