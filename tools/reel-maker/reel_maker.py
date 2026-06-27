"""
ZenPosture Cinematic Reel Maker v2
====================================
Generates Hollywood-grade branded Instagram/Facebook reels (1080x1920).

Features:
  - Real stock images auto-downloaded from Unsplash
  - Ken Burns cinematic zoom & pan effect
  - Film grain + vignette overlay
  - Cinematic color grade (teal shadows, warm highlights)
  - Smooth cross-dissolve transitions
  - Animated lower-third text with glow
  - Letterbox bars for drama (optional)
  - Background music with auto fade-out
  - Three built-in scripts + fully custom mode

Usage:
  python reel_maker.py --script office_worker --output reel.mp4
  python reel_maker.py --script new_mom --music bg.mp3 --output mom.mp4
  python reel_maker.py --script pain_hook --letterbox --output pain.mp4
  python reel_maker.py --custom --output custom.mp4
  python reel_maker.py --list
"""

import argparse
import os
import sys
import textwrap
import random
import math

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
    import numpy as np
    from moviepy.editor import (
        VideoClip, ImageClip, CompositeVideoClip,
        ColorClip, concatenate_videoclips, AudioFileClip
    )
    from moviepy.video.fx.all import fadein, fadeout, crossfadein, crossfadeout
    import requests
except ImportError as e:
    print(f"\n❌  Missing dependency: {e}\n")
    print("Run:  pip install moviepy pillow numpy requests\n")
    sys.exit(1)

# ─── Constants ─────────────────────────────────────────────────────────────────

W, H   = 1080, 1920
FPS    = 30
CACHE  = os.path.join(os.path.dirname(__file__), ".image_cache")
os.makedirs(CACHE, exist_ok=True)

# ─── Brand ────────────────────────────────────────────────────────────────────

EMERALD     = (16, 185, 129)
EMERALD_D   = (5,  150, 105)
AMBER       = (251, 191,  36)
RED         = (239,  68,  68)
WHITE       = (255, 255, 255)
DARK        = ( 15,  23,  42)
SLATE       = ( 30,  41,  59)
MUTED       = (148, 163, 184)

# ─── Unsplash image IDs per mood ──────────────────────────────────────────────
# Each list has multiple options; one is chosen randomly so videos feel unique.

MOOD_IMAGES = {
    "tired_desk": [
        "photo-1516589178581-6cd7833ae3b2",   # woman at laptop
        "photo-1541480601022-2308c0f02487",   # man at desk, tired
        "photo-1498050108023-c5249f4df085",   # laptop + coffee
    ],
    "back_pain": [
        "photo-1559757148-5c350d0d3c56",      # person holding lower back
        "photo-1544161515-4ab6ce6db874",      # back massage / pain
        "photo-1620576538906-e3cbc2b5a19c",   # stretching back
    ],
    "confident_posture": [
        "photo-1571019613454-1cb2f99b2d8b",   # athletic person standing tall
        "photo-1534438327276-14e5300c3a48",   # confident person
        "photo-1490645935967-10de6ba17061",   # healthy lifestyle
    ],
    "happy_customer": [
        "photo-1438761681033-6461ffad8d80",   # happy smiling woman
        "photo-1597586124394-fbd6ef244026",   # happy Indian woman
        "photo-1507003211169-0a1dd7228f2d",   # happy man smiling
    ],
    "product_clean": [
        "photo-1505751172876-fa1923c5c528",   # clean wellness product
        "photo-1526256262350-7da7584cf5eb",   # minimalist product
        "photo-1583947215259-38e31be8751f",   # clean flat lay
    ],
    "new_mom": [
        "photo-1555252333-9f8e92e65df9",      # mother with baby
        "photo-1519689680058-324335c77eba",   # mother and child
        "photo-1476703993599-0035a21b17a9",   # mom with newborn
    ],
    "pain_hook": [
        "photo-1516627145497-ae6968895b74",   # person with neck pain
        "photo-1559757175-0eb30cd8c063",      # stressed person at desk
        "photo-1523803326055-9729b9e02e5a",   # back tension
    ],
    "cta_end": [
        "photo-1506126613408-eca07ce68773",   # person meditating / zen
        "photo-1544367567-0f2fcb009e0b",      # yoga/wellness
        "photo-1571902943202-507ec2618e8f",   # gym / fit person
    ],
}

