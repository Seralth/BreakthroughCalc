# Pet mechanics (exchange, rarity, feeding)

Gathered 2026-07-17 from four community sources; per-claim provenance below.
This backs the Guide → Pets page and the Vault pet planner.

## Sources

- **S1** — "Pet Guide" Google Doc (docs.google.com/document/d/1973GT6uISjN-q8mD-VcHsf2RjDWbjFzTvcwo2Ls7Rng), saved at `~/Downloads/pets.txt`.
- **S2** — Pet calculator spreadsheet (docs.google.com/spreadsheets/d/1AFIvDZl2i5952C_jZ_NrmcMafAUWivwAohhOBQkUevo), all 4 tabs saved at `~/Downloads/pet-calc-*.csv`. Formulas inspected from xlsx export (see "Exchange model" below).
- **S3** — Taiyi video "Overmortal guide: Pet" (youtube.com/watch?v=R4qxx_9MaM4), manual EN subs; transcript at `~/Downloads/pet-video-overmortal-guide-pet.txt`.
- **S4** — BBG video "WHICH PET WOULD I PICK" (youtube.com/watch?v=ahEMEPWFXSg), auto captions; transcript at `~/Downloads/pet-video-which-pet-would-i-pick.txt`.

None of this is screenshot-verified from the game yet; it is community data,
internally consistent across the four sources except where noted.

## The six pets (S1, S3, S4 agree)

| Pet | Role | Exchange cost (rare essences) |
|---|---|---|
| Blazelion | Highest single-target dmg; Corporia debuffs (P.Atk dmg taken +20%, own P.Atk +10%) | 5 Metal + 5 Wood |
| Babewyrm | Best AoE; Magicka debuffs (M.dmg taken +20%, M.Def down) | 5 Water + 5 Fire |
| Babetoise | Tank; taunt; P.Evasion/P.Def buffs | 5 Metal + 5 Earth |
| Babeox | Average dmg; stun (75%/2 s); removes enemy buffs; **boosts P.Evasion** (S1, missing from an earlier pass of this table) | 5 Wood + 5 Water |
| Babedeer | PvP support (debuffs PvP dmg resistance); double cost — whale trap | 10 Fire + 10 Earth |
| Berpent | Tanky; 2nd-highest ST dmg; buff-removal; crit-res down | NOT exchangeable (event-only). **Correction:** S1 names a specific, different route — Round-completion Rewards of the weekly **Thunderwave Event** — not "Special pet eggs"/Adventure exchange/Beast Wave as previously written here; that framing doesn't appear in S1, S3, or S4 at all. If the Adventure-exchange reading came from a more recent direct observation it supersedes S1, but as sourced it should say Thunderwave Event. |

Skill % figures in the table are from S4 (spoken, auto-captions) — treat as
approximate until seen in a tooltip.

## Exchange model (S2, VERIFIED from sheet formulas, xlsx export)

- Eliminating a pet copy refunds its FULL exchange cost in rare essences.
  Berpent eliminates into 5 Water + 5 Earth despite not being exchangeable
  (formula: `G12 = ... + B8*G8`, `I12 = ... + B8*I8` with G8=I8=5).
- Elimination costs 20 fateum per pet (S3, spoken; not in S2).
- Total essence pool per type = owned essences + Σ(owned copies × refund).
- Copies obtainable of pet P = floor(min over P's two essence types of
  pool/cost). (`E16 = ROUNDDOWN(MIN(E12,F12)/5,0)` etc.)
- **Sheet bug**: `I12` (Earth pool) omits owned Earth essences (`+B15`
  missing). Our implementation includes it. Do not "fix" our code to match
  the sheet.

## Rarity ladder (S2 "Calculator" tab, right-hand table)

Cumulative pet copies consumed to reach each tier, pet-realm requirement to
apply the upgrade, and epic essences required (blank = not charted in S2):

| Rarity | Copies (cum.) | Pet realm req | Epic essences |
|---|---|---|---|
| Common | 1 | Primitive | 0 |
| Uncommon | 1 | Primitive | 0 |
| Uncommon +1 | 1 | Virtuoso Early | 2 |
| Rare | 2 | Virtuoso Late | 5 |
| Rare +1 | 3 | Nascent Early | 9 |
| Rare +2 | 5 | Nascent Middle | 13 |
| Epic | 8 | Nascent Soul Late | ? |
| Epic +1 | 11 | Incarnation Early | ? |
| Epic +2 | 14 | Incarnation Middle | ? |
| Legendary | 17 | Incarnation Late | ? |
| Legendary +1 | 21 | Voidbreak Early | ? |
| Legendary +2 | 26 | Voidbreak Middle | ? |
| Legendary +3 | 32 | Voidbreak Late | ? |

