import os
import sys

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .settings import AppSettings
from .tray import AppTray
from .updater import check_for_update
from .window import QrToTxtWindow


class _UpdateBridge(QObject):
	found = Signal(str)


def main():
	app = QApplication(sys.argv)
	app.setQuitOnLastWindowClosed(False)

	settings = AppSettings()

	icon_path = os.path.normpath(
		os.path.join(os.path.dirname(__file__), "..", "..", "icon", "qrtotxt.png")
	)
	icon = QIcon(icon_path) if os.path.isfile(icon_path) else QIcon()

	window = QrToTxtWindow(settings)
	if not icon.isNull():
		window.setWindowIcon(icon)

	tray = AppTray(icon, window)
	window.set_tray(tray)

	bridge = _UpdateBridge(app)
	bridge.found.connect(
		lambda v: window.statusBar().showMessage(
			f"Update available: v{v}  —  visit github.com/NmnRn/QR-to-TXT to download", 0
		)
	)
	if settings.check_updates:
		check_for_update(bridge.found.emit)

	window.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
