import os
import re
from datetime import datetime
from io import BytesIO
from typing import cast

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..db import AppDB
from ..i18n import tr
from ..settings import AppSettings

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)

_BADGE: dict[str, str] = {
    "link": (
        "background:#2b6be4; color:white;"
        " padding:2px 10px; border-radius:9px;"
        " font-size:11px; font-weight:bold;"
    ),
    "text": (
        "background:#2da44e; color:white;"
        " padding:2px 10px; border-radius:9px;"
        " font-size:11px; font-weight:bold;"
    ),
    "none": "padding:2px 10px;",
}

# Auto-save directory for generated QR codes
_QR_DIR = os.path.join(os.path.expanduser("~"), "QR Codes")


def _make_qr_image(
    text: str,
    fill_color: str = "black",
    back_color: str = "white",
) -> Image.Image:
    try:
        import qrcode
        import qrcode.constants
    except ImportError:
        raise ImportError(tr("err_missing_qrcode"))
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    pil_img = cast(Image.Image, qr.make_image(fill_color=fill_color, back_color=back_color))
    return pil_img.convert("RGB")


def _pil_to_pixmap(img: Image.Image) -> QPixmap:
    buf = BytesIO()
    img.save(buf, format="PNG")
    px = QPixmap()
    px.loadFromData(buf.getvalue())
    return px


def _auto_save(img: Image.Image) -> str:
    """Save QR to ~/QR Codes/ with a timestamp filename. Returns the path."""
    os.makedirs(_QR_DIR, exist_ok=True)
    filename = datetime.now().strftime("qr_%Y%m%d_%H%M%S.png")
    path = os.path.join(_QR_DIR, filename)
    img.save(path)
    return path


