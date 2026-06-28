"""
ZenPosture Cinematic Reel Maker v5  —  Agency Edition
======================================================
Improvements over v4:
  1. Montserrat Bold font auto-downloaded (vs ugly default bitmap font)
  2. Semi-transparent text bg bar on EVERY text block (always readable)
  3. Ken Burns on ALL scenes including customer photos (nothing is static)
  4. Bundled royalty-free MP3 from Mixkit auto-downloaded as default music
  5. zenposture.in URL visible on CTA + amber color
  6. Scene durations tightened: hook 2.5s, pain 3.0s, reveal 4.5s, CTA 3.5s
  7. Burned-in caption subtitle on every scene (mute-watchable)

Usage:
  python reel_maker.py --script office_worker --output reel.mp4
  python reel_maker.py --script new_mom       --output mom.mp4
  python reel_maker.py --script pain_hook     --output pain.mp4
  python reel_maker.py --script showcase      --output showcase.mp4
  python reel_maker.py --music track.mp3 --script office_worker --output reel.mp4
  python reel_maker.py --list
"""

import argparse, os, sys, textwrap, random, math
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    from moviepy.editor import VideoClip, AudioFileClip, concatenate_videoclips
    from moviepy.video.fx.all import fadein, fadeout
    from moviepy.audio.AudioClip import AudioArrayClip
except ImportError as e:
    print(f"\n❌  Missing dependency: {e}")
    print("Run:  pip install moviepy pillow numpy requests\n")
    sys.exit(1)

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H, FPS = 1080, 1920, 30

# ── Brand colors ──────────────────────────────────────────────────────────────
EMERALD   = (16,  185, 129)
EMERALD_D = (5,   150, 105)
AMBER     = (251, 191,  36)
RED       = (220,  38,  38)
WHITE     = (255, 255, 255)
BLACK     = (0,     0,   0)
DARK      = (10,   15,  30)
MUTED     = (160, 180, 200)

# ── Image folder (auto-detect from repo path) ─────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IMAGES = os.path.normpath(os.path.join(_HERE, "../../public/images"))
_ASSETS = os.path.join(_HERE, "_assets")

# ── Image filenames from public/images/ ───────────────────────────────────────
IMG = {
    "hero":       "hero-lifestyle.jpg",
    "at_work":    "posture-at-work.jpg",
    "comparison": "posture-comparison.jpg",
    "fitness":    "fitness-belt.jpg",
    "postpartum": "postpartum-care.jpg",
    "happy1":     "happy-customer-1.jpg",
    "happy2":     "happy-customer-2.jpg",
    "happy3":     "happy-customer-3.jpg",
}

# ─── Asset downloader ─────────────────────────────────────────────────────────

def _download(url, dest):
    import urllib.request
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"  ⬇️   Downloading {os.path.basename(dest)}…")
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        print(f"  ⚠️   Download failed ({e}). Will use fallback.")
        return False


def get_font_path(bold=False):
    """
    Returns path to Montserrat Bold/Regular.
    Downloads from Google Fonts CDN on first run, caches in _assets/.
    Falls back to system fonts if download fails.
    """
    name = "Montserrat-Bold.ttf" if bold else "Montserrat-Regular.ttf"
    cached = os.path.join(_ASSETS, name)
    if os.path.exists(cached):
        return cached

    urls = {
        "Montserrat-Bold.ttf":
            "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf",
        "Montserrat-Regular.ttf":
            "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Regular.ttf",
    }
    if _download(urls[name], cached):
        return cached

    # system fallbacks
    fallbacks_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    fallbacks_reg = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in (fallbacks_bold if bold else fallbacks_reg):
        if os.path.exists(p):
            return p
    return None


MUSIC_LIBRARY = {
    "motivational": [
        "https://cdn.pixabay.com/audio/2024/02/15/audio_d6c7b4a7c2.mp3",
        "https://cdn.pixabay.com/audio/2022/10/25/audio_946ff5c5fd.mp3",
        "https://cdn.pixabay.com/audio/2023/06/08/audio_6e9c6a5e6e.mp3",
    ],
    "emotional": [
        "https://cdn.pixabay.com/audio/2023/01/20/audio_6e0d6e6ab3.mp3",
        "https://cdn.pixabay.com/audio/2022/11/22/audio_febc508520.mp3",
    ],
    "energetic": [
        "https://cdn.pixabay.com/audio/2022/08/02/audio_884fe92c21.mp3",
        "https://cdn.pixabay.com/audio/2023/03/09/audio_0625658ed6.mp3",
    ],
    "calm": [
        "https://cdn.pixabay.com/audio/2022/03/15/audio_1a609c8f35.mp3",
        "https://cdn.pixabay.com/audio/2023/08/16/audio_5e3e6b47e5.mp3",
    ],
}

SCRIPT_MOOD = {
    "new_mom":       "emotional",
    "office_worker": "motivational",
    "pain_hook":     "energetic",
    "showcase":      "motivational",
}

def get_music_path(mood=None, force_fresh=False):
    """Pick a random track by mood. Downloads and caches it."""
    mood = mood or "motivational"
    urls = MUSIC_LIBRARY.get(mood, MUSIC_LIBRARY["motivational"])
    url  = random.choice(urls)
    track_id = url.split("/")[-1].split(".")[0][:12]
    cached = os.path.join(_ASSETS, f"music_{mood}_{track_id}.mp3")
    if os.path.exists(cached) and not force_fresh:
        return cached
    if _download(url, cached):
        return cached
    # try any cached track as fallback
    existing = [f for f in os.listdir(_ASSETS) if f.startswith("music_") and f.endswith(".mp3")]
    if existing:
        return os.path.join(_ASSETS, existing[0])
    return None


# ─── Font loader ──────────────────────────────────────────────────────────────

def font(size, bold=False):
    path = get_font_path(bold)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


# ─── Music Generator (fallback if no MP3 available) ──────────────────────────

