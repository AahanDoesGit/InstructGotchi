"""
Instructa-Gotchi Native macOS Desktop Simulator
Opens a 2x scaled (480x640) native desktop window simulating the UNIHIKER M10 screen.
Supports mouse clicks as touchscreen taps and runs at 12 FPS.
"""
import sys
import time
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from device_app import DeviceApp

class MacSimulator:
    def __init__(self):
        self.device_app = DeviceApp()

        self.root = tk.Tk()
        self.root.title("UNIHIKER M10 Simulator (Instructa-Gotchi)")
        self.root.geometry("320x420")
        self.root.configure(bg="#242522")
        self.root.resizable(False, False)

        # Scale factor
        self.scale = 1.25
        self.sw = int(240 * self.scale)
        self.sh = int(320 * self.scale)

        # Cardboard robot frame container
        self.frame = tk.Frame(self.root, bg="#FFC928", bd=6, relief="ridge")
        self.frame.pack(pady=15)

        self.canvas = tk.Canvas(self.frame, width=self.sw, height=self.sh, bg="#242522", highlightthickness=0)
        self.canvas.pack()

        # Bind mouse click as touchscreen event
        self.canvas.bind("<Button-1>", self.on_click)

        self.tk_img = None
        self.update_loop()

    def on_click(self, event):
        """Translates Tkinter canvas coordinates into 240x320 UNIHIKER coordinates."""
        orig_x = int(event.x / self.scale)
        orig_y = int(event.y / self.scale)
        self.device_app.handle_touch(orig_x, orig_y)

    def update_loop(self):
        """12 FPS tick and render cycle."""
        self.device_app.run_frame()

        # Scale framebuffer for retina display
        fb = self.device_app.renderer.framebuffer.resize((self.sw, self.sh), Image.Resampling.BILINEAR)
        self.tk_img = ImageTk.PhotoImage(fb)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        # Paced at ~80ms (12 FPS)
        self.root.after(80, self.update_loop)

def main():
    sim = MacSimulator()
    sim.root.mainloop()

if __name__ == "__main__":
    main()

