from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


class AppTray(QSystemTrayIcon):
	def __init__(self, icon, window):
		super().__init__(icon, window)
		self._window = window

		menu = QMenu()
		show_action = QAction("Show", menu)
		show_action.triggered.connect(self._show)
		quit_action = QAction("Quit", menu)
		quit_action.triggered.connect(QApplication.quit)
		menu.addAction(show_action)
		menu.addSeparator()
		menu.addAction(quit_action)

		self.setContextMenu(menu)
		self.setToolTip("QR to TXT")
		self.activated.connect(self._on_activated)
		self.show()

	def _show(self):
		self._window.showNormal()
		self._window.activateWindow()
		self._window.raise_()

	def _on_activated(self, reason):
		if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
			self._show()
