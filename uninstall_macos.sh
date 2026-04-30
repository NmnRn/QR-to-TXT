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

info "Removing desktop shortcut"
if [[ -f "$SHORTCUT" ]]; then
	rm -f "$SHORTCUT"
	info "Removed $SHORTCUT"
else
	warn "Shortcut not found"
fi

info "Removing project folder"
if [[ -d "$TARGET_DIR" ]]; then
	rm -rf "$TARGET_DIR"
	info "Removed $TARGET_DIR"
else
	warn "Project folder not found"
fi

success "Uninstall completed"
