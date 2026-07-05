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

import sys

if getattr(sys, "frozen", False):
    _BASE = sys._MEIPASS  # PyInstaller bundle
else:
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BASE, "data", "breakthrough.json")


def load_data(path: str | None = None) -> dict:
    with open(path or _DATA_PATH) as f:
        return json.load(f)


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
    mirror: bool = False
    mirror_star: str = "0*"
    mirror_skin: bool = False
    pearl: bool = False
    pearl_star: str = "0*"
    pearl_xp_per_10: float = 0.0    # "EXP for 10 Energy" input

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
    pill_xp_per_day: float = 0.0
    pill_speedup: float = 0.0      # ratio (E17)
    gem_speedup: float = 0.0
    mythic_pills_per_day: float = 0.0
    pearl_xp_per_day: float = 0.0
    fruit_xp: float = 0.0
    fruit_days_saved: float = 0.0
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
        vase_adder = star.get(inp.vase_star, [1, 200, 0])[2] if inp.vase else 0.0
        mirror_adder = star.get(inp.mirror_star, [1, 200, 0])[2] if inp.mirror else 0.0

        gold_xp = (1 + plus_ratio + inp.mark_gold) * gold
        purple_xp = (1 + plus_ratio + inp.mark_purple) * purple
        blue_xp = (1 + plus_ratio + inp.mark_blue) * blue
        mythic_xp = (1 + plus_ratio + vase_adder + mirror_adder + (0.08 if inp.vase_skin else 0)) * mythic

        # Vase mythic pills/day: energy/day divided by pill cost (85 at 5*, else 100)
        vase_pills = 0.0
        if inp.vase:
            rec = star.get(inp.vase_star, [1, 200, 0])[0]
            energy_day = (1440 / 15) * rec + 100
            vase_pills = energy_day / (85 if inp.vase_star == "5*" else 100)
        mirror_pills = 0.0
        if inp.vase and inp.mirror:
            rec = star.get(inp.mirror_star, [1, 200, 0])[0]
            energy_day = (1440 / 15) * rec + 100
            cost = star.get(inp.mirror_star, [1, 200, 0])[1] * (0.9 if inp.mirror_skin else 1.0)
            mirror_pills = energy_day / max(1e-9, cost) + vase_pills
        mythic_per_day = mirror_pills if (inp.vase and inp.mirror) else vase_pills

        # Pearl: uses/day * XP per use (XP for 10 energy input, +20% at 1*+)
        pearl_xp_day = 0.0
        if inp.pearl:
            rec = star.get(inp.pearl_star, [1, 200, 0])[0]
            energy_day = rec * 4 * 24 + 100
            uses = math.floor(energy_day / 10)  # FLOOR(energy, 10) / cost-per-use(10)
            star_n = int(inp.pearl_star[0]) if inp.pearl_star[:1].isdigit() else 0
            pearl_xp_day = math.floor((uses * inp.pearl_xp_per_10 * (1.2 if star_n >= 1 else 1.0)) / 10) * 10

        used_gold = min(inp.gold_per_day, inp.pill_limit)
        used_purple = min(inp.purple_per_day, inp.pill_limit)
        used_blue = min(inp.blue_per_day, inp.pill_limit)

        total_xp_day = (mythic_per_day * mythic_xp + used_gold * gold_xp
                        + used_purple * purple_xp + used_blue * blue_xp + pearl_xp_day)
        return {
            "xp_per_day": total_xp_day,
            "mythic_per_day": mythic_per_day,
            "pearl_xp_day": pearl_xp_day,
        }

    # ---- fruits ----------------------------------------------------------
    def _fruit_xp(self, inp: Inputs) -> float:
        if inp.fruit_count <= 0:
            return 0.0
        base = self.data["fruit_xp"].get(inp.fruit_rank, 0)
        if inp.fruit_highest_rank:
            base *= 1.5
        lv = self.data["fruit_levels"]
        l_gush = lv[str(max(0, min(30, inp.lvl_gush)))]
        l_culti = lv[str(max(0, min(30, inp.lvl_culti)))]
        l_qual = lv[str(max(0, min(30, inp.lvl_quality)))]

        gush_chance = l_gush["gush_chance"]
        gushed = inp.fruit_count * gush_chance
        normal = inp.fruit_count - gushed
        gush_xp_mult = l_culti["gush_xp"]          # sheet looks GushXP up by culti level
        est_xp = base * normal + base * gushed * gush_xp_mult

        culti_mult = 1 + l_culti["culti_xp"]
        ext = self.data["extractor_chance"].get(inp.extractor_rarity, [1, 0, 0, 0, 0, 0])
        total = 0.0
        thresholds = [1, 6, 11, 16, 21, 26]
        for i, qmult in enumerate(self.data["quality_mult"]):
            prob = min(1.0, l_qual["quality"][i] + ext[i])
            tier_bonus = 0.2 if inp.lvl_culti >= thresholds[i] else 0.0
            total += est_xp * (culti_mult + tier_bonus) * prob * qmult
        return total

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
        bonus = inp.absorption_ratio - cur["low"]
        abode = inp.culti_speed / inp.absorption_ratio
        gem = self.data["gem_bonus"].get(inp.aura_gem, 0.0)

        pills = self._pill_math(inp)
        pill_ratio = (pills["xp_per_day"] / inp.culti_speed) * TICK_SECONDS / 86400.0
        fruit_xp = self._fruit_xp(inp)

        def speed(row) -> float:
            return max(1e-12, abode * (row["low"] + bonus))

        def days(xp_seconds: float) -> float:
            return xp_seconds / 86400.0 / (1 + gem) / (1 + pill_ratio)

        # seconds of cultivation from "now" through the end of row j (inclusive),
        # with fruit XP credited against the earliest remaining XP.
        def raw_seconds(upto: int) -> float:
            credit = fruit_xp
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

        res.phase_days = days(raw_seconds(pend))
        res.stage_days = days(raw_seconds(send))

        if inp.target_stage:
            tstart = self.stage_start_index(inp.target_stage)
            if tstart > idx:
                res.target_days = days(raw_seconds(tstart - 1))
                res.target_valid = True
            elif tstart >= 0:
                res.error = "Target stage precedes current stage."

        # fruit time saved at current speed
        fruit_secs = fruit_xp / inp.culti_speed * TICK_SECONDS if inp.culti_speed else 0.0

        res.valid = True
        res.abode_aura = abode
        res.pill_xp_per_day = pills["xp_per_day"]
        res.pill_speedup = pill_ratio
        res.gem_speedup = gem
        res.mythic_pills_per_day = pills["mythic_per_day"]
        res.pearl_xp_per_day = pills["pearl_xp_day"]
        res.fruit_xp = fruit_xp
        res.fruit_days_saved = fruit_secs / 86400.0 / (1 + gem)
        return res


def fmt_days(d: float) -> str:
    if d < 0:
        d = 0
    total_min = int(d * 24 * 60)
    return f"{total_min // 1440}D {total_min % 1440 // 60}H {total_min % 60}M"
