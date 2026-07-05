"""Application themes.

The app forces the Fusion style plus an explicit palette so it renders
identically on every OS, instead of inheriting each platform's native theme
(which is why Windows looked inconsistent). "System" reads the OS light/dark
preference and applies the matching built-in palette.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

THEMES = ["Seralth", "Dark", "Light", "System"]

# Accent colors are resolved per-theme so labels stay readable on any
# background (used by the GUI in place of the old hardcoded hex values).
ACCENTS = {
    "dark":  {"muted": "#8a8a8a", "good": "#5fce8f", "warn": "#e0a050", "bad": "#e06060"},
    "light": {"muted": "#6a6a6a", "good": "#1f8a4c", "warn": "#b06a10", "bad": "#c0392b"},
}


def _palette(bg, base, text, highlight, disabled) -> QPalette:
    p = QPalette()
    bg, base, text = QColor(bg), QColor(base), QColor(text)
    hl = QColor(highlight)
    dim = QColor(disabled)
    p.setColor(QPalette.Window, bg)
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, bg)
    p.setColor(QPalette.ToolTipBase, base)
    p.setColor(QPalette.ToolTipText, text)
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, bg)
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.BrightText, QColor("#ff5555"))
    p.setColor(QPalette.Link, hl)
    p.setColor(QPalette.Highlight, hl)
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.PlaceholderText, dim)
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, role, dim)
    return p


_PALETTES = {
    # Blue-tinted dark scheme (the author's KDE look), now portable everywhere.
    "Seralth": _palette("#1e2530", "#191f28", "#c6d2e6", "#3d6fb5", "#5a6577"),
    "Dark":    _palette("#2b2b2b", "#232323", "#dddddd", "#2a82da", "#6e6e6e"),
    "Light":   _palette("#f2f2f2", "#ffffff", "#1c1c1c", "#2a72c8", "#a0a0a0"),
}

# Which accent set each theme uses.
_ACCENT_FOR = {"Seralth": "dark", "Dark": "dark", "Light": "light"}


def resolve(name: str) -> str:
    """Map a theme name (including 'System') to a concrete palette name."""
    if name == "System":
        from PySide6.QtWidgets import QApplication
        hints = QApplication.styleHints()
        scheme = getattr(hints, "colorScheme", lambda: None)()
        return "Light" if scheme == Qt.ColorScheme.Light else "Dark"
    return name if name in _PALETTES else "Seralth"


def accents(name: str) -> dict:
    return ACCENTS[_ACCENT_FOR.get(resolve(name), "dark")]


def apply(app, name: str) -> None:
    app.setStyle("Fusion")
    app.setPalette(_PALETTES[resolve(name)])