# ─── Script templates ─────────────────────────────────────────────────────────

SCRIPTS = {
    "office_worker": [
        {
            "duration": 3.5,
            "mood":     "tired_desk",
            "overlay":  0.55,
            "tag":      None,
            "headline": "If you sit 6+ hours a day…",
            "sub":      "watch this 👇",
            "text_pos": "center",
            "accent":   AMBER,
        },
        {
            "duration": 4.0,
            "mood":     "back_pain",
            "overlay":  0.6,
            "tag":      "THE PROBLEM",
            "headline": "Back pain.\nNeck stiffness.\nConstant fatigue.",
            "sub":      "That's what bad posture does to you — every single day.",
            "text_pos": "lower",
            "accent":   RED,
        },
        {
            "duration": 4.5,
            "mood":     "confident_posture",
            "overlay":  0.45,
            "tag":      "THE SOLUTION",
            "headline": "Meet ZenPosture.",
            "sub":      "India's most trusted posture corrector.\nFeel the difference in 60 seconds.",
            "text_pos": "lower",
            "accent":   EMERALD,
        },
        {
            "duration": 4.0,
            "mood":     "happy_customer",
            "overlay":  0.5,
            "tag":      "REAL RESULTS",
            "headline": "⭐⭐⭐⭐⭐",
            "sub":      '"Back pain gone in just 1 week."\n— Priya S., Mumbai · Verified Buyer',
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 4.0,
            "mood":     "product_clean",
            "overlay":  0.5,
            "tag":      "LIMITED OFFER",
            "headline": "🔥 Starting at ₹499",
            "sub":      "Free Shipping · Cash on Delivery\n30-Day Money-Back Guarantee",
            "text_pos": "lower",
            "accent":   RED,
        },
        {
            "duration": 4.0,
            "mood":     "cta_end",
            "overlay":  0.45,
            "tag":      None,
            "headline": "Fix your posture today.",
            "sub":      "👆  zenposture.in\nLink in bio",
            "text_pos": "center",
            "accent":   EMERALD,
            "is_cta":   True,
        },
    ],

    "pain_hook": [
        {
            "duration": 3.0,
            "mood":     "pain_hook",
            "overlay":  0.65,
            "tag":      None,
            "headline": "Your back pain\nisn't normal.",
            "sub":      "It's fixable. 🔥",
            "text_pos": "center",
            "accent":   RED,
        },
        {
            "duration": 4.0,
            "mood":     "tired_desk",
            "overlay":  0.6,
            "tag":      "THE TRUTH",
            "headline": "8 hours of sitting\nis destroying\nyour spine.",
            "sub":      "Slowly. Every. Single. Day.",
            "text_pos": "lower",
            "accent":   RED,
        },
        {
            "duration": 4.0,
            "mood":     "confident_posture",
            "overlay":  0.45,
            "tag":      "THE FIX",
            "headline": "ZenPosture fixes it\nin DAYS.",
            "sub":      "10,000+ Indians already know. Now you do too.",
            "text_pos": "lower",
            "accent":   EMERALD,
        },
        {
            "duration": 3.5,
            "mood":     "product_clean",
            "overlay":  0.5,
            "tag":      "OFFER",
            "headline": "₹499 · Free Shipping\nPay on Delivery",
            "sub":      "30-Day Guarantee. Zero risk.",
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 3.5,
            "mood":     "cta_end",
            "overlay":  0.45,
            "tag":      None,
            "headline": "Be next. 💚",
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
            "overlay":  0.5,
            "tag":      None,
            "headline": "New moms —\nnobody talks about\nTHIS after delivery.",
            "sub":      "💚",
            "text_pos": "center",
            "accent":   EMERALD,
        },
        {
            "duration": 4.5,
            "mood":     "back_pain",
            "overlay":  0.6,
            "tag":      "THE REALITY",
            "headline": "Weak core.\nAching back.\nAll day, every day.",
            "sub":      "Lifting, feeding, carrying — and your body is still healing.",
            "text_pos": "lower",
            "accent":   RED,
        },
        {
            "duration": 5.0,
            "mood":     "confident_posture",
            "overlay":  0.45,
            "tag":      "THE SOLUTION",
            "headline": "ZenPosture\nPostpartum Belt.",
            "sub":      "Supports your core while your body heals.\nBreathable. Adjustable. Made for India.",
            "text_pos": "lower",
            "accent":   EMERALD,
        },
        {
            "duration": 4.0,
            "mood":     "happy_customer",
            "overlay":  0.5,
            "tag":      "REAL MOM · REAL RESULTS",
            "headline": "⭐⭐⭐⭐⭐",
            "sub":      '"Felt supported from Day 1.\nEvery new mom needs this."\n— Ananya P., Delhi',
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 3.5,
            "mood":     "product_clean",
            "overlay":  0.5,
            "tag":      "GIFT IT",
            "headline": "Starting at ₹599\nCOD · Free Shipping",
            "sub":      "30-Day Guarantee",
            "text_pos": "lower",
            "accent":   AMBER,
        },
        {
            "duration": 3.5,
            "mood":     "cta_end",
            "overlay":  0.4,
            "tag":      None,
            "headline": "Gift it to someone\nwho needs it. 💚",
            "sub":      "👆  zenposture.in",
            "text_pos": "center",
            "accent":   EMERALD,
            "is_cta":   True,
        },
    ],
}

