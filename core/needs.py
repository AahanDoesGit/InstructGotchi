"""
Instructa-Gotchi Needs System
Manages hunger, happiness, energy, cleanliness, and health (0-100).
Calculates time-based decay, stat recovery, and care actions.
"""
import time
from typing import Dict, Any

# Decay rates in points per hour (3600 seconds)
DECAY_RATES = {
    "hunger": 6.0,       # drops ~6 points/hr
    "energy": 4.0,       # drops ~4 points/hr when active
    "cleanliness": 3.0,  # drops ~3 points/hr
    "happiness": 5.0     # drops ~5 points/hr if neglected
}

def clamp(val: float, low: float = 0.0, high: float = 100.0) -> int:
    return int(max(low, min(high, round(val))))

def calculate_decay(state: Dict[str, Any], elapsed_seconds: float) -> Dict[str, Any]:
    """Applies realistic time decay based on elapsed time since last update."""
    hours = elapsed_seconds / 3600.0
    mode = state.get("mode", "auto")
    is_charging = bool(state.get("charging", 0))

    # If charging on dock, energy and battery saturation recover rapidly
    if is_charging:
        energy_change = hours * 60.0  # fast battery recharge
        hunger_change = hours * 50.0  # power cell saturation
        clean_change = -(hours * 1.0)
        happy_change = hours * 10.0
    elif mode == "sleep":
        energy_change = hours * 15.0  # +15 energy per hour of sleep
        hunger_change = -(hours * (DECAY_RATES["hunger"] * 0.3))
        clean_change = -(hours * (DECAY_RATES["cleanliness"] * 0.2))
        happy_change = 0.0
    else:
        energy_change = -(hours * DECAY_RATES["energy"])
        hunger_change = -(hours * DECAY_RATES["hunger"])
        clean_change = -(hours * DECAY_RATES["cleanliness"])
        happy_change = -(hours * DECAY_RATES["happiness"])

    new_hunger = clamp(state["hunger"] + hunger_change)
    new_energy = clamp(state["energy"] + energy_change)
    new_clean = clamp(state["cleanliness"] + clean_change)
    new_happy = clamp(state["happiness"] + happy_change)

    # Health drops if hunger or cleanliness is critically low (< 20)
    health_change = 0.0
    if new_hunger < 20 or new_clean < 20:
        health_change = -(hours * 10.0)
    elif new_hunger > 70 and new_clean > 70 and new_energy > 70:
        health_change = hours * 5.0  # natural recovery

    new_health = clamp(state["health"] + health_change)
    new_voltage = round(3.60 + 0.60 * (new_energy / 100.0), 2)

    # Temperature tracking: fan cools, working heats
    fan_active = bool(state.get("fan_active", 0))
    current_temp = float(state.get("temperature", 36.5))
    target_temp = 31.5 if fan_active else (42.0 if state.get("activity") == "soldering_circuit" else 36.5)
    temp_diff = target_temp - current_temp
    new_temp = round(current_temp + (temp_diff * min(1.0, hours * 12.0)), 1)

    return {
        "hunger": new_hunger,
        "energy": new_energy,
        "cleanliness": new_clean,
        "happiness": new_happy,
        "health": new_health,
        "voltage": new_voltage,
        "temperature": new_temp
    }

def apply_care_action(action: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes care actions: feed/charge, clean/oil, play, rest, heal/diagnostics, fan, tighten.
    Returns the stat delta and speech reaction.
    """
    updates = {}
    speech = ""
    xp_gain = 10

    if action in ("feed", "charge", "dock_charge"):
        updates["hunger"] = clamp(current_state["hunger"] + 35)
        updates["energy"] = clamp(current_state["energy"] + 30)
        updates["voltage"] = round(3.60 + 0.60 * (updates["energy"] / 100.0), 2)
        speech = "⚡ Power dock engaged! Battery cells charged at 1.2A fast rate."
    elif action == "dock_toggle":
        curr_charging = current_state.get("charging", 0)
        new_charging = 0 if curr_charging else 1
        updates["charging"] = new_charging
        if new_charging:
            updates["energy"] = clamp(current_state["energy"] + 15)
            speech = "⚡ Click! Tinko docked into the high-voltage charging cradle."
        else:
            speech = "🔌 Unlatched from charging dock. Running on internal LiPo battery."
    elif action == "pet":
        updates["happiness"] = clamp(current_state["happiness"] + 15)
        xp_gain = 5
        speech = "*Happy servo whirrs* Thanks for the pet, Maker!"
    elif action in ("clean", "oil", "oil_gears"):
        updates["cleanliness"] = 100
        updates["happiness"] = clamp(current_state["happiness"] + 15)
        speech = "⚙️ Gears degreased and lubricated with synthetic maker oil!"
    elif action in ("tighten", "tighten_chassis", "calibrate"):
        updates["health"] = clamp(current_state["health"] + 25)
        updates["happiness"] = clamp(current_state["happiness"] + 10)
        xp_gain = 15
        speech = "🔧 Chassis bolts torqued to 0.8 Nm and servos calibrated."
    elif action in ("fan_toggle", "cooling_fan", "fan"):
        curr_fan = current_state.get("fan_active", 0)
        new_fan = 0 if curr_fan else 1
        updates["fan_active"] = new_fan
        if new_fan:
            updates["temperature"] = max(31.0, float(current_state.get("temperature", 36.5)) - 4.5)
            speech = "💨 Turbine cooling fan spun up to 8,000 RPM! Heatsink chilling."
        else:
            speech = "💨 Cooling fan throttled down to quiet silent mode."
    elif action in ("thermal_paste", "repaste"):
        updates["temperature"] = 31.5
        updates["health"] = clamp(current_state["health"] + 15)
        xp_gain = 20
        speech = "❄️ Fresh diamond thermal paste applied to CPU heatspreader!"
    elif action == "play":
        if current_state["energy"] < 15:
            speech = "Low battery warning! Need charging dock before games."
            return {"speech": speech, "xp_gain": 0}
        updates["happiness"] = clamp(current_state["happiness"] + 25)
        updates["energy"] = clamp(current_state["energy"] - 15)
        updates["hunger"] = clamp(current_state["hunger"] - 10)
        updates["voltage"] = round(3.60 + 0.60 * (updates["energy"] / 100.0), 2)
        xp_gain = 25
        speech = "🎮 Minigame completed! Subsystems energized and happy."
    elif action == "rest":
        updates["mode"] = "sleep"
        speech = "💤 Entering low-power sleep state. Standby LEDs active."
    elif action in ("heal", "diagnostics", "run_diagnostics"):
        updates["health"] = 100
        updates["happiness"] = clamp(current_state["happiness"] + 15)
        xp_gain = 15
        speech = "📊 Diagnostic complete: 0 faults, RAM verified, all servos nominal!"
    else:
        speech = "Blinked."

    return {
        "updates": updates,
        "speech": speech,
        "xp_gain": xp_gain
    }

