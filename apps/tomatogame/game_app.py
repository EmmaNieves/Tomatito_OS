"""
game_app.py — Integración de TOMÁte Salvajes en Tomatito.

Lanza el juego inmediatamente sin mostrar ninguna ventana intermedia.
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
        # Widget vacío, no se verá nada
        self.setFixedSize(0, 0)
        QVBoxLayout(self)

    def showEvent(self, event) -> None:
        """Al mostrarse, lanza el juego y oculta la ventana de inmediato."""
        super().showEvent(event)
        QTimer.singleShot(0, self._launch_and_hide)

    def _launch_and_hide(self) -> None:
        # Ocultar la ventana contenedora (WindowFrame del SO)
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

        launch_cmd = (
            f"import sys; sys.path.insert(0, r'{GAME_DIR}'); "
            f"import runpy; runpy.run_path(r'{GAME_MAIN}', run_name='__main__')"
        )
        self._process.start(sys.executable, ["-c", launch_cmd])

    def _on_game_finished(self, _exit_code: int, _exit_status) -> None:
        """Cuando el juego se cierra, cierra la ventana del SO."""
        win = self.window()
        if win:
            win.close()
