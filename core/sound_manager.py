"""
sound_manager.py — Gestor de audio de Tomatito.

Características:
- Reproduce sonidos desde assets/sounds/ mediante ResourceManager.
- Usa QtMultimedia (incluido en PyQt6) sin dependencias extra.
- Falla silenciosamente: si el archivo no existe o hay error de audio,
  la aplicación continúa sin interrupción.
- Soporte para habilitar/deshabilitar sonidos globalmente.
"""

from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
from core.resource_manager import ResourceManager


# Nombres de sonido estándar del sistema
class SoundEvent:
    STARTUP       = "startup"
    CLICK         = "click"
    WINDOW_OPEN   = "window_open"
    WINDOW_CLOSE  = "window_close"
    ERROR         = "error"
    NOTIFICATION  = "notification"
    MINIMIZE      = "minimize"
    BALLOON       = "balloon"


class SoundManager:
    """
    Gestor central de audio. Se instancia una vez en Desktop y se
    distribuye a los módulos que necesiten reproducir sonidos.
    """

    def __init__(self, resources: ResourceManager):
        self._resources = resources
        self._enabled = True
        # Cache de efectos de sonido para reutilización rápida
        self._effects: dict[str, QSoundEffect] = {}

    # ── API pública ───────────────────────────────────────────────────────

    def set_enabled(self, enabled: bool) -> None:
        """Habilita o deshabilita todos los sonidos."""
        self._enabled = enabled

    def play(self, event: str) -> None:
        """
        Reproduce el sonido asociado a un evento.
        Si el archivo no existe o hay error, no hace nada.
        """
        if not self._enabled:
            return

        if event not in self._effects:
            self._effects[event] = self._load_effect(event)

        effect = self._effects[event]
        if effect is not None:
            effect.play()

    # ── Atajos para los eventos más comunes ───────────────────────────────

    def play_startup(self)       -> None: self.play(SoundEvent.STARTUP)
    def play_click(self)         -> None: self.play(SoundEvent.CLICK)
    def play_window_open(self)   -> None: self.play(SoundEvent.WINDOW_OPEN)
    def play_window_close(self)  -> None: self.play(SoundEvent.WINDOW_CLOSE)
    def play_error(self)         -> None: self.play(SoundEvent.ERROR)
    def play_minimize(self)      -> None: self.play(SoundEvent.MINIMIZE)
    def play_notification(self)  -> None: self.play(SoundEvent.NOTIFICATION)
    def play_balloon(self)       -> None: self.play(SoundEvent.BALLOON)

    # ── Helpers internos ──────────────────────────────────────────────────

    def _load_effect(self, name: str) -> "QSoundEffect | None":
        """Carga un QSoundEffect desde assets/sounds/. Devuelve None si falla."""
        path = self._resources.get_sound_path(name)
        if path is None:
            return None
        try:
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(path))
            effect.setVolume(0.8)
            return effect
        except Exception:
            return None
