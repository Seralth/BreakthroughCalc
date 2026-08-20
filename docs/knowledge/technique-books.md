# Universal technique books — full catalog (screenshot pass 2026-07-15)

Source of truth: 91 phone screenshots taken 2026-07-15/16 (owner's account,
Incarnation (L) Late), archived at `~/Pictures/technique-books-2026-07-15/`.
Every Universal book visible in-game up to R9, with the complete chapter
(tier) bonus list per book. This supersedes the partial technique-book data
that previously lived in `docs/design/sources-shelf-inventory.md`.

## Structure facts (verified)

- The in-game "Techniques" screen has two tabs: **Universal** (documented
  here) and **Exclusive** (NOT yet documented; owner reports stats-only
  bonuses — tracking-only, no calc wiring planned).
- Universal books are grouped by rank shelves **R1–R9** (51 books total:
  1/2/3/4/5/6/9/9/12 per rank).
- Bonus thresholds are fixed steps: **on-learning, Tier 3, 6, 9, 12** and
  additionally **Tier 15** for R8/R9 books. Max tier: 12 for R6/R7,
  15 for R8/R9 (verified from in-progress tier bars "x/12", "x/15").
  R1–R5 maxes are not shown for completed books (community value: 6).
- Every book's final threshold is "Technique Stats +100%" (multiplies the
  book's basic combat stats; not calc-relevant).
- Unlock requirements exist (stage + prior-rank tier counts + a
  book-specific condition) but are deliberately NOT modeled — out of scope.

## Activation realm requirements (rank-wide)

Owner-read anchors (2026-07-18, exact): R6 Nascent Soul Late (Lion's
Roar) · R7 Incarnation Early (Bulwark, independently confirmed by
Ninefall Hoarfrost) · R8 Incarnation Middle (No-Thought Sutra,
independently confirmed by Astral Arcanum) · R9 Incarnation Late (Way of
Creation; plus the 2× R8-at-Tier-13 pair). Two same-rank books matching
pins the requirement as per-RANK, not per-book.

The pattern is exactly realm level = rank + 14, one phase per rank.
R1-R5 are EXTRAPOLATED from it (owner-directed 2026-07-18): R1 Virtuoso
Early · R2 Virtuoso Middle · R3 Virtuoso Late · R4 Nascent Early · R5
Nascent Middle. Completed books hide their activation tooltip, so these
cannot be read on this account — the extrapolation stands unless a fresh
account ever contradicts it.

## Tier-label caveat

Books the account has **completed** display every bonus as "[Activated]"
with no tier label, so for those the bonus ORDER is exact but the tier
threshold is positional inference (learn/3/6/9/12 pattern). The inference
was validated against two books whose thresholds were independently known
(Dragon Flight pill +2% @ T3; Great Yang Manual pill +4% @ T9 — both match
positionally). Books that were unlearned or mid-progress on screenshot day
show explicit "[Activate at Tier N]" labels → those thresholds are exact.

Explicit-label (exact-threshold) books: Lion's Roar, Bulwark, Ninefall
Hoarfrost, Sunset Halberd Dance, all R8, all R9, plus the unactivated tail
tiers of Unbound Blade, Conflagration, Floral Essence, Purify & Cleanse,
Vajra, Dragonsound, Aqua Power, Zixiao Sutra.
Positional-inference books: R1–R5 (all completed), Thunder Winds,
Yin's Grasp, Dragon Flight, Great Yang Manual.

R1–R5 books show only 2–4 bonus lines; with max tier unverified (community
says 6) the mid thresholds there are even-spaced guesses (learn/3/6 for
3 lines; learn/2/4/6 for 4 lines). Low stakes: these books are completed
long before the calc's audience needs threshold precision.

## Full bonus tables

Format: threshold → bonus (verbatim in-game text). `[bs]` = basic combat
stat line. Calc-wired targets: Cultivation Pill Effect, Daily Cultivation
Pill Attempts, Respira Attempts, Respira Effect. Base Abode Aura and Sense
lines are recorded but stay informational (aura is embedded in the user's
in-game aura reading; Sense has no engine input).

### R1
- **Longevity**: two chapters, two tiers each (max tier 4); learn → Base
  Abode Aura +1%; chapter 2 (T3) → Respira Attempts +1. No tech-stats
  capstone. Owner-settled 2026-07-18 — exact, do not re-verify.

