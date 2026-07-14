# BreakthroughCalc

Breakthrough-time calculator for the cultivation game OverMortal — a corrected
reimplementation of "Donk's Breakthrough calc" spreadsheet. Desktop app is
PySide6 (`breakthrough_calc/`), mobile is Flutter (`mobile/`). Core math lives
in `breakthrough_calc/engine.py`; ground-truth tests in `tests/test_engine.py`
(class `ScreenshotGroundTruth2026_07_07` pins in-game verified behavior).

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

- Pending feature: a simple donation button (desktop footer/About + mobile
  about screen) — blocked on Seralth choosing platform/URL; ask when relevant.
- RE tooling: `apk_analysis/` (see `RE_FINDINGS.md`), Il2CppDumper, ljd;
  Python venv at `.venv`.
