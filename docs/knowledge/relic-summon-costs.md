# Relic summon system — cumulative point track

Distinct from Equipment Relics (`equipment-relics.md`) and the Zodiac Relic
(`zodiac-relic.md`). This is the monetization/point-track system that
**acquires** the 8 Creation Artifacts — not their own stat/Energy
mechanics, which live in `docs.py`'s Reference → Artifacts & Gems section
(desktop) / `reference_tab.dart` (mobile).

Owner-confirmed (2026-07-29): all 8 relics below (Vase, Pot, Mirror,
Token, Sheers, Cauldron, Basin, Pearl) are Creation Artifacts. Only 3 —
Starsea Vase, Dual-Star Mirror, Timereversal Pearl — have an existing
Energy-mechanic write-up in Reference; the other 5 (Pot, Token, Sheers,
Cauldron, Basin) are real Creation Artifacts too, just undocumented there
so far because their point cost is high enough that most players never
reach them. **Integration note**: this doc's content belongs as a new
subsection *inside* the existing Artifacts & Gems section (how you obtain
them), not a new standalone Reference topic — see the note near the
price-point ranking table below. Documenting the other 5 artifacts' own
Energy mechanics is a separate, still-open task.

## Core mechanic: breakpoints, not a per-pull gacha

Points accumulate on a single running total and are **never spent or
consumed** (owner-confirmed exact behavior: bank 10,000 points in week
one, and you get Vase the moment you cross 5,000 *and* Pot is
automatically claimable the instant it enters the pool next week — no
redraw needed, the surplus carried over). Crossing each breakpoint grants
that relic and progress continues toward the next one — this is a
milestone/battle-pass shape, not a gacha where each pull costs points.

