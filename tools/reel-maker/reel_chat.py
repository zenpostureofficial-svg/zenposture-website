"""
ZenPosture AI Command Center
============================
A self-learning, multi-skill chatbot that controls your entire content pipeline.

Usage:
  python reel_chat.py
  python reel_chat.py --model qwen2.5:14b
  python reel_chat.py --reset-memory

Skills:
  • Reel Maker       — generate Instagram/Reels videos
  • Script Writer    — write UGC, ad, email, caption scripts
  • Marketing Advisor— strategy, hooks, audience advice
  • Product Expert   — knows your ZenPosture catalog
  • Memory           — remembers preferences, what worked, your brand voice
"""

import os, sys, json, traceback, random, re, time, datetime, textwrap
import urllib.request
import argparse

_HERE    = os.path.dirname(os.path.abspath(__file__))
_ASSETS  = os.path.join(_HERE, "_assets")
_MEMORY  = os.path.join(_HERE, "_assets", "memory.json")
os.makedirs(_ASSETS, exist_ok=True)

OLLAMA_CHAT = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.1:8b"

# ── Terminal colors ───────────────────────────────────────────────────────────
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
DIM    = "\033[2m"
MAGENTA= "\033[95m"
WHITE  = "\033[97m"

def c(text, color): return f"{color}{text}{RESET}"
def hr(char="━", width=58): return char * width


# ── Brand knowledge base ──────────────────────────────────────────────────────
BRAND_KNOWLEDGE = """
BRAND: ZenPosture
WEBSITE: zenposture.in
PRICE: All products ₹499 (was ₹999 — 50% off)
SHIPPING: Free shipping across India
PAYMENT: COD (Cash on Delivery) available
RETURNS: 30-day money-back guarantee

PRODUCTS:
1. Posture Corrector
   - For: Office workers, desk job, 8hr sitting
   - Pain: Neck pain, shoulder tension, slouching
   - Benefit: Pulls shoulders back gently, retrains posture
   - Wear time: 2-4 hrs/day under shirt, invisible
   - Result timeline: Feel difference in 3 days, posture fixed in 2-3 weeks

2. Postpartum Recovery Belt
   - For: New mothers, 0-12 months post delivery
   - Pain: Weak core, lower back ache, diastasis recti
   - Benefit: Gentle core compression, supports healing
   - Material: Soft breathable fabric, wearable all day
   - Result: Back pain reduction in 7-10 days

3. Compression Belt (Fitness)
   - For: Gym-goers, deadlifts, squats, heavy lifting
   - Pain: Lower back injury risk, poor core activation
   - Benefit: Intra-abdominal pressure, protects spine
   - Result: Lift heavier, zero injuries, better form

TARGET AUDIENCE: Indian consumers 22-45, middle class, health-conscious
PLATFORM FOCUS: Instagram Reels, Facebook Reels, Meta Ads
TONE: Empathetic, direct, relatable, not overly medical
LANGUAGE: Mix of Hindi emotion + English — "abhi tak kisi ne nahi bataya"
"""

PRODUCTS_CATALOG = {
    "posture_corrector": {
        "name":     "ZenPosture Posture Corrector",
        "audience": "Indian office workers 22-45 with desk job back/neck pain",
        "pain":     "8 hours of sitting destroying spine, neck stiffness, slouching",
        "benefit":  "Gently pulls shoulders back, retrains posture muscle memory",
        "result":   "Feel difference in 3 days, visible posture change in 2 weeks",
        "script":   "office_worker",
        "img":      "at_work",
        "mood":     "motivational",
    },
    "postpartum_belt": {
        "name":     "ZenPosture Postpartum Recovery Belt",
        "audience": "Indian new mothers 25-40, 0-12 months post delivery",
        "pain":     "Weak core after childbirth, lower back ache while holding baby",
        "benefit":  "Gentle core compression, supports postpartum healing",
        "result":   "Back pain relief in 7-10 days, core support from day 1",
        "script":   "new_mom",
        "img":      "postpartum",
        "mood":     "emotional",
    },
    "compression_belt": {
        "name":     "ZenPosture Compression Belt",
        "audience": "Indian gym-goers 20-40, into deadlifts, squats, heavy training",
        "pain":     "Lower back injury risk, poor core bracing, fear of getting hurt",
        "benefit":  "Intra-abdominal pressure, protects spine, enables heavier lifts",
        "result":   "Lift 20kg more in 6 weeks, zero back injuries",
        "script":   "pain_hook",
        "img":      "fitness",
        "mood":     "energetic",
    },
}

