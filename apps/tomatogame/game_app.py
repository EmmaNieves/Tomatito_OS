"""
game_app.py — Integración de TOMÁte Salvajes en tomatitOS.

Lanza el juego en su propio proceso exactamente una vez.
Cierra y restaura la pantalla de tomatitOS al finalizar.
"""

import sys
import os

from PyQt6.QtWidgets import QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QProcess, QTimer, QProcessEnvironment

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
        self._has_launched: bool = False
        self._event_manager = None
        super().__init__(resources, sounds, parent)

    def set_event_manager(self, event_manager) -> None:
        self._event_manager = event_manager

    def _build_ui(self) -> None:
        self.setFixedSize(0, 0)
        QVBoxLayout(self)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self._has_launched:
            self._has_launched = True
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

        env = QProcessEnvironment.systemEnvironment()
        env.insert("SDL_VIDEO_WINDOW_POS", "center")
        self._process.setProcessEnvironment(env)

        launch_cmd = (
            f"import sys; sys.path.insert(0, r'{GAME_DIR}'); "
            f"import runpy; runpy.run_path(r'{GAME_MAIN}', run_name='__main__')"
        )
        self._process.start(sys.executable, ["-c", launch_cmd])

    def _on_game_finished(self, _exit_code: int, _exit_status) -> None:
        """Cuando el juego se cierra, vuelve a mostrar tomatitOS y cierra la app."""
        flag_path = os.path.join(GAME_DIR, ".game_won")
        game_completed = os.path.exists(flag_path)
        if game_completed:
            try:
                os.remove(flag_path)
            except Exception:
                pass

        desktop_win = self.window()
        if desktop_win:
            desktop_win.show()
            desktop_win.showFullScreen()
            desktop_win.raise_()
            desktop_win.activateWindow()

        if game_completed and self._event_manager:
            self._event_manager.trigger("GAME_COMPLETED")

        frame = self.parentWidget()
        while frame and not hasattr(frame, "close_requested"):
            frame = frame.parentWidget()
        if frame:
            frame.close()
