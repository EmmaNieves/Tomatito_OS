"""
birthday_celebration.py — Overlay animado de celebración de cumpleaños para tomatitOS.

Muestra partículas de confeti, efectos de aplausos, revelación de mensaje
y sonido especial cuando se completa el juego o se activa el evento.
"""

import math
import random

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush

from core.sound_manager import SoundManager


class _Particle:
    """Partícula de confeti / estrella / corazón."""

    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.reset()
        self.y = random.uniform(0, h)

    def reset(self):
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(-40, -10)
        self.size = random.uniform(6, 12)
        self.speed_y = random.uniform(2, 5)
        self.speed_x = random.uniform(-1.5, 1.5)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-4, 4)
        colors = [
            QColor(255, 99, 132),   # Rosa/Rojo
            QColor(54, 162, 235),   # Azul
            QColor(255, 206, 86),   # Amarillo
            QColor(75, 192, 192),   # Verde
            QColor(153, 102, 255),  # Violeta
            QColor(255, 159, 64),   # Naranja
        ]
        self.color = random.choice(colors)

    def update(self):
        self.y += self.speed_y
        self.x += math.sin(self.y * 0.05) + self.speed_x
        self.rotation += self.rot_speed
        if self.y > self.h + 20:
            self.reset()


class BirthdayCelebrationOverlay(QWidget):
    """Overlay de pantalla completa para la celebración de cumpleaños."""

    def __init__(self, sounds: SoundManager | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self._sounds = sounds
        self._step = 0
        self._opacity = 0.0
        self._text_stage = 0
        self._particles: list[_Particle] = []

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(20)
        self._anim_timer.timeout.connect(self._on_tick)

        self._timer_phase1 = QTimer(self)
        self._timer_phase1.setSingleShot(True)
        self._timer_phase1.timeout.connect(self._phase_1_reveal)

        self._timer_phase2 = QTimer(self)
        self._timer_phase2.setSingleShot(True)
        self._timer_phase2.timeout.connect(self._phase_2_applause)

    def start_sequence(self):
        """Inicia la secuencia de celebración con la pausa de 1 segundo."""
        self._opacity = 0.0
        self._text_stage = 0
        self._timer_phase1.stop()
        self._timer_phase2.stop()
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

        # 1 segundo de silencio
        self._timer_phase1.start(1000)

    def _phase_1_reveal(self):
        # Generar partículas
        w, h = self.width(), self.height()
        self._particles = [_Particle(w, h) for _ in range(90)]

        # Sonido de revelación / campana
        if self._sounds:
            self._sounds.play_balloon()

        self._anim_timer.start()
        self._text_stage = 1

        # Pasar a la siguiente frase y aplausos en 3.5 segundos
        self._timer_phase2.start(3500)

    def _phase_2_applause(self):
        self._text_stage = 2
        if self._sounds:
            self._sounds.play_notification()

    def _on_tick(self):
        if self._opacity < 1.0:
            self._opacity = min(1.0, self._opacity + 0.03)

        for p in self._particles:
            p.update()

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        # Fondo oscuro semitransparente
        bg = QColor(6, 12, 24, int(self._opacity * 225))
        painter.fillRect(self.rect(), bg)

        if self._opacity < 0.1:
            painter.end()
            return

        # Dibujar partículas de confeti
        for p in self._particles:
            painter.save()
            painter.translate(p.x, p.y)
            painter.rotate(p.rotation)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(p.color))
            painter.drawRect(int(-p.size / 2), int(-p.size / 2), int(p.size), int(p.size))
            painter.restore()

        # Texto del Mensaje Principal
        if self._text_stage >= 1:
            # Sombra
            painter.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
            painter.setPen(QColor(0, 0, 0, 200))
            painter.drawText(QRect(cx - 302, cy - 88, 604, 80), Qt.AlignmentFlag.AlignCenter, "🎉  Feliz cumpleaños  ❤️")

            # Título Dorado Resplandeciente
            painter.setPen(QColor(255, 215, 0))
            painter.drawText(QRect(cx - 300, cy - 90, 600, 80), Qt.AlignmentFlag.AlignCenter, "🎉  Feliz cumpleaños  ❤️")

        # Texto Secundario
        if self._text_stage >= 2:
            msg = "Espero que hayas disfrutado del sistema tomatitOS, vuelve pronto"
            painter.setFont(QFont("Tahoma", 13))
            painter.setPen(QColor(230, 240, 255, 230))
            painter.drawText(QRect(cx - 350, cy + 20, 700, 50), Qt.AlignmentFlag.AlignCenter, msg)

            # Indicador para cerrar
            painter.setFont(QFont("Tahoma", 10))
            painter.setPen(QColor(160, 180, 210, 180))
            painter.drawText(QRect(cx - 200, h - 50, 400, 30), Qt.AlignmentFlag.AlignCenter, "( Haz clic en cualquier lugar para continuar )")

        painter.end()

    def mousePressEvent(self, event):
        if self._text_stage >= 2:
            self._anim_timer.stop()
            self._timer_phase1.stop()
            self._timer_phase2.stop()
            self.hide()
            self.close()
        super().mousePressEvent(event)
