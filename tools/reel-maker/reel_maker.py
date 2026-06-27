"""
ZenPosture Reel Maker
=====================
Generates branded Instagram/Facebook reels (1080x1920) from script templates.

Usage:
  python reel_maker.py --script office_worker --output my_reel.mp4
  python reel_maker.py --script new_mom --output mom_reel.mp4
  python reel_maker.py --script pain_hook --output pain_reel.mp4
  python reel_maker.py --custom --output custom_reel.mp4   (interactive mode)

Requirements:
  pip install moviepy pillow requests
  Also needs: ffmpeg installed on your system
"""

import argparse
import os
import sys
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np
    from moviepy.editor import (
        VideoClip, ImageClip, CompositeVideoClip,
        TextClip, ColorClip, concatenate_videoclips,
        AudioFileClip, CompositeAudioClip
    )
    from moviepy.video.fx.all import fadein, fadeout
except ImportError:
    print("\n❌  Missing dependencies. Run this first:\n")
    print("    pip install moviepy pillow numpy\n")
    sys.exit(1)

# ─── Brand Config ─────────────────────────────────────────────────────────────

BRAND = {
    "primary":      (16, 185, 129),   # emerald-500
    "primary_dark": (5,  150, 105),   # emerald-600
    "dark_bg":      (15,  23,  42),   # slate-900
    "white":        (255, 255, 255),
    "amber":        (251, 191,  36),
    "red":          (239,  68,  68),
    "text_muted":   (148, 163, 184),  # slate-400
}

CANVAS_W, CANVAS_H = 1080, 1920
FPS = 30

# ─── Script Templates ──────────────────────────────────────────────────────────

SCRIPTS = {
    "office_worker": [
        {
            "duration": 3,
            "style":    "hook",
            "line1":    "If you sit at a desk",
            "line2":    "for 6+ hours a day...",
            "line3":    "watch this. 👇",
            "bg":       "dark",
        },
        {
            "duration": 4,
            "style":    "problem",
            "line1":    "Back pain. Neck stiffness.",
            "line2":    "Constant fatigue.",
            "line3":    "That's what bad posture does.",
            "bg":       "dark",
        },
        {
            "duration": 4,
            "style":    "solution",
            "line1":    "Meet ZenPosture ✅",
            "line2":    "India's most trusted",
            "line3":    "posture corrector.",
            "bg":       "brand",
        },
        {
            "duration": 4,
            "style":    "proof",
            "line1":    "⭐⭐⭐⭐⭐",
            "line2":    '"Back pain gone in 1 week"',
            "line3":    "— Priya, Mumbai · Verified Buyer",
            "bg":       "dark",
        },
        {
            "duration": 4,
            "style":    "offer",
            "line1":    "🔥 Starting at just ₹499",
            "line2":    "Free Shipping · COD Available",
            "line3":    "30-Day Money-Back Guarantee",
            "bg":       "dark",
        },
        {
            "duration": 4,
            "style":    "cta",
            "line1":    "Fix your posture today.",
            "line2":    "👆 zenposture.in",
            "line3":    "Link in bio →",
            "bg":       "brand",
        },
    ],

    "pain_hook": [
        {
            "duration": 3,
            "style":    "hook",
            "line1":    "Your back pain",
            "line2":    "isn't normal.",
            "line3":    "It's fixable. 🔥",
            "bg":       "dark",
        },
        {
            "duration": 4,
            "style":    "problem",
            "line1":    "8 hours of sitting",
            "line2":    "is destroying your spine.",
            "line3":    "Slowly. Every. Day.",
            "bg":       "dark",
        },
        {
            "duration": 4,
            "style":    "solution",
            "line1":    "ZenPosture fixes it",
            "line2":    "in DAYS. Not months.",
            "line3":    "10,000+ Indians already know.",
            "bg":       "brand",
        },
        {
            "duration": 4,
            "style":    "offer",
            "line1":    "₹499 onwards",
            "line2":    "Pay on Delivery · Free Shipping",
            "line3":    "30-Day Guarantee",
            "bg":       "dark",
        },
        {
            "duration": 3,
            "style":    "cta",
            "line1":    "Be next. 💚",
            "line2":    "👆 zenposture.in",
            "line3":    "Shop Now →",
            "bg":       "brand",
        },
    ],

    "new_mom": [
        {
            "duration": 4,
            "style":    "hook",
            "line1":    "New moms —",
            "line2":    "no one talks about THIS",
            "line3":    "after delivery. 💚",
            "bg":       "dark",
        },
        {
            "duration": 5,
            "style":    "problem",
            "line1":    "Weak core. Aching back.",
            "line2":    "Lifting, feeding, carrying",
            "line3":    "— all day, every day.",
            "bg":       "dark",
        },
        {
            "duration": 5,
            "style":    "solution",
            "line1":    "ZenPosture Postpartum Belt",
            "line2":    "Supports your core",
            "line3":    "while your body heals. ✅",
            "bg":       "brand",
        },
        {
            "duration": 4,
            "style":    "proof",
            "line1":    "⭐⭐⭐⭐⭐",
            "line2":    '"Felt supported from Day 1."',
            "line3":    "— Ananya, Delhi · New Mom",
            "bg":       "dark",
        },
        {
            "duration": 4,
            "style":    "offer",
            "line1":    "Breathable · Adjustable",
            "line2":    "Comfortable in Indian summers",
            "line3":    "Starting at ₹599 · COD",
            "bg":       "dark",
        },
        {
            "duration": 3,
            "style":    "cta",
            "line1":    "Gift it to someone",
            "line2":    "who needs it. 💚",
            "line3":    "👆 zenposture.in",
            "bg":       "brand",
        },
    ],
}

