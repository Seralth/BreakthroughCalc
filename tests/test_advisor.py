"""Advisor: candidate enumeration, channel split, and engine-diff ranking."""

import unittest

from breakthrough_calc.advisor import (
    PLANNED, RANDOM, apply_deltas, candidates, channel_for, rank, steps,
)
from breakthrough_calc.engine import Engine, Inputs
from breakthrough_calc.shelf import load_sources


def base_inputs(**kw):
    d = dict(stage="Nascent", phase="LATE", grade="G5",
             culti_speed=57.22, absorption_ratio=0.275)
    d.update(kw)
    return Inputs(**d)


class StepEnumeration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = load_sources()
        cls.by_id = {s["id"]: s for s in cls.cat["sources"]}

    def test_binary_curio_owned_vs_not(self):
        lantern = self.by_id["dongxuans_lantern"]
        self.assertEqual(steps(lantern, None), [("Own", 1)])
        self.assertEqual(steps(lantern, 1), [])

    def test_tier_book_targets_next_effect_threshold(self):
        chroma = self.by_id["chroma"]
        (action, level), = steps(chroma, 6)
        self.assertGreater(level, 6)
        self.assertTrue(action.startswith("Tier "))
        # the step lands ON a threshold, not merely one tier up
        thresholds = {e.get("min_level", 1) for e in chroma["effects"]}
        self.assertIn(level, thresholds)

    def test_friend_max_sentinel_and_completion(self):
        crane = self.by_id["crane_boy"]
        self.assertEqual(steps(crane, None), [("max", -1)])
        self.assertEqual(steps(crane, -1), [])

    def test_parametric_curio_steps_each_param(self):
        ysj = self.by_id["yang_spirit_jade"]
        acts = dict(steps(ysj, [4, 8]))
        self.assertEqual(list(acts.values()), [[5, 8]])  # upgrade already max
        acts = dict(steps(ysj, [5, 3]))
        self.assertEqual(list(acts.values()), [[5, 4]])  # star already max

    def test_ladder_step_uses_rung_label(self):
        virya = self.by_id["ascension_virya"]
        (action, rung), = steps(virya, 1)
        self.assertEqual(rung, 2)
        self.assertEqual(action, virya["levels"]["labels"][1])

    def test_effectless_collection_curios_offer_no_steps(self):
        chaos_bell = self.by_id["chaos_bell"]
        self.assertEqual(steps(chaos_bell, None), [])

    def test_channels(self):
        self.assertEqual(channel_for(self.by_id["dongxuans_lantern"]), RANDOM)
        self.assertEqual(channel_for(self.by_id["chroma"]), PLANNED)
        self.assertEqual(channel_for(self.by_id["daji"]), PLANNED)


class CandidateDeltas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = load_sources()

    def test_vault_awareness_owned_curio_leaves_the_draw_pool(self):
        pool = {c.source_id for c in candidates(self.cat, {"owned": {}})}
        self.assertIn("dongxuans_lantern", pool)
        owned = candidates(self.cat, {"owned": {"dongxuans_lantern": 1}})
        self.assertNotIn("dongxuans_lantern", {c.source_id for c in owned})

    def test_info_only_sources_never_become_candidates(self):
        pool = {c.source_id for c in candidates(self.cat, {"owned": {}})}
        for sid in ("pisces_pendant", "auraseep_seal", "energy_jade"):
            self.assertNotIn(sid, pool)

    def test_lantern_delta_is_its_respira_percent(self):
        cand = next(c for c in candidates(self.cat, {"owned": {}})
                    if c.source_id == "dongxuans_lantern")
        self.assertEqual(cand.deltas, {"respira_effect": 10.0})

    def test_apply_deltas_rescales_the_respira_reading(self):
        inp = base_inputs(respira_exp=4041.0)
        out = apply_deltas(inp, {"respira_effect": 10.0}, books_now=14.0)
        self.assertAlmostEqual(out.respira_exp,
                               4041.0 * 124.0 / 114.0)
        # nothing modeled -> None (respira percent with no reading entered)
        self.assertIsNone(
            apply_deltas(base_inputs(), {"respira_effect": 10.0}, 0.0))

    def test_apply_deltas_lands_on_engine_units(self):
        inp = base_inputs(pill_effect=0.04, pill_limit=1,
                          respira_per_day=10)
        out = apply_deltas(inp, {"pill_effect": 2.0, "pill_attempts": 1.0,
                                 "respira_attempts": 1.0}, 0.0)
        self.assertAlmostEqual(out.pill_effect, 0.06)
        self.assertAlmostEqual(out.pill_limit, 2)
        self.assertAlmostEqual(out.respira_per_day, 11)


class Ranking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine()
        cls.cat = load_sources()
        cls.inp = base_inputs(
            target_stage="Incarnation", pill_rank="4R", pill_limit=4,
            pill_effect=0.04, gold_per_day=4, respira_per_day=10,
            respira_exp=4041.0)

    def test_rank_splits_plan_from_random_draws(self):
        adv = rank(self.engine, self.inp, self.cat, {"owned": {}})
        self.assertTrue(adv.valid)
        self.assertEqual(adv.metric, "target")
        self.assertTrue(adv.plan and adv.draws)
        for r in adv.plan:
            self.assertEqual(r.candidate.channel, PLANNED)
        for r in adv.draws:
            self.assertEqual(r.candidate.channel, RANDOM)
        draw_ids = {r.candidate.source_id for r in adv.draws}
        self.assertIn("dongxuans_lantern", draw_ids)
        self.assertIn("dongxuans_pot", draw_ids)

    def test_savings_positive_and_sorted(self):
        adv = rank(self.engine, self.inp, self.cat, {"owned": {}})
        for group in (adv.plan, adv.draws):
            saved = [r.days_saved for r in group]
            self.assertTrue(all(s > 0 for s in saved))
            self.assertEqual(saved, sorted(saved, reverse=True))

    def test_owning_everything_shrinks_the_lists(self):
        empty = rank(self.engine, self.inp, self.cat, {"owned": {}})
        owned = {r.candidate.source_id: r.candidate.new_owned
                 for r in empty.draws}
        adv = rank(self.engine, self.inp, self.cat, {"owned": owned})
        self.assertLess(len(adv.draws), len(empty.draws))

    def test_attempt_bonus_without_reading_is_not_ranked(self):
        # +1 Respira attempt saves nothing while no respira_exp is entered:
        # the advisor must not advertise a zero-day improvement.
        inp = base_inputs(target_stage="Incarnation")
        adv = rank(self.engine, inp, self.cat, {"owned": {}})
        ids = {r.candidate.source_id for r in adv.plan + adv.draws}
        self.assertNotIn("dongxuans_cushion", ids)

    def test_invalid_baseline_reports_reason(self):
        adv = rank(self.engine, Inputs(stage="Nascent", phase="LATE",
                                       grade="G5"), self.cat, {"owned": {}})
        self.assertFalse(adv.valid)
        self.assertTrue(adv.reason)


if __name__ == "__main__":
    unittest.main()
