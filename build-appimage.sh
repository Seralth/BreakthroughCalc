#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv; .venv/bin/pip install "PySide6==6.11.1" "pyinstaller==6.21.0"; }
.venv/bin/pyinstaller --noconfirm --clean --name breakthrough-calc --windowed \
  --add-data data/breakthrough.json:data --add-data data/pill_effect_sources.json:data --add-data packaging/breakthrough-calc.png:. main.py
rm -rf packaging/AppDir
mkdir -p packaging/AppDir/usr/bin
cp -r dist/breakthrough-calc/* packaging/AppDir/usr/bin/
cp packaging/breakthrough-calc.png packaging/AppDir/
printf '%s\n' '#!/bin/sh' 'HERE="$(dirname "$(readlink -f "$0")")"' \
  'exec "$HERE/usr/bin/breakthrough-calc" "$@"' > packaging/AppDir/AppRun
chmod +x packaging/AppDir/AppRun
printf '%s\n' '[Desktop Entry]' 'Type=Application' 'Name=Breakthrough Calculator' \
  "Comment=Cultivation breakthrough timer calculator" 'Exec=breakthrough-calc' \
  'Icon=breakthrough-calc' 'Categories=Utility;Calculator;' > packaging/AppDir/breakthrough-calc.desktop
if [ ! -x packaging/appimagetool ]; then
  curl -fsSL -o packaging/appimagetool \
    https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
  chmod +x packaging/appimagetool
fi
ARCH=x86_64 packaging/appimagetool packaging/AppDir BreakthroughCalculator-x86_64.AppImage
