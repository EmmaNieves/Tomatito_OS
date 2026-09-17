"""
window_frame.py — Marco de ventana estilo Windows XP.

Características:
- Barra de título con degradado azul y botones Minimizar / Maximizar / Cerrar.
- Arrastre con el ratón (drag to move).
- Doble clic en la barra de título: maximizar / restaurar.
- Borde con sombra y relieve.
- Estado activo / inactivo (la barra cambia de color).
- Señales Qt para comunicación con WindowManager y Taskbar.
- El contenido de la app se inserta como widget hijo en el área central.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QSize, QRect
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont, QPen, QPixmap

from styles.colors import (
    TITLE_BAR_GRAD_TOP, TITLE_BAR_GRAD_BOT, TITLE_BAR_TOP,
    TITLE_BAR_INACTIVE, WINDOW_BG, WINDOW_BORDER,
    BTN_CLOSE_BG, BTN_CLOSE_HOVER, BTN_MINMAX_BG, BTN_MINMAX_HOVER,
    TEXT_LIGHT
)


class _TitleBarButton(QPushButton):
    """Botón pequeño para la barra de título (Minimizar/Maximizar/Cerrar)."""

    def __init__(self, symbol: str, color_normal: str, color_hover: str, parent=None):
        super().__init__(symbol, parent)
        self._color_normal = QColor(color_normal)
        self._color_hover  = QColor(color_hover)
        self._hovered = False
        self.setFixedSize(21, 21)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setFont(QFont("Marlett", 7, QFont.Weight.Bold))

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = self._color_hover if self._hovered else self._color_normal

        # Fondo del botón con gradiente
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, color.lighter(130))
        grad.setColorAt(1, color.darker(110))
        painter.fillRect(self.rect(), grad)

        # Borde
        painter.setPen(QPen(color.darker(150), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # Símbolo
        painter.setPen(QPen(QColor(TEXT_LIGHT), 1))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


class _TitleBar(QWidget):
    """Barra de título arrastrable con degradado azul."""

    double_clicked = pyqtSignal()

    def __init__(self, title: str, icon_emoji: str, parent=None):
        super().__init__(parent)
        self._active = True
        self._drag_pos: QPoint | None = None
        self.setFixedHeight(28)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 3, 0)
        layout.setSpacing(3)

        # Emoji/icono
        self._icon_label = QLabel(icon_emoji)
        self._icon_label.setStyleSheet("color: white; font-size: 14px;")
        self._icon_label.setFixedSize(20, 20)
        layout.addWidget(self._icon_label)

        # Título
        self._title_label = QLabel(title)
        self._title_label.setStyleSheet(
            "color: white; font-weight: bold; font-size: 11px; background: transparent;"
        )
        layout.addWidget(self._title_label, 1)

        # Botones
        self.btn_min   = _TitleBarButton("0", BTN_MINMAX_BG, BTN_MINMAX_HOVER)
        self.btn_max   = _TitleBarButton("1", BTN_MINMAX_BG, BTN_MINMAX_HOVER)
        self.btn_close = _TitleBarButton("r", BTN_CLOSE_BG,  BTN_CLOSE_HOVER)
        self.btn_min.setToolTip("Minimizar")
        self.btn_max.setToolTip("Maximizar")
        self.btn_close.setToolTip("Cerrar")

        for btn in (self.btn_min, self.btn_max, self.btn_close):
            layout.addWidget(btn)

    def set_title(self, title: str):
        self._title_label.setText(title)

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        if self._active:
            grad.setColorAt(0.0, QColor(TITLE_BAR_GRAD_TOP).lighter(115))
            grad.setColorAt(0.5, QColor(TITLE_BAR_GRAD_TOP))
            grad.setColorAt(1.0, QColor(TITLE_BAR_GRAD_BOT))
        else:
            c = QColor(TITLE_BAR_INACTIVE)
            grad.setColorAt(0, c.lighter(110))
            grad.setColorAt(1, c.darker(110))
        painter.fillRect(self.rect(), grad)

        # Línea superior brillante
        painter.setPen(QPen(QColor("#6090E0"), 1))
        painter.drawLine(0, 0, self.width(), 0)
        painter.end()

    # ── Drag ─────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Mover la WindowFrame (parentWidget), no la ventana top-level (Desktop)
            frame = self.parentWidget()
            if frame:
                self._drag_pos = event.globalPosition().toPoint() - frame.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            frame = self.parentWidget()
            if frame:
                frame.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)


class WindowFrame(QWidget):
    """
    Marco de ventana completo. Envuelve el contenido de una aplicación
    con barra de título, borde y comportamiento de ventana XP.

    Uso:
        frame = WindowFrame(title="Mi App", icon_emoji="📁", parent=desktop)
        frame.set_content(my_app_widget)
        frame.show()
    """

    close_requested    = pyqtSignal()
    minimize_requested = pyqtSignal()
    maximize_requested = pyqtSignal()
    focus_requested    = pyqtSignal()

    def __init__(
        self,
        title: str,
        icon_emoji: str = "🖥️",
        width: int = 680,
        height: int = 500,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._is_maximized_custom = False
        self._normal_geometry: QRect | None = None
        self._title = title
        self._icon_emoji = icon_emoji

        # Ventana sin decoración del sistema operativo host
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.resize(width, height)

        self._build_ui()
        self._connect_signals()

    # ── Construcción UI ───────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(2, 2, 2, 2)
        outer.setSpacing(0)

        # Barra de título
        self._title_bar = _TitleBar(self._title, self._icon_emoji, self)
        outer.addWidget(self._title_bar)

        # Separador
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {TITLE_BAR_TOP};")
        outer.addWidget(sep)

        # Área de contenido
        self._content_area = QWidget()
        self._content_area.setStyleSheet(f"background: {WINDOW_BG};")
        self._content_layout = QVBoxLayout(self._content_area)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._content_area, 1)

    def _connect_signals(self):
        self._title_bar.btn_close.clicked.connect(self._request_close)
        self._title_bar.btn_min.clicked.connect(self.minimize_requested)
        self._title_bar.btn_max.clicked.connect(self._toggle_maximize)
        self._title_bar.double_clicked.connect(self._toggle_maximize)

    # ── API pública ───────────────────────────────────────────────────────

    def set_content(self, widget: QWidget) -> None:
        """Inserta el widget de contenido de la aplicación en el marco."""
        # Eliminar contenido previo si existe
        for i in reversed(range(self._content_layout.count())):
            self._content_layout.itemAt(i).widget().setParent(None)
        self._content_layout.addWidget(widget)

    def set_title(self, title: str) -> None:
        self._title = title
        self._title_bar.set_title(title)

    def get_title(self) -> str:
        return self._title

    def get_icon_emoji(self) -> str:
        return self._icon_emoji

    def _set_active(self, active: bool) -> None:
        """Llamado por WindowManager para indicar si esta ventana tiene el foco."""
        self._title_bar.set_active(active)
        self.update()

    # ── Comportamiento de ventana ─────────────────────────────────────────

    def _request_close(self):
        self.close_requested.emit()
        self.close()

    def _toggle_maximize(self):
        if self._is_maximized_custom:
            self._restore_window()
        else:
            self._maximize_window()

    def _maximize_window(self):
        if self.parent():
            self._normal_geometry = self.geometry()
            parent_rect = self.parent().rect()
            # Dejar espacio para la taskbar (40px abajo)
            self.setGeometry(0, 0, parent_rect.width(), parent_rect.height() - 40)
            self._is_maximized_custom = True
            self._title_bar.btn_max.setText("2")  # Símbolo restaurar en Marlett

    def _restore_window(self):
        if self._normal_geometry:
            self.setGeometry(self._normal_geometry)
        self._is_maximized_custom = False
        self._title_bar.btn_max.setText("1")

    # ── Pintura del borde ─────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)

        # Fondo completo con color de borde
        painter.fillRect(self.rect(), QColor(WINDOW_BORDER))

        # Borde iluminado arriba/izquierda
        painter.setPen(QPen(QColor("#7090D0"), 1))
        painter.drawLine(0, 0, self.width(), 0)
        painter.drawLine(0, 0, 0, self.height())

        # Borde oscuro abajo/derecha
        painter.setPen(QPen(QColor("#000050"), 1))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.end()

    # ── Foco al hacer clic ────────────────────────────────────────────────

    def mousePressEvent(self, event):
        self.focus_requested.emit()
        super().mousePressEvent(event)
