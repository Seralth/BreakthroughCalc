# Elemental Laws & Law Fruit garden mechanics (Spiritual World / Voidbreak)

Not yet in the calc's math (no engine.py/engine.dart modeling, no input
fields). Elemental Laws (Metal/Wood/Water/Fire/Earth) level up on Law
Points, earned passively and via consuming ("Blitzing") garden-grown
Law Fruit. Law Points also feed Cosmic Laws (shared pool — level
Elemental Laws first, it raises the shared income rate). Full mechanic
detail, tier tables, and exact bonus numbers are all visible in-game on
the Elemental Laws / Cosmic Laws screens — this doc only records what
ISN'T visible there: hidden formulas, cross-system interactions, and
derived strategy.

## Blitz mechanic

A fruit converts to N hours of Learning Speed progress at the element's
*current* rate — not a flat Law-Point sum (confirmed: owner's 38.3M/h
Metal speed → one Green fruit = 38.3M Law Pts). Since Learning Speed
rises with level, a fixed Blitz-hour value pays out more over time —
this is the reasoning behind "interleave, don't batch" fruit-eating.
120h/day cap; Red tier (14h, via the Shears relic) is exempt from it.
Auto Blitz unlocks at total Elemental Laws level 50 (summed across all
5, not per-element).

## Learning-speed milestones & Suppression Resonance — general mechanic only

Two separate milestone tracks per element, both visible in-game: one
doubles Learning Speed at set levels (owner confirms literal ×2, e.g.
10→20 Wood speed), the other unlocks alternating Suppression
Boost/Resist at set levels, capping in a "Completely Activated" bonus
at the top. Exact levels and values are on the in-game screen — not
reproduced here.

The Suppression track runs in two grades, G1 then G2, each a full
1000 levels per element — G2 doesn't start until G1 hits 1000 (owner,
2026-08-20; not obvious from a partially-scrolled screenshot). So
fully maxing it out needs each element at level 2000, or **10,000
summed Total Elemental Laws Level** across all five to complete both
grades everywhere.

## Law Suppression

The whole point of leveling Laws, so it's worth defining even though
most of this system is otherwise skipped in this doc: compare **total**
Elemental Law level (summed across all 5 elements) against a target's
total — every level of advantage deals **+0.05% additional final
damage** (in-game tooltip, confirmed). **There is no cap** — a
+30%-at-600-levels cap claim from three community sources (dating back
to this doc's original 2026-07 version) was retracted 2026-08-20: owner
doesn't see it anywhere in-game, and it doesn't line up with anything
in this pass's screenshots. Don't reintroduce it.

**PvP vs. PvE scope**: owner's grounded read — Suppression is PvP-only
(no PvE content references "law levels" as an enemy stat). Practically
moot either way; Laws are leveled for PvP regardless.

## Red tier & the Shears relic

Red isn't grown — the **Shears** relic (a Creation Artifact, see
`relic-summon-costs.md` for how it's acquired) spends energy to push an
existing fruit to Red. Red's 14h Blitz value is cap-exempt.

## Garden Pot artifact

A Creation Artifact (`relic-summon-costs.md`), distinct from the
unrelated Zodiac Pot curio and Dongxuan's Pot curio — three separate
"Pot" items, don't conflate them. Two effects: (1) energy → growth-speed
reduction, applies to everything including Law Fruit; (2) energy also
raises gear-crafting plants' quality ceiling from Purple to Yellow —
does NOT apply to Law Fruit, whose tier ceiling is fixed regardless of
Pot energy (Red still needs Shears). Owner's Pot: 1-star, 124.8
energy/day, 300 cap, +15% speed-up bonus — these numbers feed the
throughput math below.

## Garden grid & footprint

Full unlock is a 6×6 grid (36 cells). Law Fruit, Ploughwood, and
Soulrend Vine seeds all share a **3-cell L-tromino footprint**
(confirmed both by direct observation and, in an 2026-08-11 screenshot,
by the visual connecting-bridge between grouped cells and duplicate
countdown timers appearing on more than one cell of the same plant —
useful tell if reading a garden screenshot again).

## The other two crop types

- **Ploughwood**: Zodiac Relic upgrade material (`zodiac-relic.md`).
  Fixed, single-tier item — unlike Law Fruit/Soulrend Vine, it doesn't
  have a growth-quality ladder.
- **Soulrend Vine**: Voidbreak-stage gear/relic crafting material, adds
  a quality-boost chance per craft. Five tiers (Aged → Centa → Milia →
  Myrua → Decamyriad), each tier's own boost % — visible on the item
  tooltip in-game, not reproduced here. Top tier needs an item called
  the **Azryn Pot** to energize — likely the same artifact as the
  "Garden Pot" above, name not yet cross-confirmed.

Both share the garden's 36 cells and the same 3-cell footprint as Law
Fruit.

## Seed supply — the real constraint (owner, 2026-08-20)

**Reliable income: 20 Law Fruit Seeds/week from the Sect. Plan around
this number only** — other sources exist (some P2W, some raw-fruit
drops) but added only ~20-30 total across 2 live weeks of Voidbreak,
too unreliable to plan around.

This is the actual bottleneck, not garden cell-time or Pot energy: at
Purple's 6 Blitz-hours/seed, 20 seeds/week caps real throughput at ~17
Blitz-hours/day — far under the 72-108/day the cell-time/Pot-energy
math below would suggest is achievable. **Grow Purple by default**
(best Blitz-hours-per-seed); Green only as a top-off once Purple has
already filled the day's cap and the weekly seed reset is close. Blue
and Yellow are skipped — worse than Purple per-seed for no offsetting
benefit once seed count is the binding constraint.

**Strategic conclusion:** garden-slot count stops mattering for Law
Fruit specifically once you have enough slots to plant a week's worth
of Purple seeds — a handful, not the full 12-slot buildout. Extra slots
are better spent on Ploughwood or Soulrend Vine, which don't share Law
Fruit's seed scarcity. Still fully unlock the garden pre-Voidbreak (you
want the option to run every crop type), just don't dedicate the whole
thing to Law Fruit once seed scarcity is accounted for.

**Owner's live allocation, for reference:** 6 Law Fruit / 3 Soulrend
Vine / 2 Ploughwood, on a partially-unlocked grid. 6 Law Fruit maxes
the daily Blitz cap; 3 Soulrend Vine keeps steady gear-crafting supply;
2 Ploughwood isn't enough alone but stretches fine alongside the Zodiac
Relic's own event rewards (every 3 weeks). Players not investing in the
Zodiac Relic can swap the 2 Ploughwood slots for more Law Fruit instead.

## Cell-time/Pot-energy throughput ceiling — derived math, now secondary to seed supply above

Kept for the underlying math (still correct as a *cell-time* ceiling,
just not the actual binding constraint): fully-unlocked 6×6 garden
(12 seed slots), all-Green, no pet items — zero-energy baseline is 72
Blitz-hours/day; the owner's 124.8 energy/day (×1.15 bonus) pushes that
to `(288 + 124.8×1.15) ÷ 4 ≈ 108 Blitz-hours/day`, closing ~75% of the
gap to the 120h/day cap. Green wins this per-cell-hour comparison
(0.25 Blitz-hours/grow-hour vs. 0.1875/0.15/0.136 for Blue/Purple/
Yellow) — the opposite ranking from the per-seed comparison that
actually governs strategy now that seed supply binds first.
