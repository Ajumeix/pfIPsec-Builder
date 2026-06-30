import os
import sys
import json
import shutil
import subprocess
from datetime import datetime


def app_base_dir():
    """Base directory the app runs from — works for dev and PyInstaller bundle.
    Data is stored NEXT TO the executable/script, not bundled inside _MEIPASS,
    so it persists across rebuilds and isn't read-only."""
    if hasattr(sys, '_MEIPASS'):
        # Running as a PyInstaller bundle — use the folder containing the exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    """Get path to bundled read-only resources (ui/ files)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


BASE_DIR = app_base_dir()
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPORTS_DIR = os.path.join(DATA_DIR, 'exports')
PROFILES_DIR = os.path.join(DATA_DIR, 'profiles')
HISTORY_DIR = os.path.join(DATA_DIR, 'history')


def ensure_dirs():
    for d in (DATA_DIR, EXPORTS_DIR, PROFILES_DIR, HISTORY_DIR):
        os.makedirs(d, exist_ok=True)


def safe_name(name):
    """Sanitize a string for use as a filename/folder name."""
    if not name:
        return 'unnamed'
    keep = '-_. '
    cleaned = ''.join(c if c.isalnum() or c in keep else '-' for c in str(name))
    cleaned = cleaned.strip().replace(' ', '-')
    while '--' in cleaned:
        cleaned = cleaned.replace('--', '-')
    return cleaned[:80] or 'unnamed'