SKILLS = {
    "make_reel":       "Create an Instagram/Facebook Reel video",
    "write_script":    "Write UGC, ad copy, email, caption, or any text content",
    "marketing_advice":"Give marketing strategy, hook ideas, audience targeting advice",
    "product_info":    "Answer questions about ZenPosture products",
    "remember":        "Store a preference, feedback, or note for future use",
    "recall":          "Show what I remember about preferences or past work",
    "chat":            "General conversation or clarification",
    "help":            "Show available commands",
}


# ── Persistent Memory ─────────────────────────────────────────────────────────

class Memory:
    def __init__(self, path):
        self.path = path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "preferences":   {},
            "feedback":      [],
            "successful_scripts": [],
            "failed_scripts":     [],
            "sessions":      [],
            "brand_notes":   [],
            "reel_count":    0,
            "model":         DEFAULT_MODEL,
        }

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def set(self, key, value):
        self.data["preferences"][key] = value
        self.save()

    def get(self, key, default=None):
        return self.data["preferences"].get(key, default)

    def add_feedback(self, output_file, rating, note=""):
        self.data["feedback"].append({
            "file": output_file, "rating": rating,
            "note": note, "ts": datetime.datetime.now().isoformat()
        })
        self.save()

    def add_success(self, script_data, product, output):
        self.data["successful_scripts"].append({
            "product": product, "output": output,
            "hook": script_data.get("hook", {}).get("line1", "")[:60],
            "ts": datetime.datetime.now().isoformat()
        })
        self.data["reel_count"] = self.data.get("reel_count", 0) + 1
        self.save()

    def add_note(self, note):
        self.data["brand_notes"].append({
            "note": note, "ts": datetime.datetime.now().isoformat()
        })
        self.save()

    def context_summary(self):
        prefs = self.data.get("preferences", {})
        notes = self.data.get("brand_notes", [])[-5:]
        successes = self.data.get("successful_scripts", [])[-3:]
        feedback  = self.data.get("feedback", [])[-3:]

        parts = []
        if prefs:
            parts.append("USER PREFERENCES: " + json.dumps(prefs))
        if notes:
            parts.append("BRAND NOTES: " + " | ".join(n["note"] for n in notes))
        if successes:
            hooks = [s.get("hook","") for s in successes]
            parts.append("RECENT WINNING HOOKS: " + " | ".join(hooks))
        if feedback:
            ratings = [f"{f['rating']}/5 — {f.get('note','')}" for f in feedback]
            parts.append("RECENT FEEDBACK: " + " | ".join(ratings))
        return "\n".join(parts)


# ── Ollama helpers ────────────────────────────────────────────────────────────

def ollama_available():
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=3)
        return True
    except Exception:
        return False


def chat(messages, model, temperature=0.85, timeout=120):
    payload = json.dumps({
        "model": model, "messages": messages,
        "stream": False, "options": {"temperature": temperature}
    }).encode()
    req = urllib.request.Request(
        OLLAMA_CHAT, data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read())
    return resp["message"]["content"].strip()


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        for part in text.split("```"):
            p = part.strip().lstrip("json").strip()
            if p.startswith("{"):
                text = p
                break
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    return None


# ── Intent engine ─────────────────────────────────────────────────────────────

