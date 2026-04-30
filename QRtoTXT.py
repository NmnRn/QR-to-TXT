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
from PySide6.QtCore import Qt

from PIL import Image
from pyzbar.pyzbar import decode


def decode_qr_from_file(file_path):
	image = Image.open(file_path)
	results = decode(image)
	texts = []
	for item in results:
		try:
			texts.append(item.data.decode("utf-8"))
		except Exception:
			texts.append(item.data.decode("utf-8", errors="replace"))
	return texts


class QrToTxtWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("QR to TXT")
		self.resize(820, 540)

		self.output = QTextEdit()
		self.output.setReadOnly(True)
		self.output.setPlaceholderText("QR result will appear here...")

		self._build_ui()
		self._apply_theme()

	def _build_ui(self):
		header = QLabel("Convert QR to Text")
		header.setObjectName("Header")
		header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

		open_button = QPushButton("Select Image")
		open_button.clicked.connect(self.open_image)

		save_button = QPushButton("Save as TXT")
		save_button.clicked.connect(self.save_text)

		clear_button = QPushButton("Clear")
		clear_button.clicked.connect(self.clear_output)

		button_row = QHBoxLayout()
		button_row.addWidget(open_button)
		button_row.addWidget(save_button)
		button_row.addWidget(clear_button)
		button_row.addStretch()

		footer = QLabel("Supported formats: PNG, JPG, JPEG, BMP")
		footer.setObjectName("Footer")

		content = QVBoxLayout()
		content.addWidget(header)
		content.addLayout(button_row)
		content.addWidget(self.output)
		content.addWidget(footer)

		container = QWidget()
		container.setLayout(content)
		self.setCentralWidget(container)

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

	def open_image(self):
		file_path, _ = QFileDialog.getOpenFileName(
			self,
			"Select QR image",
			"",
			"Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
		)
		if not file_path:
			return

		try:
			texts = decode_qr_from_file(file_path)
		except Exception as exc:
			QMessageBox.critical(self, "Error", str(exc))
			return

		self.output.clear()
		if not texts:
			self.output.setPlainText("No QR code found.")
			return

		self.output.setPlainText("\n".join(f"[{i}] {t}" for i, t in enumerate(texts, 1)))

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
