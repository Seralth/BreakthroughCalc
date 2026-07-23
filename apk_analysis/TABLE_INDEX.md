# Decompiled table schema index

Per-file lookup for `om_26062402/decompiled/*.lua` and `curio/tables/*.json` —
what each file actually contains, so you don't have to open/grep every file
to find where something lives. Complements `INDEX.md` (which maps
directories/tools); this maps individual data files to their schema.

Field names are real — these are decompiled data tables (ljd from LuaJIT
bytecode), so table keys came from named config columns, not guesses.
Manager/window files are logic, not data — their row lists key functions
instead of fields. Sizes/row counts weren't exhaustively read for large
files; entries note when only the first few records were sampled to
identify the schema.

## Combat / core calc (`om_26062402/decompiled/`)

| File | What it covers | Key fields / formulas |
|---|---|---|
| `cfg_us_calc.lua` | Flat named-constant table (~1034 entries) of global balance constants across many systems (gacha pity, combat timers, drop rates, etc.) | `value`, `name`, `desc` (zh), `is_oversea_new`, `theme_server_value`. Confirmed `combat_capacity_power = 0.98` still present. |
| `cfg_us_attrib.lua` | Per-attribute metadata (~556 entries) — every character/pet stat plus curio/troop bonus attributes used by the BR/combat-power system | `name` (zh), `seq`, `type`, `entity_group`, `show_type`, `capacity_coef`, `capacity_calc`, `scale`, `score_coef`, `ashram_type`, `show_value`, `convert`, `extra`, `hide`, `id`. Confirmed `gubao_troop_all_attribs` entry (`capacity_coef=0`, `scale=0.1`, `effect_affix_name="all_attribs"`). |
| `managers_calc_mgr.lua` | Logic, not data — `CALC_MGR` accessors over `cfg_us_calc`/`std_level_calc`/`std_sub_level_calc`, plus the BR formulas | `get_std_monster_combat_capacity` (`hp^0.98 + mp^0.98`, factor from `combat_capacity_power`), `calc_std_monster_combat_capacity` (`floor(std_capacity * hp_coef * max(hp_attack_coef, mp_attack_coef))`), `std_level_hp/mp/sd`, `std_capacity_coef(l)`, `std_yunqi_limit(l)`, `get_sub_level_num(l)`. |
| `std_level_calc.lua` | Per-character-level array (index = level) of level-up costs/curves | `level`, `hp`, `mp`, `level_hp_exp`, `level_mp_exp`, `level_hp_exp_pet`, `level_mp_exp_pet`, `yunqi_limit`, `potention`, `spirit`, `skill_max_level`, `capacity_coef`, `pet_capacity_coef`, `house_relive_time`, `loop_boss_coef`, `remote_invade_damage_coef`. |
| `std_standard_monster_calc.lua` | Per-level array of the "standard monster" reference stat block used to normalize BR | `level`, `hp`, `mp`, `hp_max`, `mp_max`, `hp_attack`, `mp_attack`, `hp_defense`, `mp_defense`, `hp_hitrate`, `mp_hitrate`, `hp_dodge`, `mp_dodge`, `crit_chance`, `crit_resistance`, `money`, `inspiration`. |
| `std_sub_level_calc.lua` | Per-level array of sub-level (breakthrough tier) exp curves | `level`, `sub_level_num`, `ceng_0`/`ceng_1`/... (per-tier `{exp_percent, need_drug_power}`). |
| `std_user_attribs.lua` | Per-level array of baseline user stat grants | `level`, `hp`, `mp`, `drug`, `attack_hp`/`mp`, `defense_hp`/`mp`, `dodge_hp`/`mp`, `hitrate_hp`/`mp`, `crit_chance`, `crit_resistance`, `hp_attack`, `mp_attack`, `hp_level_hp`/`mp`, `mp_level_hp`/`mp`, `es_attack_hp`/`mp`. |

## Equipment & affixes (`om_26062402/decompiled/`)

