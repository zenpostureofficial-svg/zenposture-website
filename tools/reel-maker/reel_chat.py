"""
ZenPosture Reel Chat — AI Chatbot Interface
============================================
Talk to your reel maker in plain English.

Usage:
  python reel_chat.py
  python reel_chat.py --model qwen2.5:14b
  python reel_chat.py --model llama3.1:8b

Commands (type in chat):
  "make a reel for new moms"
  "create a gym reel, aggressive tone"
  "regenerate the last one with different music"
  "use gemma4 model"
  "quit" / "exit"
"""

import os, sys, json, subprocess, traceback, random, re, time
import urllib.request

_HERE   = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_HERE, "_assets")
os.makedirs(_ASSETS, exist_ok=True)

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_CHAT  = "http://localhost:11434/api/chat"

DEFAULT_MODEL = "llama3.1:8b"

CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
DIM    = "\033[2m"

# ── Ollama helpers ────────────────────────────────────────────────────────────

def ollama_available():
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=3)
        return True
    except Exception:
        return False


def chat_with_ollama(messages, model):
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.85}
    }).encode()
    req = urllib.request.Request(
        OLLAMA_CHAT, data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        resp = json.loads(r.read())
    return resp["message"]["content"].strip()


def extract_json(text):
    """Pull first JSON object out of LLM response."""
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{"):
                text = p
                break
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None


# ── Intent parser ─────────────────────────────────────────────────────────────

SYSTEM_INTENT = """You are a helpful assistant for ZenPosture, an Indian D2C posture & recovery brand.
The user talks to you in natural language about making Instagram Reels.

Your job: parse the user's request and return ONLY a JSON object (no markdown, no explanation):
{
  "action": "make_reel" | "regenerate" | "change_model" | "list_models" | "help" | "chat",
  "script": "new_mom" | "office_worker" | "pain_hook" | "showcase" | null,
  "mood": "motivational" | "emotional" | "energetic" | "calm" | null,
  "tone": "aggressive" | "soft" | "funny" | "emotional" | "professional" | null,
  "output": "filename.mp4" | null,
  "model": "model_name" | null,
  "custom_brief": "any extra creative direction the user gave" | null,
  "reply": "a short friendly reply to show the user before you start working"
}

Rules:
- new_mom = postpartum, baby, mother, mom, mummy
- office_worker = desk job, back pain, sitting, office, posture corrector
- gym = fitness, lifting, deadlift, belt, gym → map to "pain_hook" script
- showcase = brand, all products, general
- If user just chats (not requesting a reel), set action=chat and reply normally
- mood: new_mom→emotional, gym→energetic, office→motivational, default→motivational
"""

SYSTEM_SCRIPT = """You are a viral Instagram Reels copywriter for ZenPosture, an Indian D2C health brand.
Price is always ₹499. Website: zenposture.in.

User brief: {brief}
Product: {product}
Audience: {audience}
Tone: {tone}
Mood: {mood}

Write a 6-scene Instagram Reel script. Return ONLY valid JSON (no markdown):
{{
  "hook":   {{"line1": "CAPS HOOK\\nLINE2", "line2": "punchy subline", "caption": "subtitle"}},
  "pain":   {{"headline": "short\\npain\\nline", "sub": "one explanation line", "caption": "caption"}},
  "reveal": {{"headline": "benefit\\nline2", "sub": "feature line", "caption": "caption"}},
  "social": {{"headline": "⭐⭐⭐⭐⭐", "sub": "testimonial\\n— Name, City", "caption": "caption"}},
  "price":  {{"caption": "₹499 offer line", "tag": "SHORT TAG"}},
  "cta":    {{"headline": "emotional\\ncta\\nline", "caption": "caption with zenposture.in"}}
}}

STRICT RULES:
- line1 in hook: ALL CAPS, max 4 words per \\n-separated line, max 4 lines total
- pain headline: max 3 lines, each max 4 words
- All lines SHORT — this appears on a phone screen
- Make it emotionally scroll-stopping for Indian audience
"""

PRODUCTS = {
    "new_mom":       ("ZenPosture Postpartum Belt",      "new Indian mothers 25-40, postpartum recovery"),
    "office_worker": ("ZenPosture Posture Corrector",    "Indian office workers 22-45, desk job back pain"),
    "pain_hook":     ("ZenPosture Compression Belt",     "Indian gym-goers 20-40, weightlifting"),
    "showcase":      ("ZenPosture full product range",   "health-conscious Indians, general audience"),
}

IMG_FOR_SCRIPT = {
    "new_mom":       "postpartum",
    "office_worker": "at_work",
    "pain_hook":     "fitness",
    "showcase":      "hero",
}


# ── Reel builder ──────────────────────────────────────────────────────────────

def build_reel_from_data(data, script_key, output, mood, images_dir):
    """Import reel_maker internals and render from Ollama JSON data."""
    sys.path.insert(0, _HERE)
    import reel_maker as rm

    img_key = IMG_FOR_SCRIPT.get(script_key, "hero")

    clips = [
        rm.scene_pattern_interrupt(
            data["hook"].get("line1", "STOP SCROLLING"),
            data["hook"].get("line2", ""),
            caption=data["hook"].get("caption", ""),
            duration=3.0
        ),
        rm.scene_pain(
            img_key,
            data["pain"].get("headline", "It hurts.\nEvery day."),
            data["pain"].get("sub", "Your body needs support."),
            images_dir,
            caption=data["pain"].get("caption", ""),
            duration=3.0, do_shake=True, tag="REAL TALK"
        ),
        rm.scene_comparison_wipe(
            images_dir,
            data["reveal"].get("headline", "ZenPosture\nFixes This."),
            data["reveal"].get("sub", "Soft. Breathable. Effective."),
            caption=data["reveal"].get("caption", ""),
            duration=4.5
        ),
        rm.scene_happy_customers(
            images_dir,
            data["social"].get("headline", "⭐⭐⭐⭐⭐"),
            data["social"].get("sub", '"Changed my life."\n— Happy Customer'),
            caption=data["social"].get("caption", ""),
            duration=3.5, tag="REAL RESULTS"
        ),
        rm.scene_price_reveal(
            img_key, images_dir,
            caption=data["price"].get("caption", "₹499 only. Free shipping. COD."),
            duration=3.0, tag=data["price"].get("tag", "LIMITED OFFER")
        ),
        rm.scene_cta(
            img_key, images_dir,
            data["cta"].get("headline", "Order now.\nzenposture.in"),
            caption=data["cta"].get("caption", "Free shipping · COD · 30-day returns"),
            duration=3.5
        ),
    ]

    from moviepy.editor import concatenate_videoclips, AudioFileClip
    final = concatenate_videoclips(clips, method="compose")

    music_path = rm.get_music_path(mood=mood)
    if music_path and os.path.exists(music_path):
        audio = AudioFileClip(music_path).volumex(0.26)
        if audio.duration < final.duration:
            from moviepy.editor import concatenate_audioclips
            loops = int(final.duration / audio.duration) + 2
            audio = concatenate_audioclips([audio] * loops)
        audio = audio.subclip(0, final.duration).audio_fadeout(2.0)
        final = final.set_audio(audio)
    else:
        print(f"{YELLOW}  ⚠️  No music found — using silent fallback{RESET}")

    print(f"\n{DIM}  Rendering {output}…{RESET}")
    final.write_videofile(
        output, fps=rm.FPS, codec="libx264", audio_codec="aac",
        temp_audiofile="temp_audio.m4a", remove_temp=True,
        preset="medium", ffmpeg_params=["-crf", "17", "-pix_fmt", "yuv420p"],
        logger=None,
    )
    mb = os.path.getsize(output) / 1024 / 1024
    return mb


# ── Self-healing renderer ─────────────────────────────────────────────────────

def safe_render(data, script_key, output, mood, images_dir, model, attempt=1, max_attempts=3):
    """Try to render. On error, ask Ollama to fix the data and retry."""
    try:
        mb = build_reel_from_data(data, script_key, output, mood, images_dir)
        return mb, data
    except Exception as e:
        err = traceback.format_exc()
        if attempt >= max_attempts:
            raise
        print(f"\n{YELLOW}  ⚠️  Render error (attempt {attempt}/{max_attempts}): {e}{RESET}")
        print(f"{DIM}  Asking Ollama to fix the script…{RESET}")

        fix_messages = [
            {"role": "system", "content": (
                "You are a JSON repair assistant. The user has a reel script JSON that caused a render error. "
                "Fix any issues (too-long lines, bad characters, missing keys) and return ONLY the corrected JSON."
            )},
            {"role": "user", "content": (
                f"This JSON caused an error:\n{json.dumps(data, indent=2)}\n\n"
                f"Error:\n{err[:800]}\n\n"
                "Return ONLY the fixed JSON object."
            )}
        ]
        try:
            fix_text = chat_with_ollama(fix_messages, model)
            fixed = extract_json(fix_text)
            if fixed:
                print(f"{GREEN}  ✅  Script auto-fixed. Retrying render…{RESET}\n")
                return safe_render(fixed, script_key, output, mood, images_dir, model, attempt + 1, max_attempts)
        except Exception as fix_e:
            print(f"{RED}  ❌  Auto-fix failed: {fix_e}{RESET}")
        raise


# ── Main chat loop ────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--images", default=None)
    args = ap.parse_args()

    model = args.model
    images_dir = args.images or os.path.normpath(
        os.path.join(_HERE, "../../public/images")
    )

    print(f"\n{BOLD}{CYAN}{'═'*56}{RESET}")
    print(f"{BOLD}{CYAN}  ZenPosture Reel Chat  —  AI Reel Generator{RESET}")
    print(f"{CYAN}{'═'*56}{RESET}")
    print(f"{DIM}  Model  : {model}")
    print(f"  Images : {images_dir}")
    print(f"  Type 'help' for commands or just describe what you want.{RESET}\n")

    if not ollama_available():
        print(f"{RED}  ❌  Ollama not running. Start it with: ollama serve{RESET}\n")
        sys.exit(1)

    print(f"{GREEN}  ✅  Ollama connected.{RESET}")
    print(f"{CYAN}  Say something like:{RESET}")
    print(f"{DIM}    • make a reel for new moms")
    print(f"    • create a gym reel, aggressive tone")
    print(f"    • make office worker reel, calm music")
    print(f"    • regenerate with different music")
    print(f"    • use model qwen2.5:14b{RESET}\n")

    conversation_history = [
        {"role": "system", "content": SYSTEM_INTENT}
    ]
    last_script_key = None
    last_output     = None
    last_data       = None
    reel_count      = 0

    while True:
        try:
            user_input = input(f"{BOLD}{CYAN}You:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}  Goodbye!{RESET}\n")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye", "q"):
            print(f"\n{GREEN}  Reels generated this session: {reel_count}{RESET}")
            print(f"{DIM}  Goodbye!{RESET}\n")
            break

        # Add to conversation
        conversation_history.append({"role": "user", "content": user_input})

        # ── Parse intent ──────────────────────────────────────────────────────
        print(f"{DIM}  Thinking…{RESET}", end="\r")
        try:
            intent_messages = [
                {"role": "system", "content": SYSTEM_INTENT},
                {"role": "user",   "content": user_input}
            ]
            intent_text = chat_with_ollama(intent_messages, model)
            intent = extract_json(intent_text)
        except Exception as e:
            print(f"{RED}  ❌  Ollama error: {e}{RESET}")
            continue

        if not intent:
            print(f"\n{YELLOW}  Bot:{RESET} I didn't quite catch that. Try: 'make a reel for new moms'\n")
            continue

        action = intent.get("action", "chat")
        reply  = intent.get("reply", "")

        # ── Handle model change ───────────────────────────────────────────────
        if action == "change_model":
            new_model = intent.get("model") or user_input.split()[-1]
            model = new_model
            print(f"\n{GREEN}  Bot:{RESET} Switched to model: {BOLD}{model}{RESET}\n")
            continue

        if action == "list_models":
            print(f"\n{GREEN}  Bot:{RESET} Run {BOLD}ollama list{RESET} in another terminal to see your models.\n")
            continue

        if action == "help":
            print(f"\n{GREEN}  Bot:{RESET} Here's what I can do:")
            print(f"{DIM}  • 'make a reel for new moms' — generates postpartum reel")
            print(f"  • 'make an office worker reel, emotional music' — desk job reel")
            print(f"  • 'create gym reel, aggressive' — fitness belt reel")
            print(f"  • 'regenerate' — new version of last reel with fresh music")
            print(f"  • 'use model qwen2.5:14b' — switch AI model")
            print(f"  • 'quit' — exit{RESET}\n")
            continue

        if action == "chat":
            if reply:
                print(f"\n{GREEN}  Bot:{RESET} {reply}\n")
            else:
                print(f"\n{GREEN}  Bot:{RESET} I'm your reel maker! Tell me what kind of reel to create.\n")
            continue

        # ── Regenerate ────────────────────────────────────────────────────────
        if action == "regenerate":
            if not last_script_key:
                print(f"\n{YELLOW}  Bot:{RESET} No reel made yet! Tell me what to create first.\n")
                continue
            script_key = last_script_key
            mood       = intent.get("mood") or "motivational"
            reel_count += 1
            output     = f"reel_{script_key}_{reel_count:02d}.mp4"
            print(f"\n{GREEN}  Bot:{RESET} {reply or 'Regenerating with fresh music and new script!'}")
            print(f"{DIM}  Output: {output}{RESET}\n")

            product, audience = PRODUCTS[script_key]
            script_messages = [
                {"role": "system", "content": SYSTEM_SCRIPT.format(
                    brief="Fresh version — different angle, different hook",
                    product=product, audience=audience,
                    tone=intent.get("tone") or "emotional",
                    mood=mood
                )}
            ]
            try:
                script_text = chat_with_ollama(script_messages, model)
                data = extract_json(script_text)
                if not data:
                    raise ValueError("No JSON in response")
            except Exception as e:
                print(f"{RED}  ❌  Script generation failed: {e}{RESET}\n")
                continue

            try:
                mb, last_data = safe_render(data, script_key, output, mood, images_dir, model)
                last_output = output
                print(f"\n{BOLD}{GREEN}  ✅  Done! {output}  ({mb:.1f} MB){RESET}")
                print(f"{CYAN}  Ready for Instagram Reels / Meta Ads.{RESET}\n")
            except Exception as e:
                print(f"{RED}  ❌  Render failed after retries: {e}{RESET}\n")
            continue

        # ── Make reel ─────────────────────────────────────────────────────────
        if action == "make_reel":
            script_key = intent.get("script") or "office_worker"
            mood       = intent.get("mood") or "motivational"
            tone       = intent.get("tone") or "emotional"
            brief      = intent.get("custom_brief") or ""
            reel_count += 1
            output     = intent.get("output") or f"reel_{script_key}_{reel_count:02d}.mp4"

            print(f"\n{GREEN}  Bot:{RESET} {reply or 'On it! Generating your reel…'}")
            print(f"{DIM}  Script : {script_key} | Mood : {mood} | Tone : {tone}")
            print(f"  Output : {output}{RESET}\n")

            # Generate script with Ollama
            product, audience = PRODUCTS.get(script_key, PRODUCTS["office_worker"])
            script_messages = [
                {"role": "system", "content": SYSTEM_SCRIPT.format(
                    brief=brief, product=product, audience=audience,
                    tone=tone, mood=mood
                )}
            ]
            print(f"{DIM}  Writing viral script…{RESET}", end="\r")
            try:
                script_text = chat_with_ollama(script_messages, model)
                data = extract_json(script_text)
                if not data:
                    raise ValueError("Ollama returned no valid JSON")
                print(f"{GREEN}  ✅  Script generated.          {RESET}")
            except Exception as e:
                print(f"{RED}  ❌  Script generation failed: {e}{RESET}")
                print(f"{DIM}  Falling back to built-in script…{RESET}\n")
                # Fall back to built-in script
                try:
                    sys.path.insert(0, _HERE)
                    import reel_maker as rm
                    rm.build(script_key, output, images_dir, mood=mood)
                    last_script_key = script_key
                    last_output     = output
                    reel_count += 1
                except Exception as e2:
                    print(f"{RED}  ❌  Fallback also failed: {e2}{RESET}\n")
                continue

            # Show preview of generated script
            hook_preview = data.get("hook", {}).get("line1", "")[:40].replace("\n", " / ")
            print(f"{DIM}  Hook preview : {hook_preview}…{RESET}")

            # Render with self-healing
            try:
                mb, last_data = safe_render(data, script_key, output, mood, images_dir, model)
                last_script_key = script_key
                last_output     = output
                print(f"\n{BOLD}{GREEN}  ✅  Done! {output}  ({mb:.1f} MB){RESET}")
                print(f"{CYAN}  1080×1920 — Instagram / Facebook Reels ready{RESET}")
                print(f"{DIM}  Next: try 'regenerate' for a fresh version{RESET}\n")
            except Exception as e:
                print(f"{RED}  ❌  Render failed: {e}{RESET}\n")
            continue

        # Fallback
        print(f"\n{GREEN}  Bot:{RESET} {reply or 'Try: make a reel for new moms'}\n")


if __name__ == "__main__":
    main()
