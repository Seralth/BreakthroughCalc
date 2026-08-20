# Ascension Virya tracker

A per-realm progression tracker gating Esotability privileges behind
Myrimon Wonder boss clears and cross-path requirements — Incarnation
had its own version, this is the Voidbreak-updated one (owner,
2026-08-20). Full stage names, requirements, and bonus text are visible
on the in-game tracker screen — not reproduced here. This doc only
covers the two things that AREN'T obvious from looking at the screen.

## "Double" — closed, ignore it

Just a spacer between real tiers, does nothing on its own — "Double" is
its own label, not a stand-in for some other tier's name. Present
identically in both Incarnation and Voidbreak. Possibly maps to bonus
pills, but doesn't matter either way. Corrects the old Incarnation-era
guess in `game-mechanics-verified.md` ("×2 Cosmoapsis session") — struck
through there, superseded by this. Not an open question — don't keep
re-flagging it.

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

## Cultivation-speed relevance

Aura Absorption Ratio IS the calc's core Absorption Ratio input — that's
the whole premise of `engine.py`: `Cultivation Speed = Abode Aura ×
Absorption Ratio`. Virya's stage bonuses feed directly into that same
number (same as the already-confirmed Incarnation-era Virya pp, verified
via live arithmetic — `Abode 270.20 × 0.60 = Speed 162.12`). Not a
separate system, not a maybe.
