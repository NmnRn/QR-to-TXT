# QR to TXT

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20iOS-lightgrey)

A desktop app that reads QR codes from images, PDFs, webcam, or clipboard and converts them to text.
Uses a PySide6 UI with `pyzbar` and `Pillow` for decoding.

## Features

- Decode QR from image files (PNG/JPG/JPEG/BMP), PDFs, webcam, or clipboard
- Select multiple files at once — results append, nothing is overwritten
- Open entire folder — all images processed at once
- Drag & drop images/PDFs directly onto the window
- Clickable links in output
- Save as TXT, CSV, or JSON
- Copy all results to clipboard
- Session history, system tray, settings, auto-update check
- Keyboard shortcuts: Ctrl+O (open), Ctrl+V (paste), Ctrl+S (save), Ctrl+Shift+C (copy)

---

## Linux

Scripts are organized by distribution under the `linux/` folder.

### Debian / Ubuntu

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/debian/download.sh | bash
```

```bash
# Upgrade
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/debian/upgrade.sh | bash

# Uninstall
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/debian/uninstall.sh | bash
```

### Fedora / RHEL / CentOS

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/fedora/download.sh | bash
```

```bash
# Upgrade
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/fedora/upgrade.sh | bash

# Uninstall
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/fedora/uninstall.sh | bash
```

### Arch Linux

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/arch/download.sh | bash
```

```bash
# Upgrade
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/arch/upgrade.sh | bash

# Uninstall
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/arch/uninstall.sh | bash
```

### openSUSE

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/opensuse/download.sh | bash
```

```bash
# Upgrade
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/opensuse/upgrade.sh | bash

# Uninstall
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/linux/opensuse/uninstall.sh | bash
```

### Manual install (any distro)

Install `libzbar` with your package manager, then:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python QRtoTXT.py
```

---

## macOS

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/download_macos.sh | bash

# Upgrade
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/upgrade_macos.sh | bash

# Uninstall
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/uninstall_macos.sh | bash
```

---

## Windows

Open **PowerShell** and run:

```powershell
# Install
powershell -ExecutionPolicy Bypass -c "iwr -useb https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/download.ps1 | iex"

# Upgrade
powershell -ExecutionPolicy Bypass -c "iwr -useb https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/upgrade.ps1 | iex"

# Uninstall
powershell -ExecutionPolicy Bypass -c "iwr -useb https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/uninstall.ps1 | iex"
```

---

## iOS / macOS (Briefcase)

Requires macOS + Xcode:

```bash
pip install briefcase
briefcase build iOS
briefcase build macOS
```

---

## Architecture

See [architecture/project.md](architecture/project.md).

## Notes

- On Windows, `pyzbar` ships with a pre-built zbar DLL — no extra install needed.
- If decoding fails, make sure the image is clear and well-lit.

## License

MIT License. See [LICENSE](LICENSE).