| File | What it covers | Key fields / formulas |
|---|---|---|
| `cfg_us_equipment.lua` | Master equipment/item catalog, keyed by `class_id` | `name` (zh), `sell_type`, `tab_type`, `level_require`, `sell_price`, `classify` (zh), `unit`, `equip_type` (weapon/cloth/fabao/etc), `wp_type`, `icon`, `quality` (blue/purple/orange), `template`, `buy_price`, `weight`, `affix_marks_template`, `attribs`, `auction_price`, `dbase` (rank), `levelup_affix_template`, `skills`. |
| `cfg_us_equip_ten_lv_affix.lua` | Per-item "ten-level" affix upgrade ladder, keyed by `[item_id][level_key]` | `memo` (zh item name); each level → `{affix_id, value}` or list of pairs. Confirmed new affix IDs 5514/5516/5517 paired at ranks 20/30/40 alongside base IDs 5503-5507@10 — matches the RE_FINDINGS 26062402 diff. |
| `cfg_us_affix.lua` | Master affix-definition table, keyed by `affix_id` (10000+) — shared lookup used by equipment, curio, and ten-lv-affix ladders | `score`, `unit`, `affix_name` (zh), `desc` (zh), `affix_type` (e.g. lingyu), `seq`, `calc` (formula tag, e.g. `lingyu_affix`), `attrib` (engine stat key), `class_id`, `inlay_type`. |
| `cfg_us_affix_mark_rank.lua` | Array indexed by quality/rank tier (0-based) of per-item-class roll-weight tables for affix-mark rolling | each tier: `{exp=mult, quality=name}` plus `item_class_id → weight` (e.g. 0.12). |
| `cfg_us_affix_rank.lua` | Array indexed by equip level+1 (0-based) of per-`affix_id` base values — the base-value side of the affix-mark formula | `affix_id → numeric base value`, scales sharply with index (0 at rank 0, thousands–tens of thousands at higher ranks). |
| `affix_mark_quality_up.lua` | Affix-mark quality-upgrade cost/gate table, keyed by mark level | `quality` (white/green/blue/purple/orange), `level`, `cost` (`{item_id,amount}` pairs), `xian_mo_cost`, `xian_mo_cost_rate`. |
| `level_equip.lua` | Equipment enhance-level ladder (index = level via `id`) | `id`, `exp` (XP to reach level), `lingwen_cost`, `equip_ashram_cost`, `equip_ashram_cost_extra` (`{item_id,amount}`), `effect` (cumulative stat %). |
| `equip_levelup.lua` | Equip "star tier" gating/cost table, small array (id 1-6) | `id`, `attrib_fix`, `equip_level_require`, `equip_levelup_cost`/`_extra`/`_base` (`{item_id,amount}`), `extra_ashram_max`, `show_effect`, `xian_mo_equip_cost_rate`. |
| `equip_suit.lua` | Realm-tier equipment set-bonus table, one entry per suit-id × piece-count tier | `id`, `name` (zh suit name, e.g. 返虚套装/大乘套装), `level_require`, `level` (piece-tier 1-4), `affix` (`{affix_id,value}` pairs), `condition` (pieces required, e.g. equip=6/9), `special` (UI flag key). |
| `equip_suit_special.lua` | Lookup for the `special` UI-flag keys referenced by `equip_suit.lua` | `id`, `desc` (zh), `pos`, `reward`, `duration`, `highlight`, `dbase`. |
| `equip_affix_suit.lua` | Separate "Xuantian" (玄天) affix-mark set-bonus table — matching N affix-marks from a shared group grants a reward; distinct system from `equip_suit.lua` | `id`, `level`, `level_require`, `name`/`suit_name` (玄天), `condition_num` (marks required), `affix` (reward pairs), `affix_groups` (affix-mark ids counted). |
| `managers_equip_mgr.lua` | Logic — runtime equip-inventory/suit-piece-counting manager | `get_suit_equipping_num` (counts equipped pieces per suit name), `get_baggage_equip_filter`, `get_equip_type`; **`calc_equip_score` is stubbed to always return 100 — not a real gear-score formula.** |
| `managers_equip_affix_mgr.lua` | Logic — affix-mark calculation manager, computes the actual equipped-affix values players see | `calc_affix_mark_val(eq_lv,data) = cfg_us_affix_rank[eq_lv+1][affix_id] * cfg_us_affix_mark_rank[mark_level][affix_id]` (base value × mark-level scale); also `calc_affix_quality`, `calc_equip_ashram_and_affix_cost`, `calc_mark_upgrade_exp`. |
| `window_equip_affix_mark.lua` | Logic/UI only — `EquipAffixMark` panel controller, no reusable formulas (delegates all math to `managers_equip_affix_mgr.lua`) | `on_create`, `redraw_levelup`, `redraw_cost_items`, `add_affix_mark_exp`. |

