"""
ZenPosture Cinematic Reel Maker v4  —  CEO Edition
=====================================================
Rebuilt from scratch for CONVERSION, not just aesthetics.

What changed vs v3:
  - Scene 1: Black-screen pattern interrupt (stops the scroll)
  - posture-comparison.jpg gets a LEFT→RIGHT wipe reveal (money shot)
  - Camera shake on pain scenes (creates urgency)
  - Auto-generated background music (no external file needed)
  - ₹999 struck-through → ₹499 price reveal
  - "SOUND ON 🔊" callout on frame 1
  - Max 1 bold line per scene (readable in 2s)
  - Scarcity on CTA ("Only 47 left at this price")
  - Rounded pill CTA button with shadow
  - Trust strip on every scene

Usage:
  python reel_maker.py --script office_worker --output reel.mp4
  python reel_maker.py --script new_mom       --output mom.mp4
  python reel_maker.py --script pain_hook     --output pain.mp4
  python reel_maker.py --script showcase      --output showcase.mp4
  python reel_maker.py --music track.mp3 --script office_worker --output reel.mp4
  python reel_maker.py --list
"""

import argparse, os, sys, textwrap, random, math, struct, wave
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    from moviepy.editor import (
        VideoClip, AudioFileClip, concatenate_videoclips
    )
    from moviepy.video.fx.all import fadein, fadeout
    from moviepy.audio.AudioClip import AudioArrayClip
except ImportError as e:
    print(f"\n❌  Missing dependency: {e}")
    print("Run:  pip install moviepy pillow numpy\n")
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

# ─── Music Generator ──────────────────────────────────────────────────────────

