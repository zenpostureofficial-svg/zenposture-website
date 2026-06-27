# ZenPosture Cinematic Reel Maker v2 🎬

Generate Hollywood-grade branded Instagram/Facebook Reels (1080×1920).

## What's included
- ✅ Real stock images auto-downloaded from Unsplash (free, no API key)
- ✅ Ken Burns cinematic zoom & pan on every scene
- ✅ Cinematic teal-orange color grade
- ✅ Film grain + vignette overlay
- ✅ Smooth cross-dissolve transitions
- ✅ Animated text with glow & shadow
- ✅ Optional letterbox bars (2.35:1 drama)
- ✅ Background music with auto fade-out
- ✅ 3 built-in scripts + fully custom mode

---

## Quick Start

### 1. Install dependencies
```powershell
pip install -r requirements.txt
```

### 2. Install ffmpeg (one-time)
- **Windows:** https://ffmpeg.org/download.html → extract → add `bin` folder to PATH
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

### 3. Make your reel
```powershell
# Office Worker (best for ads — 23s)
python reel_maker.py --script office_worker --output office.mp4

# Pain Hook (aggressive — 18s)
python reel_maker.py --script pain_hook --output pain.mp4

# New Mom audience (25s)
python reel_maker.py --script new_mom --output mom.mp4

# Add cinematic letterbox bars
python reel_maker.py --script office_worker --letterbox --output office_cinema.mp4

# Add background music
python reel_maker.py --script office_worker --music bg.mp3 --output office_music.mp4

# Build completely custom slides
python reel_maker.py --custom --output custom.mp4
```

---

## Where is my MP4 saved?
In the same folder you ran the command from:
```
C:\Users\ADMIN\zenposture-website\tools\reel-maker\office.mp4
```

---

## Free Background Music
1. Go to https://pixabay.com/music/
2. Search **"motivation"** or **"cinematic"** or **"inspiring"**
3. Download MP3
4. Run: `python reel_maker.py --script office_worker --music downloaded_track.mp3 --output final.mp4`

---

## Available Scripts

| Script | Scenes | Duration | Best For |
|--------|--------|----------|----------|
| `office_worker` | 6 | 24s | Desk workers, back pain |
| `pain_hook` | 5 | 18s | Cold audience retargeting |
| `new_mom` | 6 | 25s | Women 25–35, postpartum |

## Available Image Moods (for custom mode)
- `tired_desk` — Person at laptop, tired/stressed
- `back_pain` — Someone holding their back in pain
- `confident_posture` — Athletic/confident standing person
- `happy_customer` — Smiling, satisfied customer
- `product_clean` — Clean product/wellness flat lay
- `new_mom` — Mother with baby
- `pain_hook` — Neck/back pain, stressed
- `cta_end` — Zen/wellness, confident lifestyle

---

## Ad Strategy
Run all 3 scripts as A/B test with ₹300–500/day each for 5 days.
Kill lowest CTR. Scale the winner to ₹1,500–2,000/day.
Upload directly to **Meta Ads Manager → Reels placement**.
