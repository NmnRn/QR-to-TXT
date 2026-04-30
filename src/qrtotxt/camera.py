from PIL import Image
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

try:
	import cv2
	CAMERA_AVAILABLE = True
except ImportError:
	CAMERA_AVAILABLE = False


class CameraDialog(QDialog):
	qr_detected = Signal(list)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Scan from Camera")
		self.resize(680, 560)
		self._cap = None
		self._timer = None
		self._last_texts = None
		self._build_ui()
		self._apply_theme()
		self._start()

	def _build_ui(self):
		self._preview = QLabel("Starting camera…")
		self._preview.setAlignment(Qt.AlignCenter)
		self._preview.setMinimumSize(640, 480)

		self._status = QLabel("Point camera at a QR code")
		self._status.setObjectName("Status")
		self._status.setAlignment(Qt.AlignCenter)

		close_btn = QPushButton("Close")
		close_btn.clicked.connect(self.reject)

		layout = QVBoxLayout()
		layout.setContentsMargins(10, 10, 10, 10)
		layout.setSpacing(8)
		layout.addWidget(self._preview)
		layout.addWidget(self._status)
		layout.addWidget(close_btn)
		self.setLayout(layout)

	def _apply_theme(self):
		self.setStyleSheet("""
			QDialog { background: #0f1115; }
			QLabel { color: #d7dbe2; font-size: 13px; }
			QLabel#Status { color: #8c93a0; }
			QPushButton {
				background: #2b6be4; color: white; border: none;
				padding: 8px 16px; border-radius: 8px;
			}
			QPushButton:hover { background: #3a7af0; }
		""")

	def _start(self):
		if not CAMERA_AVAILABLE:
			self._status.setText("opencv-python-headless is not installed.")
			return
		self._cap = cv2.VideoCapture(0)
		if not self._cap.isOpened():
			self._status.setText("No camera found.")
			return
		self._timer = QTimer(self)
		self._timer.timeout.connect(self._read_frame)
		self._timer.start(33)  # ~30 fps

	def _read_frame(self):
		ret, frame = self._cap.read()
		if not ret:
			return

		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		pil = Image.fromarray(rgb)

		from .decoder import _decode_pil_image
		texts = _decode_pil_image(pil)

		if texts and texts != self._last_texts:
			self._last_texts = texts
			self.qr_detected.emit(texts)
			self._stop()
			self.accept()
			return

		h, w, ch = rgb.shape
		qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
		self._preview.setPixmap(
			QPixmap.fromImage(qimg).scaled(
				self._preview.width(), self._preview.height(),
				Qt.KeepAspectRatio, Qt.SmoothTransformation,
			)
		)

	def _stop(self):
		if self._timer:
			self._timer.stop()
		if self._cap:
			self._cap.release()
			self._cap = None

	def closeEvent(self, event):
		self._stop()
		super().closeEvent(event)

	def reject(self):
		self._stop()
		super().reject()
