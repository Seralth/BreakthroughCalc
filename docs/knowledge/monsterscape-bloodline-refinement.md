# Monsterscape — Bloodline Refinement reward tracker (Voidbreak+)

Monsterscape unlocks at Voidbreak; its reward tracker is the "Refine
Blood" screen, spending Bloodstones on a rank ladder of autoplay/combat
perks. Full ladder (ranks, costs, effects) is visible in-game — not
reproduced here. The one fact worth recording:

**Cultivation Speed total — CONFIRMED (owner, 2026-08-20): live banner
reads +70%,** from four of the ladder's ranks. Nothing else on the
tracker contributes to it — an earlier read of this doc mistakenly
added a "Completion" bonus that turned out to be a shaded background
artifact from the page behind the popup, not a real fifth effect.

**Not a calc engine input.** This +70% isn't a togglable lever — it's
already baked into whatever flat Cultivation Speed number the player
reads off their own screen. `engine.py`/`engine.dart` only ever take
Cultivation Speed as one flat user-entered number and never decompose
it, so any effect that changes that on-screen number — Monsterscape
included — is automatically captured just by entering the current
value. No engine change needed, now or for any future system that
works the same way. Contrast with Aura Gem (a real togglable input) and
Absorption Ratio (a distinct input used to project future-grade speed).
