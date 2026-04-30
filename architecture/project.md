# Project Architecture

## Overview

QR to TXT is a small desktop app that decodes QR codes from image files and
shows the result in a PySide6 UI. The core flow is: select an image, decode QR
codes with `pyzbar`, and display or export the text.

## Components

- UI: PySide6 widgets in `QRtoTXT.py`.
- Decoder: `decode_qr_from_file()` uses Pillow + pyzbar.
- Export: Save decoded text to a TXT file via a save dialog.

## Scripts

- `download.sh`: installs dependencies, clones the repo, sets up venv, and
  creates a desktop shortcut.
- `upgrade.sh`: pulls the latest code and updates Python dependencies.
- `uninstall.sh`: removes the desktop shortcut and project folder.

## Runtime Flow

1. User selects an image.
2. The image is decoded via `pyzbar`.
3. Results are rendered in the output textbox.
4. Optional: save output as a TXT file.