# ─── Frame Renderer ────────────────────────────────────────────────────────────

def make_gradient_bg(w, h, top_color, bottom_color):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def load_font(size, bold=False):
    font_paths = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/System/Library/Fonts/{'Helvetica-Bold' if bold else 'Helvetica'}.ttc",
        f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_text_centered(draw, text, y, font, color, canvas_w, max_w=900, line_height=1.3):
    lines = textwrap.wrap(text, width=22)
    total_h = 0
    rendered = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        rendered.append((line, lw, lh))
        total_h += int(lh * line_height)

    cur_y = y
    for line, lw, lh in rendered:
        x = (canvas_w - lw) // 2
        # shadow
        draw.text((x + 2, cur_y + 2), line, font=font, fill=(0, 0, 0, 80))
        draw.text((x, cur_y), line, font=font, fill=color)
        cur_y += int(lh * line_height)
    return cur_y


def render_card(slide, progress=0.0):
    """Render a single slide as a PIL image. progress 0→1 for animations."""
    bg_type = slide.get("bg", "dark")

    if bg_type == "brand":
        top = BRAND["primary"]
        bot = BRAND["primary_dark"]
    else:
        top = BRAND["dark_bg"]
        bot = (30, 41, 59)  # slate-800

    img = make_gradient_bg(CANVAS_W, CANVAS_H, top, bot)
    draw = ImageDraw.Draw(img, "RGBA")

    # Decorative circle top-right
    circle_size = 500
    circle_img = Image.new("RGBA", (circle_size, circle_size), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(circle_img)
    circle_color = (*BRAND["white"], 12)
    cdraw.ellipse([0, 0, circle_size, circle_size], fill=circle_color)
    img.paste(circle_img, (CANVAS_W - circle_size // 2, -circle_size // 4), circle_img)

    # Decorative circle bottom-left
    circle2 = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    c2draw = ImageDraw.Draw(circle2)
    c2draw.ellipse([0, 0, 400, 400], fill=(*BRAND["primary"], 20))
    img.paste(circle2, (-100, CANVAS_H - 300), circle2)

    # ZenPosture brand tag top
    font_brand = load_font(36, bold=True)
    brand_text = "ZenPosture"
    bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
    bw = bbox[2] - bbox[0]
    draw.text(((CANVAS_W - bw) // 2, 100), brand_text, font=font_brand,
              fill=(*BRAND["white"], 180))

    style = slide.get("style", "default")

    # Style-specific accent
    if style == "hook":
        accent_color = BRAND["amber"]
    elif style == "problem":
        accent_color = BRAND["red"]
    elif style in ("solution", "cta"):
        accent_color = BRAND["white"]
    elif style == "proof":
        accent_color = BRAND["amber"]
    elif style == "offer":
        accent_color = BRAND["primary"]
    else:
        accent_color = BRAND["white"]

    # Animate: slide in from bottom using progress
    anim_offset = int((1 - min(progress * 3, 1)) * 80)

    font_l1 = load_font(72, bold=True)
    font_l2 = load_font(62, bold=True)
    font_l3 = load_font(44, bold=False)

    center_start = CANVAS_H // 2 - 180 + anim_offset

    # Line 1
    next_y = draw_text_centered(draw, slide["line1"], center_start,
                                 font_l1, accent_color, CANVAS_W)

    # Line 2
    if slide.get("line2"):
        next_y = draw_text_centered(draw, slide["line2"], next_y + 20,
                                     font_l2, BRAND["white"], CANVAS_W)

    # Line 3
    if slide.get("line3"):
        draw_text_centered(draw, slide["line3"], next_y + 30,
                           font_l3, (*BRAND["text_muted"], 230), CANVAS_W)

    # Bottom bar
    if style == "cta":
        bar_h = 120
        bar_img = Image.new("RGBA", (CANVAS_W, bar_h), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(bar_img)
        bdraw.rectangle([0, 0, CANVAS_W, bar_h], fill=(*BRAND["white"], 30))
        font_cta = load_font(40, bold=True)
        cta_text = "🛒 Shop Now → zenposture.in"
        bbox = bdraw.textbbox((0, 0), cta_text, font=font_cta)
        tw = bbox[2] - bbox[0]
        bdraw.text(((CANVAS_W - tw) // 2, 38), cta_text, font=font_cta,
                   fill=BRAND["white"])
        img.paste(bar_img, (0, CANVAS_H - bar_h - 80), bar_img)

    return np.array(img)


# ─── Clip Builder ──────────────────────────────────────────────────────────────

def build_clip_for_slide(slide, index):
    duration = slide["duration"]

    def make_frame(t):
        progress = t / duration
        return render_card(slide, progress)

    clip = VideoClip(make_frame, duration=duration).set_fps(FPS)

    # Fade in/out
    clip = fadein(clip, 0.3)
    clip = fadeout(clip, 0.3)

    return clip


def build_reel(script_name, output_path, bg_music=None):
    slides = SCRIPTS.get(script_name)
    if not slides:
        print(f"❌  Unknown script: {script_name}")
        print(f"   Available: {', '.join(SCRIPTS.keys())}")
        sys.exit(1)

    print(f"\n🎬  Building reel: {script_name}")
    print(f"    {len(slides)} slides | {sum(s['duration'] for s in slides)}s total\n")

    clips = []
    for i, slide in enumerate(slides):
        print(f"  ⏳ Rendering slide {i+1}/{len(slides)}: {slide['line1'][:30]}...")
        clip = build_clip_for_slide(slide, i)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")

    if bg_music and os.path.exists(bg_music):
        print(f"  🎵 Adding background music: {bg_music}")
        audio = AudioFileClip(bg_music).volumex(0.3)
        if audio.duration > final.duration:
            audio = audio.subclip(0, final.duration)
        final = final.set_audio(audio)

    print(f"\n  💾 Exporting → {output_path}")
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        preset="medium",
        ffmpeg_params=["-crf", "18"],
        logger=None,
    )

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    total_s = sum(s["duration"] for s in slides)
    print(f"\n✅  Done! {output_path} ({size_mb:.1f} MB, {total_s}s)")
    print(f"   Ready to upload to Instagram / Facebook Ads 🚀\n")


# ─── Interactive Custom Mode ───────────────────────────────────────────────────

def interactive_mode():
    print("\n🎨  ZenPosture Custom Reel Builder")
    print("   Enter your slides. Press ENTER twice when done.\n")

    slides = []
    while True:
        print(f"─── Slide {len(slides)+1} ───")
        line1 = input("  Line 1 (headline): ").strip()
        if not line1:
            break
        line2 = input("  Line 2 (subtext):  ").strip()
        line3 = input("  Line 3 (detail):   ").strip()
        duration = input("  Duration (seconds) [default 4]: ").strip()
        bg = input("  Background [dark/brand, default dark]: ").strip() or "dark"
        style = input("  Style [hook/problem/solution/proof/offer/cta, default hook]: ").strip() or "hook"

        slides.append({
            "line1": line1,
            "line2": line2,
            "line3": line3,
            "duration": int(duration) if duration.isdigit() else 4,
            "bg": bg if bg in ("dark", "brand") else "dark",
            "style": style,
        })
        print()

    if not slides:
        print("No slides entered. Exiting.")
        sys.exit(0)

    # Temporarily register the custom script
    SCRIPTS["__custom__"] = slides
    return "__custom__"


# ─── CLI Entry ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ZenPosture Reel Maker — Generate branded Instagram/Facebook reels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python reel_maker.py --script office_worker --output office.mp4
          python reel_maker.py --script new_mom --output mom.mp4
          python reel_maker.py --script pain_hook --output pain.mp4
          python reel_maker.py --custom --output my_custom.mp4
          python reel_maker.py --script office_worker --music background.mp3 --output office.mp4

        Available scripts:
          office_worker  — Targets desk workers with back/neck pain
          pain_hook      — Aggressive cold-audience hook (15-20s)
          new_mom        — Targets postpartum recovery audience
        """)
    )
    parser.add_argument("--script", choices=list(SCRIPTS.keys()),
                        help="Script template to use")
    parser.add_argument("--custom", action="store_true",
                        help="Interactive custom slide builder")
    parser.add_argument("--output", default="zenposture_reel.mp4",
                        help="Output file path (default: zenposture_reel.mp4)")
    parser.add_argument("--music", default=None,
                        help="Path to background music MP3 (optional)")
    parser.add_argument("--list", action="store_true",
                        help="List available script templates")

    args = parser.parse_args()

    print("━" * 50)
    print("  🧘 ZenPosture Reel Maker")
    print("━" * 50)

    if args.list:
        print("\nAvailable scripts:\n")
        for name, slides in SCRIPTS.items():
            total = sum(s["duration"] for s in slides)
            print(f"  {name:<20} {len(slides)} slides, {total}s")
        print()
        sys.exit(0)

    if args.custom:
        script_name = interactive_mode()
    elif args.script:
        script_name = args.script
    else:
        parser.print_help()
        print("\n💡 Tip: use --script or --custom to get started\n")
        sys.exit(0)

    build_reel(script_name, args.output, args.music)


if __name__ == "__main__":
    main()