# ─── Image Downloader ─────────────────────────────────────────────────────────

def download_image(photo_id, width=1200, height=2000):
    cache_path = os.path.join(CACHE, f"{photo_id}_{width}x{height}.jpg")
    if os.path.exists(cache_path):
        return cache_path

    url = (
        f"https://images.unsplash.com/{photo_id}"
        f"?w={width}&h={height}&fit=crop&crop=center&q=85&auto=format"
    )
    print(f"    📥 Downloading image: {photo_id[:30]}…")
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "ZenPostureReelMaker/2.0"})
        r.raise_for_status()
        with open(cache_path, "wb") as f:
            f.write(r.content)
        return cache_path
    except Exception as e:
        print(f"    ⚠️  Could not download image ({e}). Using gradient fallback.")
        return None


def get_mood_image(mood):
    ids = MOOD_IMAGES.get(mood, [])
    if not ids:
        return None
    photo_id = random.choice(ids)
    return download_image(photo_id)

# ─── Image Processing ─────────────────────────────────────────────────────────

def load_and_fit(path, w, h):
    """Load image, resize to fill canvas (center crop), return numpy array."""
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    img = img.crop((x, y, x + w, y + h))
    return np.array(img)


def color_grade(frame_np):
    """Cinematic teal-orange color grade."""
    img = Image.fromarray(frame_np)

    # Split channels
    r, g, b = img.split()

    # Shadows → teal (boost blue/green in darks)
    r_arr = np.array(r, dtype=np.float32)
    g_arr = np.array(g, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)

    # Teal shadows: reduce red slightly in dark areas
    shadow_mask = (r_arr + g_arr + b_arr) / 3 < 128
    r_arr[shadow_mask] *= 0.88
    g_arr[shadow_mask] *= 0.97
    b_arr[shadow_mask] *= 1.08

    # Warm highlights: boost red/green in bright areas
    highlight_mask = (r_arr + g_arr + b_arr) / 3 > 180
    r_arr[highlight_mask] = np.clip(r_arr[highlight_mask] * 1.06, 0, 255)
    g_arr[highlight_mask] = np.clip(g_arr[highlight_mask] * 1.02, 0, 255)
    b_arr[highlight_mask] = np.clip(b_arr[highlight_mask] * 0.95, 0, 255)

    # Slight desaturation for cinematic feel
    gray = (r_arr * 0.299 + g_arr * 0.587 + b_arr * 0.114)
    saturation = 0.85
    r_arr = np.clip(gray + (r_arr - gray) * saturation, 0, 255)
    g_arr = np.clip(gray + (g_arr - gray) * saturation, 0, 255)
    b_arr = np.clip(gray + (b_arr - gray) * saturation, 0, 255)

    result = np.stack([r_arr, g_arr, b_arr], axis=2).astype(np.uint8)
    return result


