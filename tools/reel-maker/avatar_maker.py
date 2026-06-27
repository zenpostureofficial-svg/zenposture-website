"""
ZenPosture Avatar Maker v1
==========================
Generates a talking-head video from your photo + script.
100% local. Zero credits. Optimized for RTX 5060 8GB.

Pipeline:
  Script text → Coqui XTTS v2 (voice clone) → WAV audio
  Photo + WAV  → SadTalker             → talking head MP4

First time:
  setup_avatar.bat          ← run this once

Then use:
  python avatar_maker.py --photo masroor.jpg --script founder_script.txt --output founder.mp4
  python avatar_maker.py --photo masroor.jpg --script founder_script.txt --voice-sample my_voice.wav --output founder.mp4
  python avatar_maker.py --photo masroor.jpg --script ugc_script.txt --persona "young Indian woman, office worker" --output ugc_woman.mp4
"""

import argparse, os, sys, subprocess, textwrap, shutil, time
import urllib.request

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE        = os.path.dirname(os.path.abspath(__file__))
_ASSETS      = os.path.join(_HERE, "_assets")
_SADTALKER   = os.path.join(_HERE, "_tools", "SadTalker")
_CHECKPOINTS = os.path.join(_SADTALKER, "checkpoints")
_GFPGAN      = os.path.join(_SADTALKER, "gfpgan", "weights")
_TEMP_VOICE  = os.path.join(_ASSETS, "temp_voice.wav")
_TEMP_AVATAR = os.path.join(_ASSETS, "temp_avatar.mp4")

os.makedirs(_ASSETS, exist_ok=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _bar(label, done, total, width=40):
    filled = int(width * done / max(total, 1))
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * done / max(total, 1))
    print(f"\r  {label} [{bar}] {pct}%", end="", flush=True)


def _download(url, dest, label=None):
    label = label or os.path.basename(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):
        print(f"  ✅  {label} — already downloaded")
        return True
    print(f"  ⬇️   Downloading {label}…")
    try:
        def reporthook(count, block, total):
            _bar(label, count * block, total)
        urllib.request.urlretrieve(url, dest, reporthook)
        print()
        return True
    except Exception as e:
        print(f"\n  ⚠️   Failed to download {label}: {e}")
        return False


