# Ascension Virya tracker

A per-realm progression tracker — owner confirms this isn't Voidbreak-
exclusive: **Incarnation had its own Virya tracker too**, and the one
captured this pass is the Voidbreak-updated version (owner, 2026-08-20).
Not yet in this repo's docs anywhere before this file. Distinct from
Monsterscape/Bloodline Refinement (`monsterscape-bloodline-refinement.md`)
— no confirmed mechanical link between the two systems yet, though both
were captured in the same screenshot pass.

## Sources

- Screenshot pass 2026-08-20 (owner's live account, Voidbreak (L) Late
  G6, character "Literatia" — matches the cultivation-screen capture
  from earlier in this pass): 5 screenshots of the Ascension Virya
  stage ladder. Treat as CONFIRMED for the Voidbreak version; the
  Incarnation-era version mentioned by the owner is not captured here.

## "Double" — a reward-doubling status badge, NOT a ladder tier (owner-corrected, 2026-08-20)

Present with the identical appearance in **both** Incarnation and
Voidbreak (owner confirms it "looked the same in Incarnation as well").
Owner has now identified what it actually means: **a doubling of
Blessing Rewards — i.e. your daily pill count.** It is not a ladder
stage, and not the "×2 Cosmoapsis session" guess recorded in the
Incarnation-era notes (`game-mechanics-verified.md`'s "Other observed
facts" — that guess is superseded by this). It sits visually between
tier circles, which is why the earlier screenshot-reading pass in this
doc mistakenly attributed a full Stat-Bonuses/Privilege panel to it —
that panel almost certainly belongs to a real (unnamed here) tier
between Completion and Perfection (C), not to "Double" itself. That
tier's actual name is not yet confirmed — the content below is kept
under its own heading pending a re-check of the screenshot/live screen.

## Stage ladder — CONFIRMED (screenshot, 2026-08-20; "Double" mislabel corrected above)

A horizontal stage ladder: Completion → **[unnamed tier, see below]** →
Perfection (C) → Perfect → Half Step → Aspiring Perfection (L) [shown as
"New: Wholeness (L)" at the current stage]. Each stage grants **Stat
Bonuses** (passive, always-on once reached) and unlocks a **Privilege**
gated behind a requirement — several of those requirements are "Clear
[a specific Realm]'s Mighty Monster — [boss name] in **Myrimon
Wonder**":

- **Completion**: Stat Bonuses = "Remove Realm Restrictions for Taking
  Cultivation Pills", "Blessing Rewards +1". Privilege "First
  Esotability" — requires Voidbreak (L) Late 100% + breakthrough.
- **[Unnamed tier — mislabeled "Double" in the original screenshot
  read; needs re-confirmation of its actual name]**: Stat Bonuses =
  "Voidbreak (L) Aura Absorption Ratio +20%", "Blessing Rewards +3".
  Privilege "DoublePathGear" — requires Primary Path → Voidbreak (L)
  Completion, Secondary Path → Incarnation (L) Late, AND "Clear
  Everfrost Realm Mighty Monster — Crimson Lion in Myrimon Wonder".
- **Perfection (C)**: Stat Bonuses = "Voidbreak (L) Aura Absorption
  Ratio +20%" (same wording as the tier above — carries forward, not a
  second +20%, see stacking rule below), "Absorption Ratio Before
  Wholeness (L) Middle: +20%" (a distinct/new line — windowed, dormant
  until Wholeness (L) Middle is reached), "Blessing Rewards +5".
  Privileges "DoublePathGear" + "Second Esotability" — requires
  Secondary Path → Voidbreak (L) Middle AND "Clear Everfrost Realm
  Mighty Monster — Cryovar in Myrimon Wonder".
- **Perfect / Half Step**: Stat Bonuses = "Voidbreak (L) Aura Absorption
  Ratio +40%" (same line as above, value updated 20→40 — still not
  additive with the prior 20), "Absorption Ratio Before Wholeness (L)
  Late: +40%" (a second distinct windowed line, dormant until Wholeness
  (L) Late), "Blessing Rewards +7". Privilege "DoublePathGear" —
  requires Secondary Path → Voidbreak (L) Completion AND "Clear
  Everfrost Realm Mighty Monster — Elemental Fiend in Myrimon Wonder".