INTENT_SYSTEM = """You are an AI assistant for ZenPosture, an Indian posture & recovery brand.
Parse the user's message and return ONLY a JSON object:
{{
  "skill": "make_reel"|"write_script"|"marketing_advice"|"product_info"|"remember"|"recall"|"chat"|"help",
  "product": "posture_corrector"|"postpartum_belt"|"compression_belt"|null,
  "tone": "aggressive"|"soft"|"funny"|"emotional"|"professional"|null,
  "mood": "motivational"|"emotional"|"energetic"|"calm"|null,
  "output_file": "filename.mp4"|null,
  "content_type": "ugc"|"ad"|"email"|"caption"|"hook"|"reel_script"|null,
  "platform": "instagram"|"facebook"|"email"|"whatsapp"|null,
  "model": "model_name_if_user_wants_to_change"|null,
  "memory_key": "key_to_store"|null,
  "memory_value": "value_to_store"|null,
  "brief": "any extra creative direction",
  "reply": "short friendly reply acknowledging the request (1 sentence)"
}}

Rules:
- new mom/postpartum/baby/mummy → postpartum_belt
- office/desk/posture/sitting/back pain → posture_corrector
- gym/fitness/lifting/deadlift/belt → compression_belt
- "remember X" or "note that X" → remember skill
- "what do you know" / "recall" / "show preferences" → recall skill
- If purely chatting or asking a question → chat skill
"""


def parse_intent(user_input, model, memory):
    mem_ctx = memory.context_summary()
    system = INTENT_SYSTEM
    if mem_ctx:
        system += f"\n\nCONTEXT FROM MEMORY:\n{mem_ctx}"

    messages = [
        {"role": "system",  "content": system},
        {"role": "user",    "content": user_input}
    ]
    try:
        resp = chat(messages, model, temperature=0.3)
        return extract_json(resp)
    except Exception as e:
        return {"skill": "chat", "reply": f"(parse error: {e})"}


# ── Script generation ─────────────────────────────────────────────────────────

SCRIPT_SYSTEM = """You are a top viral Instagram Reels copywriter for ZenPosture (India, ₹499 products).

BRAND KNOWLEDGE:
{brand}

MEMORY CONTEXT:
{memory}

REQUEST:
Product : {product_name}
Audience: {audience}
Pain    : {pain}
Benefit : {benefit}
Result  : {result}
Tone    : {tone}
Mood    : {mood}
Brief   : {brief}

Write a 6-scene Reel script. Return ONLY valid JSON (no markdown, no explanation):
{{
  "hook":   {{"line1": "CAPS\\nLINE2\\nLINE3", "line2": "punchy one-liner subtext", "caption": "subtitle for muted viewers"}},
  "pain":   {{"headline": "SHORT\\nPAIN\\nLINE", "sub": "one explanation sentence", "caption": "caption text"}},
  "reveal": {{"headline": "BENEFIT\\nLINE2", "sub": "feature/material sentence", "caption": "caption"}},
  "social": {{"headline": "⭐⭐⭐⭐⭐", "sub": "authentic testimonial\\n— First name, City", "caption": "social proof caption"}},
  "price":  {{"caption": "₹499 offer with COD/shipping mention", "tag": "3-4 WORD TAG"}},
  "cta":    {{"headline": "emotional\\ncta line\\nline3", "caption": "zenposture.in + benefit reminder"}}
}}

RULES (critical for mobile display):
- hook line1: ALL CAPS, max 4 words per line, use \\n for breaks, max 4 lines
- pain headline: max 3 lines, max 4 words each line
- Every text line must be SHORT — it appears on a 6-inch phone screen
- Make the hook stop the scroll — use POV, numbers, controversy, pain
- Indian audience — reference relatable situations
"""

