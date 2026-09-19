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
from PyQt6.QtCore import QUrl, QObject
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
    BIRTHDAY_APPLAUSE = "birthday_applause"
    BIRTHDAY_MUSIC    = "birthday_music"
    BIRTHDAY_FIREWORK = "birthday_firework"
    FIREWORK      = "firework"

class SoundManager(QObject):
    """
    Gestor central de audio. Se instancia una vez en Desktop y se
    distribuye a los módulos que necesiten reproducir sonidos.
    """

    def __init__(self, resources: ResourceManager, parent: QObject | None = None):
        super().__init__(parent)
        self._resources = resources
        self._enabled = True
        # Cache de efectos de sonido para reutilización rápida
        self._effects: dict[str, QSoundEffect] = {}

    # ── API pública ───────────────────────────────────────────────────────

    def set_enabled(self, enabled: bool) -> None:
        """Habilita o deshabilita todos los sonidos."""
        self._enabled = enabled

    def stop(self, event: str) -> None:
        effect = self._effects.get(event)
        if effect is not None:
            effect.stop()
            
    def play(self, event: str) -> None:
        if not self._enabled:
            return

        if event not in self._effects:
            self._effects[event] = self._load_effect(event)

        effect = self._effects.get(event)
        if effect is not None:
            try:
                if hasattr(effect, 'setPosition'):
                    effect.setPosition(0)
                effect.play()
            except Exception as e:
                print(f"SOUND ERROR: {e}")

    # ── Atajos para los eventos más comunes ───────────────────────────────

    def play_startup(self)       -> None: self.play(SoundEvent.STARTUP)
    def play_click(self)         -> None: self.play(SoundEvent.CLICK)
    def play_window_open(self)   -> None: self.play(SoundEvent.WINDOW_OPEN)
    def play_window_close(self)  -> None: self.play(SoundEvent.WINDOW_CLOSE)
    def play_error(self)         -> None: self.play(SoundEvent.ERROR)
    def play_minimize(self)      -> None: self.play(SoundEvent.MINIMIZE)
    def play_notification(self)  -> None: self.play(SoundEvent.NOTIFICATION)
    def play_balloon(self)       -> None: self.play(SoundEvent.BALLOON)
    def play_birthday_applause(self)-> None: self.play(SoundEvent.BIRTHDAY_APPLAUSE)
    def play_birthday_music(self)   -> None: self.play(SoundEvent.BIRTHDAY_MUSIC)
    def stop_birthday_music(self)   -> None: self.stop(SoundEvent.BIRTHDAY_MUSIC)
    def play_birthday_firework(self)-> None: self.play(SoundEvent.BIRTHDAY_FIREWORK)
    def play_firework(self)      -> None: self.play(SoundEvent.FIREWORK)

    # ── Helpers internos ──────────────────────────────────────────────────

    def _load_effect(self, name: str):
        """Carga un efecto desde assets/sounds/. Devuelve QSoundEffect o QMediaPlayer."""
        path = self._resources.get_sound_path(name)
        if path is None:
            return None
        try:
            ext = __import__("os").path.splitext(path)[1].lower()
            if ext == ".wav":
                effect = QSoundEffect(self)
                effect.setSource(QUrl.fromLocalFile(path))
                if name == SoundEvent.BIRTHDAY_MUSIC:
                    effect.setLoopCount(-2)
                effect.setVolume(0.8)
                return effect
            else:
                from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
                player = QMediaPlayer(self)
                audio = QAudioOutput(self)
                audio.setVolume(0.8)
                player.setAudioOutput(audio)
                player.setSource(QUrl.fromLocalFile(path))
                # Mantener vivo el audio output
                player.setProperty("audio_out", audio)
                if name == SoundEvent.BIRTHDAY_MUSIC:
                    player.setLoops(-1)
                return player
        except Exception as e:
            print(f"SOUND ERROR: {e}")
            return None
