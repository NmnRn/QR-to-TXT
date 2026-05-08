THEMES: dict[str, dict] = {
	"Dark": {
		"window_bg":    "#0f1115",
		"widget_bg":    "#151923",
		"text":         "#e6e9ef",
		"text_dim":     "#8c93a0",
		"text_header":  "#d7dbe2",
		"border":       "#202636",
		"button_bg":    "#2b6be4",
		"button_hover": "#3a7af0",
		"button_press": "#245bbf",
		"button_dis":   "#1e2433",
		"button_dis_fg":"#555e72",
		"menu_sel":     "#2b6be4",
		"list_sel":     "#2b6be4",
		"link":         "#6ab0f5",
		"result_src":   "#8c93a0",
		"result_empty": "#555e72",
		"result_text":  "#e6e9ef",
	},
	"Light": {
		"window_bg":    "#f0f2f5",
		"widget_bg":    "#ffffff",
		"text":         "#1a1d23",
		"text_dim":     "#6b7280",
		"text_header":  "#111827",
		"border":       "#d1d5db",
		"button_bg":    "#2b6be4",
		"button_hover": "#3a7af0",
		"button_press": "#245bbf",
		"button_dis":   "#e5e7eb",
		"button_dis_fg":"#9ca3af",
		"menu_sel":     "#2b6be4",
		"list_sel":     "#2b6be4",
		"link":         "#1d4ed8",
		"result_src":   "#6b7280",
		"result_empty": "#9ca3af",
		"result_text":  "#111827",
	},
	"Nord": {
		"window_bg":    "#2e3440",
		"widget_bg":    "#3b4252",
		"text":         "#eceff4",
		"text_dim":     "#7b8fa6",
		"text_header":  "#e5e9f0",
		"border":       "#434c5e",
		"button_bg":    "#5e81ac",
		"button_hover": "#81a1c1",
		"button_press": "#4c6f96",
		"button_dis":   "#3b4252",
		"button_dis_fg":"#616e88",
		"menu_sel":     "#5e81ac",
		"list_sel":     "#5e81ac",
		"link":         "#88c0d0",
		"result_src":   "#7b8fa6",
		"result_empty": "#616e88",
		"result_text":  "#eceff4",
	},
}

THEME_NAMES = list(THEMES.keys())


def build_stylesheet(name: str) -> str:
	t = THEMES.get(name, THEMES["Dark"])
	return f"""
		QMainWindow, QWidget {{ background: {t['window_bg']}; }}
		QMenuBar {{
			background: {t['window_bg']}; color: {t['text_header']};
			font-size: 13px; padding: 2px;
		}}
		QMenuBar::item:selected {{ background: {t['border']}; border-radius: 4px; }}
		QMenu {{
			background: {t['widget_bg']}; color: {t['text_header']};
			border: 1px solid {t['border']};
		}}
		QMenu::item:selected {{ background: {t['menu_sel']}; color: white; }}
		QLabel {{ color: {t['text_header']}; font-size: 13px; }}
		QLabel#Footer {{ color: {t['text_dim']}; font-size: 12px; margin-top: 2px; }}
		QPushButton {{
			background: {t['button_bg']}; color: white; border: none;
			padding: 7px 13px; border-radius: 8px; font-size: 13px;
		}}
		QPushButton:hover {{ background: {t['button_hover']}; }}
		QPushButton:pressed {{ background: {t['button_press']}; }}
		QPushButton:disabled {{
			background: {t['button_dis']}; color: {t['button_dis_fg']};
		}}
		QTextBrowser {{
			background: {t['widget_bg']}; color: {t['text']};
			border: 1px solid {t['border']}; border-radius: 10px;
			padding: 10px; font-family: Consolas,monospace; font-size: 12px;
		}}
		QStatusBar {{ background: {t['window_bg']}; color: {t['text_dim']}; font-size: 12px; }}
		QListWidget {{
			background: {t['widget_bg']}; color: {t['text']};
			border: 1px solid {t['border']}; border-radius: 8px; font-size: 12px;
		}}
		QListWidget::item:selected {{ background: {t['list_sel']}; color: white; }}
		QLineEdit, QSpinBox, QComboBox {{
			background: {t['widget_bg']}; color: {t['text']};
			border: 1px solid {t['border']}; border-radius: 6px;
			padding: 6px 8px; font-size: 13px;
		}}
		QComboBox::drop-down {{ border: none; }}
		QComboBox QAbstractItemView {{
			background: {t['widget_bg']}; color: {t['text']};
			border: 1px solid {t['border']}; selection-background-color: {t['menu_sel']};
		}}
		QCheckBox {{ color: {t['text_header']}; font-size: 13px; }}
		QCheckBox::indicator {{ width: 16px; height: 16px; }}
		QDialog {{ background: {t['window_bg']}; }}
		QDialogButtonBox QPushButton {{ padding: 7px 22px; }}
		QFrame#Separator {{
			color: {t['border']}; background: {t['border']};
			max-width: 1px; margin: 4px 4px;
		}}
		QPushButton#GenBtn {{
			background: {t['button_bg']}; color: white; border: none;
			padding: 7px 16px; border-radius: 8px; font-size: 13px; font-weight: bold;
		}}
		QPushButton#GenBtn:hover  {{ background: {t['button_hover']}; }}
		QPushButton#GenBtn:pressed {{ background: {t['button_press']}; }}
		QPushButton#ClearBtn {{
			background: transparent; color: {t['text_dim']};
			border: 1px solid {t['border']};
			padding: 7px 13px; border-radius: 8px; font-size: 13px;
		}}
		QPushButton#ClearBtn:hover {{
			background: {t['border']}; color: {t['text']};
		}}
	"""
