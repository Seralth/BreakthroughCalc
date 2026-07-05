"""Breakthrough calculator engine.

A clean reimplementation of "Donk's Breakthrough calc V4.1" (Google Sheets).
The spreadsheet model, verified against its own "speed checker" cell:

- Cultivation ticks every 8 seconds (one "Cosmoapsis"); "cultivation speed"
  (user input) is the XP gained per Cosmoapsis at the CURRENT grade.
- Each (stage, phase, grade) row has an aura ratio band [low, high].
  The player's "absorption ratio" input equals low(current) + bonus, where
  bonus (from gear etc.) stays constant as they progress.
- Implied abode aura = culti_speed / absorption_ratio, so the speed while
  cultivating any future grade r is:
      speed(r) = abode * (low_r + bonus) = culti_speed * (low_r + bonus) / absorption_ratio
  (At the current grade this reduces exactly to culti_speed — the sheet's
  "speed checker" asserts the same identity.)
- Aura gem and pill usage act as parallel speed-up ratios: time /(1+gem)/(1+pills)
  where pills = (daily pill XP / culti_speed * 8s) expressed as days/day.
- Fruit XP is a one-time XP credit applied up-front.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

TICK_SECONDS = 8.0

# Respira crit roll (cfg_us_calc yunqi_crit): multiplier x weight/1000.
_RESPIRA_CRIT = ((1, 0.60), (2, 0.30), (5, 0.08), (10, 0.02))
_RESPIRA_CRIT_MEAN = sum(m * p for m, p in _RESPIRA_CRIT)          # 1.8
_RESPIRA_CRIT_VAR = sum(p * m * m for m, p in _RESPIRA_CRIT) - _RESPIRA_CRIT_MEAN ** 2  # 2.56
# z for a ~90% central interval (P5..P95), the "best/worst" band.
_BAND_Z = 1.645

# Fruit pity: every Nth fruit is a guaranteed gush (deterministic, no variance).
GUSH_GUARANTEE_EVERY = 6

# Strive tier tables recovered from the client config (cfg_us_calc).
# Young servers (world level < 30) use a major-realm-gap table; mature servers
# (world level >= 30, the common case) use a minor-LEVEL-gap table plus an
# additive major-realm bonus — 70% + 50% = the ~120% cap seen on aged servers.
# Only the SHAPE is used; magnitude is anchored to the player's real Strive
# (the live value is server-computed hourly and unknowable client-side).
_STRIVE_SHAPE = {1: 0.15, 2: 0.20, 3: 0.30, 4: 0.40, 5: 0.50, 6: 0.60, 7: 0.70}

# (min level gap, tier) — new_sub_lv_exp_accelerate_array, world level >= 30
_STRIVE_SUB_SHAPE = ((60, 0.70), (50, 0.30), (40, 0.20))
# major-realm-gap additive bonus — extra_rank_accelerate_array
_STRIVE_EXTRA_RANK = {1: 0.30, 2: 0.50}


def _strive_shape(gap: int) -> float:
    if gap <= 0:
        return 0.0
    if gap >= 7:
        return 0.70
    return _STRIVE_SHAPE[gap]


def _strive_shape_mature(level_gap: int, major_gap: int) -> float:
    """Mature-server (world >= 30) Strive tier: minor-level-gap tier plus the
    additive major-realm bonus. level_gap counts grades (levels) to #1."""
    sub = next((p for g, p in _STRIVE_SUB_SHAPE if level_gap >= g), 0.0)
    extra = 0.0
    if major_gap >= 2:
        extra = _STRIVE_EXTRA_RANK[2]
    elif major_gap == 1:
        extra = _STRIVE_EXTRA_RANK[1]
    return sub + extra

import sys

if getattr(sys, "frozen", False):
    _BASE = sys._MEIPASS  # PyInstaller bundle
else:
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BASE, "data", "breakthrough.json")


def load_data(path: str | None = None) -> dict:
    with open(path or _DATA_PATH) as f:
        return json.load(f)


def load_pill_sources() -> list:
    """Catalog of known Cultivation Pill Effect sources (recovered from game
    data) for the GUI picker. Missing file just means no catalog."""
    try:
        with open(os.path.join(_BASE, "data", "pill_effect_sources.json")) as f:
            return json.load(f)
    except OSError:
        return []


