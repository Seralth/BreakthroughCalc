# Verified game mechanics (in-game ground truth)


Verified from Seralth's in-game screenshots (2026-07-07, Incarnation (L) Middle G1, Mortal World Epic extractor, tracks Culti 20 / Quality 15 / Gush 14). Engine implements these since the model-overhaul commit after v2.6.1:

- **Pills/Respira are flat daily XP** (pill panel shows absolute XP and % of grade XP; 112.7K/1,412,392 = the displayed 7.98%). Modeled per-row: rate = speed(row)×(1+gem)/8s + daily_xp/86400.
- **Aura Gem** = claimable storage accruing gem% × cultivation speed (16/20/24% = Rare/Epic/Legendary, 18–32h cap per claim). Multiplies cultivation speed only, NOT pills/Respira. Donk's sheet's time/(1+gem)/(1+pills) was wrong on both counts.
- **Gush**: data `gush_chance` = RANDOM trigger rate; the ×6 pity is a **SOFT pity** — any gush (random or guaranteed) resets the "guaranteed in x6" counter (observed 2026-07-10: random gush on 5th fruit reset counter to 6; issue #9). So a gush is guaranteed within 6 of the LAST gush, not every literal 6th. Engine models it as a 6-state Markov moment recursion (exact mean+variance). `gush_xp` is the total multiplier (1.5 base = "150%", 2.06 at Gush lvl 14 = "+206%"), keyed by the **Gush track level** (Donk keyed it by Culti level — wrong).
- **Orb quality**: residual-fill model confirmed exactly (Quality 15 + Epic → Blue 70/Purple 30). The +20% orb EXP boosts are gated on **extractor rarity rank** (Uncommon rank→Uncommon orbs, cumulative to Mythic; no Common line), not culti-level thresholds.
- **culti_xp is 4%/level** (80% at Lv20, "+4%" per level shown in-game). The data table originally had 2%/level — fixed ×2.
- Extractor at highest server Stage: base fruit EXP +50% (= `fruit_highest_rank`). Extractor quality/bonus reset to Common/0 on main-Stage breakthrough; leftover fruits of the previous Stage auto-consume at pre-upgrade rates.

Tests in tests/test_engine.py class ScreenshotGroundTruth2026_07_07 pin all of this. Related: [[fruit-ranks-no-r4-r5]].

## Fruit ranks


The `fruit_xp` table in data/breakthrough.json (R3, R6–R12) is complete despite the apparent gap. Per Seralth (2026-07-06): fruit ranks map to realm bands — R3 covers Nascent through Voidbreak, R6 starts the Spiritual world, R12 starts the Immortal world. R4/R5 were never omitted; they don't exist as fruit ranks. Don't flag this as missing data in future audits.

Related: fruit XP/balance tables are server-authoritative and NOT in the client APK dump (see apk_analysis/RE_FINDINGS.md) — client dumps can't verify balance numbers; Donk's sheet + in-game tooltips are the sources of truth.

## Timegate overcap / XP prestocking (verified 2026-07-15)

When a world-level timegate blocks a major-Stage breakthrough, cultivation
EXP keeps accruing past the full gauge as a tracked "Excess EXP" pool that is
applied after the (still manual) breakthrough.

- Client string (apk_analysis/i18n_en_ru.json line 47604): *"%s's EXP is full.
  Excess EXP will be returned after the breakthrough."* Breakthrough remains a
  manual, gauge-gated action (lines 26669, 21791); timegate lock strings at
  19482 ("Suppressed by Cosmic Laws...") and 70487 (server level limit).
- **Overcap display convention (VERIFIED against two independent community
  data points, exact match with data/breakthrough.json grade_xp):**
  `displayed % = cumulative EXP since the start of the CURRENT HALF-STEP ÷
  that half-step's total XP`. 100% = half-step complete (gauge full at cap).
  - "440% at Incarnation Late → arrive Voidbreak Late G1" (2026 new-player
    guide / community): (Inc LATE total + XP through VB Mid) / Inc LATE total
    = **440%** exactly per our table.
  - "Aux path Wholeness Early G20 overcapped to 404% = Wholeness completion"
    (same guide, Strive-sniffing section): (WN EARLY total + rest of WN) /
    WN EARLY total = **404%** exactly.
  - The double match also independently validates the Incarnation–Wholeness
    grade_xp table.
- Accrual rate while overcapped: pending sources; assumed normal current-row
  rate (speed×(1+gem) + flat pills/Respira) — you stay parked on the capped
  row, so NO future-row speed scaling applies. A prestock projection must
  divide the whole XP distance by the CURRENT rate (the normal target
  projection would be optimistic).
- Timegate context (2026 guide): Voidbreak gate ≈ day 35–38 of a server;
  Myrimon fruits "lose 50% of their XP" once the next realm's timegate passes —
  spend fruits before the gate. RECONCILED (2026-07-15, gameplay.tips abode
  guide): this is the same mechanic as the engine's `fruit_highest_rank` +50%
  base-EXP bonus for fruits matching the server's highest unlocked realm — the
  gate passing unlocks the next realm, so your fruits stop being highest-rank
  and lose the +50% (≈ "lose a third", community rounds to 50%). Not a
  separate penalty.
- Web cross-check (2026-07-15): the Overmortal Global Wiki's Cultivation Room
  per-grade EXP tables match data/breakthrough.json exactly at spot-checked
  rows (Inc Late G15 = 6,549,973; VB Late G20 = 25,232,632). Manual,
  pill-gated breakthroughs confirmed by the wiki; multi-grade carry-through of
  stocked EXP anecdotally supported ("Middle Voidbreak in one go" videos).
  The 440%/overcap display convention exists nowhere on the indexed web —
  our arithmetic reproduction is the only public cross-check. Accrual rate
  while overcapped remains UNVERIFIED (assumed normal capped-row rate);
  verify against the in-game % once capped.

## R8 technique books — pill-effect coverage complete (2026-07-15)

Screenshot-verified from the in-game R8 technique screens: only THREE R8
books carry Cultivation Pill Effect lines — Zixiao Sutra (+1% on learning),
Astral Arcanum (+2% at Tier 3), Chroma (+1% on learning, +3% at Tier 6,
plus +1 Respira attempt at Tier 3 and +1 daily pill attempt at Tier 12).
Per Seralth (2026-07-15): the other six R8 books (Tao of Taiqing, Origin
Scripture, No-Thought Sutra, Moon Meru, Dracophant, Cauldron Refinement)
have NO pill-effect lines — their absence from data/pill_effect_sources.json
is complete coverage, not missing data. Books' Base Abode Aura bonuses are
deliberately NOT cataloged (they're already inside the player's entered
Abode Aura reading; adding them would double-count).

## Respira base XP is FIXED per major Stage (verified 2026-07-15)

Community "Respira has a fixed value" claims are correct, with a precise
meaning: the base cultivation XP per Respira attempt is one constant for the
entire major Stage — it does not scale with phase or grade.

- **Verified (Seralth in-game readings, 2026-07-15, no Respira EXP % buffs,
  overcapped)**: Nascent Soul G6 and Nascent MIDDLE G7 both show **4041** XP
  per attempt. Same value across phases/grades ⇒ fixed per Stage.
- **Client dump sweep (verified)**: no base-XP table or constant exists
  client-side. Respira's internal key is `yunqi` (吐纳). The client ships only:
  crit table `yunqi_crit` = weights/multipliers {600,×1},{300,×2},{80,×5},
  {20,×10} with expected multiplier `yunqi_exp_crit = 1.8`; round size
  `yunqi_round = {20, 2}`; per-level daily attempt caps (`yunqi_limit`, 2 at
  lv1 → 10 default, std_level_calc.lua) plus `extra_times_yunqi` buffs;
  and percent-scale modifiers `extra_base_yunqi`/`extra_exp_yunqi`/
  `extra_crit_yunqi` (cfg_us_attrib.lua / cfg_us_affix.lua). The base amount
  is server-authoritative (consistent with all balance tables).
- **REFUTED (2026-07-15, issue #27)**: the hypothesis that the per-Stage
  constant equals 2.2% of the Stage's Early G1 grade_xp (Nascent:
  183,679 × 0.022 = 4,040.9 → 4041, match to 0.002% — but coincidence).
  Incarnation reading came in at **8,173** vs the rule's prediction of
  17,372 (Early G1) / 32,626 (Late G1); no grade_xp row in
  breakthrough.json yields 8,173 at 2.2% under any books assumption.
  Measured per-Stage constants so far (non-crit on-screen values):
  **Nascent 4,041 · Incarnation 8,173** (ratio 2.022 — near ×2 per Stage,
  but that is one ratio, not a verified law; a Voidbreak reading near
  16,3xx would support it). Formula unknown; treat the constants as a
  lookup of measured values.
- Technique-book Respira lines (screenshot-verified 2026-07-15, Incarnation
  char; cataloged in data/respira_sources.json): activated total **+28%
  Respira Effect** (Energy Unification 1, Cosmic Power 3, Golden Core 1,
  Astrology 3, Taiyin Meridian 3, Yin's Grasp 5, Floral Essence 3,
  Purify & Cleanse 4, Great Yang Manual 5) and **+2 attempts** (Cosmic Power,
  Purify & Cleanse). Not yet active: P&C Tier 9 +7%, Lion's Roar +1%,
  Cauldron Refinement T3 +3%, Moon Meru T12 +10%, Chroma T3 +1 attempt.
  "Respira Effect" = `extra_exp_yunqi`.
- Incarnation reading (2026-07-15, exact, resolves the pending cross-check):
  common non-crit value **8,173** with **16,3xx** crit procs observed in the
  same session. The earlier "low 18000s"/"22.2k sounds more correct" recall
  was wrong — a caution against recall-based confirmation. The ~×2 procs are
  consistent with the client crit table's ×1.8 *expected* value being the
  mean of a distribution that includes ×2 rolls. OPEN: whether the on-screen
  base already includes the +28% technique books (if so, unbuffed base is
  ~6,385) — needs a reading with a book newly toggled to compare.
- Guide corroboration: "do respira for Incarnation before breaking through,
  these will reset" (2026 community guide) — value is keyed to current Stage.

Engine note: no derivable formula — the Respira input stays user-entered.
A per-Stage lookup of measured constants (Nascent 4,041 / Incarnation 8,173)
could pre-fill the field as a suggestion once more Stages are recorded.
