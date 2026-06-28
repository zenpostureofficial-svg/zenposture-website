#!/usr/bin/env python3
"""
ZenPosture AI Agent
===================
Your digital employee. Controls your computer, manages your business,
creates content, runs ads, writes code, searches the web, and learns.

Usage:
  python agent.py
  python agent.py --model qwen2.5:14b
  python agent.py --headless          # Browser runs in background
  python agent.py --reset-memory
"""

import os, sys, json, re, time, datetime, traceback, logging, argparse
import urllib.request

_HERE   = os.path.dirname(os.path.abspath(__file__))
_MEMORY = os.path.join(_HERE, "memory", "memory.json")
_LOG    = os.path.join(_HERE, "logs",   "actions.log")
_CFG    = os.path.join(_HERE, "config", "settings.json")
_CREDS  = os.path.join(_HERE, "config", "credentials.json")

os.makedirs(os.path.join(_HERE, "memory"), exist_ok=True)
os.makedirs(os.path.join(_HERE, "logs"),   exist_ok=True)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=_LOG, level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
def log(msg): logging.info(msg)

# ── Terminal colors ───────────────────────────────────────────────────────────
CYAN="\033[96m"; GREEN="\033[92m"; YELLOW="\033[93m"
RED="\033[91m";  BOLD="\033[1m";   RESET="\033[0m"
DIM="\033[2m";   MAGENTA="\033[95m"; WHITE="\033[97m"
def c(t, col): return f"{col}{t}{RESET}"
def hr(ch="━", w=60): return ch * w


# ── Config & Credentials ──────────────────────────────────────────────────────
def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except Exception: pass
    return default or {}

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

CFG   = load_json(_CFG)
CREDS = load_json(_CREDS)
BRAND = CFG.get("brand", {})

OLLAMA_CHAT  = CFG.get("ollama_url", "http://localhost:11434") + "/api/chat"
DEFAULT_MODEL = CFG.get("default_model", "gemma4")


# ── Persistent Memory ─────────────────────────────────────────────────────────
class Memory:
    def __init__(self):
        self.path = _MEMORY
        self.data = load_json(_MEMORY, {
            "preferences": {}, "notes": [], "sessions": [],
            "successful_tasks": [], "failed_tasks": [],
            "learned_facts": [], "model": DEFAULT_MODEL,
            "task_count": 0
        })

    def save(self): save_json(self.path, self.data)

    def note(self, text):
        self.data["notes"].append({"text": text, "ts": _now()})
        self.save()

    def learn(self, fact):
        self.data["learned_facts"].append({"fact": fact, "ts": _now()})
        self.save()

    def success(self, task, result=""):
        self.data["successful_tasks"].append({"task": task[:100], "result": result[:100], "ts": _now()})
        self.data["task_count"] = self.data.get("task_count", 0) + 1
        self.save()

    def fail(self, task, error=""):
        self.data["failed_tasks"].append({"task": task[:100], "error": error[:200], "ts": _now()})
        self.save()

    def set(self, key, val):
        self.data["preferences"][key] = val
        self.save()

    def get(self, key, default=None):
        return self.data["preferences"].get(key, default)

    def summary(self):
        parts = []
        prefs = self.data.get("preferences", {})
        notes = self.data.get("notes", [])[-5:]
        facts = self.data.get("learned_facts", [])[-5:]
        wins  = self.data.get("successful_tasks", [])[-3:]
        if prefs: parts.append("PREFERENCES: " + json.dumps(prefs))
        if notes: parts.append("NOTES: " + " | ".join(n["text"] for n in notes))
        if facts: parts.append("LEARNED: " + " | ".join(f["fact"] for f in facts))
        if wins:  parts.append("RECENT WINS: " + " | ".join(w["task"] for w in wins))
        return "\n".join(parts)

    def reset(self):
        if os.path.exists(self.path): os.remove(self.path)
        self.__init__()


def _now(): return datetime.datetime.now().isoformat(timespec="seconds")


