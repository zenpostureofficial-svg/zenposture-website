# ZenPosture Reel Maker 🎬

Generate branded Instagram/Facebook Reels (1080×1920) in minutes — no Canva, no editor needed.

## Quick Start

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Install ffmpeg (one-time)
- **Windows:** Download from https://ffmpeg.org/download.html → add to PATH
- **Mac:** `brew install ffmpeg`
- **Linux/Ubuntu:** `sudo apt install ffmpeg`

### 3. Make your reel
```bash
# Office Worker reel (best for ads)
python reel_maker.py --script office_worker --output office_reel.mp4

# New Mom reel
python reel_maker.py --script new_mom --output mom_reel.mp4

# Short pain hook (15-18 seconds)
python reel_maker.py --script pain_hook --output pain_reel.mp4

# Add background music
python reel_maker.py --script office_worker --music background.mp3 --output office_reel.mp4

# Build your own slides interactively
python reel_maker.py --custom --output my_reel.mp4
```

## Output
- Format: MP4 (H.264 + AAC)
- Resolution: 1080×1920 (Instagram/Facebook Reels ready)
- Frame rate: 30fps

## Available Scripts

| Script | Slides | Duration | Best For |
|--------|--------|----------|----------|
| `office_worker` | 6 | ~23s | Cold audience, desk workers |
| `pain_hook` | 5 | ~18s | Aggressive retargeting |
| `new_mom` | 6 | ~25s | Women 25-35, postpartum |

## Tips
- Add royalty-free music from [pixabay.com/music](https://pixabay.com/music/) for better engagement
- Upload directly to Instagram Reels, Facebook Reels, or Meta Ads Manager
- Run all 3 versions as A/B test with ₹300-500/day each for 5 days, then scale the winner
