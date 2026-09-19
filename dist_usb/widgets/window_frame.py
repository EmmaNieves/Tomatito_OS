"""
window_frame.py — Marco de ventana estilo Windows XP con micro-animaciones.

Características:
- Transiciones sutiles de apertura, minimización y maximización (~120ms).
- Respuesta visual retro coherente en la barra de título y botones.
- Atajos Alt+F4 y Esc.
- Notificación garantizada de cierre al destruir o cerrar el marco.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QSize, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont, QPen, QPixmap, QKeyEvent, QCloseEvent

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
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        # Ajustar ligeramente la posición del texto en paintEvent
    
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

        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, color.lighter(130))
        grad.setColorAt(1, color.darker(110))
        painter.fillRect(self.rect(), grad)

        painter.setPen(QPen(color.darker(150), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        painter.setPen(QPen(QColor(TEXT_LIGHT), 1))
        painter.setFont(self.font())
        # Ajuste vertical
        y_offset = -2 if self.text() == "—" else -1
        painter.drawText(self.rect().adjusted(0, y_offset, 0, 0), Qt.AlignmentFlag.AlignCenter, self.text())
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

        self._icon_label = QLabel(icon_emoji)
        self._icon_label.setStyleSheet("color: white; font-size: 14px;")
        self._icon_label.setFixedSize(20, 20)
        layout.addWidget(self._icon_label)

        self._title_label = QLabel(title)
        self._title_label.setStyleSheet(
            "color: white; font-weight: bold; font-size: 11px; background: transparent;"
        )
        layout.addWidget(self._title_label, 1)

        self.btn_min   = _TitleBarButton("—", BTN_MINMAX_BG, BTN_MINMAX_HOVER)
        self.btn_max   = _TitleBarButton("□", BTN_MINMAX_BG, BTN_MINMAX_HOVER)
        self.btn_close = _TitleBarButton("✕", BTN_CLOSE_BG,  BTN_CLOSE_HOVER)
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

        painter.setPen(QPen(QColor("#6090E0"), 1))
        painter.drawLine(0, 0, self.width(), 0)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
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
    Marco de ventana completo estilo Windows XP con micro-animaciones.
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
        self._close_emitted = False
        self._anim: QPropertyAnimation | None = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.resize(width, height)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(2, 2, 2, 2)
        outer.setSpacing(0)

        self._title_bar = _TitleBar(self._title, self._icon_emoji, self)
        outer.addWidget(self._title_bar)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {TITLE_BAR_TOP};")
        outer.addWidget(sep)

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

    def set_content(self, widget: QWidget) -> None:
        for i in reversed(range(self._content_layout.count())):
            item = self._content_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        self._content_layout.addWidget(widget)

    def set_title(self, title: str) -> None:
        self._title = title
        self._title_bar.set_title(title)

    def get_title(self) -> str:
        return self._title

    def get_icon_emoji(self) -> str:
        return self._icon_emoji

    def _set_active(self, active: bool) -> None:
        self._title_bar.set_active(active)
        self.update()

    def animate_open(self, target_rect: QRect):
        """Micro-animación sutil de aparición al abrir la ventana (~120ms)."""
        start_rect = QRect(
            target_rect.x() + 15,
            target_rect.y() + 15,
            target_rect.width() - 30,
            target_rect.height() - 30
        )
        self.setGeometry(start_rect)
        self.setWindowOpacity(0.4)

        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(120)
        self._anim.setStartValue(start_rect)
        self._anim.setEndValue(target_rect)
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self._anim_fade = QPropertyAnimation(self, b"windowOpacity")
        self._anim_fade.setDuration(120)
        self._anim_fade.setStartValue(0.4)
        self._anim_fade.setEndValue(1.0)

        self._anim.start()
        self._anim_fade.start()

    def _request_close(self):
        import logging
        logging.info(f"[WINDOW] _request_close() ENTER para '{self._title}'")
        hide = getattr(self, "hide_on_close", False)
        if callable(hide): hide = hide()
        
        if hide:
            logging.info(f"[WINDOW] hide_on_close is True for '{self._title}', minimizing instead")
            self.minimize_requested.emit()
            return
            
        self._cleanup_content()
        self._emit_close_requested()
        logging.info(f"[WINDOW] native close() for '{self._title}'")
        self.close()
        logging.info(f"[WINDOW] deleteLater() for '{self._title}'")
        self.deleteLater()
        logging.info(f"[WINDOW] _request_close() EXIT para '{self._title}'")

    def _cleanup_content(self):
        if hasattr(self, "_content_layout") and self._content_layout:
            for i in range(self._content_layout.count()):
                item = self._content_layout.itemAt(i)
                if item and item.widget():
                    try:
                        item.widget().close()
                    except Exception:
                        pass

    def _emit_close_requested(self):
        if not self._close_emitted:
            self._close_emitted = True
            import logging
            logging.info(f"[WINDOW] close_requested.emit() for '{self._title}'")
            self.close_requested.emit()

    def closeEvent(self, event: QCloseEvent) -> None:
        import logging
        logging.info(f"[WINDOW] closeEvent() ENTER para '{self._title}'")
        self._cleanup_content()
        self._emit_close_requested()
        super().closeEvent(event)
        logging.info(f"[WINDOW] closeEvent() EXIT para '{self._title}'")

    def _toggle_maximize(self):
        if self._is_maximized_custom:
            self._restore_window()
        else:
            self._maximize_window()

    def _maximize_window(self):
        if self.parent():
            self._normal_geometry = self.geometry()
            target_rect = self.parent().rect()

            self._anim = QPropertyAnimation(self, b"geometry")
            self._anim.setDuration(120)
            self._anim.setStartValue(self.geometry())
            self._anim.setEndValue(target_rect)
            self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self._anim.start()

            self._is_maximized_custom = True
            self._title_bar.btn_max.setText("2")

    def _restore_window(self):
        if self._normal_geometry:
            self._anim = QPropertyAnimation(self, b"geometry")
            self._anim.setDuration(120)
            self._anim.setStartValue(self.geometry())
            self._anim.setEndValue(self._normal_geometry)
            self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self._anim.start()

        self._is_maximized_custom = False
        self._title_bar.btn_max.setText("1")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_F4 and (event.modifiers() & Qt.KeyboardModifier.AltModifier):
            self._request_close()
            event.accept()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(WINDOW_BORDER))

        painter.setPen(QPen(QColor("#7090D0"), 1))
        painter.drawLine(0, 0, self.width(), 0)
        painter.drawLine(0, 0, 0, self.height())

        painter.setPen(QPen(QColor("#000050"), 1))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.end()

    def mousePressEvent(self, event):
        self.focus_requested.emit()
        super().mousePressEvent(event)
