"""Sources Shelf: catalog schema, derivation, and legacy-migration pins.

Pure-logic tests (no Qt). The derivation cases live in the shared fixture
mobile/test/shelf_cases.json, which the Dart twin runs too — the two
implementations can only drift if one of these suites goes red.
"""

import json
import os
import unittest

from breakthrough_calc.shelf import (
    derive, effective, load_sources, migrate_legacy, validate_catalog,
)
from breakthrough_calc.data_io import load_pill_sources, load_respira_sources

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = os.path.join(ROOT, "mobile", "test", "shelf_cases.json")

# Ids are OMV2 wire data once the shelf ships share codes: renaming one
# breaks every shared build. Append-only — a failure here means a rename.
KNOWN_IDS = [
    "longevity", "energy_unification", "rejuvenation", "lifeboom", "focus",
    "golden_core", "astrology", "ninefall", "cosmic_power", "taiyin_meridian",
    "dragon_flight", "yins_grasp", "lions_roar", "floral_essence",
    "great_yang_manual", "purify_cleanse", "zixiao_sutra", "astral_arcanum",
    "chroma", "cauldron_refinement", "moon_meru",
    "princess_iron_fan", "daji", "shen_gongbao", "six_eared_macaque",
    "jiang_ziya", "taotie", "crane_boy", "white_astra", "princess_adalinda",
    "leizhenzi", "ascension_virya", "yang_spirit_jade", "dongxuans_pot",
    "pisces_pendant",
]

_BANNED_PROSE = ("verified", "screenshot", "confirmed", "dump",
                 "community guide")


class CatalogSchema(unittest.TestCase):
    def setUp(self):
        self.cat = load_sources()

    def test_catalog_loads_and_validates(self):
        self.assertTrue(self.cat.get("sources"))
        self.assertEqual(validate_catalog(self.cat), [])

    def test_id_set_is_append_only(self):
        ids = [s["id"] for s in self.cat["sources"]]
        for known in KNOWN_IDS:
            self.assertIn(known, ids)

    def test_display_embedded_targets_never_receive_values(self):
        # The double-count guard rail: every guarded target forbids effects,
        # and no source aims a valued effect at a display-embedded target.
        for tid, t in self.cat["targets"].items():
            if t["mode"] == "display_embedded":
                self.assertIs(t.get("effects_allowed"), False, tid)

    def test_user_visible_notes_follow_style_rules(self):
        for s in self.cat["sources"]:
            texts = [s.get("note", "")] + [e.get("note", "")
                                           for e in s["effects"]]
            for text in texts:
                for banned in _BANNED_PROSE:
                    self.assertNotIn(banned, text.lower(),
                                     f"{s['id']}: {text!r}")

    def test_legacy_aliases_cover_both_old_catalogs(self):
        claimed = {(a["catalog"], a["name"])
                   for s in self.cat["sources"] for a in s.get("legacy", [])}
        for e in load_pill_sources():
            self.assertIn(("pe", e["name"]), claimed, e["name"])
        for e in load_respira_sources():
            if e.get("kind") == "attempt":     # only these were persisted
                self.assertIn(("respira", e["name"]), claimed, e["name"])


class FieldRegistryLink(unittest.TestCase):
    """fields.py's shelf_target column stays consistent with the catalog:
    every linked target is raw_additive and names the exact field the
    registry feeds to the engine — the structural half of the
    double-counting guard."""

    def test_every_shelf_target_is_raw_additive_and_field_matched(self):
        from breakthrough_calc.fields import FIELDS
        targets = load_sources()["targets"]
        linked = [s for s in FIELDS if s.shelf_target]
        self.assertTrue(linked)
        for spec in linked:
            t = targets.get(spec.shelf_target)
            self.assertIsNotNone(t, spec.key)
            self.assertEqual(t["mode"], "raw_additive", spec.key)
            self.assertEqual(t["field"], spec.inputs_attr or spec.key,
                             spec.key)