## Ashram (cultivation-adjacent) (`om_26062402/decompiled/`)

| File | What it covers | Key fields / formulas |
|---|---|---|
| `ashram_cfg.lua` | Cultivation-realm cosmetic names/theming per level threshold (18 stages) | `color`, `stage`, `level`, `name_hp`, `name_mp`, `period`, `describe` (per-path fa/gui/jian/ru/ti flavor text). |
| `ashram_item.lua` | Ashram (idle cultivation) economy tuning: material item IDs + per-rarity-tier speed/time/cost/unlock constants | `forge_material`, `upgrade_material`, `quality_ashram_speed_factor`, `quality_ashram_time`, `quality_upgrade_material_amount`, `upgrade_unlock_level`, `overflow_upgrade_material_convert_item`. |
| `managers_ashram_mgr.lua` | Logic — Ashram screen UI-state controller and exp/crit cycle (constant `ASHRAM_CYCLE = 8`s) | `add_ashram_exp`, `notify_ashram_cycle`, `calc_attack_change`, `load_configs` (reads `yunqi_crit`). |

## Xianshu & Lingyu progression (`om_26062402/decompiled/`)

| File | What it covers | Key fields / formulas |
|---|---|---|
| `cfg_us_xianshu_equip_star.lua` | Xianshu-gear star-upgrade ladder: per `class_id`, nested by `star_level` then `sub_level` (0-5, "阶") | `class_id`, `star_level`, `sub_level`, `star_name`, `star_point`, `cost_amount`, `affix` (`[[affix_id,value]]`), `extra_affix`. |
| `cfg_xianshu_equip_level_xianshu_equip_level_part1.lua` | Xianshu-gear per-level upgrade ladder (companion axis to the star table above) | `class_id`, `level`, `level_point`, `affix` (`[[affix_id,value]]`), `cost` (`[{class_id,amount}]`). |
| `cfg_us_lingyu_level_lingyu_level_part1.lua` | Lingyu (Spirit Jade) talent-tree-style node table: per node position, affix granted + unlock/upgrade level + cost | `id`, `node`, `affix_id`, `affix_val`, `appear_level`, `level`, `cost_item`. |
| `co_us_li_lingyu_point_affix_level_part1.lua` | Companion cost/unlock ladder for the Lingyu point system above | `point_id`, `level`, `cost` (`[{class_id,amount}]`), `unlock` (`[{floor,level,id}]`). |

## Status effects & tooltips (`om_26062402/decompiled/`)

| File | What it covers | Key fields / formulas |
|---|---|---|
| `cfg_us_status.lua` | Combat status-effect (buff/debuff) registry, keyed by status id/type | `type`, `id`, `title`, `desc`, `alias`, `attribs`, `buff_type`, `default_apply_args`, `icon`, `effect`, `clear`, `reject` (clear/reject interactions with other statuses). |
| `cfg_us_forge_speed.lua` | Flat 10,000-row lookup, single `amount` field per row (index-based) — forge-queue speed-up cost/amount per level/tier | `amount` only. |
| `cfg_us_helper_text.lua` | Long-form in-game rules/help popup text per event/feature — pure localized rich text, no formulas | `title`, `info`, `window_name`. |
| `cfg_us_helper_tip.lua` | Short stat/mechanic tooltip glossary keyed by stat/feature name — **check here first for any stat-conversion claim**; e.g. `agility`: "1 point = 3 physical hit + 3 physical dodge + 3 magic hit + 3 magic dodge" | `tip_name`, `info`. |

## UI controllers / logic managers, no data schema (`om_26062402/decompiled/`)

These are runtime logic/UI code, not config tables — listed so you know not
to grep them for row schemas, and what each one's entry points do.

