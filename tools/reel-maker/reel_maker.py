"""
ZenPosture Cinematic Reel Maker v3
====================================
Generates branded Instagram/Facebook reels (1080x1920) using YOUR actual
product images from the ZenPosture website.

Usage:
  python reel_maker.py --script office_worker --output reel.mp4
  python reel_maker.py --script new_mom --music bg.mp3 --output mom.mp4
  python reel_maker.py --script pain_hook --letterbox --output pain.mp4
  python reel_maker.py --custom --output custom.mp4
  python reel_maker.py --images path/to/your/images --script office_worker --output reel.mp4
"""

import argparse
import os
import sys
import textwrap
import random
import math

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    import numpy as np
    from moviepy.editor import (
        VideoClip, concatenate_videoclips, AudioFileClip
    )
    from moviepy.video.fx.all import fadein, fadeout
except ImportError as e:
    print(f"\n❌  Missing dependency: {e}\n")
    print("Run:  pip install moviepy pillow numpy requests\n")
    sys.exit(1)

# ─── Constants ─────────────────────────────────────────────────────────────────

W, H = 1080, 1920
FPS  = 30

# Path to your real ZenPosture images (relative to this script)
# Automatically finds the public/images folder in the repo
_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IMAGES_DIR = os.path.normpath(os.path.join(_HERE, "../../public/images"))

# ─── Brand Colors ──────────────────────────────────────────────────────────────

EMERALD   = (16, 185, 129)
EMERALD_D = (5,  150, 105)
AMBER     = (251, 191,  36)
RED       = (239,  68,  68)
WHITE     = (255, 255, 255)
DARK      = ( 15,  23,  42)
MUTED     = (148, 163, 184)

# ─── Image mapping — your actual product photos ────────────────────────────────
#
# Keys are mood names used in scripts below.
# Values are filenames from public/images/.
# The tool picks one randomly if multiple listed.

MOOD_FILES = {
    "hero":          ["hero-lifestyle.jpg"],
    "posture_work":  ["posture-at-work.jpg"],
    "comparison":    ["posture-comparison.jpg"],
    "fitness":       ["fitness-belt.jpg"],
    "postpartum":    ["postpartum-care.jpg"],
    "happy1":        ["happy-customer-1.jpg"],
    "happy2":        ["happy-customer-2.jpg"],
    "happy3":        ["happy-customer-3.jpg"],
    # Aliases used in scripts for semantic clarity
    "problem":       ["posture-at-work.jpg", "posture-comparison.jpg"],
    "solution":      ["hero-lifestyle.jpg", "posture-comparison.jpg"],
    "product":       ["fitness-belt.jpg", "postpartum-care.jpg"],
    "happy":         ["happy-customer-1.jpg", "happy-customer-2.jpg", "happy-customer-3.jpg"],
    "cta":           ["hero-lifestyle.jpg"],
    "new_mom":       ["postpartum-care.jpg"],
    "pain":          ["posture-at-work.jpg"],
    "transformation":["posture-comparison.jpg"],
}

# ─── Script Templates ──────────────────────────────────────────────────────────

