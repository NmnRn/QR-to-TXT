STRINGS: dict[str, str] = {
    # ── Buttons ───────────────────────────────────────────────────────────────
    "btn_open_images":  "Open Image(s)",
    "btn_open_folder":  "Open Folder",
    "btn_open_pdf":     "Open PDF",
    "btn_scan_camera":  "Scan Camera",
    "btn_paste":        "Paste",
    "btn_generate_qr":  "Generate QR",
    "btn_copy_all":     "Copy All",
    "btn_save_txt":     "Save TXT",
    "btn_clear":        "Clear",
    "btn_browse":       "Browse",
    "btn_close":        "Close",

    # ── Tooltips ──────────────────────────────────────────────────────────────
    "tip_open_images":  "Open one or more QR code images",
    "tip_open_folder":  "Scan all images in a folder",
    "tip_open_pdf":     "Extract QR codes from a PDF",
    "tip_scan_camera":  "Scan with webcam",
    "tip_paste":        "Decode QR from clipboard image",
    "tip_generate_qr":  "Create a QR code from text or URL",
    "tip_copy_all":     "Copy all results to clipboard",
    "tip_save_txt":     "Save results as plain text",
    "tip_clear":        "Clear all results",

    # ── Menu ──────────────────────────────────────────────────────────────────
    "menu_file":            "File",
    "menu_open_images":     "Open Image(s)",
    "menu_open_folder":     "Open Folder",
    "menu_open_pdf":        "Open PDF",
    "menu_scan_camera":     "Scan Camera",
    "menu_paste":           "Paste from Clipboard",
    "menu_save_txt":        "Save as TXT",
    "menu_save_csv":        "Save as CSV",
    "menu_save_json":       "Save as JSON",
    "menu_exit":            "Exit",
    "menu_tools":           "Tools",
    "menu_generate_qr":     "Generate QR Code",
    "menu_edit":            "Edit",
    "menu_copy_all":        "Copy All",
    "menu_clear":           "Clear",
    "menu_settings":        "Settings",
    "menu_help":            "Help",
    "menu_history":         "Session History",
    "menu_upgrade":         "Upgrade",
    "menu_check_updates":   "Check for Updates",
    "menu_version":         "Version",

    # ── Shortcuts (appended to menu labels) ───────────────────────────────────
    "sc_open_images":   "   Ctrl+O",
    "sc_paste":         "   Ctrl+V",
    "sc_save_txt":      "   Ctrl+S",
    "sc_copy_all":      "   Ctrl+Shift+C",

    # ── Status bar ────────────────────────────────────────────────────────────
    "status_ready":     "Ready",
    "status_copied":    "Copied to clipboard.",
    "status_qr_copied": "QR code copied to clipboard.",
    "status_checking":  "Checking for updates…",
    "status_upgrading": "Upgrading… please wait.",
    "status_sources":   "{sources} source(s)  ·  {qrs} QR code(s) decoded",

    # ── Output area ───────────────────────────────────────────────────────────
    "placeholder_output":  "QR result will appear here…",
    "result_no_qr":        "No QR code found.",

    # ── Messages ──────────────────────────────────────────────────────────────
    "msg_no_image_clipboard":   "No image in clipboard.",
    "msg_no_content_save":      "No content to save.",
    "msg_no_content_copy":      "No content to copy.",
    "msg_no_history":           "No history yet in this session.",
    "msg_no_images_folder":     "No image files found in that folder.",
    "msg_file_saved":           "File saved.",
    "msg_csv_saved":            "CSV saved.",
    "msg_json_saved":           "JSON saved.",
    "msg_qr_saved":             "QR code saved.",
    "msg_generate_first":       "Generate a QR code first.",
    "msg_enter_text":           "Please enter some text or a URL.",
    "msg_upgrade_success":      "Upgrade successful! The app will now restart.",
    "msg_update_timeout":       "Update check timed out. Please try again.",
    "msg_restart_language":     "Restart the app to apply the new language.",

    # ── Update / upgrade ──────────────────────────────────────────────────────
    "upd_up_to_date":       "You are running the latest version (v{version}).",
    "upd_already_latest":   "Already on the latest version (v{version}).",
    "upd_available":        "New version v{version} is available.\nVisit github.com/NmnRn/QR-to-TXT to download.",
    "upd_upgrade_prompt":   "A newer version is available (you are on v{version}).\nUpgrade now?\n\nThe app will restart after upgrading.",
    "upd_reach_remote":     "Could not reach remote:\n{error}",
    "upd_reach_server":     "Could not reach update server:\n{error}",

    # ── Dialog titles ─────────────────────────────────────────────────────────
    "dlg_open_images":      "Select QR image(s)",
    "dlg_open_folder":      "Select folder",
    "dlg_open_pdf":         "Select PDF",
    "dlg_save_txt":         "Save as TXT",
    "dlg_save_csv":         "Save as CSV",
    "dlg_save_json":        "Save as JSON",
    "dlg_save_qr":          "Save QR Code",
    "dlg_history_title":    "Session History",
    "dlg_history_hint":     "Click an entry to see full results:",
    "dlg_settings_title":   "Settings",
    "dlg_generator_title":  "Generate QR Code",
    "dlg_version_text":     "QR to TXT\nVersion: v{version}",

    # ── Settings labels ───────────────────────────────────────────────────────
    "settings_theme":           "Theme:",
    "settings_language":        "Language:",
    "settings_save_folder":     "Default save folder:",
    "settings_history_limit":   "History limit (entries):",
    "settings_check_updates":   "Check for updates on start:",

    # ── Generator dialog ──────────────────────────────────────────────────────
    "gen_hint":         "Enter text or URL to encode",
    "gen_placeholder":  "Paste a link or type any text…",
    "gen_type_none":    "—",
    "gen_type_link":    "Link",
    "gen_type_text":    "Text",
    "gen_generate":     "Generate  →",
    "gen_save_png":     "Save PNG",
    "gen_copy_image":   "Copy Image",
    "gen_qr_placeholder": "QR code will appear here",
    "gen_auto_saved":   "Auto-saved to QR Codes/",

    # ── History dialog ────────────────────────────────────────────────────────
    "hist_source":      "Source:    {source}",
    "hist_time":        "Time:      {time}",
    "hist_no_qr":       "(no QR)",
    "hist_no_qr_found": "No QR code found.",

    # ── Tray ──────────────────────────────────────────────────────────────────
    "tray_show":    "Show",
    "tray_quit":    "Quit",
    "tray_tooltip": "QR to TXT",

    # ── Errors ────────────────────────────────────────────────────────────────
    "err_upgrade_failed":   "Upgrade failed",
    "err_missing_pdf":      "PDF support requires pymupdf:\n\npip install pymupdf",
    "err_missing_qrcode":   "QR generation requires qrcode:\n\npip install \"qrcode[pil]\"",

    # ── Titles for message boxes ───────────────────────────────────────────────
    "title_info":           "Info",
    "title_error":          "Error",
    "title_errors":         "Errors",
    "title_saved":          "Saved",
    "title_upgrade":        "Upgrade",
    "title_up_to_date":     "Up to date",
    "title_upgrade_avail":  "Upgrade available",
    "title_upgrade_fail":   "Upgrade failed",
    "title_upgrade_ok":     "Upgrade complete",
    "title_update_check":   "Update check",
    "title_update_fail":    "Update check failed",
    "title_update_avail":   "Update available",
    "title_missing_pkg":    "Missing package",
    "title_version":        "Version",
    "title_language":       "Language",
}
