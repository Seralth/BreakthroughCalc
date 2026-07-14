# Combat stat mechanics (verified from client data)

Scope: combat/gear only — deliberately separate from the cultivation/breakthrough
knowledge in `game-mechanics-verified.md`. Everything here is verified from the
decompiled client configs in `apk_analysis/om/decompiled/` (file:line cited) or
in-game tooltip text; community claims are labeled as such. The equations that
*combine* these constants run server-side (see "Not knowable from the client").

Much of this is already surfaced to users in the Reference → Combat & Gear and
Advanced tabs (`breakthrough_calc/gui.py`); this doc records the raw sources.

## Verified constants (cfg_us_calc.lua)

- **Crit**: coefficient p = 0.8 (L1198), q = 0.26 (L1203); `crit_damage` = 200
  (L1208), base crit multiplier 150% (`crit_damage_base` = 150, L1212, floored);
  **crit rate clamped to 1–50%** (`crit_range` {1,50}, L1217).
- **Hit rate**: clamped to **25–99%** (`hitrate_range` {25,99}, L3092 — note the
  floor is 25%, not 1%); physical and magical hit curves both use
  coefficients m = 0.9, n = 0.15 (L3147/3152 phys, L4253/4258 magic).
- **"Penetration" is not a standalone stat**: the attacker's 体相/法相
  (Physique/Psyche-type) attribute advantage reduces target P.DEF/M.DEF by
  **0.1% per point, capped at 50%** (`hp/mp_defense_dim_coefficient` →
  L3137/L4243, shared table L122). Contested: only the side with the higher
  value gets any effect.
- **Block** (刚毅/凝神): while higher than attacker's, **30% chance** per hit to
  mitigate **0.1% per point of advantage, capped at 40%**
  (`hp/mp_defense_ex_coefficient` → L3142/L4248, shared table L126
  {rate=0.1, prob=30, limit=40}).
- **Control (stun/paralysis) duration**: adjustment coefficients m = 0.7,
  n = 0.3, with the final duration multiplier clamped to **0.5–1.25×**
  (`control_time_fix_*`, L1177–1189). Control statuses are
  STUN/BLIND/SILENT/MYSTEY_CONTROL (L6814); there is no literal "paralysis"
  stat — the UI's paralysis lines map to control enhance/reduce.

## Verified per-point stat conversions (cfg_us_attrib.lua / cfg_us_helper_tip.lua)

- Agility (身法): 1 pt = +3 P.hit, +3 P.eva, +3 M.hit, +3 M.eva
  (helper_tip L7, attrib L61–64).
- Physique 1 pt = +4 P.ATK +2 P.DEF; Psyche 1 pt = +4 M.ATK +2 M.DEF.
- Crit family stats: `crit_chance`, `crit_damage`, `crit_damage_ex` (flat dmg
  added after the multiplier), `crit_defense` (−1% attacker crit multiplier
  per 1%, never prevents the crit), `crit_resistance` (reduces chance of being
  crit) — attrib L1054–1121, helper_tip L138–154.
- Stun contested dials (in-game tooltip / Advanced tab, client-stated):
  chance enhance +0.2%/pt (cap +100%) vs resist −0.2%/pt (cap −50%);
  duration enhance +0.5%/pt (**cap +25%**) vs resist −0.5%/pt (cap −50%).
- Toughness (韧性): each control hit grants 韧性×0.1 as %-based control-time
  resistance, stacking to 100 = full control immunity (helper_tip L179).
- Crit/hit/dodge/crit-resist are **flat values normalized against a
  realm-dependent standard** (`capacity_coef` ladder — see
  apk_analysis/RE_FINDINGS.md L62–64); the in-game tooltip's "rate at current
  realm" is the only exact readout.

## Community affix tier list (affix.txt) — cross-check

The circulating tier list's mechanics claims, checked against the above:

- **Confirmed**: crit hard cap 50%; hit/eva cap 99%; Agility +3 hit/eva per
  point; Physique/Manipulation +4 ATK +2 DEF; defense being weak vs
  penetration; paralysis chance ±0.2%/pt with 50–100% bounds; duration
  resist −0.5%/pt to −50%.
- **Corrected**: paralysis *duration boost* caps at **+25%**, not +50%
  (`control_time_fix_max` = 1.25); the guide's "max change of 50% the
  original duration" is only true for the resist side.
- **Corrected**: hit chance floor is **25%** (`hitrate_range`), not the
  guide's "minimum of 1%".
- **Refined**: penetration isn't a stat that "ignores def on a percentage
  basis" unconditionally — it's a contested attribute check (0.1%/pt of
  *advantage*, cap 50%, zero effect if the opponent's is higher).
- **Unverifiable from client**: the guide's assumed 1:1 cancellation for
  hit-vs-eva and crit-vs-crit-resist. The client ships only curve
  coefficients (m/n and p/q above); the combining equation is server-side,
  so treat 1:1 as plausible inference, not fact.

The Combat & Gear tab's community-tier-list paragraph (desktop gui.py and
mobile reference.dart) has been corrected to the verified numbers.

## Not knowable from the client

- The equations combining hit vs eva, crit vs crit resist, and the
  realm-normalization curve — server-side. Client proof: damage/crit/dodge
  arrive pre-computed in `combat_arpg.dec.lua` `receive_damage()` (L853), and
  `managers_calc_mgr.lua` L274 stubs `calc_base_defense()` to return 0.
- Per-item 10-level affix / resonance / carving *values* — server balance
  data (same rule as cultivation balance tables; see RE_FINDINGS.md).