def generate_script(product_key, tone, mood, brief, model, memory):
    prod = PRODUCTS_CATALOG.get(product_key, PRODUCTS_CATALOG["posture_corrector"])
    system = SCRIPT_SYSTEM.format(
        brand=BRAND_KNOWLEDGE,
        memory=memory.context_summary() or "No previous context.",
        product_name=prod["name"],
        audience=prod["audience"],
        pain=prod["pain"],
        benefit=prod["benefit"],
        result=prod["result"],
        tone=tone or "emotional",
        mood=mood or prod["mood"],
        brief=brief or "Fresh scroll-stopping reel",
    )
    messages = [{"role": "system", "content": system}]
    resp = chat(messages, model, temperature=0.9)
    return extract_json(resp)


# ── Text / script writer ──────────────────────────────────────────────────────

WRITER_SYSTEM = """You are a content writer for ZenPosture, an Indian D2C health brand.

BRAND KNOWLEDGE:
{brand}

MEMORY:
{memory}

Write {content_type} content for {platform}.
Product: {product_name}
Tone: {tone}
Brief: {brief}

Write directly — no preamble, no "here is your copy" — just the content itself.
Keep it authentic, relatable to Indian audience.
Price is always ₹499. Website: zenposture.in.
"""

def generate_text_content(product_key, content_type, platform, tone, brief, model, memory):
    prod = PRODUCTS_CATALOG.get(product_key, PRODUCTS_CATALOG["posture_corrector"])
    system = WRITER_SYSTEM.format(
        brand=BRAND_KNOWLEDGE,
        memory=memory.context_summary() or "None",
        content_type=content_type or "marketing copy",
        platform=platform or "Instagram",
        product_name=prod["name"],
        tone=tone or "relatable",
        brief=brief or "",
    )
    messages = [{"role": "system", "content": system}]
    return chat(messages, model, temperature=0.9)


# ── Marketing advisor ─────────────────────────────────────────────────────────

ADVISOR_SYSTEM = """You are a performance marketing expert for Indian D2C brands.

BRAND KNOWLEDGE:
{brand}

MEMORY:
{memory}

Give specific, actionable advice. Reference Indian market, Meta Ads, Instagram.
Keep responses concise — max 5 bullet points or 150 words.
"""

def get_marketing_advice(question, model, memory):
    system = ADVISOR_SYSTEM.format(
        brand=BRAND_KNOWLEDGE,
        memory=memory.context_summary() or "None",
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": question}
    ]
    return chat(messages, model, temperature=0.7)


# ── Reel renderer ─────────────────────────────────────────────────────────────

