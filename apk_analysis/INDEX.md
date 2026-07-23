# apk_analysis/ file index

What's in this directory and where. `apk_analysis/` is entirely gitignored
except this file and `RE_FINDINGS.md` — everything else is regenerable
scratch/tool state, kept on disk for speed (~1.7G total) but not committed.

## Root

| Path | What it is |
|---|---|
| `RE_FINDINGS.md` | Dated findings log for the OverMortal RE (crypto, mechanics, version diffs). Tracked in git. Read this first for "what do we actually know." |
| `i18n_all.json` (52M) | OverMortal EN→{ru,de,es,zh} string map, 130,039 entries. Produced by the i18n pipeline (`docs/knowledge/i18n-pipeline.md`). Used by `curio/extract_curios.py` for zh→en lookups. |
| `i18n_en_ru.json` (19M) | Earlier/narrower EN→RU-only extraction pass, superseded by `i18n_all.json` for most purposes — kept around, not actively used by current scripts. |

**Removed 2026-07-23**: `apk/` (raw split APKs) and `extract_tables.py` — these
belonged to a different game entirely, **WuXia World** (`com.dustglobal.googleplay.jianghu`
v14.2.4, app label "這就是江湖" — confirmed via manifest + resources, not a
guess), leftover from separate RE work that happened to share this scratch
directory. Deleted once identified as unrelated to OverMortal.

**Removed 2026-07-23**: `om/` (the original pipeline run for version 1.4.26052702,
pulled 2026-07-05, ~1.5G) — kept only long enough to diff against the newer
pull; see `RE_FINDINGS.md`'s 2026-07-23 update for what that diff found.
Deleted once the findings were written up. `om_26062402/` (below) is now the
only version on disk.

## `om_26062402/` — OverMortal pipeline, version 1.4.26062402 (pulled 2026-07-23)

The current (and currently only) full pipeline run. Layout (same shape gets
reused for any future version pull):

| Path | What it is |
|---|---|
| `apk/` (642M) | Raw pulled split APKs: `base.apk`, `split_config.arm64_v8a.apk`, `split_init_aab.apk`, `split_lua_aab_64.apk`. |
| `ex/` (708M) | All 4 splits unzipped into one merged tree (dex, `resources.arsc`, `res/`, `assets/`, `lib/arm64-v8a/libil2cpp.so`, `assets/bin/Data/Managed/Metadata/global-metadata.dat`) — Android splits share one virtual filesystem, so merging like this is correct. |
| `dump/` (276M) | Full Il2CppDumper output: `dump.cs`, `script.json`, `stringliteral.json`, `il2cpp.h`, `DummyDll/`. Confirmed `LuaEncryption` class with XOR key `"m71"`. |
| `decrypt_lua.py` | The portable decrypt script (XOR key `"m71"` + UnityPy Unity-bundle extraction). Resolves its `ex/assets/...` inputs relative to its own file location, so it's copied alongside each version's `ex/` rather than shared. Usage: `python3 decrypt_lua.py <bundle-name> <outdir>`. |
| `allbc/` (13M, 1396 files) | Bulk decrypt of the `lua64_config_lua_us.unity3d` "umbrella" bundle — every client config Lua table for this version, as raw LuaJIT bytecode (XOR-decrypted but not decompiled). **Naming caveat**: this build's umbrella bundle dropped the `cfg_us_`/`managers_`/`window_` prefixes from its internal TextAsset names (a packaging change, not a content reorg) — when an exact old-style name is needed, pull the specific per-file bundle by name from `ex/assets/zip_lua_infos_64.json` instead (this is what was done for the curio tables and the tracked `decompiled/` set below). |
| `decompiled/` (4.7M, ~34 files) | Human-readable Lua for specific tables of interest (combat/equipment/cultivation — `cfg_us_calc`, `cfg_us_attrib`, `std_level_calc`, `managers_calc_mgr`, etc.), produced by running the matching bytecode through `ljd` (`/home/seralth/Projects/BreakthroughCalc/ljd/main.py`). Does **not** include the curio/gubao tables — those go through `curio/dump_table.lua` instead (see below), not ljd. |

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
