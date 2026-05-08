import csv
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from io import BytesIO

from PySide6.QtCore import Qt, QBuffer, QIODevice
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
	QApplication,
	QDialog,
	QDialogButtonBox,
	QFileDialog,
	QFrame,
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
from .db import AppDB
from .decoder import _decode_pil_image, decode_qr_from_file
from .generator import GeneratorDialog
from .i18n import tr
from .settings import AppSettings, SettingsDialog
from .themes import build_stylesheet

_URL_RE = re.compile(r"https?://[^\s<>\"']+")


class _FileDlg(QFileDialog):
    """QFileDialog with a blank stylesheet so system colours are used."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setStyleSheet("")

# QR Codes auto-save directory
_QR_DIR = os.path.join(os.path.expanduser("~"), "QR Codes")


def _linkify(plain: str, link_color: str = "#6ab0f5") -> str:
	escaped = html.escape(plain)
	return _URL_RE.sub(
		lambda m: f'<a href="{m.group()}" style="color:{link_color};">{m.group()}</a>',
		escaped,
	)


# ── History dialog ─────────────────────────────────────────────────────────────

class HistoryDialog(QDialog):
	def __init__(self, history: list, settings: AppSettings, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._settings = settings
		self.setWindowTitle(tr("dlg_history_title"))
		self.resize(660, 440)

		self._list = QListWidget()
		for entry in reversed(history):
			preview = entry["texts"][0][:60] if entry["texts"] else tr("hist_no_qr")
			item = QListWidgetItem(f"[{entry['timestamp']}]  {entry['source']}  →  {preview}")
			item.setData(Qt.ItemDataRole.UserRole, entry)
			self._list.addItem(item)

		self._detail = QTextBrowser()
		self._detail.setOpenExternalLinks(True)
		self._list.currentItemChanged.connect(self._show_detail)

		close_btn = QPushButton(tr("btn_close"))
		close_btn.clicked.connect(self.accept)

		layout = QVBoxLayout()
		layout.setContentsMargins(14, 14, 14, 14)
		layout.setSpacing(8)
		layout.addWidget(QLabel(tr("dlg_history_hint")))
		layout.addWidget(self._list, 2)
		layout.addWidget(self._detail, 1)
		layout.addWidget(close_btn)
		self.setLayout(layout)
		self._apply_theme()

	def _show_detail(self, item: QListWidgetItem | None) -> None:
		if not item:
			return
		entry = item.data(Qt.ItemDataRole.UserRole)
		lines = [
			tr("hist_source").format(source=entry["source"]),
			tr("hist_time").format(time=entry["timestamp"]),
			"",
		]
		if entry["texts"]:
			lines.extend(f"[{i}] {t}" for i, t in enumerate(entry["texts"], 1))
		else:
			lines.append(tr("hist_no_qr_found"))
		self._detail.setPlainText("\n".join(lines))

	def _apply_theme(self) -> None:
		from .themes import THEMES
		t = THEMES.get(self._settings.theme, THEMES["Dark"])
		self.setStyleSheet(f"""
			QDialog {{ background: {t['window_bg']}; }}
			QLabel {{ color: {t['text_header']}; font-size: 13px; background: transparent; }}
			QListWidget {{
				background: {t['widget_bg']}; color: {t['text']};
				border: 1px solid {t['border']}; border-radius: 8px; font-size: 12px;
			}}
			QListWidget::item:selected {{ background: {t['list_sel']}; color: white; }}
			QTextBrowser {{
				background: {t['widget_bg']}; color: {t['text']};
				border: 1px solid {t['border']}; border-radius: 8px;
				padding: 8px; font-family: Consolas; font-size: 12px;
			}}
			QPushButton {{
				background: {t['button_bg']}; color: white; border: none;
				padding: 8px 16px; border-radius: 8px;
			}}
			QPushButton:hover {{ background: {t['button_hover']}; }}
			QPushButton:pressed {{ background: {t['button_press']}; }}
		""")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _sep() -> QFrame:
	"""Thin vertical separator line for the toolbar."""
	line = QFrame()
	line.setFrameShape(QFrame.Shape.VLine)
	line.setObjectName("Separator")
	return line


def _make_btn(label: str, tooltip: str = "") -> QPushButton:
	btn = QPushButton(label)
	if tooltip:
		btn.setToolTip(tooltip)
	return btn


# ── Main window ────────────────────────────────────────────────────────────────

class QrToTxtWindow(QMainWindow):
	def __init__(self, settings: AppSettings) -> None:
		super().__init__()
		self._settings = settings
		self._results: list[dict] = []
		self._history: list[dict] = []

		self.setWindowTitle(tr("tray_tooltip"))
		self.resize(980, 640)
		self.setAcceptDrops(True)

		self._output = QTextBrowser()
		self._output.setOpenExternalLinks(True)
		self._output.setPlaceholderText(tr("placeholder_output"))

		self._build_ui()
		self._build_menu()
		self._apply_current_theme()
		self._setup_shortcuts()

	# ── Menu ──────────────────────────────────────────────────────────────────

	def _build_menu(self) -> None:
		mb = self.menuBar()

		file_menu = mb.addMenu(tr("menu_file"))
		file_menu.addAction(tr("menu_open_images") + tr("sc_open_images"), self.open_images)
		file_menu.addAction(tr("menu_open_folder"), self.open_folder)
		file_menu.addAction(tr("menu_open_pdf"), self.open_pdf)
		file_menu.addSeparator()
		cam_act = file_menu.addAction(tr("menu_scan_camera"), self.scan_camera)
		if not CAMERA_AVAILABLE:
			cam_act.setEnabled(False)
		file_menu.addAction(tr("menu_paste") + tr("sc_paste"), self.paste_from_clipboard)
		file_menu.addSeparator()
		file_menu.addAction(tr("menu_save_txt") + tr("sc_save_txt"), self.save_txt)
		file_menu.addAction(tr("menu_save_csv"), self.save_csv)
		file_menu.addAction(tr("menu_save_json"), self.save_json)
		file_menu.addSeparator()
		file_menu.addAction(tr("menu_exit"), self.close)

		tools_menu = mb.addMenu(tr("menu_tools"))
		tools_menu.addAction(tr("menu_generate_qr"), self.open_generator)

		edit_menu = mb.addMenu(tr("menu_edit"))
		edit_menu.addAction(tr("menu_copy_all") + tr("sc_copy_all"), self.copy_to_clipboard)
		edit_menu.addAction(tr("menu_clear"), self.clear_output)
		edit_menu.addSeparator()
		edit_menu.addAction(tr("menu_settings"), self.open_settings)

		help_menu = mb.addMenu(tr("menu_help"))
		help_menu.addAction(tr("menu_history"), self.show_history)
		help_menu.addSeparator()
		help_menu.addAction(tr("menu_upgrade"), self.upgrade_app)
		help_menu.addAction(tr("menu_check_updates"), self.manual_update_check)
		help_menu.addSeparator()
		help_menu.addAction(tr("menu_version"), self.show_version)

	# ── UI layout ─────────────────────────────────────────────────────────────

	def _build_ui(self) -> None:
		# ── Top toolbar: import sources ───────────────────────────────────────
		open_btn   = _make_btn(tr("btn_open_images"), tr("tip_open_images"))
		folder_btn = _make_btn(tr("btn_open_folder"),  tr("tip_open_folder"))
		pdf_btn    = _make_btn(tr("btn_open_pdf"),     tr("tip_open_pdf"))
		cam_btn    = _make_btn(tr("btn_scan_camera"),  tr("tip_scan_camera"))
		paste_btn  = _make_btn(tr("btn_paste"),        tr("tip_paste"))
		gen_btn    = _make_btn(tr("btn_generate_qr"),  tr("tip_generate_qr"))
		gen_btn.setObjectName("GenBtn")

		if not CAMERA_AVAILABLE:
			cam_btn.setEnabled(False)
			cam_btn.setToolTip("Install opencv-python-headless to enable")

		open_btn.clicked.connect(self.open_images)
		folder_btn.clicked.connect(self.open_folder)
		pdf_btn.clicked.connect(self.open_pdf)
		cam_btn.clicked.connect(self.scan_camera)
		paste_btn.clicked.connect(self.paste_from_clipboard)
		gen_btn.clicked.connect(self.open_generator)

		top_bar = QHBoxLayout()
		top_bar.setSpacing(6)
		top_bar.setContentsMargins(0, 0, 0, 0)
		for btn in (open_btn, folder_btn, pdf_btn, cam_btn, paste_btn):
			top_bar.addWidget(btn)
		top_bar.addWidget(_sep())
		top_bar.addWidget(gen_btn)
		top_bar.addStretch()

		# ── Bottom toolbar: export actions ────────────────────────────────────
		copy_btn  = _make_btn(tr("btn_copy_all"), tr("tip_copy_all"))
		save_btn  = _make_btn(tr("btn_save_txt"), tr("tip_save_txt"))
		csv_btn   = _make_btn("Save CSV")
		json_btn  = _make_btn("Save JSON")
		clear_btn = _make_btn(tr("btn_clear"),    tr("tip_clear"))
		clear_btn.setObjectName("ClearBtn")

		copy_btn.clicked.connect(self.copy_to_clipboard)
		save_btn.clicked.connect(self.save_txt)
		csv_btn.clicked.connect(self.save_csv)
		json_btn.clicked.connect(self.save_json)
		clear_btn.clicked.connect(self.clear_output)

		bot_bar = QHBoxLayout()
		bot_bar.setSpacing(6)
		bot_bar.setContentsMargins(0, 0, 0, 0)
		for btn in (copy_btn, save_btn, csv_btn, json_btn):
			bot_bar.addWidget(btn)
		bot_bar.addStretch()
		bot_bar.addWidget(clear_btn)

		# ── Status bar ────────────────────────────────────────────────────────
		self._status_label = QLabel(tr("status_ready"))
		self._status_label.setObjectName("Footer")

		# ── Main layout ───────────────────────────────────────────────────────
		layout = QVBoxLayout()
		layout.setContentsMargins(12, 10, 12, 8)
		layout.setSpacing(8)
		layout.addLayout(top_bar)
		layout.addWidget(self._output, 1)
		layout.addLayout(bot_bar)
		layout.addWidget(self._status_label)

		container = QWidget()
		container.setLayout(layout)
		self.setCentralWidget(container)

	def _setup_shortcuts(self) -> None:
		QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_images)
		QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(self.paste_from_clipboard)
		QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_txt)
		QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.copy_to_clipboard)

	def _apply_current_theme(self) -> None:
		self.setStyleSheet(build_stylesheet(self._settings.theme))
		self._render()

	# ── Drag & drop ───────────────────────────────────────────────────────────

	def dragEnterEvent(self, event) -> None:  # type: ignore[override]
		if event.mimeData().hasUrls():
			if any(
				u.toLocalFile().lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".pdf"))
				for u in event.mimeData().urls()
			):
				event.acceptProposedAction()
				return
		event.ignore()

	def dropEvent(self, event) -> None:  # type: ignore[override]
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

	def open_images(self) -> None:
		d = _FileDlg(self, tr("dlg_open_images"), self._settings.save_path,
		             "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
		d.setFileMode(QFileDialog.FileMode.ExistingFiles)
		if d.exec():
			self._process_files(d.selectedFiles())

	def open_folder(self) -> None:
		d = _FileDlg(self, tr("dlg_open_folder"), self._settings.save_path)
		d.setFileMode(QFileDialog.FileMode.Directory)
		d.setOption(QFileDialog.Option.ShowDirsOnly, True)
		folder = d.selectedFiles()[0] if d.exec() else ""
		if not folder:
			return
		exts = {".png", ".jpg", ".jpeg", ".bmp"}
		paths = sorted(
			os.path.join(folder, f)
			for f in os.listdir(folder)
			if os.path.splitext(f)[1].lower() in exts
		)
		if not paths:
			QMessageBox.information(self, tr("title_info"), tr("msg_no_images_folder"))
			return
		self._process_files(paths)

	def open_pdf(self) -> None:
		d = _FileDlg(self, tr("dlg_open_pdf"), self._settings.save_path,
		             "PDF Files (*.pdf);;All Files (*)")
		d.setFileMode(QFileDialog.FileMode.ExistingFile)
		if d.exec():
			self._process_pdf(d.selectedFiles()[0])

	def scan_camera(self) -> None:
		dlg = CameraDialog(self)
		dlg.qr_detected.connect(lambda texts: self._add_result("camera", texts))
		dlg.exec()

	def paste_from_clipboard(self) -> None:
		qimage = QApplication.clipboard().image()
		if qimage.isNull():
			QMessageBox.information(self, tr("title_info"), tr("msg_no_image_clipboard"))
			return
		try:
			buf = QBuffer()
			buf.open(QIODevice.OpenModeFlag.WriteOnly)
			qimage.save(buf, "PNG")  # type: ignore[arg-type]
			pil = Image.open(BytesIO(bytes(buf.data())))  # type: ignore[arg-type]
			pil.load()
			texts = _decode_pil_image(pil)
		except Exception as exc:
			QMessageBox.critical(self, tr("title_error"), str(exc))
			return
		self._add_result("clipboard", texts)

	# ── Process helpers ───────────────────────────────────────────────────────

	def _process_files(self, paths: list[str]) -> None:
		errors = []
		for path in paths:
			try:
				self._add_result(os.path.basename(path), decode_qr_from_file(path))
			except Exception as exc:
				errors.append(f"{os.path.basename(path)}: {exc}")
		if errors:
			QMessageBox.warning(self, tr("title_errors"), "\n".join(errors))

	def _process_pdf(self, path: str) -> None:
		try:
			from .decoder import decode_qr_from_pdf
			pages = decode_qr_from_pdf(path)
		except ImportError:
			QMessageBox.critical(self, tr("title_missing_pkg"), tr("err_missing_pdf"))
			return
		except Exception as exc:
			QMessageBox.critical(self, tr("title_error"), str(exc))
			return
		name = os.path.basename(path)
		for page_num, texts in pages:
			self._add_result(f"{name} — page {page_num}", texts)

	def _add_result(self, source: str, texts: list[str]) -> None:
		entry = {
			"source": source,
			"texts": texts,
			"timestamp": datetime.now().strftime("%H:%M:%S"),
		}
		self._results.append(entry)
		self._history.append(entry)
		if len(self._history) > self._settings.history_limit:
			self._history = self._history[-self._settings.history_limit:]

		# Persist to DB
		db = AppDB.instance()
		for text in texts:
			db.add_decoded(source, text)

		self._render()
		total = sum(len(e["texts"]) for e in self._results)
		self._status_label.setText(
			tr("status_sources").format(sources=len(self._results), qrs=total)
		)

	# ── Rendering ─────────────────────────────────────────────────────────────

	def _render(self) -> None:
		from .themes import THEMES
		t = THEMES.get(self._settings.theme, THEMES["Dark"])
		if not self._results:
			self._output.clear()
			return
		parts = []
		for entry in self._results:
			src = html.escape(entry["source"])
			ts  = html.escape(entry["timestamp"])
			parts.append(
				f'<p style="color:{t["result_src"]};margin:10px 0 2px 0;">'
				f'<b>=== {src} ===</b>'
				f'<span style="font-weight:normal;font-size:11px;color:{t["result_empty"]};"> {ts}</span></p>'
			)
			if not entry["texts"]:
				parts.append(
					f'<p style="color:{t["result_empty"]};margin:1px 0 4px 0;">'
					f'&nbsp;&nbsp;{tr("result_no_qr")}</p>'
				)
			else:
				for i, text in enumerate(entry["texts"], 1):
					parts.append(
						f'<p style="color:{t["result_text"]};margin:1px 0;">'
						f'&nbsp;&nbsp;[{i}] {_linkify(text, t["link"])}</p>'
					)
		self._output.setHtml(
			f'<html><body style="background:{t["widget_bg"]};color:{t["result_text"]};'
			f'font-family:Consolas,monospace;font-size:12px;margin:10px;">'
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
				lines.append(tr("result_no_qr"))
			lines.append("")
		return "\n".join(lines).strip()

	# ── Clear ─────────────────────────────────────────────────────────────────

	def clear_output(self) -> None:
		self._results.clear()
		self._output.clear()
		self._status_label.setText(tr("status_ready"))

	# ── Export ────────────────────────────────────────────────────────────────

	def save_txt(self) -> None:
		text = self._plain_text()
		if not text:
			QMessageBox.information(self, tr("title_info"), tr("msg_no_content_save"))
			return
		d = _FileDlg(self, tr("dlg_save_txt"),
		             os.path.join(self._settings.save_path, "qr-output.txt"),
		             "Text Files (*.txt);;All Files (*)")
		d.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
		path = d.selectedFiles()[0] if d.exec() else ""
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(text)
			QMessageBox.information(self, tr("title_saved"), tr("msg_file_saved"))
		except Exception as exc:
			QMessageBox.critical(self, tr("title_error"), str(exc))

	def save_csv(self) -> None:
		if not self._results:
			QMessageBox.information(self, tr("title_info"), tr("msg_no_content_save"))
			return
		d = _FileDlg(self, tr("dlg_save_csv"),
		             os.path.join(self._settings.save_path, "qr-output.csv"),
		             "CSV Files (*.csv);;All Files (*)")
		d.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
		path = d.selectedFiles()[0] if d.exec() else ""
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
			QMessageBox.information(self, tr("title_saved"), tr("msg_csv_saved"))
		except Exception as exc:
			QMessageBox.critical(self, tr("title_error"), str(exc))

	def save_json(self) -> None:
		if not self._results:
			QMessageBox.information(self, tr("title_info"), tr("msg_no_content_save"))
			return
		d = _FileDlg(self, tr("dlg_save_json"),
		             os.path.join(self._settings.save_path, "qr-output.json"),
		             "JSON Files (*.json);;All Files (*)")
		d.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
		path = d.selectedFiles()[0] if d.exec() else ""
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				json.dump(self._results, f, ensure_ascii=False, indent=2)
			QMessageBox.information(self, tr("title_saved"), tr("msg_json_saved"))
		except Exception as exc:
			QMessageBox.critical(self, tr("title_error"), str(exc))

	def copy_to_clipboard(self) -> None:
		text = self._plain_text()
		if not text:
			QMessageBox.information(self, tr("title_info"), tr("msg_no_content_copy"))
			return
		QApplication.clipboard().setText(text)
		self._status_label.setText(tr("status_copied"))

	# ── Settings & history ────────────────────────────────────────────────────

	def open_settings(self) -> None:
		dlg = SettingsDialog(self._settings, self)
		if dlg.exec():
			self._apply_current_theme()

	def show_history(self) -> None:
		if not self._history:
			QMessageBox.information(self, tr("dlg_history_title"), tr("msg_no_history"))
			return
		HistoryDialog(self._history, self._settings, self).exec()

	def open_generator(self) -> None:
		GeneratorDialog(self._settings, self).exec()

	# ── Upgrade & update ──────────────────────────────────────────────────────

	def upgrade_app(self) -> None:
		root = os.path.normpath(
			os.path.join(os.path.dirname(__file__), "..", "..")
		)

		self.statusBar().showMessage(tr("status_checking"))
		QApplication.processEvents()

		try:
			subprocess.run(
				["git", "fetch", "--quiet"], cwd=root, check=True, timeout=15
			)
			local  = subprocess.check_output(
				["git", "rev-parse", "HEAD"], cwd=root, text=True
			).strip()
			remote = subprocess.check_output(
				["git", "rev-parse", "@{u}"], cwd=root, text=True
			).strip()
		except Exception as exc:
			self.statusBar().clearMessage()
			QMessageBox.critical(
				self, tr("title_upgrade"),
				tr("upd_reach_remote").format(error=exc),
			)
			return

		self.statusBar().clearMessage()

		from .updater import CURRENT_VERSION
		if local == remote:
			QMessageBox.information(
				self, tr("title_up_to_date"),
				tr("upd_already_latest").format(version=CURRENT_VERSION),
			)
			return

		reply = QMessageBox.question(
			self, tr("title_upgrade_avail"),
			tr("upd_upgrade_prompt").format(version=CURRENT_VERSION),
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
		)
		if reply != QMessageBox.StandardButton.Yes:
			return

		self.statusBar().showMessage(tr("status_upgrading"))
		QApplication.processEvents()

		try:
			subprocess.run(
				["git", "merge", "--ff-only", "@{u}"], cwd=root, check=True, timeout=30
			)
			subprocess.run(
				[sys.executable, "-m", "pip", "install", "-r",
				 os.path.join(root, "requirements.txt"), "-q"],
				check=True, timeout=180,
			)
		except Exception as exc:
			self.statusBar().clearMessage()
			QMessageBox.critical(self, tr("title_upgrade_fail"), str(exc))
			return

		self.statusBar().clearMessage()
		QMessageBox.information(self, tr("title_upgrade_ok"), tr("msg_upgrade_success"))
		subprocess.Popen([sys.executable] + sys.argv)
		QApplication.quit()

	def manual_update_check(self) -> None:
		from .updater import CURRENT_VERSION
		import threading

		version: str | None = None
		error: str | None = None
		done = False

		def _run() -> None:
			nonlocal version, error, done
			try:
				version = _sync_latest()
			except Exception as exc:
				error = str(exc)
			done = True

		t = threading.Thread(target=_run, daemon=True)
		t.start()
		t.join(timeout=8)

		if not done:
			QMessageBox.warning(self, tr("title_update_check"), tr("msg_update_timeout"))
		elif error is not None:
			QMessageBox.warning(
				self, tr("title_update_fail"),
				tr("upd_reach_server").format(error=error),
			)
		elif version:
			QMessageBox.information(
				self, tr("title_update_avail"),
				tr("upd_available").format(version=version),
			)
		else:
			QMessageBox.information(
				self, tr("title_up_to_date"),
				tr("upd_up_to_date").format(version=CURRENT_VERSION),
			)

	def show_version(self) -> None:
		from .updater import CURRENT_VERSION
		QMessageBox.information(
			self, tr("title_version"),
			tr("dlg_version_text").format(version=CURRENT_VERSION),
		)

	# ── Tray / close ──────────────────────────────────────────────────────────

	def set_tray(self, tray: object) -> None:
		self._tray = tray

	def closeEvent(self, event) -> None:  # type: ignore[override]
		event.accept()
		QApplication.quit()


def _sync_latest() -> str | None:
	"""Returns newer version tag if available, None if already up to date. Raises on error."""
	import json as _json
	import urllib.request
	url = "https://api.github.com/repos/NmnRn/QR-to-TXT/releases/latest"
	req = urllib.request.Request(url, headers={"User-Agent": "QRtoTXT-updater"})
	with urllib.request.urlopen(req, timeout=6) as resp:
		data = _json.loads(resp.read())
	from .updater import CURRENT_VERSION, _is_newer
	tag = data.get("tag_name", "").lstrip("v")
	return tag if tag and _is_newer(tag, CURRENT_VERSION) else None
