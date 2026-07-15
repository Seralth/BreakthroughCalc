TRACK B — ARCHITECTURE FIT: Sources Shelf design

Grounded in: `breakthrough_calc/fields.py` (FieldSpec registry), `gui.py` `_inputs()`/`_collect_state()`/`_apply_state()`, `widgets.py` (`PillEffectRows`, `make_catalog_menu`), `profiles.py`, `data_io.py` `_load_catalog`, `mobile/lib/main.dart` `_recalc`/`_afterBulkReplace`/`_formGeneration`, `input_store.dart` (atomic apply, `inputs_v1` key-set pin), `share_codec.dart` (`P`/`R` full-string convention, fresh-short-key rule), `tests/test_consistency.py` (`DataAssetList` iterates `data/*.json`), `tests/test_gui_logic.py` (Qt-less pure-logic pins), `mobile/test/widget_smoke_test.dart` (`inputsV1Keys`, "append allowed").

Key precedent that makes this fit cheap: the codebase already has the exact idiom the shelf needs — UI-layer derivation that WRITES INTO input widgets (`_toggle_respira_source` adds to `respira_per_day`, the Auto button fills `respira_exp`, `pe_rows.total()` feeds `pill_effect`). The shelf generalizes that idiom behind one registry column; it never invents a second path into the engine.

---

## 1. New modules and responsibilities

