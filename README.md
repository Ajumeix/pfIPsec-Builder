# pfIPsec Builder

Generate pfSense IPsec Phase 1 + Phase 2 XML configs for hub-and-spoke dual-WAN deployments — no copy-pasting, no manual XML editing.

## What it does

- **Hub + spoke topology**, dual WAN (WAN1 + WAN2) per site
- **IKEv2, PSK authentication**
- **P2 Profile** — define forwarding networks once (AWS, PROD, GCP, etc.), auto-applied to every tunnel
- **Live XML preview** as you type — see exactly what gets generated
- **One XML file per firewall** — hub gets its own, each spoke gets its own
- **Saved profiles** — save and reload P2 profiles across sessions
- **XML validation** before export — flags missing fields
- **Auto PSK generation** — generate secure random keys per spoke
- **Folder export** — exports all XMLs into a hub-named folder
- 100% local, no internet required

---

## Quick Start

### Windows

```
pip install pywebview pyinstaller
python main.py
```

### Linux (Fedora)

PyWebView requires either GTK+WebKit or Qt to render the UI.

**Option 1 — GTK (recommended on Fedora):**
```bash
sudo dnf install python3-gobject webkit2gtk4.1 gobject-introspection
pip install pywebview --break-system-packages
python3 main.py
```

**Option 2 — Qt:**
```bash
pip install pyqt6 qtpy pywebview --break-system-packages
python3 main.py
```

### Linux (Ubuntu/Debian)

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1
pip install pywebview --break-system-packages
python3 main.py
```

---

## Install to App Launcher (Linux)

Run the install script to register pfIPsec Builder in your app launcher so you can search for it:

```bash
chmod +x install_linux.sh
./install_linux.sh
```

After installing, search **"pfIPsec"** in your app launcher.

---

## Build Standalone Executable

### Windows (.exe)
```
.\build_windows.bat
```
Output: `dist\pfIPsec-Builder.exe`

> **Note:** If `pyinstaller` is not recognized, the build script uses `python -m PyInstaller` automatically.

### Linux (binary)
```bash
chmod +x build_linux.sh
./build_linux.sh
```
Output: `dist/pfIPsec-Builder`

---

## Data Storage

This app writes real files to disk next to wherever `main.py` (or the built executable) runs from:

```
pfsense-ipsec-tool/
└── data/
    ├── exports/<HubName>/         — every "Export to Folder" / "Export to data/exports/" click
    │   ├── hub-<HubName>-ipsec.xml
    │   └── spoke-<SpokeName>-ipsec.xml
    ├── profiles/<ProfileName>/    — every saved P2 profile, one folder each
    │   └── profile.json
    └── history/<timestamp>__<HubName>/  — auto-saved snapshot on every export
        ├── config.json            — full form state, reloadable via "Load & Edit"
        └── *.xml                  — the exact files generated that time
```

No file picker is needed — when running as a desktop app (PyWebView), exports, profile saves, and history snapshots are written directly to these folders. This works identically on Windows, Linux, and macOS, including environments where the browser-native folder picker isn't available (e.g. Linux WebKitGTK).

Use **Settings → Open Data Folder** to jump straight to `data/` in your file manager.

`data/` is excluded from git via `.gitignore` since it contains real pre-shared keys — only the empty folder structure (`.gitkeep` files) is tracked.

---

## How to Use

1. **Hub Firewall** — enter hub site name, WAN1/WAN2 IP or FQDN (with identifier type), interface name
2. **Phase 1 Crypto** — set encryption, hash, DH group, lifetime, DPD
3. **P2 Profile** — add forwarding networks (AWS, PROD, GCP, CCTV, etc.) — the hub's `localid` networks routed to each spoke. Save as a profile (written to `data/profiles/`) to reuse on future hubs.
4. **Spokes** — add each spoke: site name, WAN1/WAN2 IP or FQDN, interface name, PSK per WAN, and the spoke's LAN subnet
5. **Generate** — review the config table, then export (writes to `data/exports/<HubName>/` automatically, and saves a snapshot to `data/history/`)
6. **Export History** — every export is saved automatically; click "Load & Edit" on any past entry to restore the full config and re-export with changes

---

## XML Structure

### Hub (per spoke)
- 2× Phase 1 (one per hub WAN, sharing the hub's single physical interface)
- 2×N Phase 2 (N = P2 profile networks × 2 WANs)
  - `localid` = forwarding network (AWS, PROD, etc.)
  - `remoteid` = spoke's LAN subnet

### Spoke
- 2× Phase 1 (WAN1 → Hub WAN1, WAN2 → Hub WAN2, each spoke WAN can have its own interface name)
- 2×N Phase 2
  - `localid` = LAN (spoke's own subnet)
  - `remoteid` = forwarding networks from P2 profile

---

## Known Issues

### Linux — PyWebView fails to load

If you see `WebKit2 not available` or `QT cannot be loaded`:

**Fedora:**
```bash
sudo dnf install python3-gobject webkit2gtk4.1 gobject-introspection
```
Or use Qt instead:
```bash
pip install pyqt6 qtpy --break-system-packages
```

**Ubuntu/Debian:**
```bash
sudo apt install python3-gi gir1.2-webkit2-4.1
```

PyWebView requires either GTK+WebKit2 or PyQt6/PySide6 to be installed at the system level — pip alone is not enough for these GUI backends.
