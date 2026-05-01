#!/usr/bin/env bash
set -euo pipefail

COLOR_BLUE="\033[1;34m"
COLOR_GREEN="\033[1;32m"
COLOR_YELLOW="\033[1;33m"
COLOR_RESET="\033[0m"

info() {
	printf "%b\n" "${COLOR_BLUE}==>${COLOR_RESET} $*"
}

success() {
	printf "%b\n" "${COLOR_GREEN}OK:${COLOR_RESET} $*"
}

warn() {
	printf "%b\n" "${COLOR_YELLOW}WARN:${COLOR_RESET} $*"
}

TARGET_DIR="/home/$USER/QR-to-TXT"
APP_PY="$TARGET_DIR/.venv/bin/python"
APP_ICON="$TARGET_DIR/icon/qrtotxt.png"
DESKTOP_FILE="$HOME/.local/share/applications/qr-to-txt.desktop"

if [[ ! -d "$TARGET_DIR" ]]; then
	warn "Project folder not found: $TARGET_DIR"
	exit 1
fi

info "Checking for updates"
cd "$TARGET_DIR"
git fetch --quiet
if [[ "$(git rev-parse HEAD)" == "$(git rev-parse @{u})" ]]; then
	success "Already up to date — nothing to do."
	exit 0
fi
git merge --ff-only @{u}

info "Updating virtual environment"
if [[ ! -d ".venv" ]]; then
	python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

info "Refreshing desktop shortcut"
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

success "Upgrade completed"
