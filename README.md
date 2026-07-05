# Breakthrough Calculator

A breakthrough timer for OverMortal. You enter your current Stage, cultivation
speed, and daily inputs (pills, Creation Artifacts, Respira, Myrimon Fruits), and
it returns the time to your next half-step, next Stage, or a chosen target Stage.
Available for Windows, Linux, and Android.

The app has a Reference tab that documents each mechanic and states which values
to read from the game.

## Uses

- Time to the next half-step and next Stage.
- Time to reach a specified future Stage.
- Comparing setups: pin a result, change one input, and read the difference.
- Seeing where daily XP comes from. Results are broken down by source (base,
  pills, mythic pills, Pearl, Respira, fruits).
- Accounting for dailies already spent today, via a toggle that defers them.
- Estimating the effect of the Strive catch-up bonus and its drop-off.

## What it models

Outputs:

- Time to next half-step, next Stage, or a target Stage.
- A best/worst range on each estimate, derived from Respira crit and fruit gush
  variance.
- Daily XP broken down by source.

Inputs:

- Cultivation speed from Abode Aura and Absorption Ratio (the Cultivation Bonus
  screen).
- Pills: shared daily attempt pool, pill-effect bonuses, star marks.
- Creation Artifacts: Starsea Vase, Dual-Star Mirror, Timereversal Pearl, with
  stars, skins, daily charge, and energy costs.
- Respira: daily attempts, crit average, event bonuses.
- Myrimon Fruits: rank, gush, quality, extractor, and the guaranteed gush every
  sixth fruit.
- Aura Gems.
- Strive, with server-age handling.
- A catalog of known pill-effect sources (technique books, curios) selectable
  from a list.

Other:

- Named profiles for multiple characters or setups.
- A/B comparison against a pinned result.
- Copy results to clipboard.
- Themes: Seralth (dark), Dark, Light, or system.
- Portable settings, stored next to the app.

## Download

From the [Releases](../../releases) page:

| Platform | File | Notes |
|----------|------|-------|
| Windows | `BreakthroughCalculator.exe` | Run directly. |
| Linux | `BreakthroughCalculator-x86_64.AppImage` | Mark executable, then run. |
| Android | `BreakthroughCalculator.apk` | Sideload; requires "install from unknown sources". |

The Android build is not on the Play Store. It is a sideload-only APK attached to
each release.

## Accuracy

The balance tables originate from the community spreadsheet (Donk's Breakthrough
Calc) and have been checked against the game:

- Pill EXP values confirmed from in-game tooltips across every rarity and rank.
- Creation Artifact math (energy, costs, star and skin bonuses, per-artifact
  behaviour) recovered from the decompiled client and cross-checked with live
  readings.
- Stage XP curve corrected where the spreadsheet drifted; deep-Stage values
  confirmed exact.
- Strive uses the tier tables from the game client.

Some values are computed server-side (per-star energy recovery, exact Respira
EXP) and are entered from your own tooltips; the app indicates which. The Aura
Gem is modeled as a flat speed bonus by rarity, a deliberate simplification.
Long-range projections are estimates.

The model is documented in `breakthrough_calc/engine.py`, and a test suite pins
the confirmed values.

## Building from source

Desktop:

```bash
python3 -m venv .venv
.venv/bin/pip install PySide6
.venv/bin/python main.py
```

Tests:

```bash
python3 -m unittest discover -s tests
```

The Linux AppImage builds with `./build-appimage.sh`. Windows and Android builds
run on GitHub Actions per tagged release. The Android app is a separate Flutter
project in `mobile/`, kept isolated from the desktop app; it reuses the same data
and a Dart port of the engine verified against the Python one. See
`mobile/README.md`.