- **Half Step / Aspiring Perfection (L)** (current stage, labeled "New:
  Wholeness (L)"): Stat Bonuses = "Wholeness (L) Aura Absorption Ratio
  +40%" (a NEW current-realm line now that Wholeness is reached — the
  old Voidbreak-scoped line stops applying, matching the "bonus scoped
  to current Stage" rule already established for Incarnation),
  "Absorption Ratio Before Perfection (L) Late: +40%" (windowed, dormant
  until Perfection (L) Late), "Blessing Rewards +11". Privilege "Third
  Esotability" — requires 3 Cultivation Path(s) → Wholeness (L)
  Completion AND "Clear Kunlun Realm Mighty Monster — Red-eyed Ni in
  Myrimon Wonder".

**Stacking rule (owner, 2026-08-20):** within one tier, each *uniquely
worded* line adds to the others (e.g. a live current-stage line plus an
already-active windowed line would sum). But across tiers, a line with
**the exact same wording** reappearing at a later tier is the *same*
bonus carrying forward and updating in place — not a second instance to
add on top of the earlier one. This is the general form of the flat-
bonus rule already established for Incarnation (where every observed
tier happened to repeat the identical "+20%" wording, making it look
like a single flat value); Voidbreak's version updates that same
carried-forward line to larger numbers per tier instead of staying
fixed at one number, but the "don't stack identical wording" mechanic
itself is identical between realms.

**Myrimon Wonder** is a location containing realm-specific "Mighty
Monster" boss fights (Crimson Lion / Cryovar / Elemental Fiend tied to
Everfrost Realm; Red-eyed Ni tied to Kunlun Realm) that gate these
Esotability privileges.

A persistent status-bar element ("Demonic Miasma — Ends in 44d 3h") was
visible in these captures — unrelated debuff/buff, out of scope, see
`CLAUDE.md`/prior notes: ignore Demonic Miasma until Wholeness.

## Cultivation-speed relevance — not confirmed as literal

None of the 5 screenshots use the exact phrase "Cultivation Speed" —
that phrase only appears on the separate Monsterscape/Bloodline
Refinement tracker. The closest tie here is **"Aura Absorption Ratio"**
(e.g. "Voidbreak (L) Aura Absorption Ratio +20%/+40%"), which by naming
pattern plausibly affects how fast realm/cultivation progress advances
from Aura — but this is inference from the stat name, not a confirmed
mechanical link to the engine's cultivation-speed math. Don't wire this
into `engine.py`/`engine.dart` as a Cultivation Speed multiplier without
further confirmation of what "Aura Absorption Ratio" actually modifies.

## Comparison against the Incarnation-era version (already documented)

`game-mechanics-verified.md` has an extensive, owner-corrected writeup of
this same system from Incarnation (2026-07-15 screenshots, corrected
2026-07-20/21/22 — see that file's "Ascension Virya blessings" section).
Both discrepancies an earlier pass of this doc flagged are now resolved
directly above: the stacking/carry-forward rule generalizes across
realms unchanged (see "Stacking rule" under Stage ladder), and "Double"
is confirmed to be the same non-tier reward-doubling badge in both
realms, just previously mis-identified (see the "Double" section above)
— its actual mechanic (Blessing Rewards ×2) supersedes the old
Incarnation-era guess ("×2 Cosmoapsis session").

What's consistent across both realms: the "Clear [boss] in Myrimon
Wonder" gating pattern, the Completion tier's wording pattern ("Reach
[Realm] (L) Late 100% and break through"), Blessing Rewards scaling up
per tier, and the general Esotability-privilege structure. The realm
name substitutes (Incarnation → Voidbreak → presumably Wholeness next),
but boss names are apparently unique per realm (Amethyst Fiend/Jade-Eyed
Lion in Incarnation vs. Crimson Lion/Cryovar/Elemental Fiend/Red-eyed Ni
in Voidbreak) — no boss name reuse observed between the two realms.

## Open questions

- What did the Incarnation-era version of this tracker look like — same
  stage names/structure, or different? Not captured this pass.
- Does "Aura Absorption Ratio" map onto anything already in the calc's
  cultivation-speed formula, or is it a separate multiplier layer?
- Full requirement/bonus text for stages beyond "Half Step / Aspiring
  Perfection (L)" — not reached yet on the owner's account.
- Esotability privileges (First/Second/Third) — what do they actually
  unlock beyond the stage-gate itself?
