"""
game_app.py — Integración de TOMÁte Salvajes en tomatitOS.

Lanza el juego inmediatamente y fuerza la ventana de Pygame
al frente para evitar que se abra detrás de otras aplicaciones.
"""

import sys
import os

from PyQt6.QtWidgets import QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QProcess, QTimer

from apps.base_app import BaseApp
from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager


def _game_dir() -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
        return os.path.join(base, "apps", "tomatogame")
    return os.path.dirname(os.path.abspath(__file__))


GAME_DIR = _game_dir()
GAME_MAIN = os.path.join(GAME_DIR, "main.py")


class GameApp(BaseApp):
    """Lanza TOMÁte Salvajes sin mostrar ventana intermedia."""

    def __init__(self, resources: ResourceManager, sounds: SoundManager, parent=None):
        self._process: QProcess | None = None
        super().__init__(resources, sounds, parent)

    def _build_ui(self) -> None:
        self.setFixedSize(0, 0)
        QVBoxLayout(self)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._launch_and_hide)

    def _launch_and_hide(self) -> None:
        win = self.window()
        if win:
            win.hide()
        self._launch_game()

    def _launch_game(self) -> None:
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            return

        self._process = QProcess(self)
        self._process.setWorkingDirectory(GAME_DIR)
        self._process.finished.connect(self._on_game_finished)

        # Comando que lanza el juego e inicia un hilo para traer la ventana al frente
        launch_cmd = (
            f"import sys, os, time, ctypes, threading; "
            f"sys.path.insert(0, r'{GAME_DIR}'); "
            f"def _focus(): "
            f"  time.sleep(0.4); "
            f"  try: "
            f"    u = ctypes.windll.user32; "
            f"    h = u.GetForegroundWindow(); "
            f"    u.ShowWindow(h, 5); "
            f"    u.SetForegroundWindow(h); "
            f"  except: pass; "
            f"threading.Thread(target=_focus, daemon=True).start(); "
            f"import runpy; runpy.run_path(r'{GAME_MAIN}', run_name='__main__')"
        )
        self._process.start(sys.executable, ["-c", launch_cmd])

    def _on_game_finished(self, _exit_code: int, _exit_status) -> None:
        """Cuando el juego se cierra, vuelve a mostrar tomatitOS y cierra la app."""
        desktop_win = self.window()
        if desktop_win:
            desktop_win.show()
            desktop_win.showFullScreen()
            desktop_win.raise_()
            desktop_win.activateWindow()

        frame = self.parentWidget()
        while frame and not hasattr(frame, "close_requested"):
            frame = frame.parentWidget()
        if frame:
            frame.close()
