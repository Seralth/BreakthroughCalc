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
