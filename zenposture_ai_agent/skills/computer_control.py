"""
Computer Control Skill
Mouse, keyboard, clipboard, screenshots via pyautogui.
ALWAYS asks permission before executing actions.
"""

import os, sys, time, subprocess

_pyautogui_available = False
try:
    import pyautogui
    pyautogui.FAILSAFE = True   # Move mouse to top-left corner to abort
    pyautogui.PAUSE    = 0.3    # Small pause between actions (safety)
    _pyautogui_available = True
except ImportError:
    pass


def _require():
    if not _pyautogui_available:
        raise RuntimeError("pyautogui not installed. Run: pip install pyautogui pillow")


class ComputerControl:

    def screenshot(self, path=None):
        _require()
        path = path or os.path.join(os.path.expanduser("~"), "zenbot_screenshot.png")
        pyautogui.screenshot(path)
        return path

    def click(self, x, y, button="left"):
        _require()
        pyautogui.click(x, y, button=button)

    def double_click(self, x, y):
        _require()
        pyautogui.doubleClick(x, y)

    def move_to(self, x, y):
        _require()
        pyautogui.moveTo(x, y, duration=0.3)

    def type_text(self, text, interval=0.05):
        _require()
        pyautogui.typewrite(text, interval=interval)

    def hotkey(self, *keys):
        _require()
        pyautogui.hotkey(*keys)

    def press(self, key):
        _require()
        pyautogui.press(key)

    def copy_to_clipboard(self, text):
        """Put text in clipboard."""
        _require()
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.after(100, root.destroy)
        root.mainloop()

    def get_clipboard(self):
        _require()
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            return root.clipboard_get()
        except Exception:
            return ""
        finally:
            root.destroy()

    def open_app(self, app_name):
        """Open an application by name (Windows)."""
        subprocess.Popen(["start", app_name], shell=True)
        time.sleep(1.5)

    def find_and_click(self, image_path, confidence=0.8):
        """Find an image on screen and click it (template matching)."""
        _require()
        try:
            loc = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if loc:
                pyautogui.click(loc)
                return True
        except Exception:
            pass
        return False

    def scroll(self, clicks=3, direction="down"):
        _require()
        amount = -clicks if direction == "down" else clicks
        pyautogui.scroll(amount)

    def drag(self, x1, y1, x2, y2):
        _require()
        pyautogui.drag(x1-pyautogui.position()[0], y1-pyautogui.position()[1], duration=0.5)
        pyautogui.drag(x2-x1, y2-y1, duration=0.5)

    def get_screen_size(self):
        _require()
        return pyautogui.size()

    def emergency_stop(self):
        """Move mouse to top-left to trigger failsafe."""
        if _pyautogui_available:
            pyautogui.moveTo(0, 0)