def generate_music(duration, bpm=108, sr=44100):
    """
    Generates a simple motivational background track in memory.
    Beat: kick + hi-hat + rising synth pad. No external files needed.
    """
    n = int(duration * sr)
    audio = np.zeros(n, dtype=np.float32)
    beat = int(sr * 60 / bpm)

    for i in range(0, n, beat):
        # Kick drum
        klen = int(sr * 0.12)
        t = np.linspace(0, 0.12, klen)
        kick = np.sin(2 * np.pi * (80 - 60*t) * t) * np.exp(-t * 25) * 0.9
        end = min(i + klen, n)
        audio[i:end] += kick[:end - i]

        # Hi-hat on every half-beat
        hpos = i + beat // 2
        hlen = int(sr * 0.025)
        if hpos + hlen < n:
            t2 = np.linspace(0, 0.025, hlen)
            hat = np.random.randn(hlen) * np.exp(-t2 * 120) * 0.12
            audio[hpos:hpos + hlen] += hat

        # Snare on beats 2 & 4
        if (i // beat) % 2 == 1:
            slen = int(sr * 0.08)
            t3 = np.linspace(0, 0.08, slen)
            snare = (np.random.randn(slen) * 0.5 + np.sin(2*np.pi*200*t3)) \
                    * np.exp(-t3 * 35) * 0.45
            end2 = min(i + slen, n)
            audio[i:end2] += snare[:end2 - i]

    # Synth pad (warm chords)
    t_full = np.linspace(0, duration, n)
    freqs = [130.81, 164.81, 196.00, 261.63]  # C3 E3 G3 C4
    for f in freqs:
        audio += np.sin(2 * np.pi * f * t_full) * 0.06

    # Fade in 1.5s, fade out 2s
    fade_in  = np.clip(t_full / 1.5, 0, 1)
    fade_out = np.clip((duration - t_full) / 2.0, 0, 1)
    audio   *= fade_in * fade_out

    # Normalize
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.65

    # Stereo
    stereo = np.stack([audio, audio], axis=1)
    return stereo, sr

# ─── Image helpers ────────────────────────────────────────────────────────────

def load_img(name, images_dir, w=W, h=H):
    path = os.path.join(images_dir, IMG.get(name, name))
    if not os.path.exists(path):
        # fallback: any jpg in the folder
        files = [f for f in os.listdir(images_dir) if f.endswith((".jpg",".jpeg",".png"))]
        if files:
            path = os.path.join(images_dir, files[0])
        else:
            return np.full((h, w, 3), DARK, dtype=np.uint8)
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 1), int(ih * scale + 1)
    img = img.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - w) // 2, (nh - h) // 2
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
    # Slight desaturation
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
    z = (1.0 + 0.13*p) if zoom_in else (1.13 - 0.13*p)
    cw, ch = int(w/z), int(h/z)
    ox = int(px * p * (w - cw))
    oy = int(py * p * (h - ch))
    x1 = max(0, min((w-cw)//2 + ox, w-cw))
    y1 = max(0, min((h-ch)//2 + oy, h-ch))
    cropped = fr[y1:y1+ch, x1:x1+cw]
    return np.array(Image.fromarray(cropped).resize((w, h), Image.BILINEAR))


def shake(fr, t, strength=6):
    """Subtle camera shake — creates urgency/pain feeling."""
    dx = int(math.sin(t * 23) * strength * random.uniform(0.5, 1.0))
    dy = int(math.cos(t * 17) * strength * random.uniform(0.5, 1.0))
    dx = max(-20, min(20, dx))
    dy = max(-20, min(20, dy))
    h, w = fr.shape[:2]
    x1, y1 = max(0, dx), max(0, dy)
    x2, y2 = min(w, w+dx), min(h, h+dy)
    cropped = fr[y1:y2, x1:x2]
    return np.array(Image.fromarray(cropped).resize((w, h), Image.BILINEAR))

# ─── Font ────────────────────────────────────────────────────────────────────

def font(size, bold=False):
    paths = [
        f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf",
        f"C:/Windows/Fonts/{'calibrib' if bold else 'calibri'}.ttf",
        f"C:/Windows/Fonts/{'verdanab' if bold else 'verdana'}.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

# ─── Drawing helpers ──────────────────────────────────────────────────────────

def shadow_text(d, x, y, text, fnt, color, shadow=(0,0,0), off=4):
    for dx in [-off, 0, off]:
        for dy in [-off, 0, off]:
            if dx or dy:
                d.text((x+dx, y+dy), text, font=fnt, fill=(*shadow, 120))
    d.text((x, y), text, font=fnt, fill=color)


def centered_text(d, text, y, fnt, color, w=W, shadow=True):
    bb = d.textbbox((0,0), text, font=fnt)
    tw = bb[2]-bb[0]
    th = bb[3]-bb[1]
    x = (w - tw) // 2
    if shadow:
        shadow_text(d, x, y, text, fnt, color)
    else:
        d.text((x, y), text, font=fnt, fill=color)
    return th


def draw_pill(d, x1, y1, x2, y2, color, alpha=255):
    r = (y2-y1)//2
    d.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=(*color, alpha))

# ─── Scene Builders ───────────────────────────────────────────────────────────

def overlay_base(img_np, darkness=0.55):
    """RGBA overlay canvas with dark gradient."""
    ov = Image.new("RGBA", (W, H), (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for y in range(H):
        t = y / H
        a = int(darkness * 255 * (0.3 + 0.7 * t))
        d.line([(0,y),(W,y)], fill=(0,0,0,a))
    return ov


def logo_strip(d):
    f = font(38, bold=True)
    text = "ZENPOSTURE"
    bb = d.textbbox((0,0), text, font=f)
    tw = bb[2]-bb[0]
    x = (W - tw) // 2
    shadow_text(d, x, 72, text, f, (*WHITE, 200))
    bar_w = tw + 24
    d.rectangle([(W-bar_w)//2, 72+(bb[3]-bb[1])+6, (W+bar_w)//2, 72+(bb[3]-bb[1])+10],
                fill=(*EMERALD, 220))


def trust_strip(d):
    f = font(28)
    text = "Free Shipping  ·  COD Available  ·  30-Day Guarantee"
    bb = d.textbbox((0,0), text, font=f)
    tw = bb[2]-bb[0]
    d.rectangle([0, H-70, W, H], fill=(0,0,0,130))
    d.text(((W-tw)//2, H-52), text, font=f, fill=(*WHITE, 130))


def tag_pill(d, text, accent=EMERALD, y=155):
    f = font(30, bold=True)
    bb = d.textbbox((0,0), text, font=f)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    pad = 16
    draw_pill(d, (W-tw)//2-pad, y, (W+tw)//2+pad, y+th+12, accent, 210)
    d.text(((W-tw)//2, y+6), text, font=f, fill=(*DARK, 255))


# ── SCENE 1: Black-screen pattern interrupt ────────────────────────────────────

def scene_pattern_interrupt(line1, line2="", duration=3.0, sound_on=True):
    def make_frame(t):
        progress = t / duration
        fade = min(t / 0.25, 1.0)

        bg = Image.new("RGB", (W, H), BLACK)
        d  = ImageDraw.Draw(bg)

        # SOUND ON callout (top right)
        if sound_on:
            f_s = font(30, bold=True)
            d.text((W-240, 80), "🔊 SOUND ON", font=f_s, fill=(*EMERALD, int(fade*220)))

        # Big headline — animate scale with fade
        f_big = font(100, bold=True)
        f_big2 = font(80, bold=True)
        fnt = f_big if len(line1) <= 16 else f_big2

        anim_y = int((1 - min(progress*3, 1)) * 50)

        y = H//2 - 140 + anim_y
        for i, part in enumerate(line1.split("\n")):
            bb = d.textbbox((0,0), part, font=fnt)
            tw = bb[2]-bb[0]
            th = bb[3]-bb[1]
            col = (*AMBER, int(fade*255)) if i==0 else (*WHITE, int(fade*255))
            d.text(((W-tw)//2, y), part, font=fnt, fill=col)
            y += th + 10

        if line2:
            f_sub = font(48)
            bb = d.textbbox((0,0), line2, font=f_sub)
            tw = bb[2]-bb[0]
            d.text(((W-tw)//2, y+24+anim_y//2), line2, font=f_sub,
                   fill=(*MUTED, int(fade*200)))

        # Emerald accent line
        line_w = 120
        anim_lw = int(line_w * min(progress*4, 1))
        d.rectangle([(W-anim_lw)//2, H//2+160, (W+anim_lw)//2, H//2+165],
                    fill=(*EMERALD, int(fade*255)))

        return np.array(bg)

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── SCENE 2: Pain / problem photo with shake ──────────────────────────────────

def scene_pain(img_key, headline, sub, images_dir, duration=4.0,
               do_shake=True, tag=None):
    raw = load_img(img_key, images_dir)
    raw = color_grade(raw, teal=False, red_tint=True)
    raw = vignette(raw, s=0.7)
    zi  = random.choice([True, False])
    px, py = random.uniform(-0.03, 0.03), random.uniform(-0.02, 0.02)

    def make_frame(t):
        progress = t / duration
        fade = min(min(t/0.3, 1.0), min((duration-t)/0.3, 1.0))
        anim = int((1 - min(progress*3, 1)) * 60)

        fr = ken_burns(raw, t, duration, zi, px, py)
        if do_shake and t < duration * 0.6:
            fr = shake(fr, t, strength=5)

        bg = Image.fromarray(fr)
        ov = overlay_base(fr, darkness=0.60)
        d  = ImageDraw.Draw(ov)

        logo_strip(d)
        if tag:
            tag_pill(d, tag, RED)

        # RED urgency bar left edge
        d.rectangle([0, 0, 8, H], fill=(*RED, 200))

        # Headline
        f_h = font(86, bold=True)
        f_h2 = font(70, bold=True)
        lines = headline.split("\n")
        fnt_h = f_h if max(len(l) for l in lines) <= 14 else f_h2
        y = H - 480 + anim
        for i, line in enumerate(lines):
            bb = d.textbbox((0,0), line, font=fnt_h)
            tw = bb[2]-bb[0]; th = bb[3]-bb[1]
            col = (*RED, int(fade*255)) if i==0 else (*WHITE, int(fade*255))
            shadow_text(d, (W-tw)//2, y, line, fnt_h, col, off=4)
            y += th + 8

        # Subtext
        if sub:
            f_sub = font(38)
            for line in sub.split("\n"):
                bb = d.textbbox((0,0), line, font=f_sub)
                tw = bb[2]-bb[0]; th = bb[3]-bb[1]
                shadow_text(d, (W-tw)//2, y+16+anim//2, line, f_sub,
                            (*MUTED, int(fade*220)))
                y += th + 12

        trust_strip(d)
        bg.paste(ov, (0,0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── SCENE 3: Wipe-reveal comparison (the MONEY SHOT) ─────────────────────────

def scene_comparison_wipe(images_dir, headline, sub, duration=5.0):
    """
    posture-comparison.jpg revealed left→right like a curtain pull.
    Left side (before) fades in first, then right side (after) wipes in.
    """
    raw = load_img("comparison", images_dir)
    raw_graded = color_grade(raw, teal=True, warm=True)
    raw_graded = vignette(raw_graded, s=0.5)

    def make_frame(t):
        progress = t / duration
        fade = min(min(t/0.3, 1.0), min((duration-t)/0.3, 1.0))

        # Ken Burns — slow zoom in
        fr = ken_burns(raw_graded, t, duration, zoom_in=True, px=0.01, py=0.01)

        # Wipe progress: left side shows from start, right side wipes in after 1s
        wipe_progress = min(max((t - 0.8) / (duration * 0.55), 0.0), 1.0)
        reveal_x = int(W * wipe_progress)

        bg = Image.fromarray(fr)

        # Left side = slightly darker (before)
        left_dark = Image.fromarray(
            (fr * np.array([[[0.55, 0.55, 0.60]]]) ).clip(0,255).astype(np.uint8)
        )
        if reveal_x < W:
            bg.paste(left_dark.crop((reveal_x, 0, W, H)), (reveal_x, 0))

        # Wipe line
        ov = Image.new("RGBA", (W, H), (0,0,0,0))
        d  = ImageDraw.Draw(ov)

        if 0 < reveal_x < W:
            # Glowing wipe line
            for off in range(-6, 7):
                alpha = int(255 * (1 - abs(off)/7))
                d.line([(reveal_x+off, 0), (reveal_x+off, H)],
                       fill=(*EMERALD, alpha), width=2)

        logo_strip(d)
        tag_pill(d, "BEFORE  →  AFTER", EMERALD)

        # Labels
        if wipe_progress > 0.1:
            f_label = font(40, bold=True)
            d.text((60, H//2 - 30), "❌ BEFORE", font=f_label, fill=(*RED, 200))
        if wipe_progress > 0.5:
            f_label = font(40, bold=True)
            d.text((W//2 + 30, H//2 - 30), "✅ AFTER", font=f_label, fill=(*EMERALD, 200))

        # Headline (lower third, appears after wipe completes)
        if wipe_progress > 0.7:
            anim = int((1 - min((wipe_progress - 0.7) / 0.3, 1)) * 40)
            f_h = font(76, bold=True)
            lines = headline.split("\n")
            y = H - 440 + anim
            for i, line in enumerate(lines):
                bb = d.textbbox((0,0), line, font=f_h)
                tw = bb[2]-bb[0]; th = bb[3]-bb[1]
                col = (*EMERALD, int(fade*255)) if i==0 else (*WHITE, int(fade*255))
                shadow_text(d, (W-tw)//2, y, line, f_h, col)
                y += th + 8
            if sub:
                f_sub = font(36)
                for line in sub.split("\n"):
                    bb = d.textbbox((0,0), line, font=f_sub)
                    tw = bb[2]-bb[0]; th = bb[3]-bb[1]
                    shadow_text(d, (W-tw)//2, y+12, line, f_sub, (*MUTED, int(fade*200)))
                    y += th + 10

        trust_strip(d)
        bg.paste(ov, (0,0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── SCENE 4: Happy customers cycling ─────────────────────────────────────────

def scene_happy_customers(images_dir, headline, sub, duration=4.0, tag=None):
    imgs = [load_img(k, images_dir) for k in ("happy1","happy2","happy3")]
    imgs = [color_grade(im, teal=True, warm=True) for im in imgs]
    imgs = [vignette(im, s=0.5) for im in imgs]

    def make_frame(t):
        progress = t / duration
        fade = min(min(t/0.3, 1.0), min((duration-t)/0.3, 1.0))

        # Cycle through customer photos every ~1.3s
        idx = int((t / duration) * len(imgs)) % len(imgs)
        fr  = ken_burns(imgs[idx], t % (duration/len(imgs)),
                        duration/len(imgs), zoom_in=True)

        bg = Image.fromarray(fr)
        ov = overlay_base(fr, darkness=0.48)
        d  = ImageDraw.Draw(ov)

        logo_strip(d)
        if tag:
            tag_pill(d, tag, AMBER)

        anim = int((1 - min(progress*3, 1)) * 50)
        f_h  = font(86, bold=True)
        lines = headline.split("\n")
        y = H - 440 + anim
        for i, line in enumerate(lines):
            bb = d.textbbox((0,0), line, font=f_h)
            tw = bb[2]-bb[0]; th = bb[3]-bb[1]
            col = (*AMBER, int(fade*255)) if i==0 else (*WHITE, int(fade*255))
            shadow_text(d, (W-tw)//2, y, line, f_h, col)
            y += th + 8
        if sub:
            f_sub = font(38)
            for line in sub.split("\n"):
                bb = d.textbbox((0,0), line, font=f_sub)
                tw = bb[2]-bb[0]; th = bb[3]-bb[1]
                shadow_text(d, (W-tw)//2, y+14+anim//2, line, f_sub,
                            (*MUTED, int(fade*220)))
                y += th + 10

        trust_strip(d)
        bg.paste(ov, (0,0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── SCENE 5: Product + price reveal ──────────────────────────────────────────

def scene_price_reveal(img_key, images_dir, duration=3.5, tag=None):
    raw = load_img(img_key, images_dir)
    raw = color_grade(raw, teal=True, warm=True)
    raw = vignette(raw, s=0.55)

    def make_frame(t):
        progress = t / duration
        fade = min(min(t/0.3, 1.0), min((duration-t)/0.3, 1.0))
        anim = int((1 - min(progress*3, 1)) * 50)

        fr = ken_burns(raw, t, duration, zoom_in=False, px=0.02, py=0.02)
        bg = Image.fromarray(fr)
        ov = overlay_base(fr, darkness=0.58)
        d  = ImageDraw.Draw(ov)

        logo_strip(d)
        if tag:
            tag_pill(d, tag, RED)

        # Scarcity
        f_sc = font(32, bold=True)
        sc_text = "⚡ Only 47 units left at this price!"
        bb = d.textbbox((0,0), sc_text, font=f_sc)
        tw = bb[2]-bb[0]
        draw_pill(d, (W-tw)//2 - 20, H-340+anim, (W+tw)//2 + 20, H-295+anim, RED, 200)
        d.text(((W-tw)//2, H-335+anim), sc_text, font=f_sc, fill=(*WHITE, int(fade*255)))

        # Price — old struck through → new
        y_p = H - 280 + anim
        f_old = font(56)
        old_text = "₹999"
        bb_o = d.textbbox((0,0), old_text, font=f_old)
        ow = bb_o[2]-bb_o[0]; oh = bb_o[3]-bb_o[1]
        old_x = W//2 - ow - 20
        d.text((old_x, y_p), old_text, font=f_old, fill=(*MUTED, int(fade*180)))
        d.line([(old_x-4, y_p+oh//2), (old_x+ow+4, y_p+oh//2)],
               fill=(*RED, int(fade*255)), width=4)

        f_new = font(110, bold=True)
        new_text = "₹499"
        bb_n = d.textbbox((0,0), new_text, font=f_new)
        nw_ = bb_n[2]-bb_n[0]
        new_x = W//2 + 10
        shadow_text(d, new_x, y_p - 20, new_text, f_new, (*EMERALD, int(fade*255)))

        # Savings badge
        if progress > 0.3:
            f_save = font(32, bold=True)
            save_t = "50% OFF"
            bb_s = d.textbbox((0,0), save_t, font=f_save)
            sw = bb_s[2]-bb_s[0]
            draw_pill(d, new_x + nw_ + 14, y_p+10, new_x + nw_ + sw + 34, y_p+52, AMBER, 230)
            d.text((new_x + nw_ + 18, y_p+12), save_t, font=f_save, fill=(*DARK, 255))

        trust_strip(d)
        bg.paste(ov, (0,0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── SCENE 6: CTA finale ───────────────────────────────────────────────────────

def scene_cta(img_key, images_dir, headline, duration=4.0):
    raw = load_img(img_key, images_dir)
    raw = color_grade(raw, teal=True, warm=True)
    raw = vignette(raw, s=0.5)

    def make_frame(t):
        progress = t / duration
        fade = min(min(t/0.35, 1.0), min((duration-t)/0.35, 1.0))
        anim = int((1 - min(progress*2.5, 1)) * 55)

        fr = ken_burns(raw, t, duration, zoom_in=True, px=0.02, py=0.01)
        bg = Image.fromarray(fr)
        ov = overlay_base(fr, darkness=0.48)
        d  = ImageDraw.Draw(ov)

        logo_strip(d)

        # Main headline
        f_h = font(88, bold=True)
        lines = headline.split("\n")
        y = H//2 - (len(lines)*105)//2 + anim
        for i, line in enumerate(lines):
            bb = d.textbbox((0,0), line, font=f_h)
            tw = bb[2]-bb[0]; th = bb[3]-bb[1]
            col = (*WHITE, int(fade*255)) if i==0 else (*EMERALD, int(fade*255))
            shadow_text(d, (W-tw)//2, y, line, f_h, col)
            y += th + 10

        # Big pill CTA button
        btn_y = H - 310 + anim
        draw_pill(d, 80, btn_y, W-80, btn_y+120, EMERALD, int(fade*245))
        # Button shadow
        for i in range(1, 12):
            draw_pill(d, 80+i, btn_y+i, W-80+i, btn_y+120+i, (0,60,30), int(40/i))

        f_btn = font(50, bold=True)
        btn_text = "Shop Now →  zenposture.in"
        bb_b = d.textbbox((0,0), btn_text, font=f_btn)
        bw = bb_b[2]-bb_b[0]
        d.text(((W-bw)//2, btn_y+34), btn_text, font=f_btn, fill=(*WHITE, int(fade*255)))

        # Below button
        f_trust = font(32)
        tb = "COD  ·  Free Shipping  ·  30-Day Money-Back"
        bb_t = d.textbbox((0,0), tb, font=f_trust)
        tw = bb_t[2]-bb_t[0]
        d.text(((W-tw)//2, btn_y+142), tb, font=f_trust, fill=(*WHITE, int(fade*160)))

        bg.paste(ov, (0,0), ov)
        return np.array(bg.convert("RGB"))

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ─── Script Definitions ───────────────────────────────────────────────────────

def get_clips(script, images_dir):
    if script == "office_worker":
        return [
            scene_pattern_interrupt(
                "STILL IGNORING\nYOUR BACK PAIN?",
                "This 20-second reel might change that. 👇",
                duration=3.0
            ),
            scene_pain(
                "at_work",
                "8 hours of sitting\nis destroying\nyour spine.",
                "Back pain. Neck stiffness. Fatigue. Every. Single. Day.",
                images_dir, duration=4.0, do_shake=True, tag="THE PROBLEM"
            ),
            scene_comparison_wipe(
                images_dir,
                "This is what\nZenPosture does.",
                "Clinically-designed posture correction.\nFeel it from Day 1.",
                duration=5.0
            ),
            scene_happy_customers(
                images_dir,
                "⭐⭐⭐⭐⭐",
                '"Back pain gone in 1 week." — Priya, Mumbai\n10,000+ verified buyers across India',
                duration=4.0, tag="REAL BUYERS · REAL RESULTS"
            ),
            scene_price_reveal(
                "fitness", images_dir, duration=3.5, tag="🔥 FLASH SALE"
            ),
            scene_cta(
                "hero", images_dir,
                "Fix your posture.\nTransform your life.",
                duration=4.0
            ),
        ]

    elif script == "pain_hook":
        return [
            scene_pattern_interrupt(
                "YOUR BACK PAIN\nISN'T NORMAL.",
                "It's fixable. In DAYS. Not months. 👇",
                duration=2.5
            ),
            scene_pain(
                "at_work",
                "Most Indians spend\n8 hours slowly\nwrecking their spine.",
                "And then wonder why their back hurts at 30.",
                images_dir, duration=3.5, do_shake=True, tag="THE TRUTH"
            ),
            scene_comparison_wipe(
                images_dir,
                "One product.\nTotal transformation.",
                "93% of users report reduced back pain in 2 weeks.",
                duration=4.5
            ),
            scene_price_reveal(
                "fitness", images_dir, duration=3.5, tag="🔥 LIMITED OFFER"
            ),
            scene_cta(
                "hero", images_dir,
                "10,000+ Indians\nalready fixed theirs.",
                duration=3.5
            ),
        ]

    elif script == "new_mom":
        return [
            scene_pattern_interrupt(
                "NEW MOMS —\nNO ONE TELLS\nYOU THIS.",
                "Your back pain after delivery is NOT normal. 💚",
                duration=3.0
            ),
            scene_pain(
                "at_work",
                "Weak core.\nAching back.\nAll day, every day.",
                "Lifting, feeding, carrying — while your body is still healing.",
                images_dir, duration=4.0, do_shake=False, tag="THE REALITY"
            ),
            scene_comparison_wipe(
                images_dir,
                "ZenPosture Postpartum\nBelt fixes this.",
                "Gentle core support. Breathable. Made for India.",
                duration=5.0
            ),
            scene_happy_customers(
                images_dir,
                "⭐⭐⭐⭐⭐",
                '"Felt supported from Day 1. Every new mom needs this."\n— Ananya, Delhi',
                duration=4.0, tag="REAL MOM · REAL RESULT"
            ),
            scene_price_reveal(
                "postpartum", images_dir, duration=3.5, tag="GIFT IT 💚"
            ),
            scene_cta(
                "hero", images_dir,
                "Gift it to a mom\nwho deserves it. 💚",
                duration=3.5
            ),
        ]

    elif script == "showcase":
        return [
            scene_pattern_interrupt(
                "INDIA'S #1\nPOSTURE BRAND.",
                "10,000+ happy customers can't be wrong. 💚",
                duration=2.5
            ),
            scene_pain(
                "at_work",
                "Desk worker?\nBack pain is\nnot your destiny.",
                "ZenPosture Corrector — worn under your shirt all day.",
                images_dir, duration=3.5, do_shake=False, tag="FOR DESK WORKERS"
            ),
            scene_pain(
                "fitness",
                "Gym goer?\nLift heavier.\nTrain smarter.",
                "ZenPosture Compression Belt — zero lower-back injuries.",
                images_dir, duration=3.5, do_shake=False, tag="FOR GYM GOERS"
            ),
            scene_pain(
                "postpartum",
                "New mom?\nYour recovery\nmatters too.",
                "ZenPosture Postpartum Belt — gentle core support.",
                images_dir, duration=3.5, do_shake=False, tag="FOR NEW MOMS"
            ),
            scene_comparison_wipe(
                images_dir,
                "See the difference.",
                "93% report less pain in 2 weeks. No gimmicks.",
                duration=4.0
            ),
            scene_happy_customers(
                images_dir, "⭐⭐⭐⭐⭐",
                "10,000+ verified buyers across India",
                duration=3.5, tag="VERIFIED REVIEWS"
            ),
            scene_price_reveal("fitness", images_dir, duration=3.5, tag="🔥 SALE ON NOW"),
            scene_cta("hero", images_dir, "Shop All Products →\nzenposture.in", duration=4.0),
        ]

    else:
        print(f"❌  Unknown script '{script}'. Use: office_worker | pain_hook | new_mom | showcase")
        sys.exit(1)


# ─── Build & Export ───────────────────────────────────────────────────────────

def build(script, output, images_dir, music_path=None, letterbox=False):
    if not os.path.isdir(images_dir):
        print(f"❌  Images folder not found: {images_dir}")
        print(f"    Pass --images path/to/your/product/photos")
        sys.exit(1)

    print(f"\n{'━'*54}")
    print(f"  🎬  ZenPosture Reel Maker v4  —  CEO Edition")
    print(f"{'━'*54}")
    print(f"  Script  : {script}")
    print(f"  Images  : {images_dir}")
    print(f"  Output  : {output}\n")

    clips = get_clips(script, images_dir)
    total = sum(c.duration for c in clips)
    print(f"  Scenes  : {len(clips)}  |  Total: {total:.0f}s\n")

    print("  🎞️  Compositing scenes…")
    final = concatenate_videoclips(clips, method="compose")

    # ── Letterbox bars ──
    if letterbox:
        bar_h = int(H * 0.07)
        bar_clip_top    = ColorClip((W, bar_h), color=(0,0,0)).set_duration(final.duration)
        bar_clip_bottom = ColorClip((W, bar_h), color=(0,0,0)).set_duration(final.duration)
        from moviepy.editor import CompositeVideoClip
        bar_clip_top    = bar_clip_top.set_position(("center","top"))
        bar_clip_bottom = bar_clip_bottom.set_position(("center","bottom"))
        final = CompositeVideoClip([final, bar_clip_top, bar_clip_bottom])

    # ── Audio ──
    if music_path and os.path.exists(music_path):
        print(f"  🎵  Loading music: {os.path.basename(music_path)}")
        audio = AudioFileClip(music_path).volumex(0.28)
        if audio.duration < final.duration:
            from moviepy.editor import concatenate_audioclips
            loops = int(final.duration / audio.duration) + 2
            audio = concatenate_audioclips([audio]*loops)
        audio = audio.subclip(0, final.duration).audio_fadeout(2.0)
        final = final.set_audio(audio)
    else:
        print("  🎵  Generating background music (no --music file provided)…")
        stereo, sr = generate_music(total + 0.5)
        audio_clip = AudioArrayClip(stereo, fps=sr).audio_fadeout(2.0)
        audio_clip = audio_clip.subclip(0, final.duration)
        final = final.set_audio(audio_clip)

    print(f"  💾  Rendering → {output}  (takes 2–5 min)…\n")
    final.write_videofile(
        output, fps=FPS, codec="libx264", audio_codec="aac",
        temp_audiofile="temp_audio.m4a", remove_temp=True,
        preset="medium", ffmpeg_params=["-crf","17","-pix_fmt","yuv420p"],
        logger=None,
    )

    mb = os.path.getsize(output) / 1024 / 1024
    print(f"\n{'━'*54}")
    print(f"  ✅  DONE!  {output}  ({mb:.1f} MB  ·  {total:.0f}s)")
    print(f"  📐  1080×1920 — Instagram / Facebook Reels ready")
    print(f"  🚀  Upload to Meta Ads Manager → Reels placement")
    print(f"{'━'*54}\n")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="ZenPosture Reel Maker v4 — CEO Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Scripts:
          office_worker   Desk-worker back pain → ZenPosture solution
          pain_hook       Aggressive cold-audience hook (shorter)
          new_mom         Postpartum recovery audience
          showcase        All products — best for brand awareness ads

        Examples:
          python reel_maker.py --script office_worker --output office.mp4
          python reel_maker.py --script new_mom --music track.mp3 --output mom.mp4
          python reel_maker.py --script showcase --letterbox --output brand.mp4

        Free music: https://pixabay.com/music/  (search 'motivational')
        """)
    )
    p.add_argument("--script",   choices=["office_worker","pain_hook","new_mom","showcase"], required=True)
    p.add_argument("--output",   default="zenposture_reel.mp4")
    p.add_argument("--music",    default=None, help="Path to MP3 (optional; auto-generates if not given)")
    p.add_argument("--images",   default=DEFAULT_IMAGES, help="Path to product images folder")
    p.add_argument("--letterbox",action="store_true", help="Add cinematic letterbox bars")
    p.add_argument("--list",     action="store_true")
    args = p.parse_args()

    if args.list:
        print("\nScripts: office_worker | pain_hook | new_mom | showcase\n")
        sys.exit(0)

    build(args.script, args.output, args.images, args.music, args.letterbox)


if __name__ == "__main__":
    main()