### Shared data (single source of truth)
- **`data/sources.json`** — the one catalog. Entry schema:
  ```json
  {
    "id": "book_chroma",                    // stable, wire-frozen (see §3)
    "name": "Chroma (R8 technique)",
    "category": "technique_book",           // technique_book | immortal_friend | blessing | curio | artifact | skin
    "owned_shape": {"kind": "tier", "max": 12},   // or {"kind":"level","max":150}, {"kind":"star_upgrade",...}, {"kind":"flag"}
    "effects": [
      {"target": "pill_effect_pct",   "value": 1.0, "at": 0},
      {"target": "pill_effect_pct",   "value": 3.0, "at": 6},
      {"target": "respira_attempts",  "value": 1,   "at": 3},
      {"target": "pill_attempts",     "value": 1,   "at": 12},
      {"target": "culti_speed_pct",   "value": 2.0, "at": 9}   // info-class target: breakdown only
    ]
  }
  ```
  Supersedes `pill_effect_sources.json`/`respira_sources.json` as the canonical catalog (keep the old files + loaders one release for the migration path, then delete; `DataAssetList` in `tests/test_consistency.py` auto-covers the new file's pubspec entry because it iterates `data/*.json`; `mobile/sync_data.sh` line 7 must add it).

### Desktop
- **`breakthrough_calc/shelf.py`** — pure derivation logic, NO Qt (same discipline as `fields.py`/`profiles.py`; enforced automatically because `tests/test_shelf.py` imports it under Qt-less pytest). Contents:
  ```python
  @dataclass(frozen=True)
  class TargetSpec:
      target_id: str
      kind: str            # "sum" | "flag" | "choice"
      clazz: str           # "additive" | "model" | "info"   <- double-counting classification
      field_key: str | None  # FieldSpec.key it feeds; MUST be None when clazz == "info"
      base: float = 0.0    # e.g. respira_attempts base 10

  TARGETS: dict[str, TargetSpec]   # SINGLE enumeration point for effect targets

  @dataclass(frozen=True)
  class Contribution:
      source_id: str; name: str; value: float; note: str

  @dataclass(frozen=True)
  class Derived:
      total: float; contributions: tuple[Contribution, ...]

  def derive(catalog: list, owned: dict[str, dict]) -> dict[str, Derived]
      # owned: {source_id: {"tier": 9} | {"level": 117} | {"star": 3, "upgrade": 5} | {}}
  def effective(derived: Derived | None, override: float | None) -> float
  def validate_catalog(catalog: list) -> list[str]        # schema errors, used by tests
  def migrate_legacy(pill_sources: list, respira_checked: list,
                     respira_per_day: float, catalog: list) -> tuple[dict, list, dict]
      # -> (owned, leftover_manual_pe_rows, overrides)  — see §4 invariant
  ```
- **`breakthrough_calc/shelf_ui.py`** — Qt only, no math:
  - `class ShelfPage(QWidget)`: the set-once screen (grouped by category, per-source owned controls driven by `owned_shape`; reuses `StarUpgradeDialog`'s value model via `shelf.derive`, not its own arithmetic). Signal `changed = Signal()`.
  - `class ProvenanceChip(QWidget)`: "28% · 9 books" button + override toggle + "manual" badge + reset-to-auto. Signals `override_toggled(bool)`, `breakdown_requested()`. Renders `Derived` it is handed; computes nothing.
- **`breakthrough_calc/data_io.py`**: add `load_shelf_sources() -> list` = `_load_catalog("sources.json")` (missing file → empty shelf, same fallback contract as the existing loaders).
- **`breakthrough_calc/fields.py`**: ONE new declarative column — `FieldSpec.shelf_target: Optional[str] = None`. Set on: `respira_per_day` (`respira_attempts`), `pill_limit` (`pill_attempts`), `respira_books` (`respira_effect_pct`), `bless_pp`/`bless_window` (`blessing_pp`/`blessing_window_pp`), `mark_blue/purple/gold`, and flag-kind targets for `vase`/`mirror`/`pearl`/`*_skin`. This keeps "which fields are shelf-derived" inside the registry that already owns every other per-field behavior — no parallel list.
- **`breakthrough_calc/gui.py`** grows only composition (~50 lines): a "Sources" top-level tab, a chip-install loop over `FIELDS` where `spec.shelf_target`, and `_on_shelf_changed()` (§2). Pill-effect is the registry's one existing special case and stays special: shelf contributions become read-only auto rows in `PillEffectRows` (`set_auto_rows(contributions)` — no ✕, no editable %, provenance inline), manual rows remain user-editable beneath.

### Mobile (mirrored names, per the parity-module convention in CLAUDE.md)
- **`mobile/lib/shelf.dart`** — pure Dart twin of `shelf.py` (no Flutter imports, like `engine.dart`): `targets`, `derive()`, `effective()`, `validateCatalog()`, `migrateLegacy()`, plus `ShelfState { Map<String,dynamic> owned; Map<String,double> overrides; toMap()/fromMap() }`.
- **`mobile/lib/shelf_page.dart`** — the Sources screen (4th top tab: `TabController(length: 4)`).
- **`mobile/lib/shelf_chips.dart`** — `provenanceChip(...)` + `derivedNumField(...)` wrapper that decorates the existing `numField`/`numCtrlField` from `form_widgets.dart`.
- `input_store.dart`, `share_codec.dart`, `main.dart` — small extensions (§2–3).

## 2. Derived values → existing inputs, without bypassing the registry

Rule: **the shelf writes into the same widgets/Inputs fields the user would type into; `_inputs()` and `Inputs` assembly are untouched.** The engine never learns the shelf exists.

Desktop flow:
```
sources.json ──load_shelf_sources()──> catalog
profile["shelf"] = {owned, overrides} ──┐
                                        v
ShelfPage.changed ──> MainWindow._on_shelf_changed():
    derived = shelf.derive(catalog, self._shelf_owned)
    self._loading = True                      # existing guard, no save/recalc storm
    for spec in FIELDS if spec.shelf_target:
        d = derived.get(spec.shelf_target)
        if spec.key not in overrides:         # auto mode
            widget.setValue/setChecked(shelf.effective(d, None))   # respects spec.scale
            widget.setReadOnly(True)          # auto fields aren't hand-editable
        chip[spec.key].update(d, overridden=spec.key in overrides)
    self.pe_rows.set_auto_rows(derived["pill_effect_pct"].contributions)
    self._loading = False
    self.recalc()                             # ONE recalc, existing entry point
```
- `_inputs()` (gui.py:605) reads widget values exactly as today — registry-driven assembly is preserved by construction, not by convention.
- Override toggle: chip flips `overrides[field_key]` between `None` (auto: field read-only, shelf value applied) and the current value (manual: field editable, badge shown, shelf stops writing). Reset-to-auto deletes the override and re-runs `_on_shelf_changed`. Override storage is per-field-key, next to the shelf state (§3), so a field can be overridden even when its sources are owned.
- Display-embedded inputs (`speed`, `absorb`, `respira_exp`) get NO `shelf_target` — that absence is machine-checked (§4). Their related shelf effects (`culti_speed_pct`, absorption-embedded books, `respira_effect_pct`'s display side) are `clazz="info"`/`"model"`: they appear in the chip/shelf breakdown as "already included in your displayed value" (same UX contract as today's greyed Respira menu entries), and `respira_exp` is only ever derived through the existing Auto model `stage_base × (1 + respira_books)` — the shelf feeds `respira_books`, never `respira_exp`.

Mobile flow (same shape, adapted to the initialValue-driven form):
```
ShelfPage pops / onShelfChanged():
    final derived = derive(widget.catalog, _shelf.owned);
    applyShelf(derived, _shelf.overrides, inp);   // writes inp.* for non-overridden targets
    _syncControllers();                            // controller-backed fields
    _formGeneration++;                             // existing remount mechanism re-reads inp
    _recalc();                                     // pillEffect fold now includes auto rows
```
`_recalc()` (main.dart:240) keeps deriving `inp.pillEffect` from `_peSources`; shelf auto contributions live in a separate `_peAutoRows` list rendered read-only by `peSourcesEditor` and included in the fold — manual rows keep their stable-id handling untouched.

## 3. Persistence and the OMV2 shelf key

- **Desktop**: one nested key in each profile's state dict, handled as an extra exactly like `pill_sources`/`respira_sources` in `_collect_state()`/`_apply_state()` (gui.py:632/646):
  `state["shelf"] = {"owned": {"book_chroma": {"tier": 9}, ...}, "overrides": {"respira_per_day": 14.0}}`
  Profiles are per-profile shelves (correct: alts own different things). Missing key → empty shelf → legacy migration (§4). `ProfileStore` needs zero changes.
- **Mobile**: `inputs_v1` blob gains `'shelf': shelf.toMap()` in `InputStore.blob()`; `apply()` parses it into locals before touching out-params (same atomicity contract, input_store.dart:39). `inputsV1Keys` in `widget_smoke_test.dart` gets the appended key — the pin's own comment allows appends.
- **OMV2**: new top-level structural key `'S'` (peer of `'P'`/`'R'`, not an `_F` entry — it's not an Inputs field): `{'o': {source_id: owned_params}, 'v': {long_field_key: override_value}}`. Identity is the **stable `id` string** — order-safe like `P`/`R`'s full names, and immune to display-name edits; consequence: **ids are wire data, immutable once shipped** (document in `docs/knowledge/share-code-format.md` next to the key-order contract). Old codes lack `'S'` → `_expand`'s overlay-on-defaults construction decodes them to an empty shelf for free. Import semantics: restore raw field values, then run the normal shelf-changed derivation — non-overridden fields self-heal to the receiver's catalog, overridden fields keep the sender's exact numbers. `Inputs.toMap()` is untouched, so the codec's `_fields` table and golden vector only gain the `'S'` handling.

## 4. Test surface

- **`tests/test_shelf.py`** (pure, Qt-less — sibling of `test_gui_logic.py`):
  1. `validate_catalog(load_shelf_sources()) == []` — every effect's `target` exists in `TARGETS`; ids unique; `owned_shape` well-formed.
  2. **The double-counting pin (the critical one):** assert `TARGETS[t].field_key is None` for every `clazz == "info"` target, assert every `FieldSpec.shelf_target` references a target with `clazz in ("additive", "model")`, and pin the exact classification list (attempts/limits/books%/blessing pp/marks/flags = additive; respira_effect→Auto = model; culti_speed_pct/absorption/displayed-respira-EXP = info). A wrong future edit fails loudly here.
  3. Derivation golden vectors from a shared `tests/shelf_scenarios.json` (owned-state → expected per-target totals + contribution counts).
  4. `effective()` arbitration: override wins; `None` = auto; reset restores auto.
  5. **Migration invariant:** for any legacy `(pill_sources, respira_checked, respira_per_day)`, post-migration effective field values are IDENTICAL — exact-name catalog matches become `owned`; unmatched pe rows stay manual; if `respira_per_day != base + Σ matched attempts`, the stored value is preserved as an override (badge, not silent change). Old keys keep decoding forever (`_apply_state` already tolerates unknown/missing keys); migrate-on-load, write new shape on next save.
- **`mobile/test/shelf_test.dart`**: same vectors (reads `../tests/shelf_scenarios.json` + `../data/sources.json`, same pattern as `widget_smoke_test.dart` reading `../data/`), same classification pin against `shelf.dart`'s `targets` — the two tables consuming one scenarios file is the cross-platform drift guard, mirroring the engine-parity pattern without touching it.
- **`mobile/test/share_codec_test.dart`**: golden vector gains `'S'`; pin "OMV1-era/old OMV2 code without `'S'` decodes to empty shelf"; round-trip owned + overrides.
- **`tests/test_consistency.py`**: `DataAssetList` covers `sources.json`'s pubspec entry automatically; add one test that `mobile/sync_data.sh` names every `data/*.json` it must copy (today that gap is unpinned).
- **Engine parity: NONE, by construction.** No change to `engine.py`/`engine.dart`, `Inputs` fields, or `Results`; shelf output enters as ordinary field values indistinguishable from typing. `gen_expected.py`/`parity.dart` (28 scenarios) run byte-identical. The blob/wire growth lives in UI-layer extras (`shelf` key beside `pe_sources`), not in `Inputs.toMap()`.

## 5. Quality-slide risks and how the design prevents them

1. **Logic leaking into widgets** — all arithmetic lives in `shelf.py`/`shelf.dart`; `shelf_ui.py`/`shelf_page.dart` render `Derived` objects. Enforced mechanically: `test_shelf.py` imports `shelf.py` under Qt-less pytest (import of PySide6 would fail CI), and every number the UI shows must exist in a `Contribution` (vectors pin them).
2. **Second enumeration point drift** — exactly two registries, both already-established files: `TARGETS` (shelf.py, mirrored shelf.dart, drift-pinned by shared vectors) and `FieldSpec.shelf_target` (fields.py). Chips, wiring, override storage, and persistence all iterate these; adding a shelf-fed field = 1 line in fields.py + 1 TARGETS entry + catalog data, zero code for new sources.
3. **gui.py/main.dart god-file regrowth** — they gain only composition (`_on_shelf_changed`, chip install loop, tab insertion); page and chip widgets are separate modules on both platforms.
4. **Double-counting regression** — the `clazz` field is schema, not comment; test 2 above makes "display-embedded target acquires a field_key" a CI failure, and info targets are structurally unable to feed a widget (no field_key to write to).
5. **Wire-format erosion** — shelf identity is explicit `id` strings (order-safe), `'S'` follows the fresh-key forward-compat rule already documented in share_codec.dart's header; share-code-format.md gets the `'S'` row and the id-immutability contract.
6. **Silent value changes on upgrade** — the migration invariant test (§4.5) makes "same numbers before/after" a pinned promise, with disagreements surfacing as visible overrides instead of changed results.
7. **Advisor readiness** — `derive(catalog, owned)` is pure and side-effect-free; the future advisor is a new pure module (`advisor.py`/`advisor.dart`): `rank_next(catalog, owned, inputs, engine)` clones `Inputs` per unowned source/tier-step, applies the would-be derivation through the same TARGETS mapping, and diffs `engine.calculate` Results — no new engine surface, no UI coupling.

Open item for the owner (flag as unverified game data, per the correctness-sensitive-claims rule): the base constants for derived attempt targets (Respira base 10/day is stated in the existing tooltip; the pill-limit base per rank is not currently recorded) — these belong in `sources.json`/`breakthrough.json` as data, verified from in-game tooltips before the additive derivation for `pill_limit` ships in auto mode.