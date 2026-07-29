# Zodiac Relic (本命法宝) mechanics — client-side extraction

Personal reference for the **Zodiac Relic** system. Sourced from the client APK
decompile (`apk_analysis/`) plus in-game confirmation by the owner. Verified-from-
config vs inference is flagged throughout; confident-wrong is the worst failure mode.
Core facts (mirrored paths, non-destructive reforge, linear Soulfice scaling,
socketing/mold layers, Hexes unquantified) are now integrated into
Reference → Combat Stats & Gear; the full RE detail below (exact node-grid
mapping, per-item socket costs, mold star-upgrade tables) stays here as
backing detail. Still not wired into the calc's actual math (Vault /
combat-power).

## Identity — do not confuse with the Zodiac Pot curio

- **Zodiac Relic = 本命法宝** ("natal magic treasure"). 本命 = "natal / one's
  zodiac-year", which is why localization renders it "Zodiac". Internal config
  prefix: **`talisman_*`**. It is a standalone progression system, NOT a curio.
- **Zodiac Pot (三相之壶, curio id 91359)** is an unrelated *curio/gubao* that merely
  shares the "Zodiac" English word. See `curio-effects.md`. Keep them separate.

Extraction: bytecode tables dumped via `apk_analysis/curio/dump_table.lua` under
`luajit`; English terms resolved from `apk_analysis/om/decrypted/i18n_*.lua`.

## What it is

A personal signature artifact — you forge **one**, bonded to your path. It is not
swappable gear; it grows alongside you and **deploys into battle** (from Rank 2) as
a semi-autonomous unit that casts its Hexes and carries its **own full stat block**
that adds to your combat power (`combat_capacity_coef` folds it into 战力).

## Two types — one path, mirrored (verified, with caveats)

Exactly two relics exist (`talisman.lua`):

