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
  | $2.99 | 18 | 6.021 |
  | $4.99 | 30 | 6.012 |
  | $9.99 | 68 | **6.807** (best known tier) |
  | $14.99 | 98 | 6.538 |
  | $19.99 | 128 | 6.403 (worst known tier) |
  | $29.99 | 198 | 6.602 |
  | $49.99 | 328 | 6.561 |
  | $99.99 | 648 | 6.481 |

  $99.99 is the largest single IAP SKU seen (owner-confirmed) — there is no
  bigger single tier; event offers instead cap at up to 10× $99.99 packs
  rather than one larger bundle. The curve is **not monotonic**: $9.99 beats
  every other tier, and $19.99 — despite sitting right next to it — is
  actually the single worst-value tier of the set. Owner believes this is
  the complete common-tier ladder (9 tiers: $0.99–$99.99).

- **Voucher-funded purchase**: the same IAP tiers above can alternatively be
  paid for with SEAGM top-up vouchers instead of cash, and doing so applies
  a flat **1.1× bonus** to that tier's point yield. Voucher cost per tier
  (owner-provided):

  | Tier | Vouchers | Points (base × 1.1) |
  |---|---|---|
  | $0.99 | 600 | 6.6 |
  | $2.99 | 1,800 | 19.8 |
  | $4.99 | 3,000 | 33 |
  | $9.99 | 6,800 | 74.8 |
  | $14.99 | 9,800 | 107.8 |
  | $19.99 | 12,800 | 140.8 |
  | $29.99 | 19,800 | 217.8 |
  | $49.99 | 32,800 | 360.8 |
  | $99.99 | 64,800 | 712.8 |

  Every one of these nine tiers reduces to the exact same ratio:
  **1,000 vouchers = 11 points** (1 voucher = 0.011 points, ≈90.909
  vouchers/point). Confirmed exact across all nine data points — treat as
  a fixed conversion constant, not an approximation.

### Price-point value ranking

The voucher ratio above is fixed regardless of tier — no price point is a
better or worse deal for "voucher usage," they all convert at the exact
same 0.011 pts/voucher. The only thing that actually varies by tier is
**cash-purchase efficiency**. Ranked best to worst by cash rate:

| Price | Points (cash) | Rate (pts/$) | Vouchers (if paid via voucher) | Points via voucher (×1.1) |
|---|---|---|---|---|
| $9.99 | 68 | **6.807** ← best | 6,800 | 74.8 |
| $29.99 | 198 | 6.602 | 19,800 | 217.8 |
| $49.99 | 328 | 6.561 | 32,800 | 360.8 |
| $14.99 | 98 | 6.538 | 9,800 | 107.8 |
| $99.99 | 648 | 6.481 | 64,800 | 712.8 |
| $19.99 | 128 | 6.403 ← worst | 12,800 | 140.8 |
| $0.99 | 6 | 6.061 | 600 | 6.6 |
| $2.99 | 18 | 6.020 | 1,800 | 19.8 |
| $4.99 | 30 | 6.012 | 3,000 | 33.0 |

To optimize point gain: always buy $9.99 packs, never $19.99 (its
immediate neighbor is worse value on both sides). To optimize voucher
usage: it doesn't matter which tier you redeem through — spend down
whatever vouchers you're sitting on at any tier, the yield per voucher is
identical everywhere.

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

## LT's own voucher value vs SEAGM's real price

Seven price points ($0.99, $9.99, $14.99, $19.99, $29.99, $49.99, $99.99)
appear on **both** LT's in-game voucher-equivalent pricing (what LT itself
says a reward is worth in vouchers) and SEAGM's real storefront (what
SEAGM actually sells that many dollars of vouchers for). Comparing the two
at matching prices shows whether SEAGM is a genuine discount or just
noise:

