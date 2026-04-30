import csv
import html
import json
import os
import re
from datetime import datetime
from io import BytesIO

from PySide6.QtCore import Qt, QBuffer, QIODevice
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
	QApplication,
	QDialog,
	QDialogButtonBox,
	QFileDialog,
	QHBoxLayout,
	QLabel,
	QListWidget,
	QListWidgetItem,
	QMainWindow,
	QMessageBox,
	QPushButton,
	QTextBrowser,
	QVBoxLayout,
	QWidget,
)
from PIL import Image

from .camera import CAMERA_AVAILABLE, CameraDialog
from .decoder import _decode_pil_image, decode_qr_from_file
from .settings import AppSettings, SettingsDialog

_URL_RE = re.compile(r"https?://[^\s<>\"']+")


def _linkify(plain: str) -> str:
	escaped = html.escape(plain)
	return _URL_RE.sub(
		lambda m: f'<a href="{m.group()}" style="color:#6ab0f5;">{m.group()}</a>',
		escaped,
	)


# ── History dialog ────────────────────────────────────────────────────────────

class HistoryDialog(QDialog):
	def __init__(self, history: list, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Session History")
		self.resize(640, 420)

		self._list = QListWidget()
		for entry in reversed(history):
			preview = entry["texts"][0][:60] if entry["texts"] else "(no QR)"
			item = QListWidgetItem(f"[{entry['timestamp']}]  {entry['source']}  →  {preview}")
			item.setData(Qt.ItemDataRole.UserRole, entry)
			self._list.addItem(item)

		self._detail = QTextBrowser()
		self._detail.setOpenExternalLinks(True)
		self._list.currentItemChanged.connect(self._show_detail)

		close_btn = QPushButton("Close")
		close_btn.clicked.connect(self.accept)

		layout = QVBoxLayout()
		layout.setContentsMargins(12, 12, 12, 12)
		layout.setSpacing(8)
		layout.addWidget(QLabel("Click an entry to see full results:"))
		layout.addWidget(self._list, 2)
		layout.addWidget(self._detail, 1)
		layout.addWidget(close_btn)
		self.setLayout(layout)
		self._apply_theme()

	def _show_detail(self, item):
		if not item:
			return
		entry = item.data(Qt.ItemDataRole.UserRole)
		lines = [f"Source:    {entry['source']}", f"Time:      {entry['timestamp']}", ""]
		if entry["texts"]:
			lines.extend(f"[{i}] {t}" for i, t in enumerate(entry["texts"], 1))
		else:
			lines.append("No QR code found.")
		self._detail.setPlainText("\n".join(lines))

	def _apply_theme(self):
		self.setStyleSheet("""
			QDialog { background: #0f1115; }
			QLabel { color: #d7dbe2; font-size: 13px; }
			QListWidget {
				background: #151923; color: #e6e9ef;
				border: 1px solid #202636; border-radius: 8px; font-size: 12px;
			}
			QListWidget::item:selected { background: #2b6be4; color: white; }
			QTextBrowser {
				background: #151923; color: #e6e9ef;
				border: 1px solid #202636; border-radius: 8px;
				padding: 8px; font-family: Consolas; font-size: 12px;
			}
			QPushButton {
				background: #2b6be4; color: white; border: none;
				padding: 8px 16px; border-radius: 8px;
			}
			QPushButton:hover { background: #3a7af0; }
		""")


# ── Main window ───────────────────────────────────────────────────────────────

class QrToTxtWindow(QMainWindow):
	def __init__(self, settings: AppSettings):
		super().__init__()
		self._settings = settings
		self._results: list[dict] = []
		self._history: list[dict] = []

		self.setWindowTitle("QR to TXT")
		self.resize(920, 600)
		self.setAcceptDrops(True)

		self._output = QTextBrowser()
		self._output.setOpenExternalLinks(True)
		self._output.setPlaceholderText("QR result will appear here…")

		self._build_ui()
		self._build_menu()
		self._apply_theme()
		self._setup_shortcuts()

	# ── Menu ──────────────────────────────────────────────────────────────────

	def _build_menu(self):
		mb = self.menuBar()

		file_menu = mb.addMenu("File")
		file_menu.addAction("Open Image(s)   Ctrl+O", self.open_images)
		file_menu.addAction("Open Folder", self.open_folder)
		file_menu.addAction("Open PDF", self.open_pdf)
		file_menu.addSeparator()
		cam_act = file_menu.addAction("Scan Camera", self.scan_camera)
		if not CAMERA_AVAILABLE:
			cam_act.setEnabled(False)
		file_menu.addAction("Paste from Clipboard   Ctrl+V", self.paste_from_clipboard)
		file_menu.addSeparator()
		file_menu.addAction("Save as TXT   Ctrl+S", self.save_txt)
		file_menu.addAction("Save as CSV", self.save_csv)
		file_menu.addAction("Save as JSON", self.save_json)
		file_menu.addSeparator()
		file_menu.addAction("Exit", self.close)

		edit_menu = mb.addMenu("Edit")
		edit_menu.addAction("Copy All   Ctrl+Shift+C", self.copy_to_clipboard)
		edit_menu.addAction("Clear", self.clear_output)
		edit_menu.addSeparator()
		edit_menu.addAction("Settings", self.open_settings)

		help_menu = mb.addMenu("Help")
		help_menu.addAction("Session History", self.show_history)
		help_menu.addAction("Check for Updates", self.manual_update_check)

	# ── UI layout ─────────────────────────────────────────────────────────────

	def _build_ui(self):
		open_btn   = QPushButton("Open Image(s)")
		folder_btn = QPushButton("Open Folder")
		pdf_btn    = QPushButton("Open PDF")
		cam_btn    = QPushButton("Scan Camera")
		paste_btn  = QPushButton("Paste")
		copy_btn   = QPushButton("Copy All")
		save_btn   = QPushButton("Save TXT")
		clear_btn  = QPushButton("Clear")

		if not CAMERA_AVAILABLE:
			cam_btn.setEnabled(False)
			cam_btn.setToolTip("Install opencv-python-headless to enable")

		open_btn.clicked.connect(self.open_images)
		folder_btn.clicked.connect(self.open_folder)
		pdf_btn.clicked.connect(self.open_pdf)
		cam_btn.clicked.connect(self.scan_camera)
		paste_btn.clicked.connect(self.paste_from_clipboard)
		copy_btn.clicked.connect(self.copy_to_clipboard)
		save_btn.clicked.connect(self.save_txt)
		clear_btn.clicked.connect(self.clear_output)

		btn_row = QHBoxLayout()
		for btn in (open_btn, folder_btn, pdf_btn, cam_btn, paste_btn):
			btn_row.addWidget(btn)
		btn_row.addStretch()
		for btn in (copy_btn, save_btn, clear_btn):
			btn_row.addWidget(btn)

		self._status_label = QLabel("Ready")
		self._status_label.setObjectName("Footer")

		layout = QVBoxLayout()
		layout.setContentsMargins(12, 8, 12, 8)
		layout.setSpacing(8)
		layout.addLayout(btn_row)
		layout.addWidget(self._output)
		layout.addWidget(self._status_label)

		container = QWidget()
		container.setLayout(layout)
		self.setCentralWidget(container)

	def _setup_shortcuts(self):
		QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_images)
		QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(self.paste_from_clipboard)
		QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_txt)
		QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.copy_to_clipboard)

	def _apply_theme(self):
		self.setStyleSheet("""
			QMainWindow, QWidget { background: #0f1115; }
			QMenuBar { background: #0f1115; color: #d7dbe2; font-size: 13px; padding: 2px; }
			QMenuBar::item:selected { background: #202636; border-radius: 4px; }
			QMenu { background: #151923; color: #d7dbe2; border: 1px solid #202636; }
			QMenu::item:selected { background: #2b6be4; }
			QLabel { color: #d7dbe2; font-size: 13px; }
			QLabel#Footer { color: #8c93a0; font-size: 12px; margin-top: 2px; }
			QPushButton {
				background: #2b6be4; color: white; border: none;
				padding: 7px 13px; border-radius: 8px; font-size: 13px;
			}
			QPushButton:hover { background: #3a7af0; }
			QPushButton:pressed { background: #245bbf; }
			QPushButton:disabled { background: #1e2433; color: #555e72; }
			QTextBrowser {
				background: #151923; color: #e6e9ef;
				border: 1px solid #202636; border-radius: 10px;
				padding: 10px; font-family: Consolas,monospace; font-size: 12px;
			}
			QStatusBar { background: #0f1115; color: #8c93a0; font-size: 12px; }
		""")

	# ── Drag & drop ───────────────────────────────────────────────────────────

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			if any(
				u.toLocalFile().lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".pdf"))
				for u in event.mimeData().urls()
			):
				event.acceptProposedAction()
				return
		event.ignore()

	def dropEvent(self, event):
		imgs, pdfs = [], []
		for u in event.mimeData().urls():
			p = u.toLocalFile()
			if p.lower().endswith(".pdf"):
				pdfs.append(p)
			elif p.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
				imgs.append(p)
		if imgs:
			self._process_files(imgs)
		for p in pdfs:
			self._process_pdf(p)

	# ── Open actions ──────────────────────────────────────────────────────────

	def open_images(self):
		paths, _ = QFileDialog.getOpenFileNames(
			self, "Select QR image(s)", self._settings.save_path,
			"Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
		)
		if paths:
			self._process_files(paths)

	def open_folder(self):
		folder = QFileDialog.getExistingDirectory(
			self, "Select folder", self._settings.save_path
		)
		if not folder:
			return
		exts = {".png", ".jpg", ".jpeg", ".bmp"}
		paths = sorted(
			os.path.join(folder, f)
			for f in os.listdir(folder)
			if os.path.splitext(f)[1].lower() in exts
		)
		if not paths:
			QMessageBox.information(self, "Info", "No image files found in that folder.")
			return
		self._process_files(paths)

	def open_pdf(self):
		path, _ = QFileDialog.getOpenFileName(
			self, "Select PDF", self._settings.save_path,
			"PDF Files (*.pdf);;All Files (*)",
		)
		if path:
			self._process_pdf(path)

	def scan_camera(self):
		dlg = CameraDialog(self)
		dlg.qr_detected.connect(lambda texts: self._add_result("camera", texts))
		dlg.exec()

	def paste_from_clipboard(self):
		qimage = QApplication.clipboard().image()
		if qimage.isNull():
			QMessageBox.information(self, "Info", "No image in clipboard.")
			return
		try:
			buf = QBuffer()
			buf.open(QIODevice.OpenModeFlag.WriteOnly)
			qimage.save(buf, "PNG")
			pil = Image.open(BytesIO(bytes(buf.data())))
			pil.load()
			texts = _decode_pil_image(pil)
		except Exception as exc:
			QMessageBox.critical(self, "Error", str(exc))
			return
		self._add_result("clipboard", texts)

	# ── Process helpers ───────────────────────────────────────────────────────

	def _process_files(self, paths: list[str]):
		errors = []
		for path in paths:
			try:
				self._add_result(os.path.basename(path), decode_qr_from_file(path))
			except Exception as exc:
				errors.append(f"{os.path.basename(path)}: {exc}")
		if errors:
			QMessageBox.warning(self, "Errors", "\n".join(errors))

	def _process_pdf(self, path: str):
		try:
			from .decoder import decode_qr_from_pdf
			pages = decode_qr_from_pdf(path)
		except ImportError:
			QMessageBox.critical(
				self, "Missing package",
				"PDF support requires pymupdf:\n\npip install pymupdf",
			)
			return
		except Exception as exc:
			QMessageBox.critical(self, "Error", str(exc))
			return
		name = os.path.basename(path)
		for page_num, texts in pages:
			self._add_result(f"{name} — page {page_num}", texts)

	def _add_result(self, source: str, texts: list[str]):
		entry = {
			"source": source,
			"texts": texts,
			"timestamp": datetime.now().strftime("%H:%M:%S"),
		}
		self._results.append(entry)
		self._history.append(entry)
		if len(self._history) > self._settings.history_limit:
			self._history = self._history[-self._settings.history_limit :]
		self._render()
		total = sum(len(e["texts"]) for e in self._results)
		self._status_label.setText(
			f"{len(self._results)} source(s) · {total} QR code(s) decoded"
		)

	# ── Rendering ─────────────────────────────────────────────────────────────

	def _render(self):
		if not self._results:
			self._output.clear()
			return
		parts = []
		for entry in self._results:
			src = html.escape(entry["source"])
			ts  = html.escape(entry["timestamp"])
			parts.append(
				f'<p style="color:#8c93a0;margin:10px 0 2px 0;">'
				f'<b>=== {src} ===</b>'
				f'<span style="font-weight:normal;font-size:11px;color:#555e72;"> {ts}</span></p>'
			)
			if not entry["texts"]:
				parts.append(
					'<p style="color:#555e72;margin:1px 0 4px 0;">'
					'&nbsp;&nbsp;No QR code found.</p>'
				)
			else:
				for i, text in enumerate(entry["texts"], 1):
					parts.append(
						f'<p style="color:#e6e9ef;margin:1px 0;">'
						f'&nbsp;&nbsp;[{i}] {_linkify(text)}</p>'
					)
		self._output.setHtml(
			'<html><body style="background:#151923;color:#e6e9ef;'
			'font-family:Consolas,monospace;font-size:12px;margin:10px;">'
			+ "".join(parts)
			+ "</body></html>"
		)

	def _plain_text(self) -> str:
		lines = []
		for entry in self._results:
			lines.append(f"=== {entry['source']} ===")
			if entry["texts"]:
				lines.extend(f"[{i}] {t}" for i, t in enumerate(entry["texts"], 1))
			else:
				lines.append("No QR code found.")
			lines.append("")
		return "\n".join(lines).strip()

	# ── Clear ─────────────────────────────────────────────────────────────────

	def clear_output(self):
		self._results.clear()
		self._output.clear()
		self._status_label.setText("Ready")

	# ── Export ────────────────────────────────────────────────────────────────

	def save_txt(self):
		text = self._plain_text()
		if not text:
			QMessageBox.information(self, "Info", "No content to save.")
			return
		path, _ = QFileDialog.getSaveFileName(
			self, "Save as TXT",
			os.path.join(self._settings.save_path, "qr-output.txt"),
			"Text Files (*.txt);;All Files (*)",
		)
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(text)
			QMessageBox.information(self, "Saved", "File saved.")
		except Exception as exc:
			QMessageBox.critical(self, "Error", str(exc))

	def save_csv(self):
		if not self._results:
			QMessageBox.information(self, "Info", "No content to save.")
			return
		path, _ = QFileDialog.getSaveFileName(
			self, "Save as CSV",
			os.path.join(self._settings.save_path, "qr-output.csv"),
			"CSV Files (*.csv);;All Files (*)",
		)
		if not path:
			return
		try:
			with open(path, "w", newline="", encoding="utf-8") as f:
				w = csv.writer(f)
				w.writerow(["source", "index", "text", "timestamp"])
				for entry in self._results:
					if entry["texts"]:
						for i, text in enumerate(entry["texts"], 1):
							w.writerow([entry["source"], i, text, entry["timestamp"]])
					else:
						w.writerow([entry["source"], "", "", entry["timestamp"]])
			QMessageBox.information(self, "Saved", "CSV saved.")
		except Exception as exc:
			QMessageBox.critical(self, "Error", str(exc))

	def save_json(self):
		if not self._results:
			QMessageBox.information(self, "Info", "No content to save.")
			return
		path, _ = QFileDialog.getSaveFileName(
			self, "Save as JSON",
			os.path.join(self._settings.save_path, "qr-output.json"),
			"JSON Files (*.json);;All Files (*)",
		)
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				json.dump(self._results, f, ensure_ascii=False, indent=2)
			QMessageBox.information(self, "Saved", "JSON saved.")
		except Exception as exc:
			QMessageBox.critical(self, "Error", str(exc))

	def copy_to_clipboard(self):
		text = self._plain_text()
		if not text:
			QMessageBox.information(self, "Info", "No content to copy.")
			return
		QApplication.clipboard().setText(text)
		self._status_label.setText("Copied to clipboard.")

	# ── Settings & history ────────────────────────────────────────────────────

	def open_settings(self):
		SettingsDialog(self._settings, self).exec()

	def show_history(self):
		if not self._history:
			QMessageBox.information(self, "History", "No history yet in this session.")
			return
		HistoryDialog(self._history, self).exec()

	# ── Update ────────────────────────────────────────────────────────────────

	def manual_update_check(self):
		from .updater import CURRENT_VERSION, check_for_update

		self._update_result = None

		def found(v):
			self._update_result = v

		# Run synchronously for manual check (give it a moment)
		import threading, time
		t = threading.Thread(target=lambda: found(_sync_latest()))
		t.start()
		t.join(timeout=7)
		if self._update_result:
			QMessageBox.information(
				self, "Update available",
				f"New version v{self._update_result} is available.\n"
				"Visit github.com/NmnRn/QR-to-TXT to download.",
			)
		else:
			QMessageBox.information(
				self, "Up to date",
				f"You are running the latest version (v{CURRENT_VERSION}).",
			)

	# ── Tray / close ─────────────────────────────────────────────────────────

	def set_tray(self, tray):
		self._tray = tray

	def closeEvent(self, event):
		if getattr(self, "_tray", None) and self._settings.minimize_to_tray:
			event.ignore()
			self.hide()
			self._tray.showMessage(
				"QR to TXT", "Running in the background.", 2000
			)
		else:
			event.accept()


def _sync_latest() -> str | None:
	"""Blocking version of update check used for manual checks."""
	import json, urllib.request
	try:
		url = "https://api.github.com/repos/NmnRn/QR-to-TXT/releases/latest"
		req = urllib.request.Request(url, headers={"User-Agent": "QRtoTXT-updater"})
		with urllib.request.urlopen(req, timeout=6) as resp:
			data = json.loads(resp.read())
		from .updater import CURRENT_VERSION, _is_newer
		tag = data.get("tag_name", "").lstrip("v")
		return tag if tag and _is_newer(tag, CURRENT_VERSION) else None
	except Exception:
		return None
