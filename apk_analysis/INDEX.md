# apk_analysis/ file index

What's in this directory and where. `apk_analysis/` is entirely gitignored
except this file and `RE_FINDINGS.md` — everything else is regenerable
scratch/tool state, kept on disk for speed (~3.4G total) but not committed.

## Root

| Path | What it is |
|---|---|
| `RE_FINDINGS.md` | Dated findings log for the OverMortal RE (crypto, mechanics, version diffs). Tracked in git. Read this first for "what do we actually know." |
| `i18n_all.json` (52M) | OverMortal EN→{ru,de,es,zh} string map, 130,039 entries. Produced by the i18n pipeline (`docs/knowledge/i18n-pipeline.md`). Used by `curio/extract_curios.py` for zh→en lookups. |
| `i18n_en_ru.json` (19M) | Earlier/narrower EN→RU-only extraction pass, superseded by `i18n_all.json` for most purposes — kept around, not actively used by current scripts. |
| `extract_tables.py` | **Not OverMortal.** Table-extraction script for the *other* game in `apk/` (see below) — reads `ex/assets/assets/resources/import/**/*.json` in a completely different table format. Unrelated to the Lua/UnityPy pipeline used everywhere else in this directory. |

## `apk/` — unrelated game, not OverMortal

Raw split APKs for **WuXia World** (`com.dustglobal.googleplay.jianghu` v14.2.4,
app label "這就是江湖" — confirmed via manifest + resources, not a guess).
This is leftover from separate RE work on a different game that happens to
share this scratch directory. `extract_tables.py` at the root targets this
game's asset format. Safe to ignore for anything OverMortal-related.

## `om/` — OverMortal pipeline, version 1.4.26052702 (pulled 2026-07-05)

The original full pipeline run. Layout (same shape reused for every version):

| Path | What it is |
|---|---|
| `apk/` (639M) | Raw pulled split APKs: `base.apk`, `split_config.arm64_v8a.apk`, `split_init_aab.apk`, `split_lua_aab_64.apk`. |
| `ex/` (558M) | All 4 splits unzipped into one merged tree (dex, `resources.arsc`, `res/`, `assets/`, `lib/arm64-v8a/libil2cpp.so`, `assets/bin/Data/Managed/Metadata/global-metadata.dat`) — Android splits share one virtual filesystem, so merging like this is correct. |
| `dump/` | **Empty** — the Il2CppDumper `dump.cs` for this version wasn't retained after the initial crypto analysis. (Contrast with `om_26062402/dump/`, which has it.) |
| `decrypt_lua.py` | The portable decrypt script (XOR key `"m71"` + UnityPy Unity-bundle extraction). Resolves its `ex/assets/...` inputs relative to its own file location, so it's copied alongside each version's `ex/` rather than shared. Usage: `python3 decrypt_lua.py <bundle-name> <outdir>`. |
| `allbc/` (200M, 661 files) | Bulk decrypt of the `lua64_config_lua_us.unity3d` "umbrella" bundle — every client config Lua table for this version, as raw LuaJIT bytecode (`.luajit`/`.lua`, XOR-decrypted but not decompiled). |
| `decrypted/` (65M, 8 files) | One-off targeted decrypts, not the bulk dump: `drug_speed.lua` + `i18n_0..6.lua` (the i18n language tables — see `docs/knowledge/i18n-pipeline.md`). |
| `decompiled/` (5.1M, 41 files) | Human-readable Lua for specific tables of interest (combat/equipment/cultivation — `cfg_us_calc`, `cfg_us_attrib`, `std_level_calc`, `managers_calc_mgr`, etc.), produced by running the matching `allbc/` bytecode through `ljd` (`/home/seralth/Projects/BreakthroughCalc/ljd/main.py`). Does **not** include the curio/gubao tables — those go through `curio/dump_table.lua` instead (see below), not ljd. |

## `om_26062402/` — OverMortal pipeline, version 1.4.26062402 (pulled 2026-07-23)

Same layout as `om/`, for the newer client (device `lastUpdateTime` 2026-07-10).
Old baseline in `om/` was left untouched for diffing.

| Path | What it is |
|---|---|
| `apk/` (642M), `ex/` (708M), `decrypt_lua.py` | Same roles as in `om/`. |
| `dump/` (276M) | Full Il2CppDumper output for this version: `dump.cs`, `script.json`, `stringliteral.json`, `il2cpp.h`, `DummyDll/`. Confirmed `LuaEncryption`/`"m71"` unchanged from the old version. |
| `allbc/` (13M, 1396 files) | Bulk decrypt of the umbrella bundle. **Naming caveat**: in this build the umbrella bundle's internal names dropped the `cfg_us_`/`managers_`/`window_` prefixes (packaging change, not a content reorg), so filenames here don't line up 1:1 with `om/allbc/` — cross-reference by content/size, or pull the specific per-file bundle by its old name from `ex/assets/zip_lua_infos_64.json` when an exact match is needed (this is what was done for the curio tables and the tracked `decompiled/` set). |
| `decompiled/` (4.7M, ~34 files) | Same known-table set as `om/decompiled/`, ljd-decompiled from this version for diffing. See `RE_FINDINGS.md`'s 2026-07-23 update for the content diff results. |

## `curio/` — Curio (gubao) tooltip extraction

Standalone tool, not tied to a single version — `tables/` and `curio_tooltips.json`
represent whatever version was last extracted (currently 26062402; regenerating
overwrites in place, see `curio/README.md`).

| Path | What it is |
|---|---|
| `README.md` | Regeneration steps. |
| `dump_table.lua` | Runs under system `luajit`; executes a LuaJIT bytecode chunk with a stubbed `CONFIG` global and serializes whatever table it returns straight to JSON — no ljd decompile needed for these data-only tables. |
| `extract_curios.py` | Joins `tables/*.json` (gubao base/levels/upgrade/suit, benyuan origin, evolved, affix names) + `../i18n_all.json` → `curio_tooltips.json`. Has a hardcoded `APK` path to this repo checkout. |
| `tables/` (12 files) | Intermediate per-table JSON, produced by `dump_table.lua` from the relevant `allbc/`-or-individual-bundle bytecode of whichever version was last regenerated from. |
| `curio_tooltips.json` (5.1M) | Final joined output: 819 curios, 157 origin curios, 2 evolved, 127 suits, 472 distinct affixes. As of 2026-07-23 this is byte-identical between 26052702 and 26062402 — the curio system didn't change in this update. |
| `cultivation_slice.py` | **Stale** — hardcodes a path into a since-deleted session's job tmp dir (`/home/seralth/.claude/jobs/5cf8b056/tmp/curio_tooltips.json`). One-off analysis script (filters `curio_tooltips.json` for cultivation-adjacent affixes); would need its `open(...)` path repointed at `curio/curio_tooltips.json` to rerun. |

## Related tracked docs (outside `apk_analysis/`)

- `docs/knowledge/i18n-pipeline.md` — how `i18n_all.json` was built.
- `docs/knowledge/curio-effects.md` — curio findings write-up (consumes `curio_tooltips.json`).
- `docs/knowledge/combat-mechanics.md`, `docs/knowledge/game-mechanics-verified.md` — mechanics findings sourced partly from this RE pipeline.
