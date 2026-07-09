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
