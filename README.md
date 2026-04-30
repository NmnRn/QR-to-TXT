# QR to TXT

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

A simple desktop app that reads QR codes from image files and converts them to text.
Uses a PySide6 UI with `pyzbar` and `Pillow` for decoding.

## Features

- Decode QR from image files (PNG/JPG/JPEG/BMP)
- Show decoded text in the app
- Save output as TXT

## Installation

> On Linux, `pyzbar` requires the system `zbar` library.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Linux (zbar)

```bash
sudo apt update
sudo apt install libzbar0
```

### macOS (zbar)

```bash
brew install zbar
```

## Run

```bash
python QRtoTXT.py
```

## One-command install (Linux)

```bash
bash download.sh
```

To download and run with one command:

```bash
curl -fsSL https://raw.githubusercontent.com/NmnRn/QR-to-TXT/main/download.sh | bash
```

This script clones the repo, creates a virtual environment, and adds a desktop shortcut.

## Notes

- On Windows, `pyzbar` usually works with prebuilt wheels.
- If decoding fails, make sure the image is clear and well-lit.

## License

MIT License. See [LICENSE](LICENSE).
