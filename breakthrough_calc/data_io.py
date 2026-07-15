"""Data-file resolution and loading.

Everything PyInstaller bundling depends on lives here: the frozen-app base
path and the loaders for data/ tables and catalogs. Packaging bundles the
whole data/ directory (see build-appimage.sh / build-windows.yml).
"""

from __future__ import annotations

import json
import os
import sys

if getattr(sys, "frozen", False):
    _BASE = sys._MEIPASS  # PyInstaller bundle
else:
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BASE, "data", "breakthrough.json")


def load_data(path: str | None = None) -> dict:
    with open(path or _DATA_PATH) as f:
        return json.load(f)


def load_pill_sources() -> list:
    """Catalog of known Cultivation Pill Effect sources (recovered from game
    data) for the GUI picker. Missing file just means no catalog."""
    return _load_catalog("pill_effect_sources.json")


def load_respira_sources() -> list:
    """Catalog of known Respira attempt/EXP sources for the GUI picker.
    kind: 'attempt' (+N daily attempts), 'exp_pct' (informational — the in-game
    Respira EXP tooltip already includes it), 'pill_attempt' (raises the daily
    pill limit instead)."""
    return _load_catalog("respira_sources.json")


def _load_catalog(fname: str) -> list:
    try:
        with open(os.path.join(_BASE, "data", fname)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return []