def add_vignette(frame_np, strength=0.6):
    """Add cinematic vignette (dark edges)."""
    h, w = frame_np.shape[:2]
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    vignette = 1 - np.clip(dist * strength, 0, 1)
    vignette = vignette[:, :, np.newaxis]
    result = (frame_np * vignette).astype(np.uint8)
    return result


def add_grain(frame_np, amount=8):
    """Add subtle film grain."""
    noise = np.random.randint(-amount, amount, frame_np.shape, dtype=np.int16)
    result = np.clip(frame_np.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return result


def ken_burns(img_np, t, duration, zoom_dir=1, pan_x=0.05, pan_y=0.03):
    """
    Ken Burns effect: slow zoom + subtle pan.
    zoom_dir: 1 = zoom in, -1 = zoom out
    """
    h, w = img_np.shape[:2]
    progress = t / max(duration, 0.001)

    zoom_start = 1.0 if zoom_dir > 0 else 1.15
    zoom_end   = 1.15 if zoom_dir > 0 else 1.0
    zoom = zoom_start + (zoom_end - zoom_start) * progress

    # Pan direction
    ox = pan_x * progress * (w * (zoom - 1) / zoom)
    oy = pan_y * progress * (h * (zoom - 1) / zoom)

    # Crop size
    cw = int(w / zoom)
    ch = int(h / zoom)

    x1 = int((w - cw) / 2 + ox)
    y1 = int((h - ch) / 2 + oy)
    x1 = max(0, min(x1, w - cw))
    y1 = max(0, min(y1, h - ch))

    cropped = img_np[y1:y1+ch, x1:x1+cw]
    pil = Image.fromarray(cropped).resize((w, h), Image.BILINEAR)
    return np.array(pil)


# ─── Font Loading ──────────────────────────────────────────────────────────────

def load_font(size, bold=False):
    candidates = [
        f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf",
        f"C:/Windows/Fonts/{'calibrib' if bold else 'calibri'}.ttf",
        f"/System/Library/Fonts/Supplemental/{'Arial Bold' if bold else 'Arial'}.ttf",
        f"/System/Library/Fonts/{'Helvetica-Bold' if bold else 'Helvetica'}.ttc",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
        f"/usr/share/fonts/truetype/freefont/FreeSans{'Bold' if bold else ''}.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ─── Text Rendering ────────────────────────────────────────────────────────────

def draw_text_with_shadow(draw, text, x, y, font, color, shadow_color=(0,0,0), shadow_offset=3, alpha=255):
    """Draw text with drop shadow for depth."""
    # Glow / shadow (multiple passes for soft glow)
    for dx in range(-shadow_offset, shadow_offset+1, shadow_offset):
        for dy in range(-shadow_offset, shadow_offset+1, shadow_offset):
            if dx or dy:
                draw.text((x+dx, y+dy), text, font=font, fill=(*shadow_color, 160))
    draw.text((x, y), text, font=font, fill=(*color, alpha))


def wrap_lines(text, max_chars=20):
    """Split text on \n then wrap long lines."""
    result = []
    for line in text.split("\n"):
        wrapped = textwrap.wrap(line, width=max_chars) or [""]
        result.extend(wrapped)
    return result


def render_text_block(draw, text, center_y, font, color, canvas_w, line_spacing=1.25, alpha=255):
    """Render centered text block with shadow. Returns bottom y."""
    lines = wrap_lines(text, max_chars=22)
    line_height = font.size if hasattr(font, 'size') else 60
    total_h = len(lines) * int(line_height * line_spacing)
    y = center_y - total_h // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (canvas_w - lw) // 2
        draw_text_with_shadow(draw, line, x, y, font, color, alpha=alpha)
        y += int(lh * line_spacing)

    return y


def render_slide_overlay(slide, progress, fade_alpha):
    """
    Render the text/UI overlay for one slide as an RGBA PIL Image.
    progress: 0→1 within the slide (for text animation)
    fade_alpha: 0→255 (for transitions)
    """
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    text_pos  = slide.get("text_pos", "lower")
    accent    = slide.get("accent", WHITE)
    headline  = slide.get("headline", "")
    sub       = slide.get("sub", "")
    tag       = slide.get("tag")
    is_cta    = slide.get("is_cta", False)
    ov_alpha  = int(slide.get("overlay", 0.5) * 255)

    # Darkness overlay (gradient — heavier at bottom for lower text)
    if text_pos == "lower":
        for y in range(H):
            t = max(0, (y - H * 0.35) / (H * 0.65))
            a = int(ov_alpha * min(t * 1.4, 1))
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    else:
        # full overlay for center text
        for y in range(H):
            t = 0.5 + 0.5 * math.sin(math.pi * y / H)
            a = int(ov_alpha * 0.85 * t)
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, a))

    # Text animation: slide up from slight offset
    text_anim_offset = int((1 - min(progress * 2.5, 1)) * 60)

    # ── BRAND LOGO (top) ──
    font_logo = load_font(40, bold=True)
    logo_text = "ZENPOSTURE"
    bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
    lw = bbox[2] - bbox[0]
    draw_text_with_shadow(
        draw, logo_text,
        (W - lw) // 2, 80,
        font_logo, WHITE,
        alpha=int(fade_alpha * 0.7)
    )

    # ── TAG LABEL ──
    if tag:
        font_tag = load_font(28, bold=True)
        tag_w = draw.textbbox((0, 0), tag, font=font_tag)[2]
        tag_x = (W - tag_w) // 2
        # Pill background
        pad = 12
        pill_rect = [tag_x - pad, 140, tag_x + tag_w + pad, 140 + 38]
        draw.rectangle(pill_rect, fill=(*accent, 200))
        draw.text((tag_x, 144), tag, font=font_tag, fill=(*DARK, 255))

    # ── MAIN HEADLINE ──
    if text_pos == "lower":
        headline_y = H - 480 + text_anim_offset
    else:
        headline_y = H // 2 - 120 + text_anim_offset

    font_h = load_font(84, bold=True)
    font_h_small = load_font(68, bold=True)
    lines = wrap_lines(headline, max_chars=18)
    h_font = font_h if max(len(l) for l in lines) <= 14 else font_h_small

    y = headline_y
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=h_font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (W - lw) // 2
        # Alternate accent color on first line
        color = accent if i == 0 else WHITE
        draw_text_with_shadow(draw, line, x, y, h_font, color, shadow_offset=4,
                               alpha=int(fade_alpha))
        y += int(lh * 1.2)

    # ── SUBTEXT ──
    if sub:
        sub_y = y + 20 + text_anim_offset // 2
        font_sub = load_font(38)
        sub_alpha = int(fade_alpha * 0.85)
        for line in wrap_lines(sub, max_chars=30):
            bbox = draw.textbbox((0, 0), line, font=font_sub)
            lw_s = bbox[2] - bbox[0]
            lh_s = bbox[3] - bbox[1]
            draw_text_with_shadow(draw, line, (W - lw_s) // 2, sub_y,
                                   font_sub, MUTED, alpha=sub_alpha)
            sub_y += int(lh_s * 1.3)

    # ── CTA END CARD ──
    if is_cta:
        cta_y = H - 200
        bar_h = 110
        draw.rectangle([0, cta_y, W, cta_y + bar_h], fill=(*accent, 220))
        font_cta = load_font(44, bold=True)
        cta_text = "🛒  Shop Now →  zenposture.in"
        bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
        cw_ = bbox[2] - bbox[0]
        draw.text(((W - cw_) // 2, cta_y + 30), cta_text, font=font_cta,
                   fill=(*DARK, 255))

    # ── BOTTOM TRUST LINE ──
    if not is_cta:
        trust = "Free Shipping  ·  COD Available  ·  30-Day Guarantee"
        font_trust = load_font(30)
        bbox = draw.textbbox((0, 0), trust, font=font_trust)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, H - 80), trust, font=font_trust,
                   fill=(*WHITE, int(fade_alpha * 0.5)))

    return overlay


