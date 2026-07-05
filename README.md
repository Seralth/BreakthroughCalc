# Breakthrough Calculator

**Know exactly how long your next breakthrough will take in OverMortal.**

A free, no-ads calculator for cultivators. Punch in your current Stage, your
cultivation speed, and what you use each day — pills, Creation Artifacts,
Respira, Myrimon Fruits — and it tells you when you'll hit your next half-step,
your next Stage, or any Stage you're aiming for. Runs on **Windows, Linux, and
Android**.

> New here? Jump to [Download](#download). Not sure what to enter? The app has a
> built-in **Reference** tab that explains every mechanic and what to read from
> the game.

---

## Why use it

- **Plan around real numbers, not guesses.** See your actual time-to-breakthrough
  down to the hour, so you know whether that push is happening tonight or next
  week.
- **Find out what's actually worth it.** Toggle a Vase skin, a stronger pill, an
  extra Respira, or a better fruit setup and watch the breakthrough time move.
  Compare upgrades before you spend on them.
- **Honest estimates.** Random "crit" luck (Respira crits, fruit gushes) is shown
  as a best/worst range, not a single number pretending to be certain.
- **Everything explained in-app.** A Reference tab covers how cultivation, pills,
  artifacts, Respira, fruits, and Strive work — with the confirmed numbers — so
  you don't need a wiki open on the side.

## What you can figure out with it

- *"When do I break through?"* — time to your next half-step and next Stage.
- *"How long to reach [future Stage]?"* — set a target Stage and get the total.
- *"Is this upgrade worth it?"* — pin your current result, change one thing, and
  see the difference (A/B compare).
- *"Which pills/artifacts should I prioritise?"* — the results break down XP per
  day from each source (pills, mythic pills, Pearl, Respira, fruits).
- *"What if I've already done my dailies today?"* — a toggle defers today's
  pills/Respira so the estimate reflects the rest of your day accurately.
- *"How much does catching up to my server's #1 speed me up?"* — model the Strive
  catch-up bonus and how it fades as you climb.

## Features

**Projections**
- Time to next half-step, next Stage, or any target Stage
- Best/worst range on every estimate (from Respira crit and fruit gush luck)
- Per-source XP breakdown (base, pills, mythic pills, Pearl, Respira, fruits)

**Models everything that affects your speed**
- Cultivation speed from your Abode Aura × Absorption (read straight off the
  in-game Cultivation Bonus screen)
- Cultivation pills — shared daily attempt pool, pill-effect bonuses, star marks
- Creation Artifacts — Starsea Vase, Dual-Star Mirror, Timereversal Pearl
  (stars, skins, daily charge, energy costs)
- Respira — daily attempts, crit average, event bonuses
- Myrimon Fruits — rank, gush, quality, extractor, the every-6 guaranteed gush
- Aura Gems, and the Strive catch-up bonus (with server-age handling)
- A built-in **pill-effect catalog** — pick known technique books and curios
  from a list instead of hunting down every percentage

**Quality of life**
- Save multiple **profiles** (different characters or "what-if" setups)
- **A/B compare** — pin a result and tweak against it
- **Copy results** to share
- **Themes** — Seralth (dark), Dark, Light, or match your system
- Fully **portable** — settings live next to the app

---

## Download

Grab the latest from the [**Releases**](../../releases) page:

| Platform | File | How to run |
|----------|------|-----------|
| **Windows** | `BreakthroughCalculator.exe` | Download and double-click. |
| **Linux** | `BreakthroughCalculator-x86_64.AppImage` | `chmod +x` it, then run. |
| **Android** | `BreakthroughCalculator.apk` | Sideload it — enable "install from unknown sources" for your browser/file manager, then open the APK. |

The Android app is not on the Play Store; it's a sideload-only APK attached to
each release.

---

## How accurate is it?

The balance tables started from the community-maintained spreadsheet (Donk's
Breakthrough Calc) and have since been extensively **verified against the game**:

- **Pill EXP values** confirmed from in-game tooltips across every rarity and rank.
- **Creation Artifact math** (energy, costs, star/skin bonuses, Vase/Mirror/Pearl
  behaviour) recovered from the decompiled game client and cross-checked with
  live readings.
- **Stage XP curve** corrected at the grades where the old sheet drifted; deep-Stage
  values confirmed exact.
- **Strive** uses the actual tier tables from the game client.

The game computes cultivation server-side, so a few values (per-star energy
recovery, your exact Respira EXP) are read from your own tooltips rather than
baked in — the app tells you what to read. The Aura Gem is modeled as a flat
speed-up by rarity, a deliberate simplification. Every projection is a model, so
treat long-range estimates as guidance, not gospel.

The engine's assumptions are documented in `breakthrough_calc/engine.py`, and a
regression test suite pins the confirmed numbers so they can't silently drift.

---

## For developers

**Run the desktop app from source:**

```bash
python3 -m venv .venv
.venv/bin/pip install PySide6
.venv/bin/python main.py
```

**Run the tests:**

```bash
python3 -m unittest discover -s tests
```

**Build the Linux AppImage:** `./build-appimage.sh`

**Windows and Android** builds are produced automatically by GitHub Actions on
each tagged release. The Android app is a separate Flutter project in `mobile/`
(kept isolated so the desktop app stays lightweight) that shares the same data
tables and a Dart port of the engine, verified against the Python engine — see
`mobile/README.md`.
