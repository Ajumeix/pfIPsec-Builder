#!/bin/bash
echo "================================"
echo " pfIPsec Builder - Linux Install"
echo "================================"

INSTALL_DIR="$HOME/.local/share/pfIPsec-Builder"
DESKTOP_DIR="$HOME/.local/share/applications"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/4] Installing Python dependencies..."
pip install pywebview --break-system-packages 2>/dev/null || pip install pywebview

echo "[2/4] Copying app files to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/ui" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/api.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/icon.ico" "$INSTALL_DIR/" 2>/dev/null || true
mkdir -p "$INSTALL_DIR/data/exports" "$INSTALL_DIR/data/profiles" "$INSTALL_DIR/data/history"

echo "[3/4] Creating launcher script..."
cat > "$INSTALL_DIR/launch.sh" << LAUNCH
#!/bin/bash
cd "$INSTALL_DIR"
python3 main.py
LAUNCH
chmod +x "$INSTALL_DIR/launch.sh"

echo "[4/4] Creating desktop entry (app search)..."
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/pfipsec-builder.desktop" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=pfIPsec Builder
Comment=pfSense IPsec Bulk Config Generator
Exec=bash $INSTALL_DIR/launch.sh
Icon=$INSTALL_DIR/icon.ico
Terminal=false
Categories=Network;System;
Keywords=pfsense;ipsec;vpn;firewall;network;
StartupNotify=true
DESKTOP

chmod +x "$DESKTOP_DIR/pfipsec-builder.desktop"
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo ""
echo "✓ Installed to $INSTALL_DIR"
echo "✓ App entry created — search 'pfIPsec' in your app launcher"
echo "✓ Data (exports, profiles, history) saved to: $INSTALL_DIR/data/"
echo ""
echo "To run manually:"
echo "  python3 $INSTALL_DIR/main.py"
echo "  or: bash $INSTALL_DIR/launch.sh"