### R2
- **Energy Unification**: learn → Respira Effect +1%; T3 → Base Abode Aura +2%; T6 → Technique Stats +100%
- **Rejuvenation**: learn → Base Abode Aura +1%; T3 → Cultivation Pill Effect +2%; T6 → Technique Stats +100%

### R3
- **Yang**: learn → Crit +100 [bs]; T3 → DMG Bonus to Monsters +1%; T6 → Technique Stats +100%
- **Lifeboom**: learn → Cultivation Pill Effect +1%; T3 → Respira Attempts +1; T6 → Technique Stats +100%
- **Cosmic Power**: learn → Respira Attempts +1; T3 → Respira Effect +3%; T6 → Technique Stats +100%

### R4 (4 lines, thresholds even-spaced guess learn/2/4/6)
- **Focus**: Cultivation Pill Effect +1%; Sense +1; Sense +2; Technique Stats +100%. Extra: "Tier 3 Effect: Quick Technique Upgrade".
- **Golden Core**: Respira Effect +1%; Cultivation Pill Effect +2%; Cultivation Pill Effect +3%; Technique Stats +100%
- **Soul Drain**: Spiritium from Realms +1%; Monster DMG Reduction +1%; DMG Bonus to Monsters +1%; Technique Stats +100%
- **Astrology**: Base Abode Aura +1%; Respira Effect +3%; Daily Cultivation Pill Attempts +1; Technique Stats +100%

### R5 (4 lines, thresholds even-spaced guess learn/2/4/6)
- **Bloodization**: Spiritium from Realms +1%; Relic DMG Reduction +2%; Base Abode Aura +3%; Technique Stats +100%
- **Taiyin Meridian**: MP Regen +1%; Respira Effect +3%; M.ATK +10K [bs]; Technique Stats +100%
- **Solarics**: HP Regen +1%; Base Abode Aura +2%; P.ATK +10K [bs]; Technique Stats +100%
- **Lunarics**: Paralysis Chance Boost +5; DMG Bonus to Monsters +1%; Paralysis Duration Boost +15; Technique Stats +100%
- **Ninefall**: Base Abode Aura +1%; Cultivation Pill Effect +2%; Base Abode Aura +3%; Technique Stats +100%

### R6 (max 12; learn/3/6/9/12)
- **Unbound Blade**: MP +30K [bs]; Ability DMG Reduction +1%; Ability DMG to Taoists +2%; Base Abode Aura +3%; T12 Technique Stats +100% (T12 explicit)
- **Conflagration**: HP +30K [bs]; Ability DMG to Taoists +1%; Ability DMG Reduction +2%; T9 Base Abode Aura +3%; T12 Technique Stats +100% (T9/T12 explicit)
- **Lion's Roar** (explicit): learn Respira Effect +1%; T3 Spiritium from Realms +2%; T6 Sense +2; T9 DMG Bonus to Monsters +2%; T12 Technique Stats +100% (T12 line cut off in shot; owner-confirmed 2026-07-16)
- **Thunder Winds**: Sense +1; DMG Bonus to Monsters +1%; Crit Multiplier +5%; Crit Block +3%; Technique Stats +100%
- **Yin's Grasp**: Spiritium from Realms +1%; T3 Base Abode Aura +2%; T6 Respira Effect +5%; T9 Daily Cultivation Pill Attempts +1; T12 Technique Stats +100% (positional — NEW: pill attempt find)
- **Dragon Flight**: Sense +1; T3 Cultivation Pill Effect +2%; T6 Base Abode Aura +2%; T9 MSPD +20; T12 Technique Stats +100%

