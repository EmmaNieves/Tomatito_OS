"""
desktop_icon.py — Icono de escritorio con estilo auténtico de Windows XP.

Características:
- Sombra de texto desplegada sobre el fondo del escritorio.
- Recuadro azul de selección estilo Windows XP (#0B61A4).
- Doble clic abre la aplicación con sonido.
- Clic simple selecciona con respuesta visual clara.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPixmap, QPen

from styles.colors import ICON_SELECTED_BG, ICON_LABEL_COLOR


class DesktopIcon(QWidget):
    """Icono del escritorio con comportamiento e interfaz estilo Windows XP."""

    activated = pyqtSignal()      # doble clic
    selected  = pyqtSignal(object) # clic simple

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
        self._click_timer.setInterval(280)
        self._click_timer.timeout.connect(self._on_single_click)
        self._pending_single = False

        self.setFixedSize(86, 94)
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

        if pixmap and not pixmap.isNull():
            self._img_label.setPixmap(
                pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self._img_label.setText(emoji)
            self._img_label.setStyleSheet("font-size: 34px; background: transparent;")

        layout.addWidget(self._img_label, 0, Qt.AlignmentFlag.AlignHCenter)

        # Etiqueta de texto
        self._label_text = label
        self._text_label = QLabel(label)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text_label.setWordWrap(True)
        self._text_label.setFont(QFont("Tahoma", 9, QFont.Weight.Bold))
        self._text_label.setFixedWidth(78)
        self._update_label_style()
        layout.addWidget(self._text_label, 0, Qt.AlignmentFlag.AlignHCenter)

    def _update_label_style(self):
        if self._selected:
            self._text_label.setStyleSheet(
                "color: #ffffff; background-color: #0b61a4; border-radius: 2px; padding: 1px 2px; font-weight: bold;"
            )
            self._text_label.setGraphicsEffect(None)
        else:
            self._text_label.setStyleSheet(
                "color: #ffffff; background: transparent; font-weight: bold;"
            )
            # Aplicar sombra realista
            from PyQt6.QtWidgets import QGraphicsDropShadowEffect
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(4)
            shadow.setColor(QColor(0, 0, 0, 200))
            shadow.setOffset(1, 1)
            self._text_label.setGraphicsEffect(shadow)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._update_label_style()
        self.update()

    def is_selected(self) -> bool:
        return self._selected

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._selected:
            painter.fillRect(self.rect(), QColor(11, 97, 164, 70))
            painter.setPen(QPen(QColor(11, 97, 164, 200), 1, Qt.PenStyle.DotLine))
            painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
        elif self._hovered:
            painter.fillRect(self.rect(), QColor(255, 255, 255, 40))
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1, Qt.PenStyle.SolidLine))
            painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

        painter.end()
