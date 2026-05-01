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
	QPushButton,
	QSpinBox,
	QWidget,
)


class AppSettings:
	def __init__(self):
		self._s = QSettings("NmnRn", "QRtoTXT")

	@property
	def save_path(self):
		return self._s.value("save_path", os.path.expanduser("~"), type=str)

	@save_path.setter
	def save_path(self, v):
		self._s.setValue("save_path", v)

	@property
	def history_limit(self):
		return self._s.value("history_limit", 50, type=int)

	@history_limit.setter
	def history_limit(self, v):
		self._s.setValue("history_limit", v)

	@property
	def theme(self):
		return self._s.value("theme", "Dark", type=str)

	@theme.setter
	def theme(self, v):
		self._s.setValue("theme", v)

	@property
	def minimize_to_tray(self):
		return self._s.value("minimize_to_tray", False, type=bool)

	@minimize_to_tray.setter
	def minimize_to_tray(self, v):
		self._s.setValue("minimize_to_tray", v)

	@property
	def check_updates(self):
		return self._s.value("check_updates", True, type=bool)

	@check_updates.setter
	def check_updates(self, v):
		self._s.setValue("check_updates", v)


class SettingsDialog(QDialog):
	def __init__(self, settings: AppSettings, parent=None):
		super().__init__(parent)
		self._settings = settings
		self.setWindowTitle("Settings")
		self.setMinimumWidth(420)
		self._build_ui()
		self._apply_theme()

	def _build_ui(self):
		layout = QFormLayout()
		layout.setContentsMargins(24, 24, 24, 24)
		layout.setSpacing(16)

		# Theme
		from .themes import THEME_NAMES
		self._theme_combo = QComboBox()
		self._theme_combo.addItems(THEME_NAMES)
		current_idx = THEME_NAMES.index(self._settings.theme) if self._settings.theme in THEME_NAMES else 0
		self._theme_combo.setCurrentIndex(current_idx)
		layout.addRow("Theme:", self._theme_combo)

		# Default save folder
		row = QWidget()
		hl = QHBoxLayout(row)
		hl.setContentsMargins(0, 0, 0, 0)
		self._path_edit = QLineEdit(self._settings.save_path)
		browse_btn = QPushButton("Browse")
		browse_btn.clicked.connect(self._browse)
		hl.addWidget(self._path_edit)
		hl.addWidget(browse_btn)
		layout.addRow("Default save folder:", row)

		# History limit
		self._history_spin = QSpinBox()
		self._history_spin.setRange(10, 500)
		self._history_spin.setValue(self._settings.history_limit)
		layout.addRow("History limit (entries):", self._history_spin)

		# Minimize to tray
		self._tray_check = QCheckBox()
		self._tray_check.setChecked(self._settings.minimize_to_tray)
		layout.addRow("Minimize to system tray:", self._tray_check)

		# Check updates
		self._update_check = QCheckBox()
		self._update_check.setChecked(self._settings.check_updates)
		layout.addRow("Check for updates on start:", self._update_check)

		btns = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		)
		btns.accepted.connect(self._save)
		btns.rejected.connect(self.reject)
		layout.addRow(btns)

		self.setLayout(layout)

	def _browse(self):
		path = QFileDialog.getExistingDirectory(
			self, "Select default save folder", self._settings.save_path
		)
		if path:
			self._path_edit.setText(path)

	def _save(self):
		self._settings.theme = self._theme_combo.currentText()
		self._settings.save_path = self._path_edit.text()
		self._settings.history_limit = self._history_spin.value()
		self._settings.minimize_to_tray = self._tray_check.isChecked()
		self._settings.check_updates = self._update_check.isChecked()
		self.accept()

	def _apply_theme(self):
		self.setStyleSheet("""
			QDialog { background: #0f1115; }
			QLabel { color: #d7dbe2; font-size: 13px; }
			QLineEdit, QSpinBox {
				background: #151923; color: #e6e9ef;
				border: 1px solid #202636; border-radius: 6px;
				padding: 6px 8px; font-size: 13px;
			}
			QCheckBox { color: #d7dbe2; font-size: 13px; }
			QCheckBox::indicator { width: 16px; height: 16px; }
			QPushButton {
				background: #2b6be4; color: white; border: none;
				padding: 6px 14px; border-radius: 6px; font-size: 13px;
			}
			QPushButton:hover { background: #3a7af0; }
			QDialogButtonBox QPushButton { padding: 7px 22px; }
		""")
