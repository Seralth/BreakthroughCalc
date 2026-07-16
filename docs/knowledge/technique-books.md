# Universal technique books — full catalog (screenshot pass 2026-07-15)

Source of truth: 82 phone screenshots taken 2026-07-15/16 (owner's account,
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
- **Longevity**: learn → Base Abode Aura +1%; ? → Respira Attempts +1

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
- **Lion's Roar** (explicit): learn Respira Effect +1%; T3 Spiritium from Realms +2%; T6 Sense +2; T9 DMG Bonus to Monsters +2%; T12 Technique Stats +100% (T12 line cut off in shot; inferred by pattern)
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

## Open questions

- R1–R5 max tiers and mid thresholds (see caveat above).
- Lion's Roar final line (assumed T12 Technique Stats +100%; cut off).
- Exclusive-tab books: entirely undocumented (stats-only per owner).
- Spirit/immortal-world manuals beyond R9: not yet visible on this account.