class API:
    """Exposed to JS as window.pywebview.api.<method>()"""

    def __init__(self):
        ensure_dirs()

    # ── Paths info ──────────────────────────────────────────
    def get_data_paths(self):
        return {
            'base': BASE_DIR,
            'data': DATA_DIR,
            'exports': EXPORTS_DIR,
            'profiles': PROFILES_DIR,
            'history': HISTORY_DIR,
        }

    # ── Exports (folder-per-hub, written to disk every export) ──
    def export_to_disk(self, hub_name, files):
        """
        files: list of {filename: str, content: str}
        Writes to data/exports/<hub_name>/<filename>
        """
        try:
            ensure_dirs()
            folder = os.path.join(EXPORTS_DIR, safe_name(hub_name))
            os.makedirs(folder, exist_ok=True)
            written = []
            for f in files:
                fpath = os.path.join(folder, safe_name(f['filename']))
                # filenames already include extension; safe_name strips none of that since dots are kept
                fpath = os.path.join(folder, f['filename'])
                with open(fpath, 'w', encoding='utf-8') as fh:
                    fh.write(f['content'])
                written.append(fpath)
            return {'ok': True, 'folder': folder, 'files': written}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def open_path(self, path):
        """Open any specific folder in the OS file manager."""
        try:
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', path], check=False)
            else:
                subprocess.run(['xdg-open', path], check=False)
            return {'ok': True}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    # ── History (dated snapshot folder + the XML files generated) ──
    def save_history_entry(self, entry):
        """
        entry: { id, name, savedAt, spokeCount, p2Count, config: {...}, files: [{filename, content}] }
        Writes:
          data/history/<timestamp>__<name>/config.json
          data/history/<timestamp>__<name>/<xml files...>
        """
        try:
            ensure_dirs()
            ts = datetime.now().strftime('%Y%m%d-%H%M%S')
            folder_name = f"{ts}__{safe_name(entry.get('name',''))}"
            folder = os.path.join(HISTORY_DIR, folder_name)
            os.makedirs(folder, exist_ok=True)

            # Save the full config snapshot as JSON for reload
            meta = {
                'id': entry.get('id'),
                'name': entry.get('name'),
                'savedAt': entry.get('savedAt'),
                'spokeCount': entry.get('spokeCount'),
                'p2Count': entry.get('p2Count'),
                'config': entry.get('config'),
                'folder': folder,
            }
            with open(os.path.join(folder, 'config.json'), 'w', encoding='utf-8') as fh:
                json.dump(meta, fh, indent=2)

            # Save the actual generated XML files alongside it
            for f in entry.get('files', []):
                fpath = os.path.join(folder, f['filename'])
                with open(fpath, 'w', encoding='utf-8') as fh:
                    fh.write(f['content'])

            return {'ok': True, 'folder': folder, 'folderName': folder_name}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def list_history_entries(self):
        """Scan data/history/ and return metadata for each snapshot, newest first."""
        try:
            ensure_dirs()
            entries = []
            if os.path.isdir(HISTORY_DIR):
                for folder_name in sorted(os.listdir(HISTORY_DIR), reverse=True):
                    folder = os.path.join(HISTORY_DIR, folder_name)
                    config_path = os.path.join(folder, 'config.json')
                    if os.path.isdir(folder) and os.path.isfile(config_path):
                        try:
                            with open(config_path, 'r', encoding='utf-8') as fh:
                                meta = json.load(fh)
                            meta['folderName'] = folder_name
                            meta['folder'] = folder
                            entries.append(meta)
                        except Exception:
                            continue
            return {'ok': True, 'entries': entries}
        except Exception as e:
            return {'ok': False, 'error': str(e), 'entries': []}

    def delete_history_entry(self, folder_name):
        try:
            folder = os.path.join(HISTORY_DIR, safe_name(folder_name) if False else folder_name)
            # only allow deleting within HISTORY_DIR
            folder = os.path.abspath(folder)
            if not folder.startswith(os.path.abspath(HISTORY_DIR)):
                return {'ok': False, 'error': 'Invalid path'}
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            return {'ok': True}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def clear_all_history(self):
        try:
            ensure_dirs()
            if os.path.isdir(HISTORY_DIR):
                for folder_name in os.listdir(HISTORY_DIR):
                    folder = os.path.join(HISTORY_DIR, folder_name)
                    if os.path.isdir(folder):
                        shutil.rmtree(folder)
            return {'ok': True}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    # ── P2 Profiles (organized subfolder per profile) ───────────
    def save_p2_profile(self, profile):
        """
        profile: { id, name, savedAt, p2crypto: {...}, networks: [...] }
        Writes: data/profiles/<profile-name>/profile.json
        """
        try:
            ensure_dirs()
            folder = os.path.join(PROFILES_DIR, safe_name(profile.get('name','')))
            os.makedirs(folder, exist_ok=True)
            fpath = os.path.join(folder, 'profile.json')
            with open(fpath, 'w', encoding='utf-8') as fh:
                json.dump(profile, fh, indent=2)
            return {'ok': True, 'folder': folder, 'path': fpath}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def list_p2_profiles(self):
        try:
            ensure_dirs()
            profiles = []
            if os.path.isdir(PROFILES_DIR):
                for folder_name in sorted(os.listdir(PROFILES_DIR)):
                    folder = os.path.join(PROFILES_DIR, folder_name)
                    fpath = os.path.join(folder, 'profile.json')
                    if os.path.isdir(folder) and os.path.isfile(fpath):
                        try:
                            with open(fpath, 'r', encoding='utf-8') as fh:
                                profile = json.load(fh)
                            profile['folderName'] = folder_name
                            profile['folder'] = folder
                            profiles.append(profile)
                        except Exception:
                            continue
            return {'ok': True, 'profiles': profiles}
        except Exception as e:
            return {'ok': False, 'error': str(e), 'profiles': []}

    def delete_p2_profile(self, folder_name):
        try:
            folder = os.path.abspath(os.path.join(PROFILES_DIR, folder_name))
            if not folder.startswith(os.path.abspath(PROFILES_DIR)):
                return {'ok': False, 'error': 'Invalid path'}
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            return {'ok': True}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def rename_p2_profile(self, old_folder_name, new_name):
        try:
            old_folder = os.path.abspath(os.path.join(PROFILES_DIR, old_folder_name))
            if not old_folder.startswith(os.path.abspath(PROFILES_DIR)):
                return {'ok': False, 'error': 'Invalid path'}
            new_folder = os.path.join(PROFILES_DIR, safe_name(new_name))
            if os.path.isdir(old_folder):
                # Update the name inside profile.json too
                fpath = os.path.join(old_folder, 'profile.json')
                if os.path.isfile(fpath):
                    with open(fpath, 'r', encoding='utf-8') as fh:
                        profile = json.load(fh)
                    profile['name'] = new_name
                    with open(fpath, 'w', encoding='utf-8') as fh:
                        json.dump(profile, fh, indent=2)
                if old_folder != new_folder:
                    shutil.move(old_folder, new_folder)
            return {'ok': True, 'folder': new_folder}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
