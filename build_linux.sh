#!/bin/bash
echo "================================"
echo " pfSense IPsec Builder - Build"
echo "================================"

echo "[1/3] Installing dependencies..."
pip install pywebview pyinstaller --break-system-packages 2>/dev/null || pip install pywebview pyinstaller

echo "[2/3] Building binary with PyInstaller..."
python3 -m PyInstaller \
  --onefile \
  --windowed \
  --name "pfIPsec-Builder" \
  --add-data "ui:ui" \
  main.py

echo "[3/3] Done!"
echo "Output is in: dist/pfIPsec-Builder"
chmod +x dist/pfIPsec-Builder 2>/dev/null || true
