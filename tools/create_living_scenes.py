"""
Composites seamless 240x320 character-in-workshop living scenes for the UNIHIKER M10 display.
Zero text overlays, zero menus, zero HUD widgets.
Pure character living and working in its workshop.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
SCENES_DIR = ASSETS_DIR / "scenes"
SCENES_DIR.mkdir(parents=True, exist_ok=True)

def get_base_workshop():
    """Extracts the 3D workshop environment and crops to 240x320 portrait."""
    src = WORKSPACE_ROOT / "stitch_extracted" / "stitch_instructa_gotchi_design_system" / "04_workshop_and_system_architecture.png" / "screen.png"
    if not src.exists():
        src = WORKSPACE_ROOT / "visual_references" / "04_workshop_and_system_architecture.png"
    im = Image.open(src)
    w, h = im.size

    # Left half has the workshop bench
    crop_ws = im.crop((0, 0, int(w * 0.52), h))
    cw, ch = crop_ws.size
    target_w = int(ch * (240 / 320))
    if target_w <= cw:
        portrait_crop = crop_ws.crop((0, 0, target_w, ch))
    else:
        target_h = int(cw / (240 / 320))
        portrait_crop = crop_ws.crop((0, 0, cw, min(ch, target_h)))

    return portrait_crop.resize((240, 320), Image.Resampling.LANCZOS)

def get_mascot():
    """Loads the Stitch 3D robot mascot."""
    src = ASSETS_DIR / "characters" / "stitch_mascot_3d.png"
    if not src.exists():
        src = WORKSPACE_ROOT / "stitch_extracted" / "stitch_instructa_gotchi_design_system" / "high_quality_3d_render_of_the_exact_instructa_gotchi_robot_mascot_character" / "screen.png"
    return Image.open(src).convert("RGBA")

def build_living_scenes():
    ws_base = get_base_workshop()
    mascot = get_mascot()

    # Mascot sizing: approx 150x150 placed naturally at the bench
    mw, mh = 145, 145
    mascot_resized = mascot.resize((mw, mh), Image.Resampling.LANCZOS)

    # 1. SCENE IDLE (Character looking forward warmly at workbench)
    scene_idle = ws_base.copy()
    # Shadow beneath mascot
    shadow = Image.new("RGBA", (240, 320), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    cx, cy = 120, 225
    sdraw.ellipse([cx - 45, cy - 8, cx + 45, cy + 12], fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    scene_idle.paste(shadow, (0, 0), shadow)
    # Character on top
    char_pos = ((240 - mw) // 2, 85)
    scene_idle.paste(mascot_resized, char_pos, mascot_resized)
    scene_idle.save(SCENES_DIR / "scene_idle.png")
    print("Generated: scene_idle.png (240x320)")

    # 2. SCENE WORKING (Character actively tinkering with soldering iron / sparks)
    scene_working = ws_base.copy()
    scene_working.paste(shadow, (0, 0), shadow)
    # Slight tilt/focus bob
    char_pos_work = ((240 - mw) // 2, 88)
    scene_working.paste(mascot_resized, char_pos_work, mascot_resized)
    # Miniature tinker sparks on bench
    wdraw = ImageDraw.Draw(scene_working)
    # Glowing micro LED / solder tip on bench
    wdraw.ellipse([155, 218, 163, 226], fill=(56, 189, 248, 240))
    wdraw.ellipse([157, 220, 161, 224], fill=(255, 255, 255, 255))
    # Tiny sparks
    wdraw.line([(159, 215), (163, 210)], fill=(255, 201, 40), width=1)
    wdraw.line([(163, 220), (168, 218)], fill=(255, 201, 40), width=1)
    wdraw.line([(156, 227), (153, 231)], fill=(255, 201, 40), width=1)
    scene_working.save(SCENES_DIR / "scene_working.png")
    print("Generated: scene_working.png (240x320)")

    # 3. SCENE HAPPY / CELEBRATING (Joyous reaction when petted or care action received)
    scene_happy = ws_base.copy()
    scene_happy.paste(shadow, (0, 0), shadow)
    char_pos_happy = ((240 - mw) // 2, 80)
    scene_happy.paste(mascot_resized, char_pos_happy, mascot_resized)
    # Joyful sparkles in workshop air
    hdraw = ImageDraw.Draw(scene_happy)
    for sx, sy in [(60, 90), (180, 85), (50, 150), (195, 145)]:
        hdraw.line([(sx - 4, sy), (sx + 4, sy)], fill=(255, 201, 40), width=2)
        hdraw.line([(sx, sy - 4), (sx, sy + 4)], fill=(255, 201, 40), width=2)
        hdraw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    scene_happy.save(SCENES_DIR / "scene_happy.png")
    print("Generated: scene_happy.png (240x320)")

    # 4. SCENE SLEEP (Nighttime darkened workshop, moonlight, peaceful sleep)
    arr_night = np.array(ws_base).astype(float)
    arr_night[:, :, 0] *= 0.22  # darken red
    arr_night[:, :, 1] *= 0.26  # darken green
    arr_night[:, :, 2] *= 0.42  # preserve cool moonlight blue
    ws_night = Image.fromarray(np.clip(arr_night, 0, 255).astype(np.uint8), "RGB")

    scene_sleep = ws_night.copy()
    # Dim mascot shadow & mascot
    arr_m = np.array(mascot_resized).astype(float)
    arr_m[:, :, 0] *= 0.35
    arr_m[:, :, 1] *= 0.38
    arr_m[:, :, 2] *= 0.48
    mascot_sleep = Image.fromarray(np.clip(arr_m, 0, 255).astype(np.uint8), "RGBA")

    scene_sleep.paste(mascot_sleep, ((240 - mw) // 2, 92), mascot_sleep)
    # Gentle Zzz in air
    sdraw2 = ImageDraw.Draw(scene_sleep)
    sdraw2.text((155, 75), "z", fill=(56, 189, 248, 180))
    sdraw2.text((165, 60), "Z", fill=(56, 189, 248, 220))
    sdraw2.text((178, 42), "Z", fill=(56, 189, 248, 255))
    scene_sleep.save(SCENES_DIR / "scene_sleep.png")
    print("Generated: scene_sleep.png (240x320)")

    # 5. SCENE MUSIC (Vibrant neon workshop rhythm)
    arr_mus = np.array(ws_base).astype(float)
    arr_mus[:, :, 0] *= 0.45
    arr_mus[:, :, 2] = np.clip(arr_mus[:, :, 2] * 1.3 + 30, 0, 255)
    ws_music = Image.fromarray(np.clip(arr_mus, 0, 255).astype(np.uint8), "RGB")
    scene_music = ws_music.copy()
    scene_music.paste(shadow, (0, 0), shadow)
    scene_music.paste(mascot_resized, ((240 - mw) // 2, 82), mascot_resized)
    # Neon rhythm notes floating
    mdraw = ImageDraw.Draw(scene_music)
    mdraw.text((50, 70), "♪", fill=(56, 189, 248))
    mdraw.text((180, 65), "♫", fill=(242, 139, 36))
    scene_music.save(SCENES_DIR / "scene_music.png")
    print("Generated: scene_music.png (240x320)")

if __name__ == "__main__":
    build_living_scenes()

