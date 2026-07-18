# Sources Shelf — design synthesis

Owner goal: one set-once screen where the user records what they OWN
(technique books + tiers, immortal friends + levels, ascension blessing
tiers, curios, artifacts/skins); every affected input derives automatically
with a provenance chip and a manual-override escape hatch. Maximum
comprehensiveness; no post-refactor quality slide.

Companion documents (full detail):
- [sources-shelf-inventory.md](sources-shelf-inventory.md) — every known
  source and its effects, with data gaps flagged
- [sources-shelf-architecture.md](sources-shelf-architecture.md) — modules,
  data flow, test surface, quality guarantees
- [sources-shelf-schema.md](sources-shelf-schema.md) — data/sources.json
  schema, derivation semantics, OMV2 encoding, migration, validation rules

## Locked decisions

1. **Targets registry with modes** (the double-counting fix, in data):
   every effect points at a target; every target declares
   `raw_additive` (shelf may write the field: attempts, limits, books %,
   blessing pp, marks), `display_embedded` (shelf may NEVER write; feeds a
   model like Respira base × books for suggestions only — culti_speed,
   absorption_ratio, respira_exp, abode_aura, pearl_xp_per_10), or
   `informational` (breakdown-only). Machine-checked by schema tests;
   "display-embedded target acquires a field write" is a CI failure.
2. **Pure derivation twins**: `breakthrough_calc/shelf.py` ↔
   `mobile/lib/shelf.dart` (no Qt / no Flutter imports), same discipline as
   the engine pair; shared fixture JSON pins cross-platform derivation
   parity. UI modules (`shelf_ui.py` / `shelf_page.dart` + chips) render
   what derive() hands them and compute nothing.
3. **Registry integration, not a parallel path**: one new
   `FieldSpec.shelf_target` column; the shelf writes into the same widgets
   the user would type into; `_inputs()` / `Inputs` assembly and the ENGINE
   are untouched. Overrides are per-field (auto = read-only field + chip;
   manual = editable + badge + reset-to-auto).
4. **Stable string ids are wire data**: `id` fields are frozen once shipped
   (documented in share-code-format.md); OMV2 gains structural key `'S'`
   (owned + overrides), old codes decode to an empty shelf; unknown ids from
   newer catalogs are preserved and re-emitted (lossless version skew).
   Dual-emit legacy `'P'`/`'R'` for a deprecation window; `'S'` present ⇒
   authoritative.
5. **Migration = Option A (one-time, then delete legacy)**: per-source
   `legacy` alias tables map old pe_sources/respira_sources names (max-merge
   handles duplicates/overlaps); free-typed pe rows become per-target
   `custom` extras; parametric Yang Spirit Jade migrates value-exact with a
   re-select nudge. Invariant test: derived pill_effect bit-identical to the
   old sum. After one release, legacy inputs/pickers/files are removed.
6. **Unknown values never fabricate numbers**: `data_status: unknown`
   entries render as "≥ total, N sources unknown" and contribute 0 —
   doubling as the visible data-collection TODO list.
7. **Advisor-ready**: derive() is pure, so "what should I level next" is a
   later pure module diffing engine results per candidate acquisition — no
   schema or engine change needed.

## Phase plan (each phase = one PR, CI green, no half-shipped UI)

- **Phase A — foundation (no UI)**: `data/sources.json` (schema_version 1,
  content from the inventory with gaps as `data_status` markers),
  `shelf.py` + `shelf.dart` derivation twins, `tests/test_shelf.py` +
  mirrored Dart test + shared parity fixture, schema validation (14 rules in
  the schema doc, incl. legacy-totality and the banned-provenance-phrasing
  regex on notes), sync_data.sh + pubspec + DataAssetList coverage.
- **Phase B — desktop shelf**: Sources tab (ShelfPage), provenance chips on
  shelf-target fields, overrides, profiles persistence (`state["shelf"]`),
  pill-effect auto-rows in PillEffectRows, legacy migration on first load.
- **Phase C — mobile shelf**: 4th tab (shelf_page.dart), derivedNumField
  chips, input_store `shelf` key (+ widget_smoke inputsV1Keys append),
  migration on first load.
- **Phase D — share codes + sunset**: OMV2 `'S'` key + dual-emit + decode
  precedence, share-code-format.md update, golden tests; one release later:
  remove legacy catalogs/pickers/keys' encode path (decode kept forever).
- **Phase E — advisor (optional, later)**: rank unowned sources / next
  tiers by breakthrough-time delta via engine diffing.

## Data gaps — RESOLVED (2026-07-18, owner-directed)

The book tier thresholds once listed here (Golden Core, Astrology, Cosmic
Power, Taiyin Meridian, Yin's Grasp, Floral Essence, Great Yang) are on
completed books that do not display their thresholds in game — they are
unscreenshotable on this account, so the positional convention
(learn/3/6/9/12/15, validated against two known books) is the final
answer, not a pending gap. Friend payoffs are resolved from the community
guide. No catalog effect is `data_status: unknown` any more. The only
genuinely-open catalog work is NEW content (post-R9 manuals, higher
Stages) that needs a fresh in-game catalog, not a re-read of finished
content — see technique-books.md.

## Quality guarantees (how this avoids post-refactor slide)

- No logic in widgets; single enumeration points (TARGETS dict, FieldSpec
  column); pure modules importable under Qt-less pytest.
- Every schema pinned: catalog validation, id-set golden list (renames fail
  loudly), derivation parity fixture, migration bit-identity, mode-table
  structural assertions, OMV2 round-trips incl. unknown-id passengers.
- Engine parity surface: zero changes (assert: no Inputs/Results fields
  added by any phase A–D).