SCRIPTS = {
    "office_worker": [
        {
            "duration": 3.5,
            "mood":     "posture_work",
            "overlay":  0.45,
            "tag":      None,
            "headline": "If you sit 6+ hours\na day… watch this.",
            "sub":      "👇",
            "text_pos": "center",
            "accent":   AMBER,
        },
        {
            "duration": 4.0,
            "mood":     "pain",
            "overlay":  0.60,
            "tag":      "THE PROBLEM",
            "headline": "Back pain.\nNeck stiffness.\nConstant fatigue.",
            "sub":      "That's what bad posture does to you — every single day.",
            "text_pos": "lower",
            "accent":   RED,
        },
        {
            "duration": 4.5,
            "mood":     "solution",
            "overlay":  0.40,
            "tag":      "THE SOLUTION",
            "headline": "Meet ZenPosture.",
            "sub":      "India's most trusted posture corrector.\nFeel the difference from Day 1.",
            "text_pos": "lower",
            "accent":   EMERALD,
        },
        {
            "duration": 4.0,
            "mood":     "happy",
            "overlay":  0.50,
            "tag":      "REAL RESULTS",
            "headline": "⭐⭐⭐⭐⭐",
            "sub":      '"Back pain gone in just 1 week."\n— Priya S., Mumbai · Verified Buyer',
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 4.0,
            "mood":     "product",
            "overlay":  0.45,
            "tag":      "🔥 LIMITED OFFER",
            "headline": "Starting at ₹499",
            "sub":      "Free Shipping · Cash on Delivery\n30-Day Money-Back Guarantee",
            "text_pos": "lower",
            "accent":   RED,
        },
        {
            "duration": 4.0,
            "mood":     "hero",
            "overlay":  0.40,
            "tag":      None,
            "headline": "Fix your posture.\nTransform your life.",
            "sub":      "👆  zenposture.in  |  Link in bio",
            "text_pos": "center",
            "accent":   EMERALD,
            "is_cta":   True,
        },
    ],

    "pain_hook": [
        {
            "duration": 3.0,
            "mood":     "pain",
            "overlay":  0.60,
            "tag":      None,
            "headline": "Your back pain\nisn't normal.",
            "sub":      "It's fixable. 🔥",
            "text_pos": "center",
            "accent":   RED,
        },
        {
            "duration": 4.0,
            "mood":     "posture_work",
            "overlay":  0.55,
            "tag":      "THE TRUTH",
            "headline": "8 hours of sitting\nis destroying\nyour spine.",
            "sub":      "Slowly. Every. Single. Day.",
            "text_pos": "lower",
            "accent":   RED,
        },
        {
            "duration": 4.0,
            "mood":     "transformation",
            "overlay":  0.40,
            "tag":      "SEE THE DIFFERENCE",
            "headline": "ZenPosture fixes it\nin DAYS.",
            "sub":      "10,000+ Indians already know.\nNow you do too.",
            "text_pos": "lower",
            "accent":   EMERALD,
        },
        {
            "duration": 3.5,
            "mood":     "happy",
            "overlay":  0.45,
            "tag":      "VERIFIED BUYER",
            "headline": "⭐⭐⭐⭐⭐",
            "sub":      '"My posture changed in 2 weeks."\n— Rahul V., Bangalore',
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 3.5,
            "mood":     "hero",
            "overlay":  0.40,
            "tag":      None,
            "headline": "₹499 onwards.\nCOD. Free Shipping.",
            "sub":      "👆  zenposture.in",
            "text_pos": "center",
            "accent":   EMERALD,
            "is_cta":   True,
        },
    ],

    "new_mom": [
        {
            "duration": 4.0,
            "mood":     "new_mom",
            "overlay":  0.40,
            "tag":      None,
            "headline": "New moms —\nno one talks about\nTHIS after delivery.",
            "sub":      "💚",
            "text_pos": "center",
            "accent":   EMERALD,
        },
        {
            "duration": 4.5,
            "mood":     "pain",
            "overlay":  0.60,
            "tag":      "THE REALITY",
            "headline": "Weak core.\nAching back.\nAll day, every day.",
            "sub":      "Lifting, feeding, carrying — while your body is still healing.",
            "text_pos": "lower",
            "accent":   RED,
        },
        {
            "duration": 5.0,
            "mood":     "new_mom",
            "overlay":  0.35,
            "tag":      "THE SOLUTION",
            "headline": "ZenPosture\nPostpartum Belt.",
            "sub":      "Supports your core while your body heals.\nBreathable. Adjustable. Made for India.",
            "text_pos": "lower",
            "accent":   EMERALD,
        },
        {
            "duration": 4.0,
            "mood":     "happy",
            "overlay":  0.50,
            "tag":      "REAL MOM · REAL RESULT",
            "headline": "⭐⭐⭐⭐⭐",
            "sub":      '"Felt supported from Day 1.\nEvery new mom needs this."\n— Ananya P., Delhi',
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 3.5,
            "mood":     "new_mom",
            "overlay":  0.40,
            "tag":      None,
            "headline": "Starting at ₹599\nCOD · Free Shipping",
            "sub":      "👆  zenposture.in  |  Gift it to a new mom 💚",
            "text_pos": "center",
            "accent":   EMERALD,
            "is_cta":   True,
        },
    ],

    "product_showcase": [
        {
            "duration": 3.0,
            "mood":     "hero",
            "overlay":  0.35,
            "tag":      None,
            "headline": "India's #1\nPosture Brand.",
            "sub":      "10,000+ happy customers 💚",
            "text_pos": "center",
            "accent":   EMERALD,
        },
        {
            "duration": 3.5,
            "mood":     "posture_work",
            "overlay":  0.45,
            "tag":      "FOR DESK WORKERS",
            "headline": "Posture Corrector",
            "sub":      "Fix your slouch. Work pain-free. All day.",
            "text_pos": "lower",
            "accent":   EMERALD,
        },
        {
            "duration": 3.5,
            "mood":     "fitness",
            "overlay":  0.40,
            "tag":      "FOR GYM GOERS",
            "headline": "Fitness &\nCompression Belt",
            "sub":      "Lift heavier. Train smarter. Zero injuries.",
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 3.5,
            "mood":     "new_mom",
            "overlay":  0.40,
            "tag":      "FOR NEW MOMS",
            "headline": "Postpartum\nRecovery Belt",
            "sub":      "Gentle core support while your body heals.",
            "text_pos": "lower",
            "accent":   EMERALD,
        },
        {
            "duration": 3.5,
            "mood":     "transformation",
            "overlay":  0.40,
            "tag":      "SEE THE DIFFERENCE",
            "headline": "Before vs After.",
            "sub":      "93% report reduced back pain in 2 weeks.",
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 4.0,
            "mood":     "happy",
            "overlay":  0.45,
            "tag":      None,
            "headline": "From ₹499.\nFree Shipping.\nCOD Available.",
            "sub":      "👆  zenposture.in",
            "text_pos": "center",
            "accent":   EMERALD,
            "is_cta":   True,
        },
    ],
}

