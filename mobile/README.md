# Breakthrough Calculator — Mobile (Flutter)

A Flutter port for Android (sideloadable APK), kept **separate** from the Python
desktop app so the desktop builds stay lightweight. The two share only the game
data tables in `../data` — no shared code.

## Status
- **Engine: complete and verified.** `lib/engine.dart` is a 1:1 port of
  `breakthrough_calc/engine.py`, validated against the Python engine on all
  shared scenarios in `test/scenarios.json` (`dart run test/parity.dart` →
  all match to 1e-6). Covers pills, all three artifacts, respira, fruit gush
  pity, strive drop-off (both regimes), prestock, and the variance bands.
- **UI: feature-complete port** at parity with the desktop app (all inputs,
  catalogs, profiles via prefs, themes, i18n, Reference + Guide tabs, update
  check) plus mobile-only shareable build codes (`lib/share_codec.dart`,
  OMV2 format — not yet ported to desktop).

## Data
`../data` is the single source of truth. Copy it into the Flutter assets before
building or when it changes:

    ./sync_data.sh

(`assets/data/` is gitignored — it's a generated copy.)

## Validate the engine port
    ./sync_data.sh
    python3 test/gen_expected.py     # runs the Python engine -> test/expected.json
    dart run test/parity.dart        # checks the Dart engine against it

## Build / run (needs the Flutter SDK)
    ./sync_data.sh
    flutter pub get
    flutter run                      # desktop/web/emulator to preview
    flutter build apk --release      # sideloadable APK -> build/app/outputs/flutter-apk/
