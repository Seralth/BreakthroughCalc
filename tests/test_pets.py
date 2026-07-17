"""Pet planner: catalog schema and the shared derivation fixture.

Pure-logic tests (no Qt). The cases live in mobile/test/pet_cases.json,
which the Dart twin (mobile/test/pets_test.dart) runs too — the two
implementations can only drift if one of these suites goes red.
"""

import json
import os
import unittest

from breakthrough_calc.pets import load_pets, plan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = os.path.join(ROOT, "mobile", "test", "pet_cases.json")


class CatalogSchema(unittest.TestCase):
    def setUp(self):
        self.cat = load_pets()

    def test_catalog_loads(self):
        self.assertTrue(self.cat.get("pets"))
        self.assertTrue(self.cat.get("essences"))
        self.assertTrue(self.cat.get("rarity_ladder"))

    def test_costs_and_refunds_use_known_essences(self):
        known = {e["id"] for e in self.cat["essences"]}
        for p in self.cat["pets"]:
            for key in ("cost", "refund"):
                for ess in (p.get(key) or {}):
                    self.assertIn(ess, known, f"{p['id']}.{key}")

    def test_every_pet_refunds_something(self):
        # Elimination refunds are what make owned pets a liquid reserve;
        # a pet with no refund would silently vanish from the pool math.
        for p in self.cat["pets"]:
            self.assertTrue(p.get("refund"), p["id"])

    def test_exchangeable_pets_refund_their_exact_cost(self):
        for p in self.cat["pets"]:
            if p.get("cost"):
                self.assertEqual(p["cost"], p["refund"], p["id"])

    def test_ladder_is_sorted_by_copies(self):
        copies = [step["copies"] for step in self.cat["rarity_ladder"]]
        self.assertEqual(copies, sorted(copies))


class SharedFixture(unittest.TestCase):
    def test_cases_match_the_dart_twin(self):
        cat = load_pets()
        with open(CASES) as f:
            cases = json.load(f)
        for case in cases:
            got = plan(cat, case["owned"], case["essences"])
            for pid, want in case["expect"].items():
                p = got[pid]
                self.assertEqual(p.copies, want["copies"],
                                 f"{case['name']}: {pid} copies")
                self.assertEqual(p.rarity, want["rarity"],
                                 f"{case['name']}: {pid} rarity")
                self.assertEqual(p.realm, want["realm"],
                                 f"{case['name']}: {pid} realm")


if __name__ == "__main__":
    unittest.main()