def generate_music(duration, bpm=108, sr=44100):
    n = int(duration * sr)
    audio = np.zeros(n, dtype=np.float32)
    beat = int(sr * 60 / bpm)

    for i in range(0, n, beat):
        klen = int(sr * 0.12)
        t = np.linspace(0, 0.12, klen)
        kick = np.sin(2 * np.pi * (80 - 60*t) * t) * np.exp(-t * 25) * 0.9
        end = min(i + klen, n)
        audio[i:end] += kick[:end - i]

        hpos = i + beat // 2
        hlen = int(sr * 0.025)
        if hpos + hlen < n:
            t2 = np.linspace(0, 0.025, hlen)
            hat = np.random.randn(hlen) * np.exp(-t2 * 120) * 0.12
            audio[hpos:hpos + hlen] += hat

        if (i // beat) % 2 == 1:
            slen = int(sr * 0.08)
            t3 = np.linspace(0, 0.08, slen)
            snare = (np.random.randn(slen) * 0.5 + np.sin(2*np.pi*200*t3)) \
                    * np.exp(-t3 * 35) * 0.45
            end2 = min(i + slen, n)
            audio[i:end2] += snare[:end2 - i]

    t_full = np.linspace(0, duration, n)
    for f in [130.81, 164.81, 196.00, 261.63]:
        audio += np.sin(2 * np.pi * f * t_full) * 0.06

    fade_in  = np.clip(t_full / 1.5, 0, 1)
    fade_out = np.clip((duration - t_full) / 2.0, 0, 1)
    audio   *= fade_in * fade_out
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.65
    return np.stack([audio, audio], axis=1), sr


# ─── Image helpers ────────────────────────────────────────────────────────────

# focal_y: 0.0=top, 0.5=center, 1.0=bottom — lets portrait images show the right subject area
IMG_FOCAL_Y = {
    "postpartum": 0.35,
    "at_work":    0.45,
    "hero":       0.40,
    "fitness":    0.40,
    "happy1":     0.35,
    "happy2":     0.35,
    "happy3":     0.35,
}

def load_img(name, images_dir, w=W, h=H):
    path = os.path.join(images_dir, IMG.get(name, name))
    if not os.path.exists(path):
        files = [f for f in os.listdir(images_dir) if f.lower().endswith((".jpg",".jpeg",".png"))]
        if files:
            path = os.path.join(images_dir, files[0])
        else:
            return np.full((h, w, 3), DARK, dtype=np.uint8)
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 1), int(ih * scale + 1)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    focal = IMG_FOCAL_Y.get(name, 0.5)
    y = int((nh - h) * focal)
    y = max(0, min(y, nh - h))
    return np.array(img.crop((x, y, x+w, y+h)))


def color_grade(fr, teal=True, warm=False, red_tint=False):
    r = fr[:,:,0].astype(np.float32)
    g = fr[:,:,1].astype(np.float32)
    b = fr[:,:,2].astype(np.float32)
    lum = r*0.299 + g*0.587 + b*0.114
    dark  = lum < 100
    light = lum > 160
    if teal:
        r[dark] *= 0.82; b[dark] = np.clip(b[dark]*1.15, 0, 255)
    if warm:
        r[light] = np.clip(r[light]*1.08, 0, 255)
        b[light] = np.clip(b[light]*0.90, 0, 255)
    if red_tint:
        r = np.clip(r * 1.10, 0, 255)
        g = np.clip(g * 0.88, 0, 255)
        b = np.clip(b * 0.85, 0, 255)
    sat = 0.85
    r2 = np.clip(lum + (r - lum)*sat, 0, 255)
    g2 = np.clip(lum + (g - lum)*sat, 0, 255)
    b2 = np.clip(lum + (b - lum)*sat, 0, 255)
    return np.stack([r2, g2, b2], axis=2).astype(np.uint8)


def vignette(fr, s=0.6):
    h, w = fr.shape[:2]
    Y, X = np.ogrid[:h, :w]
    d = np.sqrt(((X - w/2)/(w/2))**2 + ((Y - h/2)/(h/2))**2)
    m = (1 - np.clip(d*s, 0, 1))[:,:,np.newaxis]
    return (fr * m).astype(np.uint8)


