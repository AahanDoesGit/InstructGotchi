"""
Instructa-Gotchi Asset Generator
Renders the design system, master character, 15 expressions, animation frames,
environments, and UI icons directly into assets/ with pixel precision.
"""
import os
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

# Colors from design tokens
C_CREAM = (245, 240, 230)
C_IVORY = (255, 249, 239)
C_GRAPHITE = (36, 37, 34)
C_DEEP_INK = (48, 45, 40)
C_MAKER_YELLOW = (255, 201, 40)
C_MAKER_YELLOW_SHADOW = (220, 160, 20)
C_SIGNAL_ORANGE = (242, 139, 36)
C_WARM_CORAL = (237, 115, 92)
C_WORKSHOP_GREEN = (131, 169, 120)
C_MUTED_STEEL = (135, 144, 153)
C_ELECTRIC_CYAN = (56, 189, 248)
C_LIGHT_BLUE = (186, 230, 253)
C_WHITE = (255, 255, 255)
C_WOOD_BROWN = (160, 110, 60)
C_DARK_WOOD = (110, 75, 40)

def create_master_character(expression="idle", frame=0, size=(140, 140)):
    """
    Renders the master character model with the requested facial expression and micro-motion.
    Returns an RGBA PIL Image.
    """
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size[0] // 2, size[1] // 2 + 6
    # Subtle idle breathing vertical bob
    bob = int(math.sin(frame * math.pi / 2) * 2) if frame > 0 else 0
    cy += bob

    # 1. Shadow underneath
    draw.ellipse([cx - 36, cy + 50, cx + 36, cy + 60], fill=(0, 0, 0, 45))

    # 2. Short legs and articulated feet
    draw.rounded_rectangle([cx - 24, cy + 32, cx - 10, cy + 52], radius=4, fill=C_MUTED_STEEL)
    draw.rounded_rectangle([cx + 10, cy + 32, cx + 24, cy + 52], radius=4, fill=C_MUTED_STEEL)
    draw.rounded_rectangle([cx - 28, cy + 48, cx - 8, cy + 56], radius=4, fill=C_GRAPHITE)
    draw.rounded_rectangle([cx + 8, cy + 48, cx + 28, cy + 56], radius=4, fill=C_GRAPHITE)

    # 3. Main Torso (Maker Yellow with bevels)
    draw.rounded_rectangle([cx - 32, cy + 2, cx + 32, cy + 38], radius=10, fill=C_MAKER_YELLOW_SHADOW)
    draw.rounded_rectangle([cx - 30, cy + 2, cx + 30, cy + 36], radius=9, fill=C_MAKER_YELLOW)

    # Chest Gear Detail
    draw.ellipse([cx - 14, cy + 10, cx + 14, cy + 30], fill=C_SIGNAL_ORANGE)
    draw.ellipse([cx - 10, cy + 14, cx + 10, cy + 26], fill=C_GRAPHITE)
    # Gear teeth
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        gx = cx + int(12 * math.cos(rad))
        gy = cy + 20 + int(12 * math.sin(rad))
        draw.rectangle([gx - 2, gy - 2, gx + 2, gy + 2], fill=C_SIGNAL_ORANGE)
    # Core glowing power LED
    draw.ellipse([cx - 4, cy + 16, cx + 4, cy + 24], fill=C_ELECTRIC_CYAN)

    # Tool belt
    draw.rectangle([cx - 30, cy + 32, cx + 30, cy + 38], fill=C_DARK_WOOD)
    draw.rectangle([cx - 6, cy + 31, cx + 6, cy + 39], fill=C_MAKER_YELLOW)
    draw.rectangle([cx - 3, cy + 33, cx + 3, cy + 37], fill=C_GRAPHITE)

    # 4. Arms
    if expression == "celebrating":
        # Arms raised in victory
        draw.line([cx - 30, cy + 15, cx - 44, cy - 8], fill=C_MUTED_STEEL, width=7)
        draw.ellipse([cx - 48, cy - 14, cx - 38, cy - 4], fill=C_SIGNAL_ORANGE)
        draw.line([cx + 30, cy + 15, cx + 44, cy - 8], fill=C_MUTED_STEEL, width=7)
        draw.ellipse([cx + 38, cy - 14, cx + 48, cy - 4], fill=C_SIGNAL_ORANGE)
        # Small wrench in right hand
        draw.line([cx + 43, cy - 10, cx + 55, cy - 24], fill=C_MUTED_STEEL, width=4)
        draw.arc([cx + 50, cy - 30, cx + 62, cy - 18], 45, 315, fill=C_MUTED_STEEL, width=3)
    elif expression == "thinking":
        # Left arm on hip, right hand at chin
        draw.line([cx - 30, cy + 15, cx - 42, cy + 30], fill=C_MUTED_STEEL, width=7)
        draw.ellipse([cx - 46, cy + 26, cx - 36, cy + 36], fill=C_SIGNAL_ORANGE)
        draw.line([cx + 30, cy + 15, cx + 22, cy - 2], fill=C_MUTED_STEEL, width=7)
        draw.ellipse([cx + 16, cy - 8, cx + 26, cy + 2], fill=C_SIGNAL_ORANGE)
    else:
        # Relaxed / idle arms
        draw.line([cx - 30, cy + 15, cx - 44, cy + 28], fill=C_MUTED_STEEL, width=7)
        draw.ellipse([cx - 48, cy + 24, cx - 38, cy + 34], fill=C_SIGNAL_ORANGE)
        draw.line([cx + 30, cy + 15, cx + 44, cy + 28], fill=C_MUTED_STEEL, width=7)
        draw.ellipse([cx + 38, cy + 24, cx + 48, cy + 34], fill=C_SIGNAL_ORANGE)

    # 5. Antenna and Maker Bulb
    draw.line([cx, cy - 40, cx, cy - 54], fill=C_MUTED_STEEL, width=5)
    # Orb color varies slightly by mood
    orb_color = C_WARM_CORAL if expression == "frustrated" else (C_WORKSHOP_GREEN if expression in ("proud", "happy", "celebrating") else C_ELECTRIC_CYAN)
    draw.ellipse([cx - 7, cy - 64, cx + 7, cy - 50], fill=orb_color)
    draw.ellipse([cx - 3, cy - 62, cx + 1, cy - 58], fill=C_WHITE)

    # 6. Head (Compact rounded rectangle)
    head_left, head_top, head_right, head_bottom = cx - 42, cy - 44, cx + 42, cy + 2
    # Ear bolts
    draw.rectangle([head_left - 5, cy - 26, head_left, cy - 14], fill=C_MUTED_STEEL)
    draw.rectangle([head_right, cy - 26, head_right + 5, cy - 14], fill=C_MUTED_STEEL)
    # Outer head shell
    draw.rounded_rectangle([head_left, head_top, head_right, head_bottom], radius=14, fill=C_MAKER_YELLOW_SHADOW)
    draw.rounded_rectangle([head_left + 2, head_top + 2, head_right - 2, head_bottom - 2], radius=13, fill=C_MAKER_YELLOW)
    # Top head highlight
    draw.rounded_rectangle([head_left + 8, head_top + 4, head_right - 8, head_top + 10], radius=3, fill=C_WHITE)

    # 7. Dark Visor Screen (Graphite Face Plate)
    visor_left, visor_top, visor_right, visor_bottom = cx - 34, cy - 36, cx + 34, cy - 4
    draw.rounded_rectangle([visor_left, visor_top, visor_right, visor_bottom], radius=8, fill=C_GRAPHITE)

    # 8. Render Facial Expression inside Visor
    draw_expression(draw, expression, cx, cy - 20)

    return img