# ── Ollama ────────────────────────────────────────────────────────────────────
def ollama_chat(messages, model, temperature=0.7, timeout=120):
    payload = json.dumps({
        "model": model, "messages": messages,
        "stream": False, "options": {"temperature": temperature}
    }).encode()
    req = urllib.request.Request(
        OLLAMA_CHAT, data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["message"]["content"].strip()

def ollama_ok():
    try:
        urllib.request.urlopen(
            CFG.get("ollama_url", "http://localhost:11434"), timeout=3)
        return True
    except: return False

def extract_json(text):
    text = text.strip()
    if "```" in text:
        for part in text.split("```"):
            p = part.strip().lstrip("json").strip()
            if p.startswith("{"): text = p; break
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try: return json.loads(m.group())
        except: pass
    return None


# ── Permission Gate ───────────────────────────────────────────────────────────
def ask_permission(action, detail="", default_yes=False):
    suffix = " [Y/n]" if default_yes else " [y/N]"
    print(f"\n{c('  ⚡ ZenBot wants to:', BOLD+YELLOW)} {action}")
    if detail: print(f"  {c('Detail:', DIM)} {detail}")
    try:
        ans = input(f"  Allow?{suffix}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(); return False
    allowed = (ans not in ("n","no")) if default_yes else (ans in ("y","yes"))
    log(f"PERMISSION: {'ALLOWED' if allowed else 'DENIED'} — {action}")
    return allowed


# ── Intent Router ─────────────────────────────────────────────────────────────
INTENT_SYSTEM = """You are ZenBot, AI agent for ZenPosture (India, zenposture.in).
Parse the user's request and return ONLY a JSON object:
{
  "skill": one of [
    "make_reel", "post_social", "shopify", "meta_ads", "google_ads",
    "seo_write", "code", "browse", "computer", "web_search",
    "youtube", "marketing_advice", "remember", "recall", "chat", "help"
  ],
  "product": "posture_corrector"|"postpartum_belt"|"compression_belt"|null,
  "platform": "instagram"|"facebook"|"youtube"|"google"|null,
  "action": short description of what specifically to do,
  "target": specific item/url/file to act on (if any),
  "brief": any creative direction or extra context,
  "model": new model name if user wants to switch|null,
  "reply": one friendly sentence acknowledging the request
}

Mapping rules:
- new mom/postpartum/baby → postpartum_belt
- posture/desk/office/back pain → posture_corrector
- gym/fitness/lifting/belt → compression_belt
- "post reel/video" → post_social
- "check ads/performance/boost/pause" → meta_ads or google_ads
- "add/delete/update product" → shopify
- "write code/script/automation" → code
- "open browser/go to website/click" → browse
- "control pc/mouse/keyboard" → computer
- "search/find/look up" → web_search
- "SEO/metadata/blog/caption/ad copy" → seo_write
- "remember/note/save" → remember
- "what do you know/recall/memory" → recall
"""


def parse_intent(user_input, model, memory):
    mem = memory.summary()
    sys_prompt = INTENT_SYSTEM
    if mem: sys_prompt += f"\n\nMEMORY:\n{mem}"
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user",   "content": user_input}
    ]
    try:
        resp = ollama_chat(messages, model, temperature=0.2, timeout=60)
        return extract_json(resp) or {"skill": "chat", "reply": ""}
    except Exception as e:
        return {"skill": "chat", "reply": f"(parse error: {e})"}


# ── Skill Dispatcher ──────────────────────────────────────────────────────────

def skill_make_reel(intent, model, memory):
    """Generate Instagram/Facebook reel."""
    product = intent.get("product") or "posture_corrector"
    brief   = intent.get("brief", "")
    sys.path.insert(0, os.path.join(_HERE, "..", "tools", "reel-maker"))
    try:
        import reel_chat as rc
        import reel_maker as rm
        script = rc.generate_script(product, None, None, brief, model, memory_obj_compat(memory))
        if not script:
            return "Could not generate reel script."
        output = f"reel_{product}_{int(time.time())}.mp4"
        images_dir = os.path.normpath(os.path.join(_HERE, "..", "public", "images"))
        if not ask_permission(f"Render reel → {output}", f"Product: {product}", default_yes=True):
            return "Reel cancelled."
        mb = rc.render_reel(script, product, output,
                            rc.PRODUCTS_CATALOG.get(product, {}).get("mood", "motivational"),
                            model, memory_obj_compat(memory))
        memory.success(f"reel:{product}", output)
        log(f"REEL: rendered {output} ({mb:.1f}MB)")
        return f"✅ Reel ready: {output} ({mb:.1f} MB)"
    except Exception as e:
        memory.fail(f"reel:{product}", str(e))
        return f"Reel failed: {e}"


def skill_web_search(intent, model, memory):
    """Search web and summarize."""
    query = intent.get("action") or intent.get("brief") or "ZenPosture India"
    sys.path.insert(0, _HERE)
    from skills.web_search import search_and_summarize
    print(f"  {c('Searching:', DIM)} {query}")
    summary, sources = search_and_summarize(query, ollama_chat, model)
    if sources:
        memory.learn(f"Searched: {query[:60]} → {summary[:80]}")
    log(f"SEARCH: {query}")
    result = summary
    if sources:
        result += f"\n\n{c('Sources:', DIM)}\n" + "\n".join(f"  • {s}" for s in sources[:3])
    return result


def skill_shopify(intent, model, memory):
    """Manage Shopify store."""
    creds = CREDS.get("shopify", {})
    if not creds.get("access_token") or not creds.get("shop_url"):
        return ("Shopify credentials not configured.\n"
                "Edit zenposture_ai_agent/config/credentials.json → shopify section.")
    from skills.shopify_manager import ShopifyManager
    sm = ShopifyManager(creds["shop_url"], creds["access_token"])
    action = (intent.get("action") or "").lower()

    if "summary" in action or "status" in action or not action:
        return sm.store_summary()

    if "list" in action and "product" in action:
        products, err = sm.list_products(limit=20)
        if err: return f"Error: {err}"
        return "\n".join(f"  • {p['title']} — ₹{p['variants'][0]['price']} (ID:{p['id']})"
                         for p in products)

    if "order" in action:
        orders, err = sm.list_orders(status="open")
        if err: return f"Error: {err}"
        return "\n".join(f"  #{o['order_number']} — ₹{o['total_price']} — {o['financial_status']}"
                         for o in orders)

    return f"Shopify action '{action}' — please be more specific."


def skill_meta_ads(intent, model, memory):
    """Manage Meta ads."""
    creds = CREDS.get("meta", {})
    if not creds.get("access_token"):
        return ("Meta credentials not configured.\n"
                "Edit zenposture_ai_agent/config/credentials.json → meta section.")
    from skills.meta_manager import MetaManager
    mm = MetaManager(
        creds["access_token"], creds["page_id"],
        creds["instagram_account_id"], creds["ad_account_id"]
    )
    action = (intent.get("action") or "").lower()

    if "performance" in action or "check" in action or "summary" in action or not action:
        return mm.campaigns_summary()

    if "boost" in action or "increase" in action:
        brief = intent.get("brief", "")
        campaigns, _ = mm.get_all_campaigns_performance()
        if not campaigns: return "No campaigns found."
        # Find best by CTR
        best = max(campaigns, key=lambda c: float(c.get("insights",{}).get("ctr",0)))
        amount = 200  # default ₹200 boost
        if not ask_permission(
            f"Boost campaign '{best['name']}'",
            f"Increase daily budget by ₹{amount}",
            default_yes=False
        ): return "Boost cancelled."
        ok, err = mm.set_campaign_budget(best["id"], amount)
        if err: return f"Error: {err}"
        memory.success(f"meta_boost:{best['name']}", f"+₹{amount}/day")
        return f"✅ Boosted '{best['name']}' by ₹{amount}/day"

    if "pause" in action or "stop" in action:
        campaigns, _ = mm.get_all_campaigns_performance()
        if not campaigns: return "No campaigns found."
        # Find worst by CTR
        worst = min(campaigns, key=lambda c: float(c.get("insights",{}).get("ctr",99)))
        if not ask_permission(
            f"Pause campaign '{worst['name']}'",
            f"CTR: {worst.get('insights',{}).get('ctr','?')}%",
            default_yes=False
        ): return "Pause cancelled."
        ok, err = mm.set_campaign_status(worst["id"], "PAUSED")
        if err: return f"Error: {err}"
        memory.success(f"meta_pause:{worst['name']}")
        return f"✅ Paused '{worst['name']}'"

    return f"Meta Ads action '{action}' — please be more specific (check/boost/pause)."


def skill_seo_write(intent, model, memory):
    """SEO writing."""
    from skills.seo_writer import generate_product_seo, generate_blog_post, generate_captions, generate_ad_copy
    action  = (intent.get("action") or "").lower()
    product = intent.get("product") or "posture corrector"
    brief   = intent.get("brief", "")
    platform= intent.get("platform") or "instagram"

    if "blog" in action:
        topic = brief or f"Best posture corrector for {product} in India"
        return generate_blog_post(topic, [product, "ZenPosture", "India"],
                                  ollama_chat_fn=ollama_chat, model=model)
    if "caption" in action or "social" in action:
        return generate_captions(product, 5, platform, "relatable", ollama_chat, model)
    if "ad copy" in action or "ad" in action:
        return generate_ad_copy(product, platform, "emotional", brief, ollama_chat, model)
    # Default: full SEO package
    return generate_product_seo(product, brief,
                                [product, "ZenPosture", "India", "₹499"],
                                ollama_chat, model)


def skill_code(intent, model, memory):
    """Write and run code."""
    from skills.coder import write_and_run
    task = intent.get("action") or intent.get("brief") or "unknown task"
    output, code, success = write_and_run(task, ollama_chat, model, ask_permission)
    if success:
        memory.success(f"code:{task[:60]}", output[:100])
    else:
        memory.fail(f"code:{task[:60]}", output[:100])
    log(f"CODE: {'OK' if success else 'FAIL'} — {task[:60]}")
    return output


def skill_browse(intent, model, memory):
    """Control browser."""
    from skills.browser_control import BrowserControl
    target = intent.get("target") or intent.get("brief") or ""
    action = (intent.get("action") or "").lower()

    if not ask_permission(f"Open browser: {action}", target, default_yes=True):
        return "Browser action cancelled."

    bc = BrowserControl(headless=CFG.get("headless", False))
    try:
        bc.start()
        if target.startswith("http"):
            title = bc.go(target)
            bc.wait(2000)
            text = bc.get_page_text()
            bc.stop()
            return f"Opened: {title}\n\n{text[:1000]}"
        elif "search" in action or "google" in action:
            text = bc.google_search(target or intent.get("brief",""))
            bc.stop()
            return text[:2000]
        else:
            bc.stop()
            return f"Browser opened. Specify URL or action."
    except Exception as e:
        try: bc.stop()
        except: pass
        return f"Browser error: {e}"


def skill_marketing_advice(intent, model, memory):
    """Marketing advice."""
    question = intent.get("brief") or intent.get("action") or "general marketing advice"
    mem_ctx  = memory.summary()
    messages = [
        {"role": "system", "content": (
            "You are a top D2C marketing strategist for Indian e-commerce brands. "
            "ZenPosture sells posture/recovery products at ₹499 on zenposture.in. "
            f"MEMORY:\n{mem_ctx}"
        )},
        {"role": "user", "content": question}
    ]
    return ollama_chat(messages, model, temperature=0.7)


def skill_post_social(intent, model, memory):
    """Post to Instagram/Facebook."""
    platform = intent.get("platform", "instagram")
    creds    = CREDS.get("meta", {})
    if not creds.get("access_token"):
        return "Meta credentials not configured. Edit config/credentials.json."

    content = intent.get("brief") or ""
    video_url = intent.get("target") or ""

    if not ask_permission(
        f"Post to {platform.capitalize()}",
        f"Content: {content[:60]}",
        default_yes=False
    ):
        return "Post cancelled."

    from skills.meta_manager import MetaManager
    mm = MetaManager(creds["access_token"], creds["page_id"],
                     creds["instagram_account_id"], creds["ad_account_id"])
    if video_url and platform == "instagram":
        post_id, err = mm.post_instagram_reel(video_url, content)
    else:
        post_id, err = mm.post_facebook(content)
    if err:
        return f"Post failed: {err}"
    memory.success(f"post:{platform}", post_id or "ok")
    log(f"POST: {platform} — {content[:40]}")
    return f"✅ Posted to {platform}! Post ID: {post_id}"


def memory_obj_compat(memory):
    """Adapter so reel_chat functions accept our Memory object."""
    class _Compat:
        def __init__(self, m): self._m = m
        def context_summary(self): return self._m.summary()
        def add_success(self, s, p, o): self._m.success(f"reel:{p}", o)
        def add_note(self, n): self._m.note(n)
        data = property(lambda self: self._m.data)
    return _Compat(memory)


# ── General Chat ──────────────────────────────────────────────────────────────
def general_chat(user_input, history, model, memory):
    mem_ctx = memory.summary()
    system  = (
        f"You are ZenBot, the AI digital employee of ZenPosture (India, zenposture.in). "
        f"You are helpful, confident, and business-savvy. You manage their entire digital presence.\n"
        f"BRAND: {json.dumps(BRAND)}\n"
        + (f"MEMORY:\n{mem_ctx}" if mem_ctx else "")
    )
    messages = [{"role": "system", "content": system}] + history[-10:] + \
               [{"role": "user", "content": user_input}]
    return ollama_chat(messages, model, temperature=0.75)


# ── Help ──────────────────────────────────────────────────────────────────────
def print_help():
    sections = [
        ("Content Creation", [
            "make a reel for new moms",
            "make a gym reel with aggressive tone",
            "write 5 Instagram captions for posture corrector",
            "write blog post about posture for office workers",
            "write Meta ad copy for postpartum belt",
        ]),
        ("Social Media", [
            "post this reel to Instagram: [url]",
            "post to Facebook: [message]",
            "check Instagram performance",
        ]),
        ("Ads Management", [
            "check Meta ad performance",
            "boost the best performing ad by ₹200",
            "pause the worst performing ad",
            "check Google Ads performance",
        ]),
        ("Shopify Store", [
            "show my store products",
            "show open orders",
            "add new product: [name] ₹499",
            "update price of product [ID] to ₹599",
        ]),
        ("Web & Research", [
            "search: best posture corrector in India",
            "open zenposture.in and check for errors",
            "find top Instagram hooks for new moms",
        ]),
        ("SEO & Content", [
            "write SEO package for posture corrector",
            "write blog post about back pain for office workers",
            "generate captions for postpartum belt",
        ]),
        ("Coding & Automation", [
            "write a Python script to resize all images in a folder",
            "write automation to backup my Shopify products to CSV",
        ]),
        ("Memory", [
            "remember: our tone is always relatable, never medical",
            "note: postpartum reel got 100k views",
            "what do you remember?",
        ]),
        ("Settings", [
            "use model qwen2.5:14b",
            "use model llama3.1:8b",
            "quit / exit",
        ]),
    ]
    print(f"\n{c(hr('═'), CYAN)}")
    print(f"{c('  ZenBot — All Commands', BOLD+CYAN)}")
    print(c(hr('─'), CYAN))
    for section, cmds in sections:
        print(f"\n  {c(section, BOLD+GREEN)}")
        for cmd in cmds:
            print(f"    {c('•', CYAN)} {cmd}")
    print(f"\n{c(hr('═'), CYAN)}\n")


# ── Header ────────────────────────────────────────────────────────────────────
def print_header(model, memory):
    tasks = memory.data.get("task_count", 0)
    print(f"\n{c(hr('═'), CYAN)}")
    print(f"  {c('ZenPosture AI Agent', BOLD+CYAN)}")
    print(f"  {c('Your digital employee — full business control', DIM)}")
    print(c(hr('─'), CYAN))
    print(f"  {c('Model', DIM)}  : {c(model, GREEN)}")
    print(f"  {c('Memory', DIM)} : {c(str(tasks) + ' tasks completed', GREEN)}")
    print(f"  {c('Skills', DIM)} : Reels · Shopify · Meta Ads · SEO · Code · Browser · Web Search")
    print(c(hr('═'), CYAN))
    print(f"\n  {c('What should I do for you today? (type help for all commands)', DIM)}\n")


# ── Main Loop ─────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="ZenPosture AI Agent")
    ap.add_argument("--model",        default=None)
    ap.add_argument("--headless",     action="store_true", help="Run browser in background")
    ap.add_argument("--reset-memory", action="store_true")
    args = ap.parse_args()

    if args.headless:
        CFG["headless"] = True

    memory = Memory()
    if args.reset_memory:
        memory.reset()
        print(c("  ✅  Memory cleared.", GREEN))

    model = args.model or memory.data.get("model", DEFAULT_MODEL)

    if not ollama_ok():
        print(c("\n  ❌  Ollama not running. Start with: ollama serve\n", RED))
        sys.exit(1)

    print_header(model, memory)

    chat_history = []
    last_output  = None
    session_tasks = 0

    SKILL_MAP = {
        "make_reel":        skill_make_reel,
        "post_social":      skill_post_social,
        "shopify":          skill_shopify,
        "meta_ads":         skill_meta_ads,
        "seo_write":        skill_seo_write,
        "code":             skill_code,
        "browse":           skill_browse,
        "web_search":       skill_web_search,
        "marketing_advice": skill_marketing_advice,
    }

    while True:
        try:
            raw = input(f"\n{c('You', BOLD+CYAN)}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{c(f'  ZenBot: Session ended. {session_tasks} tasks done.', GREEN)}\n")
            break

        if not raw: continue
        lower = raw.lower()

        if lower in ("quit","exit","bye","q"):
            print(f"\n{c(f'  ZenBot: Goodbye! {session_tasks} tasks done this session.', GREEN)}\n")
            break

        if lower in ("help","?","commands","h"):
            print_help(); continue

        if lower in ("memory","recall","what do you know","what do you remember"):
            ctx = memory.summary()
            print(f"\n{c('  ZenBot:', GREEN)} {ctx or 'Nothing stored yet.'}\n"); continue

        # Feedback: "rate last task 4/5"
        rate_m = re.search(r'rate.*?(\d)[/\s]?5', lower)
        if rate_m and last_output:
            rating = int(rate_m.group(1))
            memory.note(f"Rating {rating}/5 for: {last_output}")
            print(f"\n{c('  ZenBot:', GREEN)} Got it — {rating}/5 saved. I'll learn from this.\n")
            continue

        print(f"{c('  ZenBot:', DIM)} {c('Thinking…', DIM)}", end="\r", flush=True)
        log(f"USER: {raw}")

        try:
            intent = parse_intent(raw, model, memory)
        except Exception as e:
            print(f"\n{c('  ZenBot:', GREEN)} Sorry, parse error: {e}\n"); continue

        skill     = intent.get("skill", "chat")
        reply_msg = intent.get("reply", "")
        new_model = intent.get("model")

        # Model switch
        if new_model:
            model = new_model
            memory.data["model"] = model
            memory.save()
            print(f"\n{c('  ZenBot:', GREEN)} Switched to {c(model, BOLD)}. Ready!\n"); continue

        if skill == "help":
            print_help(); continue

        if skill == "remember":
            val = intent.get("brief") or raw
            memory.note(val)
            print(f"\n{c('  ZenBot:', GREEN)} Remembered: \"{val}\"\n"); continue

        if skill == "recall":
            ctx = memory.summary()
            print(f"\n{c('  ZenBot:', GREEN)}\n{ctx or 'Nothing yet.'}\n"); continue

        if reply_msg:
            print(f"\n{c('  ZenBot:', GREEN)} {reply_msg}")

        # Dispatch to skill
        if skill in SKILL_MAP:
            print(f"  {c('Working on it…', DIM)}", end="\r", flush=True)
            try:
                result = SKILL_MAP[skill](intent, model, memory)
                print(f"\n{c('  ZenBot:', GREEN)}")
                print(c(hr('─'), DIM))
                print(result)
                print(c(hr('─'), DIM))
                last_output = result[:80]
                session_tasks += 1
                chat_history.append({"role": "user",      "content": raw})
                chat_history.append({"role": "assistant",  "content": result[:500]})
                log(f"SKILL:{skill} — OK")
            except Exception as e:
                tb = traceback.format_exc()
                print(f"\n{c('  ZenBot:', RED)} Error in {skill}: {e}")
                memory.fail(f"{skill}:{raw[:60]}", str(e))
                log(f"SKILL:{skill} — ERROR: {e}\n{tb}")
        else:
            # General chat
            try:
                resp = general_chat(raw, chat_history, model, memory)
                print(f"\n{c('  ZenBot:', GREEN)} {resp}")
                chat_history.append({"role": "user",      "content": raw})
                chat_history.append({"role": "assistant",  "content": resp})
                if len(chat_history) > 20:
                    chat_history = chat_history[-20:]
                log(f"CHAT: {raw[:60]}")
            except Exception as e:
                print(f"\n{c('  ZenBot:', RED)} Ollama error: {e}")


if __name__ == "__main__":
    main()