def ken_burns(fr, t, dur, zoom_in=True, px=0.03, py=0.02):
    h, w = fr.shape[:2]
    p = t / max(dur, 0.001)
    z = (1.0 + 0.10*p) if zoom_in else (1.10 - 0.10*p)
    cw, ch = int(w/z), int(h/z)
    ox = int(px * p * (w - cw))
    oy = int(py * p * (h - ch))
    x1 = max(0, min((w-cw)//2 + ox, w-cw))
    y1 = max(0, min((h-ch)//2 + oy, h-ch))
    cropped = fr[y1:y1+ch, x1:x1+cw]
    return np.array(Image.fromarray(cropped).resize((w, h), Image.BILINEAR))


def shake(fr, t, strength=5):
    dx = int(math.sin(t * 23) * strength * random.uniform(0.5, 1.0))
    dy = int(math.cos(t * 17) * strength * random.uniform(0.5, 1.0))
    dx, dy = max(-18, min(18, dx)), max(-18, min(18, dy))
    h, w = fr.shape[:2]
    x1, y1 = max(0, dx), max(0, dy)
    x2, y2 = min(w, w+dx), min(h, h+dy)
    cropped = fr[y1:y2, x1:x2]
    return np.array(Image.fromarray(cropped).resize((w, h), Image.BILINEAR))


# ─── Drawing helpers ──────────────────────────────────────────────────────────

def shadow_text(d, x, y, text, fnt, color, off=4):
    shadow_col = (0, 0, 0, 140)
    for dx in [-off, 0, off]:
        for dy in [-off, 0, off]:
            if dx or dy:
                d.text((x+dx, y+dy), text, font=fnt, fill=shadow_col)
    d.text((x, y), text, font=fnt, fill=color)


def text_width_height(d, text, fnt):
    bb = d.textbbox((0, 0), text, font=fnt)
    return bb[2]-bb[0], bb[3]-bb[1]


def draw_pill(d, x1, y1, x2, y2, color, alpha=255):
    r = (y2-y1)//2
    d.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=(*color, alpha))


def text_bg_bar(d, y_top, y_bot, alpha=170, pad_x=0):
    """Semi-transparent black bar behind text — guarantees readability on any image."""
    d.rectangle([pad_x, y_top - 14, W - pad_x, y_bot + 14], fill=(0, 0, 0, alpha))


def centered_shadowed(d, text, y, fnt, color, alpha=255):
    tw, th = text_width_height(d, text, fnt)
    x = (W - tw) // 2
    shadow_text(d, x, y, text, fnt, (*color, alpha))
    return th


def wrap_lines(text, fnt, max_w=W - 80):
    """Wrap a single line so it never exceeds max_w pixels. Returns list of lines."""
    import textwrap as _tw
    result = []
    for raw_line in text.split("\n"):
        words = raw_line.split()
        if not words:
            result.append("")
            continue
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            bb = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test, font=fnt)
            if bb[2] - bb[0] <= max_w:
                current = test
            else:
                if current:
                    result.append(current)
                current = word
        if current:
            result.append(current)
    return result


def draw_text_block(d, text, fnt, y_start, color, anim=0, alpha=255,
                    bg_alpha=160, line_gap=10, max_w=W - 80):
    """Draw a block of auto-wrapped text centered on canvas. Returns final y."""
    lines = wrap_lines(text, fnt, max_w)
    line_heights = []
    for line in lines:
        bb = d.textbbox((0, 0), line, font=fnt)
        line_heights.append(bb[3] - bb[1])
    total_h = sum(line_heights) + line_gap * (len(lines) - 1)
    y = y_start + anim
    if bg_alpha > 0:
        text_bg_bar(d, y - 10, y + total_h + 10, alpha=bg_alpha)
    for i, line in enumerate(lines):
        tw, th = text_width_height(d, line, fnt)
        col = color if isinstance(color[0], int) else color[i % len(color)]
        if len(col) == 3:
            col = (*col, alpha)
        shadow_text(d, (W - tw) // 2, y, line, fnt, col)
        y += line_heights[i] + line_gap
    return y


def draw_caption(d, caption_text, alpha=255):
    """Burned-in subtitle caption at top of frame — always visible when muted."""
    if not caption_text:
        return
    f = font(34, bold=False)
    lines = caption_text.split("\n")
    line_h = 44
    total_h = len(lines) * line_h + 8
    y0 = 185
    d.rectangle([40, y0 - 8, W - 40, y0 + total_h], fill=(0, 0, 0, 160))
    for i, line in enumerate(lines):
        tw, _ = text_width_height(d, line, f)
        d.text(((W - tw) // 2, y0 + i * line_h), line, font=f,
               fill=(*WHITE, int(alpha * 0.85)))


def logo_strip(d):
    f = font(40, bold=True)
    text = "ZENPOSTURE"
    tw, th = text_width_height(d, text, f)
    x = (W - tw) // 2
    d.rectangle([0, 60, W, 60 + th + 24], fill=(0, 0, 0, 180))
    shadow_text(d, x, 68, text, f, (*WHITE, 210))
    bar_w = tw + 24
    d.rectangle([(W-bar_w)//2, 68+th+4, (W+bar_w)//2, 68+th+9], fill=(*EMERALD, 220))


def trust_strip(d):
    f = font(28)
    text = "Free Shipping  ·  COD Available  ·  30-Day Guarantee"
    tw, _ = text_width_height(d, text, f)
    d.rectangle([0, H-72, W, H], fill=(0, 0, 0, 160))
    d.text(((W-tw)//2, H-54), text, font=f, fill=(*WHITE, 140))


def tag_pill(d, text, accent=EMERALD, y=160):
    f = font(30, bold=True)
    tw, th = text_width_height(d, text, f)
    pad = 18
    draw_pill(d, (W-tw)//2-pad, y, (W+tw)//2+pad, y+th+14, accent, 220)
    d.text(((W-tw)//2, y+7), text, font=f, fill=(*DARK, 255))


def overlay_base(img_np, darkness=0.55):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(ov)
    for y in range(H):
        t = y / H
        a = int(darkness * 255 * (0.25 + 0.75 * t))
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    return ov


# ─── Scene Builders ───────────────────────────────────────────────────────────

def scene_pattern_interrupt(line1, line2="", caption="", duration=2.5, sound_on=True):
    def make_frame(t):
        progress = t / duration
        fade = min(t / 0.2, 1.0)
        anim_y = int((1 - min(progress * 3, 1)) * 45)

        bg = Image.new("RGB", (W, H), BLACK)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d  = ImageDraw.Draw(ov)

        # SOUND ON
        if sound_on:
            f_s = font(32, bold=True)
            d.text((W - 260, 80), "🔊  SOUND ON", font=f_s, fill=(*EMERALD, int(fade * 220)))

        # Logo
        logo_strip(d)

        # Caption subtitle
        draw_caption(d, caption, alpha=int(fade * 255))

        # Big headline
        lines = line1.split("\n")
        f_big = font(min(100, int(1400 / max(len(l) for l in lines))), bold=True)
        total_h = sum(d.textbbox((0,0), l, font=f_big)[3] - d.textbbox((0,0), l, font=f_big)[1] + 12
                      for l in lines)
        y = H // 2 - total_h // 2 + anim_y - 40

        for i, part in enumerate(lines):
            tw, th = text_width_height(d, part, f_big)
            col = (*AMBER, int(fade * 255)) if i == 0 else (*WHITE, int(fade * 255))
            text_bg_bar(d, y, y + th, alpha=0)  # black bg on pattern interrupt not needed
            shadow_text(d, (W - tw) // 2, y, part, f_big, col)
            y += th + 12

        # Subtext
        if line2:
            f_sub = font(44)
            tw, th = text_width_height(d, line2, f_sub)
            text_bg_bar(d, y + 20 + anim_y // 2, y + 20 + anim_y // 2 + th, alpha=0)
            d.text(((W - tw) // 2, y + 24 + anim_y // 2), line2, font=f_sub,
                   fill=(*MUTED, int(fade * 200)))

        # Animated emerald line
        lw = int(140 * min(progress * 4, 1))
        d.rectangle([(W-lw)//2, H//2 + 180, (W+lw)//2, H//2 + 186],
                    fill=(*EMERALD, int(fade * 255)))

        bg.paste(ov, (0, 0), ov)
        return np.array(bg)

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


def scene_pain(img_key, headline, sub, images_dir, caption="",
               duration=3.0, do_shake=True, tag=None):
    raw = load_img(img_key, images_dir)
    raw = color_grade(raw, teal=False, red_tint=True)
    raw = vignette(raw, s=0.7)
    zi  = random.choice([True, False])
    px, py = random.uniform(-0.03, 0.03), random.uniform(-0.02, 0.02)

    def make_frame(t):
        progress = t / duration
        fade = min(min(t / 0.25, 1.0), min((duration - t) / 0.25, 1.0))
        anim = int((1 - min(progress * 3, 1)) * 55)

        fr = ken_burns(raw, t, duration, zi, px, py)
        if do_shake and t < duration * 0.65:
            fr = shake(fr, t, strength=5)

        bg = Image.fromarray(fr)
        ov = overlay_base(fr, darkness=0.62)
        d  = ImageDraw.Draw(ov)

        logo_strip(d)
        draw_caption(d, caption, alpha=int(fade * 255))

        if tag:
            tag_pill(d, tag, RED)

        # Red urgency bar
        d.rectangle([0, 0, 8, H], fill=(*RED, 200))

        # Headline with bg bar
        f_h = font(82, bold=True)
        y = H - 490 + anim
        colors = [(*RED, int(fade * 255)), (*WHITE, int(fade * 255)), (*WHITE, int(fade * 255))]
        y = draw_text_block(d, headline, f_h, y, colors[0], bg_alpha=160, line_gap=10)

        # Subtext
        if sub:
            f_sub = font(36)
            draw_text_block(d, sub, f_sub, y + 8, (*MUTED, int(fade * 210)),
                            bg_alpha=140, line_gap=8)

        trust_strip(d)
        bg.paste(ov, (0, 0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


def scene_comparison_wipe(images_dir, headline, sub, caption="", duration=4.5):
    raw = load_img("comparison", images_dir)
    raw_graded = color_grade(raw, teal=True, warm=True)
    raw_graded = vignette(raw_graded, s=0.5)

    def make_frame(t):
        progress = t / duration
        fade = min(min(t / 0.3, 1.0), min((duration - t) / 0.3, 1.0))

        fr = ken_burns(raw_graded, t, duration, zoom_in=True, px=0.01, py=0.01)
        wipe_progress = min(max((t - 0.7) / (duration * 0.5), 0.0), 1.0)
        reveal_x = int(W * wipe_progress)

        bg = Image.fromarray(fr)

        left_dark = Image.fromarray(
            (fr * np.array([[[0.52, 0.52, 0.58]]])).clip(0, 255).astype(np.uint8)
        )
        if reveal_x < W:
            bg.paste(left_dark.crop((reveal_x, 0, W, H)), (reveal_x, 0))

        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d  = ImageDraw.Draw(ov)

        # Glowing wipe line
        if 0 < reveal_x < W:
            for off in range(-6, 7):
                alpha = int(255 * (1 - abs(off) / 7))
                d.line([(reveal_x + off, 0), (reveal_x + off, H)],
                       fill=(*EMERALD, alpha), width=2)

        logo_strip(d)
        draw_caption(d, caption, alpha=int(fade * 255))
        tag_pill(d, "BEFORE  →  AFTER", EMERALD)

        if wipe_progress > 0.08:
            f_lbl = font(42, bold=True)
            d.text((55, H // 2 - 28), "❌ BEFORE", font=f_lbl, fill=(*RED, 210))
        if wipe_progress > 0.5:
            f_lbl = font(42, bold=True)
            d.text((W // 2 + 30, H // 2 - 28), "✅ AFTER", font=f_lbl, fill=(*EMERALD, 210))

        # Headline — appears after wipe
        if wipe_progress > 0.65:
            anim = int((1 - min((wipe_progress - 0.65) / 0.35, 1)) * 38)
            f_h = font(72, bold=True)
            y = H - 440 + anim
            y = draw_text_block(d, headline, f_h, y, (*EMERALD, int(fade * 255)),
                                bg_alpha=165, line_gap=8)
            if sub:
                f_sub = font(34)
                draw_text_block(d, sub, f_sub, y + 10, (*MUTED, int(fade * 200)),
                                bg_alpha=145, line_gap=6)

        trust_strip(d)
        bg.paste(ov, (0, 0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


def scene_happy_customers(images_dir, headline, sub, caption="", duration=3.5, tag=None):
    imgs = [load_img(k, images_dir) for k in ("happy1", "happy2", "happy3")]
    imgs = [color_grade(im, teal=True, warm=True) for im in imgs]
    imgs = [vignette(im, s=0.5) for im in imgs]

    def make_frame(t):
        progress = t / duration
        fade = min(min(t / 0.25, 1.0), min((duration - t) / 0.25, 1.0))
        anim = int((1 - min(progress * 3, 1)) * 48)

        # Ken Burns on each customer photo independently
        idx = int((t / duration) * len(imgs)) % len(imgs)
        local_t = (t % (duration / len(imgs)))
        local_dur = duration / len(imgs)
        fr = ken_burns(imgs[idx], local_t, local_dur, zoom_in=(idx % 2 == 0))

        bg = Image.fromarray(fr)
        ov = overlay_base(fr, darkness=0.50)
        d  = ImageDraw.Draw(ov)

        logo_strip(d)
        draw_caption(d, caption, alpha=int(fade * 255))

        if tag:
            tag_pill(d, tag, AMBER)

        f_h = font(80, bold=True)
        y = H - 440 + anim
        y = draw_text_block(d, headline, f_h, y, (*AMBER, int(fade * 255)),
                            bg_alpha=155, line_gap=8)

        if sub:
            f_sub = font(34)
            draw_text_block(d, sub, f_sub, y + 10, (*MUTED, int(fade * 215)),
                            bg_alpha=140, line_gap=6)

        trust_strip(d)
        bg.paste(ov, (0, 0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


def scene_price_reveal(img_key, images_dir, caption="", duration=3.0, tag=None):
    raw = load_img(img_key, images_dir)
    raw = color_grade(raw, teal=True, warm=True)
    raw = vignette(raw, s=0.55)

    def make_frame(t):
        progress = t / duration
        fade = min(min(t / 0.25, 1.0), min((duration - t) / 0.25, 1.0))
        anim = int((1 - min(progress * 3, 1)) * 48)

        fr = ken_burns(raw, t, duration, zoom_in=False, px=0.02, py=0.02)
        bg = Image.fromarray(fr)
        ov = overlay_base(fr, darkness=0.60)
        d  = ImageDraw.Draw(ov)

        logo_strip(d)
        draw_caption(d, caption, alpha=int(fade * 255))

        if tag:
            tag_pill(d, tag, RED)

        # Scarcity bar
        f_sc = font(32, bold=True)
        sc_text = "Only 47 units left at this price!"
        tw_sc, th_sc = text_width_height(d, sc_text, f_sc)
        bar_y = H - 340 + anim
        draw_pill(d, (W - tw_sc) // 2 - 22, bar_y, (W + tw_sc) // 2 + 22,
                  bar_y + th_sc + 16, RED, 210)
        d.text(((W - tw_sc) // 2, bar_y + 8), sc_text, font=f_sc,
               fill=(*WHITE, int(fade * 255)))

        # Price block
        y_p = H - 265 + anim
        text_bg_bar(d, y_p - 8, y_p + 150, alpha=170)

        f_old = font(52)
        old_text = "₹999"
        tw_o, th_o = text_width_height(d, old_text, f_old)
        old_x = W // 2 - tw_o - 18
        d.text((old_x, y_p + 20), old_text, font=f_old, fill=(*MUTED, int(fade * 180)))
        d.line([(old_x - 4, y_p + 20 + th_o // 2),
                (old_x + tw_o + 4, y_p + 20 + th_o // 2)],
               fill=(*RED, int(fade * 255)), width=4)

        f_new = font(108, bold=True)
        new_text = "₹499"
        tw_n, _ = text_width_height(d, new_text, f_new)
        new_x = W // 2 + 12
        shadow_text(d, new_x, y_p - 8, new_text, f_new, (*EMERALD, int(fade * 255)))

        if progress > 0.3:
            f_save = font(30, bold=True)
            save_t = "50% OFF"
            tw_s, th_s = text_width_height(d, save_t, f_save)
            draw_pill(d, new_x + tw_n + 12, y_p + 12,
                      new_x + tw_n + tw_s + 32, y_p + th_s + 32, AMBER, 235)
            d.text((new_x + tw_n + 16, y_p + 14), save_t, font=f_save, fill=(*DARK, 255))

        trust_strip(d)
        bg.paste(ov, (0, 0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


def scene_cta(img_key, images_dir, headline, caption="", duration=3.5):
    raw = load_img(img_key, images_dir)
    raw = color_grade(raw, teal=True, warm=True)
    raw = vignette(raw, s=0.5)

    def make_frame(t):
        progress = t / duration
        fade = min(min(t / 0.3, 1.0), min((duration - t) / 0.3, 1.0))
        anim = int((1 - min(progress * 2.5, 1)) * 52)

        fr = ken_burns(raw, t, duration, zoom_in=True, px=0.02, py=0.01)
        bg = Image.fromarray(fr)
        ov = overlay_base(fr, darkness=0.50)
        d  = ImageDraw.Draw(ov)

        logo_strip(d)
        draw_caption(d, caption, alpha=int(fade * 255))

        # Headline
        f_h = font(84, bold=True)
        y = H // 2 - 240 + anim
        draw_text_block(d, headline, f_h, y, (*WHITE, int(fade * 255)),
                        bg_alpha=0, line_gap=10)

        # Big pill CTA button
        btn_y = H - 320 + anim
        draw_pill(d, 72, btn_y, W - 72, btn_y + 116, EMERALD, int(fade * 248))

        f_btn = font(46, bold=True)
        btn_text = "Shop Now  →"
        tw_b, _ = text_width_height(d, btn_text, f_btn)
        d.text(((W - tw_b) // 2, btn_y + 35), btn_text, font=f_btn,
               fill=(*WHITE, int(fade * 255)))

        # URL below button — amber, screenshot-able
        btn_y2 = btn_y + 130
        f_url = font(42, bold=True)
        url_text = "zenposture.in"
        tw_u, th_u = text_width_height(d, url_text, f_url)
        text_bg_bar(d, btn_y2 - 6, btn_y2 + th_u + 6, alpha=150)
        d.text(((W - tw_u) // 2, btn_y2), url_text, font=f_url,
               fill=(*AMBER, int(fade * 240)))

        # Trust line
        f_trust = font(30)
        tb = "COD  ·  Free Shipping  ·  30-Day Money-Back"
        tw_t, _ = text_width_height(d, tb, f_trust)
        d.text(((W - tw_t) // 2, btn_y + 260), tb, font=f_trust,
               fill=(*WHITE, int(fade * 150)))

        bg.paste(ov, (0, 0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ─── Script Definitions ───────────────────────────────────────────────────────

def get_clips(script, images_dir):
    if script == "office_worker":
        return [
            scene_pattern_interrupt(
                "STILL IGNORING\nYOUR BACK PAIN?",
                "This 20-second reel might change that.",
                caption="Your back is slowly breaking — and you don't even notice it.",
                duration=2.5
            ),
            scene_pain(
                "at_work",
                "8 hours of sitting\nis destroying\nyour spine.",
                "Back pain. Neck stiffness. Fatigue. Every single day.",
                images_dir,
                caption="Desk work = silent spine damage. Sound familiar?",
                duration=3.0, do_shake=True, tag="THE PROBLEM"
            ),
            scene_comparison_wipe(
                images_dir,
                "This is what\nZenPosture does.",
                "Clinically-designed correction. Feel it from Day 1.",
                caption="Before vs After — ZenPosture posture corrector",
                duration=4.5
            ),
            scene_happy_customers(
                images_dir,
                "⭐⭐⭐⭐⭐",
                '"Back pain gone in 1 week." — Priya, Mumbai\n10,000+ verified buyers across India',
                caption="Real customers. Real results. 10,000+ happy Indians.",
                duration=3.5, tag="REAL BUYERS · REAL RESULTS"
            ),
            scene_price_reveal(
                "fitness", images_dir,
                caption="Flash sale: ₹999 → ₹499. Only 47 units left.",
                duration=3.0, tag="FLASH SALE"
            ),
            scene_cta(
                "hero", images_dir,
                "Fix your posture.\nTransform your life.",
                caption="Order now at zenposture.in — COD available.",
                duration=3.5
            ),
        ]

    elif script == "pain_hook":
        return [
            scene_pattern_interrupt(
                "YOUR BACK PAIN\nISN'T NORMAL.",
                "It's fixable. In DAYS. Not months.",
                caption="Most people accept back pain. You don't have to.",
                duration=2.5
            ),
            scene_pain(
                "at_work",
                "Most Indians spend\n8 hours slowly\nwrecking their spine.",
                "And wonder why their back hurts at 30.",
                images_dir,
                caption="Sitting 8 hours daily = guaranteed posture damage.",
                duration=3.0, do_shake=True, tag="THE TRUTH"
            ),
            scene_comparison_wipe(
                images_dir,
                "One product.\nTotal transformation.",
                "93% report reduced back pain in 2 weeks.",
                caption="Before vs After — ZenPosture posture corrector",
                duration=4.5
            ),
            scene_price_reveal(
                "fitness", images_dir,
                caption="Limited offer: ₹499 only. 47 units left.",
                duration=3.0, tag="LIMITED OFFER"
            ),
            scene_cta(
                "hero", images_dir,
                "10,000+ Indians\nalready fixed theirs.",
                caption="Your turn. Order at zenposture.in — COD available.",
                duration=3.5
            ),
        ]

    elif script == "new_mom":
        return [
            scene_pattern_interrupt(
                "POV: You just\nhad a baby &\nyour back is\nDESTROYED.",
                "Nobody warned you about THIS part.",
                caption="Postpartum back pain affects 8 in 10 new moms. You're not alone.",
                duration=3.0
            ),
            scene_pain(
                "postpartum",
                "Every feed.\nEvery lift.\nEvery step. HURTS.",
                "Your core just went through 9 months of trauma. It needs real support.",
                images_dir,
                caption="Weak postpartum core = back pain that doesn't go away on its own.",
                duration=3.0, do_shake=True, tag="REAL TALK"
            ),
            scene_comparison_wipe(
                images_dir,
                "ZenPosture\nPostpartum Belt.",
                "Soft. Breathable. Wearable all day. Back pain gone in days.",
                caption="Clinically designed postpartum support — feels like a gentle hug.",
                duration=4.5
            ),
            scene_happy_customers(
                images_dir,
                "⭐⭐⭐⭐⭐",
                '"I wore it Day 3 post-delivery. My back pain was 80% better in a week."\n— Priya, Mumbai',
                caption="Thousands of Indian moms already wearing it. Their recovery. Their words.",
                duration=3.5, tag="MOM APPROVED · INDIA LOVED"
            ),
            scene_price_reveal(
                "postpartum", images_dir,
                caption="₹499 only. Free shipping. Cash on delivery available.",
                duration=3.0, tag="BEST GIFT FOR A NEW MOM"
            ),
            scene_cta(
                "postpartum", images_dir,
                "Her body did\nthe hard part.\nNow support it.",
                caption="zenposture.in — free shipping · COD · 30-day returns.",
                duration=3.5
            ),
        ]

    elif script == "showcase":
        return [
            scene_pattern_interrupt(
                "INDIA'S #1\nPOSTURE BRAND.",
                "10,000+ happy customers can't be wrong.",
                caption="ZenPosture — posture, recovery & fitness products.",
                duration=2.5
            ),
            scene_pain(
                "at_work",
                "Desk worker?\nBack pain is\nnot your destiny.",
                "ZenPosture Corrector — worn under your shirt, all day.",
                images_dir,
                caption="Fix your posture silently at work — no one will know.",
                duration=3.0, do_shake=False, tag="FOR DESK WORKERS"
            ),
            scene_pain(
                "fitness",
                "Gym goer?\nLift heavier.\nTrain smarter.",
                "ZenPosture Belt — zero lower-back injuries.",
                images_dir,
                caption="More gains. Zero lower-back injuries.",
                duration=3.0, do_shake=False, tag="FOR GYM GOERS"
            ),
            scene_pain(
                "postpartum",
                "New mom?\nYour recovery\nmatters too.",
                "ZenPosture Postpartum Belt — gentle core support.",
                images_dir,
                caption="Postpartum recovery support — gentle and breathable.",
                duration=3.0, do_shake=False, tag="FOR NEW MOMS"
            ),
            scene_comparison_wipe(
                images_dir,
                "See the difference.",
                "93% report less pain in 2 weeks. No gimmicks.",
                caption="Before vs After — real ZenPosture transformation.",
                duration=4.0
            ),
            scene_happy_customers(
                images_dir, "⭐⭐⭐⭐⭐",
                "10,000+ verified buyers across India",
                caption="10,000+ real Indian customers. 4.8 star average rating.",
                duration=3.5, tag="VERIFIED REVIEWS"
            ),
            scene_price_reveal(
                "fitness", images_dir,
                caption="Sale on now: ₹499. Limited units. COD available.",
                duration=3.0, tag="SALE ON NOW"
            ),
            scene_cta(
                "hero", images_dir,
                "Shop All Products",
                caption="Browse all products at zenposture.in",
                duration=3.5
            ),
        ]

    else:
        print(f"❌  Unknown script '{script}'. Use: office_worker | pain_hook | new_mom | showcase")
        sys.exit(1)


# ─── Build & Export ───────────────────────────────────────────────────────────

def build(script, output, images_dir, music_path=None, letterbox=False, mood=None):
    if not os.path.isdir(images_dir):
        print(f"❌  Images folder not found: {images_dir}")
        print(f"    Pass --images path/to/your/product/photos")
        sys.exit(1)

    print(f"\n{'━'*54}")
    print(f"  🎬  ZenPosture Reel Maker v5  —  Agency Edition")
    print(f"{'━'*54}")
    print(f"  Script  : {script}")
    print(f"  Images  : {images_dir}")
    print(f"  Output  : {output}\n")

    # Pre-download assets (font + music) before heavy rendering
    print("  🔤  Checking fonts…")
    get_font_path(bold=True)
    get_font_path(bold=False)

    clips = get_clips(script, images_dir)
    total = sum(c.duration for c in clips)
    print(f"  Scenes  : {len(clips)}  |  Total: {total:.0f}s\n")

    print("  🎞️   Compositing scenes…")
    final = concatenate_videoclips(clips, method="compose")

    if letterbox:
        bar_h = int(H * 0.07)
        from moviepy.editor import ColorClip, CompositeVideoClip
        bar_top    = ColorClip((W, bar_h), color=(0, 0, 0)).set_duration(final.duration).set_position(("center", "top"))
        bar_bottom = ColorClip((W, bar_h), color=(0, 0, 0)).set_duration(final.duration).set_position(("center", "bottom"))
        final = CompositeVideoClip([final, bar_top, bar_bottom])

    # Audio — prefer provided MP3, then bundled download, then generated
    if music_path and os.path.exists(music_path):
        print(f"  🎵  Loading music: {os.path.basename(music_path)}")
        audio = AudioFileClip(music_path).volumex(0.26)
        if audio.duration < final.duration:
            from moviepy.editor import concatenate_audioclips
            loops = int(final.duration / audio.duration) + 2
            audio = concatenate_audioclips([audio] * loops)
        audio = audio.subclip(0, final.duration).audio_fadeout(2.0)
        final = final.set_audio(audio)
    else:
        track_mood = mood or SCRIPT_MOOD.get(script, "motivational")
        bundled = get_music_path(mood=track_mood)
        if bundled and os.path.exists(bundled):
            print(f"  🎵  Using {track_mood} music: {os.path.basename(bundled)}…")
            audio = AudioFileClip(bundled).volumex(0.26)
            if audio.duration < final.duration:
                from moviepy.editor import concatenate_audioclips
                loops = int(final.duration / audio.duration) + 2
                audio = concatenate_audioclips([audio] * loops)
            audio = audio.subclip(0, final.duration).audio_fadeout(2.0)
            final = final.set_audio(audio)
        else:
            print("  🎵  Generating background music (offline fallback)…")
            stereo, sr = generate_music(total + 0.5)
            audio_clip = AudioArrayClip(stereo, fps=sr).audio_fadeout(2.0)
            audio_clip = audio_clip.subclip(0, final.duration)
            final = final.set_audio(audio_clip)

    print(f"  💾  Rendering → {output}  (takes 2–5 min)…\n")
    final.write_videofile(
        output, fps=FPS, codec="libx264", audio_codec="aac",
        temp_audiofile="temp_audio.m4a", remove_temp=True,
        preset="medium", ffmpeg_params=["-crf", "17", "-pix_fmt", "yuv420p"],
        logger=None,
    )

    mb = os.path.getsize(output) / 1024 / 1024
    print(f"\n{'━'*54}")
    print(f"  ✅  DONE!  {output}  ({mb:.1f} MB  ·  {total:.0f}s)")
    print(f"  📐  1080×1920 — Instagram / Facebook Reels ready")
    print(f"  🚀  Upload to Meta Ads Manager → Reels placement")
    print(f"{'━'*54}\n")


# ─── Ollama AI Script Generator ───────────────────────────────────────────────

_OLLAMA_URL = "http://localhost:11434/api/generate"

_OLLAMA_PROMPT = """You are a viral Instagram Reels copywriter for ZenPosture, an Indian D2C health brand.
Product: {product}
Audience: {audience}

Write a 6-scene Instagram Reel script. Return ONLY valid JSON, no markdown, no explanation.
Format:
{{
  "hook":      {{"line1": "2-4 word CAPS hook", "line2": "one punchy subline", "caption": "subtitle text"}},
  "pain":      {{"headline": "pain headline\\nline2\\nline3", "sub": "one line explanation", "caption": "caption"}},
  "reveal":    {{"headline": "product benefit\\nline2", "sub": "feature line", "caption": "caption"}},
  "social":    {{"headline": "⭐⭐⭐⭐⭐", "sub": "short testimonial quote\\n— Name, City", "caption": "caption"}},
  "price":     {{"caption": "price + offer line", "tag": "4-word tag"}},
  "cta":       {{"headline": "emotional cta\\nline2\\nline3", "caption": "zenposture.in caption"}}
}}

Rules:
- hook line1: ALL CAPS, max 4 words per line, use \\n for line breaks, max 4 lines
- pain headline: use \\n between lines, max 3 lines, each line max 4 words
- All text must fit a mobile screen — keep lines SHORT
- Make it emotional and scroll-stopping
- Price is always ₹499
- Brand: ZenPosture, website: zenposture.in
"""

PRODUCTS = {
    "new_mom":      ("ZenPosture Postpartum Recovery Belt", "new mothers 25-40, postpartum recovery"),
    "office_worker":("ZenPosture Posture Corrector",        "office workers 22-45, desk job back pain"),
    "gym":          ("ZenPosture Compression Belt",         "gym-goers 20-40, weightlifting, deadlifts"),
    "showcase":     ("ZenPosture full product range",       "general Indian health-conscious audience"),
}

def generate_script_ollama(script_key, model="llama3"):
    """Call local Ollama to generate a fresh viral script. Returns dict or None."""
    product, audience = PRODUCTS.get(script_key, PRODUCTS["office_worker"])
    prompt = _OLLAMA_PROMPT.format(product=product, audience=audience)

    print(f"  🤖  Generating fresh script with Ollama ({model})…")
    try:
        import urllib.request, json
        payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(_OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
        raw = resp.get("response", "")
        # strip any markdown code fences
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())
        print("  ✅  Ollama script ready!\n")
        return data
    except Exception as e:
        print(f"  ⚠️   Ollama failed ({e}). Using built-in script.\n")
        return None


def build_ollama_clips(data, images_dir):
    """Turn Ollama JSON into scene clips."""
    h = data.get("hook", {})
    pa = data.get("pain", {})
    rv = data.get("reveal", {})
    so = data.get("social", {})
    pr = data.get("price", {})
    ct = data.get("cta", {})

    return [
        scene_pattern_interrupt(
            h.get("line1", "STOP SCROLLING"),
            h.get("line2", ""),
            caption=h.get("caption", ""),
            duration=3.0
        ),
        scene_pain(
            "postpartum",
            pa.get("headline", "It HURTS.\nEvery day."),
            pa.get("sub", "Your body needs support."),
            images_dir,
            caption=pa.get("caption", ""),
            duration=3.0, do_shake=True, tag="REAL TALK"
        ),
        scene_comparison_wipe(
            images_dir,
            rv.get("headline", "ZenPosture\nFixes This."),
            rv.get("sub", "Soft. Breathable. Effective."),
            caption=rv.get("caption", ""),
            duration=4.5
        ),
        scene_happy_customers(
            images_dir,
            so.get("headline", "⭐⭐⭐⭐⭐"),
            so.get("sub", '"Changed my life."\n— Happy Customer'),
            caption=so.get("caption", ""),
            duration=3.5, tag="REAL RESULTS"
        ),
        scene_price_reveal(
            "postpartum", images_dir,
            caption=pr.get("caption", "₹499 only. Free shipping. COD."),
            duration=3.0, tag=pr.get("tag", "LIMITED OFFER")
        ),
        scene_cta(
            "postpartum", images_dir,
            ct.get("headline", "Order now.\nzenposture.in"),
            caption=ct.get("caption", "Free shipping · COD · 30-day returns"),
            duration=3.5
        ),
    ]


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="ZenPosture Reel Maker v5 — Agency Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Scripts:
          office_worker   Desk-worker back pain → ZenPosture solution
          pain_hook       Aggressive cold-audience hook (shorter)
          new_mom         Postpartum recovery audience
          showcase        All products — best for brand awareness ads

        Examples:
          python reel_maker.py --script office_worker --output office.mp4
          python reel_maker.py --script new_mom --output mom.mp4
          python reel_maker.py --script new_mom --generate --output mom_ai.mp4
          python reel_maker.py --script new_mom --generate --model llama3 --output mom_ai.mp4

        Free music: https://pixabay.com/music/  (search 'motivational')
        """)
    )
    p.add_argument("--script",    choices=["office_worker", "pain_hook", "new_mom", "showcase"],
                   required=True)
    p.add_argument("--output",    default="zenposture_reel.mp4")
    p.add_argument("--music",     default=None,
                   help="Path to MP3 (optional; auto-downloads royalty-free track if not given)")
    p.add_argument("--images",    default=DEFAULT_IMAGES, help="Path to product images folder")
    p.add_argument("--letterbox", action="store_true", help="Add cinematic letterbox bars")
    p.add_argument("--generate",  action="store_true",
                   help="Use local Ollama to generate a fresh viral script")
    p.add_argument("--model",     default="llama3",
                   help="Ollama model name (default: llama3)")
    p.add_argument("--list",      action="store_true")
    args = p.parse_args()

    if args.list:
        print("\nScripts: office_worker | pain_hook | new_mom | showcase\n")
        sys.exit(0)

    if args.generate:
        ollama_data = generate_script_ollama(args.script, args.model)
        if ollama_data:
            images_dir = args.images if args.images else DEFAULT_IMAGES
            clips = build_ollama_clips(ollama_data, images_dir)
            # reuse build() internals — assemble + render
            from moviepy.editor import concatenate_videoclips
            final = concatenate_videoclips(clips, method="compose")
            music_path = args.music or get_music_path()
            if music_path and os.path.exists(music_path):
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(music_path).volumex(0.18)
                audio = audio.subclip(0, final.duration).audio_fadeout(2.0)
                final = final.set_audio(audio)
            print(f"  💾  Rendering → {args.output}…\n")
            final.write_videofile(
                args.output, fps=FPS, codec="libx264", audio_codec="aac",
                temp_audiofile="temp_audio.m4a", remove_temp=True,
                preset="medium", ffmpeg_params=["-crf", "17", "-pix_fmt", "yuv420p"],
                logger=None,
            )
            mb = os.path.getsize(args.output) / 1024 / 1024
            print(f"\n✅  DONE!  {args.output}  ({mb:.1f} MB)")
            return

    build(args.script, args.output, args.images, args.music, args.letterbox)


if __name__ == "__main__":
    main()
