"""
Coder Skill
Writes Python/shell code using Ollama (qwen2.5-coder or deepseek-r1),
then executes it after user permission.
"""

import os, sys, subprocess, tempfile, re


CODER_SYSTEM = """You are an expert Python programmer assistant for ZenPosture, an Indian e-commerce brand.
When asked to write code:
1. Write clean, working Python 3.11+ code
2. Add minimal comments only where logic is non-obvious
3. Return ONLY the code block, no explanation before or after
4. Use only standard library unless the task truly needs a third-party package
5. If you need a third-party package, add a pip install comment at the top

For file/system operations: always use safe paths, never delete without confirmation.
"""


def extract_code(text):
    """Pull code block out of markdown response."""
    text = text.strip()
    # ```python ... ```
    m = re.search(r'```(?:python|py|bash|shell|sh)?\n([\s\S]*?)```', text)
    if m:
        return m.group(1).strip()
    # If no fences, treat whole thing as code if it looks like it
    if text.startswith("import ") or text.startswith("def ") or text.startswith("#"):
        return text
    return text


def write_code(task_description, ollama_chat_fn, model, context=""):
    """Ask Ollama to write code for a task. Returns (code_str, None) or (None, error)."""
    messages = [
        {"role": "system", "content": CODER_SYSTEM},
        {"role": "user",   "content": f"Task: {task_description}\n\n{context}"}
    ]
    try:
        response = ollama_chat_fn(messages, model, temperature=0.2)
        code = extract_code(response)
        return code, None
    except Exception as e:
        return None, str(e)


def run_code(code, timeout=60):
    """
    Execute Python code in a subprocess.
    Returns (stdout, stderr, return_code).
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                     delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Code timed out after {timeout}s", 1
    except Exception as e:
        return "", str(e), 1
    finally:
        try: os.unlink(tmp_path)
        except: pass


def run_shell(command, timeout=30):
    """Run a shell command. Returns (stdout, stderr, return_code)."""
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=timeout
    )
    return result.stdout, result.stderr, result.returncode


def fix_code(code, error, ollama_chat_fn, model):
    """Ask Ollama to fix broken code given the error message."""
    messages = [
        {"role": "system", "content": CODER_SYSTEM},
        {"role": "user",   "content": (
            f"This Python code has an error. Fix it and return ONLY the corrected code:\n\n"
            f"CODE:\n```python\n{code}\n```\n\n"
            f"ERROR:\n{error}"
        )}
    ]
    try:
        response = ollama_chat_fn(messages, model, temperature=0.1)
        return extract_code(response), None
    except Exception as e:
        return None, str(e)


def write_and_run(task, ollama_chat_fn, model, ask_permission_fn, max_attempts=3):
    """
    Full pipeline: write code → show to user → ask permission → run → fix if broken.
    Returns (output, final_code, success)
    """
    code, err = write_code(task, ollama_chat_fn, model)
    if not code:
        return f"Could not write code: {err}", None, False

    for attempt in range(1, max_attempts + 1):
        print(f"\n{'─'*50}")
        print(f"  Generated Code (attempt {attempt}/{max_attempts}):")
        print(f"{'─'*50}")
        print(code)
        print(f"{'─'*50}\n")

        if not ask_permission_fn(
            f"Run this Python code",
            f"Task: {task[:80]}",
            default_yes=False
        ):
            return "Code execution cancelled by user.", code, False

        stdout, stderr, rc = run_code(code)

        if rc == 0:
            output = stdout or "(Code ran successfully, no output)"
            return output, code, True

        print(f"  Error: {stderr[:300]}")
        if attempt < max_attempts:
            print(f"  Auto-fixing… (attempt {attempt+1}/{max_attempts})")
            code, fix_err = fix_code(code, stderr, ollama_chat_fn, model)
            if not code:
                return f"Could not fix: {fix_err}", None, False

    return f"Failed after {max_attempts} attempts.\nLast error: {stderr}", code, False