def _run(cmd, cwd=None, label=""):
    if label:
        print(f"  ⚙️   {label}…")
    result = subprocess.run(cmd, cwd=cwd, shell=True,
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ❌  Error:\n{result.stderr[-1000:]}")
        return False
    return True


def check_sadtalker():
    if not os.path.isdir(_SADTALKER):
        print("\n  ❌  SadTalker not found.")
        print("  Run setup_avatar.bat first.\n")
        sys.exit(1)

    required = [
        os.path.join(_CHECKPOINTS, "SadTalker_V0.0.2_256.safetensors"),
        os.path.join(_CHECKPOINTS, "mapping_00109-model.pth.tar"),
        os.path.join(_GFPGAN, "GFPGANv1.4.pth"),
    ]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print("\n  ❌  SadTalker checkpoints missing:")
        for m in missing:
            print(f"      {os.path.basename(m)}")
        print("  Run setup_avatar.bat to download them.\n")
        sys.exit(1)


def download_sadtalker_models():
    """Download all SadTalker model checkpoints."""
    os.makedirs(_CHECKPOINTS, exist_ok=True)
    os.makedirs(_GFPGAN, exist_ok=True)

    models = [
        (
            "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors",
            os.path.join(_CHECKPOINTS, "SadTalker_V0.0.2_256.safetensors"),
        ),
        (
            "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors",
            os.path.join(_CHECKPOINTS, "SadTalker_V0.0.2_512.safetensors"),
        ),
        (
            "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar",
            os.path.join(_CHECKPOINTS, "mapping_00109-model.pth.tar"),
        ),
        (
            "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar",
            os.path.join(_CHECKPOINTS, "mapping_00229-model.pth.tar"),
        ),
        (
            "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth",
            os.path.join(_GFPGAN, "GFPGANv1.4.pth"),
        ),
        (
            "https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth",
            os.path.join(_GFPGAN, "detection_Resnet50_Final.pth"),
        ),
        (
            "https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth",
            os.path.join(_GFPGAN, "parsing_parsenet.pth"),
        ),
    ]

    print("\n  Downloading SadTalker model checkpoints (~2 GB total)…\n")
    ok = True
    for url, dest in models:
        ok = ok and _download(url, dest)
    return ok


# ─── Voice Generation (Coqui XTTS v2) ────────────────────────────────────────

def generate_voice(script_text, voice_sample=None, output_path=_TEMP_VOICE,
                   language="en", speed=0.9):
    """
    Convert script text to WAV using Coqui XTTS v2.
    If voice_sample is given, clones that voice.
    Otherwise uses a clear default male English voice.
    """
    print("\n  🎙️   Generating voice with Coqui XTTS v2…")

    try:
        import torch
        from TTS.api import TTS
    except ImportError:
        print("  ❌  Coqui TTS not installed. Run: pip install TTS")
        sys.exit(1)

    device = "cuda" if __import__("torch").cuda.is_available() else "cpu"
    print(f"  🖥️   Using device: {device}")
    if device == "cpu":
        print("  ⚠️   GPU not detected — voice generation will be slow (~5 min). Normal on first run.")

    # Split long scripts into chunks to avoid XTTS context limits
    chunks = _split_script(script_text, max_chars=230)
    print(f"  📝  Script split into {len(chunks)} chunks for processing…")

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(_ASSETS, f"chunk_{i:03d}.wav")
        print(f"  🔊  Chunk {i+1}/{len(chunks)}: {chunk[:50]}…")

        if voice_sample and os.path.exists(voice_sample):
            tts.tts_to_file(
                text=chunk,
                speaker_wav=voice_sample,
                language=language,
                file_path=chunk_path,
                speed=speed,
            )
        else:
            # Default XTTS speaker — clear professional male voice
            tts.tts_to_file(
                text=chunk,
                speaker="Aaron Dreschner",
                language=language,
                file_path=chunk_path,
                speed=speed,
            )
        chunk_files.append(chunk_path)

    # Concatenate all chunks into single WAV
    _concat_wav(chunk_files, output_path)

    # Cleanup chunks
    for f in chunk_files:
        if os.path.exists(f):
            os.remove(f)

    dur = _wav_duration(output_path)
    print(f"  ✅  Voice generated → {output_path}  ({dur:.0f}s)")
    return output_path


def _split_script(text, max_chars=230):
    """Split script into sentence chunks that XTTS can handle cleanly."""
    import re
    sentences = re.split(r'(?<=[.!?—])\s+', text.strip())
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 <= max_chars:
            current = (current + " " + s).strip()
        else:
            if current:
                chunks.append(current)
            current = s
    if current:
        chunks.append(current)
    return chunks


def _concat_wav(files, output):
    """Concatenate multiple WAV files using wave module."""
    import wave
    os.makedirs(os.path.dirname(output), exist_ok=True)
    data = []
    params = None
    for f in files:
        with wave.open(f, "rb") as w:
            if params is None:
                params = w.getparams()
            data.append(w.readframes(w.getnframes()))
    with wave.open(output, "wb") as out:
        out.setparams(params)
        for d in data:
            out.writeframes(d)


def _wav_duration(path):
    import wave
    with wave.open(path, "rb") as w:
        return w.getnframes() / w.getframerate()


# ─── Avatar Generation (SadTalker) ───────────────────────────────────────────

def generate_avatar(photo_path, audio_path, output_path=_TEMP_AVATAR,
                    enhancer=True, size=256, still=False):
    """
    Animate a portrait photo with audio using SadTalker.
    photo_path : path to your portrait JPG/PNG
    audio_path : path to WAV from generate_voice()
    output_path: final MP4
    enhancer   : True = GFPGAN face enhancement (sharper, better quality)
    size       : 256 (faster) or 512 (higher quality, needs more VRAM)
    still      : True = minimal head movement (good for long videos)
    """
    check_sadtalker()

    photo_path = os.path.abspath(photo_path)
    audio_path = os.path.abspath(audio_path)
    out_dir    = os.path.abspath(os.path.join(_ASSETS, "sadtalker_out"))
    os.makedirs(out_dir, exist_ok=True)

    print("\n  🎭  Generating talking avatar with SadTalker…")
    print(f"  📸  Photo : {os.path.basename(photo_path)}")
    print(f"  🎵  Audio : {os.path.basename(audio_path)}")
    print(f"  📐  Size  : {size}px  |  Enhancer: {'on' if enhancer else 'off'}")
    print(f"  ⏱️   Estimated time: {_wav_duration(audio_path)/60 * 2:.0f}–{_wav_duration(audio_path)/60 * 4:.0f} min on RTX 5060\n")

    cmd_parts = [
        sys.executable, "inference.py",
        "--driven_audio", audio_path,
        "--source_image", photo_path,
        "--result_dir", out_dir,
        "--size", str(size),
        "--preprocess", "full",
    ]
    if enhancer:
        cmd_parts += ["--enhancer", "gfpgan"]
    if still:
        cmd_parts += ["--still"]

    cmd = " ".join(f'"{p}"' if " " in str(p) else str(p) for p in cmd_parts)

    result = subprocess.run(cmd, cwd=_SADTALKER, shell=True)
    if result.returncode != 0:
        print("\n  ❌  SadTalker failed. Check the error above.")
        sys.exit(1)

    # SadTalker saves to result_dir with a timestamped subfolder — find it
    generated = _find_latest_mp4(out_dir)
    if not generated:
        print("  ❌  SadTalker finished but no MP4 found in output folder.")
        sys.exit(1)

    shutil.copy(generated, output_path)
    mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\n  ✅  Avatar video → {output_path}  ({mb:.1f} MB)")
    return output_path


def _find_latest_mp4(folder):
    """Find the most recently created MP4 in a directory tree."""
    mp4s = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith(".mp4"):
                mp4s.append(os.path.join(root, f))
    return max(mp4s, key=os.path.getmtime) if mp4s else None


# ─── Polish: add logo + URL overlay ──────────────────────────────────────────

def add_branding_overlay(input_mp4, output_mp4):
    """
    Add ZenPosture logo strip + URL to bottom of avatar video.
    Uses ffmpeg drawtext filter — no Python dependency.
    """
    print("  🎨  Adding ZenPosture branding overlay…")
    font_path = os.path.join(_ASSETS, "Montserrat-Bold.ttf")

    if os.path.exists(font_path):
        font_arg = f"fontfile='{font_path}':"
    else:
        font_arg = ""

    # Bottom bar with URL
    vf = (
        f"drawtext={font_arg}text='zenposture.in':"
        f"fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-60:"
        f"box=1:boxcolor=black@0.6:boxborderw=14,"
        f"drawtext={font_arg}text='ZENPOSTURE':"
        f"fontcolor=white:fontsize=28:x=40:y=30:"
        f"box=1:boxcolor=0x10B981@0.8:boxborderw=10"
    )

    cmd = (
        f'ffmpeg -y -i "{input_mp4}" '
        f'-vf "{vf}" '
        f'-c:v libx264 -crf 17 -preset medium '
        f'-c:a copy "{output_mp4}"'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 or not os.path.exists(output_mp4):
        print("  ⚠️   Branding overlay failed — using raw avatar video.")
        shutil.copy(input_mp4, output_mp4)
    else:
        mb = os.path.getsize(output_mp4) / 1024 / 1024
        print(f"  ✅  Branded video → {output_mp4}  ({mb:.1f} MB)")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="ZenPosture Avatar Maker v1 — Local AI Talking Head",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          # Founder pitch (no voice sample — uses default voice):
          python avatar_maker.py --photo masroor.jpg --script founder_script.txt --output founder.mp4

          # With YOUR cloned voice (record 30s of yourself talking):
          python avatar_maker.py --photo masroor.jpg --script founder_script.txt --voice-sample my_voice.wav --output founder.mp4

          # UGC customer review video:
          python avatar_maker.py --photo customer_f.jpg --script ugc_script.txt --output ugc.mp4

          # Higher quality (slower, needs more VRAM):
          python avatar_maker.py --photo masroor.jpg --script script.txt --size 512 --output hq.mp4

          # Download SadTalker models only:
          python avatar_maker.py --download-models
        """)
    )
    p.add_argument("--photo",          help="Portrait photo (JPG or PNG)")
    p.add_argument("--script",         help="Script as .txt file path OR quoted text string")
    p.add_argument("--voice-sample",   default=None,
                   help="30s WAV of your voice for cloning (optional)")
    p.add_argument("--output",         default="avatar_video.mp4")
    p.add_argument("--size",           type=int, choices=[256, 512], default=256,
                   help="Avatar resolution: 256 (fast) or 512 (HQ, needs 8GB VRAM)")
    p.add_argument("--still",          action="store_true",
                   help="Minimal head movement — better for long videos (3+ min)")
    p.add_argument("--no-enhancer",    action="store_true",
                   help="Skip GFPGAN face enhancement (faster, lower quality)")
    p.add_argument("--no-branding",    action="store_true",
                   help="Skip ZenPosture logo/URL overlay")
    p.add_argument("--language",       default="en",
                   help="Voice language code (en, hi, etc.)")
    p.add_argument("--download-models", action="store_true",
                   help="Download SadTalker checkpoints and exit")
    args = p.parse_args()

    print(f"\n{'━'*56}")
    print(f"  🤖  ZenPosture Avatar Maker v1")
    print(f"{'━'*56}\n")

    if args.download_models:
        download_sadtalker_models()
        print("\n  ✅  All models downloaded. Ready to generate avatars.\n")
        return

    if not args.photo or not args.script:
        p.print_help()
        sys.exit(1)

    if not os.path.exists(args.photo):
        print(f"  ❌  Photo not found: {args.photo}")
        sys.exit(1)

    # Load script
    if os.path.exists(args.script):
        with open(args.script, "r", encoding="utf-8") as f:
            script_text = f.read().strip()
    else:
        script_text = args.script.strip()

    if len(script_text) < 10:
        print("  ❌  Script is empty or too short.")
        sys.exit(1)

    print(f"  📸  Photo    : {args.photo}")
    print(f"  📝  Script   : {len(script_text)} chars  ({len(script_text.split()):.0f} words)")
    if args.voice_sample:
        print(f"  🎙️   Voice    : cloning from {args.voice_sample}")
    else:
        print(f"  🎙️   Voice    : default (Aaron Dreschner / professional male)")
    print(f"  📐  Size     : {args.size}px")
    print(f"  💾  Output   : {args.output}\n")

    t0 = time.time()

    # Step 1: Voice
    voice_path = generate_voice(
        script_text,
        voice_sample=args.voice_sample,
        language=args.language,
    )

    # Step 2: Avatar
    raw_avatar = _TEMP_AVATAR
    generate_avatar(
        photo_path=args.photo,
        audio_path=voice_path,
        output_path=raw_avatar,
        enhancer=not args.no_enhancer,
        size=args.size,
        still=args.still,
    )

    # Step 3: Branding overlay
    if args.no_branding:
        shutil.copy(raw_avatar, args.output)
    else:
        add_branding_overlay(raw_avatar, args.output)

    elapsed = int(time.time() - t0)
    mb = os.path.getsize(args.output) / 1024 / 1024
    print(f"\n{'━'*56}")
    print(f"  ✅  DONE!  {args.output}  ({mb:.1f} MB)")
    print(f"  ⏱️   Total time: {elapsed // 60}m {elapsed % 60}s")
    print(f"  🚀  Ready for Meta Ads / YouTube / Investor pitch")
    print(f"{'━'*56}\n")


if __name__ == "__main__":
    main()
