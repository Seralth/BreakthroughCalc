# Elemental Laws & Law Fruit garden mechanics (Spiritual World / Voidbreak)

Integrated into Reference → World Systems (Garden & Elemental Laws) and
Guide → Timegate (garden-unlock prep bullet) — not yet in the calc's actual
math (no engine.py/engine.dart modeling, no input fields). Spiritual World
content gated behind Voidbreak; Elemental
Laws (five elements: Metal/Wood/Water/Fire/Earth) level up on Law Points,
which come from consuming ("Blitzing") garden-grown Law Fruit. Elemental
Laws feed passive stat boosts (still unquantified — not needed for garden
prep, low priority) and **Law Suppression**, which now has a quantified
formula — see its own section below. Law Points also feed a separate
**Cosmic Laws** system — G1
confirms directly that both draw from **one shared Law Point pool**, not
separate ones ("Law points are used to upgrade the level of the elements in
Elemental Laws and Cosmic Laws"), and recommends prioritizing Elemental Laws
first specifically because leveling them raises the shared pool's income
rate. Cosmic Laws additionally cost **Nature Mantra** (Seeker Shop, bought
with Revealstone) on top of Law Points — the existing "buy nothing at the
Seeker Shop before Voidbreak, you'll want 3,300+ Nature Mantras" guidance
in Reference → World Systems is this same requirement.

## Sources

- **G1** — grindnstrat.com "Overmortal Spiritual World Guide," Law Fruits
  section (grindnstrat.com/overmortal-spiritual-world-guide/#Law_Fruits).
  Community guide; prose claims are community-tier, not screenshot-verified,
  except where noted below.
- **G2/G3** — Chinese-language community guides. OverMortal is the global
  release of **一念逍遥** (Yi Nian Xiao Yao), same publisher (LTGAMES
  GLOBAL) — the Chinese-language community around the original release has
  substantially more detailed guides/wikis than the English-language scene,
  worth checking first (not just as a fallback) for any mechanic English
  guides describe vaguely. Sources for Law Suppression below: a Zhihu guide
  (zhuanlan.zhihu.com/p/579762919, "一念逍遥法则系统") and a TapTap CN forum
  post (taptap.cn/moment/364413714448778861), cross-checked against each
  other and a third aggregated search — three independent community
  sources agreeing exactly on the same numbers. Community-tier (not a
  screenshot), but strongly triangulated.
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

In-game item flavor text (screenshot, 2026-08-11): *"A special fruit
found only in areas filled with energy. Legend says eating it will
greatly benefit the study of Laws."* Category "Law Item." Growth-time
table on the item's own tooltip matches the table above exactly,
confirming it directly rather than only via the separate Blitz popup.

## Garden's other two crop types — Ploughwood & Soulrend Vine (2026-08-11 screenshot pass + owner direct knowledge)

The garden's 36 cells aren't Law-Fruit-exclusive by mechanic (see
Garden grid above) — two other crop lines share the same grid and the
same 3-cell L-tromino footprint:

- **Ploughwood** (owner, 2026-08-20): forging material for **Zodiac
  Relic** upgrades (see `zodiac-relic.md`). No item tooltip captured
  yet — flavor text, growth-time tiers, and exact upgrade mechanics
  are still open; only its purpose is confirmed so far.
- **Soulrend Vine** (screenshot-confirmed, 2026-08-11 and 2026-08-20
  passes): forging material for **equipment crafting**, specifically
  Voidbreak-stage gear (and relics — the 2026-08-20 tooltip says "Gear
  or Relics of the Voidbreak Stage," the 2026-08-11 one only said
  "Gear"; treat "or Relics" as the more complete/later reading). Owner
  confirms the plant's on-screen appearance stays visually identical
  across tiers — only the item name changes with growth time, same
  pattern as Law Fruit's Green/Blue/Purple/Yellow. Five tiers (one more
  than Law Fruit's four); each tier has its **own** quality-boost
  percentage (scaling up with tier, not a flat rate) — the two
  screenshot passes together confirm the bottom and middle rungs:

  | Tier | Growth time | Quality boost (Rare / Epic / Legendary) |
  |---|---|---|
  | Aged Soulrend Vine | 4 hours | +5% / +2% / +0.1% |
  | Centa Soulrend Vine | 12 hours | not captured |
  | Milia Soulrend Vine | 1 day 12 hours (36h) | +15% / +10% / +1% |
  | Myrua Soulrend Vine | 6 days 12 hours (156h) | not captured |
  | Decamyriad Soulrend Vine | 11 days 12 hours (276h) — tooltip says
  **"Requires Azryn Pot to energize"** instead of a plain grow time | not captured |

  The "Azryn Pot" name is new — very likely the actual in-game name of
  the "Garden Pot artifact" documented elsewhere in this file under its
  generic description (owner, 2026-07-29); needs a follow-up screenshot
  of the Pot item itself to confirm the two are the same artifact before
  renaming that section, but the naming match is strong.

- **Ploughwood** tooltip, now captured (screenshot, 2026-08-20):
  *"Plant it in the Garden to harvest Ploughwood, which can break
  through the Zodiac Relic's rank."* Confirms the owner's purpose
  description above directly. Growth-time ladder currently shows only
  a single tier ("Ploughwood," purple-colored, 1 day 0 hours / 24h) —
  unclear whether Ploughwood has other tiers not yet unlocked/visible,
  or is single-tier by design unlike Law Fruit and Soulrend Vine; open
  question.

Current stock, 2026-08-11 screenshot: Law Fruit Seed x8, Ploughwood Seed
x14, Soulrend Vine Seed x15 — all three drawn from the same seed-item UI
pattern, reinforcing they're parallel crop lines on one shared system,
not Law Fruit with two unrelated bolt-ons.

## Owner's live garden allocation — baseline suggestion (2026-08-20)

Owner's current planting across the (not yet fully unlocked) grid: **6
Law Fruit, 3 Soulrend Vine, 2 Ploughwood** concurrently growing. Owner's
own assessment (qualitative, not yet cross-checked against the seed-
supply/throughput math above):

- 6 Law Fruit is enough to max out the daily Blitz cap, consistent with
  the seed-scarcity conclusion above (only a handful of concurrent
  Purple slots are needed once seed supply — not cell-time — is the
  bottleneck).
- 3 Soulrend Vine keeps a steady enough supply for ongoing Voidbreak-
  gear crafting attempts.
- 2 Ploughwood is **not** enough on its own for Zodiac Relic upgrades,
  but stretches out fine when combined with the Zodiac Relic's own
  event rewards (recurring every 3 weeks) as the other income source —
  garden Ploughwood tops up between events rather than being the sole
  supply.
- **For players not investing in the Zodiac Relic**: swapping the 2
  Ploughwood slots for more Law Fruit instead is a viable alternative
  allocation — Ploughwood has no other use.

This is a reasonable starting-point allocation for anyone following
this doc, not a mathematically optimized one — flagged as owner's
qualitative read of his own live account, matching the "6/3/2 out of a
partially-unlocked grid" scale rather than the fully-unlocked 12-slot
scenario used in the Pot-energy ceiling math above.

## Blitz mechanic — CONFIRMED (screenshot, G1 "Blitz Laws" popup)

Consuming a fruit converts it into a fixed number of hours of Elemental Law
learning progress ("Blitz"), NOT a fixed amount of Law Points:

| Tier | Blitz value |
|---|---|
| Green | 1h |
| Blue | 3h |
| Purple | 6h |
| Yellow | 12h |
| Red | 14h (see below — not a natural growth tier) |

G1: "Law Fruits provide variable Law point rewards based on your Law points
generation rate" — i.e. a fruit grants N hours of whichever per-element
Learning Speed (K/h) it's applied to, converted at that element's *current*
rate, not a flat Law-Point sum. Since Learning Speed rises with a Law's
level (screenshot shows level and K/h moving together per element), the
actual point payout of a fixed Blitz-hour value grows over time — see the
"eat immediately" reassessment under Analysis.

UI shows **"Remaining Time: 120h"** — confirms G1's claimed 120h Blitz
budget as a real displayed number. The **daily reset cadence** is G1's
framing, not something the screenshot itself proves. Popup also has an
"Auto Blitz" toggle.

Worked example (owner's live account, screenshot pass 2026-08-20): Metal
Law Learning Speed 38.3M/h → one Green fruit's 1h Blitz value pays out
38.3M Law Pts, confirming the "hours at current rate" model directly
against a real number rather than just the mechanic description.

## In-game explanation text — CONFIRMED (screenshot, official "?" popup, 2026-08-20)

Verbatim from the Elemental Laws info popup, filling in mechanics the
community guides (G1) never covered:

- "Use Elemental Law Fragments to learn the Laws and increase their
  learning speed to gain more Law Pts." — Fragments are the resource
  that raises Learning Speed itself, separate from Blitz/fruit.
- "Law Pts are generated every minute from mastering Cosmic Laws. Your
  Law Pts = Learning Speed × Mastering Duration." — passive (non-Blitz)
  Law Pt income is framed as coming from "mastering Cosmic Laws," not
  directly from Elemental Laws; exact relationship between this passive
  trickle and the Blitz-based lump payouts above is not fully clear from
  the popup text alone — open question, not blocking for garden prep.
- "Upon a bottleneck, consume extra Elemental Law Fragments to break
  through." — a bottleneck/breakthrough gate exists, gated on Fragments,
  mechanism not detailed further.
- **"Auto Blitz unlocks when the total level of Elemental Laws reaches
  50."** — this is a different threshold from the per-element doubling
  milestones below; it's a one-time unlock keyed to the **summed total**
  across all 5 elements, not any single element's level.
- **"Inter-promoting" effect**: "If all five Laws reach the required
  level, you can activate the [Inter-promoting] effect for Law
  Suppression Boost/Resist." The in-game status bar shows this as
  "Inter-promoting: Elemental Laws reach Lv. 500 (1/5)" — so the
  required level is (at least at this bracket) 500 per element, and the
  effect is a Suppression boost/resist bonus once all five hit it. Not
  yet in the doc's Law Suppression section below prior to this pass.
- **Cosmic Laws** (extends the shared-pool note in the intro): divided
  into **Magical** and **Physical** categories, unlocked once Elemental
  Laws' total level meets a requirement. Grades raised with Law Pts;
  bottlenecks cost Nature Mantra (matches the existing Seeker Shop
  guidance). "Certain Cosmic Laws unlock Abilities when they reach the
  required grade." Cosmic Laws (and their unlocked Abilities) can be
  reset by spending **Fateum**, with all invested materials returned;
  each reset has its own cooldown.

## Law Point generation milestones — CONFIRMED (owner direct knowledge + screenshot, 2026-08-20)

Previously recorded as an imprecise community-tier claim ("doubles every
milestone, every 100 levels"), and an earlier pass at this doc mis-read
the 100-level track as a flat stat bonus — **corrected directly by the
owner**, who plays this system, superseding both:

- **Lv. 50, 150, 250, 350, 450, ...** (every 100 levels starting at 50),
  per element: Learning Multiplier **×2 — this is a literal doubling of
  that element's Learning Speed number**, not a separate bonus track.
  Owner's example: 10 Wood Learning Speed → hit Lv. 50 → 20 Wood Learning
  Speed. Compounds per element, hence the "push one element to each
  threshold before spreading to the next" strategy noted below.
- **Lv. 100, 200, 300, ... up to 1000, per element — this is NOT a flat
  stat bonus** (correcting the earlier read): it's the **Elemental Law
  Resonance** ladder, shown on the same Five Elements screen. Alternates
  **Law Suppression Boost +5%** (100, 300, 500, 700, 900) and **Law
  Suppression Resist +5%** (200, 400, 600, 800, 1000), grouped into two
  grades — **G1** (100-500) and **G2** (600-1000). At Lv. 1000 (ladder
  fully filled) a **"Completely Activated"** bonus unlocks: enhances the
  creation effects of the **Harmonia Shears** (the Red-tier Creation
  Artifact, see below), and raises the gains of **"Tao Motto"** (name as
  given by owner — not yet screenshot-confirmed spelling/identity, flag
  for a follow-up shot) and Law Suppression itself. Nothing else per the
  owner's description — no other stat/system benefits at full ladder.

## Law Suppression — trigger CONFIRMED (screenshot, 2026-08-20), formula community-tier (G2/G3, triangulated)

**Trigger mechanic, screenshot-confirmed** (official popup text): "If
the total level of the Elemental Laws exceeds the target, it will
trigger Law Suppression." Compare your **total** Elemental Law level —
summed across all 5 elements, not compared per-element — against a
target's total.

**Magnitude, still community-tier** (not restated in the official popup
text, only in the triangulated community sources): for every level your
total exceeds theirs by, deal **+0.05% additional final damage**, capping
at **+30% at 600 levels of advantage** (no further benefit past 600). E.g.
100 levels ahead of an opponent = +5% final damage against them. This is
presumably compounded/modified by the Elemental Law Resonance Boost/Resist
ladder above and the Inter-promoting bonus below — exact interaction not
captured yet.

**Inter-promoting**: a separate confirmed effect — once all 5 Laws
individually reach a required level (500, per the owner's current status
bar), an "Inter-promoting" toggle unlocks a Law Suppression Boost/Resist
bonus on top of the base mechanic above. Magnitude not yet captured.

**PvP vs. PvE scope**: owner's grounded conclusion (not a screenshot,
but reasoned from full game knowledge — treated as authoritative per
house convention on direct observation) is that Law Suppression is
**PvP-only**: there is no PvE content anywhere that references "law
levels" as an enemy stat, and the Resonance ladder above is itself
titled around Suppression Boost/Resist rather than any general damage
stat, reinforcing that Laws' whole point is PvP. Practically moot either
way — Laws are leveled for PvP regardless of whether a PvE side-effect
exists.

## Red tier — not a natural growth tier (Seralth, 2026-07-29)

The Blitz popup shows a 5th (Red) tier that G1's text never mentions. Resolved:
Red isn't grown — it's produced by the **Shears** relic, which spends energy
to advance an existing fruit up to Red. Red fruit's 14h Blitz value is
**exempt from the 120h/day cap** (same exemption pattern as Pills).

**This Shears is the Creation Artifact** documented in
`relic-summon-costs.md` (the relic summon point-track/monetization doc) —
same item, confirmed. That doc covers how you acquire it (cumulative
point breakpoints, cash/voucher cost); this doc covers what it does once
owned.

## Garden Pot artifact (Seralth, 2026-07-29)

**This Pot is also a Creation Artifact** — same acquisition doc as Shears
above, `relic-summon-costs.md`. Not to be confused with the two unrelated
curios below that also happen to be called "Pot":
**Zodiac Pot** (三相之壶, curio 91359, see `zodiac-relic.md`) and
**Dongxuan's Pot** (curio 91115, see `curio-effects.md`). Three separate
"Pot" items in this game; do not conflate any of them.

The Garden Pot is a growth-speed-up artifact, not Law-Fruit-specific
(applies to garden plants generally). It has two effects, and **for Law
Fruit only the first applies**:

- **Main effect, applies to everything**: 1 energy spent = 1 hour of
  growth speed-up. This is the Pot's whole relevance to Law Fruit — a
  reliable, large source of grow-time reduction, nothing more.
- **Secondary effect, gear-crafting plants only**: energy also raises
  those plants' "quality limit" from capping at Purple up to Yellow.
  **Does not apply to Law Fruit** — Law Fruit's tier ceiling is fixed
  regardless of Pot energy spent on it, so there's no way to grow past
  Green using the Pot alone (Red still requires the separate Shears
  relic). This resolves the earlier open question: the "concentrate
  everything in Green" conclusion under Analysis holds regardless of how
  much Pot energy gets thrown at Law Fruit.
- Energy regen is denominated in Taoist years — 1 Taoist year = 15 real
  minutes (see `game-mechanics-verified.md`'s core-mechanics note). 0-star
  grants +1 energy/year (= 4/hour = 96/day), capped at 200. Owner's Pot is
  currently **1-star**: +1.3 energy/year (= 5.2/hour = **124.8/day**), cap
  **300**, plus a flat **+15%** speed-up bonus on top.
- Energy can also be gained via "charge" — mechanism not detailed this
  session (open question).
- A 100-energy lump spend forces Red-tier evolution for gear-crafting
  plants (the mechanism behind the Purple→Yellow quality-limit boost
  above). Law Fruit's own Red-tier path is the separate Shears relic.

## Pet system daily speed-up spawns (Seralth, 2026-07-29)

Once-a-day spawn of generic (non-energy) speed-up items, distinct from the
Pot's energy-based speed-up. Spawn count scales with pets owned, capped at
10 pets. Owner's current banked stockpile: ~64h19m, accumulated over 2-3
days.

## Garden grid (Seralth, 2026-07-29; footprint re-confirmed via screenshot 2026-08-11)

Full unlock is a **6x6 grid** (36 cells); slots are purchased one at a time
at increasing cost from a smaller starting size. (Starting size is
unrecoverable/unknown and irrelevant — see Analysis: only the fully-unlocked
end state matters strategically.) Ploughwood Seeds occupy a **3-cell
L-tromino** footprint. **CONFIRMED (Seralth, 2026-07-29):** Law Fruit Seeds
share this same 3-cell L-tromino footprint, not just a visual resemblance.

**Visual confirmation (2026-08-11 garden screenshot):** grouped cells are
identifiable two ways once you look closely — a colored bridge overlay
connects the black-bordered cells belonging to one plant's footprint
(e.g. an L-shaped run of 3 cells), and cells within the same group can
echo the identical countdown timer down to the second in more than one
of their cells (two cells showing "64:47:25" simultaneously is the same
plant's timer, not two coincidentally-synced plants). Same footprint
mechanic confirmed for Soulrend Vine too (see below) — its "Energize"
plants in the same screenshot show the same connected-cell pattern.

## Fruit-growing strategy & seed supply — owner direct-knowledge (2026-08-20)

What to actually grow, and why, resolving the "which constraint binds"
question the 2026-07-29 Analysis below left open:

- Baseline, reliable seed income: **20 Law Fruit Seeds/week from the
  Sect**. Plan around this number only.
- Extra sources exist but are **not reliable enough to plan around**
  (owner, 2026-08-20, ~2 weeks of live Voidbreak data): roughly
  20-30 *additional* seeds total gained across those 2 weeks (so
  call it a small single-digit-per-week average at best), and a
  meaningful chunk of even that came from **P2W sources**, making it
  less viable to count on for a general strategy. Raw Blue fruits
  (not seeds — already-grown fruit) are also obtainable from some
  sources, roughly 10-20 seen so far, same reliability caveat.
  **Bottom line: budget for the guaranteed 20/week, treat anything
  above that as unreliable bonus, not a planning input.**
- Real play should default to growing **Purple**, not Green — Purple
  wins on Blitz-hours-per-seed (6 vs. Green's 1), and seed count, not
  garden cell-time, is the actual binding constraint in practice (see
  the resolved throughput contradiction immediately below). Blue and
  Yellow are both worse than Purple on a per-seed basis relative to
  their grow time and are skipped entirely.
- Green is only worth growing as a fast top-off: once Purple has already
  filled the day's 120h Blitz cap AND the weekly seed-reset is coming
  up (so there's no value in banking unused Purple-grown seed capacity
  past reset), quick-cycle Green fruit soaks up the remaining garden
  cell-time productively. Outside that window, Green is a worse use of
  scarce seeds despite being more grow-time-efficient.

**Throughput contradiction — RESOLVED (owner, 2026-08-20): seed supply is
the real bottleneck, not garden size or Pot energy.** At Purple's 6
Blitz-hours/seed, the reliable 20 seeds/week baseline caps out at ~17
Blitz-hours/day (20×6÷7) — nowhere near the 72-108 Blitz-hours/day the
Pot-energy ceiling analysis below computes from cell-time and Pot energy
alone, and confirmed unreliable enough that it shouldn't be modeled as
closing that gap. **This undercuts the Strategic Conclusion at the end
of this doc** (that fully unlocking the garden pre-Voidbreak is
high-leverage for Law Fruit specifically) — the Pot-energy ceiling and
Strategic Conclusion sections below describe a *cell-time* ceiling that
in practice never binds, because seed supply runs out first. Garden-size
unlock priority for **other** crops (Ploughwood, gear-crafting plants —
see the Garden update, next) is unaffected; this only concerns Law
Fruit's own throughput math.

## Pot-energy throughput ceiling — derived (2026-07-29)

Scenario: fully-unlocked 6x6 garden (12 seed slots), owner's 1-star Pot,
**no** pet speed-up items, all-Green (Green has the best Blitz-per-grow-hour
ratio of any tier — see Analysis — so it's optimal to concentrate both slots
and Pot energy there). **Caveat added 2026-08-20: this scenario assumes
unlimited Green seed supply, which the seed-income section above puts in
doubt — see the flagged contradiction there.**

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

**⚠ Partially superseded 2026-08-20 — see "Fruit-growing strategy & seed
supply" above.** The throughput ceiling computed below (72-108
Blitz-hours/day) assumes cell-time/Pot-energy is the binding constraint.
Owner's confirmed seed income (20/week reliable) caps real throughput at
~17 Blitz-hours/day instead — seed supply binds well before cell-time or
Pot energy do. The tier-efficiency math below (which tier per grow-hour
vs. per seed) is still correct and is *why* Purple is now the
recommended default (seed-bound favors per-seed efficiency); only the
final "fully unlock the garden for Law Fruit" conclusion is outdated —
see the rewritten conclusion at the end of this section.

Cross-checking G1's strategic prose against the confirmed numbers above:

- **"Prioritize green, avoid yellow" (G1) — only conditionally true.**
  Blitz-hours per grow-hour: Green 0.25, Blue 0.1875, Purple 0.15, Yellow
  0.136 — Green wins if **garden cell-time** is the binding constraint.
  But Blitz-hours per **seed**: Green 1, Blue 3, Purple 6, Yellow 12 — the
  exact opposite ranking, which wins if **seed supply** is the binding
  constraint instead. G1 never discloses which constraint it's assuming, so
  its blanket rule is incomplete, not universally correct.
- **"Eat fruit one-by-one, upgrade immediately" (G1) — revised: plausible
  mechanical basis, not confirmed.** Previous pass called this a baseless
  ritual on the assumption Law Points are a flat currency where order of
  operations can't matter. That assumption doesn't hold given the point
  above: Blitz value is hours-at-current-rate, not fixed points, and rate
  rises with level. If a level-up raises Learning Speed immediately, then
  blitzing fruit #2 *after* leveling from fruit #1 pays out more than
  blitzing both fruits back-to-back at the pre-level-up rate — a genuine
  reason to interleave rather than batch. Not confirmed: whether leveling
  actually raises rate mid-session (vs. only at reset/refresh), and
  whether a queued Blitz locks its rate at consumption-time or resolves
  later. Directionally plausible, not a ritual — but not pinned either.
- **Max theoretical garden throughput falls short of the daily cap.** Full
  6x6 (12 seed slots @ 3 cells/seed), all-Green, natural (non-boosted)
  grow speed: **72 Blitz-hours/day** — 40% short of the 120h/day cap even
  at full dedication and perfect packing. Every other tier tops out lower
  than Green at max packing, so 72/day is the organic ceiling.
- Pot energy alone (see above) closes most of that gap, to **~108/day**.
  The remaining ~12h/day is plausibly covered by banked pet-spawned
  speed-up items and/or occasional Shears/Red conversion (cap-exempt) —
  not concluded which dominates, or whether either fully closes it.
- **The garden genuinely competes for cells** (owner-confirmed): Ploughwood
  Seeds (for the Zodiac Relic) and gear-crafting plants use the same 36
  cells as Law Fruit — the 12-slot all-Green scenario above assumes zero
  competition, which isn't the real constraint. **Community wisdom
  resolves this anyway: dedicate the entire garden to Law Fruit, full
  stop, for about a real-life year** — Elemental Laws are considered
  important enough to be worth the opportunity cost of Ploughwood/gear
  plants losing garden access for that long. So the throughput numbers
  above are the right target to plan around even though the garden isn't
  Law-Fruit-exclusive by mechanic — it's Law-Fruit-exclusive by strategy.
- **Strategic conclusion (SUPERSEDED 2026-08-20, kept for history):**
  garden-slot unlock is a flat, area-scaling throughput multiplier that
  dwarfs any fruit-tier optimization G1 discusses. Since Law Fruit only
  becomes usable at Voidbreak, and Elemental Laws are G1's own pick for
  "the most important feature of Voidbreak," any garden slot not
  purchased before reaching Voidbreak is permanently lost throughput for
  however long it stays unbought — there's no way to retroactively
  recover missed Elemental Law levels. Fully unlocking the garden
  pre-Voidbreak, and running it 100% Law Fruit for roughly the first
  year of Voidbreak access, is higher-leverage than any fruit-tier
  strategy or competing use of the same cells.
- **Strategic conclusion — CURRENT (owner, 2026-08-20):** with seed
  supply (not cell-time) as the real bottleneck, garden-slot count stops
  being the lever for Law Fruit specifically once you have enough slots
  to comfortably plant a week's worth of Purple seeds (well under the
  full 12-slot/6x6 buildout — 20 seeds/week at Purple's 40h grow time
  needs only a handful of concurrent slots to never bottleneck on
  cell-time). Garden slots beyond that point are better spent on
  Ploughwood (Zodiac Relic upgrade material) or gear-crafting plants
  (Soulrend Vine — see the Garden doc), which don't share Law Fruit's
  seed scarcity. Fully unlocking the garden pre-Voidbreak is still
  correct — you want the *option* to run every crop type — but "dedicate
  the whole garden to Law Fruit for a year" is no longer the right
  default allocation once seed scarcity is accounted for.
