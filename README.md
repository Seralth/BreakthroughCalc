# Breakthrough Calculator

Breakthrough timer calculator for cultivators. Qt app, downloadable for
Windows and Linux. Enter your Stage, cultivation speed, pills, Creation
Artifacts and Myrimon Fruits and it tells you how long until your next
half-step, Stage breakthrough, or any target Stage.

Features: named profiles (save multiple setups), A/B compare (pin one result
set and tweak against it), an optional Energy Array helper that computes your
expected Cultivation Speed, copy-to-clipboard, and portable settings.

Settings save to a JSON next to the executable, so it's fully portable.
Notes on the underlying model are in `breakthrough_calc/engine.py`.

### Where the numbers come from

The balance tables (Stage XP curve, absorption ratios, pill/fruit/artifact
values) are ported from the community-maintained spreadsheet and cross-checked
against the wiki — the game computes cultivation server-side, so those numbers
are not readable from the client. The Aura Gem is modeled as a flat speed-up by
rarity, which is a deliberate simplification of the game's aura-storage mechanic.

## Run from source

```bash
python3 -m venv .venv
.venv/bin/pip install PySide6
.venv/bin/python main.py
```

## Build the AppImage

```bash
./build-appimage.sh
```

## Windows

The Windows executable is built automatically by GitHub Actions
(`.github/workflows/build-windows.yml`) on a Windows runner. Download it from:

- **Releases** — attached to each tagged release (`v*`), or
- **Actions** — the `BreakthroughCalculator-windows` artifact on any `master` build.

Settings are stored next to the `.exe` when that folder is writable, otherwise in
`%APPDATA%\BreakthroughCalc\settings.json`.
