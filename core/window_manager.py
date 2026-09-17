"""
window_manager.py — Gestor del sistema de ventanas de Tomatito.

Responsabilidades:
- Mantener la lista de ventanas abiertas.
- Controlar el z-order (qué ventana está al frente).
- Gestionar minimizar / restaurar.
- Notificar a la barra de tareas cuando se abre/cierra una ventana.
- Proporcionar instancias únicas de apps (o múltiples, configurable).
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from widgets.window_frame import WindowFrame


class WindowManager(QObject):
    """
    Gestor central de ventanas. Se conecta con la Taskbar mediante señales Qt.
    """

    # Señales para la barra de tareas
    window_opened  = pyqtSignal(object)   # WindowFrame
    window_closed  = pyqtSignal(object)   # WindowFrame
    window_focused = pyqtSignal(object)   # WindowFrame
    window_minimized = pyqtSignal(object) # WindowFrame

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._windows: list["WindowFrame"] = []
        self._z_base = 10  # z-order mínimo para ventanas

    # ── Registro de ventanas ──────────────────────────────────────────────

    def register(self, window: "WindowFrame") -> None:
        """
        Registra una nueva ventana en el gestor.
        Conecta sus señales internas y la coloca al frente.
        """
        self._windows.append(window)

        # Conectar señales de la ventana a este gestor
        window.close_requested.connect(lambda: self._on_close(window))
        window.focus_requested.connect(lambda: self._on_focus(window))
        window.minimize_requested.connect(lambda: self._on_minimize(window))

        self._on_focus(window)
        self.window_opened.emit(window)

    def unregister(self, window: "WindowFrame") -> None:
        """Elimina una ventana del registro."""
        if window in self._windows:
            self._windows.remove(window)
            self.window_closed.emit(window)

    # ── Z-order ───────────────────────────────────────────────────────────

    def _on_focus(self, target: "WindowFrame") -> None:
        """Trae la ventana al frente actualizando el z-order de todas."""
        self._windows.sort(key=lambda w: w is target)
        for i, win in enumerate(self._windows):
            win.raise_()
            win._set_active(win is target)
        if target in self._windows:
            target.raise_()
        self.window_focused.emit(target)

    # ── Minimizar / Restaurar ─────────────────────────────────────────────

    def _on_minimize(self, window: "WindowFrame") -> None:
        window.setVisible(False)
        self.window_minimized.emit(window)

    def restore(self, window: "WindowFrame") -> None:
        """Restaura una ventana minimizada y la trae al frente."""
        window.setVisible(True)
        self._on_focus(window)

    def toggle_minimize(self, window: "WindowFrame") -> None:
        """Alterna entre minimizar y restaurar."""
        if window.isVisible():
            self._on_minimize(window)
        else:
            self.restore(window)

    # ── Consultas ─────────────────────────────────────────────────────────

    def _on_close(self, window: "WindowFrame") -> None:
        self.unregister(window)

    def get_all(self) -> list["WindowFrame"]:
        return list(self._windows)

    def count(self) -> int:
        return len(self._windows)