# ─── Image Loading ─────────────────────────────────────────────────────────────

def get_mood_image(mood, images_dir):
    files = MOOD_FILES.get(mood, [])
    if not files:
        return None
    chosen = random.choice(files)
    path = os.path.join(images_dir, chosen)
    if os.path.exists(path):
        return path
    # Fallback: pick any image in the folder
    all_imgs = [f for f in os.listdir(images_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if all_imgs:
        return os.path.join(images_dir, random.choice(all_imgs))
    return None


def load_and_fit(path, w, h):
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 1), int(ih * scale + 1)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return np.array(img.crop((x, y, x + w, y + h)))

# ─── Image FX ─────────────────────────────────────────────────────────────────

def color_grade(frame):
    r, g, b = frame[:,:,0].astype(np.float32), frame[:,:,1].astype(np.float32), frame[:,:,2].astype(np.float32)
    lum = (r * 0.299 + g * 0.587 + b * 0.114)
    dark = lum < 110
    bright = lum > 170
    # Teal in shadows
    r[dark] = np.clip(r[dark] * 0.87, 0, 255)
    b[dark] = np.clip(b[dark] * 1.10, 0, 255)
    # Warm in highlights
    r[bright] = np.clip(r[bright] * 1.07, 0, 255)
    b[bright] = np.clip(b[bright] * 0.93, 0, 255)
    # Slight desaturation
    sat = 0.88
    r2 = np.clip(lum + (r - lum) * sat, 0, 255)
    g2 = np.clip(lum + (g - lum) * sat, 0, 255)
    b2 = np.clip(lum + (b - lum) * sat, 0, 255)
    return np.stack([r2, g2, b2], axis=2).astype(np.uint8)


def add_vignette(frame, strength=0.55):
    h, w = frame.shape[:2]
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt(((X - w/2)/(w/2))**2 + ((Y - h/2)/(h/2))**2)
    mask = 1 - np.clip(dist * strength, 0, 1)
    return (frame * mask[:,:,np.newaxis]).astype(np.uint8)


def ken_burns(img, t, duration, zoom_in=True, pan_x=0.04, pan_y=0.02):
    h, w = img.shape[:2]
    p = t / max(duration, 0.001)
    z0, z1 = (1.0, 1.14) if zoom_in else (1.14, 1.0)
    zoom = z0 + (z1 - z0) * p
    cw, ch = int(w / zoom), int(h / zoom)
    ox = int(pan_x * p * (w - cw))
    oy = int(pan_y * p * (h - ch))
    x1 = max(0, min((w - cw)//2 + ox, w - cw))
    y1 = max(0, min((h - ch)//2 + oy, h - ch))
    cropped = img[y1:y1+ch, x1:x1+cw]
    return np.array(Image.fromarray(cropped).resize((w, h), Image.BILINEAR))

# ─── Font ─────────────────────────────────────────────────────────────────────

def load_font(size, bold=False):
    paths = [
        f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf",
        f"C:/Windows/Fonts/{'calibrib' if bold else 'calibri'}.ttf",
        f"C:/Windows/Fonts/{'verdanab' if bold else 'verdana'}.ttf",
        f"/System/Library/Fonts/Supplemental/Arial{'%20Bold' if bold else ''}.ttf",
        f"/System/Library/Fonts/Helvetica.ttc",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

# ─── Text Rendering ────────────────────────────────────────────────────────────

def shadow_text(draw, x, y, text, font, color, shadow=(0,0,0), offset=3):
    for dx in [-offset, 0, offset]:
        for dy in [-offset, 0, offset]:
            if dx or dy:
                draw.text((x+dx, y+dy), text, font=font, fill=(*shadow, 140))
    draw.text((x, y), text, font=font, fill=color)


def render_overlay(slide, progress, images_dir):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    pos     = slide.get("text_pos", "lower")
    accent  = slide.get("accent", WHITE)
    tag     = slide.get("tag")
    is_cta  = slide.get("is_cta", False)
    ov      = int(slide.get("overlay", 0.5) * 255)

    # Text slide-in animation (fast settle)
    anim = int((1 - min(progress * 3.0, 1)) * 55)

    # ── Gradient darkness overlay ──
    for y in range(H):
        if pos == "lower":
            t = max(0, (y - H * 0.30) / (H * 0.70))
            a = int(ov * min(t * 1.5, 1))
        else:
            t = 0.4 + 0.6 * math.sin(math.pi * y / H)
            a = int(ov * 0.9 * t)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))

    # ── Logo top center ──
    f_logo = load_font(42, bold=True)
    logo = "ZENPOSTURE"
    bx = d.textbbox((0,0), logo, font=f_logo)
    lw = bx[2] - bx[0]
    shadow_text(d, (W-lw)//2, 75, logo, f_logo, (*WHITE, 180))

    # ── Emerald underline under logo ──
    bar_y = 75 + (bx[3]-bx[1]) + 8
    bar_w = lw + 20
    d.rectangle([(W-bar_w)//2, bar_y, (W+bar_w)//2, bar_y+4], fill=(*EMERALD, 220))

    # ── Tag pill ──
    if tag:
        f_tag = load_font(30, bold=True)
        tb = d.textbbox((0,0), tag, font=f_tag)
        tw = tb[2]-tb[0]
        tx = (W-tw)//2
        pad = 14
        d.rounded_rectangle([tx-pad, 155, tx+tw+pad, 155+44], radius=22, fill=(*accent, 210))
        d.text((tx, 159), tag, font=f_tag, fill=(*DARK, 255))

    # ── Headline ──
    headline = slide.get("headline", "")
    lines = []
    for line in headline.split("\n"):
        lines.extend(textwrap.wrap(line, width=20) or [""])

    f_h = load_font(90, bold=True)
    f_h2 = load_font(74, bold=True)
    f_use = f_h if max((len(l) for l in lines), default=0) <= 13 else f_h2

    if pos == "lower":
        hy = H - 500 + anim
    else:
        hy = H//2 - (len(lines) * 110)//2 + anim

    for i, line in enumerate(lines):
        bb = d.textbbox((0,0), line, font=f_use)
        lw2 = bb[2]-bb[0]
        lh2 = bb[3]-bb[1]
        x = (W - lw2)//2
        col = accent if i == 0 else WHITE
        shadow_text(d, x, hy, line, f_use, col, offset=4)
        hy += int(lh2 * 1.18)

    # ── Subtext ──
    sub = slide.get("sub", "")
    if sub:
        f_sub = load_font(40)
        sy = hy + 18 + anim//2
        for line in sub.split("\n"):
            bb = d.textbbox((0,0), line, font=f_sub)
            sw = bb[2]-bb[0]
            sh = bb[3]-bb[1]
            shadow_text(d, (W-sw)//2, sy, line, f_sub, (*MUTED, 230))
            sy += int(sh * 1.28)

    # ── CTA button bar ──
    if is_cta:
        btn_y = H - 220
        btn_h = 110
        # Pill button
        d.rounded_rectangle([80, btn_y, W-80, btn_y+btn_h], radius=55, fill=(*EMERALD, 240))
        f_cta = load_font(46, bold=True)
        cta_t = "Shop Now →  zenposture.in"
        cb = d.textbbox((0,0), cta_t, font=f_cta)
        cw2 = cb[2]-cb[0]
        d.text(((W-cw2)//2, btn_y+28), cta_t, font=f_cta, fill=(*WHITE, 255))

    # ── Bottom trust strip ──
    if not is_cta:
        trust = "Free Shipping  ·  COD Available  ·  30-Day Guarantee"
        f_tr = load_font(28)
        tb2 = d.textbbox((0,0), trust, font=f_tr)
        tw2 = tb2[2]-tb2[0]
        d.rectangle([0, H-72, W, H], fill=(0,0,0,100))
        d.text(((W-tw2)//2, H-56), trust, font=f_tr, fill=(*WHITE, 140))

    return overlay

# ─── Slide Clip ────────────────────────────────────────────────────────────────

def build_slide(slide, images_dir, letterbox=False):
    duration = slide["duration"]
    path = get_mood_image(slide["mood"], images_dir)

    if path:
        raw = load_and_fit(path, W, H)
        raw = color_grade(raw)
        raw = add_vignette(raw)
    else:
        print(f"    ⚠️  No image found for mood '{slide['mood']}' in {images_dir}")
        raw = np.full((H, W, 3), DARK, dtype=np.uint8)

    zoom_in = random.choice([True, False])
    px = random.uniform(-0.035, 0.035)
    py = random.uniform(-0.02,  0.02)
    bar_h = int(H * 0.075) if letterbox else 0

    def make_frame(t):
        progress = t / duration
        fade = min(min(t / 0.35, 1.0), min((duration - t) / 0.35, 1.0))

        bg = ken_burns(raw, t, duration, zoom_in, px, py)
        bg_pil = Image.fromarray(bg)

        ov = render_overlay(slide, progress, images_dir)

        # Fade in/out the overlay alpha
        if fade < 1.0:
            faded = Image.new("RGBA", ov.size, (0,0,0,0))
            faded.paste(ov, mask=Image.fromarray(
                (np.array(ov)[:,:,3] * fade).astype(np.uint8)
            ))
            ov = faded

        bg_pil.paste(ov, (0,0), ov)

        if bar_h:
            dr = ImageDraw.Draw(bg_pil)
            dr.rectangle([0, 0, W, bar_h], fill=(0,0,0))
            dr.rectangle([0, H-bar_h, W, H], fill=(0,0,0))

        return np.array(bg_pil.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)

# ─── Build Reel ────────────────────────────────────────────────────────────────

def build_reel(script_name, output_path, images_dir, bg_music=None, letterbox=False):
    slides = SCRIPTS.get(script_name)
    if not slides:
        print(f"❌  Unknown script '{script_name}'. Available: {', '.join(SCRIPTS)}")
        sys.exit(1)

    if not os.path.isdir(images_dir):
        print(f"❌  Images folder not found: {images_dir}")
        print(f"    Use --images to point to your product photos folder.")
        sys.exit(1)

    img_list = [f for f in os.listdir(images_dir) if f.lower().endswith((".jpg",".jpeg",".png"))]
    total_s = sum(s["duration"] for s in slides)

    print(f"\n🎬  ZenPosture Reel Maker v3")
    print(f"    Script: {script_name}  |  {len(slides)} scenes  |  {total_s:.0f}s")
    print(f"    Images: {images_dir}  ({len(img_list)} photos found)")
    if letterbox:
        print(f"    Mode: Cinematic Letterbox")
    print()

    clips = []
    for i, slide in enumerate(slides):
        img_name = MOOD_FILES.get(slide["mood"], ["?"])[0]
        print(f"  🎥 Scene {i+1}/{len(slides)}: {img_name}  —  \"{slide['headline'][:30].strip()}…\"")
        clip = build_slide(slide, images_dir, letterbox)
        clips.append(clip)

    print(f"\n  🎞️  Compositing {len(clips)} scenes…")
    final = concatenate_videoclips(clips, method="compose")

    if bg_music and os.path.exists(bg_music):
        print(f"  🎵  Adding music: {os.path.basename(bg_music)}")
        audio = AudioFileClip(bg_music).volumex(0.25)
        if audio.duration < final.duration:
            from moviepy.editor import concatenate_audioclips
            loops = int(final.duration / audio.duration) + 2
            audio = concatenate_audioclips([audio] * loops)
        audio = audio.subclip(0, final.duration).audio_fadeout(2.0)
        final = final.set_audio(audio)
    elif bg_music:
        print(f"  ⚠️  Music file not found: {bg_music}")
    else:
        print(f"  💡  Add --music track.mp3 for background music")
        print(f"      Free music: https://pixabay.com/music/  (search 'motivation')")

    print(f"\n  💾  Exporting → {output_path}  (takes 2–4 min)…\n")
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        preset="medium",
        ffmpeg_params=["-crf", "17", "-pix_fmt", "yuv420p"],
        logger=None,
    )

    mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\n{'━'*52}")
    print(f"  ✅  DONE!")
    print(f"  📁  File   : {output_path}  ({mb:.1f} MB)")
    print(f"  ⏱   Length : {total_s:.0f} seconds")
    print(f"  📐  Size   : 1080×1920  (Instagram / Facebook Reels)")
    print(f"  🚀  Upload to Meta Ads Manager → Reels placement")
    print(f"{'━'*52}\n")

# ─── Interactive Custom Mode ───────────────────────────────────────────────────

def interactive_mode():
    moods = list(MOOD_FILES.keys())
    print("\n🎨  Custom Reel Builder")
    print(f"   Available image moods:\n   {', '.join(moods)}\n")
    slides = []
    idx = 1
    while True:
        print(f"─── Scene {idx} (blank headline = done) ───")
        hl = input("  Headline (use \\n for new line): ").strip().replace("\\n", "\n")
        if not hl:
            break
        sub    = input("  Subtext: ").strip().replace("\\n", "\n")
        mood   = input(f"  Image mood [{moods[0]}]: ").strip() or moods[0]
        tag    = input("  Tag label (or blank): ").strip() or None
        dur    = input("  Duration seconds [4]: ").strip()
        pos    = input("  Text position [lower/center]: ").strip() or "lower"
        is_cta = input("  CTA slide? [y/N]: ").strip().lower() == "y"
        slides.append({
            "duration": float(dur) if dur else 4.0,
            "mood":     mood if mood in MOOD_FILES else moods[0],
            "overlay":  0.50,
            "tag":      tag,
            "headline": hl,
            "sub":      sub,
            "text_pos": pos if pos in ("lower","center") else "lower",
            "accent":   EMERALD,
            "is_cta":   is_cta,
        })
        idx += 1
        print()
    if not slides:
        print("No scenes. Exiting.")
        sys.exit(0)
    SCRIPTS["__custom__"] = slides
    return "__custom__"

# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ZenPosture Cinematic Reel Maker v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python reel_maker.py --script office_worker --output office.mp4
          python reel_maker.py --script product_showcase --output showcase.mp4
          python reel_maker.py --script new_mom --music bg.mp3 --output mom.mp4
          python reel_maker.py --script pain_hook --letterbox --output pain.mp4
          python reel_maker.py --custom --output custom.mp4

        Scripts:  office_worker | pain_hook | new_mom | product_showcase
        """)
    )
    parser.add_argument("--script",   choices=list(SCRIPTS.keys()))
    parser.add_argument("--custom",   action="store_true")
    parser.add_argument("--output",   default="zenposture_reel.mp4")
    parser.add_argument("--music",    default=None)
    parser.add_argument("--letterbox",action="store_true")
    parser.add_argument("--images",   default=DEFAULT_IMAGES_DIR,
                        help="Path to your product images folder")
    parser.add_argument("--list",     action="store_true")
    args = parser.parse_args()

    print("━" * 52)
    print("  🎬  ZenPosture Cinematic Reel Maker v3")
    print("━" * 52)

    if args.list:
        print("\nAvailable scripts:\n")
        for name, slides in SCRIPTS.items():
            total = sum(s["duration"] for s in slides)
            print(f"  {name:<20} {len(slides)} scenes, {total:.0f}s")
        print()
        sys.exit(0)

    name = interactive_mode() if args.custom else args.script
    if not name:
        parser.print_help()
        print("\n💡  Try: python reel_maker.py --script office_worker --output reel.mp4\n")
        sys.exit(0)

    build_reel(name, args.output, args.images, bg_music=args.music, letterbox=args.letterbox)


if __name__ == "__main__":
    main()
