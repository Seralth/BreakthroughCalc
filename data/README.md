# data/ — canonical game-balance tables and catalogs

Single source of truth for both apps. The desktop app reads these files
directly (bundled whole into PyInstaller builds via `--add-data data:data`);
the mobile app gets a copy in `mobile/assets/data/` via `mobile/sync_data.sh`
(gitignored, regenerated before every build). The parity harness reads the
canonical copies here directly.

| File | Consumers | Notes |
| --- | --- | --- |
| `breakthrough.json` | `breakthrough_calc/engine.py`, `mobile/lib/engine.dart`, both UIs' combo boxes, `share_codec.dart` | Rows + pill/star/gem/fruit/extractor tables. **Key order is load-bearing**: OMV2 build codes store indexes into `rows`, `gem_bonus`, `pill_xp`, `fruit_xp`, `rarity_names` — reordering corrupts every shared code (pinned by `mobile/test/share_codec_test.dart`). |
| `pill_effect_sources.json` | Pill-effect catalog pickers (desktop `widgets.py`, mobile `source_pickers.dart`) | Missing file → empty picker (no error). |
| `respira_sources.json` | Respira sources pickers (both platforms) | Same fallback. Was silently missing from packaged desktop builds v2.7.1–v2.10. |
| `sources.json` | Sources Shelf derivation (`breakthrough_calc/shelf.py`, `mobile/lib/shelf.dart`) | The unified ownership catalog (books/friends/blessings/curios). Source `id` strings are wire-frozen once share codes carry the shelf — append-only, never rename (pinned by `tests/test_shelf.py`). Supersedes the two catalogs above once the shelf UI ships; they stay until legacy migration lands. |
| `i18n_glossary.json` | **Nothing at runtime — intentional.** | Curation reference of official game-term translations extracted from the APK (see `docs/knowledge/i18n-pipeline.md`). Not shipped, not loaded; both platforms' i18n tables are hand-curated with this as the source. Contains raw extraction artifacts (multi-variant zh strings, one known wrong-sense entry) — do not sync from it mechanically. |

Adding a data file? Update: `mobile/sync_data.sh`, `mobile/pubspec.yaml`
assets (pinned by `tests/test_consistency.py`), and this table. Desktop
packaging picks it up automatically (whole-directory bundle).
