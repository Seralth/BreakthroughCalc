"""i18n invariants.

These pin the translation table's structural health so the refactor (and any
future string edit) cannot silently break lookups: tr() falls back to English
on a missing key, so this whole failure class is invisible at runtime.
"""

import ast
import os
import unittest

from breakthrough_calc import i18n

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(REPO, "breakthrough_calc")

NON_EN_LANGS = [c for c in i18n.LANGS if c != "en"]

# Literal tr() arguments that are intentionally NOT translated.
UNTRANSLATED_OK: set[str] = set()


def literal_tr_calls():
    """Every literal string passed to tr(...) anywhere in the package."""
    out = {}
    for fname in sorted(os.listdir(PKG)):
        if not fname.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(PKG, fname)).read())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name) and node.func.id == "tr"
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                out.setdefault(node.args[0].value, f"{fname}:{node.lineno}")
    return out


class TableStructure(unittest.TestCase):
    def test_all_languages_share_one_key_set(self):
        key_sets = {lang: set(i18n.TRANSLATIONS[lang]) for lang in NON_EN_LANGS}
        ref = key_sets[NON_EN_LANGS[0]]
        for lang, keys in key_sets.items():
            self.assertEqual(keys, ref,
                             f"{lang} key set differs from {NON_EN_LANGS[0]}")

    def test_placeholder_counts_match_english(self):
        for lang in NON_EN_LANGS:
            for en, xx in i18n.TRANSLATIONS[lang].items():
                self.assertEqual(en.count("{}"), xx.count("{}"),
                                 f"{lang}: placeholder mismatch for {en!r}")

    def test_no_empty_translations(self):
        for lang in NON_EN_LANGS:
            for en, xx in i18n.TRANSLATIONS[lang].items():
                self.assertTrue(xx.strip(), f"{lang}: empty translation for {en!r}")


class CallSiteCoverage(unittest.TestCase):
    def test_every_literal_tr_call_is_translated(self):
        calls = literal_tr_calls()
        missing = {}
        for text, where in calls.items():
            if text in UNTRANSLATED_OK:
                continue
            for lang in NON_EN_LANGS:
                if text not in i18n.TRANSLATIONS[lang]:
                    missing.setdefault(f"{where}: {text[:70]!r}", []).append(lang)
        self.assertFalse(missing, f"tr() call sites missing translations: {missing}")

    def test_whitelist_is_not_stale(self):
        calls = literal_tr_calls()
        for text in UNTRANSLATED_OK:
            self.assertIn(text, calls,
                          "whitelisted string no longer appears in any tr() call")
            for lang in NON_EN_LANGS:
                self.assertNotIn(text, i18n.TRANSLATIONS[lang],
                                 "whitelisted string IS translated — remove it")


class LabelMapCoverage(unittest.TestCase):
    """Display strings routed through labels.LabelMap reach tr() as
    NON-literal arguments, so the AST scan above cannot see them — cover the
    label tables explicitly (plus the engine data keys they fall back to)."""

    def test_label_display_strings_are_translated(self):
        from breakthrough_calc import labels
        # Values displayed via disp(): mapped display names, plus raw keys
        # that fall through .get(key, key) for stages without a mapping.
        from breakthrough_calc.engine import Engine
        e = Engine()
        display_strings = set(labels.STAGE_LABELS.values()) \
            | set(labels.PHASE_LABELS.values()) \
            | set(labels.VASE_INPUT_LABELS.values()) \
            | {s for s in e.stages() if s not in labels.STAGE_LABELS} \
            | set(e.data["rarity_names"]) | {"None"}
        untranslated_ok = {"N/A"}  # displayed as-is in every language
        missing = {}
        for lang in NON_EN_LANGS:
            for s in sorted(display_strings - untranslated_ok):
                if s not in i18n.TRANSLATIONS[lang]:
                    missing.setdefault(s, []).append(lang)
        self.assertFalse(missing, f"label display strings untranslated: {missing}")


