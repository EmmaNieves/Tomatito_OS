"""
desktop.py — Escritorio principal de Tomatito.

Es el widget raíz que ocupa toda la pantalla. Contiene:
- Fondo de pantalla (imagen o degradado genérico).
- Iconos del escritorio.
- WindowManager (las ventanas son hijos de este widget).
- Taskbar anclada en la parte inferior.
- StartMenu (popup).
- Botón de cierre (esquina superior derecha del escritorio).
- Orquestación general del sistema.
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPixmap, QColor, QLinearGradient, QFont

from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager
from core.app_registry import AppRegistry, AppDefinition
from core.window_manager import WindowManager
from core.taskbar import Taskbar
from core.start_menu import StartMenu
from widgets.desktop_icon import DesktopIcon
from widgets.window_frame import WindowFrame
from styles.colors import DESKTOP_BG


# ── Coordenadas de los iconos del escritorio ──────────────────────────────
ICON_GRID_START = QPoint(20, 20)
ICON_COLS       = 1   # apilados en columna izquierda
ICON_SPACING_Y  = 100


class _ShutdownButton(QPushButton):
    """
    Botón de apagado flotante en la esquina superior derecha del escritorio.
    Estética sutil: casi transparente, se ilumina al hover.
    """

    def __init__(self, parent=None):
        super().__init__("⏻", parent)
        self.setFixedSize(32, 32)
        self.setToolTip("Cerrar Tomatito")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI Symbol", 14))
        self.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 60);
                color: rgba(255, 255, 255, 160);
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(180, 30, 30, 200);
                color: white;
                border: 1px solid rgba(255, 100, 100, 180);
            }
            QPushButton:pressed {
                background: rgba(220, 50, 50, 230);
            }
        """)


