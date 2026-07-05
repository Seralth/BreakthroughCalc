# Breakthrough Calculator

Desktop version of Donk's Breakthrough calc V4.1 spreadsheet. Qt app, ships as a
Linux AppImage. Enter your stage/speed/pills/artifacts/fruits and it gives you
breakthrough timers without needing Google Sheets.

The math was pulled out of the sheet and rewritten in Python (the xlsx export
was half-broken anyway). Notes on the model are in `breakthrough_calc/engine.py`.

Settings save to a JSON next to the AppImage, so it's fully portable.

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

Credits: original calculator by Donk, data compiled with help from WuMing [E83].
