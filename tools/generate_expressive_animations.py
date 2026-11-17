"""
Generates highly expressive, fluid multi-frame animations for Instructa-Gotchi:
- music_dancing: Hands waving, head bobbing/tilting to the beat, floating rhythm notes
- working_soldering: Hand lifting and pressing soldering iron, flickering sparks, rising smoke, head tilting
- celebrating: Alternating waving hands, hopping body, bursting maker stars
- thinking: Finger tapping chin, head tilting, idea bulb pulsing brightly with rays
- sleeping: Inhale/exhale chest breathing, floating rising Zzz
"""
import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

TARGET_W, TARGET_H = 240, 320
BRAIN_DIR = Path("/Users/mac/.gemini/antigravity/brain/bf242ffa-5dc1-49f2-b9a5-ff05896a8eb0")
ANIM_DIR = Path("/Users/mac/Downloads/InstructaGotchi_Full_Context/doc/instructgotchi/assets/animations")

def load_crop_base(img_path):
    img = Image.open(img_path)
    w, h = img.size
    ratio = TARGET_W / TARGET_H
    if (w / h) > ratio:
        nw = int(h * ratio)
        left = (w - nw) // 2
        cropped = img.crop((left, 0, left + nw, h))
    else:
        nh = int(w / ratio)
        top = (h - nh) // 2
        cropped = img.crop((0, top, w, top + nh))
    return cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)

