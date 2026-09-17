"""
desktop_icon.py — Icono de escritorio estilo Windows XP.

Características:
- Muestra un emoji (o imagen desde ResourceManager) con etiqueta de texto.
- Doble clic lanza la callback asociada.
- Estados visual: normal, hover, seleccionado.
- Clic simple selecciona. Clic en otro lugar deselecciona (gestionado por Desktop).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPixmap

from styles.colors import ICON_SELECTED_BG, ICON_LABEL_COLOR


class DesktopIcon(QWidget):
    """
    Icono del escritorio con doble clic para lanzar una aplicación.
    """

    activated   = pyqtSignal()   # doble clic
    selected    = pyqtSignal(object)  # clic simple (self)

    def __init__(
        self,
        label: str,
        emoji: str = "📄",
        pixmap: QPixmap | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._selected = False
        self._hovered  = False
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(300)
        self._click_timer.timeout.connect(self._on_single_click)
        self._pending_single = False

        self.setFixedSize(80, 88)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Imagen o emoji
        self._img_label = QLabel()
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_label.setFixedSize(48, 48)

        if pixmap:
            self._img_label.setPixmap(
                pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self._img_label.setText(emoji)
            self._img_label.setStyleSheet("font-size: 32px; background: transparent;")

        layout.addWidget(self._img_label, 0, Qt.AlignmentFlag.AlignHCenter)

        # Etiqueta de texto
        self._text_label = QLabel(label)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text_label.setWordWrap(True)
        self._text_label.setStyleSheet(
            f"color: {ICON_LABEL_COLOR}; font-size: 11px; background: transparent;"
        )
        self._text_label.setFixedWidth(72)
        layout.addWidget(self._text_label, 0, Qt.AlignmentFlag.AlignHCenter)

    # ── Selección ─────────────────────────────────────────────────────────

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self.update()

    def is_selected(self) -> bool:
        return self._selected

    # ── Eventos ───────────────────────────────────────────────────────────

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pending_single = True
            self._click_timer.start()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._click_timer.stop()
            self._pending_single = False
            self.set_selected(True)
            self.selected.emit(self)
            self.activated.emit()
        super().mouseDoubleClickEvent(event)

    def _on_single_click(self):
        if self._pending_single:
            self._pending_single = False
            self.set_selected(True)
            self.selected.emit(self)

    # ── Pintura ───────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._selected:
            painter.fillRect(self.rect(), QColor(ICON_SELECTED_BG + "99"))
            painter.setPen(QColor(ICON_SELECTED_BG))
            painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
        elif self._hovered:
            painter.fillRect(self.rect(), QColor(ICON_SELECTED_BG + "55"))

        painter.end()
