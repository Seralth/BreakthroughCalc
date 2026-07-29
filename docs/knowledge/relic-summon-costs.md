# Relic summon system — cumulative point track

How the 8 Creation Artifacts get acquired — not their own stat/Energy
mechanics, which live in Reference → Artifacts & Gems (`docs.py` desktop /
`reference_tab.dart` mobile). Not yet wired into the calc.

Distinct from Equipment Relics (`equipment-relics.md`) and the Zodiac Relic
(`zodiac-relic.md`) — unrelated systems that just happen to share the word
"relic."

All 8 below — Vase, Pot, Mirror, Token, Sheers, Cauldron, Basin, Pearl —
are Creation Artifacts. Each has a full descriptor-plus-item name (Starsea
Vase, Dual-Star Mirror, Timereversal Pearl, same pattern for the rest),
but nobody calls them that — everyone just says Vase, Mirror, Pearl, and
so on, and that's what this doc uses too. Only three of them have their
Energy mechanic written up in Reference already; the other five are just
as real, they're simply too expensive for most players to reach, so
nobody's gotten around to documenting their mechanics yet.

**Integration note**: this belongs as a subsection inside the existing
Artifacts & Gems section — how you obtain them — not a new standalone
Reference topic (see the note near the price-point ranking table below).
Documenting the other five artifacts' own Energy mechanics is separate
work.

## Core mechanic: breakpoints, not a per-pull gacha

Points build up on one running total that never gets spent. Cross a
breakpoint and that relic's yours — progress just keeps climbing toward
the next one. Bank 10,000 points in week one and Vase is already yours
the moment 5,000 gets crossed, and Pot is claimable the instant it enters
the pool the following week — no redraw needed, the surplus just carries
straight over. It's a milestone/battle-pass shape, not a gacha where
every pull costs points.

Cosmetics sit on the same track too — between relics and continuing past
Pearl, with the whole thing eventually ending at a capstone cosmetic. Not
worth getting into here.

### The weekly pool gate — a hard ceiling independent of money

Only one relic is in the pool at a time, always the next one in the
sequence below. Each one sits for exactly a week, rolling over Monday —
miss it and it just stays another week instead of getting replaced. Two
ways to win it:

1. **Points** — cross the cumulative threshold. Guaranteed.
2. **Lottery** — every draw also carries an independent **0.25%**
   instant-win shot at whatever's currently in the pool, on top of
   whatever points are banked. Fixed rate, every relic, no exceptions —
   it comes from a permanent event that's never changed and isn't going
   to.

The pool never advances early. Doesn't matter if there's ten times the
needed points banked, or a relic gets won by lottery an hour into its
week — the next one doesn't show up until the scheduled rollover. Any
draws spent after that week's relic is already won can't win anything: no
second copy of what's already yours, and nothing to win on a relic that
isn't even in the pool yet. That's the "functionally a waste" warning the
game throws up.

Which means money hits a hard ceiling on how fast this whole thing goes:
one relic a week, eight weeks minimum for all of them, no matter how much
gets thrown at it. Past the point where a week's relic is already
guaranteed, spending more that week buys nothing — it only decides which
weeks get paid for outright versus left to luck and banked draws (see the
banking strategy below).

### Relic breakpoints (cumulative points)

This table is also the pool order — relics show up top to bottom, one at
a time, Vase first and Pearl last.

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

- **Creation draw**: spends 1 Creation Diagram, grants 10 points plus the
  0.25% lottery shot above (see Diagram economy below for where diagrams
  come from and the banking strategy this opens up).
- **Direct purchase (App Store)**: fixed point yield per real-money tier:

  | Tier | Points | Rate (pts/$) |
  |---|---|---|
  | $0.99 | 6 | 6.061 |
  | $2.99 | 18 | 6.021 |
  | $4.99 | 30 | 6.012 (worst tier) |
  | $9.99 | 68 | **6.807** (best tier) |
  | $14.99 | 98 | 6.538 |
  | $19.99 | 128 | 6.403 |
  | $29.99 | 198 | 6.602 |
  | $49.99 | 328 | 6.561 |
  | $99.99 | 648 | 6.481 |

  $99.99 is the biggest single pack there is — no bigger single tier
  exists; events instead offer up to 10× $99.99 packs rather than one
  larger bundle. The curve isn't clean: $9.99 beats every other tier, and
  the three cheapest packs ($0.99/$2.99/$4.99) are the worst value of the
  bunch — $4.99 worst of all. $19.99 looks bad sitting between two strong
  neighbors but isn't actually the floor. This is the full common-tier
  ladder, $0.99 to $99.99.

