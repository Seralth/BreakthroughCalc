# Data-gathering screenshot checklist (set 2026-07-21)

Fills the open `gap`/`need` entries in `docs/design/sources-shelf-inventory.md`.
Organized by in-game screen so you can grab a batch each time you're in that
menu. Each shot should show the tooltip/effect TEXT clearly (values are
server-side, so the screen is the source of truth). Tick items as they land;
when a batch is in, drop the PNGs somewhere and ping me to transcribe →
`data/sources.json` + knowledge docs.

Priority: **P1** = sharpens the advisor most + easy to grab · **P2** = useful,
straightforward · **P3** = tedious / low marginal value · **GATED** = needs
progression you don't have yet (do opportunistically).

---

## A. Technique-book tier screens  (open each book → capture the full tier ladder with effect text)

Most of these have a KNOWN effect value but an UNRECORDED tier threshold, or a
roadmap-recommended tier whose payoff we've never seen. One clean shot of the
tier list per book resolves them.

- [ ] **P1 Astrology** (R4) — tier of the Respira **+3%** line; AND the **Tier 7** payoff
- [ ] **P1 Yin's Grasp** (R6) — tier of the Respira **+5%** line; AND the **Tier 10** payoff
- [ ] **P1 Golden Core** (R4) — which tier grants Respira **+1%**
- [ ] **P1 Cosmic Power** (rank?) — book **rank**, and tiers of its **+1 attempt** and Respira **+3%** lines
- [ ] **P1 Taiyin Meridian** (rank?) — book **rank**, and tier of the Respira **+3%** line
- [ ] **P1 Floral Essence** (R7) — tier of the Respira **+3%** line
- [ ] **P1 Great Yang Manual** (R7) — tier of the Respira **+5%** line
- [ ] **P1 Purify & Cleanse** (rank?) — book **rank** (values already known)
- [ ] **P1 Energy Unification** (rank?) — book **rank**
- [ ] **P2 Dragon's Flight** (R6) — payoffs above Tier 3 (esp. **Tier 10**)
- [ ] **P2 Bloodization** (R5) — **Tier 7** payoff (may be combat-only → then "no calc effect")
- [ ] **P2 Immortal Ascension** (R10) — **Tier 13** payoff
- [ ] **P2 R8 books** (Tao of Taiqing, Origin Scripture, No-Thought Sutra, Dracophant) — confirm they have **no Respira/attempt lines** (pill-effect absence already confirmed; just need Respira columns)
- [ ] **P3 R9 books (all)** — full list + every effect (nothing recorded; roadmap has no R9 picks either)

## B. Immortal-friend bonus screens  (open friend → the level/bonus breakdown)

- [ ] **P1 Crane Boy** — the **level number** at which its **+1 pill attempt** lands (currently "max, number unknown")
- [ ] **P2 White Astra** — **level 31** payoff
- [ ] **P2 Princess Adalinda** — **level 81** payoff
- [ ] **P2 Leizhenzi** — **level 129** payoff

## C. Artifact detail screens  (open artifact → upgrade/star preview showing every star's effect)

The upgrade screen usually previews all star tiers at once — one shot each.

- [~] **P1 Starsea Vase** — PARTIAL (owner 2026-07-21): regen progressive 0★1→2★1.6→3★2 /Taoist Yr; cap 0★200→1★300→2★400→3★500 (+100/star). Special effects ONLY at stars **1/2/5** (3-4 stat-only, awakening separate) → EXP mapping corrected to 1★+10% / 2★+20% / 5★ no-cost. STILL need: confirm exact **1★/2★ EXP values** from tooltip; the **awakening** effect; **1★/4★ regen**; **4★/5★ cap** (pattern predicts 600/700); which refined **red pills** unlock per Vase tier (gates Mirror copies)
- [ ] **P1 Dual-Star Mirror** — **star 2 & 4** effects; regen/cap per star; whether the **1★ −5% and 3★ −10%** copy-cost discounts **replace or add**
- [ ] **P2 Timereversal Pearl** — per-star **energy-cost discount** values; **star 2–5** effects; regen/cap per star
- [ ] **P2 Aura Gem** — do **rarities below Rare** exist (values?); the per-rarity **claim-cap hours** between 18 and 32 (Legendary=32 known)

## D. Mark / treasure tooltips

- [ ] **P2 Star Marks** — which systems grant them (Constellation Altar / Samsara?) and **per-level pp** values, split by pill color (gold/purple/blue)
- [ ] **P2 Dao Ancestor (Daozu) treasures** — item list + pill-effect / mark **values** (read each tooltip)
- [ ] **P3 Lotus Throne** — its mark values and **which color(s)**

## E. Respira / base-count readings  (cultivation & Respira screens)

- [ ] **P2 Respira per-attempt value at Voidbreak** — one display reading once you're in Voidbreak (predicted ~**12.8–12.9k**; confirms the per-Stage base table). *(Do this at the same time as the Voidbreak blessing read — see §G.)*
- [ ] **P2 Base daily pill attempts** — the pill screen value with **zero pill-attempt sources** owned (what `pill_limit` floors to)
- [ ] **P3 Base Respira attempts per character level** — the yunqi_limit ladder (client has 2@lv1 → 10 default; full ladder unknown)

## F. Elixir tolerance ladders  (elixir "Used count" screen)

- [ ] **P3 XP-elixir ladder widths** — capture the **Used counter** as you cross each tier boundary (ratio steps 150→120→100→70→50→30→20→0). Tedious; grab opportunistically as tiers flip. *(Stat-elixir ladders don't matter to the calc — skip.)*

## G. Ascension Virya  (ties to the ~Aug 3 Voidbreak read)

- [ ] **GATED Voidbreak blessing value** — THE big one (§1 of the docket): does +20% persist into Voidbreak? does the "Before Voidbreak Middle" line activate, at what value? Read the absorption panel in VB Early. Unblocks the blessing re-model + guide/prestock redo.
- [ ] **GATED Half Step** (4th Virya tier) — its bonus (once you reach it)
- [ ] **GATED Post-ascension privileges** — the structure behind the dump-only "+200% absorption + high-stage pill access"
- [ ] **P3 "Double" ×2-Cosmoapsis badge** — confirm the ×2 by comparing the /Cosmoapsis readout during vs after the session timer (plausible-but-unverified)

---

## Already resolved — do NOT re-shoot
- Additive-pp (40%+20% → 60%, not 48%): DONE (Abode 270.20 × 0.60 = Speed
  162.12). Inventory line 150 still lists it as a "need" — stale, drop it.
- Virya tier STACKING: corrected to flat +20 in Incarnation (owner account,
  2026-07-20). Only the Voidbreak carry-over (§G) remains open.
- Respira bases Nascent (3,157) / Incarnation (6,385): recorded.

## How to hand a batch back
Screenshots → any folder (e.g. `~/Downloads/…`), tell me the folder. I'll
read the tooltip text, write the values into `data/sources.json`
(with `data_status`), update the knowledge/inventory docs, and clear the
matching checkboxes here.
