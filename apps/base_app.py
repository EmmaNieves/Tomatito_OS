"""
base_app.py — Clase base para todas las aplicaciones de Tomatito.

Todas las apps deben heredar de BaseApp e implementar _build_ui().
Proporciona acceso a ResourceManager y SoundManager desde el constructor.
"""

from PyQt6.QtWidgets import QWidget
from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager


class BaseApp(QWidget):
    """
    Clase base para las aplicaciones del sistema Tomatito.

    Subclases deben implementar _build_ui() para construir su interfaz.
    El contenido de la app se inserta directamente en este widget,
    que luego se coloca dentro de un WindowFrame por el Desktop.
    """

    def __init__(
        self,
        resources: ResourceManager,
        sounds: SoundManager,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.resources = resources
        self.sounds = sounds
        self._build_ui()

    def _build_ui(self) -> None:
        """Construir la interfaz de la aplicación. Implementar en subclases."""
        raise NotImplementedError("Las apps deben implementar _build_ui()")