def draw_expression(draw, expression, fx, fy):
    """Draws expressive eyes and mouth inside the visor screen centered at (fx, fy)."""
    left_eye_cx, right_eye_cx = fx - 16, fx + 16

    if expression == "idle":
        # Friendly round eyes
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.ellipse([ecx - 8, fy - 8, ecx + 8, fy + 6], fill=C_ELECTRIC_CYAN)
            draw.ellipse([ecx - 4, fy - 6, ecx + 1, fy - 1], fill=C_WHITE)
        # Small smile
        draw.arc([fx - 6, fy, fx + 6, fy + 8], 20, 160, fill=C_WHITE, width=2)

    elif expression == "happy":
        # Upward curved joyous arches
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.arc([ecx - 8, fy - 6, ecx + 8, fy + 6], 190, 350, fill=C_ELECTRIC_CYAN, width=3)
        # Open mouth
        draw.chord([fx - 8, fy + 1, fx + 8, fy + 9], 0, 180, fill=C_WARM_CORAL)

    elif expression == "excited":
        # Star / sparkle eyes
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.line([ecx, fy - 9, ecx, fy + 7], fill=C_ELECTRIC_CYAN, width=3)
            draw.line([ecx - 8, fy - 1, ecx + 8, fy - 1], fill=C_ELECTRIC_CYAN, width=3)
            draw.ellipse([ecx - 3, fy - 4, ecx + 3, fy + 2], fill=C_WHITE)
        draw.chord([fx - 10, fy + 1, fx + 10, fy + 10], 0, 180, fill=C_MAKER_YELLOW)

    elif expression == "curious":
        # Asymmetrical eyes (one raised, one squinting)
        draw.ellipse([left_eye_cx - 9, fy - 10, left_eye_cx + 9, fy + 6], fill=C_ELECTRIC_CYAN)
        draw.ellipse([left_eye_cx - 4, fy - 7, left_eye_cx + 1, fy - 2], fill=C_WHITE)
        draw.ellipse([right_eye_cx - 7, fy - 5, right_eye_cx + 7, fy + 5], fill=C_ELECTRIC_CYAN)
        draw.arc([fx - 6, fy + 2, fx + 6, fy + 8], 30, 150, fill=C_WHITE, width=2)
        # Raised brow tick
        draw.line([left_eye_cx - 6, fy - 12, left_eye_cx + 6, fy - 14], fill=C_ELECTRIC_CYAN, width=2)

    elif expression == "surprised":
        # Big wide round 'O' eyes & mouth
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.ellipse([ecx - 9, fy - 9, ecx + 9, fy + 7], fill=C_ELECTRIC_CYAN)
            draw.ellipse([ecx - 4, fy - 6, ecx + 2, fy], fill=C_WHITE)
        draw.ellipse([fx - 4, fy + 2, fx + 4, fy + 9], fill=C_WHITE)

    elif expression == "bored":
        # Half-closed droopy eyes
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.ellipse([ecx - 8, fy - 4, ecx + 8, fy + 6], fill=C_ELECTRIC_CYAN)
            draw.rectangle([ecx - 9, fy - 8, ecx + 9, fy], fill=C_GRAPHITE)
        draw.line([fx - 7, fy + 5, fx + 7, fy + 5], fill=C_WHITE, width=2)

    elif expression == "sleepy":
        # Closed sleepy lines
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.arc([ecx - 7, fy - 2, ecx + 7, fy + 6], 20, 160, fill=C_ELECTRIC_CYAN, width=3)
        draw.arc([fx - 4, fy + 3, fx + 4, fy + 7], 20, 160, fill=C_WHITE, width=2)

    elif expression == "frustrated":
        # Angled angry brows
        draw.line([left_eye_cx - 7, fy - 7, left_eye_cx + 7, fy - 1], fill=C_WARM_CORAL, width=3)
        draw.ellipse([left_eye_cx - 6, fy - 2, left_eye_cx + 6, fy + 6], fill=C_WARM_CORAL)
        draw.line([right_eye_cx + 7, fy - 7, right_eye_cx - 7, fy - 1], fill=C_WARM_CORAL, width=3)
        draw.ellipse([right_eye_cx - 6, fy - 2, right_eye_cx + 6, fy + 6], fill=C_WARM_CORAL)
        # Zigzag mouth
        draw.line([(fx - 7, fy + 6), (fx - 3, fy + 4), (fx + 2, fy + 7), (fx + 7, fy + 5)], fill=C_WHITE, width=2)

    elif expression == "proud":
        # Confident closed happy lines
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.arc([ecx - 8, fy - 5, ecx + 8, fy + 5], 190, 350, fill=C_WORKSHOP_GREEN, width=3)
        # Confident smirk
        draw.arc([fx - 6, fy, fx + 8, fy + 7], 10, 150, fill=C_WHITE, width=2)

    elif expression == "thinking":
        # Eyes looking upwards to the right
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.ellipse([ecx - 7, fy - 7, ecx + 7, fy + 5], fill=C_ELECTRIC_CYAN)
            draw.ellipse([ecx + 1, fy - 6, ecx + 5, fy - 2], fill=C_WHITE)
        draw.line([fx - 4, fy + 5, fx + 5, fy + 4], fill=C_WHITE, width=2)

    elif expression == "sad":
        # Drooping sad eyes & small tear
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.ellipse([ecx - 7, fy - 5, ecx + 7, fy + 6], fill=C_ELECTRIC_CYAN)
            draw.rectangle([ecx - 8, fy - 8, ecx + 8, fy - 1], fill=C_GRAPHITE)
        draw.arc([fx - 6, fy + 5, fx + 6, fy + 12], 200, 340, fill=C_WHITE, width=2)
        # Blue teardrop
        draw.ellipse([right_eye_cx + 8, fy + 3, right_eye_cx + 12, fy + 8], fill=C_ELECTRIC_CYAN)

    elif expression == "focused":
        # Focused horizontal slits
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.rectangle([ecx - 8, fy - 2, ecx + 8, fy + 4], fill=C_ELECTRIC_CYAN)
            draw.rectangle([ecx - 2, fy - 1, ecx + 2, fy + 3], fill=C_WHITE)
        draw.line([fx - 6, fy + 6, fx + 6, fy + 6], fill=C_WHITE, width=2)

    elif expression == "laughing":
        # > < double-closed laugh
        draw.line([left_eye_cx - 7, fy - 5, left_eye_cx + 6, fy], fill=C_MAKER_YELLOW, width=3)
        draw.line([left_eye_cx - 7, fy + 5, left_eye_cx + 6, fy], fill=C_MAKER_YELLOW, width=3)
        draw.line([right_eye_cx + 7, fy - 5, right_eye_cx - 6, fy], fill=C_MAKER_YELLOW, width=3)
        draw.line([right_eye_cx + 7, fy + 5, right_eye_cx - 6, fy], fill=C_MAKER_YELLOW, width=3)
        draw.chord([fx - 8, fy + 1, fx + 8, fy + 9], 0, 180, fill=C_WARM_CORAL)

    elif expression == "confused":
        # Asymmetrical swirly pupil
        draw.ellipse([left_eye_cx - 8, fy - 7, left_eye_cx + 8, fy + 6], fill=C_ELECTRIC_CYAN)
        draw.line([left_eye_cx - 3, fy - 1, left_eye_cx + 3, fy - 1], fill=C_GRAPHITE, width=2)
        draw.ellipse([right_eye_cx - 6, fy - 5, right_eye_cx + 6, fy + 5], fill=C_ELECTRIC_CYAN)
        # Squiggly mouth
        draw.line([(fx - 7, fy + 5), (fx - 2, fy + 3), (fx + 3, fy + 7), (fx + 7, fy + 4)], fill=C_WHITE, width=2)

    elif expression == "celebrating":
        # Glowing party eyes
        for ecx in [left_eye_cx, right_eye_cx]:
            draw.arc([ecx - 8, fy - 6, ecx + 8, fy + 6], 190, 350, fill=C_ELECTRIC_CYAN, width=4)
        draw.chord([fx - 9, fy + 1, fx + 9, fy + 10], 0, 180, fill=C_MAKER_YELLOW)

