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