class GeneratorDialog(QDialog):
    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self._pil_image: Image.Image | None = None      # white bg — for save/copy
        self._display_image: Image.Image | None = None  # themed bg — for preview
        self._saved_path: str = ""
        self._content_type: str = "none"
        self.setWindowTitle(tr("dlg_generator_title"))
        self.setMinimumSize(400, 540)
        self.resize(440, 580)
        self._build_ui()
        self._apply_theme()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout()
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(14)

        outer.addWidget(self._make_input_card())
        outer.addWidget(self._make_qr_card(), 1)
        outer.addLayout(self._make_button_row())

        self.setLayout(outer)

    def _make_input_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        hint = QLabel(tr("gen_hint"))
        hint.setObjectName("Hint")

        self._input = QTextEdit()
        self._input.setPlaceholderText(tr("gen_placeholder"))
        self._input.setFixedHeight(80)
        self._input.textChanged.connect(self._on_text_changed)

        self._badge = QLabel(tr("gen_type_none"))
        self._badge.setObjectName("Badge")
        self._badge.setStyleSheet(_BADGE["none"])

        self._gen_btn = QPushButton(tr("gen_generate"))
        self._gen_btn.setObjectName("Primary")
        self._gen_btn.clicked.connect(self._generate)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self._badge)
        row.addStretch()
        row.addWidget(self._gen_btn)

        inner = QVBoxLayout()
        inner.setContentsMargins(14, 14, 14, 14)
        inner.setSpacing(8)
        inner.addWidget(hint)
        inner.addWidget(self._input)
        inner.addLayout(row)
        card.setLayout(inner)
        return card

    def _make_qr_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("QrCard")

        self._qr_label = QLabel(tr("gen_qr_placeholder"))
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setObjectName("QrLabel")
        self._qr_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self._auto_save_label = QLabel("")
        self._auto_save_label.setObjectName("AutoSave")
        self._auto_save_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner = QVBoxLayout()
        inner.setContentsMargins(16, 16, 16, 8)
        inner.addWidget(self._qr_label)
        inner.addWidget(self._auto_save_label)
        card.setLayout(inner)
        return card

    def _make_button_row(self) -> QHBoxLayout:
        self._save_btn = QPushButton(tr("gen_save_png"))
        self._save_btn.setObjectName("Primary")
        self._copy_btn = QPushButton(tr("gen_copy_image"))
        self._copy_btn.setObjectName("Primary")
        close_btn = QPushButton(tr("btn_close"))
        close_btn.setObjectName("Ghost")

        self._save_btn.clicked.connect(self._save)
        self._copy_btn.clicked.connect(self._copy)
        close_btn.clicked.connect(self.reject)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self._save_btn)
        row.addWidget(self._copy_btn)
        row.addStretch()
        row.addWidget(close_btn)
        return row

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _on_text_changed(self) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            self._badge.setText(tr("gen_type_none"))
            self._badge.setStyleSheet(_BADGE["none"])
            self._content_type = "none"
        elif _URL_RE.match(text):
            self._badge.setText(tr("gen_type_link"))
            self._badge.setStyleSheet(_BADGE["link"])
            self._content_type = "link"
        else:
            self._badge.setText(tr("gen_type_text"))
            self._badge.setStyleSheet(_BADGE["text"])
            self._content_type = "text"

    def _generate(self) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            QMessageBox.information(self, tr("title_info"), tr("msg_enter_text"))
            return
        from ..themes import THEMES
        t = THEMES.get(self._settings.theme, THEMES["Dark"])

        try:
            self._pil_image    = _make_qr_image(text)                           # white — for save/copy
            self._display_image = _make_qr_image(text, t["text"], t["widget_bg"])  # themed — for preview
        except ImportError as exc:
            QMessageBox.critical(self, tr("title_missing_pkg"), str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, tr("title_error"), str(exc))
            return

        # Auto-save and record in DB
        try:
            path = _auto_save(img)
            self._saved_path = path
            AppDB.instance().add_generated(text, self._content_type, path)
            self._auto_save_label.setText(
                f"{tr('gen_auto_saved')}  —  {os.path.basename(path)}"
            )
        except Exception:
            self._auto_save_label.setText("")

        self._refresh_pixmap()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._pil_image is not None:
            self._refresh_pixmap()

    def _refresh_pixmap(self) -> None:
        img = self._display_image or self._pil_image
        if img is None:
            return
        pixmap = _pil_to_pixmap(img)
        size = self._qr_label.size()
        self._qr_label.setPixmap(
            pixmap.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _save(self) -> None:
        if self._pil_image is None:
            QMessageBox.information(self, tr("title_info"), tr("msg_generate_first"))
            return
        default = self._saved_path or os.path.join(
            self._settings.save_path, "qrcode.png"
        )
        d = QFileDialog(self, tr("dlg_save_qr"), default, "PNG Images (*.png);;All Files (*)")
        d.setStyleSheet("")
        d.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        path = d.selectedFiles()[0] if d.exec() else ""
        if not path:
            return
        try:
            self._pil_image.save(path)
            # Update DB record if path changed
            if path != self._saved_path:
                AppDB.instance().add_generated(
                    self._input.toPlainText().strip(),
                    self._content_type,
                    path,
                )
            QMessageBox.information(self, tr("title_saved"), tr("msg_qr_saved"))
        except Exception as exc:
            QMessageBox.critical(self, tr("title_error"), str(exc))

    def _copy(self) -> None:
        if self._pil_image is None:
            QMessageBox.information(self, tr("title_info"), tr("msg_generate_first"))
            return
        QApplication.clipboard().setPixmap(_pil_to_pixmap(self._pil_image))
        p = self.parent()
        if isinstance(p, QMainWindow):
            p.statusBar().showMessage(tr("status_qr_copied"))

    # ── Theme ─────────────────────────────────────────────────────────────────

    def _apply_theme(self) -> None:
        from ..themes import THEMES
        t = THEMES.get(self._settings.theme, THEMES["Dark"])

        self.setStyleSheet(f"""
            QDialog {{
                background: {t['window_bg']};
            }}

            /* ── Input card ── */
            QFrame#Card {{
                background: {t['widget_bg']};
                border: 1px solid {t['border']};
                border-radius: 12px;
            }}
            QLabel#Hint {{
                color: {t['text_dim']};
                font-size: 12px;
                font-weight: normal;
            }}
            QLabel#AutoSave {{
                color: {t['text_dim']};
                font-size: 11px;
            }}
            QTextEdit {{
                background: {t['window_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                selection-background-color: {t['button_bg']};
            }}
            QLabel#Badge {{
                font-size: 11px;
            }}

            /* ── QR card ── */
            QFrame#QrCard {{
                background: {t['widget_bg']};
                border: 1px solid {t['border']};
                border-radius: 12px;
            }}
            QLabel#QrLabel {{
                background: transparent;
                color: {t['text_dim']};
                font-size: 13px;
            }}

            /* ── Buttons ── */
            QPushButton#Primary {{
                background: {t['button_bg']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton#Primary:hover  {{ background: {t['button_hover']}; }}
            QPushButton#Primary:pressed {{ background: {t['button_press']}; }}

            QPushButton#Ghost {{
                background: transparent;
                color: {t['text_dim']};
                border: 1px solid {t['border']};
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 13px;
            }}
            QPushButton#Ghost:hover {{
                background: {t['border']};
                color: {t['text']};
            }}
        """)
