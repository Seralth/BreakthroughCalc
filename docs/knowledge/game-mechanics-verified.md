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

## Stage sub-rank suffixes: (M)/(C)/(P) tracks and "Incarnation Completed" (2026-07-15)

Verified from APK i18n strings (`apk_analysis/i18n_all.json`, en/zh/ru):

- Stage names carry a **track suffix**, they are parallel ladders, not extra
  ranks on the Magicka ladder:
  - **(M) = Magicka** (main cultivation) — zh classics: Foundation (M) 筑基,
    Virtuoso (M) 结丹, Nascent Soul (M) 元婴, Incarnation 化神, Voidbreak (M)
    返虚, Wholeness 合体, Perfection (M) 大乘, Nirvana (M) 渡劫.
  - **(C) = Corporia** (body cultivation) — zh: Foundation (C) 锻骨 "forge
    bone", Incarnation (C) 神力, Voidbreak (C) 破虚, etc. Confirmed by item
    text: "A Fateum Bag for the Coporia Incarnation Stage" = 'Incarnation (C)
    Fateum Pack'.
  - **(P) = Pet** cultivation — zh: Connection (P) 通智 "gain sentience",
    Virtuoso (P) 妖丹 "demon core", Celestial (P) 仙兽 "immortal beast".
    NOT "Perfected".
- **"Incarnation (Perfected)" (live-game wording) = 化神圆满/神力圆满**, in
  our dump translated 'Incarnation (M) Completed' / 'Incarnation (C)
  Completed'. It is the ONLY stage with a Completed/圆满 state — the terminal
  sub-rank after maxing Incarnation (Late) G15 while waiting to ascend to the
  Immortal World (Voidbreak). No other mortal-world stage has it.
- Grade ladders per dump (matches data/breakthrough.json): Incarnation Early
  G1–G8, Middle G1–G9, Late G1–G15.
- Completed/Perfected is not an extra XP band — breakthrough.json's
  Incarnation Late G15 row already covers the XP to reach it. Ascension
  itself is event/quest-gated ("Path to Ascension is not yet unlocked.
  Unable to ascend."), which the time calculator does not model.
  UNVERIFIED (server-side): whether cultivation XP keeps accruing/prestocks
  while sitting in Completed awaiting ascension — same open question as the
  overcap accrual rate above.

### Blessing Ranking tied to Completed/Perfected (2026-07-15, in-game tooltip)

Per Seralth's in-game blessing tooltip, corroborated by dump strings
('Higher cultivation means higher blessing ranking for more rewards. /
Completing stage to progress forward can increase rewards.' = 圆满后境界精进
可增加福泽奖励; templates '%s Absorption Ratio + %s%%' and 'Absorption Ratio
Before %s: + %s%%'; 'Activate the "Cultivation Pill Auto-Transmogrification"
Privilege.'):

- Tier 1 **Completion** (Incarnation 100% + breakthrough): removes the realm
  restriction on taking Cultivation Pills; unlocks the Cultivation Pill
  Auto-Transmogrification privilege; blessing rewards +1.
- Tier 2 **Perfection (C)** (Tier 1 + Corporia path at Nascent Soul Late):
  Incarnation (Late) Aura Absorption Ratio +20%; blessing rewards +3.
- Tier 3 **Perfect Incarnation** (Corporia path at Incarnation Middle):
  Aura Absorption Ratio +20% applying to stages before Voidbreak (Late)/
  Middle; blessing rewards +5.
- Dump also has a rank→reward table (Blessing Ranking 1→6, 2→5, 3→4,
  4–10→3, 11+→2) and post-ascension privileges granting Absorption Ratio
  +200% at (mortal? immortal-world) stages plus high-stage pill access.
- Official absorption formula (dump): Cultivation Speed = Abode Aura ×
  Absorption Ratio (× Heavenly Power Bonus); Absorption Ratio = Base Stage
  Absorption Ratio × (1 + Strive Bonus) + Virya Absorption Ratio.

**Calculator impact — REVISED: this CAN affect the time math.** The engine's
projection cancels the entered absorption ratio (speed(row) = culti_speed ×
low_row / low_cur, engine.py) — valid only when bonuses scale all rows
uniformly. A blessing bonus restricted to a realm window ("before Voidbreak
(Late)") breaks the cancellation: windowed rows are faster than the pure
base-band progression predicts. Same class of issue for the +200%
post-ascension privilege and Virya (both additive terms, per the formula).
UNVERIFIED: whether the blessing "+20%" is +20 percentage points added to
the ratio (like Virya) or ×1.2 on it — needs an in-game absorption-tooltip
breakdown screenshot with the blessing active before modeling it. Until
then the calc under-estimates speed (over-estimates time) for accounts with
these blessings on pre-Voidbreak rows.