| Price | LT vouchers | LT rate | SEAGM vouchers | SEAGM rate | Extra vouchers | Extra points |
|---|---|---|---|---|---|---|
| $0.99 | 600 | 606.06/$ | 600 | 606.06/$ | 0 | 0.0 |
| $9.99 | 6,800 | 680.68/$ | 6,900 | 690.69/$ | 100 | 1.1 |
| $14.99 | 9,800 | 653.77/$ | 10,000 | 667.11/$ | 200 | 2.2 |
| $19.99 | 12,800 | 640.32/$ | 13,500 | 675.34/$ | 700 | 7.7 |
| $29.99 | 19,800 | 660.22/$ | 20,500 | 683.56/$ | 700 | 7.7 |
| $49.99 | 32,800 | 656.13/$ | 33,800 | 676.14/$ | 1,000 | 11.0 |
| $99.99 | 64,800 | 648.06/$ | 68,000 | 680.07/$ | 3,200 | 35.2 |

At every shared price point SEAGM matches or beats LT's own voucher
valuation — never worse. "Extra points" = extra vouchers × 0.011 (the
fixed ratio above), i.e. how many more points that same dollar amount
nets you by routing through SEAGM instead of paying LT direct-voucher
price. The $99.99 tier has the widest gap (~5% more vouchers, 35.2 bonus
points) — consistent with the per-relic savings in the next section.

### Time-limited pop-up bundles

The game also runs random time-limited pop-up offers, always presented as
3 options (cheap/mid/high). Owner-confirmed: these are **not** a separate
pricing tier — a pop-up priced at $14.99 always grants the exact same
points and vouchers as the fixed $14.99 catalog tier above, no exceptions,
same for every other price. The scarcity/urgency framing is pure dark
pattern with zero pricing difference underneath it. Practical takeaway:
the "cheap/mid/high" pop-up is exploitable the same way the fixed $9.99
tier beats its neighbors — just match whichever price appears against the
tables above rather than treating the pop-up as a unique deal.

## Cost per relic breakpoint (at-a-glance)

Since points are cumulative and never spent, each row's cost is the total
spend to go from zero all the way to that relic — not an incremental
per-relic price. Buying up to Pearl automatically nets every relic above
it too.

**Route A — Direct IAP**, repeating the best known tier ($9.99 → 68 pts):

| Relic | Points needed | Cost |
|---|---|---|
| Vase | 5,000 | $739.26 |
| Pot | 10,000 | $1,478.52 |
| Mirror | 20,000 | $2,947.05 |
| Token | 40,000 | $5,884.11 |
| Sheers | 70,000 | $10,289.70 |
| Cauldron | 88,888 | $13,066.92 |
| Basin | 128,888 | $18,941.04 |
| Pearl | 158,888 | $23,346.63 |

**Route B — SEAGM vouchers**, using the best bulk rate (~699.51
vouchers/$, from the $599.99+ tiers). Points come from vouchers at the
fixed 1,000-vouchers-per-11-points ratio:

| Relic | Vouchers needed | Cost |
|---|---|---|
| Vase | 454,546 | ~$649.80 |
| Pot | 909,091 | ~$1,299.61 |
| Mirror | 1,818,182 | ~$2,599.22 |
| Token | 3,636,364 | ~$5,198.43 |
| Sheers | 6,363,637 | ~$9,097.26 |
| Cauldron | 8,080,728 | ~$11,551.96 |
| Basin | 11,717,091 | ~$16,750.39 |
| Pearl | 14,444,364 | ~$20,649.21 |

Route B is consistently the cheaper option, by ~11.6–12.1% at every
breakpoint — a much smaller gap than a naive per-voucher reading of the
1.1× bonus would suggest (an earlier pass on this math mistakenly treated
it as ~1 voucher ≈ 1.1 points, which is wrong — see the ratio above).
Route B's figures are a continuous approximation (real purchases are
bundle-quantized — true cost could run a little higher for small
thresholds, a little lower with careful bundle-mixing); treat as accurate
to within ~1%.

## Open questions

- No exhaustive bin-packing proof that $20,650 is the true minimum-cost
  SEAGM bundle combination — that number uses the flat top-tier rate as an
  approximation; real minimum could be a few dollars lower by mixing
  bundle sizes for the remainder.
- Cosmetic rewards on the same track: values and count not captured (owner:
  out of scope for now).