# ─── Slide Clip Builder ────────────────────────────────────────────────────────

def build_slide_clip(slide, letterbox=False):
    duration = slide["duration"]
    mood     = slide["mood"]

    # Download/load background image
    img_path = get_mood_image(mood)
    if img_path:
        raw = load_and_fit(img_path, W, H)
    else:
        # Gradient fallback
        raw = np.zeros((H, W, 3), dtype=np.uint8)
        for y in range(H):
            t = y / H
            raw[y, :] = [
                int(DARK[0] * (1-t) + SLATE[0] * t),
                int(DARK[1] * (1-t) + SLATE[1] * t),
                int(DARK[2] * (1-t) + SLATE[2] * t),
            ]

    # Pre-process image
    raw = color_grade(raw)
    raw = add_vignette(raw, strength=0.65)

    # Ken Burns params (randomize direction per slide)
    zoom_dir = random.choice([1, -1])
    pan_x    = random.uniform(-0.04, 0.04)
    pan_y    = random.uniform(-0.02, 0.02)

    # Letterbox bars
    bar_h = int(H * 0.08) if letterbox else 0

    def make_frame(t):
        progress = t / duration

        # Fade in/out alpha
        fade_in  = min(t / 0.4, 1.0)
        fade_out = min((duration - t) / 0.4, 1.0)
        fade     = min(fade_in, fade_out)
        text_alpha = int(fade * 255)

        # Ken Burns
        bg = ken_burns(raw, t, duration, zoom_dir, pan_x, pan_y)

        # Grain (subtle, varies per frame)
        if t % 0.1 < 0.033:  # don't recalculate every frame
            bg = add_grain(bg, amount=6)

        # Composite text overlay
        bg_pil = Image.fromarray(bg)
        overlay = render_slide_overlay(slide, progress, text_alpha)
        bg_pil.paste(overlay, (0, 0), overlay)

        # Letterbox
        if bar_h > 0:
            draw = ImageDraw.Draw(bg_pil)
            draw.rectangle([0, 0, W, bar_h], fill=(0, 0, 0))
            draw.rectangle([0, H - bar_h, W, H], fill=(0, 0, 0))

        return np.array(bg_pil.convert("RGB"))

    clip = VideoClip(make_frame, duration=duration).set_fps(FPS)
    return clip