- **Voucher-funded purchase**: the same tiers above can be paid for with
  SEAGM top-up vouchers instead of cash, which applies a flat **1.1×**
  bonus to that tier's point yield:

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
  vouchers/point). Treat it as a fixed conversion constant.

### Price-point value ranking

The voucher ratio is fixed no matter the tier — no price point is a
better or worse deal for "voucher usage," they all convert at exactly
0.011 pts/voucher. The only thing that actually varies by tier is
cash-purchase efficiency. Ranked best to worst by cash rate:

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

To optimize point gain: always buy $9.99 packs, never $4.99 — the three
smallest packs are all bad value, not $19.99 as it might look from its
position next to two strong neighbors. To optimize voucher usage, it
doesn't matter which tier gets redeemed through — spend down whatever
vouchers are sitting around at any tier, the yield per voucher is
identical everywhere.

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

## SEAGM voucher pricing

SEAGM sells the same "Vouchers" currency directly for cash, at bundle
pricing that doesn't scale linearly — bigger bundles are usually but not
always a better rate, plateauing at ~699.5 vouchers/$ from the $199.99
tier up, no further bulk bonus above that.

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

The rate isn't strictly monotonic — 6,900 beats the pricier 10,000 tier,
20,500 beats the pricier 33,800 tier — worth checking the table before
assuming bigger is always better on any specific bundle.

## LT's own voucher value vs SEAGM's real price

Seven price points ($0.99, $9.99, $14.99, $19.99, $29.99, $49.99, $99.99)
show up on both LT's in-game voucher-equivalent pricing (what a reward is
worth in vouchers) and SEAGM's real storefront (what SEAGM actually sells
that many dollars of vouchers for). Lined up at matching prices:

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
valuation — never worse. "Extra points" is extra vouchers × 0.011 (the
fixed ratio above) — how many more points that same dollar amount nets by
routing through SEAGM instead of paying LT direct-voucher price. $99.99
has the widest gap, ~5% more vouchers, 35.2 bonus points.

### Time-limited pop-up bundles

The game also runs random time-limited pop-up offers, always 3 options —
cheap/mid/high. These aren't a separate pricing tier: a pop-up priced at
$14.99 grants the exact same points and vouchers as the fixed $14.99
catalog tier, no exceptions, same at every other price. The scarcity
framing is pure urgency with zero pricing difference underneath it — the
"cheap/mid/high" pop-up is worth the same exact math as the fixed $9.99
tier beating its neighbors, just match whichever price shows up against
the tables above instead of treating the pop-up as a unique deal.

## Cost per relic breakpoint (at-a-glance)

Since points are cumulative and never spent, each row's cost is the total
spend to go from zero all the way to that relic — not an incremental
per-relic price. Buying up to Pearl nets every relic above it too. These
tables answer "what does it cost to guarantee every relic with cash" —
they don't account for the weekly pool gate (8-week minimum regardless of
spend) or the diagram-banking strategy below, both of which can cut real
spend substantially for a patient player.

**Route A — Direct purchase**, repeating the best tier ($9.99 → 68 pts):

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

**Route B — SEAGM vouchers**. Points come from vouchers at the fixed
1,000-vouchers-per-11-points ratio. These are the exact optimal cost for
each threshold, solved across all 13 SEAGM bundle sizes rather than
approximated off the flat top-tier rate:

| Relic | Vouchers needed | Cost |
|---|---|---|
| Vase | 454,546 | $650.93 |
| Pot | 909,091 | $1,301.86 |
| Mirror | 1,818,182 | $2,599.97 |
| Token | 3,636,364 | $5,199.92 |
| Sheers | 6,363,637 | $9,099.71 |
| Cauldron | 8,080,728 | $11,554.61 |
| Basin | 11,717,091 | $16,752.75 |
| Pearl | 14,444,364 | $20,650.61 |

Route B is consistently the cheaper option, by ~11.6–12.1% at every
breakpoint — a much smaller gap than a naive per-voucher reading of the
1.1× bonus would suggest (that reading — treating it as ~1 voucher ≈ 1.1
points — is wrong; see the ratio above for the actual conversion). Both
routes' figures are exact.

## Diagram economy

Creation Diagrams are what a Creation draw consumes. Reliable sources are
the 3 subscription passes below. Time-limited events occasionally throw
in extra diagrams too, but those are infrequent and irregular enough to
plan around the passes only and treat event diagrams as pure bonus on
top:

