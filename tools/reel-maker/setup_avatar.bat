@echo off
setlocal enabledelayedexpansion
title ZenPosture Avatar Maker — One-Click Setup

echo.
echo  ══════════════════════════════════════════════════
echo    ZenPosture Avatar Maker — Setup
echo    RTX 5060 8GB  ^|  Windows 11
echo  ══════════════════════════════════════════════════
echo.

REM ── Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.10+ from python.org
    pause & exit /b 1
)
echo  [OK] Python found

REM ── Check Git ─────────────────────────────────────────────────────────────
git --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Git not found. Install Git from git-scm.com
    pause & exit /b 1
)
echo  [OK] Git found

REM ── Check FFmpeg ──────────────────────────────────────────────────────────
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo  [WARN] FFmpeg not found — branding overlay will be skipped.
    echo         Install from: https://ffmpeg.org/download.html
    echo         Add ffmpeg\bin to your PATH, then re-run this setup.
    echo.
) else (
    echo  [OK] FFmpeg found
)

echo.
echo  Step 1/5 — Installing PyTorch with CUDA 12.6 (RTX 5060 support)...
echo  (This downloads ~2 GB — takes 5-10 min on first run)
echo.
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
if errorlevel 1 (
    echo  [WARN] CUDA 12.6 install failed. Trying CUDA 12.4...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
)
echo  [OK] PyTorch installed

echo.
echo  Step 2/5 — Installing Coqui TTS (voice cloning)...
pip install TTS
if errorlevel 1 (
    echo  [ERROR] Coqui TTS install failed.
    pause & exit /b 1
)
echo  [OK] Coqui TTS installed

echo.
echo  Step 3/5 — Installing reel maker dependencies...
pip install moviepy==1.0.3 Pillow>=10.0.0 numpy>=1.24.0 requests>=2.31.0 safetensors
echo  [OK] Dependencies installed

echo.
echo  Step 4/5 — Cloning SadTalker...
if not exist "_tools" mkdir _tools
if exist "_tools\SadTalker" (
    echo  [OK] SadTalker already cloned — skipping
) else (
    git clone https://github.com/OpenTalker/SadTalker _tools\SadTalker
    if errorlevel 1 (
        echo  [ERROR] Failed to clone SadTalker. Check your internet connection.
        pause & exit /b 1
    )
    echo  [OK] SadTalker cloned
)

echo.
echo  Installing SadTalker requirements...
pip install -r _tools\SadTalker\requirements.txt
echo  [OK] SadTalker requirements installed

echo.
echo  Step 5/5 — Downloading AI model checkpoints (~2 GB)...
echo  (This only happens once — models are cached for future use)
echo.
python avatar_maker.py --download-models
if errorlevel 1 (
    echo  [WARN] Some models may not have downloaded. Run again if needed.
)

echo.
echo  ══════════════════════════════════════════════════
echo    Setup Complete!
echo  ══════════════════════════════════════════════════
echo.
echo  To verify GPU is detected:
echo    python -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"
echo.
echo  To generate your founder video:
echo    python avatar_maker.py --photo masroor.jpg --script founder_script.txt --output founder.mp4
echo.
echo  To clone your own voice (record 30s of yourself first):
echo    python avatar_maker.py --photo masroor.jpg --script founder_script.txt --voice-sample my_voice.wav --output founder.mp4
echo.
pause
