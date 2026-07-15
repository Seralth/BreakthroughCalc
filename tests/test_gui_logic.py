"""Pure-logic GUI helpers: version parsing, label maps, the profile store.

These pin persistence-compatibility promises (settings keys, legacy display
name migration, v1 store migration) without needing Qt — this module must
never import PySide6 so it runs under a Qt-less system pytest.
"""

import json
import os
import tempfile
import unittest

from breakthrough_calc import i18n, parse_version
from breakthrough_calc.labels import (
    PHASE_LABELS, STAGE_LABELS, VASE_INPUT_LABELS,
    phase_disp, phase_key, stage_disp, stage_key,
    vase_input_disp, vase_input_key,
)
from breakthrough_calc.profiles import ProfileStore


class ParseVersion(unittest.TestCase):
    """Pins the exact current behavior (shared with the update checker)."""

    def test_v_prefix_pads_to_three(self):
        self.assertEqual(parse_version("v2.7"), (2, 7, 0))

    def test_plain_and_full(self):
        self.assertEqual(parse_version("2.14"), (2, 14, 0))
        self.assertEqual(parse_version("1.2.3"), (1, 2, 3))

    def test_prerelease_and_build_suffixes_ignored(self):
        self.assertEqual(parse_version("2.8.0-rc1"), (2, 8, 0))
        self.assertEqual(parse_version("v2.8.0+build5"), (2, 8, 0))

    def test_extra_components_truncated(self):
        self.assertEqual(parse_version("1.2.3.4"), (1, 2, 3))

    def test_junk_is_none(self):
        self.assertIsNone(parse_version("not-a-version"))
        self.assertIsNone(parse_version(""))
        self.assertIsNone(parse_version("v"))
        self.assertIsNone(parse_version("..."))


class LabelRoundTrips(unittest.TestCase):
    """disp() -> key() round-trips in every language, for mapped labels and
    for raw internal keys that pass through unmapped."""

    # (disp fn, key fn, internal keys) per persisted combo domain.
    DOMAINS = [
        (stage_disp, stage_key,
         list(STAGE_LABELS) + ["Novice", "Connection", "Voidbreak", "Supreme"]),
        (phase_disp, phase_key, list(PHASE_LABELS)),
        (vase_input_disp, vase_input_key, list(VASE_INPUT_LABELS)),
    ]

    def test_round_trip_every_language(self):
        try:
            for lang in i18n.LANGS:
                i18n.set_lang(lang)
                for disp, key, keys in self.DOMAINS:
                    for k in keys:
                        self.assertEqual(key(disp(k)), k,
                                         f"{lang}: {k!r} does not round-trip")
        finally:
            i18n.set_lang("en")

    def test_legacy_localized_display_names_resolve(self):
        # Old settings stored display names in the UI language of the day;
        # key() must still resolve them regardless of the current language.
        self.assertEqual(i18n.get_lang(), "en")
        ru_nascent = i18n.TRANSLATIONS["ru"]["Nascent Soul"]
        self.assertEqual(stage_key(ru_nascent), "Nascent")
        de_late = i18n.TRANSLATIONS["de"]["Late"]
        self.assertEqual(phase_key(de_late), "LATE")

    def test_legacy_english_display_names_resolve(self):
        self.assertEqual(stage_key("Nascent Soul"), "Nascent")
        self.assertEqual(vase_input_key("Gold (Legendary)"), "Gold")

    def test_internal_keys_pass_through(self):
        self.assertEqual(stage_key("Nascent"), "Nascent")
        self.assertEqual(phase_key("EARLY"), "EARLY")
        self.assertEqual(vase_input_key("Blue"), "Blue")


class ProfileStoreBehavior(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "settings.json")
        self.store = ProfileStore(self.path)

    def _write_raw(self, obj):
        with open(self.path, "w") as f:
            json.dump(obj, f)

    def test_v1_flat_dict_migrates_to_default_profile(self):
        flat = {"stage": "Novice", "speed": 5.0, "vase": True}
        self._write_raw(flat)
        self.assertEqual(self.store.read(),
                         {"version": 2, "current": "Default",
                          "profiles": {"Default": flat}})

    def test_missing_file_yields_empty_default(self):
        self.assertEqual(self.store.read(),
                         {"version": 2, "current": "Default",
                          "profiles": {"Default": {}}})
        self.assertEqual(self.store.current, "Default")

    def test_corrupt_file_yields_empty_default(self):
        with open(self.path, "w") as f:
            f.write("{not json")
        self.assertEqual(self.store.read(),
                         {"version": 2, "current": "Default",
                          "profiles": {"Default": {}}})

    def test_missing_current_falls_back_to_first_profile(self):
        self._write_raw({"profiles": {"A": {"speed": 1}, "B": {"speed": 2}}})
        self.assertEqual(self.store.current, "A")

    def test_stale_current_falls_back_to_first_profile(self):
        self._write_raw({"current": "Gone", "profiles": {"A": {}, "B": {}}})
        self.assertEqual(self.store.current, "A")

    def test_crud_round_trip(self):
        # a fresh store always materializes the migrated "Default" profile
        self.store.set("Main", {"speed": 7})
        self.store.set("Alt", {"speed": 9})
        self.assertEqual(self.store.names(), ["Default", "Main", "Alt"])
        self.assertEqual(self.store.current, "Alt")
        self.assertEqual(self.store.get("Main"), {"speed": 7})
        self.store.current = "Main"
        self.assertEqual(self.store.current, "Main")
        self.assertEqual(self.store.delete("Main"), "Default")
        self.assertEqual(self.store.names(), ["Default", "Alt"])

    def test_delete_refuses_last_profile(self):
        self._write_raw({"version": 2, "current": "Only",
                         "profiles": {"Only": {"speed": 1}}})
        self.assertIsNone(self.store.delete("Only"))
        self.assertEqual(self.store.names(), ["Only"])

    def test_write_swallows_oserror(self):
        store = ProfileStore(os.path.join(self.tmp.name, "no", "such", "dir.json"))
        store.write({"version": 2})  # must not raise


if __name__ == "__main__":
    unittest.main()
