"""
Instructa-Gotchi UNIHIKER M10 Device Application
Dedicated pure character living screen on the 2.8" (240x320) portrait display.
Shows ONLY the character living, animating, and working inside its workshop.
No menus, no HUD, no buttons, no text clutter.
All feature controls, care buttons, detailed stats, and missions live in the Phone Web UI.
"""
import time
import os
from pathlib import Path
from core.pet_state import PetStateManager
from core.animation_controller import AnimationController
from display.renderer import ScreenRenderer
from display.living_screen import LivingScreenManager
from typing import Optional

active_device_app: Optional['DeviceApp'] = None

def get_active_device_app() -> Optional['DeviceApp']:
    global active_device_app
    return active_device_app

class DeviceApp:
    def __init__(self):
        global active_device_app
        active_device_app = self

        self.renderer = ScreenRenderer()
        self.pet_manager = PetStateManager()
        self.anim = AnimationController()
        self.living_screen = LivingScreenManager(self.renderer, self.pet_manager, self.anim)

        self.is_running = True
        self.boot_duration = 1.5  # seconds
        self.start_time = time.time()
        self.is_booted = False

    def handle_touch(self, x: int, y: int):
        """Translates physical touchscreen tap on UNIHIKER into pet interaction."""
        self.renderer.handle_touch_event(x, y)
        self.run_frame()

    def trigger_phone_reaction(self, mood: str, speech: str = ""):
        """Called when user executes a care action or switches mode from their phone."""
        self.living_screen.trigger_reaction(mood, speech)

    def run_frame(self):
        """Single 12 FPS render cycle for the 240x320 screen."""
        state = self.pet_manager.tick()

        # Render the pure living character in its workshop (Zero text, Zero UI clutter)
        # Directly alive and working from frame 0
        self.living_screen.render_living_workshop(state)

    def main_loop(self):
        """Main loop targeting 12 FPS."""
        print("Starting Instructa-Gotchi Pure Living Screen on UNIHIKER M10 (240x320)...")
        try:
            while self.is_running:
                loop_start = time.time()
                self.run_frame()
                elapsed = time.time() - loop_start
                sleep_time = max(0.01, (1.0 / 12.0) - elapsed)
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("Instructa-Gotchi Device App gracefully stopping...")

def main():
    app = DeviceApp()
    app.main_loop()

if __name__ == "__main__":
    main()
