"""
start_menu.py — Menú Inicio estilo Windows XP.

- Se abre/cierra al pulsar el botón Inicio.
- Lista las aplicaciones registradas en AppRegistry.
- Al seleccionar una app, la lanza mediante callback.
- Se cierra automáticamente al hacer clic fuera o al seleccionar una app.
- Arquitectura preparada para añadir secciones (documentos, configuración, etc.).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont, QPen

from core.app_registry import AppRegistry
from styles.colors import (
    STARTMENU_BG, STARTMENU_HEADER_BG, STARTMENU_ITEM_HOVER,
    STARTMENU_SEPARATOR, TEXT_DARK, TEXT_LIGHT, TITLE_BAR_GRAD_TOP, TITLE_BAR_GRAD_BOT
)


class _MenuHeader(QWidget):
    """Cabecera azul del menú Inicio con el nombre del sistema."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(54)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        icon = QLabel("🍅")
        icon.setStyleSheet("font-size: 28px;")
        layout.addWidget(icon)

        name = QLabel("Tomatito")
        name.setStyleSheet(
            "color: white; font-size: 14px; font-weight: bold; font-style: italic;"
        )
        layout.addWidget(name)
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0, QColor(TITLE_BAR_GRAD_TOP))
        grad.setColorAt(1, QColor(TITLE_BAR_GRAD_BOT))
        painter.fillRect(self.rect(), grad)
        painter.end()


class _AppMenuItem(QPushButton):
    """Elemento individual del menú (una aplicación)."""

    def __init__(self, emoji: str, name: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(),
            self.sizePolicy().verticalPolicy()
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)

        icon = QLabel(emoji)
        icon.setStyleSheet("font-size: 22px; background: transparent;")
        icon.setFixedSize(28, 28)
        layout.addWidget(icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)

        title_lbl = QLabel(name)
        title_lbl.setStyleSheet(
            f"color: {TEXT_DARK}; font-weight: bold; font-size: 12px; background: transparent;"
        )
        text_col.addWidget(title_lbl)

        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setStyleSheet(
                f"color: #666666; font-size: 10px; background: transparent;"
            )
            text_col.addWidget(desc_lbl)

        layout.addLayout(text_col)
        layout.addStretch()

        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                text-align: left;
            }
            QPushButton:hover {
                background: #316AC5;
                border-radius: 2px;
            }
        """)


class _SectionLabel(QLabel):
    """Etiqueta de sección dentro del menú (ej. 'PROGRAMAS')."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            "color: #316AC5; font-weight: bold; font-size: 10px;"
            "padding: 6px 10px 2px 10px; background: transparent;"
        )


class StartMenu(QWidget):
    """
    Menú Inicio. Se posiciona sobre la barra de tareas.
    """

    app_launched = pyqtSignal(str)  # app_id

    def __init__(self, registry: AppRegistry, parent: QWidget | None = None):
        super().__init__(parent)
        self._registry = registry
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedWidth(260)

        self._build_ui()
        self.hide()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Cabecera
        layout.addWidget(_MenuHeader())

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {STARTMENU_SEPARATOR};")
        layout.addWidget(sep)

        # Área de programas
        programs_area = QWidget()
        programs_area.setStyleSheet(f"background: {STARTMENU_BG};")
        prg_layout = QVBoxLayout(programs_area)
        prg_layout.setContentsMargins(0, 4, 0, 4)
        prg_layout.setSpacing(0)

        prg_layout.addWidget(_SectionLabel("PROGRAMAS"))

        for app_def in self._registry.start_menu_apps():
            btn = _AppMenuItem(
                emoji=app_def.emoji,
                name=app_def.name,
                description=app_def.description,
            )
            # Capturar app_id en closure
            app_id = app_def.app_id
            btn.clicked.connect(lambda checked, aid=app_id: self._launch(aid))
            prg_layout.addWidget(btn)

        prg_layout.addStretch()
        layout.addWidget(programs_area, 1)

        # Footer apagar
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {STARTMENU_SEPARATOR};")
        layout.addWidget(sep2)

        footer = QWidget()
        footer.setStyleSheet(f"background: #D4D0C8;")
        footer.setFixedHeight(36)
        layout.addWidget(footer)

        self._update_height()

    def _update_height(self):
        n = max(1, len(self._registry.start_menu_apps()))
        self.setFixedHeight(54 + 4 + n * 46 + 20 + 4 + 36 + 30)

    def _launch(self, app_id: str):
        self.hide()
        self.app_launched.emit(app_id)

    # ── Posicionamiento ───────────────────────────────────────────────────

    def show_above(self, taskbar: QWidget) -> None:
        """Posiciona y muestra el menú encima del botón Inicio."""
        pos = taskbar.mapToGlobal(QPoint(0, 0))
        x = pos.x()
        y = pos.y() - self.height()
        self.move(x, y)
        self.show()
        self.raise_()

    # ── Pintura del fondo ─────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(STARTMENU_BG))
        # Borde exterior
        painter.setPen(QPen(QColor("#0A246A"), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        painter.end()