@dataclass
class Inputs:
    stage: str = "Novice"
    phase: str = "N/A"          # N/A / EARLY / MIDDLE / LATE
    grade: str = "N/A"          # N/A / F1.. / G1..
    grade_completion: float = 0.0   # 0..1 fraction of current grade done
    culti_speed: float = 0.0        # XP per 8s tick
    absorption_ratio: float = 0.0   # e.g. 0.017 for 1.7%
    aura_gem: str = "None"
    target_stage: str = ""          # for "time until future stage"
    top_stage: str = ""             # server #1's Stage; enables Strive drop-off projection
    mature_server: bool = True      # world level >= 30: minor-gap tiers + extra-rank bonus
    dailies_done: bool = False      # today's daily pills/respira already used; defer to next reset

    # Respira (daily cultivation exercise). Each attempt grants base EXP times a
    # crit roll: x1/x2/x5/x10 at 60/30/8/2% (mean 1.8, from client config).
    respira_per_day: float = 0.0    # daily attempt limit (base + permanent bonuses)
    respira_event: float = 0.0      # one-off extra attempts today (event/item)
    respira_exp: float = 0.0        # base (non-crit) EXP per attempt, from tooltip

    # Pills
    pill_rank: str = "1R"
    pill_effect: float = 0.0        # "Cultivation pill effect" as a fraction (0.05 = +5%)
    pill_limit: float = 0.0         # daily pill limit
    gold_per_day: float = 0.0
    purple_per_day: float = 0.0
    blue_per_day: float = 0.0
    mark_blue: float = 0.0          # star marks (bonus XP ratios)
    mark_purple: float = 0.0
    mark_gold: float = 0.0

    # Creation artifacts
    vase: bool = False
    vase_star: str = "0*"
    vase_skin: bool = False
    vase_input: str = "Blue"        # pill quality fed to the Vase: Blue / Purple / Gold
    mirror: bool = False
    mirror_star: str = "0*"
    mirror_skin: bool = False
    pearl: bool = False
    pearl_star: str = "0*"
    pearl_skin: bool = False
    pearl_xp_per_10: float = 0.0    # "EXP for 10 Energy" input
    # Daily 100-energy charge (30 Fateum/Destium, once per day, per artifact)
    vase_charge: bool = True
    mirror_charge: bool = True
    pearl_charge: bool = True

    # Fruit magic
    fruit_rank: str = "R3"
    fruit_count: float = 0.0
    fruit_highest_rank: bool = False
    lvl_culti: int = 0
    lvl_quality: int = 0
    lvl_gush: int = 0
    extractor_rarity: str = "Common"


@dataclass
class Results:
    valid: bool = False
    error: str = ""
    phase_days: float = 0.0        # time until end of current phase (w/ pills+fruit)
    stage_days: float = 0.0        # time until end of current stage
    target_days: float = 0.0       # time until start of target stage
    target_valid: bool = False
    abode_aura: float = 0.0
    strive: float = 0.0                 # implied Strive Bonus (multiplier, e.g. 0.30 = +30%)
    base_xp_per_day: float = 0.0        # culti_speed at the current grade, per day
    effective_xp_per_day: float = 0.0   # base with gem + pill speed-ups applied
    pill_xp_per_day: float = 0.0
    pill_speedup: float = 0.0      # ratio (E17)
    gem_speedup: float = 0.0
    mythic_pills_per_day: float = 0.0
    pearl_xp_per_day: float = 0.0
    respira_xp_per_day: float = 0.0
    fruit_xp: float = 0.0
    fruit_days_saved: float = 0.0
    # 90% (P5..P95) time bands from fruit/respira crit variance: (low, high).
    phase_band: tuple = (0.0, 0.0)
    stage_band: tuple = (0.0, 0.0)
    target_band: tuple = (0.0, 0.0)
    breakdown: dict = field(default_factory=dict)