Note Common/Uncommon/Uncommon+1 all sit at 1 copy — the sheet's achievable-
rarity lookup returns the LAST tier ≤ copies, so 1 copy reads as Uncommon+1.

Provenance nuance (xlsx formulas): copy counts for Epic…Legendary+2 are
FORMULAS in S2 (`=M8+3`, +3, +3, +3, +4, +5) anchored on Rare+2=5 and
Legendary+3=32 (both hardcoded) — i.e. partly extrapolated by the sheet
author, though consistent with S4's spoken "you start needing 8, 9, 10
copies" for late steps. Epic-essence figures 5/9/13 are cumulative sums of
a per-essence-type table charted only for Babetoise.

## Pet realm XP (S2 "Pet Realm XP Data" tab — raw values, no formulas)

Connection F2 13 XP → Voidbreak Middle cumulative 230,088,727. Full table in
`~/Downloads/pet-calc-pet-realm-xp.csv`. Voidbreak Late unknown.

## Feeding (S2 "Feed Data" tab)

Pet XP per pill by pill rank and rarity (Common/Uncommon/Rare/Epic/Legendary):
- R1 (Cleansing Powder/Aura Pill): 125 / 250 / 400 / 750 / ?
- R2 (Nutrition Powder/Revitalising Pill): 625 / 1250 / 2000 / 3750 / ?
- R3 (Crimson Powder/Ice Heart Pill): 1900 / 3800 / 6080 / ? / ?
- R4 (Purity Powder/Dracospirit Pill): 5000 / 10000 / 16000 / ? / ?
- R5 (Chalcedonius Powder/Reinvigoration Pill): 8000 / 16000 / 25600 / ? / ?
R6+ pills: no data. Ratios within a rank: ×1 / ×2 / ×3.2 / **×6** (R1–R2 —
correction: recomputed directly from the feed-data values, 750/125=6.0 and
3750/625=6.0, not the previously-stated ×7.5), R3–R5 Rare is ×3.2 (confirmed
exact).

Food: Platycodon 3,500 · Siler 11,000 · Redarrow Flower 33,500 · Dragongall
Flower 54,000 · Curculigo 79,000.

Sheet's own advice (community, not verified): don't feed Rare+ pills at low
realm.

## Which pet — community positions (subjective; keep framed as recommendation)

- One pet only: unanimous (S1, S3, S4). Costs scale steeply; multi-pet
  activities are limited (Realm Map allows one).
- Corporia → Blazelion: unanimous.
- Magicka → SPLIT. S1 + S3: Blazelion anyway (pet's own damage ≈ scales with
  its rarity; Flame Essence scarcity leaves a Wyrm ~2/3 the strength of a
  Lion long-term; S1's ~50% vs ~30% argument). S4: Babewyrm for the Magicka
  debuffs, while conceding fire essence is the scarcest and Wyrm the hardest
  pet to level. App framing: state both, let the planner show the user's own
  achievable-rarity gap.
- Babedeer: unanimous avoid (double cost, PvP-only value).
- Berpent: event-only; realistic for heavy spenders only (S1).
- Pets matter in PvE damage rankings (Abyss boss, Monster Hunt, Town Boss,
  tower), not PvP (S1, S3 with in-game before/after numbers: 1200B→1900B
  Abyss dmg, 18000→25340 Monster Hunt points switching Turtle→Lion).

## Open questions

- Legendary pill XP per rank; Epic pill XP for R3–R5; R6+ pill feed values.
- Epic-essence requirements for Epic tier and above (S2 charted 2/5/9/13
  through Rare+2 only, and per-essence-type breakdown only partially, for
  Babetoise).
- Whether elimination refund is truly 100% of cost in-game (S2 models it as
  such; S3 says elimination yields "purple material" = rare essences).
- Skill Demonroot costs: S2 "Skill Data" tab is marked WIP; levels 1–62
  charted with realm gates (saved in pet-calc-skill-data.csv).
