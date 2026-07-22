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
  `update_banner.dart`, `theme.dart`, `i18n.dart`, `vault_tab.dart` (Vault
  UI twin of desktop shelf_ui.py; shelf state in the 'shelf_v1' prefs blob).
- The Vault (desktop: top-level tab; mobile: full-screen page opened from
  the Calculator's summary card / app-bar book icon — NOT a top tab, it
  feeds the calculator) is the unified ownership home:
  Library (technique books on R1–R9 rank shelves, Universal/Exclusive),
  Treasury (curios), Companions (immortal friends + blessings + base
  values). ALL catalog sources live ONLY in data/sources.json; the
  Reference "sources" tables render from it too. The legacy
  pill_effect_sources.json / respira_sources.json are retained solely as
  migration-test fixtures (not shipped, no UI pickers — those were
  removed 2026-07-16); old user rows migrate via legacy[] aliases.
- Gates (all must stay green; CI runs them on every push via
  `.github/workflows/ci.yml`): `pytest` from the repo root; `cd mobile &&
  flutter analyze && flutter test`; parity `python test/gen_expected.py &&
  dart run test/parity.dart` (every `Results` field, 28 scenarios). Engine
  changes must land in BOTH engines + regenerate expected.json; data-table
  KEY ORDER is part of the OMV2 wire format (pinned by share_codec_test).
- Known duplication that is NOT engine-parity: translations (i18n.py vs
  i18n.dart) and Reference/Guide prose (docs.py vs reference_tab/
  guide_tab.dart) are hand-maintained twice — unification is a planned
  follow-up; keep edits mirrored manually until then. The translation
  drift is now ratcheted: `test_i18n.py::CrossPlatformDrift` fails if a
  key shared by both files disagrees beyond the 80 pairs grandfathered in
  `tests/i18n_drift_baseline.json`. Those 80 need a human language-QA pass
  (automated reconciliation degrades quality — the game glossary carries
  wrong homonyms and each platform holds some better game-term matches);
  fixing a pair means removing it from the baseline.

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
- `docs/knowledge/technique-books.md` — ALL Universal technique books R1–R9
  with full chapter/tier bonus tables (2026-07-15 screenshot pass); which
  thresholds are exact vs positional inference. The Vault's Library renders
  these from data/sources.json (categories technique_book + exclusive_book).
- `docs/knowledge/combat-mechanics.md` — verified combat/gear stat mechanics
  (crit/hit/pen/block/control constants from cfg_us_calc.lua) + community
  affix tier-list cross-check; kept separate from cultivation knowledge
- `docs/knowledge/elixir-sense-mechanics.md` — elixir tolerance ladders, pill
  taxonomy (3 distinct "pill" meanings), alchemy, Sense stat; has OPEN
  QUESTIONS — check before writing reference sections
- `docs/knowledge/curio-effects.md` — curio (gubao) tooltips + star/upgrade
  effect ladders ARE client-side (unlike balance tables); extraction pipeline
  (apk_analysis/curio/), verified effect model, Vault catalog gap list
- `docs/knowledge/zodiac-relic.md` — Zodiac Relic (本命法宝, internal `talisman_*`)
  system: two mirrored physical/magical paths, linear Soulfice scaling, Hexes,
  socketing, mold/forge, non-destructive path-swap reforge. Distinct from the
  Zodiac Pot curio. Noted for future integration; not yet in the calc
- `docs/knowledge/equipment-relics.md` — equipment relics (法宝): the 6 class/
  generic combat-skill items, on the SAME gear system as weapons/armor (rank,
  level curve, quality tiers, blacksmith-gated forging, marks, dual set
  bonuses). Distinct from curios and the Zodiac Relic. Not yet in the calc
- `docs/knowledge/i18n-pipeline.md` — extracting official en/ru/de/es/zh
  strings from the APK dump; curated glossary at `data/i18n_glossary.json`

## User-facing text style (enforced by owner, 2026-07-15)

- NO provenance/verification phrasing in anything the user sees — catalog
  notes, Reference/Guide prose, tooltips, hints, result labels. Banned:
  "screenshot-verified", "confirmed from game data", "verified in-game",
  dates like 2026-07-15, "(2026 community guide)", "from the dump /
  decompiled client". Verification history belongs in docs/knowledge/ and
  code comments only. The app states facts plainly.
- Opinion-vs-fact distinctions ARE kept, in product language: "subjective" /
  "exact" / "recommended" — not "community consensus" vs "verified".
- NO data-status markers in the UI at all (no "*" on entries, no
  exact/community badges, no "not exactly established" tooltips). The
  customer uses a product, not a dev log. data_status stays in the data
  files, docs/knowledge/, and code comments only. (Owner, 2026-07-16,
  after a "*" shipped on Vault book rows.)

## Release checklist (owner rule, 2026-07-16)

- Bump versions WITH each user-facing change set, not just at tag time:
  `breakthrough_calc/__init__.__version__`, `mobile/pubspec.yaml` version
  (increment the +build number too), `mobile/lib/main.dart` appVersion.
  tests/test_consistency.py pins all three together.
- **Releases are automatic on version bumps** (2026-07-17): pushing master
  with a bumped `__version__` makes the Build and Build Android workflows
  create the `v<version>` tag + GitHub release themselves (auto-generated
  notes) and attach the Windows exe, Linux AppImage, and Android APK.
  Manual `v*` tags still work; master pushes without a bump build
  artifacts only and skip the release. Why this matters: installed
  desktop/Android apps poll GitHub releases for updates — before this,
  web had reached 2.18 while releases/latest sat at v2.10 and installed
  apps reported "up to date" the whole time. Polish notes afterwards with
  `gh release edit v<version> --notes`.
- Deploy latency: push → ~4 min build/deploy → up to 10 min GitHub Pages
  CDN cache (max-age=600, headers not configurable). Inside that window
  even a correct Force refresh serves the previous build — check
  `curl -s https://omvault.app/version.json` before debugging "stuck"
  updates.

## Working notes

- Android release signing (2026-07-17): CI signs the APK from
  ANDROID_KEYSTORE_BASE64 / ANDROID_KEYSTORE_PASSWORD / ANDROID_KEY_PASSWORD
  repo secrets (key alias `omvault`); tag builds FAIL without them so a
  debug-signed APK can never ship again (pre-2.19 releases were each signed
  by a throwaway CI debug key — first signed update needs uninstall/
  reinstall). Keystore: `~/keystores/omvault-release.jks` on both machines,
  NEVER in this public repo. Local release builds read
  `mobile/android/key.properties` (see key.properties.example).
- Donation button (done, desktop + mobile): SEAGM in-game voucher gifting —
  URL and recipient ID in `breakthrough_calc/__init__.py` (no URL prefill
  supported by SEAGM, so instructions include the RID for manual entry).
- RE tooling: `apk_analysis/` (see `RE_FINDINGS.md`), Il2CppDumper, ljd;
  Python venv at `.venv`.