### R7 (max 12; learn/3/6/9/12)
- **Floral Essence**: Base Abode Aura +1%; T3 Respira Effect +3%; T6 Cultivation Pill Effect +3%; T9 Daily Cultivation Pill Attempts +1; T12 Technique Stats +100%
- **Purify & Cleanse**: learn "Complete all Respira instantly"; T3 Respira Effect +4%; T6 Respira Attempts +1; T9 Respira Effect +7%; T12 Technique Stats +100% (T9/T12 explicit)
- **Vajra** (explicit): Spiritium from Realms +1%; T3 DMG Bonus to Monsters +1%; T6 Relic DMG Reduction +2%; T9 Relic DMG to Taoists +4%; T12 Technique Stats +100%
- **Dragonsound** (explicit): Paralysis Chance Boost +5; T3 Paralysis Chance Boost +10; T6 DMG Bonus to Monsters +1%; T9 DMG Bonus to Monsters +2%; T12 Technique Stats +100%
- **Bulwark** (explicit): Paralysis Chance Resist +5; T3 Paralysis Chance Resist +10; T6 Monster DMG Reduction +1%; T9 Monster DMG Reduction +2%; T12 Technique Stats +100%
- **Aqua Power**: MP Regen +1%; Ability DMG to Taoists +1%; Ability DMG Reduction +2%; T9 Spiritium from Realms +4%; T12 Technique Stats +100% (T9/T12 explicit)
- **Great Yang Manual**: HP Regen +1%; T3 Base Abode Aura +2%; T6 Respira Effect +5%; T9 Cultivation Pill Effect +4%; T12 Technique Stats +100%
- **Ninefall Hoarfrost** (explicit): Manipulation +500 [bs]; T3 HP +200K [bs]; T6 Ability DMG to Taoists +2%; T9 Ability DMG Reduction +4%; T12 Technique Stats +100%
- **Sunset Halberd Dance** (explicit): Physique +500 [bs]; T3 MP +200K [bs]; T6 Ability DMG Reduction +2%; T9 Ability DMG to Taoists +4%; T12 Technique Stats +100%

