# Breakthrough Calculator

A breakthrough timer for OverMortal. You enter your current Stage, cultivation
speed, and daily inputs (pills, Creation Artifacts, Respira, Myrimon Fruits), and
it returns the time to your next half-step, next Stage, or a chosen target Stage.
Available for Windows, Linux, Android, and the web.

**Use it in the browser (works on iPhone):**
<https://omvault.app/>

### Install as an app

- **iOS**: open the link in **Safari** (other browsers can't install web apps on
  iPhone), tap the **Share** button, then **Add to Home Screen** and confirm.
  You get a full-screen app icon; your inputs are kept between sessions.
- **Android**: open the link in Chrome, tap the **⋮** menu → **Add to Home
  screen** (or **Install app** when offered) and confirm. Note: Android users
  should prefer the **native APK** from the [Releases](../../releases) page — it
  performs better and checks for updates on launch (or updates automatically
  via Obtainium, see below); the web app is mainly for iPhone users, where no
  native build is possible outside the App Store.
- The web app always serves the latest release — no updates to manage.

### Automatic updates on Android (Obtainium)

The APK notifies you in-app when a new version is out, but installing it is
manual. [Obtainium](https://obtainium.imranr.dev/) automates the whole loop —
it watches this repository's releases and installs each new APK for you:

1. Install Obtainium from [obtainium.imranr.dev](https://obtainium.imranr.dev/).
2. In Obtainium, tap **Add App** and paste this repository's URL:
   `https://github.com/Seralth/BreakthroughCalc`
3. That's it — Obtainium notifies you on every new release and updates the
   app in place, keeping all your data.

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
- Myrimon Fruits: rank, gush, quality, extractor, and the gush pity (a gush is
  guaranteed within six fruits of the last one).
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
| Web / iOS | [omvault.app](https://omvault.app/) | PWA; on iPhone use Safari → Add to Home Screen. |

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

v2.7 corrected the time model against verified game mechanics:

- Pills and Respira grant flat daily EXP. The spreadsheet froze pill value as a
  speed ratio at the current grade and applied it to all future grades.
- The Aura Gem multiplies cultivation speed only; the spreadsheet also
  multiplied pill EXP by it.
- The gush guarantee is a soft pity on top of the random trigger rate: any
  gush resets the "guaranteed in x6" counter, so a gush is guaranteed within
  6 fruits of the last one, not on every literal 6th (verified in-game with a
  counted batch). The gush multiplier follows the Gush upgrade track.
- The extractor's Cultivation Bonus is 4% per level, and its +20% orb-EXP
  boosts unlock per extractor rarity rank.

The first two errors compound over long projections. Measured divergence for a
pill-heavy account (~530K daily pill/Respira EXP, Legendary gem, Incarnation):

| Projection length | Spreadsheet model | Corrected model | Optimism error |
|---|---|---|---|
| ~40 days  | 36.2d  | 39.2d  | -8%  |
| ~60 days  | ~54d   | ~60d   | -10% |
| ~180 days | 155.6d | 183.3d | -18% |
| ~350 days | 290.3d | 352.0d | -21% |

The gap scales with pill dependence: with weak pills and no gem the two models
agree, and short-range estimates match either way.

Some values are computed server-side (per-star energy recovery, exact Respira
EXP) and are entered from your own tooltips; the app indicates which.
Long-range projections remain estimates (Strive drift, crit luck — the
best/worst band covers the latter).

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
pytest                # or: python3 -m unittest discover -s tests
```

The Linux AppImage builds locally with `./build-appimage.sh`. CI builds the
Windows exe and Linux AppImage on every master push and attaches all desktop
artifacts (plus the Android APK) to tagged `v*` releases; the web app deploys
on every master push touching `mobile/` or `data/`. The Android/web app is a
separate Flutter project in `mobile/`, kept isolated from the desktop app; it
reuses the same data and a Dart port of the engine verified against the Python
one. See `mobile/README.md`.

## License

The app code is licensed under the [PolyForm Noncommercial License
1.0.0](LICENSE): free to use, read, modify, and share — selling it or putting
features behind a paywall is reserved to the author. The compiled game
information stays free: game facts belong to no one, in-game text remains the
publisher's, and this project's own prose and curation are
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Details in
[NOTICE.md](NOTICE.md).