# ─── Reel Builder ─────────────────────────────────────────────────────────────

def build_reel(script_name, output_path, bg_music=None, letterbox=False):
    slides = SCRIPTS.get(script_name)
    if not slides:
        print(f"❌  Unknown script '{script_name}'. Available: {', '.join(SCRIPTS)}")
        sys.exit(1)

    total = sum(s["duration"] for s in slides)
    print(f"\n🎬  Building CINEMATIC reel: {script_name}")
    print(f"    {len(slides)} scenes · {total:.0f}s · 1080×1920 · {FPS}fps\n")

    clips = []
    for i, slide in enumerate(slides):
        print(f"  🎥 Scene {i+1}/{len(slides)}: [{slide['mood']}] {slide['headline'][:35].strip()}…")
        clip = build_slide_clip(slide, letterbox=letterbox)
        # Cross-dissolve: fade out each clip slightly
        clip = fadeout(fadein(clip, 0.4), 0.4)
        clips.append(clip)

    print(f"\n  🎞️  Compositing {len(clips)} scenes…")
    final = concatenate_videoclips(clips, method="compose")

    # Background music
    if bg_music and os.path.exists(bg_music):
        print(f"  🎵  Adding music: {bg_music}")
        audio = AudioFileClip(bg_music).volumex(0.28)
        if audio.duration < final.duration:
            # Loop music
            loops = int(final.duration / audio.duration) + 2
            from moviepy.editor import concatenate_audioclips
            audio = concatenate_audioclips([audio] * loops)
        audio = audio.subclip(0, final.duration)
        # Fade out last 2s
        audio = audio.audio_fadeout(2.0)
        final = final.set_audio(audio)
    else:
        if bg_music:
            print(f"  ⚠️  Music file not found: {bg_music}")
        print(f"  💡  Tip: Add --music your_song.mp3 for background music")
        print(f"      Free music: https://pixabay.com/music/ (search 'motivation')")

    print(f"\n  💾  Exporting → {output_path}")
    print(f"      This may take 1-3 minutes…\n")

    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger=None,
    )

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\n{'━'*50}")
    print(f"  ✅  DONE!  {output_path}")
    print(f"  📁  Size:  {size_mb:.1f} MB")
    print(f"  ⏱   Duration: {total:.0f} seconds")
    print(f"  📐  Resolution: 1080×1920 (Instagram/Facebook Reels)")
    print(f"  🚀  Ready to upload to Meta Ads Manager!")
    print(f"{'━'*50}\n")


