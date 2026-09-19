"""
app_registry.py — Registro modular de aplicaciones de Tomatito.

Para añadir una nueva aplicación en el futuro basta con:
  1. Crear la clase en apps/<nombre>/
  2. Registrarla aquí con AppRegistry.register(...)

El escritorio, el menú Inicio y los iconos de escritorio consultan
este registro. No es necesario tocar ningún otro archivo del core.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.base_app import BaseApp


@dataclass
class AppDefinition:
    """Descriptor de una aplicación registrada."""
    app_id: str           # Identificador único (ej. "gallery")
    name: str             # Nombre para mostrar (ej. "Mis imágenes")
    icon_key: str         # Clave de icono en ResourceManager (ej. "my_pictures")
    emoji: str            # Emoji de respaldo si no hay icono (ej. "📁")
    app_class: type       # Clase que hereda BaseApp
    desktop_icon: bool    # ¿Aparece en el escritorio?
    start_menu: bool      # ¿Aparece en el menú Inicio?
    description: str = "" # Descripción breve (opcional)


class AppRegistry:
    """
    Registro central de aplicaciones disponibles en el sistema.
    Se instancia una vez y se comparte entre Desktop, StartMenu y WindowManager.
    """

    def __init__(self):
        self._apps: dict[str, AppDefinition] = {}

    def register(self, definition: AppDefinition) -> None:
        """Registra una aplicación. Lanza error si el ID ya existe."""
        if definition.app_id in self._apps:
            raise ValueError(f"App '{definition.app_id}' ya está registrada.")
        self._apps[definition.app_id] = definition

    def get(self, app_id: str) -> AppDefinition | None:
        """Devuelve la definición de una app por su ID."""
        return self._apps.get(app_id)

    def all(self) -> list[AppDefinition]:
        """Devuelve todas las aplicaciones registradas en orden de registro."""
        return list(self._apps.values())

    def desktop_apps(self) -> list[AppDefinition]:
        """Aplicaciones que deben aparecer como iconos en el escritorio."""
        return [a for a in self._apps.values() if a.desktop_icon]

    def start_menu_apps(self) -> list[AppDefinition]:
        """Aplicaciones que deben aparecer en el menú Inicio."""
        return [a for a in self._apps.values() if a.start_menu]