Cosmetic rewards also sit on the same point track at other values —
intentionally out of scope here (owner: don't care about those for now).

### The weekly pool gate — a hard ceiling independent of money

Only **one relic is "in the pool" at a time**, always the next one in the
sequence above. Each pool slot lasts exactly 1 week (server week, rolling
over Monday); if nobody wins it that week, the same relic just stays in
the pool for another week rather than being replaced. Two ways to win the
current slot's relic:

1. **Points** — cross its cumulative threshold (guaranteed).
2. **Lottery** — every draw (see Diagram economy below) also carries an
   independent **0.25% instant-win chance** on the current pool relic,
   regardless of accumulated points.

Critically: **the pool does not advance early**. Even if you have more
than enough points banked to clear several thresholds at once, or you win
the current relic via lottery in the first hour of its week, the next
relic doesn't enter the pool until the next scheduled rollover. Extra
draws made after that week's relic is already won are guaranteed to not
win anything (can't win a second copy of what you have, can't win a relic
that isn't in the pool yet) — this is the "functionally a waste" warning
the game itself shows.

**This means money has a hard ceiling on how fast it can get you through
the whole track: 1 relic per week, minimum 8 weeks for all 8, no matter
how much is spent.** Past the point where you can already guarantee the
current week's relic, additional spending that week buys nothing — it
only matters for *which* weeks you can afford to guarantee versus rely on
luck/banked draws for (see the banking strategy below).

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

- **Creation draw**: spends 1 Creation Diagram, grants 10 points plus an
  independent 0.25% instant-win roll on the current pool relic (see
  Diagram economy below for where diagrams come from and the banking
  strategy this enables).
- **Direct purchase (App Store IAP)**: fixed point yield per real-money
  tier, confirmed by owner:

  | Tier | Points | Rate (pts/$) |
  |---|---|---|
  | $0.99 | 6 | 6.061 |
  | $2.99 | 18 | 6.021 |
  | $4.99 | 30 | 6.012 (worst known tier) |
  | $9.99 | 68 | **6.807** (best known tier) |
  | $14.99 | 98 | 6.538 |
  | $19.99 | 128 | 6.403 |
  | $29.99 | 198 | 6.602 |
  | $49.99 | 328 | 6.561 |
  | $99.99 | 648 | 6.481 |

  $99.99 is the largest single IAP SKU seen (owner-confirmed) — there is no
  bigger single tier; event offers instead cap at up to 10× $99.99 packs
  rather than one larger bundle. The curve is **not monotonic**: $9.99 beats
  every other tier, and the three smallest tiers ($0.99/$2.99/$4.99) are
  the worst value of the set — $4.99 is the single worst. $19.99 is a local
  dip (worse than both its immediate neighbors $14.99 and $29.99) but isn't
  the global worst. Owner believes this is the complete common-tier ladder
  (9 tiers: $0.99–$99.99).

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
| $19.99 | 128 | 6.403 | 12,800 | 140.8 |
| $0.99 | 6 | 6.061 | 600 | 6.6 |
| $2.99 | 18 | 6.020 | 1,800 | 19.8 |
| $4.99 | 30 | 6.012 ← worst | 3,000 | 33.0 |

To optimize point gain: always buy $9.99 packs, never $4.99 (the actual
worst tier — the three smallest packs are all bad value, not $19.99 as it
might look from its position next to two strong neighbors). To optimize
voucher usage: it doesn't matter which tier you redeem through — spend
down whatever vouchers you're sitting on at any tier, the yield per
voucher is identical everywhere.

**UI note for whenever this ships**: this data has no ownership state and
feeds no calculation, so it does NOT belong in the Vault (Library/Treasury/
Companions all track owned items that feed engine.py/engine.dart math —
this doesn't). It's static informational content — specifically it
belongs *inside* Reference's existing **Artifacts & Gems** section
(`docs.py` desktop / `reference_tab.dart` mobile), as an "acquiring the
Creation Artifacts" subsection alongside the current Starsea Vase/
Dual-Star Mirror/Timereversal Pearl write-up (see the note at the top of
this doc) — not a new standalone Reference topic and not the Guide tab
(Guide is narrative/subjective strategy prose; this is hard numbers).

If it ships there: the Rate column is the sort key the whole table is
ordered by — give it a distinct color/weight so that's obvious at a
glance, rather than reading as just another data column. This is a
sort-order affordance, not a data-status marker, so it doesn't conflict
with the no-provenance-badges rule in the root CLAUDE.md.

## Diagram economy

Creation Diagrams are the item a Creation draw consumes. Owner-confirmed
sources, all subscription passes (no known way to buy diagrams directly
with cash or vouchers):

| Pass | Diagrams | Duration | Price | Other benefit |
|---|---|---|---|---|
| Monthly | 1/day | 30 days | $4.99 | AFK cap +12h |
| Season | 1/day | 90 days | $12.99 | AFK cap +24h |
| Permanent | 2/week (Mon 8am) | forever | unrecorded | — |

Owner-confirmed community wisdom: **pass cost is out of scope for relic
optimization entirely**. If a player spends money on anything, these 3
passes come first, above and beyond relic strategy, because their other
benefits (chiefly the AFK gathering cap) are treated as required to play
the game at full efficiency — without any pass, anything gathered past
12h AFK is simply lost. Passes are assumed as sunk/baseline spend, and
their diagram output is treated as free income for relic purposes.

Combined baseline income, assuming all 3 passes active (monthly and
season stack, both granting 1/day independently): **1 + 1 = 2/day, plus
2/week from Permanent → 16 diagrams/week**, i.e. 160 points/week
guaranteed if every diagram were drawn immediately (see banking strategy
below for why that's usually not the best use of them).

### The banking strategy

Since the 0.25% lottery roll is identical on every draw regardless of
accumulated points, and diagrams don't expire or need to be spent
immediately, the strategic move is: **don't draw every week**. While a
relic is still cheap enough to pity out with cash, pay cash and leave
diagrams unspent. Once the point cost gets too expensive to justify
(the later relics — Cauldron/Basin/Pearl), dump the entire banked stockpile
at once for a concentrated batch of independent 0.25% shots, which can hit
well before the cash-pity threshold is reached — and even if it doesn't
hit, every draw still adds its 10 points toward the cumulative total, so a
failed lottery dump is never wasted value, just a missed shortcut.

Odds of winning via lottery alone from N banked draws (1 − 0.9975^N):

| Banked draws | Win chance | Weeks to bank (@16/week, all 3 passes) |
|---|---|---|
| 100 | 22.1% | 6.3 |
| 277 | 50.0% | 17.3 |
| 500 | 71.4% | 31.3 |
| 920 | 90.0% | 57.5 |
| 1,197 | 95.0% | 74.8 |
| 1,840 | 99.0% | 115.0 |

This is a genuinely long-horizon game (owner's own account is ~2 years
from Rank 6R+), so banking diagrams across dozens or low hundreds of
weeks while cash-pitying the early relics, then unloading the stockpile
against Pearl, is a realistic strategy — not a theoretical one.

### Most efficient dump target: Basin, not Pearl

The lottery odds for a given stockpile size are identical no matter which
relic is currently in the pool — the "cost" side of a dump never changes
by target. What *does* change is the payoff if it hits: the **marginal**
point gap for that specific relic (its own threshold minus the previous
relic's, since everything below is already banked). Since dump cost is
constant, the best target is whichever relic has the largest marginal gap
— that's where a win saves the most cash for the same stockpile.

| Relic | Cumulative points | Marginal points | Cash saved if won (SEAGM rate) | Cash saved if won (best IAP) |
|---|---|---|---|---|
| Vase | 5,000 | 5,000 | $649.80 | $734.56 |
| Pot | 10,000 | 5,000 | $649.80 | $734.56 |
| Mirror | 20,000 | 10,000 | $1,299.61 | $1,469.12 |
| Token | 40,000 | 20,000 | $2,599.22 | $2,938.24 |
| Sheers | 70,000 | 30,000 | $3,898.82 | $4,407.35 |
| Cauldron | 88,888 | 18,888 | $2,454.70 | $2,774.87 |
| **Basin** | 128,888 | **40,000** | **$5,198.43** | **$5,876.47** |
| Pearl | 158,888 | 30,000 | $3,898.82 | $4,407.35 |

**Basin has the single biggest marginal jump of the whole track (40,000
points) — bigger even than Pearl's (30,000)**, despite Pearl being the
final and most expensive relic overall. That's not obvious from the
cumulative totals alone: Basin costs less than Pearl in total, but the
*specific step* from Cauldron to Basin is the priciest single jump to
clear. A banked stockpile is best spent trying to snipe Basin, not saved
all the way for Pearl — and if the dump on Basin misses, the same
diagrams' points still count toward Pearl's total anyway, so there's no
downside to trying at Basin first.

### Strategies for lower spenders

The whale-tier tables above ($20k+ to guarantee everything) aren't the
realistic plan for most players. Two strategies work well without
committing to that:

**1. Spend to a ceiling, then bank-and-ride past it.** Pick the relic
where cash stops feeling worth it (owner: everything through Mirror is
reasonable, Token is next), pay cash up to that ceiling at the best rate
($9.99 tier or SEAGM vouchers), then stop spending entirely. Past the
ceiling, don't draw diagrams weekly — bank them. Passive income alone
(16/week from the 3 passes, already-sunk cost) keeps the cumulative total
climbing for free, and periodic stockpile dumps at whatever relic is
currently in the pool give real shots at winning it outright with no
cash. A miss never costs anything extra — the points still bank toward
the next relic regardless.

**2. Snipe the biggest marginal jump inside your own near-term goal, not
the global one.** Basin is the best target for a whale aiming at
everything, but a lower spender should compare marginal jumps only among
the relics they actually care about next. For someone stopping around
Token, the relevant jumps are Vase/Pot (5,000 each), Mirror (10,000), and
Token (20,000) — **Token is the biggest of that set**, meaning it's the
single relic in that range where a lottery win saves the most cash
relative to just paying for it ($2,599–$2,938 depending on route).
Concretely: banking ~150–300 diagrams (9–19 weeks of passive income
alone) gives a 31–53% chance of winning Token via lottery before ever
paying full price for its marginal 20,000 points:

| Banked draws | Win chance | Weeks to bank (@16/week) |
|---|---|---|
| 50 | 11.8% | 3.1 |
| 100 | 22.1% | 6.2 |
| 150 | 31.3% | 9.4 |
| 200 | 39.4% | 12.5 |
| 277 | 50.0% | 17.3 |
| 300 | 52.8% | 18.8 |

Combining both: pay cash through Mirror (cheap enough that cash is the
faster path anyway), then bank diagrams for several months and dump the
stockpile at Token before defaulting to a straight cash top-up for
whatever points the dump didn't cover.

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
it too. These tables answer "what does it cost to *guarantee* every relic
with cash" — they don't account for the weekly pool gate (8-week minimum
regardless of spend) or the banking strategy above, both of which can
substantially reduce real spend for a patient player.

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
- Permanent pass price not recorded (owner: doesn't matter for this doc
  since pass cost is out of scope regardless — captured for completeness
  only if it ever becomes relevant elsewhere).
- No confirmation of whether Creation Diagrams are obtainable any other
  way (direct cash/voucher purchase, event rewards, etc.) beyond the 3
  passes — assumed to be pass-only until shown otherwise.
- The banking-strategy odds table treats each draw as fully independent
  at a flat 0.25%; not confirmed whether the rate is literally fixed
  every week for every remaining relic or could vary by relic.
