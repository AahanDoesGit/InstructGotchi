"""
Instructa-Gotchi Mood Computation
Evaluates pet stats, current activity, and environment to determine emotional state.
"""
from typing import Dict, Any

def evaluate_mood(state: Dict[str, Any]) -> str:
    """
    Computes primary mood string matching available expression assets:
    'idle', 'happy', 'excited', 'curious', 'surprised', 'bored', 'sleepy',
    'frustrated', 'proud', 'thinking', 'sad', 'focused', 'laughing', 'celebrating'.
    """
    mode = state.get("mode", "auto")
    energy = state.get("energy", 80)
    hunger = state.get("hunger", 80)
    happiness = state.get("happiness", 80)
    cleanliness = state.get("cleanliness", 80)
    activity = state.get("activity", "observing")

    # Sleep mode takes precedence
    if mode == "sleep" or energy < 15:
        return "sleepy"

    # Critically low needs
    if hunger < 20:
        return "frustrated"
    if cleanliness < 20 or happiness < 25:
        return "sad"

    # Mode-driven expressions
    if mode == "focus":
        return "focused"
    if mode == "music":
        return "excited" if happiness > 60 else "happy"
    if mode == "workshop":
        if "repair" in activity or "soldering" in activity:
            return "focused"
        if "celebrat" in activity or "success" in activity:
            return "celebrating"
        return "curious"

    # Default / Auto mode evaluation
    if happiness >= 85 and energy >= 70:
        return "excited"
    if happiness >= 65:
        return "happy"
    if energy < 35:
        return "bored"

    return "idle"

