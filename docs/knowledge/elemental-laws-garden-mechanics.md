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

**Full unlock is a 6×6 grid, 36 cells — confirmed by pixel-level
inspection of the owner's own reference layout images**
(`~/Pictures/omvault-2026-08-11-garden/layout_8fruit_3vine.png`,
`layout_6fruit_4vine.png`, `layout_4fruit_6vine.png`; these are the
owner's own planning mockups, not in-game screenshots, but their
legends and grid geometry are ground truth for footprint shapes).

**Law Fruit and Ploughwood are a 3-cell L-tromino** (an L made from a
2×2 block minus one corner). **Soulrend Vine is a 4-cell shape — a
straight line of 3 cells plus one bump off the middle cell**,
perpendicular to the line (a T-tetromino). This is the fact that was
wrong in every earlier pass of this doc: Vine does NOT share Law
Fruit's 3-cell footprint. Verified by sampling cell colors from
`layout_8fruit_3vine.png` pixel-by-pixel and confirming three
independent 4-cell groups (V1/V2/V3) against eight independent 3-cell
groups (F1–F8), matching the image's own legend text exactly.

**Max plant count is NOT a fixed number — it depends on the crop mix**,
because Vine costs more cells per plant than Fruit/Ploughwood:
- All-Law-Fruit (or all-Ploughwood) grid: 36 ÷ 3 = **12 plants**.
- All-Vine grid: 36 ÷ 4 = **9 plants**.
- Any mix in between lands somewhere in that range — e.g. the owner's
  live 6 Fruit / 3 Vine / 2 Ploughwood totals 6×3 + 3×4 + 2×3 = 36
  cells exactly (11 plants, zero cells left over), which is why "11,
  all slots filled" and "12 is the cell-math ceiling" are both true at
  once — they're answers to different questions (this specific mix's
  plant count vs. the grid's per-crop-type cell capacity).

## The other two crop types

- **Ploughwood**: Zodiac Relic upgrade material (`zodiac-relic.md`).
  Fixed, single-tier item — unlike Law Fruit/the gear-crafting crop
  below, it doesn't have a growth-quality ladder. Shares Law Fruit's
  3-cell L-tromino footprint.
- **Gear-crafting crop** (Voidbreak-stage name: **Soulrend Vine**):
  gear/relic crafting material, adds a quality-boost chance per craft.
  Five tiers (Aged → Centa → Milia → Myrua → Decamyriad), each tier's
  own boost % — visible on the item tooltip in-game, not reproduced
  here. Top tier needs an item called the **Azryn Pot** to energize —
  likely the same artifact as the "Garden Pot" above, name not yet
  cross-confirmed. **Owner (2026-08-20): this crop is not unique to
  Voidbreak — every World stage has its own equivalent gear-crafting
  garden crop under its own name**, "Soulrend Vine" is just the
  Voidbreak-stage instance. **4-cell footprint** (see above) — do NOT
  describe it as sharing Law Fruit's 3-cell shape. **Owner (2026-08-21):
  don't name "Soulrend Vine" in user-facing Reference/Guide prose at
  all** — not even as a "Voidbreak's version is called X" aside. Calling
  out the Voidbreak-specific name implies Voidbreak is somehow the
  relevant stage, when the mechanic (crop, footprint, seed behavior) is
  identical at every World stage. Just say "the gear-crafting crop" and
  stop there; "Soulrend Vine" stays a doc-internal fact for citing
  sources, not something the app prints.

## Seed supply — the real constraint (owner, 2026-08-20)

**Reliable income: 20 Law Fruit Seeds/week from the Sect. Plan around
this number only** — other sources exist (some P2W, some raw-fruit
drops) but added only ~20-30 total across 2 live weeks of Voidbreak,
too unreliable to plan around.

This is the actual bottleneck, not garden cell-time or Pot energy: at
Purple's 6 Blitz-hours/seed, 20 seeds/week caps real throughput at ~17
Blitz-hours/day — far under the 72–108/day the cell-time/Pot-energy
math below would suggest is achievable for a garden dedicated entirely
to Law Fruit. **Grow Purple by default** (best Blitz-hours-per-seed);
Green only as a top-off once Purple has already filled the day's cap
and the weekly seed reset is close. Blue and Yellow are skipped —
worse than Purple per-seed for no offsetting benefit once seed count
is the binding constraint.

