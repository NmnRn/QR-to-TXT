from PIL import Image
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

try:
	import importlib.util
	CAMERA_AVAILABLE = importlib.util.find_spec("cv2") is not None
except Exception:
	CAMERA_AVAILABLE = False


class CameraDialog(QDialog):
	qr_detected = Signal(list)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Scan from Camera")
		self.resize(680, 580)
		self._cap = None
		self._timer = None
		self._last_texts = None
		self._confirm_texts = None
		self._confirm_count = 0
		self._mirror = True
		self._build_ui()
		self._apply_theme()
		self._start()

	def _build_ui(self):
		self._preview = QLabel("Starting camera…")
		self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self._preview.setMinimumSize(640, 480)

		self._status = QLabel("Point camera at a QR code")
		self._status.setObjectName("Status")
		self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self._mirror_btn = QPushButton("Mirror: ON")
		self._mirror_btn.setCheckable(True)
		self._mirror_btn.setChecked(True)
		self._mirror_btn.clicked.connect(self._toggle_mirror)

		close_btn = QPushButton("Close")
		close_btn.clicked.connect(self.reject)

		btn_row = QHBoxLayout()
		btn_row.addWidget(self._mirror_btn)
		btn_row.addStretch()
		btn_row.addWidget(close_btn)

		layout = QVBoxLayout()
		layout.setContentsMargins(10, 10, 10, 10)
		layout.setSpacing(8)
		layout.addWidget(self._preview)
		layout.addWidget(self._status)
		layout.addLayout(btn_row)
		self.setLayout(layout)

	def _toggle_mirror(self, checked):
		self._mirror = checked
		self._mirror_btn.setText("Mirror: ON" if checked else "Mirror: OFF")

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
			QPushButton:checked { background: #245bbf; }
		""")

	def _start(self):
		if not CAMERA_AVAILABLE:
			self._status.setText("opencv-python-headless is not installed.")
			return
		import cv2 as _cv2
		self._cv2 = _cv2
		self._cap = self._cv2.VideoCapture(0)
		if not self._cap.isOpened():
			self._status.setText("No camera found.")
			return
		self._timer = QTimer(self)
		self._timer.timeout.connect(self._read_frame)
		self._timer.start(33)  # ~30 fps

	def _read_frame(self):
		if self._cap is None:
			return
		ret, frame = self._cap.read()
		if not ret:
			return

		rgb = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)

		from .decoder import _decode_pil_image
		texts = _decode_pil_image(Image.fromarray(rgb))

		if texts:
			if texts == self._confirm_texts:
				self._confirm_count += 1
			else:
				self._confirm_texts = texts
				self._confirm_count = 1

			self._status.setText(f"Locking… ({self._confirm_count}/3)")

			if self._confirm_count >= 3:
				self._last_texts = texts
				self.qr_detected.emit(texts)
				self._stop()
				self.accept()
				return
		else:
			self._confirm_texts = None
			self._confirm_count = 0
			self._status.setText("Point camera at a QR code")

		display = self._cv2.flip(rgb, 1) if self._mirror else rgb
		h, w, ch = display.shape
		qimg = QImage(display.data, w, h, ch * w, QImage.Format.Format_RGB888)
		self._preview.setPixmap(
			QPixmap.fromImage(qimg).scaled(
				self._preview.width(), self._preview.height(),
				Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
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