def render_reel(data, product_key, output, mood, model, memory):
    """Build video from AI script data. Self-heals on error."""
    sys.path.insert(0, _HERE)
    import reel_maker as rm

    prod    = PRODUCTS_CATALOG.get(product_key, PRODUCTS_CATALOG["posture_corrector"])
    img_key = prod["img"]
    images_dir = os.path.normpath(os.path.join(_HERE, "../../public/images"))

    def _build_clips(d):
        return [
            rm.scene_pattern_interrupt(
                d["hook"].get("line1", "STOP SCROLLING"),
                d["hook"].get("line2", ""),
                caption=d["hook"].get("caption", ""),
                duration=3.0
            ),
            rm.scene_pain(
                img_key,
                d["pain"].get("headline", "It hurts.\nEvery day."),
                d["pain"].get("sub", "Your body needs support."),
                images_dir,
                caption=d["pain"].get("caption", ""),
                duration=3.0, do_shake=True, tag="REAL TALK"
            ),
            rm.scene_comparison_wipe(
                images_dir,
                d["reveal"].get("headline", "ZenPosture\nFixes This."),
                d["reveal"].get("sub", "Effective. Breathable. Made for India."),
                caption=d["reveal"].get("caption", ""),
                duration=4.5
            ),
            rm.scene_happy_customers(
                images_dir,
                d["social"].get("headline", "⭐⭐⭐⭐⭐"),
                d["social"].get("sub", '"Amazing product."\n— Happy Customer'),
                caption=d["social"].get("caption", ""),
                duration=3.5, tag="REAL RESULTS"
            ),
            rm.scene_price_reveal(
                img_key, images_dir,
                caption=d["price"].get("caption", "₹499. Free shipping. COD available."),
                duration=3.0, tag=d["price"].get("tag", "LIMITED OFFER")
            ),
            rm.scene_cta(
                img_key, images_dir,
                d["cta"].get("headline", "Order today.\nzenposture.in"),
                caption=d["cta"].get("caption", "Free shipping · COD · 30-day returns"),
                duration=3.5
            ),
        ]

    for attempt in range(1, 4):
        try:
            clips = _build_clips(data)
            from moviepy.editor import concatenate_videoclips, AudioFileClip
            final = concatenate_videoclips(clips, method="compose")

            music = rm.get_music_path(mood=mood or prod["mood"])
            if music and os.path.exists(music):
                audio = AudioFileClip(music).volumex(0.26)
                if audio.duration < final.duration:
                    from moviepy.editor import concatenate_audioclips
                    loops = int(final.duration / audio.duration) + 2
                    audio = concatenate_audioclips([audio] * loops)
                audio = audio.subclip(0, final.duration).audio_fadeout(2.0)
                final = final.set_audio(audio)
            else:
                print(c("  ⚠️  No music downloaded — using generated beat", YELLOW))
                stereo, sr = rm.generate_music(final.duration + 0.5)
                from moviepy.audio.AudioClip import AudioArrayClip
                import numpy as np
                audio_clip = AudioArrayClip(stereo, fps=sr).audio_fadeout(2.0)
                audio_clip = audio_clip.subclip(0, final.duration)
                final = final.set_audio(audio_clip)

            final.write_videofile(
                output, fps=rm.FPS, codec="libx264", audio_codec="aac",
                temp_audiofile="temp_audio.m4a", remove_temp=True,
                preset="medium", ffmpeg_params=["-crf", "17", "-pix_fmt", "yuv420p"],
                logger=None,
            )
            return os.path.getsize(output) / 1024 / 1024

        except Exception as e:
            err_text = traceback.format_exc()
            if attempt >= 3:
                raise
            print(c(f"\n  ⚠️  Render error (attempt {attempt}/3): {e}", YELLOW))
            print(c("  🔧  Auto-fixing script with AI…", DIM))
            fix_msg = [
                {"role": "system", "content": (
                    "You are a JSON repair assistant. Fix this reel script JSON that caused a render error. "
                    "Keep all keys. Shorten any line that might overflow a 1080px canvas. "
                    "Return ONLY the corrected JSON object."
                )},
                {"role": "user", "content": (
                    f"Script:\n{json.dumps(data, indent=2)}\n\n"
                    f"Error:\n{err_text[:600]}\n\nReturn fixed JSON only."
                )}
            ]
            try:
                fixed_text = chat(fix_msg, model)
                fixed = extract_json(fixed_text)
                if fixed:
                    data = fixed
                    print(c("  ✅  Script auto-fixed. Retrying…\n", GREEN))
            except Exception:
                pass


# ── General chat ──────────────────────────────────────────────────────────────

CHAT_SYSTEM = """You are ZenBot, AI assistant for ZenPosture (Indian posture & recovery brand).
You help with: creating Reels, writing content, marketing advice, product questions.
Be friendly, concise (max 3-4 sentences), practical.

BRAND:
{brand}

MEMORY:
{memory}
"""

def general_chat(user_input, history, model, memory):
    system = CHAT_SYSTEM.format(
        brand=BRAND_KNOWLEDGE,
        memory=memory.context_summary() or "None"
    )
    messages = [{"role": "system", "content": system}] + history[-10:]
    messages.append({"role": "user", "content": user_input})
    return chat(messages, model, temperature=0.8)


# ── Main loop ─────────────────────────────────────────────────────────────────

