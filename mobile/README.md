# Breakthrough Calculator — Mobile (Flutter)

A Flutter port for Android (sideloadable APK), kept **separate** from the Python
desktop app so the desktop builds stay lightweight. The two share only the game
data tables in `../data` — no shared code.

## Status
- **Engine: complete and verified.** `lib/engine.dart` is a 1:1 port of
  `breakthrough_calc/engine.py`, validated against the Python engine on 12
  shared scenarios (`dart run test/parity.dart` → all match to 1e-6). Covers
  pills, all three artifacts, respira, fruit gush pity, strive drop-off (both
  regimes), and the variance bands.
- **UI: starter foundation.** `lib/main.dart` wires the core cultivation inputs
  and headline results to the engine. Remaining UI work: pills, artifacts,
  respira, fruit, star-mark inputs, the pill-effect catalog picker, profiles,
  the theme selector, and the Reference tab (all straightforward — the engine
  and data already provide everything).

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
