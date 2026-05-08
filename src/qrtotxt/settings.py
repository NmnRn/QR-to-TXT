import os

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
	QCheckBox,
	QComboBox,
	QDialog,
	QDialogButtonBox,
	QFileDialog,
	QFormLayout,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QMessageBox,
	QPushButton,
	QSpinBox,
	QWidget,
)


class AppSettings:
	def __init__(self) -> None:
		self._s = QSettings("NmnRn", "QRtoTXT")

	@property
	def save_path(self) -> str:
		return str(self._s.value("save_path", os.path.expanduser("~")))

	@save_path.setter
	def save_path(self, v: str) -> None:
		self._s.setValue("save_path", v)

	@property
	def history_limit(self) -> int:
		v = self._s.value("history_limit", 50)
		return int(v) if v is not None else 50  # type: ignore[arg-type]

	@history_limit.setter
	def history_limit(self, v: int) -> None:
		self._s.setValue("history_limit", v)

	@property
	def theme(self) -> str:
		return str(self._s.value("theme", "Dark"))

	@theme.setter
	def theme(self, v: str) -> None:
		self._s.setValue("theme", v)

	@property
	def check_updates(self) -> bool:
		v = self._s.value("check_updates", True)
		if isinstance(v, bool):
			return v
		return str(v).lower() not in ("false", "0", "no")

	@check_updates.setter
	def check_updates(self, v: bool) -> None:
		self._s.setValue("check_updates", v)


class SettingsDialog(QDialog):
	def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._settings = settings
		from .i18n import tr
		self.setWindowTitle(tr("dlg_settings_title"))
		self.setMinimumWidth(440)
		self._build_ui()
		self._apply_theme()

	def _build_ui(self) -> None:
		from .i18n import LANGUAGES, tr
		from .themes import THEME_NAMES

		layout = QFormLayout()
		layout.setContentsMargins(24, 24, 24, 24)
		layout.setSpacing(16)

		# Theme
		self._theme_combo = QComboBox()
		self._theme_combo.addItems(THEME_NAMES)
		idx = THEME_NAMES.index(self._settings.theme) if self._settings.theme in THEME_NAMES else 0
		self._theme_combo.setCurrentIndex(idx)
		layout.addRow(tr("settings_theme"), self._theme_combo)

		# Language (stored in DB)
		from .db import AppDB
		self._lang_combo = QComboBox()
		lang_codes = list(LANGUAGES.keys())
		self._lang_combo.addItems(list(LANGUAGES.values()))
		current_lang = AppDB.instance().get("language", "en")
		lang_idx = lang_codes.index(current_lang) if current_lang in lang_codes else 0
		self._lang_combo.setCurrentIndex(lang_idx)
		self._lang_codes = lang_codes
		layout.addRow(tr("settings_language"), self._lang_combo)

		# Default save folder
		row = QWidget()
		hl = QHBoxLayout(row)
		hl.setContentsMargins(0, 0, 0, 0)
		self._path_edit = QLineEdit(self._settings.save_path)
		browse_btn = QPushButton(tr("btn_browse"))
		browse_btn.clicked.connect(self._browse)
		hl.addWidget(self._path_edit)
		hl.addWidget(browse_btn)
		layout.addRow(tr("settings_save_folder"), row)

		# History limit
		self._history_spin = QSpinBox()
		self._history_spin.setRange(10, 500)
		self._history_spin.setValue(self._settings.history_limit)
		layout.addRow(tr("settings_history_limit"), self._history_spin)

		# Check updates
		self._update_check = QCheckBox()
		self._update_check.setChecked(self._settings.check_updates)
		layout.addRow(tr("settings_check_updates"), self._update_check)

		btns = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		btns.accepted.connect(self._save)
		btns.rejected.connect(self.reject)
		layout.addRow(btns)

		self.setLayout(layout)

	def _browse(self) -> None:
		d = QFileDialog(self, "Select default save folder", self._settings.save_path)
		d.setStyleSheet("")
		d.setFileMode(QFileDialog.FileMode.Directory)
		d.setOption(QFileDialog.Option.ShowDirsOnly, True)
		if d.exec():
			self._path_edit.setText(d.selectedFiles()[0])

	def _save(self) -> None:
		from .db import AppDB
		from .i18n import tr

		self._settings.theme = self._theme_combo.currentText()
		self._settings.save_path = self._path_edit.text()
		self._settings.history_limit = self._history_spin.value()
		self._settings.check_updates = self._update_check.isChecked()

		new_lang = self._lang_codes[self._lang_combo.currentIndex()]
		old_lang = AppDB.instance().get("language", "en")
		if new_lang != old_lang:
			AppDB.instance().set("language", new_lang)
			QMessageBox.information(
				self, tr("title_language"), tr("msg_restart_language")
			)

		self.accept()

	def _apply_theme(self) -> None:
		from .themes import THEMES
		t = THEMES.get(self._settings.theme, THEMES["Dark"])
		self.setStyleSheet(f"""
			QDialog {{ background: {t['window_bg']}; }}
			QLabel {{
				color: {t['text_header']}; font-size: 13px;
				background: transparent;
			}}
			QLineEdit, QSpinBox {{
				background: {t['widget_bg']}; color: {t['text']};
				border: 1px solid {t['border']}; border-radius: 6px;
				padding: 6px 8px; font-size: 13px;
			}}
			QComboBox {{
				background: {t['widget_bg']}; color: {t['text']};
				border: 1px solid {t['border']}; border-radius: 6px;
				padding: 6px 8px; font-size: 13px;
			}}
			QComboBox::drop-down {{ border: none; }}
			QComboBox QAbstractItemView {{
				background: {t['widget_bg']}; color: {t['text']};
				border: 1px solid {t['border']};
				selection-background-color: {t['menu_sel']};
			}}
			QCheckBox {{ color: {t['text_header']}; font-size: 13px; background: transparent; }}
			QCheckBox::indicator {{ width: 16px; height: 16px; }}
			QPushButton {{
				background: {t['button_bg']}; color: white; border: none;
				padding: 6px 14px; border-radius: 6px; font-size: 13px;
			}}
			QPushButton:hover {{ background: {t['button_hover']}; }}
			QPushButton:pressed {{ background: {t['button_press']}; }}
			QDialogButtonBox QPushButton {{ padding: 7px 22px; }}
		""")
