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
        # Every 6th fruit is a guaranteed gush, so 6 fruits carry only 5 fruits'
        # worth of gush variance (guaranteed one is deterministic).
        kw = dict(fruit_rank="R3", lvl_culti=10, lvl_quality=10, lvl_gush=10)
        _, v6 = self.e._fruit_stats(base_inputs(fruit_count=6, **kw))
        _, v1 = self.e._fruit_stats(base_inputs(fruit_count=1, **kw))
        self.assertAlmostEqual(v6, 5 * v1, places=6)


class Formatting(unittest.TestCase):
    def test_fmt_days(self):
        self.assertEqual(fmt_days(1.5), "1D 12H 0M")
        self.assertTrue(fmt_days(400).endswith("yr)"))
        self.assertEqual(fmt_days(-1), "0D 0H 0M")


if __name__ == "__main__":
    unittest.main()
