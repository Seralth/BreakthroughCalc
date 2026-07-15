# BreakthroughCalc

Breakthrough-time calculator for the cultivation game OverMortal — a corrected
reimplementation of "Donk's Breakthrough calc" spreadsheet. Desktop app is
PySide6 (`breakthrough_calc/`), mobile is Flutter (`mobile/`). Core math lives
in `breakthrough_calc/engine.py`; ground-truth tests in `tests/test_engine.py`
(class `ScreenshotGroundTruth2026_07_07` pins in-game verified behavior).

## Architecture (2026-07-15 refactor)

The two apps are deliberately parallel; module layouts mirror each other.
- Desktop: `engine.py` (math; parity twin of `engine.dart`), `data_io.py`
  (frozen-app paths + loaders), `gui.py` (thin MainWindow), `fields.py`
  (declarative input-field registry: widget/persistence/Inputs/tooltip in ONE
  place), `docs.py` (all Reference/Guide HTML; no Qt), `widgets.py`,
  `labels.py`, `profiles.py`, `update_check.py`, `theme.py`, `i18n.py`.
- Mobile: `engine.dart`, `main.dart` (thin coordinator), `form_widgets.dart`,
  `results_card.dart` + `absorption_diag.dart`, `reference_tab.dart` /
  `guide_tab.dart` / `doc_nav.dart` / `doc_widgets.dart`, `share_codec.dart`
  (OMV2 build codes — wire format doc: `docs/knowledge/share-code-format.md`),
  `input_store.dart`, `source_pickers.dart`, `app_dialogs.dart`,
  `update_banner.dart`, `theme.dart`, `i18n.dart`.
- Gates (all must stay green; CI runs them on every push via
  `.github/workflows/ci.yml`): `pytest` from the repo root; `cd mobile &&
  flutter analyze && flutter test`; parity `python test/gen_expected.py &&
  dart run test/parity.dart` (every `Results` field, 28 scenarios). Engine
  changes must land in BOTH engines + regenerate expected.json; data-table
  KEY ORDER is part of the OMV2 wire format (pinned by share_codec_test).
- Known duplication that is NOT engine-parity: translations (i18n.py vs
  i18n.dart, drifted) and Reference/Guide prose (docs.py vs reference_tab/
  guide_tab.dart) are hand-maintained twice — unification is a planned
  follow-up; keep edits mirrored manually until then.

## Critical mechanics rules (violating these = wrong math)

- **Pills/Respira are FLAT daily XP**, not multipliers. Aura Gem multiplies
  cultivation speed ONLY (never pills/Respira). Per-row rate =
  `speed(row)×(1+gem)/8s + daily_xp/86400`. Donk's `time/(1+gem)/(1+pills)`
  was wrong on both counts.
- **Gush pity is SOFT**: any gush (random or guaranteed) resets the ×6
  counter. Engine models it as a 6-state Markov recursion. `gush_xp` is keyed
  by the GUSH track level (not Culti level).
- **Fruit ranks R4/R5 do not exist** — the `fruit_xp` gap (R3, R6–R12) is
  intentional (ranks map to realm bands). Never flag as missing data.
- **Balance tables are server-side**, not in the client APK dump. Sources of
  truth are in-game tooltips/screenshots, not the dump.
- Full detail: `docs/knowledge/game-mechanics-verified.md`

## Knowledge index

- `docs/knowledge/game-mechanics-verified.md` — verified pill/gem/gush/orb/
  extractor semantics (2026-07-07 screenshots)
- `docs/knowledge/combat-mechanics.md` — verified combat/gear stat mechanics
  (crit/hit/pen/block/control constants from cfg_us_calc.lua) + community
  affix tier-list cross-check; kept separate from cultivation knowledge
- `docs/knowledge/elixir-sense-mechanics.md` — elixir tolerance ladders, pill
  taxonomy (3 distinct "pill" meanings), alchemy, Sense stat; has OPEN
  QUESTIONS — check before writing reference sections
- `docs/knowledge/i18n-pipeline.md` — extracting official en/ru/de/es/zh
  strings from the APK dump; curated glossary at `data/i18n_glossary.json`

## Working notes

- Donation button (done, desktop + mobile): SEAGM in-game voucher gifting —
  URL and recipient ID in `breakthrough_calc/__init__.py` (no URL prefill
  supported by SEAGM, so instructions include the RID for manual entry).
- RE tooling: `apk_analysis/` (see `RE_FINDINGS.md`), Il2CppDumper, ljd;
  Python venv at `.venv`.
