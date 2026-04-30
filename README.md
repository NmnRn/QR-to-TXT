# QR to TXT

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20iOS-lightgrey)

A simple desktop app that reads QR codes from image files and converts them to text.
Uses a PySide6 UI with `pyzbar` and `Pillow` for decoding.

## Features

- Decode QR from image files (PNG/JPG/JPEG/BMP)
- Select multiple files at once — results append, nothing is overwritten
- Drag & drop images directly onto the window
- Paste an image from clipboard (Ctrl+V)
- Save output as TXT
- Keyboard shortcuts: Ctrl+O (open), Ctrl+V (paste), Ctrl+S (save)

---

## Linux

### One-command install

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/download.sh | bash
```

### Upgrade

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/upgrade.sh | bash
```

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/uninstall.sh | bash
```

### Manual install

```bash
sudo apt install libzbar0
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python QRtoTXT.py
```

---

## macOS

### One-command install

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/download_macos.sh | bash
```

Installs Homebrew (if needed), `zbar`, Python, clones the repo, and creates a
double-clickable shortcut on your Desktop.

### Upgrade

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/upgrade_macos.sh | bash
```

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/uninstall_macos.sh | bash
```

---

## Windows

### One-command install

Open **PowerShell** and run:

```powershell
powershell -ExecutionPolicy Bypass -c "iwr -useb https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/download.ps1 | iex"
```

Installs Python and Git via `winget` (if needed), clones the repo, and creates a
shortcut on your Desktop.

### Upgrade

```powershell
powershell -ExecutionPolicy Bypass -c "iwr -useb https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/upgrade.ps1 | iex"
```

### Uninstall

```powershell
powershell -ExecutionPolicy Bypass -c "iwr -useb https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/uninstall.ps1 | iex"
```

---

## iOS / macOS (Briefcase)

Requires macOS + Xcode:

```bash
pip install briefcase
briefcase build iOS
briefcase build macOS   # native .app bundle
```

On iOS, `pyzbar` is replaced automatically by `zxingcpp` (no code changes needed).

---

## Architecture

See [architecture/project.md](architecture/project.md).

## Notes

- On Windows, `pyzbar` ships with a pre-built zbar DLL — no extra install needed.
- If decoding fails, make sure the image is clear and well-lit.

## License

MIT License. See [LICENSE](LICENSE).
