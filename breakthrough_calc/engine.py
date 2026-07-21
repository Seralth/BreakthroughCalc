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
- Aura gem multiplies cultivation speed only (in-game it is claimable storage
  that accrues gem% of your cultivation speed, up to 18-32h per claim — treated
  as continuous). Pills/Respira are FLAT daily XP added on top, verified
  in-game 2026-07-07: the pill panel shows each pill as both absolute XP and
  the exact percentage of the current grade's XP. Per-row:
      rate(row) = speed(row) * (1+gem) / 8s  +  daily_xp / 86400   [XP/sec]
  (Donk's sheet instead used time /(1+gem)/(1+pills) with pills frozen at the
  current grade's speed — optimistic on long projections and wrongly gem-boosted.)
- Fruit XP is a one-time XP credit applied up-front.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Re-exported for compatibility: data loading lives in data_io (the GUI and
# tests import these names from here).
from .data_io import (  # noqa: F401
    _load_catalog,
    load_data,
    load_pill_sources,
    load_respira_sources,
)

TICK_SECONDS = 8.0

# Respira crit roll (cfg_us_calc yunqi_crit): multiplier x weight/1000.
_RESPIRA_CRIT = ((1, 0.60), (2, 0.30), (5, 0.08), (10, 0.02))
_RESPIRA_CRIT_MEAN = sum(m * p for m, p in _RESPIRA_CRIT)          # 1.8
_RESPIRA_CRIT_VAR = sum(p * m * m for m, p in _RESPIRA_CRIT) - _RESPIRA_CRIT_MEAN ** 2  # 2.56

# Respira per-attempt BASE XP is one server-side constant per major Stage;
# the on-screen value is base x (1 + Respira Effect books %) (resolved
# 2026-07-15 from two-account readings, game-mechanics-verified.md).
_RESPIRA_BASE = {"Nascent": 3157.0, "Incarnation": 6385.0}
# Unmeasured Stages are extrapolated by the measured Nascent->Incarnation
# ratio (2.02249); each extrapolated step carries model risk ~1%.
_RESPIRA_STAGE_RATIO = _RESPIRA_BASE["Incarnation"] / _RESPIRA_BASE["Nascent"]
# z for a ~90% central interval (P5..P95), the "best/worst" band.
_BAND_Z = 1.645

# Fruit pity: a gush is guaranteed within N fruits of the last gush (SOFT
# pity — any gush resets the counter; observed in-game 2026-07-10: a random
# gush on the 5th fruit reset the "guaranteed in x6" counter back to 6).
GUSH_GUARANTEE_EVERY = 6

# Extractor rarity ladder = data["rarity_names"]; rank N grants +20% orb EXP
# to tiers 1..N (no Common line) — see fruit_stats.

# Base abode energy for the Connection..Incarnation stage band (in-game
# "Cultivation Bonus" screen, verified 2026-07-05: abode 208.06 = 130 x 1.60).
# Outside that band the base is unknown, so the GUI's implied-aura-bonus
# readout is hidden.
BASE_ENERGY = 130.0

# Strive Bonus caps at +120% while in the mortal world (Nascent..Incarnation
# per the in-game Strive panel); the GUI warns above it.
STRIVE_CAP_MORTAL = 1.20

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
    target_phase: str = ""          # optional: half-step within target_stage
    target_grade: str = ""          # optional: grade within target_phase
    # UI-only: never read by the math. Both UIs compare it against
    # prestock_days; it rides Inputs for the cross-platform schema (prefs
    # blob + OMV2 'td' key on mobile).
    timegate_days: float = 0.0      # days until the world-level timegate lifts (0 = not set)
    top_stage: str = ""             # server #1's Stage; enables Strive drop-off projection
    mature_server: bool = True      # world level >= 30: minor-gap tiers + extra-rank bonus
    dailies_done: bool = False      # today's daily pills/respira already used; defer to next reset
    reset_in_hours: float = 24.0    # hours until the daily reset (only used with dailies_done)

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

    # Ascension Virya blessings: ADDITIVE percentage-point bonuses on the
    # absorption ratio (community-triple-confirmed additive 2026-07-15; see
    # docs/knowledge/game-mechanics-verified.md). Fractions of 1 (0.20 = +20pp).
    # The entered absorption_ratio is the on-screen TOTAL, which already
    # includes them; the engine strips them to recover the true Strive.
    bless_pp: float = 0.0           # Virya absorption pp; flat +0.20 in Incarnation (tiers don't stack)
    bless_window_pp: float = 0.0    # windowed tier; dormant in Incarnation, Voidbreak value unverified — enter manually once read

    # XP elixirs: a flat daily XP stream analogous to Respira (no crit roll).
    elixir_per_day: float = 0.0     # elixirs consumed per day
    elixir_exp: float = 0.0         # EXP per elixir (item tooltip)
    elixir_effect: float = 1.0      # effectiveness after elixir tolerance (1.0 = 100%)


@dataclass
class Results:
    valid: bool = False
    error: str = ""
    phase_days: float = 0.0        # time until end of current phase (w/ pills+fruit)
    stage_days: float = 0.0        # time until end of current stage
    target_days: float = 0.0       # time until start of target stage
    target_valid: bool = False
    # Prestock (timegated): XP stocked while parked at the current Stage's cap.
    prestock_valid: bool = False
    prestock_pct: float = 0.0      # overcap % needed, in the game's display convention
    prestock_days: float = 0.0     # days to stock the target's XP at the capped rate
    prestock_band: tuple = (0.0, 0.0)
    abode_aura: float = 0.0
    strive: float = 0.0                 # implied Strive Bonus (multiplier, e.g. 0.30 = +30%)
    base_xp_per_day: float = 0.0        # culti_speed at the current grade, per day
    effective_xp_per_day: float = 0.0   # base with gem + pill speed-ups applied
    pill_xp_per_day: float = 0.0
    # Daily flat XP as a fraction of base tick XP (legacy Donk-sheet ratio,
    # cell E17). No UI displays it; kept for cross-engine parity coverage.
    pill_speedup: float = 0.0
    gem_speedup: float = 0.0
    mythic_pills_per_day: float = 0.0
    pearl_xp_per_day: float = 0.0
    respira_xp_per_day: float = 0.0
    elixir_xp_per_day: float = 0.0
    fruit_xp: float = 0.0
    fruit_days_saved: float = 0.0
    # 90% (P5..P95) time bands from fruit/respira crit variance: (low, high).
    phase_band: tuple = (0.0, 0.0)
    stage_band: tuple = (0.0, 0.0)
    target_band: tuple = (0.0, 0.0)


@dataclass(frozen=True)
class PillBreakdown:
    """Daily pill/artifact XP model (the unit-test API for pill math)."""
    xp_per_day: float
    mythic_per_day: float
    pearl_xp_per_day: float


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

    def target_start_index(self, stage: str, phase: str = "", grade: str = "") -> int:
        """Row index where the target begins: start of the stage, of a
        half-step within it, or of a specific grade."""
        if not phase:
            return self.stage_start_index(stage)
        if not grade:
            for i, r in enumerate(self.rows):
                if r["stage"] == stage and r["phase"] == phase:
                    return i
            return -1
        return self.row_index(stage, phase, grade)

    def base_low(self, stage: str, phase: str, grade: str) -> float | None:
        """Base absorption band low for a row; None for an unknown row."""
        i = self.row_index(stage, phase, grade)
        return self.rows[i]["low"] if i >= 0 else None

    def implied_strive(self, stage: str, phase: str, grade: str,
                       absorption_ratio: float) -> float | None:
        """Implied Strive Bonus from the entered absorption at a row (game
        formula: Absorption = Base x (1 + Strive)); None for an unknown row."""
        low = self.base_low(stage, phase, grade)
        if low is None or low <= 0:
            return None
        return absorption_ratio / low - 1

    def respira_base_estimate(self, stage: str) -> float | None:
        """Per-Stage Respira base XP: measured where known, otherwise the
        nearest measured anchor scaled by the per-Stage ratio."""
        order = self.stages()
        if stage not in order:
            return None
        if stage in _RESPIRA_BASE:
            return _RESPIRA_BASE[stage]
        i = order.index(stage)
        anchors = [(order.index(s), b) for s, b in _RESPIRA_BASE.items()
                   if s in order]
        if not anchors:
            return None
        ai, ab = min(anchors, key=lambda t: abs(t[0] - i))
        return ab * _RESPIRA_STAGE_RATIO ** (i - ai)

    def blessing_applies(self, stage: str, phase: str, grade: str) -> bool:
        """Whether the conditional (before Voidbreak MIDDLE) blessing tier
        still applies at a row; True when the boundary is not in the data."""
        i = self.row_index(stage, phase, grade)
        vbm = self.target_start_index("Voidbreak", "MIDDLE")
        return i >= 0 and (vbm < 0 or i < vbm)

    def has_strive(self, stage: str) -> bool:
        """Strive Bonus exists from Nascent Soul onward (earlier stages have
        no Strive panel in-game)."""
        order = self.stages()
        return stage in order and order.index(stage) >= order.index("Nascent")

    def base_energy_known(self, stage: str) -> bool:
        """BASE_ENERGY = 130 is verified for Connection..Incarnation only."""
        order = self.stages()
        if stage not in order:
            return False
        return (order.index("Connection") <= order.index(stage)
                <= order.index("Incarnation"))

    # ---- pills ---------------------------------------------------------
    def pill_math(self, inp: Inputs) -> PillBreakdown:
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
        return PillBreakdown(total_xp_day, mythic_per_day, pearl_xp_day)

    _pill_math = pill_math  # compat alias

    # ---- fruits ----------------------------------------------------------
    def fruit_stats(self, inp: Inputs) -> tuple[float, float]:
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
        # Gush multiplier is upgraded via the Gush track (in-game "Gush Bonus"
        # panel, verified 2026-07-07: Gush lvl 14 shows +206% = gush_xp 2.06;
        # base 1.5 = the "base Gush multiplier is 150%" intro text). Donk's
        # sheet looked this up by culti level — wrong track.
        gxm = l_gush["gush_xp"]

        culti_mult = 1 + l_culti["culti_xp"]
        ext = self.data["extractor_chance"].get(inp.extractor_rarity, [1, 0, 0, 0, 0, 0])
        # Extractor rarity rank unlocks "+20% <tier> Aura Orb EXP" cumulatively
        # from Uncommon up to its own tier (in-game "EXP Boost" list — there is
        # no Common line). Verified: Epic extractor shows exactly
        # Uncommon/Rare/Epic +20%. (Donk's sheet gated these on culti-level
        # thresholds instead, which also boosted the Common tier.)
        ladder = self.data["rarity_names"]
        rank_idx = ladder.index(inp.extractor_rarity) \
            if inp.extractor_rarity in ladder else 0
        # Expected quality factor (treated as deterministic — the data models it
        # as an aggregate, not a single-tier draw, so only gush drives variance).
        # The quality table rows sum to 1.0 (levels 0-10) or 0.7 (levels 11+);
        # the extractor fills the missing mass at its rarity tier, so the tier
        # probabilities always form a true distribution. (Naively adding the two
        # tables double-counts up to 100% of the mass and makes a BETTER
        # extractor lower the projection for mismatched combos.)
        qual = l_qual["quality"]
        residual = max(0.0, 1.0 - sum(qual))
        ext_tot = sum(ext)
        e_q = 0.0
        for i, qmult in enumerate(self.data["quality_mult"]):
            p = qual[i] + (ext[i] / ext_tot * residual if ext_tot > 0 else 0.0)
            e_q += p * (culti_mult + (0.2 if 1 <= i <= rank_idx else 0.0)) * qmult

        # gc is the RANDOM trigger rate (extractor panel: "20.0% (Gush
        # guaranteed in Aura Orb x6)" — track bonus sums to exactly 20%, pity
        # listed separately). The pity is SOFT: any gush resets the x6 counter
        # (observed 2026-07-10 — a random gush on the 5th fruit reset the
        # counter to 6), so a gush is guaranteed within 6 fruits of the LAST
        # gush, not on every literal 6th. Model: Markov chain over consecutive
        # misses s = 0..4; the fruit gushes with prob 1 at s = 5, else gc.
        # Exact mean/variance of the gush count via moment recursion, counter
        # assumed fresh at batch start.
        n = int(inp.fruit_count)
        k = GUSH_GUARANTEE_EVERY
        p = [0.0] * k   # P(miss streak = s)
        m = [0.0] * k   # E[gushes · 1{streak = s}]
        q = [0.0] * k   # E[gushes² · 1{streak = s}]
        p[0] = 1.0
        for _ in range(n):
            p2 = [0.0] * k; m2 = [0.0] * k; q2 = [0.0] * k
            for s in range(k):
                pg = 1.0 if s == k - 1 else gc
                p2[0] += pg * p[s]
                m2[0] += pg * (m[s] + p[s])
                q2[0] += pg * (q[s] + 2 * m[s] + p[s])
                if s < k - 1:
                    p2[s + 1] += (1 - pg) * p[s]
                    m2[s + 1] += (1 - pg) * m[s]
                    q2[s + 1] += (1 - pg) * q[s]
            p, m, q = p2, m2, q2
        exp_gushes = sum(m)
        var_gush_count = max(0.0, sum(q) - exp_gushes ** 2)
        mean = base * e_q * (n + exp_gushes * (gxm - 1))
        var_total = (base * e_q) ** 2 * (gxm - 1) ** 2 * var_gush_count
        return mean, var_total

    _fruit_stats = fruit_stats  # compat alias

    # ---- strive drop-off ---------------------------------------------------
    def _strive_dropoff(self, inp: Inputs, idx: int, strive: float):
        """Optional Strive drop-off: if server #1's Stage is given and you're
        behind them, Strive steps DOWN as you climb major realms toward #1
        (gap shrinks). Anchored to your real current Strive via _strive_shape,
        so at the current grade it's unchanged; it fades to 0 at #1's realm.
        Returns strive_of(row) or None (then Strive is held constant — and
        cancels out of the time entirely)."""
        stage_order = self.stages()
        if inp.top_stage not in stage_order or inp.stage not in stage_order:
            return None
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
        # strive <= 0 (absorption at/below base) cannot fade toward #1 —
        # a negative scale would make speeds RISE toward them.
        if not (cur_gap > 0 and cur_shape > 0 and strive > 0):
            return None
        scale = strive / cur_shape
        return lambda row: scale * shape_at(row_idx[id(row)], row["stage"])

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

        # Ascension blessing pp: the conditional tier applies only to rows
        # BEFORE Voidbreak MIDDLE ("Absorption Ratio Before Voidbreak (L)
        # Middle: +20%"); the persistent tiers apply to every row.
        vbm = self.target_start_index("Voidbreak", "MIDDLE")
        bless_end = vbm if vbm >= 0 else len(self.rows)

        def bless_at(j: int) -> float:
            return inp.bless_pp + (inp.bless_window_pp if j < bless_end else 0.0)

        bless_cur = bless_at(idx)
        if bless_cur > 0 and inp.absorption_ratio <= bless_cur:
            res.error = "Absorption ratio must exceed the blessing bonus."
            return res

        # Official composition (client rules text): Absorption ratio =
        # (Stage base + Virya blessing pp) x (1 + Strive Bonus) — blessing pp
        # join the base BEFORE the Strive multiplier. The entered absorption
        # is the on-screen total, so true Strive is recovered by dividing by
        # the blessed base.
        # NOTE: with no blessing, abode = culti_speed/absorption and
        # (1+strive) = absorption/low_cur make strive/absorption CANCEL out of
        # speed(row) below: speed(row) = culti_speed * low_row / low_cur —
        # the entered absorption does not affect the projected time at all.
        # Blessing pp break that cancellation only via the base shift:
        # speed(row) = abode * (low_row + bless(row)) * (1+strive), which
        # still reduces exactly to culti_speed at the current row.
        strive = (inp.absorption_ratio / (cur["low"] + bless_cur) - 1
                  if cur["low"] + bless_cur > 0 else 0.0)
        gem = self.data["gem_bonus"].get(inp.aura_gem, 0.0)

        pills = self.pill_math(inp)
        # Respira: mean daily XP = attempts x base x 1.8 (crit mean). Event
        # attempts are a one-off, credited up front like fruit.
        respira_daily = inp.respira_per_day * inp.respira_exp * _RESPIRA_CRIT_MEAN
        respira_event_xp = inp.respira_event * inp.respira_exp * _RESPIRA_CRIT_MEAN
        # XP elixirs: flat daily XP, deterministic (no crit roll observed).
        # Rides daily_xp, so it obeys the dailies_done reset window and is
        # never gem-multiplied, exactly like pills/Respira.
        elixir_daily = inp.elixir_per_day * inp.elixir_exp * inp.elixir_effect
        daily_xp = pills.xp_per_day + respira_daily + elixir_daily
        pill_ratio = (daily_xp / inp.culti_speed) * TICK_SECONDS / 86400.0
        fruit_mean, fruit_var = self.fruit_stats(inp)
        fruit_xp = fruit_mean + respira_event_xp

        # Crit variance for the best/worst band. Fruit + event attempts are
        # up-front lumps; daily respira accumulates over the projection horizon.
        # var per attempt = base^2 * crit_var; independent, so counts add.
        exp2 = inp.respira_exp * inp.respira_exp * _RESPIRA_CRIT_VAR
        var_upfront = fruit_var + inp.respira_event * exp2
        var_daily = inp.respira_per_day * exp2      # per day of projection

        strive_of = self._strive_dropoff(inp, idx, strive)

        def speed(j: int) -> float:
            row = self.rows[j]
            s = strive_of(row) if strive_of else strive
            return max(1e-12, abode * (row["low"] + bless_at(j)) * (1 + s))

        def row_rate(j: int) -> float:
            # XP/sec while cultivating row j, before daily flat XP.
            return speed(j) * (1 + gem) / TICK_SECONDS

        # Per-row wall-clock integration. Gem multiplies cultivation speed
        # (claimable storage of gem% x speed — treated as continuous, i.e.
        # claimed before the 18-32h cap); pills and Respira are FLAT daily XP
        # added on top, so their value shrinks as base speed grows in later
        # grades (verified in-game 2026-07-07). If today's dailies are already
        # spent, the window until the daily reset (reset_in_hours) runs without
        # the daily XP — and event Respira, which also needs the reset, is
        # credited when the window ends rather than up-front. Piecewise, so a
        # stronger daily setup never perversely increases a short estimate.
        daily_rate = daily_xp / 86400.0            # XP per real second
        reset_window = min(24.0, max(0.0, inp.reset_in_hours)) * 3600.0 \
            if inp.dailies_done else 0.0
        if reset_window > 0.0:
            start_credit, deferred_credit = fruit_mean, respira_event_xp
        else:
            start_credit, deferred_credit = fruit_xp, 0.0

        completion = min(1.0, max(0.0, inp.grade_completion))
        remaining_cur = cur["grade_xp"] * (1 - completion)

        def real_seconds(upto: int) -> float:
            credit = start_credit
            deferred = deferred_credit
            window_left = reset_window
            total = 0.0
            for j in range(idx, upto + 1):
                xp = remaining_cur if j == idx else self.rows[j]["grade_xp"]
                take = min(credit, xp)
                credit -= take
                left = xp - take
                base_rate = row_rate(j)
                if window_left > 0.0 and left > 0.0:
                    sec_np = left / base_rate
                    if sec_np <= window_left:
                        window_left -= sec_np
                        total += sec_np
                        continue
                    left -= base_rate * window_left
                    total += window_left
                    window_left = 0.0
                    credit += deferred
                    deferred = 0.0
                    take = min(credit, left)
                    credit -= take
                    left -= take
                total += left / (base_rate + daily_rate)
            return total

        def days(wall_seconds: float) -> float:
            return wall_seconds / 86400.0

        # end of current phase
        pend = idx
        while pend + 1 < len(self.rows) and self.rows[pend + 1]["stage"] == inp.stage \
                and self.rows[pend + 1]["phase"] == inp.phase:
            pend += 1
        # end of current stage
        send = pend
        while send + 1 < len(self.rows) and self.rows[send + 1]["stage"] == inp.stage:
            send += 1

        base_per_day = inp.culti_speed * (86400.0 / TICK_SECONDS)
        eff_per_day = base_per_day * (1 + gem) + daily_xp

        def xp_ahead(upto: int) -> float:
            total = remaining_cur
            for j in range(idx + 1, upto + 1):
                total += self.rows[j]["grade_xp"]
            return max(0.0, total - start_credit - deferred_credit)

        def band(t_days: float, upto: int) -> tuple:
            # Cumulative-XP SD at the point estimate, mapped to a time spread by
            # the average XP-per-day over THIS horizon (using the current-grade
            # rate would overstate the spread once later, faster grades are in
            # scope). Up-front lump variance + daily respira variance accrued
            # over the horizon. z*SD gives the P5..P95 edges.
            if var_upfront <= 0 and var_daily <= 0:
                return (t_days, t_days)
            rate = xp_ahead(upto) / t_days if t_days > 0 else eff_per_day
            if rate <= 0:
                return (t_days, t_days)
            var_xp = var_upfront + var_daily * max(0.0, t_days)
            sd_days = (var_xp ** 0.5) / rate
            return (max(0.0, t_days - _BAND_Z * sd_days), t_days + _BAND_Z * sd_days)

        res.phase_days = days(real_seconds(pend))
        res.stage_days = days(real_seconds(send))
        res.phase_band = band(res.phase_days, pend)
        res.stage_band = band(res.stage_days, send)

        if inp.target_stage:
            tstart = self.target_start_index(
                inp.target_stage, inp.target_phase, inp.target_grade)
            if tstart > idx:
                res.target_days = days(real_seconds(tstart - 1))
                res.target_band = band(res.target_days, tstart - 1)
                res.target_valid = True
                if tstart > send + 1:
                    # Prestock scenario: a timegate parks you at the Stage cap,
                    # where excess EXP accrues at the CAPPED row's rate (no
                    # future-row speed scaling; pills/Respira stay flat).
                    # Overcap accrual runs WITHOUT the Strive Bonus (player-
                    # confirmed 2026-07-15, see game-mechanics-verified.md),
                    # so the aura component is de-strived: abode x base low.
                    # Blessing pp are an absorption-band bonus, not Strive,
                    # and are assumed to still apply (unverified).
                    cap_speed = abode * (self.rows[send]["low"] + bless_at(send))
                    cap_base = cap_speed * (1 + gem) / TICK_SECONDS
                    pre = real_seconds(send)
                    # The overcap leg is reset-window aware: if the
                    # dailies-done window outlasts the climb to the cap,
                    # overcap accrues WITHOUT the daily XP until the reset,
                    # and the deferred event-Respira credit lands at the
                    # reset (real_seconds credits it before the cap only
                    # when the window closes there, i.e. window_rem == 0).
                    # Credits are accounted explicitly: only what was
                    # actually available during the climb can spill into
                    # the overcap XP.
                    window_rem = max(0.0, reset_window - pre)
                    raw_to_send = remaining_cur + sum(
                        self.rows[j]["grade_xp"] for j in range(idx + 1, send + 1))
                    raw_over = sum(self.rows[j]["grade_xp"]
                                   for j in range(send + 1, tstart))
                    pre_credit = start_credit + (
                        0.0 if window_rem > 0.0 else deferred_credit)
                    over = max(0.0, raw_over - max(0.0, pre_credit - raw_to_send))
                    total = pre
                    if window_rem > 0.0 and over > 0.0:
                        in_win = cap_base * window_rem
                        if over <= in_win:
                            total += over / cap_base
                            over = 0.0
                        else:
                            over = max(0.0, over - in_win - deferred_credit)
                            total += window_rem
                    total += over / (cap_base + daily_rate)
                    res.prestock_days = days(total)
                    res.prestock_band = band(res.prestock_days, tstart - 1)
                    # Overcap % in the game's display convention (verified
                    # 2026-07-15): cumulative XP since the start of the Stage's
                    # final half-step ÷ that half-step's total.
                    cap_phase = self.rows[send]["phase"]
                    hs_total = sum(r["grade_xp"] for r in self.rows
                                   if r["stage"] == inp.stage and r["phase"] == cap_phase)
                    beyond = sum(self.rows[j]["grade_xp"]
                                 for j in range(send + 1, tstart))
                    if hs_total > 0:
                        res.prestock_pct = (hs_total + beyond) / hs_total * 100.0
                        res.prestock_valid = True
            elif tstart >= 0:
                res.error = "Target must be after your current grade."

        # fruit time saved at current speed
        fruit_secs = fruit_xp / inp.culti_speed * TICK_SECONDS if inp.culti_speed else 0.0

        res.valid = True
        res.abode_aura = abode
        res.strive = strive
        res.base_xp_per_day = base_per_day
        res.effective_xp_per_day = eff_per_day
        res.pill_xp_per_day = pills.xp_per_day
        res.pill_speedup = pill_ratio
        res.gem_speedup = gem
        res.mythic_pills_per_day = pills.mythic_per_day
        res.pearl_xp_per_day = pills.pearl_xp_per_day
        res.respira_xp_per_day = respira_daily
        res.elixir_xp_per_day = elixir_daily
        res.fruit_xp = fruit_xp
        # Matches Donk's sheet (myrfruits B45/B46): fruit XP / current speed, no gem/pill divisor.
        res.fruit_days_saved = fruit_secs / 86400.0
        return res


def fmt_days(d: float) -> str:
    if d < 0:
        d = 0
    total_min = round(d * 24 * 60)
    out = f"{total_min // 1440}D {total_min % 1440 // 60}H {total_min % 60}M"
    if d > 365:
        out += f"  (~{d / 365.25:.1f} yr)"
    return out
