@echo off
echo ================================
echo  pfSense IPsec Builder - Build
echo ================================

echo [1/3] Installing dependencies...
pip install -r requirements.txt

echo [2/3] Building .exe with PyInstaller...
python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "pfIPsec-Builder" ^
  --add-data "ui;ui" ^
  --icon "icon.ico" ^
  main.py

echo [3/3] Done!
echo Output is in: dist\pfIPsec-Builder.exe
pause