### R8 (max 15; learn/3/6/9/12/15 — all explicit)
- **Tao of Taiqing**: M.ATK +3000 [bs]; T3 MP +400K [bs]; T6 Ability DMG Reduction +2%; T9 Ability DMG to Taoists +4%; T12 Base Abode Aura +4%; T15 Technique Stats +100%
- **Origin Scripture**: P.ATK +3000 [bs]; T3 HP +400K [bs]; T6 Ability DMG to Taoists +2%; T9 Ability DMG Reduction +4%; T12 Monster DMG Reduction +3%; T15 Technique Stats +100%
- **No-Thought Sutra**: Paralysis Chance Boost +5; T3 Sense +1; T6 Paralysis Chance Boost +20; T9 Paralysis Chance Resist +30; T12 Ability DMG to Taoists +6%; T15 Technique Stats +100%
- **Moon Meru**: Paralysis Chance Resist +5; T3 Sense +1; T6 Paralysis Duration Boost +10; T9 Paralysis Duration Resist +20; T12 Respira Effect +10%; T15 Technique Stats +100%
- **Dracophant**: Monster DMG Reduction +1%; T3 Spiritium from Realms +2%; T6 Relic DMG to Taoists +2%; T9 Relic DMG Reduction +4%; T12 Monster DMG Reduction +3%; T15 Technique Stats +100%
- **Cauldron Refinement**: DMG Bonus to Monsters +1%; T3 Respira Effect +3%; T6 Relic DMG Reduction +2%; T9 Relic DMG to Taoists +4%; T12 Sense +3; T15 Technique Stats +100%
- **Astral Arcanum**: Spiritium from Realms +1%; T3 Cultivation Pill Effect +2%; T6 Sense +2; T9 Base Abode Aura +3%; T12 Base Abode Aura +4%; T15 Technique Stats +100%
- **Zixiao Sutra**: Cultivation Pill Effect +1%; T3 Base Abode Aura +2% (activated at owner's Tier 4 → ≤3); T6 Paralysis Chance Boost +20; T9 Paralysis Chance Resist +30; T12 Spiritium from Realms +4%; T15 Technique Stats +100%
- **Chroma**: Cultivation Pill Effect +1%; T3 Respira Attempts +1; T6 Cultivation Pill Effect +3%; T9 Base Abode Aura +4%; T12 Daily Cultivation Pill Attempts +1; T15 Technique Stats +100%

### R9 (max 15; learn/3/6/9/12/15 — all explicit; unlock gate "R8 Techniques reach Tier 13: x/2")
- **Laws of Nature**: Cultivation Pill Effect +1%; T3 Sense +1; T6 Paralysis Duration Boost +10; T9 Paralysis Duration Resist +20; T12 Respira Effect +10%; T15 Technique Stats +100%
- **Harvest God Secret**: Base Abode Aura +1%; T3 Respira Effect +3%; T6 Base Abode Aura +3%; T9 Base Abode Aura +4%; T12 Daily Cultivation Pill Attempts +1; T15 Technique Stats +100%
- **Zhurong Mantra**: M.ATK +10K [bs]; T3 Ability DMG Reduction +1%; T6 Ability DMG to Taoists +2%; T9 Ability DMG Reduction +4%; T12 MSPD +50; T15 Technique Stats +100%
- **Divine Water**: Manipulation +2000 [bs]; T3 Ability DMG to Taoists +1%; T6 Ability DMG Reduction +2%; T9 Ability DMG to Taoists +4%; T12 Ability DMG Reduction +6%; T15 Technique Stats +100%
- **Mara Incarnation**: P.ATK +10K [bs]; T3 Ability DMG Reduction +1%; T6 Ability DMG to Taoists +2%; T9 Ability DMG Reduction +4%; T12 Paralysis Duration Resist +30; T15 Technique Stats +100%
- **Heartless**: Physique +2000 [bs]; T3 Ability DMG to Taoists +1%; T6 Ability DMG Reduction +2%; T9 Ability DMG to Taoists +4%; T12 Respira Effect +10%; T15 Technique Stats +100%
- **Gold Smasher**: Spiritium from Realms +1%; T3 Paralysis Duration Resist +10; T6 Relic DMG to Taoists +2%; T9 Relic DMG Reduction +4%; T12 Paralysis Duration Boost +30; T15 Technique Stats +100%
- **Seven Star Blade**: Sense +1; T3 Spiritium from Realms +2%; T6 Relic DMG Reduction +2%; T9 Relic DMG to Taoists +4%; T12 Paralysis Chance Boost +30; T15 Technique Stats +100%
- **Way of Creation**: MP Regen +1%; T3 Relic DMG to Taoists +1%; T6 Relic DMG Reduction +2%; T9 MSPD +20; T12 Ability DMG to Taoists +6%; T15 Technique Stats +100%
- **Eight-Nine Method**: HP Regen +1%; T3 Relic DMG Reduction +1%; T6 Relic DMG to Taoists +2%; T9 Ability DMG to Taoists +4%; T12 Ability DMG Reduction +6%; T15 Technique Stats +100%
- **Honored Origin**: Base Abode Aura +1%; T3 Paralysis Chance Boost +5; T6 Paralysis Chance Resist +10; T9 Base Abode Aura +3%; T12 Paralysis Duration Resist +30; T15 Technique Stats +100%
- **Wordless Scripture**: DMG Bonus to Monsters +1%; T3 Paralysis Chance Resist +5; T6 Paralysis Chance Boost +10; T9 MSPD +20; T12 Paralysis Duration Boost +30; T15 Technique Stats +100%

### R11 (max 15; learn/3/6/9/12/15 — screenshot pass 2026-08-20, confirmed)
- **Moon Howl**: learn Paralysis Chance Resist +8; T3 Respira Effect +4%; T6 Earth Law Learning Speed +6%; T9 Fire Law Learning Speed +8%; T12 Relic DMG to Taoists +5%; T15 Technique Stats +100%
- **Soul Refiner**: learn Paralysis Chance Boost +8; T3 Relic DMG Reduction +1%; T6 Relic DMG to Taoists +2%; T9 Relic DMG Reduction +3%; T12 Relic DMG to Taoists +5%; T15 Technique Stats +100%
- **Thunder Lord Incantation**: learn Metal Law Learning Speed +2%; T3 Water Law Learning Speed +4%; T6 Water Law Learning Speed +6%; T9 Metal Law Learning Speed +8%; T12 Earth Law Learning Speed +10%; T15 Technique Stats +100%
- **Square Inch Scripture**: learn DMG Bonus to Monsters +1%; T3 Ability DMG to Taoists +1%; T6 Ability DMG Reduction +2%; T9 Respira Effect +7%; T12 Monster DMG Reduction +3%; T15 Technique Stats +100%
- **Pure Mysterious Agreement**: learn Base Abode Aura +1%; T3 Base Abode Aura +2%; T6 Crit Multiplier +3%; T9 Crit Block +3%; T12 Fire Law Learning Speed +10%; T15 Technique Stats +100%
- **Heavenly Rhythm**: learn Respira Effect +1%; T3 Respira Effect +3%; T6 Respira Attempts +1; T9 Respira Effect +7%; T12 Respira Effect +9%; T15 Technique Stats +100%

### R12 (max 15; learn/3/6/9/12/15 — screenshot pass 2026-08-20, confirmed)
- **Star Blade**: learn Crit Block +1%; T3 Water Law Learning Speed +4%; T6 Crit Multiplier +3%; T9 Ability DMG Reduction +3%; T12 Fire Law Learning Speed +10%; T15 Technique Stats +100%
- **Spring Autumn Annals**: learn Spiritium from Realms +1%; T3 Respira Effect +4%; T6 Crit Block +2%; T9 Ability DMG to Taoists +3%; T12 Spiritium from Realms +4%; T15 Technique Stats +100%
- **Soul Devourer**: learn DMG Bonus to Monsters +1%; T3 Spiritium from Realms +2%; T6 Respira Effect +5%; T9 Metal Law Learning Speed +8%; T12 Paralysis Duration Resist +30; T15 Technique Stats +100%
- **Dragon Heaven Art**: learn Paralysis Duration Resist +8; T3 Water Law Learning Speed +4%; T6 Paralysis Chance Boost +10; T9 Paralysis Duration Resist +20; T12 Paralysis Duration Boost +30; T15 Technique Stats +100%
- **Solar Jade**: learn Paralysis Chance Resist +8; T3 Relic DMG to Taoists +1%; T6 Relic DMG Reduction +2%; T9 Relic DMG to Taoists +3%; T12 Relic DMG Reduction +4%; T15 Technique Stats +100%
- **Cloud Satchel**: learn Fire Law Learning Speed +2%; T3 Earth Law Learning Speed +4%; T6 Earth Law Learning Speed +6%; T9 Fire Law Learning Speed +8%; T12 Earth Law Learning Speed +10%; T15 Technique Stats +100%

### R13 (max 15; learn/3/6/9/12/15 — screenshot pass 2026-08-20, confirmed)
- **Demon Abyss**: learn Paralysis Chance Boost +8; T3 Relic DMG Reduction +1%; T6 Water Law Learning Speed +6%; T9 Earth Law Learning Speed +8%; T12 Metal Law Learning Speed +10%; T15 Technique Stats +100%
- **Qian Mantra**: learn Spiritium from Realms +1%; T3 Relic DMG to Taoists +1%; T6 Respira Attempts +1; T9 Respira Effect +7%; T12 Ability DMG Reduction +4%; T15 Technique Stats +100%
- **Five-Thunder Mantra**: learn Base Abode Aura +1%; T3 Ability DMG Reduction +1%; T6 Ability DMG to Taoists +2%; T9 Ability DMG Reduction +3%; T12 Ability DMG to Taoists +4%; T15 Technique Stats +100%
- **Yin Yang Overturn**: learn Monster DMG Reduction +1%; T3 Relic DMG to Taoists +1%; T6 Relic DMG Reduction +2%; T9 Relic DMG to Taoists +3%; T12 Relic DMG Reduction +4%; T15 Technique Stats +100%
- **Divine Code**: learn DMG Bonus to Monsters +1%; T3 Ability DMG to Taoists +1%; T6 Ability DMG Reduction +2%; T9 Ability DMG to Taoists +3%; T12 Ability DMG Reduction +4%; T15 Technique Stats +100%
- **Pure Starlight**: learn Spiritium from Realms +2%; T3 Respira Effect +3%; T6 Crit Multiplier +3%; T9 Wood Law Learning Speed +8%; T12 Water Law Learning Speed +10%; T15 Technique Stats +100%

## Exclusive tab (screenshot pass 2026-07-16 — 12 books, complete)

Flat 4×3 grid, no rank shelves. All max Tier 6; every book's capstone is
"Technique Stats +500%". All combat/stat bonuses (tracking only — nothing
calc-wired); the single non-combat line is Whirling Fish Mystery's Base
Abode Aura +3% on learning (display-embedded in the aura reading like all
aura lines). Unlocks are per-book manual items (out of scope). Most carry
a "Divine Magicka" badge; Shade Command, Porcelain Purity and Whirling
Fish Mystery lack it on the list icons. Thresholds verbatim: 4-line books
at learn/T2/T4/T6, 3-line books at learn/T3/T6.

Display order and tables:
1.  **Heavenly Scripture**: Crit Block +8%; T2 Ability DMG Reduction +2%; T4 Ability DMG to Taoists +3%; T6 +500%
2.  **Glacial Craft**: identical to Heavenly Scripture
3.  **Petalstorm Mantra**: Crit Multiplier +12%; T2 Relic DMG to Taoists +2%; T4 Relic DMG Reduction +3%; T6 +500%
4.  **Shade Command** (3-line): Crit Multiplier +8%; T3 Relic DMG Reduction +2%; T6 +500%
5.  **Beyond Requiem**: Crit Multiplier +12%; T2 Relic DMG Reduction +2%; T4 Relic DMG to Taoists +3%; T6 +500%
6.  **Porcelain Purity** (3-line): Crit Block +8%; T3 Relic DMG to Taoists +2%; T6 +500%
7.  **Whirling Fish Mystery** (3-line): Base Abode Aura +3% on learning; T3 Relic DMG Reduction +2%; T6 +500%
8.  **Gourd Command**: Crit Multiplier +12%; T2 Relic DMG Reduction +2%; T4 Relic DMG to Taoists +3%; T6 +500%
9.  **Snow Wander**: Crit Block +8%; T2 Ability DMG to Taoists +2%; T4 Ability DMG Reduction +3%; T6 +500%
10. **Peach Radiance**: identical to Snow Wander
11. **Dusk Revelation**: identical to Gourd Command
12. **Phoenix Reborn**: identical to Heavenly Scripture

## Corrections to prior data

- Cosmic Power is **R3** (was unranked; sources.json had no rank).
- Taiyin Meridian is **R5** (was unranked).
- Astrology is R4 with **Daily Cultivation Pill Attempts +1** (already
  suspected; now on-screen verbatim) — table order Aura/Respira/PillAtt.
- Yin's Grasp: Respira Effect +5% pinned to **T6**, and a previously
  unrecorded **Daily Cultivation Pill Attempts +1 at T9**.
- Golden Core pill lines (+2%, +3%) and Focus pill (+1%) confirmed verbatim.
- Purify & Cleanse: Respira Effect +4% is **T3**, Respira Attempts +1 is
  **T6** (both were min_level 1 before), +7% at T9 confirmed.
- All 12 R9 book names and tables recorded (previously a complete blank).

## Post-R9 manuals — community priority sheet (extracted 2026-07-17)

Source: "Tech manual priority.xlsx" (community tier list, downloaded
2026-07-14 to ~/Downloads). Columns per manual: unlock/T3/T6/T9/T12 node
bonuses, an S+…C rating (R8+ only), free-text build notes. NOT
screenshot-verified — but every R4–R9 row cross-checks node-for-node
against the verified tables above (Chroma, Yin's Grasp, Purify & Cleanse,
Conflagration, Unbound Blade, Honored Origin spot-checked identical), so
per owner decision 2026-07-17 the post-R9 half is treated as reliable
until proven otherwise. Shipped in-app as Guide → Techniques + the
Reference → World Systems roadmap (v2.20). As of v3.1 the in-app table
covers ALL manuals R1–R21 with ratings derived from THESE tables under
a fixed cultivation-speed rubric (attempt nodes heaviest; aura/pill/
Respira/law-speed/Qiyun strong; combat = C) — independent of the
sheet's own grades, which are recorded above for reference only.

R11–R13 are now screenshot-confirmed (see the R11/R12/R13 sections
above) and their sheet rows have been removed from the table below — the
sheet turned out to have three real errors there, all now corrected in
the confirmed tables: Thunder Lord Incantation's node 3 was listed as
Water Law Learning Speed +4% twice (the actual second Water line, at T6,
is +6%); Square Inch Scripture's node stats were sheet-garbled as PvE/
PvP damage lines when the real stats are Ability DMG Reduction/Respira
Effect/Monster DMG Reduction; Star Blade's T9 was listed as a PvP DMG
Reduction line when it's actually Ability DMG Reduction +3%. R14+ below
is still sheet-only and unverified.

Alias notes (sheet → canonical): "Yang Sword" = Sunset Halberd Dance
(node-for-node match), "Harvest God" = Harvest God Secret, "Honoured
Origin" = Honored Origin, "Control" = Paralysis. Post-R9 sheet names may
themselves be translation/pinyin aliases — recognizable labels, not
confirmed in-game names. Normalized in the apps: "Heavenly Rythum" →
Heavenly Rhythm, "Ying Yang Harmony" → Yin Yang Harmony, "Jade
Reincarnation Tech" → Jade Reincarnation Technique.

Caveats (why the Vault shelves still stop at R9): the sheet is a priority
list, not a catalog — per-rank lists are likely incomplete (for R4–R9 it
covers only 3–6 of each rank's books); max tiers, threshold spacing and
the final "Technique Stats +100%" capstone are not stated (thresholds
below assume learn/3/6/9/12 by analogy); the R10 row said only "MUST
TAKE" with no names — **resolved below**: R10 turns out to be a single
book, Immortal Ascension, now fully cataloged from an in-game screenshot
(the "to Tier 13" figure the apps carried was the sheet/community guide's
imprecise phrasing, not a real threshold — see the R10 section). Shelf
entries beyond R10 still need full-catalog quality — owner will supply
complete details later.

New node families first seen here: elemental-law learning speed
(Metal/Wood/Water/Fire/Earth "law spd"), Qiyun efficiency, DMG to
divine/demonic, and "DF culti" stat lines (sheet shorthand, deliberately
left unexpanded in the apps).

### Sheet data (rank | manual | unlock; T3; T6; T9; T12 | rating | note)

- R14 | Samsara Scripture | PvE dmg reduc +1%; Abode aura +2%; PvE dmg +2%; Crit block +3%; Spiritum +4% | B | take to 2nd unlock
- R14 | Yin Yang Harmony | Water +2%; Fire +4%; Fire +6%; Water +8%; Fire +10% | S | law speed important
- R14 | Chaos Origin | Respira effect +1%; +3%; Respira attempts +1; +7%; +9% | A | Respira central
- R15 | Taisu Scripture | Abode aura +1%; Wood law +4%; Crit block +2%; Wood +8%; Water +10% | A | —
- R15 | Celestial Cloud Scripture | Wood +2%; Metal +4%; Metal +6%; Wood +8%; Metal +10% | S | —
- R15 | Heaven Execution | Crit block +1%; PvP dmg reduc +1%; PvP dmg +2%; PvP reduc +3%; PvP dmg +4% | A | decent PvP, low priority
- R16 | Supreme Heavenly Tao | Respira effect +1%; Spiritum +2%; Respira attempts +1 (sheet types "+1%" — % assumed typo); PvE dmg reduc +3%; PvP dmg +4% | B | decent mix
- R16 | Immortality Cloud | Earth +2%; Wood +4%; Wood +6%; Earth +8%; Wood +10% | S | learning speed important
- R16 | Pure Jade One | Abode aura +1%; aura +2%; PvP dmg +2%; PvP reduc +3%; PvP reduc +4% | S | aura + PvP stats
- R17 | Demonbane Technique | DMG to divine +1%; Divine dmg reduc +1%; Qiyun efficiency +2%; Divine reduc +2%; DMG to divine +3% | A | "you just want t3 unlock" (read: the Qiyun node — its 3rd unlock)
- R17 | Zen Lotus Technique | demonic-side mirror of Demonbane | A | same
- R18 | Sanskrit Chant | Crit block +1%; Crit multi +3%; Crit block +3%; Crit multi +5%; Spiritum +4% | A | decent crit nodes
- R18 | Magnetic Light Maneuver | PvE dmg reduc +1%; Qiyun eff +1%; Qiyun eff +2%; Respira effect +7%; PvP dmg +4% | A+ | double Qiyun nodes
- R19 | Draconic Demon Taming | Dmg to demon +1%; +1%; Qiyun eff +2%; DF culti m.atk +2%; DF culti m.def +4% | A− | first 3 nodes; rest as magicka
- R19 | Jade Reincarnation Technique | Dmg to demon +1%; +1%; DF culti m.atk +2%; DF p.atk +2%; DF p.def +4% | B | same minus Qiyun
- R20 | Book of Forgotten Wishes | (author: "I hate everything in this section, take whatever you like") | — | —
- R21 | Book of Necromancy | PvE dmg reduc +1%; Qiyun eff +1%; PvP relic dmg +2%; DF cult health +3%; Divine dmg reduc +3% | — | —
- R21 | Book of Meditation | Cntrl dura amp +5; DF m.atk +1%; Cntrl chance +10; DF MP +3%; DF relic dmg reduc +3% | C | —

### R4–R9 ratings/notes from the same sheet (nodes all match tables above)

- R4: Golden Core BIS; Astrology BIS; Focus "unlock is good"
- R5: Ninefall BIS; Bloodization "take up to T6"; Solarics "T3 if
  magicka, all the way if corp"
- R6: Yin's Grasp BIS "take to T9"; Conflagration BIS; Unbound Blade
  BIS (both: PvP + aura); Dragon Flight "take to T6"
- R7: Floral Essence BIS; Purify & Cleanse BIS; Great Yang Manual
  "unlock is whatever, everything else good"; Aqua Power PvP "to T6";
  Ninefall Hoarfrost PvP; Sunset Halberd Dance ("Yang Sword") PvP
- R8: Tao of Taiqing S+ (magicka); Astral Arcanum S+; Chroma S+ ("if
  you don't take you'll fall behind"); Origin Scripture A (corp
  all-rounder); Zixiao Sutra B ("take the first two nodes")
- R9: Harvest God Secret S+; Divine Water A+ (magicka PvP); Honored
  Origin A (bought for aura); Heartless A (corp PvP); Laws of Nature B
  ("grab the first node")

## Threshold resolution (settled — not open questions)

Every shipped book's tier thresholds are the positional convention
(learn / T3 / T6 / T9 / T12 / T15), which was validated against the two
books whose thresholds were independently known (Dragon Flight pill +2%
@ T3, Great Yang Manual pill +4% @ T9 — both matched). Owner-directed
2026-07-18: **these are the answers.** Completed books do not display
their thresholds in game, so they are unscreenshotable on this account —
the positional inference stands as final, not pending verification. Do
NOT re-list Golden Core / Astrology / Cosmic Power / Taiyin Meridian /
Yin's Grasp / Floral Essence / Great Yang (or any completed book) as a
data gap. If a fresh account ever surfaces a contradicting tooltip, that
is the only thing that reopens it.

Friend payoffs are likewise resolved from the community guide (White
Astra 31 pill-EXP + Daemonfae quest, Adalinda 81 Law-Fruit growth,
Leizhenzi 129 pill +3%, and the Iron Fan / Daji / Macaque / Jiang Ziya /
Taotie / Shen Gongbao / Crane Boy lines already in the catalog).

## R10: Immortal Ascension (confirmed, 2026-07-28 screenshot)

Owner's account (Incarnation (M) Late 46.6%, Technique Rating 157.45M),
two screenshots: the R10 shelf and the book's own detail page. The R10
shelf holds exactly **one** Universal book, confirming the sheet's
"MUST TAKE" single-book note — not an incomplete list.

- **Immortal Ascension**, Technique Rating 14.22M, currently Tier 12/15
  ("T12 Bottleneck"). Node order (learn/T3/T6/T9/T12/T15, same threshold
  pattern as R8/R9 — the four shown `[Activated]` are positional, not
  tier-labeled, per the completed-book tier-label caveat above):
  1. Base HP +2%
  2. Base MP +2%
  3. Base Abode Aura +3%
  4. Spiritium from Realms +3%
  5. **[Tier 12]** Daily Cultivation Pill Attempts +1
  6. **[Tier 15]** Technique Stats +100% (the universal capstone)
- The 2026 community guide's "take Immortal Ascension to Tier 13" doesn't
  land on a labeled threshold here (nothing changes between T12 and T15) —
  most likely means "past the T12 pill-attempt payoff," not a distinct
  T13 node. Node 5 (T12, +1 daily pill attempt) is the cultivation-relevant
  payoff; node 6 (T15) is stats-only.

## Still genuinely open (R14+, needs a fresh in-game catalog, not a gap
in completed content)

- R11–R13 are now fully cataloged (screenshot pass 2026-08-20, see
  above); Square Inch Scripture's learn/T3 lines were missed in that
  pass and confirmed by the owner directly instead: learn DMG Bonus to
  Monsters +1%, T3 Ability DMG to Taoists +1%.
- Post-R13 manuals: complete per-rank catalogs, max tiers, capstone nodes
  and confirmed in-game names — required before the Vault extends past R13.
