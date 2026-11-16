#!/usr/bin/env python3
"""Check that everything the widget-builder skill  needs is in place, before any building starts.

Prints one JSON line: {"ok": bool, "docs": path, "ego": path|null, "ego_note": str|null, "password_dir": path|null,
"problems": [plain-English lines]}. password_dir is a folder only the person can open, for the storefront password file.
Exit code 0 when ok, 1 when something is missing. ego lite is optional: without it the person previews by hand
or in their own browser, so a missing ego lite is a note, never a problem.

Usage:
    python3 preflight.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
DOCS = PLUGIN / "references" / "docs"
NEEDED_PAGES = ["index.md", "build.md", "style.md", "phone.md", "outputs/liquid-section.md", "recipes/photo-tiles.md"]


def ego_path() -> str | None:
    """ego lite puts its command in ~/.local/bin, which many shells don't search."""
    found = shutil.which("ego-browser")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "ego-browser"
    return str(local) if local.is_file() else None


def timed_out_output(e: subprocess.TimeoutExpired) -> str:
    """What a timed-out run printed before it was stopped. Python hands it back as bytes even in text mode."""
    parts = [p.decode("utf-8", errors="replace") if isinstance(p, bytes) else p for p in (e.stdout, e.stderr) if p]
    return "\n".join(parts)


def read_password(password: str | None, password_file: Path | None) -> str | None:
    """The storefront password, from a private file when one is given, so it never sits on a command line.

    The file is made readable by its owner only. --password still works, for a run by hand.
    """
    if password_file:
        try:
            password_file.chmod(0o600)
        except OSError:
            pass  # not ours to change (another owner, a read-only disk): reading it is what matters
        return password_file.read_text(encoding="utf-8").strip() or None
    return password


PRIVATE = Path.home() / ".loox-widget-build"
STALE_HOURS = 12


def password_dir() -> str | None:
    """A folder only its owner can open, for the storefront password file. Made before the password is asked for,
    so the file is private from the moment it is written, whatever permissions the writer gives it.

    A password file left by an earlier build (older than STALE_HOURS) is removed here: the skill asks Claude to
    delete it at the end of a build, and this is the backstop when that didn't happen.
    """
    try:
        PRIVATE.mkdir(mode=0o700, exist_ok=True)
        PRIVATE.chmod(0o700)
        for f in PRIVATE.iterdir():
            if f.is_file() and time.time() - f.stat().st_mtime > STALE_HOURS * 3600:
                f.unlink()
        return str(PRIVATE)
    except OSError:
        return None


def main() -> int:
    problems: list[str] = []
    if sys.version_info < (3, 9):
        problems.append(f"Python is {sys.version.split()[0]}. The tools need 3.9 or newer.")
    missing = [p for p in NEEDED_PAGES if not (DOCS / p).exists()]
    if missing:
        problems.append(f"The widget docs are missing pages ({', '.join(missing)}). Download the skill again.")
    if not (HERE / "install.py").exists():
        problems.append("The installer is missing. Download the skill again.")
    ego, ego_note = ego_path(), None
    if not ego:
        ego_note = "ego lite isn't installed. That's fine: the preview can be done by hand or in your own browser."
    else:
        try:
            run = subprocess.run([ego, "--help"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
            if run.returncode != 0:
                ego, ego_note = None, "ego lite is installed but didn't answer. Open the ego lite app once to use it."
        except (OSError, subprocess.TimeoutExpired):
            ego, ego_note = None, "ego lite is installed but didn't answer. Open the ego lite app once to use it."
    print(json.dumps({"ok": not problems, "docs": str(DOCS), "ego": ego, "ego_note": ego_note, "password_dir": password_dir(), "problems": problems}))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
