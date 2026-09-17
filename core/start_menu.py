"""
start_menu.py — Menú Inicio estilo Windows XP.

- Se abre/cierra al pulsar el botón Inicio.
- Lista las aplicaciones registradas en AppRegistry.
- Muestra los iconos PNG personalizados cuando están disponibles.
- Al seleccionar una app, la lanza mediante callback.
- Se cierra automáticamente al hacer clic fuera o al seleccionar una app.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont, QPen, QPixmap, QIcon

from core.app_registry import AppRegistry
from core.resource_manager import ResourceManager
from styles.colors import (
    STARTMENU_BG, STARTMENU_HEADER_BG, STARTMENU_ITEM_HOVER,
    STARTMENU_SEPARATOR, TEXT_DARK, TEXT_LIGHT, TITLE_BAR_GRAD_TOP, TITLE_BAR_GRAD_BOT
)


class _MenuHeader(QWidget):
    """Cabecera azul del menú Inicio con el nombre del sistema e icono de Tomatito."""

    def __init__(self, resources: ResourceManager | None = None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(54)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        path = resources.get_icon_path("tomatito") if resources else None
        if path and os.path.isfile(path):
            px = QPixmap(path)
            if not px.isNull():
                icon_lbl.setPixmap(px.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                icon_lbl.setText("🍅")
                icon_lbl.setStyleSheet("font-size: 24px; background: transparent;")
        else:
            icon_lbl.setText("🍅")
            icon_lbl.setStyleSheet("font-size: 24px; background: transparent;")

        layout.addWidget(icon_lbl)

        name = QLabel("Tomatito")
        name.setStyleSheet(
            "color: white; font-size: 14px; font-weight: bold; font-style: italic; background: transparent;"
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
    """Elemento individual del menú (una aplicación) con icono de imagen o emoji."""

    def __init__(self, emoji: str, name: str, description: str = "", icon_path: str | None = None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(28, 28)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if icon_path and os.path.isfile(icon_path):
            px = QPixmap(icon_path)
            if not px.isNull():
                icon_lbl.setPixmap(px.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                icon_lbl.setText(emoji)
                icon_lbl.setStyleSheet("font-size: 20px; background: transparent;")
        else:
            icon_lbl.setText(emoji)
            icon_lbl.setStyleSheet("font-size: 20px; background: transparent;")

        layout.addWidget(icon_lbl)

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
    """Etiqueta de sección dentro del menú."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            "color: #316AC5; font-weight: bold; font-size: 10px;"
            "padding: 6px 10px 2px 10px; background: transparent;"
        )


class StartMenu(QWidget):
    """Menú Inicio."""

    app_launched = pyqtSignal(str)

    def __init__(self, registry: AppRegistry, resources: ResourceManager | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self._registry = registry
        self._resources = resources
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedWidth(260)

        self._build_ui()
        self.hide()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(_MenuHeader(self._resources))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {STARTMENU_SEPARATOR};")
        layout.addWidget(sep)

        programs_area = QWidget()
        programs_area.setStyleSheet(f"background: {STARTMENU_BG};")
        prg_layout = QVBoxLayout(programs_area)
        prg_layout.setContentsMargins(0, 4, 0, 4)
        prg_layout.setSpacing(0)

        prg_layout.addWidget(_SectionLabel("PROGRAMAS"))

        for app_def in self._registry.start_menu_apps():
            icon_path = self._resources.get_icon_path(app_def.icon_key) if self._resources else None
            btn = _AppMenuItem(
                emoji=app_def.emoji,
                name=app_def.name,
                description=app_def.description,
                icon_path=icon_path,
            )
            app_id = app_def.app_id
            btn.clicked.connect(lambda checked, aid=app_id: self._launch(aid))
            prg_layout.addWidget(btn)

        prg_layout.addStretch()
        layout.addWidget(programs_area, 1)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {STARTMENU_SEPARATOR};")
        layout.addWidget(sep2)

        footer = QWidget()
        footer.setStyleSheet("background: #D4D0C8;")
        footer.setFixedHeight(36)
        layout.addWidget(footer)

        self._update_height()

    def _update_height(self):
        n = max(1, len(self._registry.start_menu_apps()))
        self.setFixedHeight(54 + 4 + n * 46 + 20 + 4 + 36 + 30)

    def _launch(self, app_id: str):
        self.hide()
        self.app_launched.emit(app_id)

    def show_above(self, taskbar: QWidget) -> None:
        pos = taskbar.mapToGlobal(QPoint(0, 0))
        x = pos.x()
        y = pos.y() - self.height()
        self.move(x, y)
        self.show()
        self.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(STARTMENU_BG))
        painter.setPen(QPen(QColor("#0A246A"), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        painter.end()
