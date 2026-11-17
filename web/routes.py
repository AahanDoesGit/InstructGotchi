"""
Instructa-Gotchi Web Companion Server & API Routes
Provides REST endpoints and static file serving for the local Wi-Fi mobile companion.
Supports Flask when installed, and provides a built-in Python http.server fallback.
"""
import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, Any
from storage.database import (
    get_pet_state, update_pet_state, log_activity,
    get_activity_history, get_missions, get_inventory, get_achievements,
    get_maker_parts, add_maker_part, consume_maker_parts
)
from storage.backup import create_backup, export_zip
from core.needs import apply_care_action
from core.mood import evaluate_mood
from core.personality import get_contextual_speech
from config.settings import WEB_HOST, WEB_PORT, BASE_DIR, DATA_DIR

def handle_api_request(endpoint: str, method: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Pure business logic dispatcher for web API calls."""
    data = data or {}
    from device_app import get_active_device_app

    if endpoint == "/api/device/touch" and method == "POST":
        x = int(data.get("x", 0))
        y = int(data.get("y", 0))
        app = get_active_device_app()
        if app:
            app.handle_touch(x, y)
            return {"status": "ok", "touched": {"x": x, "y": y}}
        return {"status": "error", "message": "Device app not active"}

    elif endpoint == "/api/state" and method == "GET":
        st = get_pet_state()
        # Guarantee robot telemetry
        if "voltage" not in st or not st["voltage"]:
            st["voltage"] = round(3.60 + 0.60 * (st.get("energy", 80) / 100.0), 2)
        if "temperature" not in st or not st["temperature"]:
            st["temperature"] = 36.5
        if "charging" not in st:
            st["charging"] = 0
        if "fan_active" not in st:
            st["fan_active"] = 0
        if "firmware_version" not in st:
            st["firmware_version"] = "v1.0.4"
        return {"status": "ok", "state": st}

    elif endpoint in ("/api/care", "/api/charge", "/api/maintenance") and method == "POST":
        action = data.get("action", "feed")
        current_state = get_pet_state()
        res = apply_care_action(action, current_state)
        updates = res.get("updates", {})
        if "speech" in res:
            updates["speech"] = res["speech"]
        if "xp_gain" in res and res["xp_gain"] > 0:
            updates["xp"] = current_state.get("xp", 0) + res["xp_gain"]
            log_activity("experience", current_state["mode"], f"+{res['xp_gain']} XP from {action}", xp_gained=res["xp_gain"])

        current_state.update(updates)
        current_state["mood"] = evaluate_mood(current_state)
        update_pet_state(current_state)
        log_activity("care", current_state["mode"], f"Robot Care: {action.replace('_', ' ').title()}", res.get("speech", ""))

        app = get_active_device_app()
        if app:
            mood_reaction = "happy" if action in ("feed", "charge", "clean", "oil", "play") else ("sleepy" if action == "rest" else "excited")
            app.trigger_phone_reaction(mood_reaction, res.get("speech", ""))

        return {"status": "ok", "state": current_state, "speech": res.get("speech")}

    elif endpoint == "/api/minigame" and method == "POST":
        game = data.get("game", "wire_fixer")
        score = int(data.get("score", 100))
        current_state = get_pet_state()

        xp_gain = max(20, min(100, score // 2))
        happy_gain = 25
        energy_change = 10 if game == "wire_fixer" else -5

        current_state["happiness"] = min(100, current_state.get("happiness", 90) + happy_gain)
        if energy_change > 0:
            current_state["energy"] = min(100, current_state.get("energy", 80) + energy_change)
        current_state["xp"] = current_state.get("xp", 0) + xp_gain

        # Random maker parts drop
        import random
        available_parts = ["resistor", "led", "gear", "solder_wire", "timer_555", "copper_coil"]
        drop = random.choice(available_parts)
        drop_count = random.randint(1, 3)
        add_maker_part(drop, drop_count)

        current_state["speech"] = f"Minigame Win! +{xp_gain} XP & salvaged {drop_count}x {drop}!"
        update_pet_state(current_state)
        log_activity("game", current_state["mode"], f"Minigame: {game.replace('_', ' ').title()}", f"Scored {score} pts. Salvaged {drop_count}x {drop}", xp_gained=xp_gain)

        app = get_active_device_app()
        if app:
            app.trigger_phone_reaction("excited", current_state["speech"])

        return {
            "status": "ok",
            "state": current_state,
            "xp_gain": xp_gain,
            "drop": {"part_id": drop, "count": drop_count},
            "parts": get_maker_parts()
        }

    elif endpoint == "/api/craft" and method == "POST":
        recipe = data.get("recipe", "solder_wand")
        recipes = {
            "solder_wand": {
                "name": "Titanium Solder Wand",
                "req": {"copper_coil": 2, "resistor": 1},
                "xp": 80,
                "speech": "⚡ Crafted Titanium Solder Wand! Precision soldering active."
            },
            "worklight": {
                "name": "Dual LED Worklight",
                "req": {"led": 2, "solder_wire": 1},
                "xp": 60,
                "speech": "💡 Crafted Dual LED Worklight! Workshop brilliantly illuminated."
            },
            "turbine_fan": {
                "name": "Turbine Heatsink",
                "req": {"gear": 2, "timer_555": 1},
                "xp": 100,
                "speech": "🌀 Crafted Turbine Heatsink! Overheat throttle eliminated."
            },
            "pulse_clock": {
                "name": "555 Pulse Generator",
                "req": {"timer_555": 1, "resistor": 2},
                "xp": 75,
                "speech": "⏱️ Crafted 555 Pulse Generator! Precision timing clock."
            }
        }

        if recipe not in recipes:
            return {"status": "error", "message": f"Unknown recipe {recipe}"}

        rec = recipes[recipe]
        success = consume_maker_parts(rec["req"])
        if not success:
            return {"status": "error", "message": "Missing required parts in workshop inventory!"}

        current_state = get_pet_state()
        current_state["xp"] = current_state.get("xp", 0) + rec["xp"]
        current_state["happiness"] = min(100, current_state.get("happiness", 90) + 20)
        current_state["speech"] = rec["speech"]
        update_pet_state(current_state)
        log_activity("craft", current_state["mode"], f"Crafted {rec['name']}", f"+{rec['xp']} XP", xp_gained=rec["xp"])

        app = get_active_device_app()
        if app:
            app.trigger_phone_reaction("excited", current_state["speech"])

        return {
            "status": "ok",
            "state": current_state,
            "parts": get_maker_parts(),
            "crafted": rec["name"],
            "speech": rec["speech"]
        }

    elif endpoint == "/api/firmware" and method == "POST":
        current_state = get_pet_state()
        curr_level = current_state.get("level", 1)
        new_level = curr_level + 1
        versions = {
            1: "v1.0.4",
            2: "v1.2.0",
            3: "v2.0.0",
            4: "v2.5.0",
            5: "v3.0.0"
        }
        fw = versions.get(new_level, f"v{new_level}.0.0")
        current_state["level"] = new_level
        current_state["firmware_version"] = fw
        current_state["xp_next"] = int(current_state.get("xp_next", 100) * 1.5)
        current_state["speech"] = f"Firmware Flash Complete! Running {fw} 'Master Maker'."
        update_pet_state(current_state)
        log_activity("firmware", current_state["mode"], f"Flashed Firmware {fw}", f"Upgraded to Level {new_level}", xp_gained=100)

        app = get_active_device_app()
        if app:
            app.trigger_phone_reaction("excited", current_state["speech"])

        return {"status": "ok", "state": current_state, "firmware": fw}

    elif endpoint == "/api/command" and method == "POST":
        cmd = data.get("command", "solder")
        current_state = get_pet_state()
        app = get_active_device_app()

        speech_map = {
            "solder": ("soldering_circuit", "Solder flux ready! Working on the circuit board.", "excited"),
            "dance": ("music_dancing", "Cranking the workshop synth beats! Let's jam.", "excited"),
            "think": ("thinking_blueprint", "Analyzing schematics and drafting blueprints...", "happy"),
            "sleep": ("sleeping_hammock", "Powering down to sleep mode. Goodnight!", "sleepy"),
            "pet": ("celebrating", "*Happy servo purrs* Maker touch detected!", "happy")
        }

        if cmd in speech_map:
            act, sp, reaction = speech_map[cmd]
            current_state["activity"] = act
            current_state["speech"] = sp
            if cmd == "sleep":
                current_state["mode"] = "sleep"
            elif current_state.get("mode") == "sleep":
                current_state["mode"] = "auto"
            update_pet_state(current_state)
            log_activity("remote_command", current_state["mode"], f"Phone Command: {cmd.capitalize()}", sp)
            if app:
                app.trigger_phone_reaction(reaction, sp)

        return {"status": "ok", "state": current_state}

    elif endpoint == "/api/parts" and method == "GET":
        return {"status": "ok", "parts": get_maker_parts()}

    elif endpoint == "/api/mode" and method == "POST":
        mode = data.get("mode", "auto")
        current_state = get_pet_state()
        current_state["mode"] = mode
        current_state["mood"] = evaluate_mood(current_state)
        current_state["speech"] = get_contextual_speech(current_state["mood"], mode, current_state.get("activity", ""))
        update_pet_state(current_state)
        log_activity("mode_change", mode, f"Switched to {mode.capitalize()} via Phone")

        app = get_active_device_app()
        if app:
            app.trigger_phone_reaction(current_state["mood"], current_state["speech"])

        return {"status": "ok", "state": current_state}

    elif endpoint == "/api/missions" and method == "GET":
        return {"status": "ok", "missions": get_missions()}

    elif endpoint == "/api/inventory" and method == "GET":
        return {"status": "ok", "inventory": get_inventory()}

    elif endpoint == "/api/achievements" and method == "GET":
        return {"status": "ok", "achievements": get_achievements()}

    elif endpoint == "/api/diary" and method == "GET":
        return {"status": "ok", "diary": get_activity_history(30)}

    elif endpoint == "/api/backup" and method == "POST":
        backup_file = create_backup("phone_manual")
        return {"status": "ok", "backup_created": bool(backup_file), "filename": backup_file.name if backup_file else None}

    return {"status": "error", "message": f"Unknown endpoint {endpoint}"}

def run_standalone_server():
    """Runs a zero-dependency standard Python HTTP server for local Wi-Fi pairing."""
    from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
    import mimetypes

    web_root = BASE_DIR / "web"
    assets_root = BASE_DIR / "assets"

    class InstructaHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/api/device/screen.png"):
                from device_app import get_active_device_app, DeviceApp
                app = get_active_device_app()
                if not app:
                    app = DeviceApp()
                    app.run_frame()
                img_bytes = app.renderer.get_framebuffer_png_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(img_bytes)
                return

            if self.path.startswith("/api/"):
                endpoint = self.path.split("?")[0]
                resp = handle_api_request(endpoint, "GET")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode("utf-8"))
                return

            if self.path.startswith("/assets/"):
                rel_path = self.path[len("/assets/"):]
                fpath = assets_root / rel_path
                if fpath.exists() and fpath.is_file():
                    self.send_response(200)
                    mime, _ = mimetypes.guess_type(str(fpath))
                    self.send_header("Content-Type", mime or "application/octet-stream")
                    self.end_headers()
                    with open(fpath, "rb") as f:
                        self.wfile.write(f.read())
                    return

            # Route mapping
            if self.path == "/design-system":
                target_file = web_root / "templates" / "design_system.html"
            elif self.path == "/simulator":
                target_file = web_root / "templates" / "simulator.html"
            elif self.path == "/":
                target_file = web_root / "templates" / "index.html"
            else:
                target_file = web_root / self.path.lstrip("/")

            if target_file.exists():
                self.send_response(200)
                mime, _ = mimetypes.guess_type(str(target_file))
                self.send_header("Content-Type", mime or "text/html")
                self.end_headers()
                with open(target_file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File Not Found")

        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                data = json.loads(body)
            except Exception:
                data = {}

            endpoint = self.path.split("?")[0]
            resp = handle_api_request(endpoint, "POST", data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))

    server = ThreadingHTTPServer((WEB_HOST, WEB_PORT), InstructaHandler)
    print(f"Instructa-Gotchi Phone Companion running at http://{WEB_HOST}:{WEB_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Web companion shutting down...")

if __name__ == "__main__":
    run_standalone_server()

