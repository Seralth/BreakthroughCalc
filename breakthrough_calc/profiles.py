"""Settings location and the profile store (pure JSON, no Qt).

Store schema: {version, current, profiles: {name: state}}, plus app-level
keys (theme, lang) that the GUI keeps at the top level via read()/write().
Legacy v1 files (one flat state dict) are migrated to a single "Default"
profile on read.
"""

from __future__ import annotations

import json
import os
import sys


def settings_path() -> str:
    """Prefer a JSON next to the executable (portable/self-contained); fall back
    to a per-OS user config location if that directory isn't writable.

    - Linux AppImage: next to the .AppImage (via the APPIMAGE env var).
    - Windows onefile .exe: next to the .exe, else %APPDATA%\\BreakthroughCalc.
    - Otherwise: next to a frozen executable, else ~/.config/breakthrough-calc.
    """
    # Portable location next to the executable.
    exe_dir = None
    appimage = os.environ.get("APPIMAGE")
    if appimage:
        exe_dir = os.path.dirname(appimage)
        name = os.path.basename(appimage) + ".settings.json"
    elif getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        name = "settings.json"
    if exe_dir and os.access(exe_dir, os.W_OK):
        return os.path.join(exe_dir, name)

    # Per-OS user config fallback.
    if sys.platform == "win32":
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                            "BreakthroughCalc")
    else:
        base = os.path.join(os.path.expanduser("~"), ".config", "breakthrough-calc")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "settings.json")


class ProfileStore:
    """Profile CRUD over one settings file. Writes are best-effort: OSError
    is swallowed so a read-only install directory never crashes the app."""

    def __init__(self, path: str):
        self.path = path

    # ---- raw store (also carries the app-level theme/lang keys) -----------
    def read(self) -> dict:
        try:
            with open(self.path) as f:
                obj = json.load(f)
        except (OSError, ValueError):
            obj = None
        if isinstance(obj, dict) and "profiles" in obj:
            return obj
        # migrate a flat v1 settings dict into a single "Default" profile
        flat = obj if isinstance(obj, dict) else {}
        return {"version": 2, "current": "Default", "profiles": {"Default": flat}}

    def write(self, obj: dict):
        try:
            with open(self.path, "w") as f:
                json.dump(obj, f, indent=1)
        except OSError:
            pass

    # ---- profile CRUD ------------------------------------------------------
    def names(self) -> list[str]:
        return list(self.read().get("profiles", {}))

    def get(self, name: str) -> dict:
        return self.read().get("profiles", {}).get(name, {})

    def set(self, name: str, state: dict):
        """Save a profile's state and make it the current profile."""
        obj = self.read()
        obj.setdefault("profiles", {})[name] = state
        obj["current"] = name
        self.write(obj)

    def delete(self, name: str):
        """Delete a profile and return the new current profile's name, or
        None (and change nothing) if it is the last one — the store always
        keeps at least one profile."""
        obj = self.read()
        profs = obj.get("profiles", {})
        if len(profs) <= 1:
            return None
        profs.pop(name, None)
        newcur = next(iter(profs))
        obj["current"] = newcur
        self.write(obj)
        return newcur

    @property
    def current(self) -> str:
        """The current profile's name; falls back to the first existing
        profile when the stored name is missing."""
        obj = self.read()
        profs = obj.get("profiles", {})
        cur = obj.get("current", "Default")
        if cur not in profs and profs:
            cur = next(iter(profs))
        return cur

    @current.setter
    def current(self, name: str):
        obj = self.read()
        obj["current"] = name
        self.write(obj)
