#!/usr/bin/env bash
set -euo pipefail

COLOR_BLUE="\033[1;34m"
COLOR_GREEN="\033[1;32m"
COLOR_YELLOW="\033[1;33m"
COLOR_RESET="\033[0m"

info()    { printf "%b\n" "${COLOR_BLUE}==>${COLOR_RESET} $*"; }
success() { printf "%b\n" "${COLOR_GREEN}OK:${COLOR_RESET} $*"; }
warn()    { printf "%b\n" "${COLOR_YELLOW}WARN:${COLOR_RESET} $*"; }

REPO_URL="https://github.com/NmnRn/QR-to-TXT.git"
TARGET_DIR="$HOME/QR-to-TXT"

info "Installing dependencies"
sudo pacman -Sy --noconfirm git python python-pip zbar

info "Python version"
python --version

if [[ ! -d "$TARGET_DIR" ]]; then
	info "Cloning repository"
	git clone "$REPO_URL" "$TARGET_DIR"
else
	warn "Repository already exists, skipping clone"
fi

cd "$TARGET_DIR"

info "Creating virtual environment"
python -m venv .venv
source .venv/bin/activate

info "Installing Python dependencies"
pip install --upgrade pip
pip install -r requirements.txt

APP_PY="$TARGET_DIR/.venv/bin/python"
APP_ICON="$TARGET_DIR/icon/qrtotxt.png"
DESKTOP_FILE="$HOME/.local/share/applications/qr-to-txt.desktop"

info "Creating desktop shortcut"
mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=QR to TXT
Comment=Decode QR codes to text
Exec=$APP_PY $TARGET_DIR/QRtoTXT.py
Icon=$APP_ICON
Terminal=false
Categories=Utility;Graphics;
EOF

success "Setup completed"
