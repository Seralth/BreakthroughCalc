"""Engine regression tests.

The expected values are ground truth: in-game tooltip readings and hand-checked
projections (see closed issues #1/#2). If a refactor changes any of these
numbers, the engine no longer matches the game.
"""

import math
import unittest

from breakthrough_calc.engine import Engine, Inputs, fmt_days


def base_inputs(**kw):
    d = dict(stage="Nascent", phase="LATE", grade="G5",
             culti_speed=57.22, absorption_ratio=0.275)
    d.update(kw)
    return Inputs(**d)


class SpeedModel(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def test_abode_aura_identity(self):
        # Ground truth: 57.22 XP/tick at 27.5% absorption -> 208.07 abode aura,
        # and 208.06 = 130 x 1.60 (Connection..Incarnation base energy).
        r = self.e.calculate(base_inputs())
        self.assertTrue(r.valid, r.error)
        self.assertAlmostEqual(r.abode_aura, 57.22 / 0.275, places=6)
        self.assertAlmostEqual(r.base_xp_per_day, 57.22 * 86400 / 8, places=3)

    def test_speed_from_cultivation_bonus_screen(self):
        # In-game reading 2026-07-05: abode 213.98 x 27.5% = 58.84 (2dp).
        self.assertAlmostEqual(round(213.98 * 0.275, 2), 58.84)

    def test_strive_cancels_out_of_time(self):
        # Same speed at two different absorption ratios (=> different Strive)
        # must give identical projections when no drop-off is modeled.
        a = self.e.calculate(base_inputs(absorption_ratio=0.275))
        b = self.e.calculate(base_inputs(absorption_ratio=0.30))
        self.assertAlmostEqual(a.stage_days, b.stage_days, places=9)

    def test_invalid_inputs_rejected(self):
        self.assertFalse(self.e.calculate(base_inputs(culti_speed=0)).valid)
        self.assertFalse(self.e.calculate(Inputs(stage="Nope")).valid)


class PillTable(unittest.TestCase):
    """Base EXP values confirmed from tooltips at 15.4% pill effect (issue #2)."""

    def setUp(self):
        self.d = Engine().data["pill_xp"]

    def test_confirmed_bases(self):
        gold, purple, blue, mythic = self.d["4R"]
        self.assertEqual((gold, purple, blue, mythic), (60000, 30000, 16000, 120000))
        gold3, purple3, blue3, _ = self.d["3R"]
        self.assertEqual((gold3, purple3, blue3), (22800, 11400, 6080))

    def test_tooltip_reconstruction(self):
        # 4R Legendary: 69.24k (+9,240); 3R Rare: 7,016 (+936); mythic 4R via
        # 1* Vase at 15.4%: 150.48k (+30.48k) with ADDITIVE percentage points.
        self.assertAlmostEqual(60000 * 1.154, 69240)
        self.assertAlmostEqual(6080 * 1.154, 7016.32, places=2)
        self.assertAlmostEqual(120000 * (1 + 0.154 + 0.10), 150480)


class StageXpCurve(unittest.TestCase):
    """Grade XP totals confirmed from in-game progress bars (issue #3)."""

    def setUp(self):
        self.rows = {(r["stage"], r["phase"], r["grade"]): r["grade_xp"]
                     for r in Engine().rows}

    def test_confirmed_grade_totals(self):
        self.assertEqual(self.rows[("Nascent", "LATE", "G5")], 1472337.0)
        self.assertEqual(self.rows[("Nascent", "LATE", "G6")], 1671600.0)
        self.assertEqual(self.rows[("Virtuoso", "MIDDLE", "G2")], 77190.0)
        # Deep-curve rows confirmed EXACT in-game (no correction needed):
        self.assertEqual(self.rows[("Incarnation", "LATE", "G1")], 1483013.0)
        self.assertEqual(self.rows[("Wholeness", "MIDDLE", "G20")], 21644001.0)
        self.assertEqual(self.rows[("Perfection", "LATE", "G20")], 75067764.0)

    def test_cumulative_consistency(self):
        cum = 0.0
        for r in Engine().rows:
            cum += r["grade_xp"]
            self.assertEqual(r["cum_xp"], cum, r["grade"])


class PillMath(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def test_mythic_bonus_stacking(self):
        # Vase 1*, 15.4% pill effect: red pill EXP must be base x 1.254 (additive),
        # not base x 1.154 x 1.10 (multiplicative).
        inp = base_inputs(pill_rank="4R", pill_effect=0.154, vase=True, vase_star="1*")
        pills = self.e._pill_math(inp)
        mythic_each = pills["xp_per_day"] / pills["mythic_per_day"]
        self.assertAlmostEqual(mythic_each, 150480, places=6)

    def test_shared_attempt_pool(self):
        # 10 attempts, 6 gold + 8 purple entered -> 6 gold + 4 purple used.
        inp = base_inputs(pill_rank="4R", pill_limit=10, gold_per_day=6,
                          purple_per_day=8, blue_per_day=5)
        xp = self.e._pill_math(inp)["xp_per_day"]
        self.assertAlmostEqual(xp, 6 * 60000 + 4 * 30000)


class VaseModel(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def pills_per_day(self, **kw):
        return self.e._pill_math(base_inputs(vase=True, **kw))["mythic_per_day"]

    def test_rank_cost_table(self):
        # In-game cost table: 75/82/90/97 for 1R-4R, 100 from 5R on.
        # 3* vase, charge on: energy/day = 96 x 2.0 + 100 = 292.
        for rank, cost in (("1R", 75), ("2R", 82), ("3R", 90), ("4R", 97), ("5R", 100)):
            self.assertAlmostEqual(
                self.pills_per_day(pill_rank=rank, vase_star="3*"), 292 / cost,
                msg=rank)

    def test_quality_discounts(self):
        # Epic -5%, Legendary -20% are baseline Vase behavior.
        blue = self.pills_per_day(pill_rank="5R", vase_star="3*", vase_input="Blue")
        purple = self.pills_per_day(pill_rank="5R", vase_star="3*", vase_input="Purple")
        gold = self.pills_per_day(pill_rank="5R", vase_star="3*", vase_input="Gold")
        self.assertAlmostEqual(purple, blue / 0.95)
        self.assertAlmostEqual(gold, blue / 0.80)

    def test_five_star_expected_cost(self):
        # 5*: 15% chance of zero cost -> expected x0.85. Energy 388 (96x3+100).
        self.assertAlmostEqual(
            self.pills_per_day(pill_rank="5R", vase_star="5*"), 388 / 85.0)

    def test_charge_optional(self):
        with_charge = self.pills_per_day(pill_rank="5R", vase_star="0*")
        without = self.pills_per_day(pill_rank="5R", vase_star="0*", vase_charge=False)
        self.assertAlmostEqual(with_charge - without, 1.0)  # 100 energy / 100 cost


class MirrorModel(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def mythic(self, **kw):
        return self.e._pill_math(
            base_inputs(vase=True, vase_star="0*", mirror=True, **kw))["mythic_per_day"]

    def test_additive_star_skin_discount(self):
        # 5* (-10%) + skin (-10%) -> cost 200 x 0.80 = 160, NOT 200 x 0.9 x 0.9.
        vase_only = self.e._pill_math(
            base_inputs(vase=True, vase_star="0*"))["mythic_per_day"]
        copies = self.mythic(mirror_star="5*", mirror_skin=True) - vase_only
        energy = 96 * 3.0 + 100
        self.assertAlmostEqual(copies, energy / 160.0 * 1.15)

    def test_five_star_extra_copy(self):
        vase_only = self.e._pill_math(
            base_inputs(vase=True, vase_star="0*"))["mythic_per_day"]
        c4 = self.mythic(mirror_star="4*") - vase_only
        c5 = self.mythic(mirror_star="5*") - vase_only
        # Same energy discount tier (-10%) at 4* and 5*; the ratio is the
        # regen difference (energy 388 vs 330.4) times the 5* 15% extra-copy proc.
        self.assertAlmostEqual(c5 / c4, (388 / 330.4) * 1.15)


class PearlModel(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def pearl_xp(self, **kw):
        return self.e._pill_math(
            base_inputs(pearl=True, pearl_xp_per_10=1000, **kw))["pearl_xp_day"]

    def test_flat_twenty_percent_from_one_star(self):
        # 1* + skin: cost floor(10 x 0.85) = 8; energy 224.8 -> 28 uses x 1200.
        self.assertAlmostEqual(
            self.pearl_xp(pearl_star="1*", pearl_skin=True), 33600)
        # bonus stays +20% at 5* (does not grow).
        e5 = 96 * 3.0 + 100                      # 388
        per_use = math.floor(10 * (1 - 0.20))    # -10% star, -10% skin
        expect = math.floor((math.floor(e5 / per_use) * 1000 * 1.2) / 10) * 10
        self.assertAlmostEqual(self.pearl_xp(pearl_star="5*", pearl_skin=True), expect)

    def test_charge_optional(self):
        with_c = self.pearl_xp(pearl_star="1*")
        without = self.pearl_xp(pearl_star="1*", pearl_charge=False)
        self.assertGreater(with_c, without)


class StriveShapes(unittest.TestCase):
    """Tier tables recovered from cfg_us_calc (issue #6)."""

    def test_mature_regime(self):
        from breakthrough_calc.engine import _strive_shape_mature as m
        self.assertEqual(m(65, 3), 0.70 + 0.50)   # the ~120% aged-server cap
        self.assertEqual(m(55, 1), 0.30 + 0.30)
        self.assertEqual(m(45, 0), 0.20)          # same realm as #1, still striving
        self.assertEqual(m(10, 0), 0.0)           # nearly caught up

    def test_young_regime_unchanged(self):
        from breakthrough_calc.engine import _strive_shape as s
        self.assertEqual(s(1), 0.15)
        self.assertEqual(s(9), 0.70)
        self.assertEqual(s(0), 0.0)


class StriveDropoff(unittest.TestCase):
    def test_anchored_at_current_grade(self):
        # With a top-stage set, the CURRENT grade's speed must be unchanged
        # (shape is anchored to the real Strive), so a projection with the
        # drop-off is never faster than without it.
        e = Engine()
        plain = e.calculate(base_inputs(target_stage="Perfection"))
        drop = e.calculate(base_inputs(target_stage="Perfection", top_stage="Nirvana"))
        self.assertTrue(plain.target_valid and drop.target_valid)
        self.assertGreaterEqual(drop.target_days, plain.target_days)


class DailiesDone(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def test_defers_one_day_of_pills(self):
        # Checking "already used today's pills" should push the estimate later
        # by exactly one day's pill XP worth of time (deficit / effective rate).
        kw = dict(pill_rank="4R", pill_limit=10, gold_per_day=2,
                  purple_per_day=4, blue_per_day=4)
        base = self.e.calculate(base_inputs(**kw))
        done = self.e.calculate(base_inputs(dailies_done=True, **kw))
        pill_xp = self.e._pill_math(base_inputs(**kw))["xp_per_day"]
        eff_rate = base.effective_xp_per_day
        self.assertAlmostEqual(done.stage_days - base.stage_days,
                               pill_xp / eff_rate, places=6)
        self.assertGreater(done.stage_days, base.stage_days)

    def test_no_effect_without_pills(self):
        base = self.e.calculate(base_inputs())
        done = self.e.calculate(base_inputs(dailies_done=True))
        self.assertAlmostEqual(base.stage_days, done.stage_days, places=9)

    def test_beneficial_upgrade_never_slower_with_dailies_done(self):
        # Regression: with "already used today's pills", enabling the Vase skin
        # (more pill XP) must never INCREASE the estimate, even for a short
        # near-breakthrough horizon (previously the deficit model perversely did).
        for comp in (0.5, 0.99, 0.999):
            kw = dict(grade="G8", grade_completion=comp, pill_rank="4R", pill_limit=10,
                      gold_per_day=2, purple_per_day=4, blue_per_day=4,
                      vase=True, vase_star="3*", dailies_done=True)
            off = self.e.calculate(base_inputs(**kw, vase_skin=False))
            on = self.e.calculate(base_inputs(**kw, vase_skin=True))
            self.assertLessEqual(on.stage_days, off.stage_days + 1e-9, f"comp={comp}")


class RespiraAndBands(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def test_respira_mean(self):
        r = self.e.calculate(base_inputs(respira_per_day=20, respira_exp=5000))
        self.assertAlmostEqual(r.respira_xp_per_day, 20 * 5000 * 1.8)  # crit mean 1.8

    def test_band_collapses_without_crit_sources(self):
        r = self.e.calculate(base_inputs(pill_rank="4R", pill_limit=10, gold_per_day=2))
        self.assertEqual(r.stage_band, (r.stage_days, r.stage_days))

    def test_band_brackets_estimate(self):
        r = self.e.calculate(base_inputs(respira_per_day=20, respira_exp=5000))
        lo, hi = r.stage_band
        self.assertLess(lo, r.stage_days)
        self.assertGreater(hi, r.stage_days)
        self.assertAlmostEqual(r.stage_days - lo, hi - r.stage_days, places=6)  # symmetric

    def test_fruit_variance_positive(self):
        _, var = self.e._fruit_stats(base_inputs(
            fruit_rank="R3", fruit_count=50, lvl_culti=10, lvl_quality=10, lvl_gush=10))
        self.assertGreater(var, 0)

    def test_gush_guarantee_reduces_variance(self):
        # The soft pity (gush guaranteed within 6 of the last gush) truncates
        # long miss streaks, so 6 fruits carry LESS gush variance than 6
        # independent Bernoulli fruits.
        kw = dict(fruit_rank="R3", lvl_culti=10, lvl_quality=10, lvl_gush=10)
        _, v6 = self.e._fruit_stats(base_inputs(fruit_count=6, **kw))
        _, v1 = self.e._fruit_stats(base_inputs(fruit_count=1, **kw))
        self.assertLess(v6, 6 * v1)
        self.assertGreater(v6, 0)


class FruitQualityDistribution(unittest.TestCase):
    """The tier probabilities (quality level + extractor) must form a true
    distribution, and a rarer extractor must never lower the projection."""

    def setUp(self):
        self.e = Engine()

    def tier_probs(self, lvl_quality, rarity):
        qual = self.e.data["fruit_levels"][str(lvl_quality)]["quality"]
        ext = self.e.data["extractor_chance"][rarity]
        residual = max(0.0, 1.0 - sum(qual))
        ext_tot = sum(ext)
        return [q + (x / ext_tot * residual if ext_tot > 0 else 0.0)
                for q, x in zip(qual, ext)]

    def test_probability_mass_is_one_for_all_combos(self):
        for lvl in range(31):
            for rarity in self.e.data["extractor_chance"]:
                self.assertAlmostEqual(
                    sum(self.tier_probs(lvl, rarity)), 1.0, places=9,
                    msg=f"lvl {lvl} + {rarity}")

    def test_better_extractor_never_lowers_mean(self):
        order = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
        kw = dict(fruit_rank="R8", fruit_count=10, lvl_culti=20, lvl_gush=20)
        for lvl in (0, 5, 10, 11, 20, 30):
            means = [self.e._fruit_stats(base_inputs(
                lvl_quality=lvl, extractor_rarity=r, **kw))[0] for r in order]
            for a, b in zip(means, means[1:]):
                self.assertLessEqual(a, b + 1e-9, msg=f"lvl {lvl}: {means}")


class ScreenshotGroundTruth2026_07_07(unittest.TestCase):
    """Pinned to in-game readings (Incarnation (L) Middle G1, extractor at
    Mortal World rank Epic, tracks Culti 20 / Quality 15 / Gush 14)."""

    def setUp(self):
        self.e = Engine()
        self.fl = self.e.data["fruit_levels"]

    def test_culti_bonus_is_4pct_per_level(self):
        # Upgrade panel: "Crafting yields 80% Aura Orb cultivation. (+4%)" at Lv20.
        self.assertAlmostEqual(self.fl["20"]["culti_xp"], 0.80)
        for lvl in range(31):
            self.assertAlmostEqual(self.fl[str(lvl)]["culti_xp"], 0.04 * lvl)

    def test_gush_track_readings(self):
        # Stats panel at Gush 14: trigger rate 20.0% (pity listed separately),
        # gush orbs +206% EXP; intro: base multiplier 150%.
        self.assertAlmostEqual(self.fl["14"]["gush_chance"], 0.20)
        self.assertAlmostEqual(self.fl["14"]["gush_xp"], 2.06)
        self.assertAlmostEqual(self.fl["0"]["gush_xp"], 1.5)

    def test_orb_quality_distribution_matches_extractor_panel(self):
        # Quality 15 + Epic extractor -> Blue 70 / Purple 30 (sums to 100).
        qual = self.fl["15"]["quality"]
        ext = self.e.data["extractor_chance"]["Epic"]
        residual = 1.0 - sum(qual)
        p = [q + x / sum(ext) * residual for q, x in zip(qual, ext)]
        self.assertAlmostEqual(p[2], 0.70)
        self.assertAlmostEqual(p[3], 0.30)
        self.assertAlmostEqual(sum(p), 1.0)

    def test_pity_gushes_add_to_mean(self):
        # Soft pity (observed 2026-07-10): any gush resets the "guaranteed in
        # x6" counter, so the 6th fruit gushes for sure only if the first 5
        # all missed; otherwise it rolls gc like any other fruit.
        kw = dict(fruit_rank="R8", lvl_culti=20, lvl_quality=15, lvl_gush=14,
                  extractor_rarity="Epic")
        m6, _ = self.e._fruit_stats(base_inputs(fruit_count=6, **kw))
        m5, _ = self.e._fruit_stats(base_inputs(fruit_count=5, **kw))
        m1, _ = self.e._fruit_stats(base_inputs(fruit_count=1, **kw))
        gc = self.fl["14"]["gush_chance"]
        gxm = self.fl["14"]["gush_xp"]
        per_fruit = m1 / (1 + gc * (gxm - 1))  # base * E[quality factor]
        p6 = (1 - gc) ** 5 + (1 - (1 - gc) ** 5) * gc  # gush prob on fruit 6
        self.assertAlmostEqual(m6, m5 + per_fruit * (1 + p6 * (gxm - 1)),
                               places=6)

    def test_gush_multiplier_keyed_by_gush_level(self):
        # Raising the Gush track (not the Culti track) must raise the payout.
        kw = dict(fruit_rank="R8", fruit_count=5, lvl_culti=20, lvl_quality=15,
                  extractor_rarity="Epic")
        lo, _ = self.e._fruit_stats(base_inputs(lvl_gush=0, **kw))
        hi, _ = self.e._fruit_stats(base_inputs(lvl_gush=14, **kw))
        self.assertGreater(hi, lo)

    def test_gem_does_not_multiply_pill_xp(self):
        # Aura Gem is claimable storage of gem% x cultivation speed; pills are
        # flat XP. Effective rate must be base*(1+gem) + daily, not
        # base*(1+gem)*(1+pills).
        kw = dict(pill_rank="4R", pill_limit=10, gold_per_day=2,
                  purple_per_day=4, blue_per_day=4, pill_effect=0.154)
        r = self.e.calculate(base_inputs(aura_gem="Mythic", **kw))
        expected = r.base_xp_per_day * 1.28 + r.pill_xp_per_day
        self.assertAlmostEqual(r.effective_xp_per_day, expected, places=6)

    def test_orb_exp_boost_gated_by_extractor_rank(self):
        # Epic rank boosts Uncommon..Epic orb tiers by +20%; a Common extractor
        # boosts nothing. At quality 0 (all-Common orbs) rarity Epic vs Common
        # must differ only via the residual fill, which is zero at quality<=10.
        kw = dict(fruit_rank="R8", fruit_count=5, lvl_culti=20, lvl_gush=14)
        m_c, _ = self.e._fruit_stats(base_inputs(
            lvl_quality=0, extractor_rarity="Common", **kw))
        m_e, _ = self.e._fruit_stats(base_inputs(
            lvl_quality=0, extractor_rarity="Epic", **kw))
        self.assertAlmostEqual(m_c, m_e, places=6)  # tier 0 gets no +20% either way


class InputHardening(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def test_grade_completion_clamped(self):
        # completion > 1 must behave exactly like 100%, not go negative.
        over = self.e.calculate(base_inputs(grade_completion=2.5))
        full = self.e.calculate(base_inputs(grade_completion=1.0))
        self.assertTrue(over.valid)
        self.assertAlmostEqual(over.stage_days, full.stage_days, places=9)

    def test_negative_strive_disables_dropoff(self):
        # Absorption below the base band implies strive < 0; drop-off must not
        # engage (a negative scale would make speeds RISE toward #1).
        cur = base_inputs()
        low = self.e.rows[self.e.row_index(cur.stage, cur.phase, cur.grade)]["low"]
        neg = base_inputs(absorption_ratio=low * 0.9, top_stage="Incarnation")
        plain = base_inputs(absorption_ratio=low * 0.9)
        a = self.e.calculate(neg)
        b = self.e.calculate(plain)
        self.assertAlmostEqual(a.stage_days, b.stage_days, places=9)


class ResetTiming(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    KW = dict(pill_rank="4R", pill_limit=10, gold_per_day=2, purple_per_day=4,
              blue_per_day=4, pill_effect=0.154, respira_per_day=20,
              respira_exp=5000, respira_event=5)

    def test_zero_hours_to_reset_equals_dailies_not_done(self):
        a = self.e.calculate(base_inputs(dailies_done=True, reset_in_hours=0.0, **self.KW))
        b = self.e.calculate(base_inputs(dailies_done=False, **self.KW))
        self.assertAlmostEqual(a.stage_days, b.stage_days, places=9)

    def test_shorter_reset_never_slower(self):
        prev = None
        for h in (24.0, 12.0, 6.0, 0.0):
            r = self.e.calculate(base_inputs(dailies_done=True, reset_in_hours=h, **self.KW))
            if prev is not None:
                self.assertLessEqual(r.stage_days, prev + 1e-9, msg=f"reset {h}h")
            prev = r.stage_days

    def test_event_respira_deferred_with_dailies_done(self):
        # With dailies done, event attempts wait for the reset: on a horizon
        # shorter than the reset window they must not help at all.
        base = dict(stage="Nascent", phase="LATE", grade="G8",
                    grade_completion=0.95, culti_speed=57.22,
                    absorption_ratio=0.275, dailies_done=True,
                    reset_in_hours=24.0)
        with_event = self.e.calculate(Inputs(**base, respira_exp=5000, respira_event=50))
        without = self.e.calculate(Inputs(**base, respira_exp=5000))
        if with_event.phase_days < 1.0:   # finishes inside the reset window
            self.assertAlmostEqual(with_event.phase_days, without.phase_days, places=9)


class DataConsistency(unittest.TestCase):
    def test_star_cost_column_matches_energy_discount(self):
        # star[k][1] and artifact_energy_discount encode the same fact
        # (mirror copy cost = 200 x (1 - disc%)); keep them from drifting.
        e = Engine()
        for k, disc in e.data["artifact_energy_discount"].items():
            self.assertEqual(e.data["star"][k][1], 200 * (100 - disc) / 100,
                             msg=f"star[{k}][1] disagrees with discount {disc}%")


class Formatting(unittest.TestCase):
    def test_fmt_days(self):
        self.assertEqual(fmt_days(1.5), "1D 12H 0M")
        self.assertTrue(fmt_days(400).endswith("yr)"))
        self.assertEqual(fmt_days(-1), "0D 0H 0M")


if __name__ == "__main__":
    unittest.main()