class RoundTrip(unittest.TestCase):
    """Display-string -> English reverse mapping for values that persist to
    settings (combo items go through i18n.reverse on save/load)."""

    # The combo-item domains that actually round-trip via reverse().
    DOMAINS = [
        "Nascent Soul", "Incarnation", "Voidbreak", "Wholeness", "Perfection",
        "Early", "Middle", "Late",
        "Blue", "Purple", "Gold",
        "None", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic",
    ]

    def test_reverse_recovers_english_in_every_language(self):
        try:
            for lang in NON_EN_LANGS:
                i18n.set_lang(lang)
                for en in self.DOMAINS:
                    disp = i18n.tr(en)
                    self.assertEqual(i18n.reverse(disp), en,
                                     f"{lang}: {en!r} -> {disp!r} does not round-trip")
        finally:
            i18n.set_lang("en")


class DurationFormatting(unittest.TestCase):
    """tr_duration output is pinned per language; mobile's trDuration mirrors
    these exact strings, so a change here must be coordinated with i18n.dart."""

    CASES = {
        "en": ("1D 12H 5M", "450D 0H 30M  (~1.2 yr)"),
        "ru": ("1д 12ч 5м", "450д 0ч 30м  (~1.2 г)"),
        "de": ("1T 12Std 5Min", "450T 0Std 30Min  (~1.2 J)"),
        "es": ("1d 12h 5min", "450d 0h 30min  (~1.2 años)"),
        "zh": ("1天12时5分", "450天0时30分  (~1.2年)"),
    }

    def test_goldens(self):
        try:
            for lang, (short, long) in self.CASES.items():
                i18n.set_lang(lang)
                self.assertEqual(i18n.tr_duration("1D 12H 5M"), short, lang)
                self.assertEqual(i18n.tr_duration("450D 0H 30M  (~1.2 yr)"), long, lang)
        finally:
            i18n.set_lang("en")


if __name__ == "__main__":
    unittest.main()


class CrossPlatformDrift(unittest.TestCase):
    """Ratchet: desktop (i18n.py) and mobile (i18n.dart) hand-maintain the
    same translations, so a key present on both should translate the same.
    80 existing disagreements are grandfathered in i18n_drift_baseline.json
    (they need a human language-QA pass — automated reconciliation degrades
    quality, since the game glossary carries wrong homonyms and each
    platform holds some better game-term matches). This test fails only if
    NEW drift appears, or if a baselined pair is fixed but not removed from
    the baseline — keeping the debt visible and strictly non-growing."""

    _DART = os.path.join(REPO, "mobile", "lib", "i18n.dart")
    _BASELINE = os.path.join(os.path.dirname(__file__),
                             "i18n_drift_baseline.json")
    _LANGS = ("ru", "de", "es", "zh")

    def _mobile_map(self) -> dict:
        import re
        src = open(self._DART, encoding="utf-8").read()
        body = re.search(
            r"const Map<String, Map<String, String>> _t = \{(.*)\};",
            src, re.S).group(1)

        def unq(s):
            return ast.literal_eval(s.replace("\n", " "))
        out = {}
        for k, inner in re.findall(
                r"\n  ((?:'(?:[^'\\]|\\.)*')|(?:\"(?:[^\"\\]|\\.)*\")):"
                r"\s*\{([^}]*)\}", body):
            key = unq(k)
            d = {}
            for lk, lv in re.findall(
                    r"'(\w+)':\s*((?:'(?:[^'\\]|\\.)*')"
                    r"|(?:\"(?:[^\"\\]|\\.)*\"))", inner):
                d[lk] = unq(lv)
            out[key] = d
        return out

    def _current_drift(self) -> set:
        mobile = self._mobile_map()
        py = {}
        for lang in self._LANGS:
            for en, v in i18n.TRANSLATIONS.get(lang, {}).items():
                py.setdefault(en, {})[lang] = v
        drift = set()
        for en in set(py) & set(mobile):
            for lang in self._LANGS:
                a, b = py[en].get(lang), mobile[en].get(lang)
                if a is not None and b is not None and a != b:
                    drift.add((en, lang))
        return drift

    def test_no_new_cross_platform_drift(self):
        baseline = {(en, lang) for en, lang in
                    __import__("json").load(open(self._BASELINE,
                                                 encoding="utf-8"))}
        drift = self._current_drift()
        new = drift - baseline
        self.assertFalse(new, "NEW desktop/mobile translation drift — make "
                         "the two i18n files agree for these (key, lang): "
                         f"{sorted(new)}")
        stale = baseline - drift
        self.assertFalse(stale, "These baselined drifts are now fixed — "
                         "remove them from tests/i18n_drift_baseline.json: "
                         f"{sorted(stale)}")