class Desktop(QWidget):
    """
    Widget principal de la aplicación. Ocupa toda la pantalla.
    Actúa como el 'sistema operativo' virtual.
    """

    def __init__(
        self,
        resources: ResourceManager,
        sounds: SoundManager,
        registry: AppRegistry,
    ):
        super().__init__()
        self._resources = resources
        self._sounds = sounds
        self._registry = registry

        self._wallpaper: QPixmap | None = None
        self._icons: list[DesktopIcon] = []
        self._open_apps: dict[str, WindowFrame] = {}  # app_id -> frame

        # Quitar decoración del sistema operativo host
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._wm = WindowManager(self)
        self._build_ui()
        self._load_wallpaper()
        self._populate_icons()

        self.showFullScreen()

    # ── Construcción UI ───────────────────────────────────────────────────

    def _build_ui(self):
        # Layout principal: contenido arriba, taskbar abajo
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Área del escritorio (fondo + iconos + ventanas)
        self._work_area = QWidget(self)
        self._work_area.setStyleSheet("background: transparent;")
        main_layout.addWidget(self._work_area, 1)

        # Barra de tareas
        self._taskbar = Taskbar(self._wm, self)
        self._taskbar.start_clicked.connect(self._toggle_start_menu)
        main_layout.addWidget(self._taskbar)

        # Menú Inicio (popup, padre = este widget)
        self._start_menu = StartMenu(self._registry, self)
        self._start_menu.app_launched.connect(self._launch_app)

        # Botón de cierre (se coloca en resizeEvent para posicionarlo siempre en la esquina)
        self._shutdown_btn = _ShutdownButton(self)
        self._shutdown_btn.clicked.connect(self._confirm_shutdown)
        self._shutdown_btn.raise_()

    # ── Fondo de pantalla ─────────────────────────────────────────────────

    def _load_wallpaper(self):
        wp_path = self._resources.get_wallpaper()
        if wp_path and os.path.isfile(wp_path):
            self._wallpaper = QPixmap(wp_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self._wallpaper and not self._wallpaper.isNull():
            scaled = self._wallpaper.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            # Centrar
            x = (self.width()  - scaled.width())  // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            # Degradado genérico XP si no hay wallpaper
            grad = QLinearGradient(0, 0, self.width(), self.height())
            grad.setColorAt(0.0, QColor("#1A6E3C"))  # verde XP
            grad.setColorAt(0.5, QColor("#2B7FBF"))  # azul XP
            grad.setColorAt(1.0, QColor("#1A5C8A"))
            painter.fillRect(self.rect(), grad)
        painter.end()

    # ── Iconos del escritorio ─────────────────────────────────────────────

    def _populate_icons(self):
        """Crea iconos para las aplicaciones marcadas con desktop_icon=True."""
        for i, app_def in enumerate(self._registry.desktop_apps()):
            icon_path = self._resources.get_icon_path(app_def.icon_key)
            pix = QPixmap(icon_path) if icon_path else None
            icon = DesktopIcon(
                label=app_def.name,
                emoji=app_def.emoji,
                pixmap=pix,
                parent=self._work_area,
            )
            x = ICON_GRID_START.x()
            y = ICON_GRID_START.y() + i * ICON_SPACING_Y
            icon.move(x, y)
            icon.show()

            # Conectar eventos
            app_id = app_def.app_id
            icon.activated.connect(lambda aid=app_id: self._launch_app(aid))
            icon.selected.connect(self._on_icon_selected)
            self._icons.append(icon)

    def _on_icon_selected(self, selected_icon: DesktopIcon) -> None:
        """Deselecciona todos los iconos excepto el seleccionado."""
        for icon in self._icons:
            if icon is not selected_icon:
                icon.set_selected(False)

    # ── Lanzar aplicaciones ───────────────────────────────────────────────

    def _launch_app(self, app_id: str) -> None:
        """
        Lanza o restaura una aplicación.
        Cada app tiene una sola instancia (si ya está abierta, se trae al frente).
        """
        # Si ya está abierta, restaurar y enfocar
        if app_id in self._open_apps:
            frame = self._open_apps[app_id]
            self._wm.restore(frame)
            return

        app_def = self._registry.get(app_id)
        if app_def is None:
            return

        # Instanciar la aplicación
        app_instance = app_def.app_class(
            resources=self._resources,
            sounds=self._sounds,
        )

        # Envolver en WindowFrame
        frame = WindowFrame(
            title=app_def.name,
            icon_emoji=app_def.emoji,
            width=720,
            height=520,
            parent=self._work_area,
        )
        frame.set_content(app_instance)

        # Centrar la ventana en el área de trabajo
        wa = self._work_area
        x = max(0, (wa.width()  - frame.width())  // 2)
        y = max(0, (wa.height() - frame.height()) // 2)
        # Escalonar ventanas si hay varias abiertas
        offset = len(self._open_apps) * 24
        frame.move(x + offset, y + offset)

        frame.show()

        # Registrar en WindowManager
        self._wm.register(frame)

        # Rastrear instancia
        self._open_apps[app_id] = frame

        # Limpiar cuando se cierre
        frame.close_requested.connect(lambda aid=app_id: self._on_app_closed(aid))
        frame.minimize_requested.connect(lambda: self._sounds.play_minimize())

        self._sounds.play_window_open()

    def _on_app_closed(self, app_id: str) -> None:
        self._open_apps.pop(app_id, None)
        self._sounds.play_window_close()

    # ── Menú Inicio ───────────────────────────────────────────────────────

    def _toggle_start_menu(self):
        if self._start_menu.isVisible():
            self._start_menu.hide()
        else:
            self._start_menu.show_above(self._taskbar)

    # ── Apagado ───────────────────────────────────────────────────────────

    def _confirm_shutdown(self):
        """Cierra la aplicación con sonido."""
        self._sounds.play_window_close()
        QApplication.quit()

    # ── Clic en el escritorio ─────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for icon in self._icons:
                icon.set_selected(False)
        if self._start_menu.isVisible():
            self._start_menu.hide()
        super().mousePressEvent(event)

    # ── Resize ────────────────────────────────────────────────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reposicionar el botón de cierre en la esquina superior derecha
        margin = 8
        self._shutdown_btn.move(
            self.width() - self._shutdown_btn.width() - margin,
            margin,
        )
        self._shutdown_btn.raise_()
