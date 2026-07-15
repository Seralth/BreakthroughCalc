"""Declarative input-field registry for the desktop GUI (no Qt).

One FieldSpec per input field replaces the six hand-maintained registration
sites each field used to need (widget creation aside): the persistence
widget map, the signal-wiring loops, the collect/apply state converters,
the engine Inputs assembly, and the tooltip table. Keys, widget attribute
names and converters are verbatim from the old dicts, so settings files and
the engine mapping are unchanged.

Widgets that are NOT persisted input fields (output labels, buttons, the
pill-effect rows) are not in the registry and keep their own handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from . import i18n
from .i18n import tr
from .labels import (
    phase_disp, phase_key, stage_disp, stage_key,
    vase_input_disp, vase_input_key,
)


@dataclass(frozen=True)
class FieldSpec:
    key: str                            # persisted settings key
    widget_attr: str                    # MainWindow attribute for the widget
    kind: str                           # combo | check | spin | dspin
    inputs_attr: Optional[str] = None   # engine Inputs field (None = UI-only)
    to_key: Optional[Callable] = None   # combo display text -> internal key
    to_disp: Optional[Callable] = None  # internal key -> combo display text
    scale: Optional[float] = None       # Inputs value = widget value / scale
    tooltip: Optional[str] = None       # English source string; tr()'d at install
    on_change: Optional[str] = None     # MainWindow handler name (default: recalc)


# Shared tooltip strings (one string, several widgets — as before).
_MARK_TIP = ("Your in-game 'Cultivation Pill EXP Bonus' for this pill rarity (mainly from "
             "Constellation Altar Star Marks). Entered as a ratio: 0.10 = +10%.")
_CHARGE_TIP = ("Daily Energy Charge: 30 Fateum/Destium adds 100 Energy to this artifact, "
               "once per day. Check if you use it every day.")

# Combo values are persisted as INTERNAL keys (language-independent);
# to_key/to_disp convert display text <-> internal key per field.
FIELDS: tuple = (
    FieldSpec("stage", "stage", "combo", inputs_attr="stage",
              to_key=stage_key, to_disp=stage_disp, on_change="_on_stage_changed"),
    FieldSpec("phase", "phase", "combo", inputs_attr="phase",
              to_key=phase_key, to_disp=phase_disp, on_change="_on_phase_changed"),
    FieldSpec("grade", "grade", "combo", inputs_attr="grade"),
    FieldSpec("completion", "completion", "dspin", inputs_attr="grade_completion",
              scale=100.0,
              tooltip="How far into the current Grade you are, as a percent."),
    FieldSpec("speed", "speed", "dspin", inputs_attr="culti_speed",
              tooltip="The in-game Cultivation Speed: XP gained per 8-second Cosmoapsis tick."),
    FieldSpec("absorb", "absorb", "dspin", inputs_attr="absorption_ratio",
              scale=100.0,
              tooltip="Your Absorption Ratio as a percent (e.g. 27.5). Shown below is the Stage's base for the selected Grade."),
    FieldSpec("gem", "gem", "combo", inputs_attr="aura_gem",
              to_key=i18n.reverse, to_disp=tr,
              tooltip="Aura Gem rarity. In-game it's claimable storage that accrues gem% of your cultivation speed "
                      "(up to 18-32h per claim); modeled as a continuous speed multiplier on cultivation only — "
                      "pills/Respira are flat XP and are NOT boosted by the gem."),
    FieldSpec("target", "target", "combo", inputs_attr="target_stage",
              to_key=stage_key, to_disp=stage_disp, on_change="_on_target_stage_changed",
              tooltip="Optional: a future Stage to time your arrival at."),
    FieldSpec("target_phase", "target_phase", "combo", inputs_attr="target_phase",
              to_key=phase_key, to_disp=phase_disp, on_change="_on_target_phase_changed",
              tooltip="Optional: a half-step within the target Stage. Blank = start of the Stage."),
    FieldSpec("target_grade", "target_grade", "combo", inputs_attr="target_grade",
              tooltip="Optional: a grade within the target half-step. Blank = start of the half-step."),
    FieldSpec("timegate_days", "timegate", "dspin", inputs_attr="timegate_days",
              tooltip="Optional: days until the world-level timegate lifts (shown in-game once someone "
                      "reaches the last half-step). Compared against the prestock time. Reminder: use "
                      "Myrimon fruits BEFORE the gate — the gate unlocks the next realm, so they lose the +50% highest-realm bonus."),
    FieldSpec("top_stage", "top_stage", "combo", inputs_attr="top_stage",
              to_key=stage_key, to_disp=stage_disp,
              tooltip="Optional: your server's #1 cultivator's Stage. Models your Strive stepping DOWN as you "
                      "break through toward them (estimated; assumes #1 stays put; live value is server-computed hourly). "
                      "Leave blank to hold Strive constant."),
    FieldSpec("pill_rank", "pill_rank", "combo", inputs_attr="pill_rank"),
    FieldSpec("pill_limit", "pill_limit", "dspin", inputs_attr="pill_limit",
              tooltip="Daily pill-use limit that caps Gold/Purple/Blue usage."),
    FieldSpec("gold_day", "gold_day", "dspin", inputs_attr="gold_per_day"),
    FieldSpec("purple_day", "purple_day", "dspin", inputs_attr="purple_per_day"),
    FieldSpec("blue_day", "blue_day", "dspin", inputs_attr="blue_per_day"),
    FieldSpec("mark_blue", "mark_blue", "dspin", inputs_attr="mark_blue", tooltip=_MARK_TIP),
    FieldSpec("mark_purple", "mark_purple", "dspin", inputs_attr="mark_purple", tooltip=_MARK_TIP),
    FieldSpec("mark_gold", "mark_gold", "dspin", inputs_attr="mark_gold", tooltip=_MARK_TIP),
    FieldSpec("vase", "vase", "check", inputs_attr="vase"),
    FieldSpec("vase_star", "vase_star", "combo", inputs_attr="vase_star"),
    FieldSpec("vase_skin", "vase_skin", "check", inputs_attr="vase_skin",
              tooltip="Transmog skin: refined pills give +8% Cultivation EXP"),
    FieldSpec("vase_input", "vase_input", "combo", inputs_attr="vase_input",
              to_key=vase_input_key, to_disp=vase_input_disp,
              tooltip="Which pill quality you refine into red pills. Refines are discounted by input "
                      "quality (Epic -5%, Legendary -20% Energy), so feeding gold pills yields extra "
                      "red pills over time. Base cost also depends on pill rank (75-100 energy)."),
    FieldSpec("mirror", "mirror", "check", inputs_attr="mirror"),
    FieldSpec("mirror_star", "mirror_star", "combo", inputs_attr="mirror_star"),
    FieldSpec("mirror_skin", "mirror_skin", "check", inputs_attr="mirror_skin",
              tooltip="Transmog skin: Duplication consumes 10% less Energy"),
    FieldSpec("pearl", "pearl", "check", inputs_attr="pearl"),
    FieldSpec("pearl_star", "pearl_star", "combo", inputs_attr="pearl_star"),
    FieldSpec("pearl_skin", "pearl_skin", "check", inputs_attr="pearl_skin",
              tooltip="Transmog skin: Timereversal Pearl Energy Cost -10%"),
    FieldSpec("mature_server", "mature_server", "check", inputs_attr="mature_server",
              tooltip="Server age changes how Strive is computed. Mature servers (world level 30+, "
                      "the common case) use finer level-gap tiers plus a realm-gap bonus (cap ~120%); "
                      "young servers use the plain realm-gap table (cap 70%). Only used when "
                      "Server #1's Stage is set."),
    FieldSpec("dailies_done", "dailies_done", "check", inputs_attr="dailies_done",
              tooltip="Check if you've already taken today's daily pills and Respira. The "
                      "projection then defers that boost to the next daily reset (today runs "
                      "at base speed). Mainly affects short estimates."),
    FieldSpec("reset_in_hours", "reset_in", "dspin", inputs_attr="reset_in_hours",
              tooltip="Hours until the game's daily reset. Only used when the box above is "
                      "checked: the projection runs the window until the reset without the "
                      "daily pill/Respira XP (and defers event Respira to the reset), then "
                      "resumes the normal daily routine."),
    FieldSpec("respira_per_day", "respira_per_day", "dspin", inputs_attr="respira_per_day",
              tooltip="Your daily Respira attempt limit as shown in-game (base + permanent "
                      "bonus attempts). The base limit is 10/day (confirmed from game "
                      "data). Leave out temporary event attempts."),
    FieldSpec("respira_event", "respira_event", "dspin", inputs_attr="respira_event",
              tooltip="One-off extra Respira attempts available today only (event/item). "
                      "Credited once, not as a daily rate."),
    FieldSpec("respira_exp", "respira_exp", "dspin", inputs_attr="respira_exp",
              tooltip="The base (non-crit) Cultivation EXP from one Respira attempt — see the "
                      "note below the field."),
    FieldSpec("pearl_xp10", "pearl_xp10", "dspin", inputs_attr="pearl_xp_per_10",
              tooltip="Timereversal Pearl: EXP granted per 10 energy."),
    FieldSpec("vase_charge", "vase_charge", "check", inputs_attr="vase_charge", tooltip=_CHARGE_TIP),
    FieldSpec("mirror_charge", "mirror_charge", "check", inputs_attr="mirror_charge", tooltip=_CHARGE_TIP),
    FieldSpec("pearl_charge", "pearl_charge", "check", inputs_attr="pearl_charge", tooltip=_CHARGE_TIP),
    FieldSpec("fruit_rank", "fruit_rank", "combo", inputs_attr="fruit_rank"),
    FieldSpec("fruit_high", "fruit_high", "check", inputs_attr="fruit_highest_rank"),
    FieldSpec("fruit_count", "fruit_count", "dspin", inputs_attr="fruit_count",
              tooltip="Number of Myrimon Fruits processed through the Aura Extractor."),
    FieldSpec("lvl_culti", "lvl_culti", "spin", inputs_attr="lvl_culti"),
    FieldSpec("lvl_quality", "lvl_quality", "spin", inputs_attr="lvl_quality"),
    FieldSpec("lvl_gush", "lvl_gush", "spin", inputs_attr="lvl_gush"),
    FieldSpec("extractor", "extractor", "combo", inputs_attr="extractor_rarity",
              to_key=i18n.reverse, to_disp=tr),
    FieldSpec("abode_aura", "abode_aura", "dspin",
              tooltip="Your Abode Aura as shown on the Cultivation Bonus screen. With Absorption "
                      "Ratio entered, Cultivation Speed = Abode Aura × Absorption Ratio."),
)

FIELD_BY_KEY = {spec.key: spec for spec in FIELDS}
