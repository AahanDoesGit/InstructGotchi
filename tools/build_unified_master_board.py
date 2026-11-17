"""
Builds the complete Instructa-Gotchi Master Design Board.
Seamlessly integrates the authentic original reference character from visual_references/01_mascot_and_product_identity.png,
the turnaround and expressions from 02_character_turnaround_and_expressions.png,
the live UNIHIKER 240x320 touchscreen UI screens, and the phone companion mockup into one
clean presentation board (2048 x 1152).
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
REF_DIR = WORKSPACE_ROOT / "visual_references"
ASSETS_DIR = PROJECT_ROOT / "assets"
PREVIEWS_DIR = PROJECT_ROOT / "tests" / "previews"

def build_board():
    board_w, board_h = 2048, 1152
    board = Image.new("RGBA", (board_w, board_h), (255, 249, 239, 255)) # Warm Ivory
    draw = ImageDraw.Draw(board)

    # 1. Header Banner
    draw.rectangle([0, 0, board_w, 80], fill=(48, 45, 40)) # Deep Ink
    draw.line([0, 80, board_w, 80], fill=(255, 201, 40), width=4) # Maker Yellow border
    draw.text((40, 24), "INSTRUCTA-GOTCHI", fill=(255, 201, 40))
    draw.text((320, 28), "|   MASTER DESIGN SYSTEM & CHARACTER REFERENCE BOARD", fill=(245, 240, 230))
    draw.text((board_w - 360, 28), "Target: DFRobot UNIHIKER M10 (240x320)", fill=(135, 144, 153))

    # 2. Panel 1 (Top Left): ORIGINAL CHARACTER REFERENCE (from 01_mascot_and_product_identity.png)
    p1_box = [40, 110, 680, 660]
    draw.rounded_rectangle(p1_box, radius=16, fill=(245, 240, 230), outline=(220, 210, 195), width=2)
    draw.text((60, 126), "1. ORIGINAL 3D CHARACTER REFERENCE", fill=(242, 139, 36))
    draw.text((60, 146), "Master vinyl maker robot mascot with cyan glowing eyes & toolbelt", fill=(135, 144, 153))

    ref1_path = REF_DIR / "01_mascot_and_product_identity.png"
    if ref1_path.exists():
        im1 = Image.open(ref1_path)
        # Crop the mascot cleanly
        mascot_crop = im1.crop((320, 20, 605, 385))
        mw, mh = mascot_crop.size
        # Scale to fit nicely in panel 1
        scale = min(580 / mw, 460 / mh)
        mascot_resized = mascot_crop.resize((int(mw * scale), int(mh * scale)), Image.Resampling.LANCZOS)
        # Paste with card shadow
        px = 40 + (640 - mascot_resized.width) // 2
        py = 180 + (460 - mascot_resized.height) // 2
        board.paste(mascot_resized, (px, py))

    # 3. Panel 2 (Top Right): CHARACTER TURNAROUND & EXPRESSIONS (from 02_character_turnaround_and_expressions.png)
    p2_box = [710, 110, 2008, 420]
    draw.rounded_rectangle(p2_box, radius=16, fill=(245, 240, 230), outline=(220, 210, 195), width=2)
    draw.text((730, 126), "2. TURNAROUND ANGLES & EMOTIONAL EXPRESSIONS", fill=(242, 139, 36))
    draw.text((730, 146), "Exact multi-angle poses & facial sprite specifications from reference sheet", fill=(135, 144, 153))

    ref2_path = REF_DIR / "02_character_turnaround_and_expressions.png"
    if ref2_path.exists():
        im2 = Image.open(ref2_path)
        tw, th = im2.size
        # Fit in panel 2
        t_scale = min(1250 / tw, 230 / th)
        t_resized = im2.resize((int(tw * t_scale), int(th * t_scale)), Image.Resampling.LANCZOS)
        tpx = 710 + (1298 - t_resized.width) // 2
        tpy = 175
        board.paste(t_resized, (tpx, tpy))

    # 4. Panel 3 (Bottom Right): UNIHIKER M10 240x320 TOUCHSCREEN SCREENS
    p3_box = [710, 440, 2008, 980]
    draw.rounded_rectangle(p3_box, radius=16, fill=(245, 240, 230), outline=(220, 210, 195), width=2)
    draw.text((730, 456), "3. UNIHIKER M10 DEVICE UI (EXACT 240x320 PORTRAIT IMPLEMENTATION)", fill=(242, 139, 36))
    draw.text((730, 476), "Character-led touchscreen interface running live on the device with reference art", fill=(135, 144, 153))

    # Place 4 key device screens side-by-side: Home, Workshop, Care, Modes
    screen_names = [
        ("home_240x320.png", "Home Screen"),
        ("workshop_240x320.png", "Workshop Screen"),
        ("care_240x320.png", "Care Screen"),
        ("modes_240x320.png", "Modes Screen"),
        ("music_240x320.png", "Music Screen")
    ]
    sx = 735
    for sfile, slabel in screen_names:
        spath = PREVIEWS_DIR / sfile
        if spath.exists():
            sim = Image.open(spath)
            # Scale down slightly to fit 5 screens
            sw, sh = sim.size
            scale = 0.94
            s_resized = sim.resize((int(sw * scale), int(sh * scale)), Image.Resampling.LANCZOS)
            # Outer screen bezel
            draw.rounded_rectangle([sx - 4, 506, sx + s_resized.width + 4, 506 + s_resized.height + 8], radius=8, fill=(36, 37, 34))
            board.paste(s_resized, (sx, 510))
            draw.text((sx + 10, 510 + s_resized.height + 14), slabel, fill=(48, 45, 40))
            sx += s_resized.width + 28

    # 5. Panel 4 (Bottom Left): WORKSHOP ENVIRONMENT REFERENCE (from 04)
    p4_box = [40, 680, 680, 980]
    draw.rounded_rectangle(p4_box, radius=16, fill=(245, 240, 230), outline=(220, 210, 195), width=2)
    draw.text((60, 696), "4. WORKSHOP ENVIRONMENT REFERENCE", fill=(242, 139, 36))
    draw.text((60, 716), "Warm maker workshop workbench and tool background", fill=(135, 144, 153))

    ref4_path = REF_DIR / "04_workshop_and_system_architecture.png"
    if ref4_path.exists():
        im4 = Image.open(ref4_path)
        w4, h4 = im4.size
        crop4 = im4.crop((0, 0, int(w4 * 0.52), h4))
        c4_scale = min(600 / crop4.width, 220 / crop4.height)
        c4_resized = crop4.resize((int(crop4.width * c4_scale), int(crop4.height * c4_scale)), Image.Resampling.LANCZOS)
        c4x = 40 + (640 - c4_resized.width) // 2
        c4y = 745
        board.paste(c4_resized, (c4x, c4y))

    # 6. Bottom Color Tokens & Swatches
    draw.rectangle([0, 1000, board_w, board_h], fill=(36, 37, 34)) # Graphite footer
    draw.text((40, 1020), "5. DESIGN SYSTEM PALETTE TOKENS:", fill=(255, 201, 40))

    swatches = [
        ("Workshop Cream", "#F5F0E6", (245, 240, 230)),
        ("Warm Ivory", "#FFF9EF", (255, 249, 239)),
        ("Maker Yellow", "#FFC928", (255, 201, 40)),
        ("Signal Orange", "#F28B24", (242, 139, 36)),
        ("Workshop Green", "#83A978", (131, 169, 120)),
        ("Graphite", "#242522", (36, 37, 34)),
        ("Electric Cyan", "#38BDF8", (56, 189, 248))
    ]
    sw_x = 40
    for name, hex_code, rgb in swatches:
        draw.rounded_rectangle([sw_x, 1050, sw_x + 40, 1090], radius=6, fill=rgb, outline=(200, 200, 200), width=1)
        draw.text((sw_x + 50, 1052), name, fill=(245, 240, 230))
        draw.text((sw_x + 50, 1070), hex_code, fill=(135, 144, 153))
        sw_x += 275

    out_file = ASSETS_DIR / "complete_project_reference_sheet.png"
    board.save(out_file, "PNG")
    print(f"Successfully generated master reference sheet: {out_file} (2048x1152)")

if __name__ == "__main__":
    build_board()