def create_feathered_mask(w, h, border=10):
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([border, border, w - border, h - border], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(border // 2))

# ==============================================================================
# 1. MUSIC DANCING ANIMATION (4 Frames - True Groove, Waving Hand, Head Tilting)
# ==============================================================================
def make_music_dancing():
    out_dir = ANIM_DIR / "music_dancing"
    out_dir.mkdir(parents=True, exist_ok=True)
    base = load_crop_base(BRAIN_DIR / "tinko_workshop_dancing_1794899081340.jpg")

    # Crop Left Arm/Hand (the peace/groove hand: x: 30-75, y: 120-180)
    lx0, ly0, lx1, ly1 = 30, 115, 75, 185
    left_arm = base.crop((lx0, ly0, lx1, ly1))
    lmask = create_feathered_mask(lx1 - lx0, ly1 - ly0, 6)

    # Crop Right Arm (x: 165-215, y: 165-230)
    rx0, ry0, rx1, ry1 = 165, 160, 215, 230
    right_arm = base.crop((rx0, ry0, rx1, ry1))
    rmask = create_feathered_mask(rx1 - rx0, ry1 - ry0, 6)

    # Crop Head (x: 40-200, y: 35-155)
    hx0, hy0, hx1, hy1 = 40, 35, 200, 155
    head_patch = base.crop((hx0, hy0, hx1, hy1))
    hmask = create_feathered_mask(hx1 - hx0, hy1 - hy0, 8)

    # 4 Groove Frames:
    # Frame 0: Baseline neutral groove
    # Frame 1: Left arm pumps high (+6px), head tilts left (-3 deg), right arm sways out (+3px)
    # Frame 2: Beat drop! Head bob down (-3px), notes burst
    # Frame 3: Left arm swings forward, head tilts right (+3 deg), right arm pumps

    groove_params = [
        {"l_dy": 0, "r_dy": 0, "h_tilt": 0, "h_dy": 0, "note_pulse": 0},
        {"l_dy": -8, "r_dy": 4, "h_tilt": -2.5, "h_dy": -2, "note_pulse": 1},
        {"l_dy": -3, "r_dy": -4, "h_tilt": 0, "h_dy": 3, "note_pulse": 2},
        {"l_dy": 4, "r_dy": -8, "h_tilt": 2.5, "h_dy": -1, "note_pulse": 3},
    ]

    for idx, p in enumerate(groove_params):
        frame = base.copy()

        # Head transform (tilt & bob)
        h_rot = head_patch.rotate(p["h_tilt"], resample=Image.Resampling.BICUBIC, center=((hx1-hx0)//2, (hy1-hy0)//2))
        h_shifted = Image.new("RGB", (hx1 - hx0, hy1 - hy0), (0, 0, 0))
        h_shifted.paste(h_rot, (0, p["h_dy"]))
        frame.paste(h_shifted, (hx0, hy0), mask=hmask)

        # Left hand pump
        l_shifted = Image.new("RGB", (lx1 - lx0, ly1 - ly0), (0, 0, 0))
        l_shifted.paste(left_arm, (0, p["l_dy"]))
        frame.paste(l_shifted, (lx0, ly0), mask=lmask)

        # Right hand pump
        r_shifted = Image.new("RGB", (rx1 - rx0, ry1 - ry0), (0, 0, 0))
        r_shifted.paste(right_arm, (0, p["r_dy"]))
        frame.paste(r_shifted, (rx0, ry0), mask=rmask)

        # Floating bouncing musical rhythm VFX
        vfx = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vfx)

        # Notes bounce
        n1_y = 110 + int(math.sin(idx * math.pi / 2) * 6)
        n2_y = 95 - int(math.cos(idx * math.pi / 2) * 6)
        n3_y = 70 + int(math.sin((idx + 1) * math.pi / 2) * 7)

        # Cyan sound ring
        draw.ellipse([25, n1_y - 12, 55, n1_y + 18], fill=(56, 189, 248, 45 + idx * 10))
        # Orange sound ring
        draw.ellipse([185, n2_y - 15, 220, n2_y + 18], fill=(242, 139, 36, 45 + (3 - idx) * 10))
        # Top beat sparkle
        draw.ellipse([150, n3_y - 10, 180, n3_y + 20], fill=(255, 230, 100, 50))

        vfx = vfx.filter(ImageFilter.GaussianBlur(3))
        frame.paste(vfx, (0, 0), mask=vfx)

        frame.save(out_dir / f"frame_{idx}.png", format="PNG", optimize=True)

    print("✅ music_dancing frames generated")

# ==============================================================================
# 2. WORKING SOLDERING ANIMATION (4 Frames - Precise Stroke, Sparks, Drifting Smoke)
# ==============================================================================
def make_working_soldering():
    out_dir = ANIM_DIR / "working_soldering"
    out_dir.mkdir(parents=True, exist_ok=True)
    base = load_crop_base(BRAIN_DIR / "tinko_workshop_working_soldering_1794898980075.jpg")

    # Hand holding soldering iron (x: 35-130, y: 165-265)
    ix0, iy0, ix1, iy1 = 35, 165, 130, 265
    tool_patch = base.crop((ix0, iy0, ix1, iy1))
    tmask = create_feathered_mask(ix1 - ix0, iy1 - iy0, 8)

    # Head (x: 40-200, y: 40-155)
    hx0, hy0, hx1, hy1 = 40, 40, 200, 155
    head_patch = base.crop((hx0, hy0, hx1, hy1))
    hmask = create_feathered_mask(hx1 - hx0, hy1 - hy0, 8)

    # 4 Soldering steps:
    # 0: Solder tip firmly down on PCB contact pad, spark flare
    # 1: Solder iron lifting up (+5px), inspection, smoke drifts right
    # 2: Solder iron shifts towards adjacent component (+6px up, +2px right)
    # 3: Solder iron presses down into next pad, bright micro-flash!

    solder_steps = [
        {"tool_dy": 1, "tool_dx": 0, "head_dy": 2, "spark": 1, "smoke_y": 230},
        {"tool_dy": -5, "tool_dx": 1, "head_dy": -1, "spark": 0, "smoke_y": 218},
        {"tool_dy": -7, "tool_dx": 3, "head_dy": -2, "spark": 0, "smoke_y": 206},
        {"tool_dy": 2, "tool_dx": 1, "head_dy": 1, "spark": 2, "smoke_y": 232},
    ]

    for idx, s in enumerate(solder_steps):
        frame = base.copy()

        # Head micro-motion (leaning in to inspect work)
        h_shift = Image.new("RGB", (hx1 - hx0, hy1 - hy0), (0, 0, 0))
        h_shift.paste(head_patch, (0, s["head_dy"]))
        frame.paste(h_shift, (hx0, hy0), mask=hmask)

        # Tool stroke motion
        t_shift = Image.new("RGB", (ix1 - ix0, iy1 - iy0), (0, 0, 0))
        t_shift.paste(tool_patch, (s["tool_dx"], s["tool_dy"]))
        frame.paste(t_shift, (ix0, iy0), mask=tmask)

        # Dynamic solder smoke and contact sparks
        vfx = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vfx)

        # Smoke billows
        sy = s["smoke_y"]
        sx = 118 + (idx * 3)
        draw.ellipse([sx - 6, sy - 8, sx + 8, sy + 8], fill=(235, 240, 255, 60 - idx * 8))
        draw.ellipse([sx - 2, sy - 16, sx + 12, sy - 2], fill=(235, 240, 255, 40 - idx * 6))

        # Contact sparks
        if s["spark"] > 0:
            cx, cy = 115, 247
            bright = 255 if s["spark"] == 2 else 200
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 200, 80, 140))
            draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 220, bright))
            # Star rays
            draw.line([cx - 7, cy, cx + 7, cy], fill=(255, 255, 240, bright), width=1)
            draw.line([cx, cy - 7, cx, cy + 7], fill=(255, 255, 240, bright), width=1)

        vfx = vfx.filter(ImageFilter.GaussianBlur(1))
        frame.paste(vfx, (0, 0), mask=vfx)

        frame.save(out_dir / f"frame_{idx}.png", format="PNG", optimize=True)

    print("✅ working_soldering frames generated")

