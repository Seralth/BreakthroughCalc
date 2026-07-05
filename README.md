# Breakthrough Calculator

Ever wonder exactly when your next breakthrough in OverMortal is actually going
to land? That's what this is for.

You tell it where you are (your Stage, your cultivation speed, what you burn
through each day: pills, artifacts, Respira, fruits) and it works out when you'll
hit your next half-step, your next Stage, or whatever Stage you're grinding
toward. It's free, there are no ads, and it runs on Windows, Linux, and Android.

If you're brand new to it, skip down to [Download](#download) and grab it. And
don't worry if you're not sure what half the fields mean, there's a Reference tab
inside the app that walks through every mechanic and tells you what number to
pull from the game.

## What's the point

Mostly it saves you from guessing. A few things it's handy for:

- Knowing whether a breakthrough is happening tonight or realistically not for
  another week.
- Checking if an upgrade is worth it before you commit to it. Flip on a Vase
  skin, bump your pill rank, add a Respira, whatever, and watch the breakthrough
  time actually move. If it barely budges, you have your answer.
- Getting an estimate that's honest about luck. Respira crits and fruit gushes
  are random, so instead of one confident number the app gives you a
  best-and-worst range.
- Not needing a wiki open next to it. The Reference tab explains cultivation,
  pills, artifacts, Respira, fruits, and Strive, with the actual confirmed
  numbers.

## Stuff people use it for

- "When do I break through?" — next half-step and next Stage.
- "How long until I reach [some Stage]?" — set it as your target and it totals
  everything in between.
- "Is this upgrade even worth it?" — pin your current result, change one thing,
  and compare side by side.
- "Where's my XP actually coming from?" — the results split out daily XP by
  source, so you can see what's carrying you and what isn't.
- "I already did my dailies today, does that change things?" — yep, there's a
  toggle for that so the estimate reflects the rest of your day.
- "How much faster would I be if I caught up to my server's #1?" — you can model
  the Strive catch-up bonus and how it drops off as you climb.

## What it covers

Projections it gives you:

- Time to your next half-step, next Stage, or a target Stage
- A best/worst range on each one (thanks to Respira and fruit RNG)
- A per-source breakdown of your daily XP (base, pills, mythic pills, Pearl,
  Respira, fruits)

Everything it factors into your speed:

- Cultivation speed from Abode Aura and Absorption, taken right off the in-game
  Cultivation Bonus screen
- Pills, including the shared daily attempt pool, pill-effect bonuses, and star
  marks
- All three Creation Artifacts (Starsea Vase, Dual-Star Mirror, Timereversal
  Pearl) with their stars, skins, daily charge, and energy costs
- Respira: daily attempts, the crit average, and one-off event bonuses
- Myrimon Fruits, down to gush, quality, extractor, and the guaranteed gush every
  6th fruit
- Aura Gems and the Strive catch-up bonus (which behaves differently depending on
  how old your server is)
- A catalog of known pill-effect sources so you can just pick your technique books
  and curios off a list instead of chasing down every percentage yourself

Nice-to-haves:

- Multiple saved profiles, for different characters or just "what if I did this"
  setups
- Pin a result and tweak against it (A/B compare)
- Copy your results out to share them
- Four themes: Seralth (dark), plain Dark, Light, or follow your system
- Portable, your settings sit right next to the app

## Download

Everything's on the [Releases](../../releases) page.

| Platform | File | What to do with it |
|----------|------|--------------------|
| Windows | `BreakthroughCalculator.exe` | Download, double-click, done. |
| Linux | `BreakthroughCalculator-x86_64.AppImage` | Mark it executable and run it. |
| Android | `BreakthroughCalculator.apk` | Sideload it. Let your browser or file manager install from unknown sources, then open the APK. |

Heads up: the Android build isn't on the Play Store. It's a sideload-only APK
that gets attached to each release.

## Is it accurate?

Reasonably, yes, and it's been getting more accurate over time. The numbers
started life in the community spreadsheet (Donk's Breakthrough Calc) and a lot of
them have since been checked directly against the game:

- Pill EXP values were confirmed off in-game tooltips for every rarity and rank.
- The Creation Artifact math (energy, costs, star and skin bonuses, how each
  artifact behaves) was pulled out of the decompiled client and cross-checked
  against live readings.
- The Stage XP curve got corrected where the old sheet had drifted, and the
  deep-Stage values were confirmed exact.
- Strive uses the real tier tables from the game client.

A handful of values genuinely live server-side (per-star energy recovery, your
exact Respira EXP), so those you read from your own tooltips and type in. The app
tells you which ones and what to look for. The Aura Gem is treated as a flat
speed bonus by rarity, which is a simplification on purpose. And like any
calculator, the further out the projection, the more you should read it as a
ballpark rather than a promise.

If you want the gory details of how the model works, they're written up in
`breakthrough_calc/engine.py`, and there's a test suite that locks in the
confirmed numbers so nothing quietly breaks later.

## Building it yourself

Desktop app from source:

```bash
python3 -m venv .venv
.venv/bin/pip install PySide6
.venv/bin/python main.py
```

Tests:

```bash
python3 -m unittest discover -s tests
```

The Linux AppImage builds with `./build-appimage.sh`. The Windows and Android
builds happen automatically on GitHub whenever a release is tagged. The Android
version is a separate Flutter project over in `mobile/`, kept on its own so the
desktop app stays small; it reuses the same data and a Dart copy of the engine
that's checked against the Python one. There's a bit more detail in
`mobile/README.md`.
