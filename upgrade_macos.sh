#!/usr/bin/env bash
set -euo pipefail

COLOR_BLUE="\033[1;34m"
COLOR_GREEN="\033[1;32m"
COLOR_YELLOW="\033[1;33m"
COLOR_RESET="\033[0m"

info()    { printf "%b\n" "${COLOR_BLUE}==>${COLOR_RESET} $*"; }
success() { printf "%b\n" "${COLOR_GREEN}OK:${COLOR_RESET} $*"; }
warn()    { printf "%b\n" "${COLOR_YELLOW}WARN:${COLOR_RESET} $*"; }

TARGET_DIR="$HOME/QR-to-TXT"
SHORTCUT="$HOME/Desktop/QR to TXT.command"

if [[ ! -d "$TARGET_DIR" ]]; then
	warn "Project folder not found: $TARGET_DIR"
	exit 1
fi

info "Checking for updates"
cd "$TARGET_DIR"

pull_output=$(git pull --ff-only 2>&1)
if echo "$pull_output" | grep -q "Already up to date"; then
	success "Already up to date — nothing to do."
	exit 0
fi

info "Updating virtual environment"
if [[ ! -d ".venv" ]]; then
	python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

info "Refreshing desktop shortcut"
cat > "$SHORTCUT" <<EOF
#!/usr/bin/env bash
cd "$TARGET_DIR"
.venv/bin/python QRtoTXT.py
EOF
chmod +x "$SHORTCUT"

success "Upgrade completed"