def generate_workshop_background(mode="default", size=(240, 320)):
    """Generates 240x320 portrait workshop backgrounds."""
    img = Image.new("RGBA", size)
    draw = ImageDraw.Draw(img)
    w, h = size

    if mode == "night":
        # Darkened night workshop
        for y in range(h):
            ratio = y / h
            r = int(24 * (1 - ratio) + 16 * ratio)
            g = int(28 * (1 - ratio) + 20 * ratio)
            b = int(36 * (1 - ratio) + 26 * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
        # Night lamp glow
        draw.ellipse([w // 2 - 50, 100, w // 2 + 50, 200], fill=(40, 55, 75, 70))
        # Dim workbench
        draw.rectangle([0, 220, w, h], fill=(30, 32, 38))
        draw.line([0, 220, w, 220], fill=(55, 60, 70), width=2)

    elif mode == "focus":
        # Clean minimalist zen workshop
        for y in range(h):
            ratio = y / h
            r = int(32 * (1 - ratio) + 24 * ratio)
            g = int(35 * (1 - ratio) + 26 * ratio)
            b = int(42 * (1 - ratio) + 30 * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
        # Minimalist measurement grid
        for gy in range(40, 220, 24):
            draw.line([(0, gy), (w, gy)], fill=(45, 50, 60, 80), width=1)
        for gx in range(0, w, 24):
            draw.line([(gx, 40), (gx, 220)], fill=(45, 50, 60, 80), width=1)
        # Bench top
        draw.rectangle([0, 220, w, h], fill=(40, 44, 52))
        draw.line([0, 220, w, 220], fill=C_SIGNAL_ORANGE, width=2)

    elif mode == "music":
        # Vibrant rhythm workshop with equalizer glow
        for y in range(h):
            ratio = y / h
            r = int(30 * (1 - ratio) + 20 * ratio)
            g = int(25 * (1 - ratio) + 35 * ratio)
            b = int(45 * (1 - ratio) + 55 * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
        # Equalizer bars in background
        bar_x = 24
        for bar_h in [25, 45, 70, 95, 60, 80, 40, 65, 30]:
            draw.rectangle([bar_x, 215 - bar_h, bar_x + 12, 215], fill=(56, 189, 248, 60))
            draw.rectangle([bar_x, 215 - bar_h, bar_x + 12, 215 - bar_h + 4], fill=C_ELECTRIC_CYAN)
            bar_x += 22
        draw.rectangle([0, 220, w, h], fill=(28, 30, 42))
        draw.line([0, 220, w, 220], fill=C_ELECTRIC_CYAN, width=2)

    else:
        # Default warm maker workshop
        # 1. Warm cream wall gradient
        for y in range(220):
            ratio = y / 220
            r = int(245 * (1 - ratio) + 235 * ratio)
            g = int(240 * (1 - ratio) + 228 * ratio)
            b = int(230 * (1 - ratio) + 215 * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

        # 2. Pegboard holes on back wall
        for py in range(50, 170, 16):
            for px in range(16, w - 16, 16):
                draw.point((px, py), fill=(210, 200, 185))

        # 3. Pegboard tool silhouettes
        # Wrench silhouette
        draw.line([30, 70, 30, 110], fill=(195, 185, 170), width=4)
        draw.ellipse([26, 64, 34, 72], fill=(195, 185, 170))
        # Screwdriver silhouette
        draw.line([50, 75, 50, 115], fill=(195, 185, 170), width=3)
        draw.rectangle([48, 105, 52, 120], fill=(195, 185, 170))

        # 4. Blueprint paper on workbench
        draw.rectangle([140, 212, 224, 230], fill=(59, 130, 246, 180))
        draw.line([144, 216, 220, 216], fill=C_WHITE, width=1)
        draw.line([144, 220, 210, 220], fill=C_WHITE, width=1)

        # 5. Warm wooden workbench
        draw.rectangle([0, 220, w, h], fill=C_WOOD_BROWN)
        draw.line([0, 220, w, 220], fill=C_DARK_WOOD, width=3)
        draw.line([0, 223, w, 223], fill=(200, 145, 85), width=2)
        # Wood grain lines
        draw.line([0, 240, w, 240], fill=C_DARK_WOOD, width=1)
        draw.line([0, 270, w, 270], fill=C_DARK_WOOD, width=1)

    return img

def generate_icons():
    """Generates crisp 32x32 UI and mode icons."""
    icons = {}

    def new_ico():
        return Image.new("RGBA", (32, 32), (0, 0, 0, 0))

    # mode_auto (Cog with lightning / A)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_SIGNAL_ORANGE)
    d.ellipse([10, 10, 22, 22], fill=C_GRAPHITE)
    d.polygon([(16, 8), (12, 22), (18, 14), (20, 22)], fill=C_WHITE)
    icons["mode_auto"] = im

    # mode_workshop (Wrench & Hammer cross)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_MAKER_YELLOW)
    d.line([8, 8, 24, 24], fill=C_GRAPHITE, width=4)
    d.line([8, 24, 24, 8], fill=C_GRAPHITE, width=4)
    icons["mode_workshop"] = im

    # mode_music (Headphones / Note)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_ELECTRIC_CYAN)
    d.arc([8, 8, 24, 24], 180, 360, fill=C_GRAPHITE, width=3)
    d.rectangle([7, 16, 11, 24], fill=C_GRAPHITE)
    d.rectangle([21, 16, 25, 24], fill=C_GRAPHITE)
    icons["mode_music"] = im

    # mode_game (Gamepad)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_WARM_CORAL)
    d.rounded_rectangle([7, 12, 25, 22], radius=4, fill=C_WHITE)
    # D-pad cross & button dots
    d.line([10, 17, 14, 17], fill=C_GRAPHITE, width=2)
    d.line([12, 15, 12, 19], fill=C_GRAPHITE, width=2)
    d.ellipse([19, 14, 21, 16], fill=C_WARM_CORAL)
    d.ellipse([21, 17, 23, 19], fill=C_WARM_CORAL)
    icons["mode_game"] = im

    # mode_study (Open Book / Lightbulb)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_WORKSHOP_GREEN)
    d.polygon([(8, 12), (16, 15), (24, 12), (24, 24), (16, 22), (8, 24)], fill=C_WHITE)
    d.line([16, 15, 16, 22], fill=C_GRAPHITE, width=2)
    icons["mode_study"] = im

    # mode_focus (Timer / Clock)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_MUTED_STEEL)
    d.ellipse([6, 6, 26, 26], fill=C_WHITE)
    d.line([16, 16, 16, 10], fill=C_GRAPHITE, width=2)
    d.line([16, 16, 21, 16], fill=C_GRAPHITE, width=2)
    icons["mode_focus"] = im

    # mode_companion (Heart)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_WARM_CORAL)
    d.polygon([(16, 24), (8, 15), (12, 9), (16, 13), (20, 9), (24, 15)], fill=C_WHITE)
    icons["mode_companion"] = im

    # mode_sleep (Moon and Zzz)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_GRAPHITE)
    d.ellipse([8, 8, 24, 24], fill=C_MAKER_YELLOW)
    d.ellipse([12, 6, 26, 22], fill=C_GRAPHITE)
    icons["mode_sleep"] = im

    # Care: Hunger (Energy Battery / Meal)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([7, 9, 23, 23], radius=3, fill=C_SIGNAL_ORANGE)
    d.rectangle([23, 13, 26, 19], fill=C_SIGNAL_ORANGE)
    d.rectangle([10, 12, 20, 20], fill=C_WHITE)
    icons["care_hunger"] = im

    # Care: Happiness (Sparkle Smiley)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([5, 5, 27, 27], fill=C_MAKER_YELLOW)
    d.ellipse([10, 11, 13, 14], fill=C_GRAPHITE)
    d.ellipse([19, 11, 22, 14], fill=C_GRAPHITE)
    d.arc([11, 14, 21, 22], 20, 160, fill=C_GRAPHITE, width=2)
    icons["care_happiness"] = im

    # Care: Energy (Lightning Bolt)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_ELECTRIC_CYAN)
    d.polygon([(17, 7), (10, 17), (15, 17), (14, 25), (22, 15), (17, 15)], fill=C_WHITE)
    icons["care_energy"] = im

    # Care: Cleanliness (Water Droplet / Sparkle)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_WORKSHOP_GREEN)
    d.polygon([(16, 7), (9, 21), (13, 25), (19, 25), (23, 21)], fill=C_WHITE)
    icons["care_clean"] = im

    # Care: Health (Shield with Cross)
    im = new_ico()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 28, 28], fill=C_WARM_CORAL)
    d.polygon([(16, 7), (8, 11), (8, 19), (16, 26), (24, 19), (24, 11)], fill=C_WHITE)
    d.line([16, 12, 16, 21], fill=C_WARM_CORAL, width=2)
    d.line([12, 16, 20, 16], fill=C_WARM_CORAL, width=2)
    icons["care_health"] = im

    return icons

def main():
    print("Generating Instructa-Gotchi master design system & character assets...")

    expressions = [
        "idle", "happy", "excited", "curious", "surprised", "bored",
        "sleepy", "frustrated", "proud", "thinking", "sad", "focused",
        "laughing", "confused", "celebrating"
    ]

    manifest = {
        "project": "Instructa-Gotchi",
        "version": "1.0.0",
        "categories": {
            "characters": [],
            "expressions": [],
            "animations": [],
            "backgrounds": [],
            "icons": []
        }
    }

    # 1. Master Character & Expressions
    for expr in expressions:
        char_img = create_master_character(expression=expr, frame=0)
        out_path = ASSETS_DIR / "expressions" / f"{expr}.png"
        char_img.save(out_path, "PNG")
        manifest["categories"]["expressions"].append({
            "name": expr,
            "path": f"assets/expressions/{expr}.png",
            "size": [140, 140],
            "format": "RGBA PNG"
        })

    # Master base model
    master_img = create_master_character(expression="idle", frame=0)
    master_img.save(ASSETS_DIR / "characters" / "master_character.png", "PNG")
    manifest["categories"]["characters"].append({
        "name": "master_character",
        "path": "assets/characters/master_character.png",
        "size": [140, 140],
        "format": "RGBA PNG"
    })

    # 2. Idle Animation Frames (4 frames breathing loop)
    for frame_idx in range(4):
        anim_img = create_master_character(expression="idle", frame=frame_idx)
        out_path = ASSETS_DIR / "animations" / f"idle_{frame_idx}.png"
        anim_img.save(out_path, "PNG")
        manifest["categories"]["animations"].append({
            "sequence": "idle",
            "frame": frame_idx,
            "path": f"assets/animations/idle_{frame_idx}.png",
            "size": [140, 140]
        })

    # 3. Workshop Backgrounds (240x320)
    bg_modes = ["default", "night", "focus", "music"]
    for bg_mode in bg_modes:
        bg_img = generate_workshop_background(mode=bg_mode)
        out_path = ASSETS_DIR / "backgrounds" / f"workshop_{bg_mode}.png"
        bg_img.save(out_path, "PNG")
        manifest["categories"]["backgrounds"].append({
            "name": f"workshop_{bg_mode}",
            "path": f"assets/backgrounds/workshop_{bg_mode}.png",
            "size": [240, 320],
            "format": "RGBA PNG"
        })

    # 4. Icons
    icons = generate_icons()
    for name, icon_img in icons.items():
        out_path = ASSETS_DIR / "icons" / f"{name}.png"
        icon_img.save(out_path, "PNG")
        manifest["categories"]["icons"].append({
            "name": name,
            "path": f"assets/icons/{name}.png",
            "size": [32, 32],
            "format": "RGBA PNG"
        })

    # Write manifest.json
    with open(ASSETS_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(expressions)} expressions, 4 idle animation frames, 4 backgrounds, and {len(icons)} UI icons.")

if __name__ == "__main__":
    main()

