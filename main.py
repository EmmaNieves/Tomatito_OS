"""
main.py — Punto de entrada de Tomatito.exe

Flujo de arranque:
  1. Inicializar Qt + subsistemas (ResourceManager, SoundManager, AppRegistry).
  2. Mostrar SplashScreen con animación y sonido de inicio.
  3. Al terminar el splash, mostrar el Desktop.

Para añadir una nueva aplicación en el futuro:
  1. Crear la clase en apps/<nombre>/
  2. Añadir registry.register(...) en _register_apps()
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path de importación.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager
from core.app_registry import AppRegistry, AppDefinition
from core.splash_screen import SplashScreen
from core.desktop import Desktop
from styles.xp_theme import QSS_THEME


def _register_apps(registry: AppRegistry) -> None:
    """
    Registro central de aplicaciones del sistema.
    ── Añadir nuevas apps aquí cuando llegue el momento ────────────────────
    Ejemplo:
        from apps.music.music_app import MusicApp
        registry.register(AppDefinition(
            app_id="music", name="Reproductor", icon_key="music",
            emoji="🎵", app_class=MusicApp, desktop_icon=True, start_menu=True,
        ))
    ────────────────────────────────────────────────────────────────────────
    """
    from apps.gallery.gallery_app import GalleryApp
    from apps.tomatogame.game_app import GameApp
    from apps.music.music_app import MusicApp
    from apps.camera.camera_app import CameraApp

    registry.register(AppDefinition(
        app_id      = "gallery",
        name        = "Mis imágenes",
        icon_key    = "my_pictures",
        emoji       = "📁",
        app_class   = GalleryApp,
        desktop_icon= True,
        start_menu  = True,
        description = "Galería de fotografías",
    ))

    registry.register(AppDefinition(
        app_id      = "tomatogame",
        name        = "TOMÁte Salvajes",
        icon_key    = "tomatogame",
        emoji       = "🍅",
        app_class   = GameApp,
        desktop_icon= True,
        start_menu  = True,
        description = "Juego de plataformas",
    ))

    registry.register(AppDefinition(
        app_id      = "music",
        name        = "Reproductor",
        icon_key    = "my_pictures",
        emoji       = "🎵",
        app_class   = MusicApp,
        desktop_icon= True,
        start_menu  = True,
        description = "Reproductor de música retro",
    ))

    registry.register(AppDefinition(
        app_id      = "camera",
        name        = "Cámara",
        icon_key    = "my_pictures",
        emoji       = "📷",
        app_class   = CameraApp,
        desktop_icon= True,
        start_menu  = True,
        description = "Cámara digital Cyber-shot 2000s",
    ))


def main() -> None:
    # Habilitar DPI alto antes de crear QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("tomatitOS")
    app.setApplicationDisplayName("tomatitOS")

    # Fuente por defecto (Tahoma es emblemática de XP)
    default_font = QFont("Tahoma", 9)
    app.setFont(default_font)

    # Aplicar tema global
    app.setStyleSheet(QSS_THEME)

    # Inicializar subsistemas
    resources = ResourceManager()
    sounds    = SoundManager(resources)
    registry  = AppRegistry()

    # Asignar icono global de la aplicación (barra de tareas y ventanas)
    from PyQt6.QtGui import QIcon
    icon_path = resources.get_icon_path("tomatito")
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))

    _register_apps(registry)

    # Crear el Desktop inmediatamente para evitar parpadeos o salir de la app
    desktop = Desktop(resources, sounds, registry)

    # Mostrar splash screen como overlay sobre el escritorio
    splash = SplashScreen(sounds=sounds, parent=desktop)
    splash.finished.connect(splash.deleteLater)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