class Derivation(unittest.TestCase):
    def setUp(self):
        self.cat = load_sources()
        with open(CASES) as f:
            self.cases = json.load(f)

    def test_shared_fixture_cases(self):
        for case in self.cases:
            derived = derive(self.cat, case["shelf"])
            got = {tid: d.total for tid, d in derived.items()}
            self.assertEqual(set(got), set(case["expect"]), case["name"])
            for tid, want in case["expect"].items():
                self.assertAlmostEqual(got[tid], want, places=9,
                                       msg=f"{case['name']}: {tid}")

    def test_contributions_carry_provenance(self):
        d = derive(self.cat, {"owned": {"purify_cleanse": 9}})
        books = d["respira_effect"]
        self.assertEqual(len(books.contributions), 2)
        self.assertEqual({c.name for c in books.contributions},
                         {"Purify & Cleanse"})
        self.assertEqual(books.contributions[0].level_label, "Tier 9")

    def test_ordering_is_deterministic(self):
        shelf = {"owned": {"moon_meru": 12, "six_eared_macaque": 17,
                           "purify_cleanse": 1}}
        d = derive(self.cat, shelf)["respira_effect"]
        # category order first (books before friends), then value descending.
        self.assertEqual([c.source_id for c in d.contributions],
                         ["moon_meru", "purify_cleanse", "six_eared_macaque"])

    def test_effective_precedence(self):
        d = derive(self.cat, {"owned": {"chroma": 12}})["pill_attempts"]
        self.assertEqual(effective(d, None, base=10.0), 11.0)
        self.assertEqual(effective(d, 15.0, base=10.0), 15.0)  # override wins
        self.assertEqual(effective(None, None, base=10.0), 10.0)


class LegacyMigration(unittest.TestCase):
    def setUp(self):
        self.cat = load_sources()
        self.pe = load_pill_sources()

    def test_pill_effect_total_is_bit_identical(self):
        # A user with EVERY old pill-effect row checked at catalog values:
        # the migrated shelf must reproduce the exact same total.
        rows = [[e["name"], e["percent"]] for e in self.pe]
        old_total = sum(p for _, p in rows)
        owned, custom, notes = migrate_legacy(rows, [], self.cat)
        derived = derive(self.cat, {"owned": owned, "custom": custom})
        self.assertAlmostEqual(derived["pill_effect"].total, old_total,
                               places=9)

    def test_parametric_row_preserved_as_custom(self):
        rows = [["Yang Spirit Jade (curio)", 3.4]]
        owned, custom, notes = migrate_legacy(rows, [], self.cat)
        self.assertNotIn("yang_spirit_jade", owned)
        self.assertEqual(custom["pill_effect"], [["Yang Spirit Jade (curio)", 3.4]])
        self.assertTrue(notes)

    def test_free_typed_row_preserved_as_custom(self):
        rows = [["My event buff", 2.0]]
        owned, custom, _ = migrate_legacy(rows, [], self.cat)
        self.assertEqual(owned, {})
        self.assertEqual(custom["pill_effect"], [["My event buff", 2.0]])

    def test_respira_names_max_merge(self):
        # The old catalog's Chroma duplicate rows both imply tier 3; the pe
        # row implies tier 6 — max-merge must win with 6.
        owned, _, _ = migrate_legacy(
            [["Chroma (R8 technique)", 4.0]],
            ["Chroma Tier 3 (R8 technique)", "Chroma (R8 book, Tier 3)"],
            self.cat)
        self.assertEqual(owned["chroma"], 6)

    def test_friend_checkboxes_imply_levels(self):
        owned, _, _ = migrate_legacy(
            [], ["Iron Fan (immortal friend, lv 36)",
                 "Crane Boy (immortal friend, max)"], self.cat)
        self.assertEqual(owned["princess_iron_fan"], 36)
        self.assertEqual(owned["crane_boy"], -1)


if __name__ == "__main__":
    unittest.main()
