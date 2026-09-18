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


import logging
import traceback
import sys

# Configuración de logging de diagnóstico (Flush inmediato a bajo nivel)
log_file = os.path.join(BASE_DIR, "debug_output.txt")

# Borrar handlers previos si los hay
root_logger = logging.getLogger()
if root_logger.hasHandlers():
    root_logger.handlers.clear()
root_logger.setLevel(logging.DEBUG)

class ImmediateFlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

# Crear el handler
file_handler = ImmediateFlushFileHandler(log_file, mode='w', encoding='utf-8')
formatter = logging.Formatter("[%(asctime)s.%(msecs)03d] %(message)s", datefmt="%H:%M:%S")
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.critical("========== UNHANDLED EXCEPTION ==========")
    logging.critical("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    logging.critical("=========================================")
    # Asegurar flush en excepciones
    for h in logging.getLogger().handlers:
        h.flush()
sys.excepthook = handle_exception

def qt_message_handler(mode, context, message):
    msg = f"QtMessage: {message} (file: {context.file}, line: {context.line})"
    if mode == QtMsgType.QtDebugMsg:
        logging.debug(msg)
    elif mode == QtMsgType.QtInfoMsg:
        logging.info(msg)
    elif mode == QtMsgType.QtWarningMsg:
        logging.warning(msg)
    elif mode == QtMsgType.QtCriticalMsg:
        logging.critical(msg)
    elif mode == QtMsgType.QtFatalMsg:
        logging.critical(f"FATAL: {msg}")
        
from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
qInstallMessageHandler(qt_message_handler)

# FLAGS DE DIAGNÓSTICO (El usuario puede cambiarlos)
BIRTHDAY_DIAGNOSTIC_NO_AUDIO = False
BIRTHDAY_DIAGNOSTIC_NO_OVERLAY = False
BIRTHDAY_DIAGNOSTIC_NO_TIMER = False
os.environ["BIRTHDAY_NO_AUDIO"] = "1" if BIRTHDAY_DIAGNOSTIC_NO_AUDIO else "0"
os.environ["BIRTHDAY_NO_OVERLAY"] = "1" if BIRTHDAY_DIAGNOSTIC_NO_OVERLAY else "0"
os.environ["BIRTHDAY_NO_TIMER"] = "1" if BIRTHDAY_DIAGNOSTIC_NO_TIMER else "0"

def main() -> None:
    logging.info("================ STARTING TOMATITO OS ================")
    
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("tomatitOS")
    app.setApplicationDisplayName("tomatitOS")
    
    app.aboutToQuit.connect(lambda: logging.info("[APP] aboutToQuit emitted"))

    default_font = QFont("Tahoma", 9)
    app.setFont(default_font)
    app.setStyleSheet(QSS_THEME)

    resources = ResourceManager()
    sounds    = SoundManager(resources)
    registry  = AppRegistry()

    from PyQt6.QtGui import QIcon
    icon_path = resources.get_icon_path("tomatito")
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))

    _register_apps(registry)

    splash = SplashScreen(sounds=sounds)
    desktop = Desktop(resources, sounds, registry)
    
    desktop.destroyed.connect(lambda: logging.info("[DESKTOP] DESTROYED"))
    
    desktop.showFullScreen()
    splash.raise_()
    splash.activateWindow()

    def _on_splash_finished():
        desktop.raise_()
        desktop.activateWindow()
        splash.deleteLater()

    splash.finished.connect(_on_splash_finished)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
