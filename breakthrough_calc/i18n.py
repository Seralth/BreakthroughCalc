"""Tiny gettext-style i18n for the desktop GUI.

tr(s) looks up the English source string in the current language's dict and
falls back to English (s itself). Translations are the SINGLE SOURCE OF
TRUTH shared with the mobile app: data/i18n.json ({en: {ru,de,es,zh}}),
synced to mobile/assets/data and pinned by tests. Desktop and mobile can
never drift because they read the same file — edit a string once, both
platforms get it.

reverse(s) maps a translated display string (any language) back to its
English source — used to turn combo display text back into internal keys
and to migrate legacy settings that stored localized display names.
"""

from __future__ import annotations

import json

from .data_io import resource_path

LANGS = {"en": "English", "ru": "Русский", "de": "Deutsch", "es": "Español", "zh": "中文"}


def _load_translations() -> dict:
    """data/i18n.json ({en: {lang: val}}) -> {lang: {en: val}} for tr()."""
    try:
        with open(resource_path("data", "i18n.json"), encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError):
        return {lang: {} for lang in LANGS if lang != "en"}
    out: dict = {lang: {} for lang in LANGS if lang != "en"}
    for en, row in raw.items():
        for lang, val in row.items():
            out.setdefault(lang, {})[en] = val
    return out

_current = "en"


def set_lang(code: str):
    global _current
    _current = code if code in LANGS else "en"


def get_lang() -> str:
    return _current


def tr(s: str) -> str:
    if _current == "en":
        return s
    return TRANSLATIONS.get(_current, {}).get(s, s)


def reverse(s: str) -> str:
    """Translated display string (any language) -> English source; identity
    for English/unknown strings."""
    return _REVERSE.get(s, s)


TRANSLATIONS = _load_translations()

# Translated display string -> English source, across all languages. The
# shared table holds both display labels ("Nascent Soul") and the raw
# internal keys the mobile app translates directly ("Nascent") — which can
# share a translation. reverse() is used to turn a combo's DISPLAYED text
# back into its English label, so on a collision the more specific (longer)
# key wins, keeping the display-label round-trip intact.
_REVERSE = {}
for _lang in TRANSLATIONS.values():
    for _en in sorted(_lang, key=lambda s: (-len(s), s)):
        _REVERSE.setdefault(_lang[_en], _en)


# Duration suffixes for display-time localization of engine fmt_days output.
# The engine string stays canonical English ("1D 12H 0M  (~1.2 yr)") — tests
# and cross-engine parity compare its exact output.
_DUR_SUFFIXES = {
    "ru": ("д", "ч", "м", "г"),
    "de": ("T", "Std", "Min", "J"),
    "es": ("d", "h", "min", "años"),
    "zh": ("天", "时", "分", "年"),
}

_DUR_RE = None
_YR_RE = None


def tr_duration(s: str) -> str:
    """Localize a fmt_days string at display time; identity for English."""
    global _DUR_RE, _YR_RE
    suf = _DUR_SUFFIXES.get(get_lang())
    if suf is None:
        return s
    import re
    if _DUR_RE is None:
        _DUR_RE = re.compile(r"(\d+)D (\d+)H (\d+)M")
        _YR_RE = re.compile(r"\(~([\d.]+) yr\)")
    joiner = "" if get_lang() == "zh" else " "
    s = _DUR_RE.sub(lambda m: f"{m[1]}{suf[0]}{joiner}{m[2]}{suf[1]}{joiner}{m[3]}{suf[2]}", s)
    s = _YR_RE.sub(lambda m: f"(~{m[1]}{joiner}{suf[3]})", s)
    return s