class Engine:
    def __init__(self, data: dict | None = None):
        self.data = data or load_data()
        self.rows = self.data["rows"]

    # ---- data helpers -------------------------------------------------
    def stages(self) -> list[str]:
        out = []
        for r in self.rows:
            if r["stage"] not in out:
                out.append(r["stage"])
        return out

    def phases_for(self, stage: str) -> list[str]:
        out = []
        for r in self.rows:
            if r["stage"] == stage and r["phase"] not in out:
                out.append(r["phase"])
        return out

    def grades_for(self, stage: str, phase: str) -> list[str]:
        return [r["grade"] for r in self.rows if r["stage"] == stage and r["phase"] == phase]

    def row_index(self, stage: str, phase: str, grade: str) -> int:
        for i, r in enumerate(self.rows):
            if r["stage"] == stage and r["phase"] == phase and r["grade"] == grade:
                return i
        return -1

    def stage_start_index(self, stage: str) -> int:
        for i, r in enumerate(self.rows):
            if r["stage"] == stage:
                return i
        return -1

    # ---- pills ---------------------------------------------------------
    def _pill_math(self, inp: Inputs) -> dict:
        gold, purple, blue, mythic = self.data["pill_xp"].get(inp.pill_rank, [0, 0, 0, 0])
        plus_ratio = inp.pill_effect
        star = self.data["star"]
        disc = self.data["artifact_energy_discount"]
        # Mirror copies inherit the copied pill's own EXP bonus (copyable mythic
        # pills are gated to match the Vase's unlocked bonus tiers), so only the
        # Vase's star bonus and skin apply to mythic pill XP.
        vase_adder = star.get(inp.vase_star, [1, 200, 0])[2] if inp.vase else 0.0

        gold_xp = (1 + plus_ratio + inp.mark_gold) * gold
        purple_xp = (1 + plus_ratio + inp.mark_purple) * purple
        blue_xp = (1 + plus_ratio + inp.mark_blue) * blue
        mythic_xp = (1 + plus_ratio + vase_adder + (0.08 if inp.vase_skin else 0)) * mythic

        # Each artifact regenerates its own energy: 1 per 15 min scaled by the
        # star recovery multiplier, plus (optionally) that artifact's paid
        # daily charge of 100 energy (30 Fateum/Destium, once per day).
        def energy_day(star_key: str, charged: bool) -> float:
            rec = star.get(star_key, [1, 200, 0])[0]
            return (1440 / 15) * rec + (100 if charged else 0)

        # Vase mythic pills/day. Base refine cost depends on the pill's rank
        # (in-game readings: 75/82/90/97 for 1R-4R, 100 from 5R on). The
        # input-quality discount (Epic -5%, Legendary -20%) is baseline Vase
        # behavior, and the 5* effect is a 15% chance to consume NO energy,
        # so expected cost is a further x0.85.
        vase_pills = 0.0
        if inp.vase:
            base_cost = self.data.get("vase_energy_cost", {}).get(inp.pill_rank, 100)
            quality_disc = {"Gold": 0.20, "Purple": 0.05}.get(inp.vase_input, 0.0)
            cost = base_cost * (1 - quality_disc) * (0.85 if inp.vase_star == "5*" else 1.0)
            vase_pills = energy_day(inp.vase_star, inp.vase_charge) / cost
        mirror_pills = 0.0
        if inp.vase and inp.mirror:
            # Star and skin energy discounts stack ADDITIVELY (the game applies
            # one (1 - (star% + skin%)/100) factor to the 200 base cost).
            d = disc.get(inp.mirror_star, 0) + (10 if inp.mirror_skin else 0)
            cost = 200 * (1 - d / 100)
            copies = energy_day(inp.mirror_star, inp.mirror_charge) / max(1e-9, cost)
            if inp.mirror_star == "5*":
                copies *= 1.15  # 5*: 15% chance of an extra copy per Duplication
            mirror_pills = copies + vase_pills
        mythic_per_day = mirror_pills if (inp.vase and inp.mirror) else vase_pills

        # Pearl: uses/day * XP per use ("EXP for 10 Energy" tooltip input).
        # Star bonus is flat +20% from 1* (it does not grow at higher stars);
        # star/skin discounts reduce the 10-energy cost per use additively.
        pearl_xp_day = 0.0
        if inp.pearl:
            d = disc.get(inp.pearl_star, 0) + (10 if inp.pearl_skin else 0)
            per_use = max(1, math.floor(10 * (1 - d / 100)))
            uses = math.floor(energy_day(inp.pearl_star, inp.pearl_charge) / per_use)
            star_n = int(inp.pearl_star[0]) if inp.pearl_star[:1].isdigit() else 0
            pearl_xp_day = math.floor((uses * inp.pearl_xp_per_10 * (1.2 if star_n >= 1 else 1.0)) / 10) * 10

        # In-game the daily pill limit is a SHARED attempt pool across all
        # cultivation pills (vase red/mythic pills are exempt). Allocate the
        # shared limit highest-XP-first: gold > purple > blue. For a valid
        # distribution (gold+purple+blue <= limit) this equals per-color caps;
        # it only bites when the entered counts exceed the shared limit.
        rem = inp.pill_limit
        used_gold = min(inp.gold_per_day, rem); rem -= used_gold
        used_purple = min(inp.purple_per_day, rem); rem -= used_purple
        used_blue = min(inp.blue_per_day, rem); rem -= used_blue

        total_xp_day = (mythic_per_day * mythic_xp + used_gold * gold_xp
                        + used_purple * purple_xp + used_blue * blue_xp + pearl_xp_day)
        return {
            "xp_per_day": total_xp_day,
            "mythic_per_day": mythic_per_day,
            "pearl_xp_day": pearl_xp_day,
        }

    # ---- fruits ----------------------------------------------------------
    def _fruit_stats(self, inp: Inputs) -> tuple[float, float]:
        """(mean XP, variance) for a fruit batch. Each fruit independently rolls
        a gush (the crit) and a quality tier, so the batch total is a sum of
        i.i.d. per-fruit XP — mean and variance both scale with the count."""
        if inp.fruit_count <= 0:
            return 0.0, 0.0
        base = self.data["fruit_xp"].get(inp.fruit_rank, 0)
        if inp.fruit_highest_rank:
            base *= 1.5
        lv = self.data["fruit_levels"]
        l_gush = lv[str(max(0, min(30, inp.lvl_gush)))]
        l_culti = lv[str(max(0, min(30, inp.lvl_culti)))]
        l_qual = lv[str(max(0, min(30, inp.lvl_quality)))]

        gc = l_gush["gush_chance"]
        gxm = l_culti["gush_xp"]                    # sheet looks GushXP up by culti level
        # The fruit "crit" is the gush: a gushed fruit's XP is x gxm instead of x1.
        # Mean gush factor (gush rate gc is the calibrated total, guarantees
        # included) — the mean is left exactly as Donk's sheet.
        e_gush = (1 - gc) + gc * gxm

        culti_mult = 1 + l_culti["culti_xp"]
        ext = self.data["extractor_chance"].get(inp.extractor_rarity, [1, 0, 0, 0, 0, 0])
        thresholds = [1, 6, 11, 16, 21, 26]
        # Expected quality factor (treated as deterministic — the data models it
        # as an aggregate, not a single-tier draw, so only gush drives variance).
        e_q = 0.0
        for i, qmult in enumerate(self.data["quality_mult"]):
            p = min(1.0, l_qual["quality"][i] + ext[i])
            e_q += p * (culti_mult + (0.2 if inp.lvl_culti >= thresholds[i] else 0.0)) * qmult

        n = inp.fruit_count
        mean = base * n * e_gush * e_q
        # Variance: every 6th fruit is a GUARANTEED gush (pity) and carries no
        # randomness, so only the other (n - n//6) fruits contribute Bernoulli
        # gush variance — this narrows the band by ~5/6. The mean is unchanged
        # (still the calibrated n*gc gush rate).
        g = int(n) // GUSH_GUARANTEE_EVERY
        var_gush_count = (n - g) * gc * (1 - gc)
        var_total = (base * e_q) ** 2 * (gxm - 1) ** 2 * var_gush_count
        return mean, var_total

    # ---- main calc -------------------------------------------------------
    def calculate(self, inp: Inputs) -> Results:
        res = Results()
        idx = self.row_index(inp.stage, inp.phase, inp.grade)
        if idx < 0:
            res.error = "Select a valid stage / phase / grade."
            return res
        if inp.culti_speed <= 0 or inp.absorption_ratio <= 0:
            res.error = "Cultivation speed and absorption ratio must be > 0."
            return res

        cur = self.rows[idx]
        abode = inp.culti_speed / inp.absorption_ratio
        # Strive is a MULTIPLIER on each stage's base absorption (game formula:
        # Absorption = Base x (1 + Strive)), held constant across the projection.
        # NOTE: because abode = culti_speed/absorption and (1+strive) =
        # absorption/low_cur, strive/absorption CANCEL out of speed(row) below:
        # speed(row) = culti_speed * low_row / low_cur. So the entered absorption
        # (and thus strive) does NOT affect the projected TIME at all — time is
        # driven purely by culti_speed and the base-band progression. strive is
        # retained only to expose the implied value for display. This is also
        # why the "no strive on overcapped XP" restriction and the Nascent-Soul
        # unlock are immaterial to the time math: strive never scales it.
        strive = inp.absorption_ratio / cur["low"] - 1 if cur["low"] > 0 else 0.0
        gem = self.data["gem_bonus"].get(inp.aura_gem, 0.0)

        pills = self._pill_math(inp)
        # Respira: mean daily XP = attempts x base x 1.8 (crit mean). Event
        # attempts are a one-off, credited up front like fruit.
        respira_daily = inp.respira_per_day * inp.respira_exp * _RESPIRA_CRIT_MEAN
        respira_event_xp = inp.respira_event * inp.respira_exp * _RESPIRA_CRIT_MEAN
        daily_xp = pills["xp_per_day"] + respira_daily
        pill_ratio = (daily_xp / inp.culti_speed) * TICK_SECONDS / 86400.0
        fruit_mean, fruit_var = self._fruit_stats(inp)
        fruit_xp = fruit_mean + respira_event_xp

        # Crit variance for the best/worst band. Fruit + event attempts are
        # up-front lumps; daily respira accumulates over the projection horizon.
        # var per attempt = base^2 * crit_var; independent, so counts add.
        exp2 = inp.respira_exp * inp.respira_exp * _RESPIRA_CRIT_VAR
        var_upfront = fruit_var + inp.respira_event * exp2
        var_daily = inp.respira_per_day * exp2      # per day of projection

        # Optional Strive drop-off: if server #1's Stage is given and you're
        # behind them, Strive steps DOWN as you climb major realms toward #1
        # (gap shrinks). Anchored to your real current Strive via _strive_shape,
        # so at the current grade it's unchanged; it fades to 0 at #1's realm.
        # Without this, Strive is held constant (and cancels out of the time).
        stage_order = self.stages()
        strive_of = None
        if inp.top_stage in stage_order and inp.stage in stage_order:
            top_i = stage_order.index(inp.top_stage)
            cur_gap = top_i - stage_order.index(inp.stage)
            # #1's exact grade is unknown; approximate them at the start of
            # their Stage for the level-gap count (mature-server regime).
            top_row = self.stage_start_index(inp.top_stage)
            stage_idx = {s: i for i, s in enumerate(stage_order)}
            row_idx = {id(r): i for i, r in enumerate(self.rows)}

            def shape_at(row_i: int, row_stage: str) -> float:
                major = top_i - stage_idx.get(row_stage, top_i)
                if inp.mature_server:
                    return _strive_shape_mature(top_row - row_i, major)
                return _strive_shape(major)

            cur_shape = shape_at(idx, inp.stage)
            if cur_gap > 0 and cur_shape > 0:
                scale = strive / cur_shape
                def strive_of(row):
                    return scale * shape_at(row_idx[id(row)], row["stage"])

        def speed(row) -> float:
            s = strive_of(row) if strive_of else strive
            return max(1e-12, abode * row["low"] * (1 + s))

        # `xp_seconds` is base cultivation-seconds (raw_seconds); gem and pills
        # are applied here as speed-ups. If today's dailies are already spent,
        # the FIRST real day runs at base speed (pills deferred, gem still
        # applies) and the daily rate resumes after — a proper piecewise model
        # so a stronger daily setup never perversely increases a short estimate.
        _base_day = 86400.0 * (1 + gem)   # base-seconds covered in 1 real day, no pills

        def days(xp_seconds: float) -> float:
            full = (1 + gem) * (1 + pill_ratio)
            if not inp.dailies_done:
                return xp_seconds / 86400.0 / full
            if xp_seconds <= _base_day:
                return xp_seconds / 86400.0 / (1 + gem)
            return 1.0 + (xp_seconds - _base_day) / 86400.0 / full

        start_credit = fruit_xp

        # seconds of cultivation from "now" through the end of row j (inclusive),
        # with the starting credit applied against the earliest remaining XP.
        def raw_seconds(upto: int) -> float:
            credit = start_credit
            total = 0.0
            remaining_cur = cur["grade_xp"] * (1 - inp.grade_completion)
            for j in range(idx, upto + 1):
                xp = remaining_cur if j == idx else self.rows[j]["grade_xp"]
                take = min(credit, xp)
                credit -= take
                total += (xp - take) / speed(self.rows[j]) * TICK_SECONDS
            return total

        # end of current phase
        pend = idx
        while pend + 1 < len(self.rows) and self.rows[pend + 1]["stage"] == inp.stage \
                and self.rows[pend + 1]["phase"] == inp.phase:
            pend += 1
        # end of current stage
        send = pend
        while send + 1 < len(self.rows) and self.rows[send + 1]["stage"] == inp.stage:
            send += 1

        eff_per_day = inp.culti_speed * (86400.0 / TICK_SECONDS) * (1 + gem) * (1 + pill_ratio)

        def band(t_days: float) -> tuple:
            # Cumulative-XP SD at the point estimate, mapped to a time spread by
            # the effective daily rate. Up-front lump variance + daily respira
            # variance accrued over the horizon. z*SD gives the P5..P95 edges.
            if eff_per_day <= 0 or (var_upfront <= 0 and var_daily <= 0):
                return (t_days, t_days)
            var_xp = var_upfront + var_daily * max(0.0, t_days)
            sd_days = (var_xp ** 0.5) / eff_per_day
            return (max(0.0, t_days - _BAND_Z * sd_days), t_days + _BAND_Z * sd_days)

        res.phase_days = days(raw_seconds(pend))
        res.stage_days = days(raw_seconds(send))
        res.phase_band = band(res.phase_days)
        res.stage_band = band(res.stage_days)

        if inp.target_stage and inp.target_stage != inp.stage:
            tstart = self.stage_start_index(inp.target_stage)
            if tstart > idx:
                res.target_days = days(raw_seconds(tstart - 1))
                res.target_band = band(res.target_days)
                res.target_valid = True
            elif tstart >= 0:
                res.error = "Target stage precedes current stage."

        # fruit time saved at current speed
        fruit_secs = fruit_xp / inp.culti_speed * TICK_SECONDS if inp.culti_speed else 0.0

        res.valid = True
        res.abode_aura = abode
        res.strive = strive
        res.base_xp_per_day = inp.culti_speed * (86400.0 / TICK_SECONDS)
        res.effective_xp_per_day = res.base_xp_per_day * (1 + gem) * (1 + pill_ratio)
        res.pill_xp_per_day = pills["xp_per_day"]
        res.pill_speedup = pill_ratio
        res.gem_speedup = gem
        res.mythic_pills_per_day = pills["mythic_per_day"]
        res.pearl_xp_per_day = pills["pearl_xp_day"]
        res.respira_xp_per_day = respira_daily
        res.fruit_xp = fruit_xp
        # Matches Donk's sheet (myrfruits B45/B46): fruit XP / current speed, no gem/pill divisor.
        res.fruit_days_saved = fruit_secs / 86400.0
        return res


def fmt_days(d: float) -> str:
    if d < 0:
        d = 0
    total_min = int(d * 24 * 60)
    out = f"{total_min // 1440}D {total_min % 1440 // 60}H {total_min % 60}M"
    if d > 365:
        out += f"  (~{d / 365.25:.1f} yr)"
    return out
