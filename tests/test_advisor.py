"""Advisor: step tracks, obtainability gating, and engine-diff ranking."""

import unittest

from breakthrough_calc.advisor import (
    PLANNED, RANDOM, apply_deltas, candidates, channel_for, player_level,
    rank, steps,
)
from breakthrough_calc.engine import Engine, Inputs
from breakthrough_calc.shelf import load_sources


def base_inputs(**kw):
    d = dict(stage="Nascent", phase="LATE", grade="G5",
             culti_speed=57.22, absorption_ratio=0.275)
    d.update(kw)
    return Inputs(**d)


class StepTracks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = load_sources()
        cls.by_id = {s["id"]: s for s in cls.cat["sources"]}

    def test_binary_curio_owned_vs_not(self):
        lantern = self.by_id["dongxuans_lantern"]
        self.assertEqual(steps(lantern, None), [[("Own", 1, None)]])
        self.assertEqual(steps(lantern, 1), [])

    def test_tier_walk_covers_every_future_threshold(self):
        longevity = self.by_id["longevity"]
        (track,) = steps(longevity, None)
        self.assertEqual([a for a, _, _ in track], ["Tier 1", "Tier 3"])
        chroma = self.by_id["chroma"]
        (track,) = steps(chroma, 6)
        self.assertTrue(all(lvl > 6 for _, lvl, _ in track))

    def test_friend_max_sentinel_and_completion(self):
        crane = self.by_id["crane_boy"]
        self.assertEqual(steps(crane, None), [[("max", -1, None)]])
        self.assertEqual(steps(crane, -1), [])

    def test_parametric_curio_tracks_carry_upgrade_requirements(self):
        ysj = self.by_id["yang_spirit_jade"]
        tracks = steps(ysj, [6, 3])
        self.assertEqual(len(tracks), 1)          # star maxed: upgrade only
        actions = [(a, r) for a, _, r in tracks[0]]
        self.assertEqual(actions[0], ("Upgrade level 4", 18))
        self.assertEqual(actions[-1], ("Upgrade level 8", 26))
        star_only = steps(ysj, [4, 8])
        self.assertEqual([a for a, _, _ in star_only[0]],
                         ["Star 5", "Star 6"])

    def test_ladder_track_walks_remaining_rungs(self):
        virya = self.by_id["ascension_virya"]
        (track,) = steps(virya, 1)
        self.assertEqual([a for a, _, _ in track],
                         virya["levels"]["labels"][1:])

    def test_effectless_collection_curios_offer_no_steps(self):
        self.assertEqual(steps(self.by_id["chaos_bell"], None), [])

    def test_channels(self):
        self.assertEqual(channel_for(self.by_id["dongxuans_lantern"]), RANDOM)
        self.assertEqual(channel_for(self.by_id["chroma"]), PLANNED)


class Obtainability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = load_sources()

    def test_player_level_from_realm_table(self):
        self.assertEqual(player_level(self.cat, "Novice", "N/A"), 1)
        self.assertEqual(player_level(self.cat, "Nascent", "EARLY"), 18)
        self.assertEqual(player_level(self.cat, "Voidbreak", "LATE"), 26)
        self.assertIsNone(player_level(self.cat, "Atlantis", "EARLY"))

    def test_walk_reaches_past_info_only_thresholds(self):
        ids = {c.source_id: c for c in candidates(self.cat, {"owned": {}})}
        self.assertEqual(ids["longevity"].action, "Tier 3")
        self.assertEqual(ids["longevity"].deltas, {"respira_attempts": 1.0})
        self.assertEqual(ids["rejuvenation"].action, "Tier 3")
        self.assertEqual(ids["rejuvenation"].deltas, {"pill_effect": 2.0})

    def test_blessing_gated_until_incarnation_late_completed(self):
        for lvl in (18, 21, 23):    # Nascent .. Incarnation Late (in progress)
            ids = {c.source_id
                   for c in candidates(self.cat, {"owned": {}},
                                       current_level=lvl)}
            self.assertNotIn("ascension_virya", ids, lvl)
        voidbreak = {c.source_id
                     for c in candidates(self.cat, {"owned": {}},
                                         current_level=24)}
        self.assertIn("ascension_virya", voidbreak)

    def test_friends_gated_until_voidbreak(self):
        pre = {c.source_id for c in candidates(self.cat, {"owned": {}},
                                               current_level=23)}
        self.assertNotIn("daji", pre)
        self.assertNotIn("princess_iron_fan", pre)
        post = {c.source_id for c in candidates(self.cat, {"owned": {}},
                                                current_level=24)}
        self.assertIn("daji", post)

    def test_r9_books_gated_on_two_r8_books_at_tier_13(self):
        no_r8 = {c.source_id for c in candidates(self.cat, {"owned": {}})}
        self.assertNotIn("laws_of_nature", no_r8)
        ready = {"chroma": 13, "zixiao_sutra": 13}
        with_r8 = {c.source_id
                   for c in candidates(self.cat, {"owned": ready})}
        self.assertIn("laws_of_nature", with_r8)
        one_short = {c.source_id
                     for c in candidates(self.cat,
                                         {"owned": {"chroma": 13,
                                                    "zixiao_sutra": 12}})}
        self.assertNotIn("laws_of_nature", one_short)

    def test_curio_upgrade_gated_by_realm_level(self):
        shelf = {"owned": {"yang_spirit_jade": [6, 3]}}
        low = [c for c in candidates(self.cat, shelf, current_level=12)
               if c.source_id == "yang_spirit_jade"]
        self.assertEqual(low, [])         # upgrade 4 needs level 18
        mid = [c for c in candidates(self.cat, shelf, current_level=18)
               if c.source_id == "yang_spirit_jade"]
        self.assertEqual([c.action for c in mid], ["Upgrade level 4"])

    def test_book_ranks_gate_by_realm_phase(self):
        # Rank realm gates: R6 Nascent Late, R7 Inc Early, R8 Inc Middle,
        # R9 Inc Late (read from one book per rank, applied rank-wide).
        def ids(level, owned=None):
            return {c.source_id
                    for c in candidates(self.cat, {"owned": owned or {}},
                                        current_level=level)}
        self.assertNotIn("lions_roar", ids(19))
        self.assertIn("lions_roar", ids(20))
        self.assertNotIn("chroma", ids(21))
        self.assertIn("chroma", ids(22))
        ready = {"chroma": 13, "zixiao_sutra": 13}
        self.assertNotIn("laws_of_nature", ids(22, ready))
        self.assertIn("laws_of_nature", ids(23, ready))

    def test_ungated_when_stage_unknown(self):
        shelf = {"owned": {"yang_spirit_jade": [6, 3]}}
        cands = [c for c in candidates(self.cat, shelf, current_level=None)
                 if c.source_id == "yang_spirit_jade"]
        self.assertEqual(len(cands), 1)

    def test_vault_awareness_owned_curio_leaves_the_draw_pool(self):
        pool = {c.source_id for c in candidates(self.cat, {"owned": {}})}
        self.assertIn("dongxuans_lantern", pool)
        owned = candidates(self.cat, {"owned": {"dongxuans_lantern": 1}})
        self.assertNotIn("dongxuans_lantern", {c.source_id for c in owned})

    def test_info_only_sources_never_become_candidates(self):
        pool = {c.source_id for c in candidates(self.cat, {"owned": {}})}
        for sid in ("pisces_pendant", "auraseep_seal", "energy_jade"):
            self.assertNotIn(sid, pool)


