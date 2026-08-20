# Monsterscape — Bloodline Refinement reward tracker (Voidbreak+)

Monsterscape is a Voidbreak-unlocked system (owner, 2026-08-20). Its
reward tracker is the **"Refine Blood" / "Bloodline Refinement Stats
Overview"** screen — screenshot pass 2026-08-20 captured this tracker in
full; the rest of Monsterscape itself (the actual monster-hunting/combat
loop that earns Bloodstones) was not screenshotted this pass. Not yet in
this repo's docs anywhere before this file.

## Sources

- Screenshot pass 2026-08-20 (owner's live account): two screenshots of
  the "Refine Blood" tracker. Treat the tracker's own numbers as
  CONFIRMED; everything about how Bloodstones are actually earned
  (the Monsterscape gameplay loop itself) is unscreenshotted and open.

## Refine Blood / Bloodline Refinement — CONFIRMED (screenshot, 2026-08-20)

Header: "Refine Blood". Subtitle: *"Consume Bloodstones to enhance
autoplay rewards."* Currency: **Bloodstones** (owner's balance at
capture: 130.9K). Total BR (Bloodline Refinement?) stat shown: 67600.

A rank ladder, R1 through at least R14 (R11+ partially cut off in the
capture — confirm ceiling on a future pass), each rank consuming an
escalating Bloodstone cost to unlock one effect. All ranks shown
"Activated" on the owner's account:

| Rank | Cost (as shown) | Effect |
|---|---|---|
| R1 | 8.12M / 900K | **Cultivation Speed +10%** |
| R2 | 8.12M / 1.6M | Quality Boost of Monster Materials +12% |
| R3 | 8.12M / 1.8M | Quality Boost of Monster Cores +12% |
| R4 | 8.12M / 2.4M | Bloodstone Drop Quantity +10% |
| R5 | 8.12M / 3M | **Cultivation Speed +15%** |
| R6 | 8.12M / 3.2M | Unlock Auto Add Demonlure |
| R7 | 8.12M / 3.6M | **Cultivation Speed +20%** |
| R8 | 8.12M / 4M | Bloodstone Drop Quantity +20% |
| R9 | 8.12M / 4.5M | Colossus Effect +25% |
| R10 | 8.12M / 5.5M | Autoplay Time Limit +240m |
| R11 | 8.12M / 6M | Colossus Effect +25% (2nd instance) |
| R12 | 8.12M / 7M | Demonlure Efficiency +35% |
| R13 | 8.12M / 7.5M | Autoplay Time Limit +240m (2nd instance) |
| R14 | 8.12M / 8M | **Cultivation Speed +25%** |

The "8.12M" half of each cost is identical across every rank shown —
plausibly a second resource (not Bloodstones) that's already maxed/not
the actual gating cost, or a display quirk; not resolved, flag for a
follow-up screenshot at a non-maxed rank to clarify what varies vs. what
doesn't.

**Correction (owner, 2026-08-20): the "Bloodline: Completion" section
described in an earlier pass of this doc doesn't exist as a distinct
mechanic.** It was a screenshot-reading artifact — a shaded/dimmed
section visible behind the rank-list popup, belonging to the page
underneath it, redisplaying the owner's most-recently-unlocked rank
(R14, Cultivation Speed +25%) rather than showing some separate
"completion bonus." There is no fifth, completion-only effect.

**Cultivation Speed total — CONFIRMED (owner, 2026-08-20): live banner
reads +70%, exactly R1+R5+R7+R14 (10+15+20+25).** No other rank or
section contributes to it.

**Not a calc engine input, and doesn't need independent verification
either (owner, 2026-08-20).** This +70% isn't a discrete lever the
player toggles or a bonus displayed as its own line anywhere — owner
states it's baked directly into the flat on-screen Cultivation Speed
number (account currently reads 469.58/Cosmoapsis). Whether or not
that's literally true doesn't matter for the calc: `engine.py`/
`engine.dart` only ever take Cultivation Speed as one flat user-entered
number (see the file header comment: "cultivation speed (user input) is
the XP gained per Cosmoapsis at the CURRENT grade" — the engine never
decomposes it). **Any effect that changes the flat Speed number —
Monsterscape included — is automatically captured just by the user
re-entering their current on-screen Speed, with zero special-casing
needed.** This is the general reason Monsterscape needs no engine
change at all, not specific to this one system — same as any other
speed-affecting mechanic the game might add in the future. This doc
entry is reference material only, explaining part of *why* the flat
speed number is what it is. Contrast with Aura Gem, which genuinely is
a togglable engine input (a separate multiplier layered on top of
Speed, not baked into it) and Absorption Ratio, which is a distinct
second input used only to project future-grade speed, not to explain
the current one.

Undefined terms introduced by this ladder, not explained on this screen:
**Demonlure**, **Colossus Effect**, **Monster Materials**, **Monster
Cores** (Monster Materials/Cores get their own quality-boost ranks here,
R2/R3, but what they're used for isn't shown). All open questions for a
future Monsterscape-proper screenshot pass (the actual hunting/combat
screen, not just this reward tracker).

## Open questions

- What is the actual Monsterscape gameplay loop (how Bloodstones are
  earned) — this doc only covers the reward-spending tracker.
- Does the R1-R14 ladder go past R14, and what's the true cost/effect
  for R11-R13 (partially cut off in the capture)?
- What do Demonlure and Colossus Effect actually do mechanically?
- What are Monster Materials/Monster Cores used for (crafting? another
  system entirely?), and is either related to the Garden's crop items
  (`elemental-laws-garden-mechanics.md`) or to Zodiac Relic/equipment
  crafting (`zodiac-relic.md`, `equipment-relics.md`)?
- Why is the "8.12M" cost component identical across all 14 ranks —
  separate resource, or display artifact?
