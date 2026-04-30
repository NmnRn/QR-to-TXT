import os
from io import BytesIO

from PySide6.QtWidgets import (
	QApplication,
	QFileDialog,
	QLabel,
	QMainWindow,
	QMessageBox,
	QPushButton,
	QTextEdit,
	QWidget,
	QHBoxLayout,
	QVBoxLayout,
)
from PySide6.QtCore import Qt, QBuffer, QIODevice
from PySide6.QtGui import QKeySequence, QShortcut

from PIL import Image
from pyzbar.pyzbar import decode


def _decode_pil_image(image):
	return [item.data.decode("utf-8", errors="replace") for item in decode(image)]


def decode_qr_from_file(file_path):
	return _decode_pil_image(Image.open(file_path))


class QrToTxtWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("QR to TXT")
		self.resize(820, 540)
		self.setAcceptDrops(True)

		self.output = QTextEdit()
		self.output.setReadOnly(True)
		self.output.setPlaceholderText("QR result will appear here...")

		self._build_ui()
		self._apply_theme()
		self._setup_shortcuts()

	def _build_ui(self):
		header = QLabel("Convert QR to Text")
		header.setObjectName("Header")
		header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

		open_button = QPushButton("Select Image")
		open_button.clicked.connect(self.open_images)

		paste_button = QPushButton("Paste from Clipboard")
		paste_button.clicked.connect(self.paste_from_clipboard)

		save_button = QPushButton("Save as TXT")
		save_button.clicked.connect(self.save_text)

		clear_button = QPushButton("Clear")
		clear_button.clicked.connect(self.clear_output)

		button_row = QHBoxLayout()
		button_row.addWidget(open_button)
		button_row.addWidget(paste_button)
		button_row.addWidget(save_button)
		button_row.addWidget(clear_button)
		button_row.addStretch()

		footer = QLabel("Supported formats: PNG, JPG, JPEG, BMP  •  Drag & drop or Ctrl+V to paste")
		footer.setObjectName("Footer")

		content = QVBoxLayout()
		content.addWidget(header)
		content.addLayout(button_row)
		content.addWidget(self.output)
		content.addWidget(footer)

		container = QWidget()
		container.setLayout(content)
		self.setCentralWidget(container)

	def _setup_shortcuts(self):
		QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(self.paste_from_clipboard)
		QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_images)
		QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_text)

	def _apply_theme(self):
		self.setStyleSheet(
			"""
			QMainWindow {
				background: #0f1115;
			}
			QLabel {
				color: #d7dbe2;
				font-size: 13px;
			}
			QLabel#Header {
				font-size: 20px;
				font-weight: 600;
				margin: 10px 0 6px 0;
			}
			QLabel#Footer {
				color: #8c93a0;
				margin: 6px 0 0 0;
			}
			QPushButton {
				background: #2b6be4;
				color: white;
				border: none;
				padding: 8px 16px;
				border-radius: 8px;
			}
			QPushButton:hover {
				background: #3a7af0;
			}
			QPushButton:pressed {
				background: #245bbf;
			}
			QTextEdit {
				background: #151923;
				color: #e6e9ef;
				border: 1px solid #202636;
				border-radius: 10px;
				padding: 10px;
				font-family: "Consolas";
				font-size: 12px;
			}
			"""
		)

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			urls = event.mimeData().urls()
			if any(u.toLocalFile().lower().endswith((".png", ".jpg", ".jpeg", ".bmp")) for u in urls):
				event.acceptProposedAction()
				return
		event.ignore()

	def dropEvent(self, event):
		paths = [
			u.toLocalFile()
			for u in event.mimeData().urls()
			if u.toLocalFile().lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
		]
		if paths:
			self._process_files(paths)

	def open_images(self):
		file_paths, _ = QFileDialog.getOpenFileNames(
			self,
			"Select QR image(s)",
			"",
			"Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
		)
		if file_paths:
			self._process_files(file_paths)

	def paste_from_clipboard(self):
		qimage = QApplication.clipboard().image()
		if qimage.isNull():
			QMessageBox.information(self, "Info", "No image in clipboard.")
			return

		try:
			buf = QBuffer()
			buf.open(QIODevice.OpenModeFlag.WriteOnly)
			qimage.save(buf, "PNG")
			pil_image = Image.open(BytesIO(bytes(buf.data())))
			pil_image.load()
			texts = _decode_pil_image(pil_image)
		except Exception as exc:
			QMessageBox.critical(self, "Error", str(exc))
			return

		self.output.clear()
		if not texts:
			self.output.setPlainText("No QR code found.")
			return

		self.output.setPlainText("\n".join(f"[{i}] {t}" for i, t in enumerate(texts, 1)))

	def _process_files(self, paths):
		self.output.clear()
		lines = []
		errors = []
		multi = len(paths) > 1

		for path in paths:
			try:
				texts = decode_qr_from_file(path)
			except Exception as exc:
				errors.append(f"{os.path.basename(path)}: {exc}")
				continue

			if multi:
				lines.append(f"=== {os.path.basename(path)} ===")

			if not texts:
				lines.append("No QR code found.")
			else:
				lines.extend(f"[{i}] {t}" for i, t in enumerate(texts, 1))

			if multi:
				lines.append("")

		if errors:
			lines.append("--- Errors ---")
			lines.extend(errors)

		self.output.setPlainText("\n".join(lines).strip())

	def save_text(self):
		content = self.output.toPlainText().strip()
		if not content:
			QMessageBox.information(self, "Info", "No content to save.")
			return

		file_path, _ = QFileDialog.getSaveFileName(
			self,
			"Save as TXT",
			"qr-output.txt",
			"Text Files (*.txt);;All Files (*)",
		)
		if not file_path:
			return

		try:
			with open(file_path, "w", encoding="utf-8") as file_handle:
				file_handle.write(content)
		except Exception as exc:
			QMessageBox.critical(self, "Error", str(exc))
			return

		QMessageBox.information(self, "Success", "File saved.")

	def clear_output(self):
		self.output.clear()


if __name__ == "__main__":
	app = QApplication([])
	window = QrToTxtWindow()
	window.show()
	app.exec()