| id | `talisman_type` | path | notes |
|---|---|---|---|
| 78300 | `hp` (inferred from desc text + naming, not a literal field) | **Corporia / Physical** (color #973434, embedded in desc string) | 纯钧之器; 5 sword forms 纯钧剑→金霞剑→鸿光剑→神光剑→太一剑 (the "Enlarge" model progression) |
| 78301 | `mp` (literal field value) | **Magicka / Magical** | hexes `skill_list [8510,8511,8512]` |

Caveat: 78300 has no `talisman_type` field at all in `talisman.json` — `hp`
is a reasonable inference from its desc text ("适合物理系修士", "suited to
physical cultivators") and the `hp_node_*` naming convention in
`talisman_levels.json`. 78301 has no `desc` field, so it carries no
comparable color field.

**The two paths are the SAME progression, mirrored** — physical vs magical only
changes which stat type the identical structure outputs:

- **Base level curve** (`std_talisman_level_calc`): a single shared table grants
  `hp` and `mp` stats **equally** at every level (L40 = 83.7M HP *and* 83.7M MP,
  hp_attack/mp_attack both 784,652 → ~785k rounded — identical, confirmed with
  zero mismatches across all 41 rows). A third parallel pair on the same table,
  `hp_defense`/`mp_defense`, is *almost* but not quite identical: `mp_defense`
  is exactly 1 less than `hp_defense` in 20 of the 41 rows (a rounding
  artifact, e.g. L2: 7847 vs 7846) — negligible in practice, but the pair
  isn't byte-identical the way hp/mp/atk/max are.
- **Soulfice node grid** (`talisman_levels`): `hp_node` and `mp_node` trees
  match exactly on level/round/cost for every one of the 40 ranks (same
  materials 97050/97051/97052, same amounts). They are **not** a perfect
  structural mirror though: every `mp_node` entry carries an extra
  `class_id:78301` field no `hp_node` entry has, and in this extract the
  hp-side rank-10 entry is missing its `node` array entirely (no per-node
  list) while the mp-side rank-10 has the full 9-node list — hp totals 338
  nodes vs mp's 347 (a 9-node gap, likely an export artifact rather than a
  real design asymmetry, but not verifiable either way from this data).
- **Hexes**: structurally two 3-hex sets exist (see Hexes section below), but
  the specific cooldowns/quality/rank claimed for them are **not confirmed
  by any file in this extraction** — see that section for the full caveat.
- **Marks**: only 12 of the 16 stones are type-matched HP/MP stat stones on a
  shared schema; the other 4 are proc-effect "trait stones" unrelated to the
  HP/MP split — see the Socketing section.

So there is no separate "physical grind" and "magical grind" — it is one
progression re-expressed as physical or magical — but several of the
specific "mirrored" details above have small asymmetries or gaps once
checked against the raw tables rather than assumed by symmetry.

## Reforge = path swap (owner-confirmed mechanic)

- The "Reforge Zodiac Relic" action swaps physical↔magical (owner-confirmed
  in-game behavior). The config's own terms are **重铸** ("recast", the cost
  field: `"reforge_cost":{"desc":"重铸需要消耗的机缘","value":500}`) and
  **铸造** ("forging/casting", the cooldown field: `"forge_cd":{"desc":
  "铸造CD","value":172800}`). Cost `reforge_cost = 500` Fateum (机缘) or a
  Reforge Card/Stone (本命重铸石/重铸卡, not itself in this config). Gated by
  `forge_cd = 172800` (seconds → 48h inferred from the value; the desc
  doesn't state the unit).
- **Only one type is active at a time** (owner-confirmed) — the swap changes which
  is live; both cannot run together.
- **Swapping is non-destructive** (owner-adjudicated 2026-07: the client shows no
  lost-progress/lost-item warning, and a cheap repeatable reforge with *sold*
  reforge cards would not be designed to wipe investment; consistent with every
  comparable system). The inactive type's progress is preserved but dormant. No
  dialog/warning string table exists in this file set to prove it directly.
- Practical read: the physical/magical choice is a **single active stance**, not a
  permanent commitment and not a run-both setup. You build the type you run; you
  *can* swap on the CD when path/content genuinely calls for it, without regrind.

## Soulfice (祭灵) — the stat backbone (verified, node-grid claim corrected)

- **Pure-linear** base stats per level: `level N ≈ 2,092,404 × N` HP/MP,
  `19,616 × N` P/M.ATK, `3,923 × N` P/M.DEF (max deviation 28 over 40 levels,
  confirmed by least-squares regression — essentially perfectly linear).
  L1 = 2.09M HP → L40 = 83.7M HP / 784,652 ATK (~785k rounded, not 784k) /
  157k DEF. No breakpoints.
- Structured as a **node grid**: nodes `{hp,mp}_node_R_N` exist, and material
  ids 97050/97051/97052 do gate them — but the round/rank/level-gating shape
  is **not** the simple "rounds 5–30 across ranks 2–6" previously claimed.
  The actual distinct round values are {5,10,15,...,95} (19 values, cycling
  across the rank range); ranks run 1–40 explicitly (not 2–6); cost material
  97050+97051 (2400+20) appears only on the very first rank-1/round-5 entry,
  while 97052 alone (amount scaling 1→90) is the recurring material for
  ranks 2–39; level-gating is real but partial — only levels
  {21,...,29,33} appear as gates anywhere in the table, and ranks 34–40 carry
  no `level` field at all in this extract. Caps per rank ("Max Soulfice
  reached, advance first") still applies; the exact per-round/per-rank
  mapping needs a fuller pass before it can be documented precisely.
- Higher level raises `enchant_mark_level_max` — it starts at 4 (L1–2) and
  climbs by +1 every two levels, reaching **14 by L21–22** (not "9+" as
  previously stated — that undersold it; 9 is only the value at L11–12).
  The field is absent from this table for L23–40, so the true final cap
  isn't visible in this extract.
- Auto/Quick Soulfice unlocks at Rank `rank_for_fast_levelup_unlock = 9`
  (base Soulfice itself unlocks at Rank 1, per `levelup_preview_config`).

## Hexes (法技) — the cast spells (IDs confirmed, CD/quality/rank/effects unsourced)

Each relic has 3 exclusive Hexes. Confirmed: `talisman.json`'s only
populated `skill_list` is on 78301 (`mp`/magical) = `[8510 玄渊诀, 8511
须弥仙雷, 8512 玄水神光]`. `talisman_addition_skill_pool.json` references
skill_id 8501 (逐日神剑) and 8502 (离火剑阵) directly alongside 8510–8512,
repeating the same 3-entry level:30/60/(100) pattern for each — structurally
consistent with a sibling id 8500 (纯钧斩) also existing, though 8500 itself
is never referenced directly. 78300 (physical) has no `skill_list` field at
all in `talisman.json` — the 8500–8502 physical assignment is inferred
purely from the `type:hp` + naming-symmetry pattern, not from any direct
link. No cooldown, quality, rank, or `skill_classify_type` value for any of
these 6 skill ids exists in any file in the current extraction (checked
every file in `relic-data/` for the Chinese Hex names and for a per-skill
CD/quality/rank field) — that data needs a skill-effect config that isn't
present here, or an in-game tooltip read.

Hex slots unlock at Ranks `rank_for_skill_slot_unlock = [2,5,7]` (confirmed
exactly). Two further skills, 8521 业火双刃 and 8526 两仪阵盘, exist as
`bind_skill` values on `talisman_mold.json` mold ids 1005 and 1003
respectively — i.e. they belong to the Mold system (unlocked at Rank 8, see
below), not the Hex addition pool. Neither mold entry has a `quality` field
("purple" doesn't appear anywhere in `talisman_mold.json` — only "blue" and
"orange" do), and no `rank` or cooldown field exists for either skill in any
file checked. The level-gated addition pool (L30/60/100, via
`skill_level_for_addtion_unlock = [30,60,100]`) is real and confirmed, and
only augments the base 3+3 hexes (8500–8502, 8510–8512) — 8521/8526 are not
part of it.

## Socketing — two sub-systems (counts verified, per-item details corrected)

- **Marks / Runes (符石, `talisman_marks`)**: 16 stones total (confirmed:
  ids 1001–1004, 2001–2012), two slots (`common_talisman_mark_id
  [98901, 98916]`), `mark_combine_amount = 3` stones merge to next tier,
  unlocks ("附灵"/inlay) at Rank `unlock_inlay = 3` — all confirmed exactly.
  **Correction:** "each granting 2 affixes (flat + `percent_per_10`)" only
  describes 4 of the 16 stones (赤阳石/玄阴石/离火石/震雷石, ids 1001–1004).
  The 8 "trigram" stones (坤地石 etc., ids 2001–2008) each carry **4**
  affixes instead, with mixed `percent_per_5`/`_7`/`_10`/`_15` scalers, not
  a uniform `percent_per_10`. The remaining 4 (ids 2009–2012, "特性石"/trait
  stones — 咒魂石, 封灵石, 梵音石, 神威石) have **no stat affixes at all**:
  `attrib_num:0`, and instead define an on-hit/on-attack proc effect via
  `status_para`/`status_trigger` (e.g. 咒魂石: 300s CD curse proc on attack).
  These 4 aren't HP-typed or MP-typed and don't fit the HP/MP pairing
  pattern the other 12 follow.
- **Socket treasures (附灵, `slot_treasure`)**: 8 socket bonuses confirmed
  (ids 1001–1008: 乾坤社稷图, 灵兽宝鉴, 玄光宝匣…). **Correction:** materials
  are not limited to 93001–93003, and quantities aren't ~30–50. Seven of the
  eight entries each use one distinct material id from **93001 through
  93007** (one id per socket), in quantities ranging from **20 to 200** —
  e.g. 玄光宝匣 needs 30× material 93003, 玄天造化图 needs 200× material
  93006. The eighth socket, 乾坤社稷图 (id 1001), has **no fragment/material
  requirement at all** in this data — it may unlock some other way not
  captured here.

## Mold / Forge (铸宝, `talisman_mold`) (counts verified, per-mold completeness corrected)

14 molds confirmed (ids 1003,1004,1005,1007,1008,1009,1010,1012,1014,1015,
1016,1017,1018,1019 — 两仪阵盘, 真火双刃…), star-upgradeable via
`talisman_mold_stars` (85 rows confirmed exactly: 17 mold-id groups × 5
rounds), with `skill_levelup` (1–5), escalating affixes, and level gates
(6/18/24/30). Unlocks at Rank `unlock_mold = 8` (confirmed exactly).
**Correction:** not every mold grants all three of affix + bind Hex +
appearance — 4 of the 14 (29%) are missing at least one: 1004 (真火双刃) has
`affix` but no `bind_skill` and no `outlook`; 1007 (白虎灵剑), 1012
(日芒宝锥, which has a `status_id` field instead of `affix`), and 1015
(金银双铃) each have `bind_skill`+`outlook` but no `affix`. The material ids
also aren't just "700007/700207" — 700207 *is* a universal material shared
across all 85 star rows, but the other cost id is mold-specific and ranges
across 700007–700024 (17 distinct ids, one per mold group); 700007 is only
mold 1004's own cost id, not a general one.

## Stat block & progression (mostly corrected)

- Own stat block (`talisman_config.attrib_sort`, 20 keys, confirmed exact
  order): **HP_max, MP_max** (these come *first*, not after ATK/DEF as
  previously implied), hp_attack, mp_attack, hp_defense, mp_defense,
  hp_hitrate, mp_hitrate, hp_dodge, mp_dodge, crit_chance, crit_resistance,
  pve_talisman_attack, pvp_talisman_attack, pvp_talisman_defense,
  talisman_criti_attack, talisman_criti_defense, crit_damage,
  talisman_final_attack, talisman_final_defense. **Correction:** "separate
  PvE vs PvP talisman attack/defense" overstates it — there is only **one**
  PvE field (`pve_talisman_attack`); no `pve_talisman_defense` exists
  anywhere, only PvP has both attack and defense variants. The doc also
  previously omitted a real pair, `talisman_criti_attack`/
  `talisman_criti_defense` (distinct from `crit_chance`/`crit_resistance`).
- Model/form changes at ranks `model_rank = [1,3,8,13,17]` (confirmed
  exactly). No Rank×Grade (阶×重) progression axis exists in
  `talisman_config.json` or `talisman_levels.json` — the only "重" hit in
  either file is 重铸/"recast" in `reforge_cost`'s desc, unrelated to a tier
  concept.
- Rank unlock ladder, cross-checked against `levelup_preview_config`'s own
  per-rank text plus the standalone gate fields it doesn't cover:
  - R1: gain innate stats + unlock Soulfice (matches the preview text exactly).
  - R2: can enter battle + unlock a new Hex (matches) — **and** a skill slot
    (per `rank_for_skill_slot_unlock = [2,5,7]`, which the previous "R5/R7"
    framing omitted rank 2 entirely).
  - R3: unlock inlay/socket (matches) — the preview text also notes the
    model enlarges here, which the doc previously dropped.
  - R5, R7: new inlay slot + new Hex per the preview text; also skill slots
    per `rank_for_skill_slot_unlock` above.
  - R8: preview text says only "new appearance" + "new inlay slot" — the
    Mold unlock at R8 is real but comes from the separate `unlock_mold = 8`
    field, not from R8's own preview text.
  - R9: preview text says only "new inlay slot" — it says nothing about
    Soulfice. Auto-Soulfice unlocking at R9 comes from the separate
    `rank_for_fast_levelup_unlock = 9` field, not R9's preview text.

## Open questions (need in-game observation or a fuller extraction)

- Hex CD/quality/rank/`skill_classify_type` — no skill-effect config with
  this data exists in the current extraction at all (see Hexes section);
  needs either a different config file or in-game tooltip reads.
- Exact Hex damage scales/effects beyond base `attack_scale` coefficients.
- Per-node Soulfice stat values, and a full accurate mapping of the node
  grid's round/rank/level-gate structure (19-value cycling round sequence
  across ranks 1–40, only partially level-gated — see Soulfice section).
- Whether the relic uses a Rank × Grade (阶×重) progression axis at all — no
  Grade/重 field was found anywhere in `talisman_config.json` or
  `talisman_levels.json`; this may be a UI-only concept not present in these
  tables, or may not exist as described.
- The relic's true rank ceiling and any advancement-cost table beyond what's
  visible in `levelup_preview_config` (which only goes to Rank 17).
- Monetization details (pack pricing/tiers) — needs an actual shop/store
  config; none is present in `talisman_config.json`.
- Confirm whether node/mark fills are stored once and re-expressed vs mirrored-but-
  separate on swap (no player-facing consequence given non-destructive swaps).