# ==============================================================================
# 3. CELEBRATING ANIMATION (4 Frames - Alternating Arm Wave, Hopping, Twinkling Stars)
# ==============================================================================
def make_celebrating():
    out_dir = ANIM_DIR / "celebrating"
    out_dir.mkdir(parents=True, exist_ok=True)
    base = load_crop_base(BRAIN_DIR / "tinko_workshop_celebrating_1794898990705.jpg")

    # Left raised arm (x: 20-75, y: 100-180)
    lx0, ly0, lx1, ly1 = 20, 100, 75, 180
    left_arm = base.crop((lx0, ly0, lx1, ly1))
    lmask = create_feathered_mask(lx1 - lx0, ly1 - ly0, 6)

    # Right raised arm (x: 165-220, y: 100-180)
    rx0, ry0, rx1, ry1 = 165, 100, 220, 180
    right_arm = base.crop((rx0, ry0, rx1, ry1))
    rmask = create_feathered_mask(rx1 - rx0, ry1 - ry0, 6)

    # Entire upper body for hopping (x: 20-220, y: 30-260)
    bx0, by0, bx1, by1 = 20, 30, 220, 260
    body = base.crop((bx0, by0, bx1, by1))
    bmask = create_feathered_mask(bx1 - bx0, by1 - by0, 10)

    # 4 Waving & Hopping steps:
    hop_params = [
        {"hop_y": 0, "l_dy": 0, "r_dy": 0, "star_rot": 0},
        {"hop_y": -4, "l_dy": -6, "r_dy": 4, "star_rot": 1},
        {"hop_y": -7, "l_dy": -3, "r_dy": -5, "star_rot": 2},
        {"hop_y": -2, "l_dy": 5, "r_dy": -7, "star_rot": 3},
    ]

    for idx, p in enumerate(hop_params):
        frame = base.copy()

        # Body hop
        b_shift = Image.new("RGB", (bx1 - bx0, by1 - by0), (0, 0, 0))
        b_shift.paste(body, (0, p["hop_y"]))
        frame.paste(b_shift, (bx0, by0), mask=bmask)

        # Alternating waving arms
        l_shift = Image.new("RGB", (lx1 - lx0, ly1 - ly0), (0, 0, 0))
        l_shift.paste(left_arm, (0, p["hop_y"] + p["l_dy"]))
        frame.paste(l_shift, (lx0, ly0), mask=lmask)

        r_shift = Image.new("RGB", (rx1 - rx0, ry1 - ry0), (0, 0, 0))
        r_shift.paste(right_arm, (0, p["hop_y"] + p["r_dy"]))
        frame.paste(r_shift, (rx0, ry0), mask=rmask)

        # Twinkling star VFX
        vfx = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vfx)

        stars = [(42, 65), (198, 55), (75, 45), (165, 40)]
        for s_idx, (sx, sy) in enumerate(stars):
            sz = 6 + int(math.sin((idx + s_idx) * math.pi / 2) * 3)
            alpha = 180 + int(math.cos((idx + s_idx) * math.pi / 2) * 70)
            draw.line([sx - sz, sy, sx + sz, sy], fill=(255, 255, 200, alpha), width=2)
            draw.line([sx, sy - sz, sx, sy + sz], fill=(255, 255, 200, alpha), width=2)

        vfx = vfx.filter(ImageFilter.GaussianBlur(1))
        frame.paste(vfx, (0, 0), mask=vfx)

        frame.save(out_dir / f"frame_{idx}.png", format="PNG", optimize=True)

    print("✅ celebrating frames generated")