| Pass | Diagrams | Duration | Price | Other benefit |
|---|---|---|---|---|
| Monthly | 1/day | 30 days | $4.99 | AFK cap +12h |
| Season | 1/day | 90 days | $12.99 | AFK cap +24h |
| Permanent | 2/week (Mon 8am) | forever | — | — |

Pass cost is out of scope for relic optimization entirely. If money's
going anywhere, these 3 passes come first, above and beyond relic
strategy — the AFK gathering cap alone makes them required to play at
full efficiency, since anything gathered past 12h AFK with no pass active
is simply lost. Passes are sunk/baseline spend; their diagram output is
free income for relic purposes.

Combined baseline income with all 3 passes active (monthly and season
stack, each granting 1/day independently): 1 + 1 = 2/day, plus 2/week from
Permanent → **16 diagrams/week**, i.e. 160 points/week guaranteed if
every diagram gets drawn immediately (see the banking strategy below for
why that's usually not the best use of them).

**Weekly draw cap: 999 attempts.** That's a cap on how many draws can get
*spent* in a given week, not on how many diagrams can be *held* — banking
a stockpile well past 999 is fine, a big dump just has to spread across
multiple weeks (1,840 banked draws takes 999 + 841, i.e. 2 weeks to fully
deploy). Since the target relic stays in the pool until someone wins it,
splitting a dump across weeks doesn't change the odds math below at all —
the same total draws still add up to the same win chance, just not all in
one week.

### The banking strategy

Since the 0.25% lottery roll is identical on every draw regardless of
banked points, and diagrams don't expire or need spending immediately,
the move is: don't draw every week. While a relic's still cheap enough to
pity out with cash, pay cash and leave diagrams unspent. Once the point
cost gets too steep to justify — the later relics, Cauldron/Basin/Pearl —
dump the whole banked stockpile at once for a concentrated batch of
independent 0.25% shots, which can hit well before the cash-pity
threshold is reached. Even a miss isn't wasted — every draw still adds
its 10 points to the cumulative total, so a failed dump is never wasted
value, just a missed shortcut.

Odds of winning via lottery alone from N banked draws (1 − 0.9975^N).
Rows past 999 need 2 weeks to actually spend, per the draw cap above:

| Banked draws | Win chance | Weeks to bank (@16/week, all 3 passes) | Weeks to deploy (999/week cap) |
|---|---|---|---|
| 100 | 22.1% | 6.3 | 1 |
| 277 | 50.0% | 17.3 | 1 |
| 500 | 71.4% | 31.3 | 1 |
| 920 | 90.0% | 57.5 | 1 |
| 1,197 | 95.0% | 74.8 | 2 |
| 1,840 | 99.0% | 115.0 | 2 |

This is a long-horizon game — banking diagrams across dozens or low
hundreds of weeks while cash-pitying the early relics, then unloading the
stockpile against Pearl, is a realistic strategy, not a theoretical one.

### Most efficient dump target: Basin, not Pearl

The lottery odds for a given stockpile are identical no matter which
relic's currently in the pool — the cost side of a dump never changes by
target. What changes is the payoff if it hits: the marginal point gap for
that specific relic, its own threshold minus the previous relic's, since
everything below is already banked. Dump cost being constant, the best
target is whichever relic has the largest marginal gap — that's where a
win saves the most cash for the same stockpile. Marginal costs below are
exact diffs of the Route A/B tables above, so they're consistent with the
cumulative figures:

| Relic | Cumulative points | Marginal points | Cash saved if won (SEAGM) | Cash saved if won (best IAP) |
|---|---|---|---|---|
| Vase | 5,000 | 5,000 | $650.93 | $739.26 |
| Pot | 10,000 | 5,000 | $650.93 | $739.26 |
| Mirror | 20,000 | 10,000 | $1,298.11 | $1,468.53 |
| Token | 40,000 | 20,000 | $2,599.95 | $2,937.06 |
| Sheers | 70,000 | 30,000 | $3,899.79 | $4,405.59 |
| Cauldron | 88,888 | 18,888 | $2,454.90 | $2,777.22 |
| **Basin** | 128,888 | **40,000** | **$5,198.14** | **$5,874.12** |
| Pearl | 158,888 | 30,000 | $3,897.86 | $4,405.59 |

Basin has the single biggest marginal jump of the whole track — 40,000
points, bigger even than Pearl's 30,000 — despite Pearl being the final
and most expensive relic overall. Not obvious from the cumulative totals
alone: Basin costs less than Pearl in total, but the specific step from
Cauldron to Basin is the priciest single jump to clear. A banked
stockpile is best spent trying to snipe Basin, not saved all the way for
Pearl — and if the dump on Basin misses, the same diagrams' points still
count toward Pearl's total anyway, so there's no downside to trying at
Basin first.

### Strategies for lower spenders

The whale-tier tables above ($20k+ to guarantee everything) aren't the
realistic plan for most players. Everyone's ceiling is different —
figure out where cash stops feeling worth it for your own means, then
apply these two strategies from that line rather than any specific relic
named as an example below:

**1. Spend to a ceiling, then bank-and-ride past it.** Pay cash up to
whatever relic still feels reasonable at the best rate ($9.99 tier or
SEAGM vouchers), then stop spending entirely. Past that ceiling, don't
draw diagrams weekly — bank them. Passive income alone (16/week from the
3 passes, already-sunk cost) keeps the cumulative total climbing for
free, and periodic stockpile dumps at whatever relic's currently in the
pool give real shots at winning it outright with no cash. A miss never
costs anything extra — the points still bank toward the next relic
regardless. This scales down to a $0 ceiling just as well: bank from day
one, never buy a single point, and let passive income plus lottery odds
do all the work — slower, but the 8-week floor applies either way, so
patience alone eventually gets there. It also scales up: someone with
more room to spend just pushes the ceiling further down the list before
switching to banking.

For a worked example: everything through Mirror is a comfortable cash
spend for one player, Token the next stretch past it — someone else's
line will fall somewhere else entirely, and that's fine, the method's the
same regardless of where it lands.

**2. Snipe the biggest marginal jump inside your own near-term goal, not
the global one.** Basin's the best target for a whale going all the way,
but anyone stopping earlier should compare marginal jumps only among the
relics they actually care about next — list the jump size for each relic
up to your own stopping point and target whichever's biggest, the same
logic as Basin just applied to a smaller range.

Worked example, for someone stopping around Token: the relevant jumps are
Vase/Pot (5,000 each), Mirror (10,000), and Token (20,000) — Token's the
biggest of that set, meaning it's the single relic in that range where a
lottery win saves the most cash relative to just paying for it ($2,600
via SEAGM / $2,937 via best IAP). Banking ~150–300 diagrams (9–19 weeks
of passive income alone) gives a 31–53% chance of winning it via lottery
before ever paying full price for its marginal 20,000 points:

| Banked draws | Win chance | Weeks to bank (@16/week) |
|---|---|---|
| 50 | 11.8% | 3.1 |
| 100 | 22.1% | 6.2 |
| 150 | 31.3% | 9.4 |
| 200 | 39.4% | 12.5 |
| 277 | 50.0% | 17.3 |
| 300 | 52.8% | 18.8 |

Combining both, for that same example: pay cash through Mirror since cash
is the faster path there anyway, then bank diagrams for several months
and dump the stockpile at Token before defaulting to a straight cash
top-up for whatever points the dump didn't cover. Redo the same
comparison at your own stopping point instead — the method carries over
exactly, only the specific numbers change.

## Practical read

Points are one cumulative total that's never spent — reaching a
breakpoint just unlocks that relic and progress keeps climbing toward the
next. The pool only ever advances one relic per week regardless of
spending, so 8 weeks is the hard floor no matter how much cash goes in.
$9.99 is always the best cash rate, direct or via SEAGM voucher; $4.99 is
always the worst. SEAGM vouchers beat paying LT direct at every shared
price point, but only by ~12%, not the huge margin a naive reading of the
voucher bonus would suggest. Guaranteeing every relic with cash tops out
around $20,650 (SEAGM) to $23,347 (direct) — a whale number, not a
realistic plan for most players. For everyone else: pay cash up to
whichever relic still feels reasonable for your own means — that line
could sit anywhere from zero to Sheers or beyond depending on the
player — then stop and bank Creation Diagrams instead of drawing them
weekly. Even a $0 ceiling works, just slower: the 8-week floor applies
either way, so patience plus passive income from the 3 passes (already
sunk cost for the AFK-cap benefits alone) gets there on its own, keeping
real lottery shots banked for free. The best place to spend a stockpile
is whichever relic has the biggest single step from the one before it —
Basin for a whale going all the way, or
whatever's biggest within a smaller stopping point otherwise.
