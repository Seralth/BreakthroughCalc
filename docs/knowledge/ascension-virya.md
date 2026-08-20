# Ascension Virya tracker

A per-realm progression tracker gating Esotability privileges behind
Myrimon Wonder boss clears and cross-path requirements — Incarnation
had its own version, this is the Voidbreak-updated one (owner,
2026-08-20). Full stage names, requirements, and bonus text are visible
on the in-game tracker screen — not reproduced here. This doc only
covers the two things that AREN'T obvious from looking at the screen.

## "Double" is not a ladder tier

It's a **Blessing Rewards ×2 badge** (daily pill count), present
identically in both Incarnation and Voidbreak. Not a stage — an earlier
screenshot-reading pass mistakenly attributed a real tier's panel to it;
that tier's actual name between Completion and Perfection (C) is still
unconfirmed. This also corrects the old Incarnation-era guess in
`game-mechanics-verified.md` ("×2 Cosmoapsis session") — struck through
there, superseded by this.

## Stacking rule (owner, 2026-08-20)

Within one tier, differently-worded bonus lines add together. Across
tiers, a line with the **exact same wording** reappearing later is the
same bonus carrying forward and updating in place — not additive with
its earlier value. (Matches the flat-bonus behavior already established
for Incarnation's Virya absorption bonus in `game-mechanics-verified.md`;
generalizes cleanly to Voidbreak per owner: "all the mechanics work the
same, it's just different tiers you gotta make to unlock each step.")
Also: a bonus scoped to the current realm stops applying once you
advance past that realm — the new realm's own line takes over instead
of stacking with the old one.

## Cultivation-speed relevance — not confirmed as literal

The stage bonuses use "Aura Absorption Ratio," not "Cultivation Speed"
— that phrase only appears on the separate Monsterscape tracker. Don't
wire this into `engine.py`/`engine.dart` without confirming what Aura
Absorption Ratio actually modifies.

## Open questions

- Real name of the tier mislabeled "Double" above.
- Whether "Aura Absorption Ratio" maps onto the calc's existing
  cultivation-speed formula.
