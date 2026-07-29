# Elemental Laws & Law Fruit garden mechanics (Spiritual World / Voidbreak)

Not yet in the calc. Spiritual World content gated behind Voidbreak; Elemental
Laws (five elements: Metal/Wood/Water/Fire/Earth) level up on Law Points,
which come from consuming ("Blitzing") garden-grown Law Fruit.

## Sources

- **G1** — grindnstrat.com "Overmortal Spiritual World Guide," Law Fruits
  section (grindnstrat.com/overmortal-spiritual-world-guide/#Law_Fruits).
  Community guide; prose claims are community-tier, not screenshot-verified,
  except where noted below.
- Three images embedded in G1 are direct screenshots of actual game UI
  (Law Fruit Seed tooltip, Elemental Laws main screen, Blitz Laws popup).
  Treat the *numbers* in these as confirmed even though the guide's
  surrounding prose commentary is only community-tier.
- Everything else below (Red tier / Shears relic, the Garden Pot artifact,
  pet daily speed-up spawns, 6x6 grid + Ploughwood footprint) is owner
  direct-knowledge (Seralth, 2026-07-29), not re-screenshotted this session
  but treated as ground truth per house convention (direct observation
  overrides guide/community sources).
- The throughput figures under Analysis are DERIVED from the confirmed
  inputs above via exact math, not independently observed — flagged
  separately from raw fact.

## Law Fruit tiers — CONFIRMED (screenshot, G1 tooltip)

Single item "Law Fruit Seed"; grows into one of four natural rarities
(道法果, "Dao-Law Fruit"):

| Tier | Growth time |
|---|---|
| Green | 4 hours |
| Blue | 16 hours |
| Purple | 1 day 16 hours (40h) |
| Yellow | 3 days 16 hours (88h) |

Seed obtained from multiple sources including Sect Library 6F (unlocks at
Voidbreak); visually resembles a Ploughwood Seed (G1). A "Ripen" button in
the tooltip UI confirms grow-time speed-up items apply here.

## Blitz mechanic — CONFIRMED (screenshot, G1 "Blitz Laws" popup)

Consuming a fruit converts it into a fixed number of hours of Elemental Law
learning progress ("Blitz"):

| Tier | Blitz value |
|---|---|
| Green | 1h |
| Blue | 3h |
| Purple | 6h |
| Yellow | 12h |
| Red | 14h (see below — not a natural growth tier) |

UI shows **"Remaining Time: 120h"** — confirms G1's claimed 120h/day Blitz
cap as a real displayed budget — plus an "Auto Blitz" toggle.

## Red tier — not a natural growth tier (Seralth, 2026-07-29)

The Blitz popup shows a 5th (Red) tier that G1's text never mentions. Resolved:
Red isn't grown — it's produced by the **Shears** relic, which spends energy
to advance an existing fruit up to Red. Red fruit's 14h Blitz value is
**exempt from the 120h/day cap** (same exemption pattern as Pills).

## Garden Pot artifact (Seralth, 2026-07-29)

**Disambiguation:** this is a third, unrelated system that happens to share
the English word "pot" with two existing curios already in this repo —
**Zodiac Pot** (三相之壶, curio 91359, see `zodiac-relic.md`) and
**Dongxuan's Pot** (curio 91115, see `curio-effects.md`). Do not conflate.

The Garden Pot is a growth-speed-up artifact, not Law-Fruit-specific
(applies to garden plants generally):

- 1 energy spent = 1 hour of growth speed-up; also raises a plant's
  "quality limit" (the max tier it can reach).
- Energy regen is denominated in Taoist years — 1 Taoist year = 15 real
  minutes (see `game-mechanics-verified.md`'s core-mechanics note). 0-star
  grants +1 energy/year (= 4/hour = 96/day), capped at 200. Owner's Pot is
  currently **1-star**: +1.3 energy/year (= 5.2/hour = **124.8/day**), cap
  **300**, plus a flat **+15%** speed-up bonus on top.
- Energy can also be gained via "charge" — mechanism not detailed this
  session (open question).
- A 100-energy lump spend forces Red-tier evolution, but only for
  **gear-crafting plants**, NOT Law Fruit. Law Fruit's Red-tier path is the
  separate Shears relic above.

## Pet system daily speed-up spawns (Seralth, 2026-07-29)

Once-a-day spawn of generic (non-energy) speed-up items, distinct from the
Pot's energy-based speed-up. Spawn count scales with pets owned, capped at
10 pets. Owner's current banked stockpile: ~64h19m, accumulated over 2-3
days.

## Garden grid (Seralth, 2026-07-29)

Full unlock is a **6x6 grid** (36 cells); slots are purchased one at a time
at increasing cost from a smaller starting size. (Starting size is
unrecoverable/unknown and irrelevant — see Analysis: only the fully-unlocked
end state matters strategically.) Ploughwood Seeds occupy a **3-cell
L-tromino** footprint. **CONFIRMED (Seralth, 2026-07-29):** Law Fruit Seeds
share this same 3-cell L-tromino footprint, not just a visual resemblance.

## Pot-energy throughput ceiling — derived (2026-07-29)

Scenario: fully-unlocked 6x6 garden (12 seed slots), owner's 1-star Pot,
**no** pet speed-up items, all-Green (Green has the best Blitz-per-grow-hour
ratio of any tier — see Analysis — so it's optimal to concentrate both slots
and Pot energy there).

- Zero-energy baseline: 12 slots × (24h ÷ 4h/cycle) × 1h Blitz = **72
  Blitz-hours/day**.
- Solving for the optimal per-cycle time-shave given a fixed daily energy
  income (not just a linear add-on — shrinking cycles means more of them
  need shaving per day) collapses to a clean closed form:
  `daily Blitz-hours = (24 × slots + energy/day × bonus) ÷ natural grow time`
  `= (288 + 124.8 × 1.15) ÷ 4 = 107.88 Blitz-hours/day`.
- That implies each Green cycle runs at effectively ~2.67h instead of the
  natural 4h once all 124.8 energy/day is continuously reinvested across
  the 12 slots (~107.9 harvests/day).
- **Result: Pot energy alone (no pet items, no Shears/Red) closes ~75% of
  the 72→120h/day gap**, landing at ~108/day, ~12h/day short of the cap.
- Caveat: assumes continuous/fractional energy spend and no floor on
  cycle time — the real game likely spends energy in whole-number chunks
  and may have a minimum grow-time floor, so the true ceiling is probably
  slightly under 107.88.

## Analysis: throughput math & guide-claim fact-check (2026-07-29)

Cross-checking G1's strategic prose against the confirmed numbers above:

- **"Prioritize green, avoid yellow" (G1) — only conditionally true.**
  Blitz-hours per grow-hour: Green 0.25, Blue 0.1875, Purple 0.15, Yellow
  0.136 — Green wins if **garden cell-time** is the binding constraint.
  But Blitz-hours per **seed**: Green 1, Blue 3, Purple 6, Yellow 12 — the
  exact opposite ranking, which wins if **seed supply** is the binding
  constraint instead. G1 never discloses which constraint it's assuming, so
  its blanket rule is incomplete, not universally correct.
- **"Eat fruit one-by-one, upgrade immediately" (G1) — no observed
  mechanical basis.** No Law-Point storage cap or decay has been observed
  that would make immediate-spend beat batch-spend; if Law Points are a
  plain currency, order of operations is mathematically irrelevant to
  total output. Treat as unverified ritual, not a mechanic, unless a
  storage cap turns up.
- **Max theoretical garden throughput falls short of the daily cap.** Full
  6x6 (12 seed slots @ 3 cells/seed), all-Green, natural (non-boosted)
  grow speed: **72 Blitz-hours/day** — 40% short of the 120h/day cap even
  at full dedication and perfect packing. Every other tier tops out lower
  than Green at max packing, so 72/day is the organic ceiling.
- Pot energy alone (see above) closes most of that gap, to **~108/day**.
  The remaining ~12h/day is plausibly covered by banked pet-spawned
  speed-up items and/or occasional Shears/Red conversion (cap-exempt) —
  not concluded which dominates, or whether either fully closes it.
- **Strategic conclusion:** garden-slot unlock is a flat, area-scaling
  throughput multiplier that dwarfs any fruit-tier optimization G1
  discusses. Since Law Fruit only becomes usable at Voidbreak, and
  Elemental Laws are G1's own pick for "the most important feature of
  Voidbreak," any garden slot not purchased before reaching Voidbreak is
  permanently lost throughput for however long it stays unbought — there's
  no way to retroactively recover missed Elemental Law levels. Fully
  unlocking the garden pre-Voidbreak is higher-leverage than any
  fruit-tier strategy.

## Open questions

- Is the garden single-purpose per plot, or do other crop types compete for
  the same 36 cells concurrently (reducing effective Law-Fruit capacity
  below the theoretical 12-slot max)?
- What exactly closes the remaining ~12h/day gap between the Pot-boosted
  ~108/day ceiling and the 120h/day cap — pet speed-ups, Shears/Red
  conversion, both, or an uncatalogued additional fruit source (Sect
  Library rewards, shop, events)?
- Does energy actually spend continuously/fractionally in-game, or in
  discrete chunks with a grow-time floor? Affects how close to the 107.88
  theoretical ceiling is reachable in practice.
- Pot artifact "charge" energy source — mechanism not detailed this
  session.
