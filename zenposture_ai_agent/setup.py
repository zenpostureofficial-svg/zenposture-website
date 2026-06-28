"""
ZenPosture AI Agent — Setup
Run this once to install all dependencies.
"""
import subprocess, sys

PACKAGES = [
    # Core
    "requests",
    # Browser control
    "playwright",
    # Computer control
    "pyautogui",
    "pillow",
    # Web search
    "duckduckgo-search",
    # Google Ads (optional — comment out if not using yet)
    # "google-ads",
    # Voice output (optional)
    "edge-tts",
]

def run(cmd):
    print(f"  Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

print("\n  Installing ZenBot dependencies...\n")
for pkg in PACKAGES:
    if pkg.startswith("#"): continue
    run(f"{sys.executable} -m pip install {pkg} -q")

print("\n  Installing Playwright browsers...")
run("playwright install chromium")

print("""
  ✅  Setup complete!

  Next steps:
  1. Edit config/credentials.json — add your API keys:
     • Shopify access token
     • Meta (Facebook/Instagram) access token
     • Google Ads credentials
     • YouTube credentials

  2. Run the agent:
     python agent.py

  3. Type 'help' to see all commands.
""")
