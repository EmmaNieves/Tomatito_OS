"""
taskbar.py — Barra de tareas estilo Windows XP.

Incluye:
- Botón Inicio con logo 🍅.
- Área de botones de ventanas abiertas (se actualiza via WindowManager).
- Reloj digital actualizado cada segundo.
- Área de notificación (visual).
- Se comunica con WindowManager mediante señales.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QTime
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QPen, QFont

from core.window_manager import WindowManager
from widgets.taskbar_button import TaskbarButton
from styles.colors import (
    TASKBAR_BG, TASKBAR_BORDER_TOP, START_BTN_TOP, START_BTN_BOT,
    START_BTN_HOVER_TOP, START_BTN_HOVER_BOT, TEXT_LIGHT
)


class _StartButton(QPushButton):
    """Botón Inicio verde estilo XP."""

    def __init__(self, parent=None):
        super().__init__("  tomatitOS", parent)
        self.setFixedSize(130, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))

        import os
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons", "tomatito.png")
        if os.path.isfile(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(22, 22))

        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {START_BTN_TOP}, stop:1 {START_BTN_BOT});
                color: white;
                border: 1px solid #1A5A10;
                border-top: 1px solid #7ACC55;
                border-radius: 12px;
                padding: 0 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {START_BTN_HOVER_TOP}, stop:1 {START_BTN_HOVER_BOT});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {START_BTN_BOT}, stop:1 {START_BTN_TOP});
            }}
        """)


class _ClockWidget(QLabel):
    """Reloj digital actualizado cada segundo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "color: white; font-size: 11px; font-family: Tahoma; background: transparent;"
            "padding: 0 8px;"
        )
        self.setFixedWidth(60)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(1000)
        self._update_time()

    def _update_time(self):
        t = QTime.currentTime()
        self.setText(t.toString("HH:mm"))
        self.setToolTip(t.toString("hh:mm:ss AP"))


class Taskbar(QWidget):
    """
    Barra de tareas inferior. Altura fija de 40px.
    Se conecta con WindowManager para reflejar ventanas abiertas/cerradas.
    """

    start_clicked = pyqtSignal()

    def __init__(self, window_manager: WindowManager, parent: QWidget | None = None):
        super().__init__(parent)
        self._wm = window_manager
        # Mapa: WindowFrame -> TaskbarButton
        self._buttons: dict[object, TaskbarButton] = {}

        self.setFixedHeight(40)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self._build_ui()
        self._connect_window_manager()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # Botón Inicio
        self._start_btn = _StartButton()
        self._start_btn.clicked.connect(self.start_clicked)
        layout.addWidget(self._start_btn)

        # Separador vertical
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #1A3888; max-height: 30px;")
        layout.addWidget(sep)

        # Área de botones de ventanas
        self._buttons_area = QWidget()
        self._buttons_area.setStyleSheet("background: transparent;")
        self._buttons_layout = QHBoxLayout(self._buttons_area)
        self._buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._buttons_layout.setSpacing(3)
        self._buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._buttons_area, 1)

        # Área de notificación + reloj
        notif_sep = QFrame()
        notif_sep.setFrameShape(QFrame.Shape.VLine)
        notif_sep.setStyleSheet("color: #1A3888; max-height: 30px;")
        layout.addWidget(notif_sep)

        self._clock = _ClockWidget()
        layout.addWidget(self._clock)

    def _connect_window_manager(self):
        self._wm.window_opened.connect(self._on_window_opened)
        self._wm.window_closed.connect(self._on_window_closed)
        self._wm.window_focused.connect(self._on_window_focused)
        self._wm.window_minimized.connect(self._on_window_minimized)

    # ── Gestión de botones de ventana ─────────────────────────────────────

    def _on_window_opened(self, window) -> None:
        btn = TaskbarButton(
            label=window.get_title(),
            emoji=window.get_icon_emoji(),
        )
        btn.set_active(True)
        btn.clicked.connect(lambda: self._on_button_clicked(window))
        self._buttons_layout.addWidget(btn)
        self._buttons[window] = btn

    def _on_window_closed(self, window) -> None:
        if window in self._buttons:
            btn = self._buttons.pop(window)
            self._buttons_layout.removeWidget(btn)
            btn.deleteLater()

    def _on_window_focused(self, window) -> None:
        for win, btn in self._buttons.items():
            btn.set_active(win is window)

    def _on_window_minimized(self, window) -> None:
        if window in self._buttons:
            self._buttons[window].set_active(False)

    def _on_button_clicked(self, window) -> None:
        self._wm.toggle_minimize(window)

    # ── Pintura ───────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        # Gradiente de fondo
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#4878D8"))
        grad.setColorAt(0.15, QColor(TASKBAR_BG))
        grad.setColorAt(0.85, QColor("#1A48B0"))
        grad.setColorAt(1.0, QColor("#0A2880"))
        painter.fillRect(self.rect(), grad)

        # Línea superior brillante
        painter.setPen(QPen(QColor(TASKBAR_BORDER_TOP), 2))
        painter.drawLine(0, 0, self.width(), 0)
        painter.end()
