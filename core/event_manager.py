"""
event_manager.py — Sistema central de eventos especiales de tomatitOS.

Maneja sorpresas y momentos especiales como GAME_COMPLETED y BirthdayCelebration.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class EventManager(QObject):
    """Gestor de eventos especiales e interacciones ocultas."""

    event_triggered = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._history: set[str] = set()

    def trigger(self, event_name: str) -> None:
        """Dispara un evento especial (ej. GAME_COMPLETED)."""
        self._history.add(event_name)
        self.event_triggered.emit(event_name)

    def has_occurred(self, event_name: str) -> bool:
        """Devuelve True si el evento ya se ha completado en la sesión."""
        return event_name in self._history
