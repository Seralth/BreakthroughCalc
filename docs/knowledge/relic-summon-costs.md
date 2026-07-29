# Relic summon system — cumulative point track

Distinct from Equipment Relics (`equipment-relics.md`) and the Zodiac Relic
(`zodiac-relic.md`) — this is the monetization/point-track system that grants
those 8 relic items, not the relics' own stat mechanics.

## Core mechanic: breakpoints, not a per-pull gacha

Points accumulate on a single running total and are **never spent or
consumed**. Crossing each breakpoint grants that relic and progress
continues toward the next one — this is a milestone/battle-pass shape, not
a gacha where each pull costs points. Practical consequence: the only cost
that matters is reaching the **highest** breakpoint you want; every relic
below it arrives for free along the way.

Cosmetic rewards also sit on the same point track at other values —
intentionally out of scope here (owner: don't care about those for now).

### Relic breakpoints (owner-provided, cumulative points)

| Relic | Points |
|---|---|
| Vase | 5,000 |
| Pot | 10,000 |
| Mirror | 20,000 |
| Token | 40,000 |
| Sheers | 70,000 |
| Cauldron | 88,888 |
| Basin | 128,888 |
| Pearl | 158,888 |

## Point sources

- **Creation draw**: 10 points per draw, earned via in-game play/currency
  (not real money).
- **Direct purchase (App Store IAP)**: fixed point yield per real-money
  tier, confirmed by owner:

  | Tier | Points | Rate (pts/$) |
  |---|---|---|
  | $0.99 | 6 | 6.061 |
  | $4.99 | 30 | 6.012 |
  | $9.99 | 68 | **6.807** (best known tier) |
  | $19.99 | 128 | 6.403 (worst known tier) |
  | $29.99 | 198 | 6.602 |
  | $49.99 | 328 | 6.561 |
  | $99.99 | 648 | 6.481 |

  $99.99 is the largest single IAP SKU seen (owner-confirmed) — there is no
  bigger single tier; event offers instead cap at up to 10× $99.99 packs
  rather than one larger bundle. The curve is **not monotonic**: $9.99 beats
  every other tier, and $19.99 — despite sitting right next to it — is
  actually the single worst-value tier of the seven.

- **Voucher-funded purchase**: the same IAP tiers above can alternatively be
  paid for with SEAGM top-up vouchers instead of cash, and doing so applies
  a flat **1.1× bonus** to that tier's point yield. Voucher cost per tier
  (owner-provided):

  | Tier | Vouchers | Points (base × 1.1) |
  |---|---|---|
  | $0.99 | 600 | 6.6 |
  | $4.99 | 3,000 | 33 |
  | $9.99 | 6,800 | 74.8 |
  | $19.99 | 12,800 | 140.8 |
  | $29.99 | 19,800 | 217.8 |
  | $49.99 | 32,800 | 360.8 |
  | $99.99 | 64,800 | 712.8 |

  Every one of these seven tiers reduces to the exact same ratio:
  **1,000 vouchers = 11 points** (1 voucher = 0.011 points, ≈90.909
  vouchers/point). Confirmed exact across all seven data points — treat as a
  fixed conversion constant, not an approximation.

## SEAGM voucher pricing (screenshot-verified, 2026-07-29, laptop)

SEAGM sells the same "Vouchers" currency directly for cash, at bundle
pricing that does NOT scale linearly — bigger bundles are usually but not
always a better rate, plateauing at ~699.5 vouchers/$ from the $199.99 tier
up (no further bulk bonus above that).

| Vouchers | Price (USD) | Rate (vouchers/$) |
|---|---|---|
| 600 | 0.99 | 606.06 |
| 6,900 | 9.99 | 690.69 |
| 10,000 | 14.99 | 667.11 |
| 13,500 | 19.99 | 675.34 |
| 19,000 | 27.99 | 678.81 |
| 20,500 | 29.99 | 683.56 |
| 33,800 | 49.99 | 676.14 |
| 68,000 | 99.99 | 680.07 |
| 138,000 | 199.99 | 690.03 |
| 208,300 | 299.99 | 694.36 |
| 419,700 | 599.99 | 699.51 |
| 699,500 | 999.99 | 699.51 |
| 2,098,520 | 2,999.99 | 699.51 |

Note the rate isn't strictly monotonic (6,900 beats the pricier 10,000
tier; 20,500 beats the pricier 33,800 tier) — worth checking the table
before assuming "bigger is always better" on any specific bundle choice.

## Cost to fully clear the track (Pearl, 158,888 points)

Vouchers needed: 158,888 × 1000/11 ≈ 14,444,364.

| Route | Effective rate | Cost |
|---|---|---|
| Direct IAP, best known tier ($9.99 × 2,337) | 6.807 pts/$ | $23,346.63 |
| SEAGM vouchers, best bulk bundles | ~7.69 pts/$ | ~$20,650 |

SEAGM's voucher route is the cheaper path, but only by ~13% over the best
direct-IAP tier — a much smaller gap than a naive per-voucher reading of
the 1.1× bonus would suggest (an earlier pass on this math mistakenly
treated it as ~1 voucher ≈ 1.1 points, which is wrong — see the ratio
above).

## Open questions

- No exhaustive bin-packing proof that $20,650 is the true minimum-cost
  SEAGM bundle combination — that number uses the flat top-tier rate as an
  approximation; real minimum could be a few dollars lower by mixing
  bundle sizes for the remainder.
- Cosmetic rewards on the same track: values and count not captured (owner:
  out of scope for now).