**Strategic conclusion:** garden-slot count stops mattering for Law
Fruit specifically once you have enough slots to plant a week's worth
of Purple seeds — a handful, not the full 12-slot buildout a
dedicated-Fruit grid could hold. Extra slots are better spent on
Ploughwood or the gear-crafting crop, which don't share Law Fruit's
seed scarcity — even though Vine's bigger 4-cell footprint means those
"extra slots" buy fewer Vine plants than the equivalent cell-count in
Fruit or Ploughwood would. Still fully unlock the garden pre-Voidbreak
(you want the option to run every crop type), just don't dedicate the
whole thing to Law Fruit once seed scarcity is accounted for.

**Owner's live allocation, for reference (a working example layout —
fully-unlocked garden, all 36 cells filled, no cells left over):** 6
Law Fruit / 3 gear-crafting crop / 2 Ploughwood = 11 plants total
(6×3 + 3×4 + 2×3 = 36 cells exactly). 6 Law Fruit maxes the daily
Blitz cap; 3 gear-crafting crop slots keep steady crafting supply; 2
Ploughwood isn't enough alone but stretches fine alongside the Zodiac
Relic's own event rewards (every 3 weeks). Players not investing in
the Zodiac Relic can swap the 2 Ploughwood slots for more Law Fruit
instead (which would buy 3 more Fruit plants per 2 Ploughwood removed,
since both share the 3-cell footprint 1:1).

## Watering (owner, 2026-08-20/21)

**Baseline is 1 free watering/day from the garden itself.** The **Sword
Trio set bonus** adds **+1 free watering/day** on top of that, for
**2 free waterings/day** once the set bonus is active. **Each watering
skips every planted seed forward 3 hours** — it's a flat time-skip
applied garden-wide per use, not per-plant.

Even with the Sword Trio bonus, 2 free waterings/day (6 hours skipped)
is **not enough by itself** to keep a Purple-heavy Law Fruit lineup
running at full seed throughput — this is why the extra sources below
matter, and why the garden matters more the less you're willing to pay:
growth time can't be skipped for free beyond those free waterings.

- **The first paid watering is very cheap** and worth buying every day
  regardless of spend level — good value even for an otherwise F2P
  account.
- **Various companions/NPCs** can add extra skip-time to each watering,
  or reduce a plant's required grow time outright (a flat reduction,
  not a per-watering skip) — worth watching for as you unlock
  companions; specific names/breakpoints not catalogued yet.
- **Pets give some free grow-time-skip every day** — only the amount
  varies, so don't count on a specific number. Various other daily
  sources add more on top, same caveat.

## Filling the daily Blitz cap without over-relying on the garden (owner, 2026-08-20)

The garden's own Purple-seed throughput (~17 Blitz-hours/day, see
above) is well under what a fully-invested Blitz routine can use. **The
daily "tea party" event (and other minor daily sources) grants Law
Fruit directly**, independent of the garden — in practice these direct
grants are *required* to fill out the daily Blitz cap, since the
garden alone is unlikely to produce enough fruit every single day
without paying.

**The Pot Creation Artifact is very strong here if you pull it**: on
top of its per-energy grow-time-shaving effect (above), it provides a
reliably large amount of time-skip every day, which is one of the
better ways to close the gap between the garden's raw seed-bound
output and what a maxed daily Blitz routine wants.

## Cell-time/Pot-energy throughput ceiling — derived math, now secondary to seed supply above

Kept for the underlying math (still correct as a *cell-time* ceiling,
just not the actual binding constraint): fully-unlocked garden
dedicated entirely to Law Fruit (12 slots at the 3-cell footprint —
see the corrected footprint math above; this ceiling drops if any
cells go to Vine instead, since Vine's 4-cell footprint buys fewer
plants per cell), all-Green, no Pot energy — zero-energy baseline is
72 Blitz-hours/day; the owner's 124.8 energy/day (×1.15 bonus) pushes
that to `(288 + 124.8×1.15) ÷ 4 ≈ 108 Blitz-hours/day`, closing ~75%
of the gap to the 120h/day cap. Green wins this per-cell-hour comparison
(0.25 Blitz-hours/grow-hour vs. 0.1875/0.15/0.136 for Blue/Purple/
Yellow) — the opposite ranking from the per-seed comparison that
actually governs strategy now that seed supply binds first.
