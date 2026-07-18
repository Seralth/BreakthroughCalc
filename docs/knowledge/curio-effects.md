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
- **Discrepancy (unresolved):** client star scalar ladder is
  [0, 0.4, 0.8, 1.2, 1.6, 2.0, 3.2] over levels 0–6, while sources.json
  star_add (5 in-game stars) is [0, 0.8, 1.2, 2.2, 3.2]. Stars 2, 3, 5 match
  client levels 2, 3, 6; the in-game star-4 reading of +2.2 matches no client
  level (1.6 / 2.0 nearby). Either the star→level mapping is nonlinear, the
  client table drifted from the server, or our star-4 reading was off.
  In-game evidence wins until re-verified — sources.json stays as-is.

## Cultivation-relevant curios (max values from client ladders)

Values = max upgrade + max star scalar, units %  unless noted. Already in
the Vault catalog: Yang Spirit Jade (5.8 pill effect), Dongxuan's Pot
(2 pill effect), Pisces Pendant (accessory system, not gubao — its
"Base Abode Aura +3% in Mortal World" tooltip confirmed in i18n).

**Not yet in `data/sources.json`** (client-exact ladders in
curio_tooltips.json; treat as plausible until an in-game tooltip confirms —
see the star-4 discrepancy above):

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

## Notes

- The 5-star display vs 7 client star-levels question also affects how
  `star_upgrade` value models in sources.json should be read from
  curio_tooltips.json — map by matching values, not by index.
- Curio shards enumerate the acquirable roster: 637 "Used to combine or star
  up the Curio: X." strings in i18n vs 819 table rows (rest are unreleased /
  event/skin variants).
- The gubao suit table's tier names ("套装" / "3星套装" / "觉醒套装" =
  set / 3-star set / awakened set) imply star level 6 = awakening.
