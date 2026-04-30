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

# Homebrew
if ! command -v brew &>/dev/null; then
	info "Installing Homebrew"
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# zbar (required by pyzbar)
info "Installing zbar"
brew install zbar

# Python
if ! command -v python3 &>/dev/null; then
	info "Installing Python"
	brew install python
fi
python3 --version

# Git (usually pre-installed on macOS via Xcode CLI tools)
if ! command -v git &>/dev/null; then
	info "Installing Git"
	brew install git
fi

# Clone
if [[ ! -d "$TARGET_DIR" ]]; then
	info "Cloning repository"
	git clone "$REPO_URL" "$TARGET_DIR"
else
	warn "Repository already exists at $TARGET_DIR, skipping clone"
fi

cd "$TARGET_DIR"

info "Creating virtual environment"
python3 -m venv .venv
source .venv/bin/activate

info "Installing Python dependencies"
pip install --upgrade pip
pip install -r requirements.txt

# Desktop shortcut (.command file — double-clickable on macOS)
SHORTCUT="$HOME/Desktop/QR to TXT.command"
cat > "$SHORTCUT" <<EOF
#!/usr/bin/env bash
cd "$TARGET_DIR"
.venv/bin/python QRtoTXT.py
EOF
chmod +x "$SHORTCUT"

success "Setup completed — shortcut created on Desktop"
