"""
Browser Control Skill
Uses Playwright to control Chrome — can navigate, click, type, screenshot.
Falls back to webbrowser module if Playwright not installed.
"""

import os, sys, time, base64

_playwright_available = False
try:
    from playwright.sync_api import sync_playwright
    _playwright_available = True
except ImportError:
    pass


class BrowserControl:
    def __init__(self, headless=False, downloads_dir=None):
        self.headless     = headless
        self.downloads_dir = downloads_dir or os.path.expanduser("~/Downloads/ZenBot")
        os.makedirs(self.downloads_dir, exist_ok=True)
        self._pw   = None
        self._browser = None
        self._page    = None

    def start(self):
        if not _playwright_available:
            raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install chromium")
        self._pw      = sync_playwright().__enter__()
        self._browser = self._pw.chromium.launch(headless=self.headless, slow_mo=50)
        ctx           = self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            downloads_path=self.downloads_dir
        )
        self._page = ctx.new_page()
        return self

    def stop(self):
        if self._browser: self._browser.close()
        if self._pw:      self._pw.__exit__(None, None, None)

    def go(self, url):
        self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return self._page.title()

    def click(self, selector_or_text, by_text=False):
        if by_text:
            self._page.get_by_text(selector_or_text).first.click()
        else:
            self._page.click(selector_or_text)

    def type_into(self, selector, text, clear_first=True):
        el = self._page.locator(selector).first
        if clear_first:
            el.triple_click()
        el.type(text, delay=40)

    def screenshot(self, path=None):
        path = path or os.path.join(self.downloads_dir, f"screenshot_{int(time.time())}.png")
        self._page.screenshot(path=path)
        return path

    def screenshot_b64(self):
        return base64.b64encode(self._page.screenshot()).decode()

    def get_text(self, selector="body"):
        return self._page.locator(selector).inner_text()

    def get_page_text(self):
        return self._page.evaluate("document.body.innerText")[:5000]

    def wait(self, ms=1000):
        self._page.wait_for_timeout(ms)

    def fill_form(self, fields: dict):
        """fields: {selector: value}"""
        for selector, value in fields.items():
            self.type_into(selector, value)

    def press(self, key):
        self._page.keyboard.press(key)

    def scroll_down(self, amount=500):
        self._page.evaluate(f"window.scrollBy(0, {amount})")

    def find_text_on_page(self, text):
        return text.lower() in self._page.content().lower()

    # ── High-level helpers ────────────────────────────────────────────────────

    def google_search(self, query):
        import urllib.parse
        self.go(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
        self.wait(1500)
        return self.get_page_text()

    def open_url_and_read(self, url):
        self.go(url)
        self.wait(2000)
        return self.get_page_text()
