# Zodiac Relic (本命法宝) mechanics — client-side extraction

Personal reference for the **Zodiac Relic** system. **Not** part of the calc yet —
noted for future integration (Vault / combat-power). Sourced from the client APK
decompile (`apk_analysis/`) plus in-game confirmation by the owner. Verified-from-
config vs inference is flagged throughout; confident-wrong is the worst failure mode.

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

## Two types — one path, mirrored (verified)

Exactly two relics exist (`talisman.lua`):

| id | `talisman_type` | path | notes |
|---|---|---|---|
| 78300 | `hp` | **Corporia / Physical** (color #973434) | 纯钧之器; 5 sword forms 纯钧剑→金霞剑→鸿光剑→神光剑→太一剑 (the "Enlarge" model progression) |
| 78301 | `mp` | **Magicka / Magical** (color #345597) | hexes `skill_list [8510,8511,8512]` |

**The two paths are the SAME progression, mirrored** — physical vs magical only
changes which stat type the identical structure outputs:

- **Base level curve** (`std_talisman_level_calc`): a single shared table grants
  `hp` and `mp` stats **equally** at every level (L40 = 83.7M HP *and* 83.7M MP,
  784k P.ATK *and* 784k M.ATK — identical). So a physical and magical relic at the
  same level have identical base stats; the type just decides which are "active".
- **Soulfice node grid** (`talisman_levels`): `hp_node` and `mp_node` trees are
  mirror images — identical levels, ranks, rounds, node counts, and the **same
  costs on the same materials** (97050/97051/97052). Only the hp/mp label differs.
- **Hexes**: mirrored cooldowns/structure (15/20/25s), physical-damage set vs
  magical-damage set; different names/visuals, parallel mechanics.
- **Marks**: type-matched stones (HP-stones vs MP-stones), same system.

So there is no separate "physical grind" and "magical grind" — it is one
progression re-expressed as physical or magical.

## Reforge = path swap (verified + owner-confirmed)

- The "Reforge Zodiac Relic" action **is** "reselect path" (重选道路), i.e. swap
  physical↔magical. Cost `reforge_cost = 500` Fateum (机缘) or a Reforge Card/Stone
  (本命重铸石/重铸卡). Gated by a multi-hour cooldown (`forge_cd = 172800` = 48h; the
  UI also exposes a "重选道路cd，单位为小时" path-reselect CD in hours).
- **Only one type is active at a time** (owner-confirmed) — the swap changes which
  is live; both cannot run together.
- **Swapping is non-destructive** (owner-adjudicated 2026-07: the client shows no
  lost-progress/lost-item warning, and a cheap repeatable reforge with *sold*
  reforge cards would not be designed to wipe investment; consistent with every
  comparable system). The inactive type's progress is preserved but dormant.
- Practical read: the physical/magical choice is a **single active stance**, not a
  permanent commitment and not a run-both setup. You build the type you run; you
  *can* swap on the CD when path/content genuinely calls for it, without regrind.

## Soulfice (祭灵) — the stat backbone (verified)

- **Pure-linear** base stats per level: `level N ≈ 2,092,404 × N` HP/MP,
  `19,616 × N` P/M.ATK, `3,923 × N` P/M.DEF (max deviation 28 over 40 levels).
  L1 = 2.09M HP → L40 = 83.7M HP / 784k ATK / 157k DEF. No breakpoints.
- Structured as a **node grid**: nodes `{hp,mp}_node_R_N` unlocked in **rounds**
  (5/10/15/20/25/30) across **ranks 2–6**, gated by level, costing Soulfice mats
  (97050/97051/97052). Caps per rank ("Max Soulfice reached, advance first").
- Higher level raises `enchant_mark_level_max` (4→9+) = the cap on Mark levels.
- Auto/Quick Soulfice unlocks at Rank `rank_for_fast_levelup_unlock = 9`.

## Hexes (法技) — the cast spells (verified)

Each relic has **3 exclusive Hexes** (`skill_classify_type = talisman`, quality
blue, rank 6), escalating cooldowns:

| slot | Physical (type hp) | Magical (type mp) | CD |
|---|---|---|---|
| 1 | 8500 纯钧斩 | 8510 玄渊诀 | 15s |
| 2 | 8501 逐日神剑 | 8511 须弥仙雷 | 20s |
| 3 | 8502 离火剑阵 | 8512 玄水神光 | 25s |

Hex slots unlock at Ranks `rank_for_skill_slot_unlock = [2,5,7]`. More Hexes come
from Molds (`bind_skill`) and a level-gated addition pool
(`talisman_addition_skill_pool`, unlocks L30/60/100 per `skill_level_for_addtion_unlock`),
including stronger purple rank-11 assist Hexes (e.g. 8521 业火双刃, 8526 两仪阵盘, 120s CD).
*(Physical hex→relic link is inferred from `type:hp`; the direct 78300 skill_list
was truncated in the dump.)*

## Socketing — two sub-systems (verified)

- **Marks / Runes (符石, `talisman_marks`)**: 16 stones (赤阳石 HP, 玄阴石 MP,
  离火石 P.ATK…), each granting 2 affixes (flat stat + a `percent_per_10` scaler),
  leveled up to the Soulfice-gated cap; two slots (`common_talisman_mark_id
  [98901, 98916]`), `mark_combine_amount = 3` stones merge to next tier. Unlocks
  ("附灵"/inlay) at Rank `unlock_inlay = 3`.
- **Socket treasures (附灵, `slot_treasure`)**: 8 socket bonuses (乾坤社稷图,
  灵兽宝鉴, 玄光宝匣…), each unlocked by collecting ~30–50 fragments (93001/93002/93003).

## Mold / Forge (铸宝, `talisman_mold`) (verified)

14 molds (两仪阵盘, 真火双刃…), each granting affixes + a bind Hex + an appearance
(`outlook` model), star-upgradeable (`talisman_mold_stars`, 85 rows: `skill_levelup`,
more affixes, level-gated, mats 700007/700207). Unlocks at Rank `unlock_mold = 8`.

## Stat block & progression (verified)

- Own stat block (`talisman_config.attrib_sort`): P/M ATK, P/M DEF, HP, MP,
  hit/dodge, crit chance/resist, **separate PvE vs PvP talisman attack/defense**,
  crit damage, and **final attack/defense** multipliers.
- Progression = **Rank 阶 × Grade 重** (e.g. R4 G5). Model/form changes at ranks
  `model_rank = [1,3,8,13,17]`.
- Rank unlock ladder (`levelup_preview_config`): R1 gain stats + Soulfice; then
  Hex/battle (R2), inlay/socket (R3), skill slots (R5/R7), mold (R8), auto-Soulfice (R9).
- Heavily monetized: Zodiac Relic Packs I–VI, Fateum packs, ¥30–648 bundles.

## Open questions (need in-game observation)

- Exact Hex damage scales/effects beyond base `attack_scale` coefficients.
- Per-node Soulfice stat values (node grid gives structure/costs, not per-node stat).
- Rank×Grade advancement costs and the full rank ceiling.
- Confirm whether node/mark fills are stored once and re-expressed vs mirrored-but-
  separate on swap (no player-facing consequence given non-destructive swaps).
