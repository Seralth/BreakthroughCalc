# OverMortal RE findings (game = com.ltgames.android.m71.us, Unity IL2CPP + tolua)

## Engine
- Unity IL2CPP (libil2cpp.so 109MB) + tolua (libtolua.so). Game logic & data = Lua.
- global-metadata.dat: version 31, magic 0xFAB11BAF, NOT scrambled (pglarmor left it intact).
- Il2CppDumper works cleanly → dump.cs (1.08M lines).

## Crypto classes (from dump.cs)
- LuaEncryption (KEY="m71"): repeating-key XOR. CONFIRMED via disasm of Decrypt @ RVA 0x2E691A0:
    plaintext[i] = cipher[i] XOR "m71"[i % 3]
  → decrypts all Lua bytes files.
- PCAssetsEncryption (KEY="ad83dd97d41dab676398e19612098a47c6e18a1d"): used for assets/config/*.json
  (bootstrap config only — 1KB, channel/SDK/server list, NOT cultivation tables). Non-standard AES
  derivation; NOT yet cracked. Low priority (not the game data).
- XOREncryption (key param): generic repeating-XOR helper.

## Where the DATA is
- Cultivation tables (pill XP, absorption ratios, artifacts, fruits) = Lua tables inside
  the .lua.bytes TextAssets, packed in Unity AssetBundles (.unity3d) in split_lua_aab_64.apk /
  assetpack/lua_package_64.asset.

## Monday plan (est ~2-4h)
1. Extract .unity3d AssetBundles with UnityPy → pull each .lua.bytes TextAsset (encrypted).
2. XOR-decrypt each with "m71" → Lua bytecode (luac) or source.
3. If bytecode: decompile with unluac/luajit-decompiler → readable Lua config tables.
4. Grep for the cultivation/pill/absorption/fruit tables; diff vs Donk's numbers.

## RESULT (extraction complete)
Pipeline fully working: decrypt (XOR "m71") → strip 12-byte prefix → UnityFS bundle →
UnityPy TextAsset → LuaJIT bytecode (\x1bLJ\x02) → ljd decompiler → readable Lua.
All 661 client config Lua files decrypted & decompilable (proof: drug_speed, level_job).

**BUT the cultivation BALANCE tables are NOT in the client — they are server-authoritative:**
- Realm XP curve (e.g. Eternal cum 1,050,668,882): 0 client files.
- Pill-rank XP (7,312,500 / 1,540,500): 0 client files.
- Absorption ratios (0.275, 0.208, 0.5, 0.8 ...): 0 client files (searched as IEEE-754 doubles).
- Fruit base XP (65000/800000): only coincidental hits in reward/item tables, not a fruit-XP table.

Client Lua DOES contain: UI, logic, localization text, and some client tables
(drug_speed = {amount, speed} 10k rows; level_job weights) — but not the progression numbers.

**Conclusion:** OverMortal computes cultivation server-side; the APK cannot independently
verify Donk's balance numbers. This is exactly why the community relies on a datamined sheet.
Donk's sheet (already cross-checked against the wiki to float precision) remains the
authoritative source. No calculator changes warranted from the APK — terminology polish
(Cosmoapsis / Absorption ratio / half-steps) already applied stands as the net gain.

## UPDATE 2026-07-09: std tables ARE shipped (combat/BR excavation)

The earlier conclusion that std_level_calc.xlsx & friends are server-only was WRONG for
the client-side copies: the umbrella bundle `lua64_config_lua_us.unity3d` (1363 TextAssets,
extracted via decrypt_lua.py's pipeline against the whole-bundle entry rather than
per-file bundles) contains `std_level_calc.lua`, `std_standard_monster_calc.lua`,
`std_user_attribs.lua`, `std_sub_level_calc.lua`, `std_base_level_attribs.lua`, etc.
Decompiled copies live in `om/decompiled/`.

Key recoveries:
- **Respira attempts/day** (`yunqi_limit` in std_level_calc): 2 at level 1, default 10
  thereafter — the base-attempts input the Respira model needed readings for.
- **Per-level `capacity_coef`** ladder (66,080 at levels 12-14 up to ~231e9 by level 47+,
  stepping every 3 levels ≈ per grade tier, roughly ×5-8 per step): the realm "standard"
  used to normalize flat stats (crit/hit/dodge) and score BR.
- **Standard monster BR** (managers_calc_mgr.lua): floor((hp_std^0.98 + mp_std^0.98) ×
  hp_mult × max(hp_atk_mult, mp_atk_mult)), combat_capacity_power = 0.98 (cfg_us_calc).
- **Character BR** is server-computed; client holds per-stat weights (`capacity_coef` in
  cfg_us_attrib: hp/mp_max 3000, attack 280k, defense 600k, etc.) and the breakdown
  category structure (managers_desc_mgr COMBAT_CAPACITY_SUB_TYPE_*), but only displays
  the server total. Weight direction (× vs ÷) unverified in client code.
- Combat/gear findings (stat conversions, ten-lv affixes, carvings, suits, resonance):
  see the calculator's Reference → Combat & Gear / Advanced tabs, sourced from
  cfg_us_attrib / cfg_us_equipment / cfg_us_equip_ten_lv_affix / cfg_us_helper_tip /
  equip_suit / level_equip (all in om/decompiled/).

## UPDATE 2026-07-18: curio (gubao) tooltips & effect ladders ARE client-side

Second correction to the "nothing useful in the client" conclusion: the whole
Curio system ships in the client config Lua. `cfg_us_gubao` (819 curios: zh
names + lore descs), `cfg_us_gubao_levels`/`_upgrade` (per-star and
per-upgrade effect ladders as [[affix_id, value]] pairs), `cfg_us_gubao_suit`
(127 set bonuses), `benyuan_gubao` (+levels; 157 Origin curios), `gubao_evol`
(2 evolved). Affix ids resolve via `cfg_us_affix` (zh name + engine attrib +
unit); zh→EN via the i18n tables.

Cross-checked against in-game-verified data: Yang Spirit Jade upgrade ladder
1.0→2.6 (+0.2/step, affix 8624 extra_exp_ashram_drug) + star scalar max 3.2
= 5.8 max — exactly the sources.json values. One open discrepancy at star 4
(client 1.6/2.0 vs in-game 2.2 reading).

Extraction: `apk_analysis/curio/` (dump_table.lua executes bytecode under
system luajit with a stubbed CONFIG, no decompile needed; extract_curios.py
joins + localizes → curio_tooltips.json). Full writeup:
docs/knowledge/curio-effects.md.

## UPDATE 2026-07-23: version 1.4.26062402 pulled & diffed (was 1.4.26052702)

Re-ran the full pipeline against the newer client (`versionCode 26062402`,
device `lastUpdateTime` 2026-07-10, pulled 2026-07-23) into
`apk_analysis/om_26062402/`, old baseline in `apk_analysis/om/` untouched
for comparison.

- **Crypto CONFIRMED unchanged**: new `dump.cs` still has
  `LuaEncryption` with `KEY = "m71"`, same class/method shape. XOR decrypt
  verified working on this version (LuaJIT magic `\x1bLJ\x02` on sampled
  output files).
- **Individual per-file Lua bundle catalog is nearly identical** (818→820
  entries; only +5/-3 changed, all cosmetic or new minor features — gang
  boss manager, bug-report-v2, a new `gubao_troop` UI controls script, one
  reward-table shard added, one dialogue shard renamed). The earlier scare
  of "everything got renamed" was a red herring from decrypting the
  `lua64_config_lua_us.unity3d` umbrella bundle specifically: its internal
  TextAsset names dropped the `cfg_us_`/`managers_`/`window_` prefixes in
  this build (a packaging change, not a content reorg) — the individual
  per-file bundles (`lua64_managers_calc_mgr.lua.bytes.unity3d` etc.) still
  resolve fine by the old names and were used to backfill the diff.
- **Combat BR formula (`managers_calc_mgr.lua`) is UNCHANGED** except one
  new trivial helper (`is_positive_num`) — the standard-monster BR formula
  and `combat_capacity_power = 0.98` from the 2026-07-09 update still hold.
- **New curio attribute type**: `cfg_us_attrib` gained
  `gubao_troop_all_attribs` (`scale = 0.1`, `capacity_calc =
  "special_percent"`, `effect_affix_name = "all_attribs"`) — an all-stats
  %-boost curio-troop attribute that didn't exist in 26052702. Not yet
  cross-checked against in-game data; flag if a curio troop tooltip shows
  an all-stat % this doesn't explain.
- **Ten-lv equipment affix ladder extended**: `cfg_us_equip_ten_lv_affix`
  gained new affix-id entries (5514–5517) at ranks 20/30/40, purely
  additive (existing entries unchanged).
- `cfg_us_equipment` grew ~700 lines (new gear item IDs, e.g. 7082–7084)
  — routine catalog growth, not a mechanics change.
- Curio (gubao) bundle set is unchanged (same `cfg_us_gubao*`/
  `benyuan_gubao*`/`gubao_evol`/`gubao_upgrade` bundles present; only
  `gubao_upgrade_part4` dropped, likely consolidated into part3 — not
  content-diffed this pass) — the existing `apk_analysis/curio/` JSON
  pipeline should still work unmodified if re-run against this version.
  Not regenerated this pass (out of scope — decompiled/diffed the
  previously-tracked `om/decompiled/` file set only, not the curio JSON
  extraction).
- No changes found in `cfg_us_affix`/`_rank`/`_mark_rank`,
  `cfg_us_helper_text`/`_tip`, `cfg_us_status`, `managers_desc_mgr`,
  `managers_equip_mgr`/`_item_mgr`/`_skill_mgr`/`_equip_affix_mgr`, or
  `window_character`/`_equip_affix_mark` beyond additive new entries
  (new items/affixes/strings) — no formula or weight changes detected.

**Net effect for the calculator: no math changes required.** The one
open item worth watching is the new `gubao_troop_all_attribs` curio
attribute — worth a quick in-game screenshot check if a troop curio
tooltip shows an unexplained all-stat percentage.
