# Breakthrough Calculator

Standalone Qt (PySide6) desktop port of **"Donk's Breakthrough calc V4.1"**
(the Google Sheets calculator, from `~/Downloads/Copy of of Donk's Breakthrough calc V4.1.xlsx`).

The xlsx export was partially broken (several key cells were dead Google-Sheets
`DUMMYFUNCTION` stubs), so this is a clean reimplementation of the calculator's
*math*, not a cell-for-cell port. The model was recovered from the sheet
formulas and validated against the sheet's own internal "speed checker"
identity — see the docstring in `breakthrough_calc/engine.py` for the model.

## Layout

- `data/breakthrough.json` — game data extracted from the spreadsheet: the 508-row
  stage/phase/grade XP + aura table, pill XP table, gem/star/artifact tables,
  fruit level & extractor tables.
- `breakthrough_calc/engine.py` — pure-Python calculation engine (no Qt).
- `breakthrough_calc/gui.py` — PySide6 UI, live-recalculating.
- `main.py` — entry point.
- `packaging/` — icon + appimagetool + AppDir scratch.

## Run from source

```bash
.venv/bin/python main.py        # or: python3 -m venv .venv && .venv/bin/pip install PySide6
```

## Build the AppImage

```bash
./build-appimage.sh             # produces BreakthroughCalculator-x86_64.AppImage
```

Credits: original calculator by Donk; data compiled with help from WuMing [E83]
(per the spreadsheet).
