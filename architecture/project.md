# Project Architecture

## Overview

QR to TXT is a cross-platform desktop app (Linux, Windows, macOS) that decodes QR
codes from images, PDFs, webcam, and clipboard — and also generates QR codes from
text or URLs. Built with PySide6 and Python 3.10+.

All decoded and generated QR records are persisted in a local SQLite database with
an in-memory read cache. The UI is fully internationalised (English / Turkish).

---

## Directory Structure

```
src/qrtotxt/
  __init__.py          — package marker
  __main__.py          — entry point: init DB + i18n, build QApplication, start loop
  camera.py            — webcam capture dialog (OpenCV)
  decoder.py           — QR decode logic (pyzbar / zxingcpp fallback)
  updater.py           — GitHub release version check
  settings.py          — AppSettings (QSettings) + SettingsDialog
  themes.py            — THEMES colour dict + build_stylesheet()
  tray.py              — system-tray icon and context menu
  window.py            — QrToTxtWindow main window + HistoryDialog
  db/
    __init__.py        — AppDB singleton: RAM cache + async SQLite writes
    migrations.py      — versioned schema migrations (v1, v2, …)
  i18n/
    __init__.py        — tr(key), set_language(), LANGUAGES dict
    _en.py             — English strings (~90 keys)
    _tr.py             — Turkish strings (~90 keys)
  generator/
    __init__.py        — re-exports GeneratorDialog
    dialog.py          — QR generation dialog: themed preview + white-bg save

QRtoTXT.py             — thin launcher shim (adds src/ to sys.path)
requirements.txt       — runtime pip dependencies
pyproject.toml         — Briefcase packaging config (macOS / iOS)
architecture/
  project.md           — this file
icon/
  qrtotxt.png          — application icon
```

---

## Module Responsibilities

### `__main__.py` — Bootstrap

```
AppDB.instance()          ← initialise DB + apply migrations
set_language(lang)        ← load i18n strings from DB preference
QApplication              ← create Qt app
QrToTxtWindow             ← build main window
AppTray                   ← system tray
check_for_update(...)     ← background version check
```

### `db/` — Persistence Layer

**Design:** write-through RAM cache. The entire database is loaded into Python
lists/dicts at startup. All reads are served from memory (zero I/O). All writes
update the cache synchronously and dispatch an SQLite write to a daemon thread.

```
AppDB.instance()          ← singleton
  .get(key) / .set(key, value)        ← settings table (language, …)
  .add_decoded(source, content)       ← decoded_qrs table
  .get_decoded() → list[dict]
  .add_generated(content, type, path) ← generated_qrs table
  .get_generated() → list[dict]
```

**Schema migrations** (`migrations.py`): each migration is a plain function
`fn(conn: sqlite3.Connection)`. The `schema_version` table tracks the highest
applied version. On startup, any unapplied migrations run in order. Adding a new
migration = appending one function to `MIGRATIONS`.

**DB location:**
| Platform | Path |
|----------|------|
| Linux    | `~/.local/share/QRtoTXT/app.db` |
| Windows  | `C:\Users\<user>\AppData\Local\QRtoTXT\app.db` *(planned)* |
| macOS    | `~/Library/Application Support/QRtoTXT/app.db` *(planned)* |

### `i18n/` — Internationalisation

```python
from .i18n import tr, set_language, LANGUAGES

set_language("tr")          # called once at startup from DB preference
tr("btn_open_images")       # → "Resim Aç"
```

String files are `_en.py` and `_tr.py` (prefixed `_` to avoid shadowing the
`tr()` function on import). Language changes are stored in the DB and take effect
after restart.

### `window.py` — Main Window

Layout:

```
┌─ menu bar (File · Tools · Edit · Help) ─────────────────────────────┐
├─ top toolbar ────────────────────────────────────────────────────────┤
│  [Open Image] [Folder] [PDF] [Camera] [Paste]  │  [Generate QR]     │
├─ output area (QTextBrowser, linkified, themed HTML) ─────────────────┤
├─ bottom toolbar ─────────────────────────────────────────────────────┤
│  [Copy All] [Save TXT] [Save CSV] [Save JSON]          [Clear]       │
├─ status label ───────────────────────────────────────────────────────┤
└──────────────────────────────────────────────────────────────────────┘
```

Every decoded result is written to `AppDB.add_decoded()` in `_add_result()`.

### `generator/dialog.py` — QR Generator

On **Generate**:
1. Produce a **themed** PIL image (`text` colour on `widget_bg`) → display preview.
2. Produce a **white-bg** PIL image (black on white) → save / clipboard export.
3. Auto-save white image to `~/QR Codes/qr_YYYYMMDD_HHMMSS.png`.
4. Record in `AppDB.add_generated()`.

The user can additionally **Save PNG** (manual path) or **Copy Image** (clipboard);
both use the white-bg image so QR codes are universally scannable.

### `themes.py` — Theming

Three built-in themes: **Dark**, **Light**, **Nord**. Each theme is a `dict` with
named colour keys (`window_bg`, `widget_bg`, `text`, `border`, `button_bg`, …).

`build_stylesheet(name)` generates a single Qt stylesheet string applied to the
main window. Dialogs call their own `_apply_theme()` using the same colour dict.

### `updater.py` — Version Checks

Two independent mechanisms:

| Action | Mechanism |
|--------|-----------|
| Help → Upgrade | `git fetch` + hash compare; `git merge --ff-only` on confirm |
| Help → Check for Updates | GitHub Releases API (`/repos/.../releases/latest`) |

`_sync_latest()` raises on network error so the caller can show a proper error
message instead of silently reporting "up to date".

---

## Data Flow

### Decode path

```
File / Camera / Clipboard / PDF
        │
        ▼
  decoder.py  (pyzbar → zxingcpp fallback)
        │
        ▼
  window._add_result()
     ├─ append to self._results  (session, in-memory)
     ├─ append to self._history  (session, capped)
     ├─ AppDB.add_decoded()      (persisted)
     └─ _render()  →  QTextBrowser (themed HTML)
```

### Generate path

```
User types text / URL
        │
        ▼
  generator.dialog._generate()
     ├─ _make_qr_image(…, themed colours)  → display pixmap
     ├─ _make_qr_image(…, black/white)     → save image
     ├─ _auto_save()  →  ~/QR Codes/*.png
     └─ AppDB.add_generated()
```

---

## Platform Support

| Platform | Installer | Run |
|----------|-----------|-----|
| Linux    | `bash download.sh` | `python QRtoTXT.py` |
| Windows  | `.\download.ps1` (PowerShell) | `pythonw QRtoTXT.py` |
| macOS    | `bash download_macos.sh` | `python QRtoTXT.py` |
| iOS      | `briefcase build iOS` (macOS + Xcode) | Briefcase runner |

Camera (`camera.py`) requires `opencv-python-headless` and is disabled gracefully
when the package is absent (iOS, some CI environments).

PDF decoding requires `pymupdf` and is imported lazily — missing package shows an
inline error dialog rather than crashing.

---

## Scripts

- `download.sh` / `download.ps1` / `download_macos.sh`: clone repo, create venv,
  install dependencies, create desktop/Start-Menu shortcut.
- `upgrade.sh` / `upgrade.ps1` / `upgrade_macos.sh`: `git pull`, update packages.
- `uninstall.sh` / `uninstall.ps1` / `uninstall_macos.sh`: remove shortcut + folder.

In-app upgrade (Help → Upgrade) runs the same `git fetch` + `pip install -r`
sequence without leaving the application.

---

## IDE / Type Checking

`pyrightconfig.json` sets `extraPaths = ["src"]` so Pylance resolves `qrtotxt.*`
imports. All public functions carry type annotations; `cast()` is used where
third-party stubs (qrcode, PIL) are incomplete.