| File | What it does |
|---|---|
| `window_character.lua` | Character-sheet screen controller (equip slots, HP/MP bars, skill buttons). Cost calcs delegate to `CALC_MGR` curve lookups, e.g. `calc_remove_demon_cost` uses `calc_curve("demon_recover_gold", i)`. |
| `managers_item_mgr.lua` | Inventory/item manager — icon/background path lookups by quality + `class_id`, baggage-amount queries. Key fns: `get_item_icon_path`, `get_class_id_amount`, `get_name_with_quality`, `get_item_info_bg_with_quality`. |
| `managers_skill_mgr.lua` | Skill-system manager — learn/upgrade eligibility, per-path (fa/gui/jian/ru/ti) rank tracking across human/spirit/xian tiers. Key fns: `check_can_levelup_skill`, `check_can_upgrade_skill`, `can_cost_skill_upgrade_items`; constant `MAX_RANK{human,spirit,xian}{fa,gui,ti,jian,ru}`. |
| `managers_desc_mgr.lua` | Central tooltip/description-text builder for the whole game (props, skills, pets, gubao materials). Includes `COMBAT_CAPACITY_SUB_TYPE_NAME`/`_DEFAULT_TIP` (the BR-breakdown category tooltips) and `PERCENT_ATTRIB` (which affix ids are percent vs flat). Key fns: `get_desc`, `prop_name`, `skill_name`, `get_gubao_material_desc`. |
| `gubao_levels1.lua` | **Not unrelated to curios** (its name reads like a red herring) — it's the game's lazy-load dispatcher for `cfg_us_gubao_levels`, routing curio ids to `gubao_levels_part1` (ids 91000-91412) or `part2` (ids 91413+) on demand. Same underlying data the `curio/tables/` pipeline extracts directly; this is just the module-loader stub, not the data itself. |

## Curio (gubao) tables (`curio/tables/*.json` + `curio/curio_tooltips.json`)

Schema confirmed directly from `curio/extract_curios.py`, which consumes
these — see that file for the authoritative join logic.

| File | What it covers | Key fields |
|---|---|---|
| `cfg_us_gubao.json` | Base curio rows, keyed by curio id | `name`/`desc` (zh), `quality`, `rank`, `suit_id`, `brief_desc`, `gubao_tags`. |
| `cfg_us_gubao_levels_gubao_levels_part1.json` / `_part2.json` | Per-star effect ladders, keyed by curio id (merged as one dict by `extract_curios.py`) | per star entry: `level`, `attribs` (`[[affix_id,val]]` pairs), `affix` (special-affix scalar). |
| `cfg_us_gubao_upgrade_gubao_upgrade_part1/2/3.json` | Per-upgrade ladders, keyed by curio id (merged) | per upgrade entry: `index`, `require_level`, `affix` (`[[affix_id,val]]` pairs). |
| `cfg_us_gubao_suit.json` | Curio set bonuses, keyed by suit id | per tier: `level`, `level_name`, `attribs` (`[[affix_id,val]]` pairs). |
| `cfg_us_benyuan_gubao_levels.json` | Origin-curio ("benyuan") effect ladders, keyed by curio id | `level`, `affix` (`[[affix_id,val]]` pairs), `population`. |
| `benyuan_gubao.json` | Origin-curio base info, keyed by curio id | `name` (zh), `quality`, `rank`. |
| `gubao_evol.json` | Evolved curios — small positional-array format | `[evol_id, base_id, pos, name, ?, lore, ...]`. |
| `gubao_extra.json` | Small flag-list table, **not currently consumed by `extract_curios.py`** — curio-id lists by special category | `ashram_speed_buff_gubao_ids`, `evolvable_gubao_ids`, `refinable_gubao_ids`, `rst_active_gubaos`, `temple_buff_gubao_ids`. |
| `cfg_us_affix.json` | Same affix-definition source as `om_26062402/decompiled/cfg_us_affix.lua`, extracted separately for curio use | `affix_id → {zh name, attrib key, unit}`. |
| `curio_tooltips.json` | Final joined output (5.1M) — the one file most lookups actually want | Top-level: `_generated`, `stats`, `affixes_used`, `suits`, `curios`, `origin_curios`, `evolved_curios`. Each `curios[id]`: `name_en`/`name_zh`, `quality`, `rank`, `tags`, `lore_en`/`lore_zh`, `brief_desc_en`/`_zh`, `suit_id`, `suit_name_en`/`_zh`, `star_levels` (`[{level, special_affix_add, attribs:[{affix_id,value,name_en,name_zh,attrib,unit}]}]`), `upgrades` (`[{index,require_level,affix:[...]}]`), `origin_levels` (same shape as star_levels, for Origin curios). |
