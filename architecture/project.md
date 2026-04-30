# Project Architecture

## Overview

QR to TXT is a cross-platform desktop (and iOS mobile) app that decodes QR codes
from image files and shows the result in a PySide6 UI. The core flow is: select
one or more images, decode QR codes with `pyzbar` (or `zxingcpp` on iOS), and
display or export the text.

## Directory Structure

```
src/
  qrtotxt/
    __init__.py       — package marker
    __main__.py       — all app logic (decoder + UI window + main())
QRtoTXT.py            — thin launcher shim for direct `python QRtoTXT.py` usage
icon/
  qrtotxt.png         — source icon (PNG)
  qrtotxt.ico         — generated on Windows install (PNG → ICO via Pillow)
architecture/
  project.md          — this file
```

## Components

- **Decoder** (`src/qrtotxt/__main__.py`): `decode_qr_from_file()` uses Pillow +
  pyzbar. On platforms where pyzbar is unavailable (iOS), falls back to `zxingcpp`
  automatically via a try/except import.
- **UI** (`src/qrtotxt/__main__.py`): `QrToTxtWindow` — PySide6 widgets with dark
  theme, drag & drop support, clipboard paste, and keyboard shortcuts.
- **Export**: Save decoded text to a TXT file via a save dialog.
- **Shim** (`QRtoTXT.py`): Adds `src/` to `sys.path` and delegates to
  `qrtotxt.__main__.main()`. Keeps the original launch command working.

## Platform Support

| Platform | How to install | How to build |
|----------|---------------|--------------|
| Linux    | `bash download.sh` | — (run directly with Python) |
| Windows  | `.\download.ps1` in PowerShell | — (run directly with pythonw) |
| macOS    | `briefcase build macOS` | Requires macOS + Xcode |
| iOS      | `briefcase build iOS` | Requires macOS + Xcode |

## Scripts

- `download.sh` / `download.ps1`: install dependencies, clone repo, set up venv,
  create desktop shortcut (Linux: `.desktop` file; Windows: `.lnk` on Desktop).
- `upgrade.sh` / `upgrade.ps1`: `git pull`, update pip packages, refresh shortcut.
- `uninstall.sh` / `uninstall.ps1`: remove shortcut and project folder.

## Briefcase (iOS / macOS)

`pyproject.toml` configures [BeeWare Briefcase](https://briefcase.readthedocs.io)
for packaging:

```bash
pip install briefcase
briefcase build iOS      # requires macOS + Xcode
briefcase build macOS
briefcase build windows  # alternative to the PS script
```

The `sources = ["src/qrtotxt"]` entry tells Briefcase to bundle the `qrtotxt`
package. On iOS, `pyzbar` is replaced by `zxingcpp` (listed in
`[tool.briefcase.app.qrtotxt.iOS].requires`); the app detects the missing pyzbar
at import time and switches automatically.

## Runtime Flow

1. User selects one or more images (file dialog, drag & drop, or clipboard paste).
2. Each image is decoded via `_decode_pil_image()` (pyzbar or zxingcpp).
3. Results are appended to the output textbox with per-file `=== name ===` headers.
4. Optional: save accumulated output as a TXT file.

## IDE Configuration

`pyrightconfig.json` sets `extraPaths = ["src"]` so Pylance resolves
`qrtotxt.*` imports without errors.