# ==============================================================================
# 4. THINKING ANIMATION (4 Frames - Tapping Chin, Head Tilt, Idea Bulb Pulsing)
# ==============================================================================
def make_thinking():
    out_dir = ANIM_DIR / "thinking"
    out_dir.mkdir(parents=True, exist_ok=True)
    base = load_crop_base(BRAIN_DIR / "tinko_workshop_thinking_1794899152990.jpg")

    # Hand on chin (x: 105-155, y: 125-175)
    hx0, hy0, hx1, hy1 = 105, 125, 155, 175
    hand_patch = base.crop((hx0, hy0, hx1, hy1))
    hmask = create_feathered_mask(hx1 - hx0, hy1 - hy0, 6)

    # Head (x: 40-200, y: 35-150)
    tx0, ty0, tx1, ty1 = 40, 35, 200, 150
    head_patch = base.crop((tx0, ty0, tx1, ty1))
    tmask = create_feathered_mask(tx1 - tx0, ty1 - ty0, 8)

    # 4 Thinking steps (finger tapping chin, idea bulb blinking/glowing):
    think_params = [
        {"tap_y": 0, "head_tilt": 0, "bulb_glow": 50, "rays": False},
        {"tap_y": -3, "head_tilt": -2.0, "bulb_glow": 90, "rays": False},
        {"tap_y": -1, "head_tilt": -3.5, "bulb_glow": 180, "rays": True},
        {"tap_y": 1, "head_tilt": -1.0, "bulb_glow": 120, "rays": True},
    ]

    for idx, p in enumerate(think_params):
        frame = base.copy()

        # Head tilt
        h_rot = head_patch.rotate(p["head_tilt"], resample=Image.Resampling.BICUBIC, center=((tx1-tx0)//2, (ty1-ty0)//2))
        frame.paste(h_rot, (tx0, ty0), mask=tmask)

        # Finger tap motion on chin
        tap_shift = Image.new("RGB", (hx1 - hx0, hy1 - hy0), (0, 0, 0))
        tap_shift.paste(hand_patch, (0, p["tap_y"]))
        frame.paste(tap_shift, (hx0, hy0), mask=hmask)

        # Idea lightbulb pulsing with radiant rays
        vfx = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vfx)

        bx, by = 195, 52  # Lightbulb center
        glow_rad = 14 + (idx * 3)
        draw.ellipse([bx - glow_rad, by - glow_rad, bx + glow_rad, by + glow_rad], fill=(255, 240, 120, p["bulb_glow"]))

        if p["rays"]:
            ray_len = 12 + idx * 2
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(angle)
                rx1 = bx + int(math.cos(rad) * 14)
                ry1 = by + int(math.sin(rad) * 14)
                rx2 = bx + int(math.cos(rad) * (14 + ray_len))
                ry2 = by + int(math.sin(rad) * (14 + ray_len))
                draw.line([rx1, ry1, rx2, ry2], fill=(255, 255, 180, 190), width=1)

        vfx = vfx.filter(ImageFilter.GaussianBlur(2))
        frame.paste(vfx, (0, 0), mask=vfx)

        frame.save(out_dir / f"frame_{idx}.png", format="PNG", optimize=True)

    print("✅ thinking frames generated")

# ==============================================================================
# 5. SLEEPING ANIMATION (4 Frames - Breathing Expansion, Rising Floating Zzz)
# ==============================================================================
def make_sleeping():
    out_dir = ANIM_DIR / "sleeping"
    out_dir.mkdir(parents=True, exist_ok=True)
    base = load_crop_base(BRAIN_DIR / "tinko_workshop_sleeping_1794899070412.jpg")

    # Upper torso / chest region for breathing (x: 40-200, y: 40-240)
    bx0, by0, bx1, by1 = 40, 40, 200, 240
    chest = base.crop((bx0, by0, bx1, by1))
    cmask = create_feathered_mask(bx1 - bx0, by1 - by0, 12)

    # 4 Breath cycles (Inhale, hold, exhale, rest):
    breath_steps = [
        {"dy": 0, "zzz_dy": 0, "zzz_alpha": 120},
        {"dy": -2, "zzz_dy": -4, "zzz_alpha": 160},
        {"dy": -4, "zzz_dy": -8, "zzz_alpha": 200},
        {"dy": -1, "zzz_dy": -12, "zzz_alpha": 90},
    ]

    for idx, b in enumerate(breath_steps):
        frame = base.copy()

        # Chest breath shift
        c_shift = Image.new("RGB", (bx1 - bx0, by1 - by0), (0, 0, 0))
        c_shift.paste(chest, (0, b["dy"]))
        frame.paste(c_shift, (bx0, by0), mask=cmask)

        # Floating glowing Zzz in arc
        vfx = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vfx)

        zy = 55 + b["zzz_dy"]
        zx = 195 + int(math.sin(idx * math.pi / 2) * 3)

        # Soft warm Zzz glow
        draw.ellipse([zx - 16, zy - 12, zx + 18, zy + 22], fill=(255, 220, 140, b["zzz_alpha"] // 3))

        vfx = vfx.filter(ImageFilter.GaussianBlur(3))
        frame.paste(vfx, (0, 0), mask=vfx)

        frame.save(out_dir / f"frame_{idx}.png", format="PNG", optimize=True)

    print("✅ sleeping frames generated")

if __name__ == "__main__":
    make_music_dancing()
    make_working_soldering()
    make_celebrating()
    make_thinking()
    make_sleeping()
    print("All expressive animations generated!")