def print_header(model, memory):
    print(f"\n{c(hr('═'), CYAN)}")
    print(c(f"  ZenPosture AI Command Center", BOLD + CYAN))
    print(c(f"  Your content pipeline — all in one chat", DIM))
    print(c(hr('─'), CYAN))
    print(f"  {c('Model', DIM)}   : {c(model, GREEN)}")
    print(f"  {c('Memory', DIM)}  : {c(str(memory.data.get('reel_count', 0)) + ' reels created', GREEN)}")
    print(f"  {c('Skills', DIM)}  : Reel Maker · Script Writer · Marketing Advisor · Product Expert")
    print(c(hr('═'), CYAN))
    print(f"\n  {c('What can I do for you? (type help for commands)', DIM)}\n")


def print_help():
    print(f"\n{c('  SKILLS', BOLD + CYAN)}")
    print(f"  {c('Reel Maker', GREEN)}")
    print(f"    • make a reel for new moms")
    print(f"    • create a gym reel, aggressive tone")
    print(f"    • office worker reel with calm music")
    print(f"    • regenerate with different vibe")
    print(f"\n  {c('Script / Content Writer', GREEN)}")
    print(f"    • write a UGC script for posture corrector")
    print(f"    • give me 5 Instagram captions for postpartum belt")
    print(f"    • write an email for gym customers")
    print(f"    • write 3 hooks for Facebook ad")
    print(f"\n  {c('Marketing Advisor', GREEN)}")
    print(f"    • what audience should I target for new moms?")
    print(f"    • give me Meta ad strategy for ₹499 product")
    print(f"    • what hooks work best for Indian women?")
    print(f"\n  {c('Memory', GREEN)}")
    print(f"    • remember: our tone is always relatable not medical")
    print(f"    • note: postpartum reel performed well last week")
    print(f"    • what do you remember?")
    print(f"\n  {c('Settings', GREEN)}")
    print(f"    • use model qwen2.5:14b")
    print(f"    • use model gemma4")
    print(f"    • quit / exit\n")


