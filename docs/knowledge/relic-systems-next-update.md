# Relic systems — integration-readiness digest

Both **Equipment Relics** (`equipment-relics.md`) and the **Zodiac Relic**
(`zodiac-relic.md`) are fully client-side-verified but not yet wired into
the calc (no Vault catalog entries, no combat-power modeling). This doc
pulls the confirmed, high-confidence subset of both into one reference for
scoping that work — the two source docs still hold full detail, per-field
citations, and the open questions; this is the "what can we build on right
now" digest.

Curios (`curio-effects.md`) aren't included here — that system is already
in the Vault catalog and doesn't need a scoping pass.

## Equipment Relics — fully modelable today

327 relics (`cfg_us_equipment`, `classify: 法宝`), one combat skill each,
occupying 6 of a build's equipment slots. They sit on the **same gear
system as weapon/armor/accessory** — no relic-specific formulas to invent.

- **Identity**: rank (1–14) selects which skill you have; level within rank
  and quality scale surrounding stats only, never the skill itself.
- **Rank**: gated by player level, the same realm-gate rhythm as curios and
  the Zodiac Relic (2/12/15/18/21/24…/45).
- **Level curve** (`equip_rank`, 47 rows, exact): `score` 120 → 17.6B,
  `equip_skill_cost` 1 → 31.8B. `capacity_coef` (efficiency/point) tapers
  9 → 5 → 1.432 → 1.828 → 1.606 across levels 1–32, then is unlabeled for
  33–47.
- **Quality** (`quality.lua`, shared 6-tier ladder — white/green/blue/
  purple/orange/red): `attrib_scale` 0(white, no affixes) / 0.75 / **1.0
  baseline** / 1.5 / 2.0 / 2.5. Cost (`price_scale`) spreads 20× (green→red)
  against 2.5× stats — each tier is worse value than the last.
  Quality-up odds are flat 20% per step except **orange→red at 10%**.
- **Forging gate** (`level_forge`): a 52-level, 13-rank-group blacksmith
  skill progression 1:1 with equipment rank. Junior tier caps at blue,
  Peak unlocks orange, confirmed by `target_quality` fields.
- **Star layer** (`equip_levelup`, 6 steps): flat `attrib_fix` bonuses +
  grows socket capacity (`extra_ashram_max`, steps 2–6). Hard gates at
  levels 21 and 42.
- **Set bonuses**, two independent stacking systems: slot-count sets
  (`equip_suit`, 8 sets × 4 tiers, thresholds 6/9 pieces then affix-count
  gated) and affix-collection sets (`equip_affix_suit`, 12 entries, level
  gates 39/42/45).
- **Class vs generic relics are peers** (owner-confirmed): identical slots,
  cost, and tier ceiling — the only difference is class-lock and which
  skill each grants. No generic-is-weaker hierarchy to model.
- **Quality does not touch skill damage/effect magnitude** — confirmed
  across all 327 relics (0/462 live skill-bearing entries carry a `quality`
  field). Skill strength is purely a function of rank.

Net: "how strong is my relic" cleanly decomposes into rank (skill) × level
(exponential grind, exact curve) × quality (stat multiplier, blacksmith-
gated) × marks/sets (min-max layer) — every one of those four axes has an
exact, cited formula or table already.

## Zodiac Relic — what's solid enough to build the stat-block contribution

One relic per account (`talisman_*`), forged into a physical/magical stance,
deploys into battle from Rank 2 and adds its own stat block to combat power.

- **Two types, one shared progression** (`talisman.lua`): id 78300 (physical,
  `hp`) / 78301 (magical, `mp`). Base level curve is **pure-linear** and
  identical between the two paths: `level N ≈ 2,092,404 × N` HP/MP,
  `19,616 × N` ATK, `3,923 × N` DEF, confirmed by regression (max deviation
  28 over 40 levels). L40 = 83.7M HP / ~785k ATK / 157k DEF.
- **Reforge (path swap)**: `reforge_cost = 500` Fateum, `forge_cd = 172800`s
  (48h). Only one path active at a time; swap is non-destructive
  (owner-adjudicated — no loss warning exists, and a sellable reforge item
  wouldn't be designed to wipe investment).
- **Rank ladder** (`levelup_preview_config` + standalone gate fields, fully
  cross-checked): R1 innate stats + Soulfice; R2 battle-ready + Hex +
  skill-slot; R3 socket unlock + model enlarge; R5/R7 inlay slot + Hex +
  skill-slot; R8 new appearance + Mold unlock (`unlock_mold = 8`); R9 inlay
  slot + Auto-Soulfice (`rank_for_fast_levelup_unlock = 9`).
- **Own stat block** (`talisman_config.attrib_sort`, 20 keys, exact order):
  HP_max, MP_max, hp/mp_attack, hp/mp_defense, hp/mp_hitrate, hp/mp_dodge,
  crit_chance, crit_resistance, pve_talisman_attack, pvp_talisman_attack/
  defense, talisman_criti_attack/defense, crit_damage, talisman_final_
  attack/defense. This is a complete, typed field list — enough to model
  the relic's stat-block contribution to combat power on its own.
- **Socketing counts**: 16 Marks (`talisman_marks`, 2 slots, 3-merge to next
  tier, unlocks Rank 3) and 8 Socket treasures (`slot_treasure`, unlocks via
  material ids 93001–93007 in varying quantities, one socket with no
  material gate at all).
- **Mold** (`talisman_mold`, 14 molds, unlocks Rank 8): star-upgradeable
  via a confirmed 85-row table (17 mold groups × 5 rounds), material
  700207 universal + one mold-specific id per group.

**What isn't modelable yet — Hexes.** Each relic casts 3 exclusive Hexes
(6 skill ids total, IDs and unlock ranks confirmed), but no file in the
current extraction carries their cooldown, quality, rank, or damage
effect — that needs either a different config table or in-game tooltip
reads. Any combat-power model built from this doc should treat Hex damage
the same way `technique-books.md` treats capstone effects: acknowledged,
not calc-relevant until sourced.

## Recommended first-pass scope

The stat-block contribution (both systems) is fully specified and exact —
that alone is enough for a first Vault/combat-power integration pass.
Leave Hex damage modeling out of scope until the gap above is closed; it
doesn't block shipping the rest.

## Outstanding blockers (see source docs' own Open Questions for full list)

- Zodiac Relic Hex CD/quality/rank/damage — no source in this extraction.
- Zodiac Relic per-node Soulfice stat values and the node grid's exact
  round/rank/level-gate mapping.
- Equipment relic `equip_recipe` forge-cost breakdown and the
  `affix_marks_template` → rollable stat-pool mapping.
