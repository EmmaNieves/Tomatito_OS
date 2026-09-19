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
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer
from PyQt6.QtGui import QPainter, QPixmap, QColor, QLinearGradient, QFont

from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager
from core.app_registry import AppRegistry, AppDefinition
from core.window_manager import WindowManager
from core.taskbar import Taskbar
from core.start_menu import StartMenu
from core.event_manager import EventManager
from widgets.desktop_icon import DesktopIcon
from widgets.window_frame import WindowFrame
from widgets.birthday_celebration import BirthdayCelebrationOverlay
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
        self.setToolTip("Cerrar tomatitOS")
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
        self._visited_apps: set[str] = set()           # Apps abiertas durante esta sesión

        self._event_manager = EventManager(self)
        self._birthday_overlay = BirthdayCelebrationOverlay(
            sounds=self._sounds, 
            resources=self._resources, 
            parent=self
        )
        self._birthday_overlay.destroyed.connect(lambda: __import__('logging').info("[BIRTHDAY] OVERLAY DESTROYED"))
        self._event_manager.event_triggered.connect(self._on_event_triggered)

        # Quitar decoración del sistema operativo host
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._wm = WindowManager(self)
        self._build_ui()
        self._load_wallpaper()
        self._populate_icons()

    def _on_event_triggered(self, event_name: str) -> None:
        if event_name == "GAME_COMPLETED":
            # Pausar la música si está sonando
            if "music" in self._open_apps:
                try:
                    from PyQt6.QtMultimedia import QMediaPlayer
                    music_app = self._open_apps["music"]._content_layout.itemAt(0).widget()
                    if hasattr(music_app, "_player") and music_app._player:
                        if music_app._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                            music_app._player.pause()
                except Exception:
                    pass
            if not self._birthday_overlay.isVisible():
                self._birthday_overlay.start_sequence()

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
        self._start_menu = StartMenu(self._registry, self._resources, self)
        self._start_menu.app_launched.connect(self._launch_app)

        # Botón de cierre (en el escritorio, detrás de las ventanas)
        self._shutdown_btn = _ShutdownButton(self._work_area)
        self._shutdown_btn.clicked.connect(self._confirm_shutdown)
        self._shutdown_btn.lower()

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
        # Si abre el juego, pausar música si está sonando
        if app_id == "tomatogame":
            if "music" in self._open_apps:
                try:
                    from PyQt6.QtMultimedia import QMediaPlayer
                    music_frame = self._open_apps["music"]
                    music_app = music_frame._content_layout.itemAt(0).widget()
                    if hasattr(music_app, "_player") and music_app._player:
                        if music_app._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                            music_app._player.pause()
                            self._music_paused_by_game = True
                except Exception:
                    pass

        # Si ya está abierta, restaurar y enfocar
        if app_id in self._open_apps:
            frame = self._open_apps[app_id]
            self._wm.restore(frame)
            return

        # Registrar que el usuario ha visitado esta app
        self._visited_apps.add(app_id)

        app_def = self._registry.get(app_id)
        if app_def is None:
            return

        # Instanciar la aplicación
        app_instance = app_def.app_class(
            resources=self._resources,
            sounds=self._sounds,
        )
        if hasattr(app_instance, "set_event_manager"):
            app_instance.set_event_manager(self._event_manager)

        # Envolver en WindowFrame
        frame = WindowFrame(
            title=app_def.name,
            icon_emoji=app_def.emoji,
            width=720,
            height=520,
            parent=self._work_area,
        )
        frame.destroyed.connect(lambda f=frame, t=app_def.name: __import__('logging').info(f"[WINDOW] DESTROYED: {t}"))
        frame.set_content(app_instance)

        # Centrar la ventana en el área de trabajo
        wa = self._work_area
        x = max(0, (wa.width()  - frame.width())  // 2)
        y = max(0, (wa.height() - frame.height()) // 2)
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
        import logging
        logging.info(f"[DESKTOP] _on_app_closed() ENTER para {app_id}")
        logging.info(f"[DESKTOP] _open_apps before = {len(self._open_apps)}")
        try:
            self._open_apps.pop(app_id, None)
            logging.info(f"[DESKTOP] _open_apps after = {len(self._open_apps)}")
            self._sounds.play_window_close()
            
            # Reanudar música si se cerró el juego
            if app_id == "tomatogame" and getattr(self, "_music_paused_by_game", False):
                self._music_paused_by_game = False
                if "music" in self._open_apps:
                    try:
                        music_app = self._open_apps["music"]._content_layout.itemAt(0).widget()
                        if hasattr(music_app, "_player") and music_app._player:
                            music_app._player.play()
                            if hasattr(music_app, "_btn_play"): music_app._btn_play.setText("⏸")
                            if hasattr(music_app, "_lbl_now"): music_app._lbl_now.setText("▶  REPRODUCIENDO")
                            if hasattr(music_app, "_visualizer"): music_app._visualizer.set_playing(True)
                    except Exception:
                        pass
            
            logging.info(f"[DESKTOP] Llamando a _check_birthday_condition()")
            self._check_birthday_condition()
        except Exception as e:
            logging.error(f"[DESKTOP] Error en _on_app_closed: {e}")
        logging.info(f"[DESKTOP] _on_app_closed() EXIT")

    def _check_birthday_condition(self) -> None:
        import logging
        import os
        logging.info(f"[DESKTOP] _check_birthday_condition() ENTER")
        try:
            # Evitar reentrancia: asegurar que solo se dispare una vez por sesión
            if getattr(self, "_birthday_triggered", False):
                logging.info("[BIRTHDAY] Condition ya fue disparada (bloqueada reentrancia).")
                return

            all_app_ids = {app_def.app_id for app_def in self._registry.all()}
            logging.info(f"[BIRTHDAY] visited: {len(self._visited_apps)}, total: {len(all_app_ids)}, open: {len(self._open_apps)}")
            
            if len(self._visited_apps) >= len(all_app_ids) or self._visited_apps.issuperset(all_app_ids):
                if len(self._open_apps) == 0:
                    logging.info("[BIRTHDAY] Condition satisfied")
                    if not self._event_manager.has_occurred("GAME_COMPLETED"):
                        self._birthday_triggered = True
                        if os.environ.get("BIRTHDAY_NO_TIMER", "0") == "1":
                            logging.info("[BIRTHDAY] Diagnostic: NO_TIMER is True, triggering synchronously")
                            self._event_manager.trigger("GAME_COMPLETED")
                        else:
                            logging.info("[BIRTHDAY] Scheduling celebration (QTimer 500ms)")
                            self._birthday_timer = QTimer(self)
                            self._birthday_timer.setSingleShot(True)
                            self._birthday_timer.setInterval(500)
                            self._birthday_timer.timeout.connect(lambda: self._event_manager.trigger("GAME_COMPLETED"))
                            self._birthday_timer.start()
        except Exception as e:
            logging.error(f"[BIRTHDAY] Error checking condition: {e}")
        logging.info(f"[DESKTOP] _check_birthday_condition() EXIT")

    def closeEvent(self, event):
        import logging
        logging.info(f"[DESKTOP] closeEvent CALLED. Visible={self.isVisible()}, Active={self.isActiveWindow()}, ClosingDown={QApplication.closingDown()}")
        if hasattr(self, "_birthday_timer") and self._birthday_timer is not None:
            try:
                self._birthday_timer.stop()
                self._birthday_timer = None
            except Exception:
                pass
        if hasattr(self, "_birthday_overlay") and self._birthday_overlay is not None:
            try:
                self._birthday_overlay.hide()
            except Exception:
                pass
        super().closeEvent(event)

    # ── Menú Inicio ───────────────────────────────────────────────────────

    def _toggle_start_menu(self):
        if self._start_menu.isVisible():
            self._start_menu.hide()
        else:
            self._start_menu.show_above(self._taskbar)

    # ── Apagado ───────────────────────────────────────────────────────────

    def _confirm_shutdown(self):
        """Cierra la aplicación con sonido."""
        import logging
        logging.info("[DESKTOP] _confirm_shutdown CALLED (user pressed power button)")
        self._sounds.play_window_close()
        QApplication.quit()

    # ── Clic y Teclas en el escritorio ──────────────────────────────────

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F12 or (
            event.key() == Qt.Key.Key_B and (event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        ):
            self._event_manager.trigger("GAME_COMPLETED")
        super().keyPressEvent(event)

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
        # Reposicionar el botón de cierre en la esquina superior derecha del escritorio
        margin = 8
        self._shutdown_btn.move(
            self._work_area.width() - self._shutdown_btn.width() - margin,
            margin,
        )
        self._shutdown_btn.lower()
        if hasattr(self, "_birthday_overlay"):
            self._birthday_overlay.setGeometry(0, 0, self.width(), self.height() - 48)