def main():
    ap = argparse.ArgumentParser(description="ZenPosture AI Command Center")
    ap.add_argument("--model",        default=None,        help="Ollama model name")
    ap.add_argument("--reset-memory", action="store_true", help="Clear all memory and start fresh")
    args = ap.parse_args()

    memory = Memory(_MEMORY)

    if args.reset_memory:
        if os.path.exists(_MEMORY):
            os.remove(_MEMORY)
        memory = Memory(_MEMORY)
        print(c("  ✅  Memory cleared.", GREEN))

    model = args.model or memory.data.get("model", DEFAULT_MODEL)

    if not ollama_available():
        print(c("\n  ❌  Ollama not running. Start it with: ollama serve\n", RED))
        sys.exit(1)

    print_header(model, memory)

    chat_history    = []
    last_product    = None
    last_output     = None
    last_script_data= None
    session_count   = 0

    while True:
        try:
            raw = input(f"{c('You', BOLD + CYAN)}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{c('  Goodbye! Total reels created: ' + str(memory.data.get('reel_count',0)), GREEN)}\n")
            break

        if not raw:
            continue

        lower = raw.lower()

        if lower in ("quit","exit","bye","q"):
            print(f"\n{c('  ZenBot: See you! ' + str(session_count) + ' tasks done this session.', GREEN)}\n")
            break

        if lower in ("help","?","commands"):
            print_help()
            continue

        # Quick recall shortcut
        if lower in ("recall","memory","what do you remember","what do you know"):
            ctx = memory.context_summary()
            print(f"\n{c('  ZenBot:', GREEN)} {ctx or 'Nothing stored yet. Tell me your preferences!'}\n")
            continue

        # Feedback shortcut "rate last reel X/5"
        rate_match = re.search(r'rate\s.*?(\d)[/ ]?5', lower)
        if rate_match and last_output:
            rating = int(rate_match.group(1))
            memory.add_feedback(last_output, rating, raw)
            print(f"\n{c('  ZenBot:', GREEN)} Got it — {rating}/5 noted for {last_output}. I'll use this to improve future reels.\n")
            continue

        print(f"{c('  ZenBot:', DIM)} {c('Thinking…', DIM)}", end="\r", flush=True)

        # ── Parse intent ──────────────────────────────────────────────────────
        try:
            intent = parse_intent(raw, model, memory)
        except Exception as e:
            print(f"\n{c('  ZenBot:', GREEN)} Sorry, Ollama timed out. Try again? ({e})\n")
            continue

        if not intent:
            intent = {"skill": "chat", "reply": ""}

        skill     = intent.get("skill", "chat")
        product   = intent.get("product") or last_product
        tone      = intent.get("tone")
        mood      = intent.get("mood")
        brief     = intent.get("brief", "")
        reply_msg = intent.get("reply", "")
        new_model = intent.get("model")

        # Model switch
        if new_model:
            model = new_model
            memory.data["model"] = model
            memory.save()
            print(f"\n{c('  ZenBot:', GREEN)} Switched to {c(model, BOLD)}. Ready!\n")
            continue

        # ── SKILL: help ───────────────────────────────────────────────────────
        if skill == "help":
            print_help()
            continue

        # ── SKILL: remember ───────────────────────────────────────────────────
        if skill == "remember":
            key   = intent.get("memory_key") or "note"
            value = intent.get("memory_value") or brief or raw
            memory.add_note(value)
            print(f"\n{c('  ZenBot:', GREEN)} Got it — I'll remember: \"{value}\"\n")
            continue

        # ── SKILL: recall ─────────────────────────────────────────────────────
        if skill == "recall":
            ctx = memory.context_summary()
            print(f"\n{c('  ZenBot:', GREEN)} Here's what I know:\n{c(ctx or 'Nothing stored yet.', DIM)}\n")
            continue

        # ── SKILL: product_info ───────────────────────────────────────────────
        if skill == "product_info":
            if reply_msg:
                print(f"\n{c('  ZenBot:', GREEN)} {reply_msg}")
            # Answer from brand knowledge
            try:
                prod_answer = general_chat(raw, chat_history, model, memory)
                print(f"\n{c('  ZenBot:', GREEN)} {prod_answer}\n")
                chat_history.append({"role": "user",      "content": raw})
                chat_history.append({"role": "assistant", "content": prod_answer})
            except Exception as e:
                print(f"\n{c('  ZenBot:', RED)} Error: {e}\n")
            continue

        # ── SKILL: marketing_advice ───────────────────────────────────────────
        if skill == "marketing_advice":
            if reply_msg:
                print(f"\n{c('  ZenBot:', GREEN)} {reply_msg}")
            print(f"{c('  Consulting marketing brain…', DIM)}", end="\r")
            try:
                advice = get_marketing_advice(raw, model, memory)
                print(f"\n{c('  ZenBot:', GREEN)} {advice}\n")
                chat_history.append({"role": "user",      "content": raw})
                chat_history.append({"role": "assistant", "content": advice})
                session_count += 1
            except Exception as e:
                print(f"\n{c('  ZenBot:', RED)} Error: {e}\n")
            continue

        # ── SKILL: write_script ───────────────────────────────────────────────
        if skill == "write_script":
            if reply_msg:
                print(f"\n{c('  ZenBot:', GREEN)} {reply_msg}")
            content_type = intent.get("content_type", "marketing copy")
            platform     = intent.get("platform", "Instagram")
            product_key  = product or "posture_corrector"
            print(f"{c('  Writing ' + content_type + '…', DIM)}", end="\r")
            try:
                content = generate_text_content(product_key, content_type, platform, tone, brief or raw, model, memory)
                print(f"\n{c('  ZenBot:', GREEN)}")
                print(c(hr('─'), DIM))
                print(content)
                print(c(hr('─'), DIM) + "\n")
                chat_history.append({"role": "user",      "content": raw})
                chat_history.append({"role": "assistant", "content": content})
                session_count += 1
                last_product = product_key
            except Exception as e:
                print(f"\n{c('  ZenBot:', RED)} Error: {e}\n")
            continue

        # ── SKILL: make_reel ──────────────────────────────────────────────────
        if skill in ("make_reel", "regenerate"):
            product_key = product or "posture_corrector"
            if not product and not last_product:
                print(f"\n{c('  ZenBot:', GREEN)} Which product? postpartum belt / posture corrector / gym belt?\n")
                continue

            session_count += 1
            output = intent.get("output_file") or f"reel_{product_key}_{session_count:02d}.mp4"

            print(f"\n{c('  ZenBot:', GREEN)} {reply_msg or 'On it!'}")
            print(f"{c('  Product', DIM)} : {PRODUCTS_CATALOG.get(product_key, {}).get('name','')}")
            print(f"{c('  Mood', DIM)}    : {mood or PRODUCTS_CATALOG.get(product_key, {}).get('mood','motivational')}")
            print(f"{c('  Output', DIM)}  : {output}\n")

            # Generate AI script
            print(f"{c('  ✍️  Writing viral script with AI…', DIM)}", end="\r")
            try:
                script_data = generate_script(product_key, tone, mood, brief or raw, model, memory)
                if not script_data:
                    raise ValueError("No JSON returned from model")
                hook_preview = script_data.get("hook", {}).get("line1", "")[:50].replace("\n"," / ")
                print(f"{c('  ✅  Script ready', GREEN)}  Hook: {c(hook_preview, DIM)}")
            except Exception as e:
                print(f"{c('  ⚠️  AI script failed. Using built-in script.', YELLOW)}")
                script_data = None

            if script_data:
                # Render with self-healing
                print(f"{c('  🎬  Rendering…', DIM)}")
                try:
                    mb = render_reel(script_data, product_key, output,
                                     mood or PRODUCTS_CATALOG[product_key]["mood"],
                                     model, memory)
                    memory.add_success(script_data, product_key, output)
                    last_product    = product_key
                    last_output     = output
                    last_script_data= script_data

                    print(f"\n{c(hr(), GREEN)}")
                    print(f"{c('  ✅  DONE!', BOLD + GREEN)}  {output}  ({mb:.1f} MB)")
                    print(f"  {c('1080×1920', DIM)} — Instagram / Facebook Reels ready")
                    print(f"  {c('Next: rate it (e.g. \"rate last reel 4/5\") or say \"regenerate\"', DIM)}")
                    print(c(hr(), GREEN) + "\n")
                except Exception as e:
                    print(f"\n{c('  ❌  Render failed: ' + str(e), RED)}\n")
            else:
                # Fall back to built-in
                try:
                    sys.path.insert(0, _HERE)
                    import reel_maker as rm
                    images_dir = os.path.normpath(os.path.join(_HERE, "../../public/images"))
                    script_map = {
                        "posture_corrector": "office_worker",
                        "postpartum_belt":   "new_mom",
                        "compression_belt":  "pain_hook",
                    }
                    rm.build(script_map.get(product_key, "office_worker"),
                             output, images_dir,
                             mood=mood or PRODUCTS_CATALOG[product_key]["mood"])
                    last_output  = output
                    last_product = product_key
                    print(f"\n{c('  ✅  Done (built-in script): ' + output, GREEN)}\n")
                except Exception as e2:
                    print(f"{c('  ❌  All methods failed: ' + str(e2), RED)}\n")
            continue

        # ── SKILL: chat (fallback) ────────────────────────────────────────────
        try:
            response = general_chat(raw, chat_history, model, memory)
            print(f"\n{c('  ZenBot:', GREEN)} {response}\n")
            chat_history.append({"role": "user",      "content": raw})
            chat_history.append({"role": "assistant", "content": response})
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]
        except Exception as e:
            print(f"\n{c('  ZenBot:', RED)} Ollama error: {e}\n")


if __name__ == "__main__":
    main()