# ─── Interactive Custom Builder ───────────────────────────────────────────────

def interactive_build():
    print("\n🎨  ZenPosture Custom Reel Builder")
    print(f"   Available moods: {', '.join(MOOD_IMAGES.keys())}\n")

    slides = []
    idx = 1
    while True:
        print(f"─── Scene {idx} (press ENTER on 'headline' to finish) ───")
        headline = input("  Headline text (use \\n for line breaks): ").strip()
        if not headline:
            break
        headline = headline.replace("\\n", "\n")
        sub      = input("  Subtext: ").strip().replace("\\n", "\n")
        mood     = input(f"  Mood [{'/'.join(MOOD_IMAGES.keys())}]: ").strip()
        if mood not in MOOD_IMAGES:
            mood = list(MOOD_IMAGES.keys())[0]
        tag      = input("  Tag label (e.g. THE PROBLEM) or blank: ").strip() or None
        dur      = input("  Duration seconds [4]: ").strip()
        pos      = input("  Text position [lower/center]: ").strip() or "lower"
        is_cta   = input("  Is this the final CTA slide? [y/N]: ").strip().lower() == "y"

        slides.append({
            "duration": float(dur) if dur else 4.0,
            "mood":     mood,
            "overlay":  0.55,
            "tag":      tag,
            "headline": headline,
            "sub":      sub,
            "text_pos": pos if pos in ("lower", "center") else "lower",
            "accent":   EMERALD,
            "is_cta":   is_cta,
        })
        idx += 1
        print()

    if not slides:
        print("No scenes entered.")
        sys.exit(0)

    SCRIPTS["__custom__"] = slides
    return "__custom__"


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ZenPosture Cinematic Reel Maker v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python reel_maker.py --script office_worker --output office.mp4
          python reel_maker.py --script new_mom --music bg.mp3 --output mom.mp4
          python reel_maker.py --script pain_hook --letterbox --output pain.mp4
          python reel_maker.py --custom --output my_reel.mp4
          python reel_maker.py --list

        Free background music:
          https://pixabay.com/music/ → search "motivation" or "cinematic"
          Download MP3 and pass with --music your_track.mp3
        """),
    )
    parser.add_argument("--script", choices=list(SCRIPTS.keys()), help="Script template")
    parser.add_argument("--custom", action="store_true", help="Build custom slides interactively")
    parser.add_argument("--output", default="zenposture_reel.mp4", help="Output MP4 path")
    parser.add_argument("--music",  default=None, help="Background music MP3 path")
    parser.add_argument("--letterbox", action="store_true", help="Add cinematic letterbox bars")
    parser.add_argument("--list", action="store_true", help="List available scripts")
    args = parser.parse_args()

    print("━" * 50)
    print("  🎬  ZenPosture Cinematic Reel Maker v2")
    print("━" * 50)

    if args.list:
        print("\nAvailable scripts:\n")
        for name, slides in SCRIPTS.items():
            total = sum(s["duration"] for s in slides)
            print(f"  {name:<20} {len(slides)} scenes, {total:.0f}s")
        print()
        sys.exit(0)

    if args.custom:
        name = interactive_build()
    elif args.script:
        name = args.script
    else:
        parser.print_help()
        print("\n💡  Try: python reel_maker.py --script office_worker --output reel.mp4\n")
        sys.exit(0)

    build_reel(name, args.output, bg_music=args.music, letterbox=args.letterbox)


if __name__ == "__main__":
    main()
