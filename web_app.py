"""
Instructa-Gotchi Web Companion Entry Point
Starts the companion web server on the local Wi-Fi interface.
"""
from web.routes import run_standalone_server

if __name__ == "__main__":
    run_standalone_server()

