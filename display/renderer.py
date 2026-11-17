"""
Instructa-Gotchi Display Renderer
Provides a high-level UI rendering pipeline for the 240x320 portrait screen.
Gracefully binds to the official UNIHIKER `GUI` library if available,
or operates via a headless Pillow/framebuffer buffer for development and testing.
"""
import os
import io
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
from config.settings import DISPLAY_WIDTH, DISPLAY_HEIGHT, TOKENS, ASSETS_DIR

# Check for hardware unihiker GUI
try:
    from unihiker import GUI as UnihikerGUI
    HAS_UNIHIKER_GUI = True
except ImportError:
    HAS_UNIHIKER_GUI = False

class ScreenRenderer:
    def __init__(self):
        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        self.use_hardware = HAS_UNIHIKER_GUI
        self.touch_handlers: List[Dict[str, Any]] = []
        self._hw_image_widget = None

        if self.use_hardware:
            try:
                self.gui = UnihikerGUI()
                print("Attached to UNIHIKER hardware display.")
            except Exception as e:
                print(f"Failed to initialize UNIHIKER GUI hardware: {e}. Switching to software buffer.")
                self.use_hardware = False

        # Virtual software buffer
        self.framebuffer = Image.new("RGBA", (self.width, self.height), (245, 240, 230, 255))
        self.draw = ImageDraw.Draw(self.framebuffer)

    def clear(self, color=(245, 240, 230)):
        """Clears the display buffer."""
        self.touch_handlers.clear()
        if self.use_hardware:
            try:
                self.gui.clear()
            except Exception:
                pass
        self.framebuffer = Image.new("RGBA", (self.width, self.height), (*color, 255))
        self.draw = ImageDraw.Draw(self.framebuffer)

    def draw_image(self, x: int, y: int, image_path: Path, width: Optional[int] = None, height: Optional[int] = None):
        """Draws an image onto the screen, updating the hardware widget cleanly to prevent memory leaks."""
        if not image_path.exists():
            return
        if self.use_hardware:
            try:
                if self._hw_image_widget is not None:
                    self._hw_image_widget.config(image=str(image_path))
                else:
                    self._hw_image_widget = self.gui.draw_image(x=x, y=y, w=width or 0, h=height or 0, image=str(image_path))
            except Exception:
                try:
                    self._hw_image_widget = self.gui.draw_image(x=x, y=y, w=width or 0, h=height or 0, image=str(image_path))
                except Exception:
                    pass
        # Blend onto software buffer
        try:
            img = Image.open(str(image_path)).convert("RGBA")
            if width and height:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            self.framebuffer.paste(img, (x, y), img)
        except Exception:
            pass

    def draw_text(self, x: int, y: int, text: str, size: int = 12, color: str = "#242522"):
        """Renders text with the specified size and color."""
        if self.use_hardware:
            try:
                self.gui.draw_text(x=x, y=y, text=text, font_size=size, color=color)
            except Exception:
                pass
        # Pillow buffer drawing
        try:
            self.draw.text((x, y), text, fill=color)
        except Exception:
            pass

    def draw_rect(self, x: int, y: int, w: int, h: int, fill: str, radius: int = 0):
        """Draws a solid or rounded rectangle."""
        if radius > 0:
            self.draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill)
        else:
            self.draw.rectangle([x, y, x + w, y + h], fill=fill)

    def register_touch_target(self, x: int, y: int, w: int, h: int, callback: Callable):
        """Registers a touch hitbox."""
        self.touch_handlers.append({
            "bounds": (x, y, x + w, y + h),
            "callback": callback
        })
        if self.use_hardware:
            try:
                self.gui.on_click(x, y, w, h, callback)
            except Exception:
                pass

    def handle_touch_event(self, tx: int, ty: int):
        """Dispatches touch coordinate to registered hitboxes."""
        for handler in reversed(self.touch_handlers):
            x1, y1, x2, y2 = handler["bounds"]
            if x1 <= tx <= x2 and y1 <= ty <= y2:
                handler["callback"]()
                return

    def save_debug_screenshot(self, output_path: Path):
        """Saves current virtual framebuffer to disk."""
        self.framebuffer.save(output_path, "PNG")

    def get_framebuffer_png_bytes(self) -> bytes:
        """Returns PNG image bytes of the current screen for web streaming."""
        buf = io.BytesIO()
        self.framebuffer.save(buf, format="PNG")
        return buf.getvalue()

