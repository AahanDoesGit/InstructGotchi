"""
Instructa-Gotchi Unified Launcher
Runs both the UNIHIKER device application and phone companion web server.

Usage:
    python3 run.py            # Runs both device app and companion web server
    python3 run.py --device   # Runs UNIHIKER device app only
    python3 run.py --web      # Runs phone companion web server only
"""
import sys
import threading
import time
from device_app import DeviceApp
from web.routes import run_standalone_server

def run_device():
    app = DeviceApp()
    app.main_loop()

def run_web():
    run_standalone_server()

def main():
    args = sys.argv[1:]

    if "--web" in args:
        run_web()
    elif "--device" in args:
        run_device()
    else:
        print("Launching Instructa-Gotchi (UNIHIKER M10 Device App + Phone Web Companion)...")
        web_thread = threading.Thread(target=run_web, daemon=True)
        web_thread.start()

        # Run device app in foreground thread
        time.sleep(0.5)
        run_device()

if __name__ == "__main__":
    main()