class CandidateDeltas(unittest.TestCase):
    def test_apply_deltas_rescales_the_respira_reading(self):
        inp = base_inputs(respira_exp=4041.0)
        out = apply_deltas(inp, {"respira_effect": 10.0}, books_now=14.0)
        self.assertAlmostEqual(out.respira_exp, 4041.0 * 124.0 / 114.0)
        self.assertIsNone(
            apply_deltas(base_inputs(), {"respira_effect": 10.0}, 0.0))

    def test_apply_deltas_prices_blessing_via_absorption(self):
        e = Engine()
        inp = base_inputs(stage="Incarnation", phase="EARLY", grade="G1")
        out = apply_deltas(inp, {"bless_pp": 0.2}, 0.0, e)
        base = e.base_low("Incarnation", "EARLY", "G1")
        factor = (base + 0.2) / base
        self.assertAlmostEqual(out.bless_pp, 0.2)
        self.assertAlmostEqual(out.absorption_ratio, 0.275 * factor)
        # Abode Aura (speed/absorption) must be preserved by the gain
        self.assertAlmostEqual(out.culti_speed / out.absorption_ratio,
                               inp.culti_speed / inp.absorption_ratio)
        # a blessing gain is unpriceable without the engine's row base
        self.assertIsNone(apply_deltas(inp, {"bless_pp": 0.2}, 0.0))

    def test_apply_deltas_lands_on_engine_units(self):
        inp = base_inputs(pill_effect=0.04, pill_limit=1, respira_per_day=10)
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
        ids = {r.candidate.source_id for r in adv.plan + adv.draws}
        self.assertIn("dongxuans_lantern", ids)
        # a Nascent player cannot hold an ascension blessing yet
        self.assertNotIn("ascension_virya", ids)

    def test_blessing_ranks_once_ascended(self):
        inp = base_inputs(stage="Voidbreak", phase="EARLY", grade="G1",
                          culti_speed=208.0, absorption_ratio=1.0,
                          target_stage="Wholeness", respira_per_day=10,
                          respira_exp=12900.0)
        adv = rank(self.engine, inp, self.cat, {"owned": {}})
        ids = {r.candidate.source_id for r in adv.plan}
        self.assertIn("ascension_virya", ids)

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

    def test_blank_respira_fields_floor_to_the_stock_minimum(self):
        # Respira is never empty: blank fields assume 10 stock attempts and
        # the Stage's base EXP estimate, so respira sources still price.
        inp = base_inputs(target_stage="Incarnation")
        adv = rank(self.engine, inp, self.cat, {"owned": {}})
        ids = {r.candidate.source_id for r in adv.plan + adv.draws}
        self.assertIn("dongxuans_cushion", ids)   # +1 attempt on stock 10
        self.assertIn("dongxuans_lantern", ids)   # +10% on the estimate

    def test_ties_break_by_cheapness(self):
        # At Voidbreak with stock respira, every +1-attempt source saves
        # the same days; the cheaper acquisition must list first: R1 book
        # before R3 book before any immortal friend.
        inp = base_inputs(stage="Voidbreak", phase="EARLY", grade="G1",
                          culti_speed=208.0, absorption_ratio=1.0,
                          target_stage="Wholeness")
        adv = rank(self.engine, inp, self.cat, {"owned": {}})
        order = [r.candidate.source_id for r in adv.plan]
        self.assertIn("longevity", order)
        self.assertIn("cosmic_power", order)
        self.assertLess(order.index("longevity"), order.index("cosmic_power"))
        friend_idx = [order.index(i) for i in ("princess_iron_fan", "daji")
                      if i in order]
        for fi in friend_idx:
            self.assertGreater(fi, order.index("cosmic_power"))

    def test_invalid_baseline_reports_reason(self):
        adv = rank(self.engine, Inputs(stage="Nascent", phase="LATE",
                                       grade="G5"), self.cat, {"owned": {}})
        self.assertFalse(adv.valid)
        self.assertTrue(adv.reason)


if __name__ == "__main__":
    unittest.main()
