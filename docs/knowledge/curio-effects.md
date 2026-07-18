# Curio (gubao) tooltips & effect tables — client-side extraction

Extracted 2026-07-18 from the APK dump. Full dataset (5 MB, not committed —
bulk verbatim game text stays out of the public repo):
`apk_analysis/curio/curio_tooltips.json` + regeneration scripts in the same
directory (gitignored, lives only on the analysis machines).

**Key correction to earlier RE conclusions:** cultivation *balance* tables
(realm XP, pill XP, absorption) remain server-side, but the entire curio
system — names, lore tooltips, star/upgrade effect ladders, set bonuses — IS
shipped client-side, in `gubao_*` Lua config tables ("gubao" 古宝 = Curio).

## Where the data lives

| Table (allbc/*.luajit or umbrella bundle) | Contents |
|---|---|
| `cfg_us_gubao` | 819 curios: zh name, zh lore `desc`, quality, rank, suit_id, tags |
| `cfg_us_gubao_levels` part1/2 | per star level 0–6: `attribs` [[affix_id, value]] + `affix` scalar (adds to the upgrade affix) |
| `cfg_us_gubao_upgrade` part1–3 | per upgrade index 0–8: `affix` [[affix_id, value]], `require_level` gate |
| `cfg_us_gubao_suit` | 127 set bonuses (level 0 / 3-star / awakened tiers) |
| `benyuan_gubao` (+`cfg_us_benyuan_gubao_levels`) | 157 Origin curios (separate id space 212001+, the map-location-named ones: "Land of X", "Mount X", spiritlands) |
| `gubao_evol` | 2 evolved curios |
| `cfg_us_affix` | affix_id → zh name, engine attrib key, unit (2008 affixes; curios use 472) |

Effect ids resolve through `cfg_us_affix`; zh → EN via the i18n pipeline's
`i18n_all.json`. Coverage: 774/819 curios have EN names, 523/625 lore texts
have EN translations (the rest are new/CN-only entries).

Extraction trick: instead of decompiling, `dump_table.lua` **executes** the
LuaJIT bytecode under the system `luajit` with a stubbed auto-vivifying
`CONFIG` global, and serializes the returned table to JSON. Works for every
config table, including ones that call `CONFIG.patch_config(...)`.

## Effect model (verified against in-game readings)

A curio's active effect =
`upgrade[idx].affix value` (base, grows per upgrade) **+**
`star_levels[star].affix` scalar (grows per star; same affix).
`star_levels[].attribs` are separate flat combat stats (spell pen/block etc.).
`require_level` on upgrades is a player realm-level gate (positional
inference, not verified).

Cross-check vs `data/sources.json` (in-game verified 2026-07-07):

- **Yang Spirit Jade** (91008): upgrade ladder for affix 8624 "Cultivation
  Pill Effect Bonus" = 1.0 → 2.6 in +0.2 steps — exactly our base 1.0 /
  per_upgrade 0.2 / 8 upgrades. Star scalar tops at +3.2; 2.6 + 3.2 = 5.8 =
  our verified max. ✓
- **Dongxuan's Pot** (91115): single upgrade, 8624 = 2 — our flat +2%. ✓
- **Model fully validated (2026-07-18, 6-curio random sample across
  rarity tiers):** every reading matched the client tables exactly —
  star scalars at 0★/3★/4★/5★, percent passives additive in points
  (YSJ 1.6+1.6=3.2, Ancient Exorcism Ring 2.2+1.2=3.4), flat passives
  multiplicative (Nine Rank Lotus Throne 6,695,700 HP × 1.40 = the
  displayed 9.37M; Soulrend Blade 7 × 1.5 = the displayed 10 HP/kill).
  Stars display 0–5 then AWAKEN (= client levels 0–6; Soulrend at 5★
  shows an Awaken button); base curios start at 0★ (star params are
  0-based). "Special" curios (Spirit Seal trio) can't star or upgrade —
  modeled binary. The 12 cultivation-relevant curio effects are
  data_status exact on the strength of this sample.
- **Star mapping RESOLVED (2026-07-18 4★ tooltip):** YSJ at 4 stars +3
  upgrades shows Passive 3.2% with "Star Up Effects +1.6%" — displayed star
  N = client star level N (4★ = level 4 scalar 1.6, basic stats M.PEN 15 /
  M.Block 60 = the level-4 attribs row). The old sources.json star-4 value
  (+2.2) was wrong; the corrected model is 6 stars, star_add
  [0, 0.8, 1.2, 1.6, 2.0, 3.2] (client ladder anchored in-game at stars
  1/2/3/4 and the 5.8 max). Displayed stars = client star levels − 1 for
  the generic roster too (7 levels = 6 stars).

## Cultivation-relevant curios (max values from client ladders)

Values = max upgrade + max star scalar, units %  unless noted. Already in
the Vault catalog: Yang Spirit Jade (5.8 pill effect), Dongxuan's Pot
(2 pill effect), Pisces Pendant (accessory system, not gubao — its
"Base Abode Aura +3% in Mortal World" tooltip confirmed in i18n).

**Not yet in `data/sources.json`** as of this extraction (the 3.5 catalog
branch ships them all; client-exact ladders in curio_tooltips.json, held at
data_status community until an in-game tooltip confirms each):

| Curio | Affix (engine attrib) | Max |
|---|---|---|
| Dongxuan's Lantern | Respira EXP Bonus (`extra_exp_yunqi`) | 10 |
| Northern Mirror | Respira EXP Bonus | 8 |
| Spirit Seal Bowl | Respira EXP Bonus | 2 |
| Dongxuan's Cushion | Respira Attempts (`extra_times_yunqi`) | +1/day |
| Spirit Seal Gourd | Respira Attempts | +1/day |
| Jade of Respira | Cultivation EXP from Respira Up (`extra_base_yunqi`) | 35 |
| Auraseep Seal | Extra gains from Aura Gem (`ashram_item_extra_receive`) | 50 |
| Classic of Mountains and Seas | Abode Aura Bonus (`extra_house_energy`) | 10 |
| Energy Jade | Abode Aura Bonus | 5.8 |
| Greed Wolf Cauldron | Abode Aura Bonus | 5 |
| Spirit Seal Pearl | Abode Aura Bonus | 1 |
| Wisdom Confluence | Auxiliary Path independent cultivation rate (`second_job_ashram_rate`) | 20 |

Also client-side but out of calculator scope: Realm Spiritium bonuses
(Taiyi Seal / Skylight Wood 10, Mystical Metallic Gourd 11.6, …), pet pill
effect (Archdemon Pearl 30), Daemonfae cultivation (Integration Pendant 5),
clone exploration time (Fate Insight Compass −30), Celestial Jade / citizen
affixes on Origin curios.

## Scaling shape: linear vs breakpoints (client-ladder census 2026-07-18)

Aggregated across all 819 roster curios' client ladders (star
`special_affix_add`, star `attribs`, upgrade `affix` values, and the
`material` star-up costs in `cfg_us_gubao_levels`). Client-exact tier —
same extraction as above; the red-trio ladders below haven't had an
in-game tooltip read yet, so their displayed-star alignment inherits the
resolved YSJ mapping.

**Percent-unit passives (every cultivation-relevant affix) are linear in
upgrades; stars are linear until awakening.**

- Upgrade ladders with `%` units: 152/177 exactly constant-step (YSJ
  1.0 → 2.6 in +0.2s), 25 mildly progressive (≤3× step drift, e.g. Casual
  Whip 0.6 → 1.8). Zero exponential % ladders exist.
- Star scalar, dominant pattern (546 of 687 curios that have one): five
  equal steps then a **3× awakening step** — awakening holds a median 38%
  of the max star scalar (YSJ [0, .4, .8, 1.2, 1.6, 2, 3.2]). 126 curios
  are pure-linear instead (89% have EN names, so not just unreleased CN
  rows).
- Star flat combat attribs: 1356/1400 series are linear with a 2×
  awakening step.

**Exception — the red r4 cultivation curios have bespoke mid-loaded star
ladders; awakening adds almost nothing to their passive:**

| Curio | Client star ladder | Awaken step (share of scalar) |
|---|---|---|
| Auraseep Seal | [0, 3, 7, 16, 26, 36, 40] | +4 (10%) |
| Jade of Respira | [0, 3.5, 7, 14, 21, 26, 28] | +2 (7%) |
| Wisdom Confluence | [0, 2, 4, 8, 12, 16, 17] | +1 (6%) |

Their sweet zone is stars 2→5 (steps of +9/+10 for Auraseep vs +3/+4
early). Dongxuan's Lantern and Classic of Mountains and Seas have NO star
scalar at all — single upgrade, effect is binary on ownership; stars only
add combat attribs.

**Flat-unit combat stats (HP/ATK) are strongly super-linear in upgrades:**
467/475 ladders; the last two upgrades — realm-gated at levels 27/29
(Wholeness Early/Late) — hold a **median 74% of the max value**
(Orientation Sword 20…140, 212, 273, 710, 1065). Cultivation % curios
top out at gate 26; the 27/29 gates exist only on the 500 curios with
11-step flat ladders.

**Costs break upward faster than power.** Own-shard star-up cost roughly
doubles per star with a 3× spike at awakening (purple medians
30/60/120/180/300, then 900 + 750 any-quality shards). Marginal %-per-shard
on the standard pattern falls ~10× across the stars: YSJ 1.33%/100 shards
at 1★ → 0.13 at 5★; awakening matches 5★'s own-shard rate but adds the
large any-quality bill.

Practical read: % passives have no power breakpoint to chase — early stars
are the cheapest %s in the system and efficiency only degrades; awakening
is the single biggest power step for standard-pattern curios but the worst
shards-per-%; for the red trio above, stop at 5★ — awakening is a combat-
stat/set-bonus play only. Flat combat power is dominated by the two
final realm-gated upgrades.

## Related client-exact recoveries (2026-07-18)

- **realm_levels** (shipped in data/sources.json): exact player-level index
  per Stage from the client's `level_job` config — Novice 1, Connection
  2–11, then three per Stage (Foundation 12–14 … Voidbreak 24–26 …
  Supreme 42–44; Sublime/Cosmic Prime 45–50 pre-recorded for issue #4).
  Sub-level 1/2/3 = Early/Middle/Late. This makes the curio
  `upgrade_requires_level` ladders (gubao_upgrade `require_level`)
  realm-gateable: e.g. YSJ upgrade 8 needs level 26 = Voidbreak Late.
- **Technique-book activation requirements are server-side**: the full
  1363-asset client config bundle contains no book config at all (names
  are i18n-only). The client ships only the "Activation Requirements and
  Costs" tooltip title, the `'%s Techniques reach %s: %s'` fill-in
  template, and one baked string ("Longevity reaches Tier 2"). The R9
  gate (2× R8 books at Tier 13) is screenshot-verified; R2–R8
  requirements need an in-game activation-tooltip pass.

## Notes

- Curio shards enumerate the acquirable roster: 637 "Used to combine or star
  up the Curio: X." strings in i18n vs 819 table rows (rest are unreleased /
  event/skin variants).
- The gubao suit table's tier names ("套装" / "3星套装" / "觉醒套装" =
  set / 3-star set / awakened set) imply star level 6 = awakening.
