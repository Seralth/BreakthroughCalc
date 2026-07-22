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
equipment relics (`classify: 法宝`) and the Zodiac Relic (本命**法宝**). Config
fields containing "fabao" (e.g. `attrib_tag.lua`'s `fabao_limit`,
`fabao_consume_defense`) cluster with Soulfice-cost wording and read as
Zodiac-Relic-specific, not equipment-relic-specific — don't conflate them.

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
  level/stage gate: 2/12/15/18/21/24…/45). Generic sets carry `job_require:
  null` — open to any class, same rank range (3–14), same slot cost.
- **Owner-confirmed: generic and class relics are peers, not a floor/ceiling.**
  Identical slots, identical forge/upgrade resource cost, identical tier
  ceiling. The only differences are (a) access — class-locked vs open — and
  (b) which skill each grants. Pick by skill fit for the build, not by a
  perceived generic-is-weaker hierarchy.
- Rank-up replaces the whole themed set with a new one carrying a new/stronger
  skill (Literatia inkstone skill ids climb 4402→4404→4406→4408… across ranks).

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
Steep, exponential power-vs-cost: `score` (combat power) climbs from **120 at
level 1 to ~17.5 billion at level 47**; `equip_skill_cost` (leveling currency)
climbs similarly, 1 → ~31.8 billion. `capacity_coef` (efficiency per point
spent) *drops* as you level (9 → 5 → 1.4–1.8) — front-loaded efficiency,
back-loaded cost, the same shape as curio stars and Zodiac Relic Soulfice.

### 3. Quality/color tier — how strong your rolls are
Universal 6-tier ladder, confirmed shared across ALL equipment
(`quality.lua`): **white → green → blue → purple → orange → red**. Core stat
multiplier `attrib_scale`: white *(none — no affixes roll)*, green 0.75,
**blue 1.0 (baseline)**, purple 1.5, orange 2.0, red 2.5. Linear from blue up
(+0.5/tier); white can't even roll bonus affixes.

Cost scales far faster than power: `price_scale` 1 → 1.8 → 4 → 10 → 20
(green→red, 20× spread) vs only ~2.5× more stats — each tier is worse
value-per-resource than the last. `skill_cost_scale` (cost to level the
granted skill) climbs more mildly, 1.2 → 2.0.

Quality-up reroll odds (`relic_quality.lua`, per attempt): white→green 20%,
green→blue 20%, blue→purple 20%, purple→orange 20%, **orange→red only 10%**
— the top tier is deliberately the hardest reroll, half the rate of every
tier below it.

### 4. Forging & Blacksmith proficiency (`level_forge`) — quality is skill-gated, not just luck
A **separate player-side crafting-skill progression** (器师 "artificer," 52
levels = 4 sub-tiers × 13 rank-groups, tied 1:1 to equipment rank) gates which
quality you're even capable of forging at your current rank. Junior tier at a
given rank can only reach blue; Intermediate/Senior raise the ceiling; only
Peak (顶级) tier unlocks orange-quality forges at that rank. Blacksmith XP
requirements themselves explode exponentially alongside gear rank (6 exp at
rank-1-junior → 61M+ exp at rank-13-peak).

### 5. Level-up "star" layer (`equip_levelup`, 6 steps) — a second enhancement track
Adds flat `attrib_fix` bonuses and **grows inlay/socket capacity**
(`extra_ashram_max`: 20→30→40→50→70), spent on its own currency (62332/62333).
Hard gates at **levels 21 and 42** — the same realm-breakpoint pattern as the
curio 27/29 flat-stat gates.

### 6. Marks/affixes
Each item template carries a pool (`affix_marks_template`) of rollable
bonus-stat lines, distinct from its base stats — the itemized min-max layer,
conceptually the same as the Zodiac Relic's Marks/runes.

### 7. Set bonuses — two independent, stacking systems
- **Slot-count sets** (`equip_suit`, 32 entries): 6-piece / 9-piece
  thresholds, tiered (e.g. 返虚套装 levels 1–3, condition `{equip: 6}` /
  `{equip: 9}`).
- **Affix-collection sets** (`equip_affix_suit`, 12 entries, "Xuantian" 玄天):
  a separate high-level-gated (42/45) bonus keyed to owning specific affix
  *groups* across your gear, not slot count. Stacks independently of the
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

## Open questions (need in-game observation)

- Exact `equip_recipe` forge-cost breakdown per rank/quality (table uses
  unlabeled numeric keys in this extract; currency costs confirmed steep,
  e.g. one recipe row costs 30,000,000 Spiritium).
- Whether quality affects relic skill damage/effect magnitude at all, or is
  strictly cosmetic-to-stats as inferred from rank owning the skill id.
- Full `affix_marks_template` → rollable stat pool mapping per relic.
