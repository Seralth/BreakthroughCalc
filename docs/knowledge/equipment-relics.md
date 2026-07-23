# Equipment relics (法宝) — full gear-system mechanics

Personal reference for **equipment relics**: the 6 class-specific/generic combat
items that occupy equipment slots and grant a skill (Literatia's inkstones/brush,
Ghostia's mask/chains/armguards, etc.). Sourced from the client APK decompile
(`apk_analysis/`); owner-confirmed corrections folded in. Noted for future
integration; not yet in the calc.

## Identity — a third distinct "relic" system

Do not confuse with either of the other two "relic" systems already documented:

- **Curios (gubao, 古宝)** — see `curio-effects.md`. Collectible artifacts with
  their own star/upgrade/suit system.
- **Zodiac Relic (本命法宝, internal `talisman`)** — see `zodiac-relic.md`. The
  single signature artifact with Soulfice/Hexes/Marks. **Equipment relics do
  NOT have Soulfice** — that mechanic is exclusive to the Zodiac Relic.
- **Equipment relics (this doc)** — `classify: 法宝` items in `cfg_us_equipment`.
  **They are gear.** They forge, level, and quality-tier on the exact same
  system as weapons/armor/accessories — not a side system.

Note: 法宝 ("fabao", magic treasure) is used as Chinese naming/flavor by *both*
equipment relics (`classify: 法宝`) and the Zodiac Relic (本命**法宝**).
**Correction (verified against source):** `attrib_tag.lua`'s "fabao" fields —
`fabao_limit` ("法宝效果上限"), `fabao_consume_defense` ("祭炼消耗降低"), and two
more the doc previously omitted, `pvp_fabao` ("修士法宝伤害加成及减免") and
`xm_fabao_damage` ("仙魔法宝伤害加成及减免") — read as **equipment-relic-specific,
not Zodiac-Relic-specific** (the opposite of what this note used to say).
`pvp_fabao`/`xm_fabao_damage` name the 修士 class system and 仙宝/魔宝 classify
types that live in `cfg_us_equipment`, and `quality.lua` (the shared 6-tier
system equipment relics use — see below) carries a `fabao_limit_scale`
coefficient per tier. None of the four fields, nor "祭炼", appear anywhere in
the `talisman*.lua` files (the Zodiac Relic's actual table family) or the
`gubao_*.lua` (curio) files.

## What they are

327 relics (`cfg_us_equipment`, `classify: 法宝`), each granting **exactly one
combat skill** (`skills: [{id: N}]`). They fill 6 of your equipment slots
alongside weapon/armor/accessory pieces and are, functionally, both gear *and*
your active-skill loadout — classes diverge mechanically through which relics
they equip, not through weapon/armor stats.

## Class sets vs generic sets (verified via `job_require`)

| Class (`tab_type`) | pieces | example names |
|---|---|---|
| Literatia (`ru`, 儒) | 砚 inkstone · 笔 brush | 青云砚/笔 → 傲月砚/笔 → 紫霄砚/笔 → 玄冥砚/笔 … |
| Ghostia (`gui`, 鬼) | 面 mask · 索 chains · 臂甲 armguards · 魂幡 soul-banner · 旗 flag | 太极灵魂幡/旗/臂甲/面/索 |
| Swordia (`jian`, 剑) | 巨剑 greatsword · 长剑 longsword | |
| Magicka (`fa`, 法) | 仪 instrument · 珠 orb | |
| Body (`ti`, 体) | 鼓 drum | |
| **Generic — physical-flavored** (`tab_type: hp`, 62 items) | 印 seal · 塔 tower · 钟 bell · 链 chain · 履 boots · 弓 bow | 风雷印/钟/塔/链 (rank 2) … |
| **Generic — magic-flavored** (`tab_type: None`, 75 items) | 幡 banner · 符 talisman · 镜 mirror · 鼎 cauldron · 葫芦 gourd · 琵琶 pipa | 青云符/镜/鼎/葫芦/仪/幡 (rank 2) … |

- Class sets carry `job_require: [class, level]` (locked to a class **and** a
  level/stage gate: 2/12/15/18/21/24…/45 — this exact list is confirmed, it's
  the full distinct set of gate levels across all 175 job-gated relics).
  Generic sets carry `job_require: null` — open to any class, same slot cost.
  **Correction:** rank range is not evenly 3–14 on both sides. `dbase.rank`
  across the 327 relics actually spans 1–14: a rank-1 tier exists (10 items,
  the non-gated "穹顶" Magicka/Body pieces below), and Ghostia's rank-2 tier
  is job-gated (`['gui', 2]`) rather than open. The two true generic groups
  (`tab_type: hp`/`None`) start at rank 3; there is no rank-1/2 generic tier.
  Also, `job_require: null` isn't exclusive to the two generic groups: 10
  more items (5 `tab_type: fa`, 5 `tab_type: ti` — rank-1 "穹顶" pieces) carry
  a class's `tab_type` but no job gate, so `tab_type` alone isn't a clean
  proxy for "which set is this."
- **Owner-confirmed: generic and class relics are peers, not a floor/ceiling.**
  Identical slots, identical forge/upgrade resource cost, identical tier
  ceiling. The only differences are (a) access — class-locked vs open — and
  (b) which skill each grants. Pick by skill fit for the build, not by a
  perceived generic-is-weaker hierarchy.
- Rank-up replaces the whole themed set with a new one carrying a new/stronger
  skill (Literatia inkstone skill ids climb 4402→4404→4406→4408… — verified
  the full 13-rank chain, it continues +2/rank through 4426 at rank 14).
- **Correction — table above is not exhaustive.** Ghostia has an undocumented
  6th piece-name: `冥渊魂铠` (rank 2, job-gated) is a "铠"/cuirass sharing the
  armguard's equip slot but a different skill — the doc's 5-piece Ghostia
  list should read 面·索·臂甲·魂幡·旗·**铠**. The generic-magic example list is
  also wrong on one entry: "青云仪" is *not* a generic piece — it's job-gated
  to Magicka (`['fa', 2]`); the real generic-magic rank-2 set is 符/镜/鼎/葫芦/幡
  (no 仪). Generic-magic also has one more unlisted piece type, 太极灵如意
  (ruyi scepter, 1 item). The 62/75 generic-item counts are correct but only
  after excluding `(已废弃)`-suffixed deprecated duplicates (65 raw hp, 77 raw
  None) — the doc's counts match the live totals, it just doesn't mention the
  exclusion.

## The shared gear system (identical for weapon/armor/accessory/relic)

Relics go through every layer below exactly like other equipment. The one
relic-specific wrinkle: **rank determines which skill you have; quality only
scales the surrounding stats/affixes, not the skill itself.**

### 1. Rank (1–14) — which item you have
Gated by player level (2/12/15/18/21/24…/45 — the same realm-gate rhythm seen
in curios and the Zodiac Relic). A rank-up is a new item (new `class_id`, new
name, new stats, and for relics a new/stronger skill) — not an upgrade of the
old one.

### 2. Level within a rank (`equip_rank`, 47 rows) — the grind curve
Steep, exponential power-vs-cost, confirmed exactly: `score` (combat power)
climbs from **120 at level 1 to 17,555,340,469 (~17.6B) at level 47**;
`equip_skill_cost` (leveling currency) climbs from **1 to 31,826,433,202
(~31.8B)**. `capacity_coef` (efficiency per point spent) *drops* as you
level, front-loaded efficiency / back-loaded cost — but the actual shape is
messier than a clean 3-step taper: **9** (levels 1–11) → **5** (12–23) →
**1.432** (24–26) → **1.828** (27–29, a bump back *up*) → **1.606** (30–32).
The field is **absent entirely for levels 33–47** (the last 15 rows carry no
`capacity_coef` key at all) — unknown whether it stops applying past level 32
or is just unlabeled in this extract.

### 3. Quality/color tier — how strong your rolls are
Universal 6-tier ladder, confirmed shared across ALL equipment
(`quality.lua`): **white → green → blue → purple → orange → red**. Core stat
multiplier `attrib_scale`: white *(none — no affixes roll)*, green 0.75,
**blue 1.0 (baseline)**, purple 1.5, orange 2.0, red 2.5. Linear from blue up
(+0.5/tier); white can't even roll bonus affixes.

Cost scales far faster than power: `price_scale` 1 → 1.8 → 4 → 10 → 20
(green→red, exactly 20× spread) vs exactly 2.5× more stats (red 2.5 ÷ blue
1.0) — each tier is worse value-per-resource than the last. `skill_cost_scale`
(cost to level the granted skill) climbs more mildly — full 6-tier
progression: white *(no field — N/A)*, green **1.0**, blue **1.2**, purple
**1.4**, orange **1.7**, red **2.0**.

Quality-up reroll odds (`relic_quality.lua`, per attempt): white→green 20%,
green→blue 20%, blue→purple 20%, purple→orange 20%, **orange→red only 10%**
— the top tier is deliberately the hardest reroll, half the rate of every
tier below it.

### 4. Forging & Blacksmith proficiency (`level_forge`) — quality is skill-gated, not just luck
A **separate player-side crafting-skill progression** (器师 "artificer," 52
levels = 4 sub-tiers × 13 rank-groups, tied 1:1 to equipment rank — confirmed:
13 rank-groups map exactly onto the 13 upgrade-transitions of the 14-rank
equipment ladder) gates which quality you're even capable of forging at your
current rank. Junior tier at a given rank can only reach blue (`target_quality:
'blue'` explicit on all 13 Junior entries); Peak (顶级) tier explicitly
unlocks orange (`target_quality: 'orange'` on all 13 Peak entries).
**Caveat:** "Intermediate/Senior raise the ceiling" is an inference, not an
explicit field — those two sub-tiers carry no `target_quality` at all, only a
boosted index in a `rate_up` array that lines up with purple by position.
Blacksmith XP requirements explode exponentially alongside gear rank,
confirmed exactly: **6** exp at rank-1-junior → **61,361,664** exp at
rank-13-peak.

### 5. Level-up "star" layer (`equip_levelup`, 6 steps) — a second enhancement track
Adds flat `attrib_fix` bonuses and **grows inlay/socket capacity**. Confirmed
gates: hard gates at **levels 21 (steps 4–5) and 42 (step 6)**, steps 1–3
ungated — this part of the doc was exactly right. **Correction:**
`extra_ashram_max` (20→30→40→50→70) only covers **steps 2–6**; step 1 has no
`extra_ashram_max` field at all (not a 0 — the key is simply absent), so
socket-capacity growth effectively spans 5 of the 6 steps, not all 6. Spent on
currency ids 62332/62333, confirmed present on steps 1/2/3/5/6 — step 4 has no
cost field in this extract either.

### 6. Marks/affixes
Each item template carries a pool (`affix_marks_template`) of rollable
bonus-stat lines, distinct from its base stats — the itemized min-max layer,
conceptually the same as the Zodiac Relic's Marks/runes.

### 7. Set bonuses — two independent, stacking systems
- **Slot-count sets** (`equip_suit`, 32 entries = 8 named sets × 4 tiers):
  **correction — 4 tiers per set, not 3.** 返虚套装 (and every other named set,
  confirmed identical pattern across all 8) actually has: level 1 `{equip: 6}`,
  level 2 `{equip: 9}`, level 3 with **no condition field at all**, and level 4
  gated by `{"affix": 27}` — an *affix-count* condition, not a further
  equip-count threshold. The 6/9-piece thresholds themselves are real and
  correctly cited.
- **Affix-collection sets** (`equip_affix_suit`, 12 entries, "Xuantian"
  玄天·装备套装效果): a separate bonus keyed to owning specific affix *groups*
  across your gear (`affix_groups` + `condition_num`), not slot count — that
  part is confirmed. **Correction — three level gates, not two:** distinct
  `level_require` values are **39, 42, and 45**, plus a fourth tier with no
  `level_require` field at all (ungated / lowest). Stacks independently of the
  slot-count sets.

### 8. Blacksmith operations (`blacksmith.lua`)
- `resolve` (熔炼, salvage/disenchant) — **explicitly capped at purple**:
  orange and red gear cannot be melted down, marking them the "keeper" tiers.
- `inlay_combine` / `inlay_remove` (灵纹融合, "spirit pattern fusion") — a
  separate socketable-rune system layered on top, filling the
  `extra_ashram_max` slots grown in layer 5.

## Practical read

"How strong is my relic" decomposes into four largely independent questions:
**rank** (which skill you have), **level** (raw power, exponential grind),
**quality** (stat multiplier, gated by blacksmith skill as much as luck), and
**marks/sets** (the min-max layer). None of these are relic-only mechanics —
mastering this system for a weapon means you already understand it for a
relic. Generic and class relics compete on equal footing for the same 6
slots and the same resources; choose by skill fit, not tier assumptions.

## Resolved (previously open questions)

- **Quality does not affect relic skill damage/effect magnitude** — confirmed
  from source, not just inferred. Across all 327 relics, `skills` and
  `quality` essentially never co-occur: of 462 *live* (non-deprecated)
  skill-bearing entries, **zero** carry a `quality` field (only 3 deprecated
  legacy rows do). Skill id increments strictly with `dbase.rank` in every
  template family checked (e.g. the 印/seal line: rank 3→skill 4037, rank
  4→4048 … rank 14→4197), never with quality. Quality is purely
  cosmetic-to-stats, as the original inference guessed.

## Open questions (need in-game observation)

- Exact `equip_recipe` forge-cost breakdown per rank/quality (table uses
  unlabeled numeric keys in this extract, confirmed no legend field exists).
  **Correction to the example:** 30,000,000 of item id 65002 ("Spiritium" —
  name not directly confirmable from this extract, but consistent with the
  term's established use elsewhere in the app) does appear in a recipe row,
  but it's a mid-tier cost, not representative of the ceiling — the same
  item id runs up to **4,000,000,000** elsewhere in the same table (row
  "无量青锋"). "Steep" undersells it.
- Full `affix_marks_template` → rollable stat pool mapping per relic. Still
  open: `equip_mark_quality_affix.json` is an empty array, and
  `affix_mark_quality_up.json` turns out to be an unrelated
  upgrade-cost/quality table (not a stat-pool mapping). Referenced template
  ids (e.g. `[7022, 7024, 7032]`) are never expanded anywhere in this extract.
