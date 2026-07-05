# Breakthrough Calculator

Breakthrough timer calculator for cultivators. Qt app, ships as a Linux
AppImage. Enter your realm, cultivation speed, pills, artifacts and spirit
fruits and it tells you how long until your next phase, realm breakthrough,
or any target realm.

Settings save to a JSON next to the AppImage, so it's fully portable.
Notes on the underlying model are in `breakthrough_calc/engine.py`.

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
