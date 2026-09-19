"""
birthday_celebration.py — Overlay animado de celebración de cumpleaños para tomatitOS.
Reproduce la estética original Windows XP con overlay translúcido sobre el escritorio,
efectos de partículas (confeti, fuegos artificiales, estrellas), textos decorativos,
personajes en pixel art y ventana central de felicitación.
"""

import math
import random
import os
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QRect, QPointF, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPixmap

from core.sound_manager import SoundManager


# ── Físicas de Efectos ──────────────────────────────────────────────────

class _ConfettiParticle:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = random.choice(['#ff6b6b', '#ffd93d', '#6bcbef', '#ff9ff3', '#4cd137', '#ffbe76'])
        self.size_x = random.uniform(6, 12)
        self.size_y = random.uniform(8, 16)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-10, 10)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.22 # gravedad
        self.vx *= 0.98 # fricción del aire
        self.rotation += self.rot_speed
        
    def draw(self, painter: QPainter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.color))
        painter.drawRect(int(-self.size_x/2), int(-self.size_y/2), int(self.size_x), int(self.size_y))
        painter.restore()


class _FireworkJS:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.exploded = False
        self.particles = []
        
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        self.life = 0
        self.max_life = max(1, dist / 15.0)
        self.vx = dx / self.max_life
        self.vy = dy / self.max_life
        self.color = random.choice(['#ff6b6b', '#ffd93d', '#6bcbef', '#ff9ff3', '#ffffff', '#a29bfe'])
        self.trail = []

    def update(self):
        if not self.exploded:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 4:
                self.trail.pop(0)
            self.x += self.vx
            self.y += self.vy
            self.life += 1
            if self.life >= self.max_life:
                self.explode()
                return True # señal para sonido de explosión
        else:
            alive = []
            for p in self.particles:
                p[0] += p[2]
                p[1] += p[3]
                p[3] += 0.08
                p[2] *= 0.96
                p[3] *= 0.96
                p[4] -= 1
                if p[4] > 0:
                    alive.append(p)
            self.particles = alive
        return False

    def explode(self):
        self.exploded = True
        num = random.randint(35, 60)
        for _ in range(num):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            life = random.randint(25, 55)
            self.particles.append([
                self.x, self.y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life, life
            ])
            
    def draw(self, painter: QPainter):
        painter.save()
        if not self.exploded:
            painter.setPen(QPen(QColor(self.color), 3))
            if len(self.trail) > 1:
                for i in range(len(self.trail)-1):
                    painter.drawLine(QPointF(self.trail[i][0], self.trail[i][1]), 
                                     QPointF(self.trail[i+1][0], self.trail[i+1][1]))
        else:
            for p in self.particles:
                alpha = int(255 * (p[4] / p[5]))
                c = QColor(self.color)
                c.setAlpha(alpha)
                painter.setPen(QPen(c, 3))
                painter.drawLine(QPointF(p[0], p[1]), QPointF(p[0] - p[2]*2, p[1] - p[3]*2))
        painter.restore()

    def is_dead(self):
        return self.exploded and len(self.particles) == 0


class _TwinkleStar:
    def __init__(self, w, h):
        self.x = random.uniform(0, max(1, w))
        self.y = random.uniform(0, max(1, h))
        self.size = random.uniform(10, 18)
        self.life = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.05, 0.1)
        
    def update(self):
        self.life += self.speed
        
    def draw(self, painter: QPainter):
        painter.save()
        painter.translate(self.x, self.y)
        opacity = (math.sin(self.life) + 1) / 2 * 0.85
        c = QColor(255, 255, 255)
        c.setAlphaF(opacity)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(c)
        s = self.size
        painter.drawPolygon([QPointF(0, -s), QPointF(s/3, 0), QPointF(0, s), QPointF(-s/3, 0)])
        painter.drawPolygon([QPointF(-s, 0), QPointF(0, -s/3), QPointF(s, 0), QPointF(0, s/3)])
        painter.restore()


# ── Componentes de la Interfaz ──────────────────────────────────────────

class PixelButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(160, 44)
        self.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Sombra negra 3D retro
        painter.fillRect(4, 4, self.width()-4, self.height()-4, QColor("#000000"))
        
        # Cuerpo
        offset = 2 if self.isDown() else 0
        rect = QRect(offset, offset, self.width()-6, self.height()-6)
        
        painter.fillRect(rect, QColor("#F0EFE4"))
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawRect(rect)
        
        painter.setPen(QColor("#1E3A8A"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


class MascotWidget(QWidget):
    def __init__(self, pixmap=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(76, 76)
        self._pixmap = pixmap
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        if self._pixmap and not self._pixmap.isNull():
            # Dibujar pixel art crisp sin difuminar (FastTransformation)
            scaled = self._pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            return

        # Fallback si no hay imagen
        painter.scale(2.5, 2.5) 
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#FF4500"))
        painter.drawEllipse(4, 10, 22, 18)
        painter.setBrush(QColor("#32CD32"))
        painter.drawEllipse(12, 8, 6, 4)
        painter.setBrush(QColor("#1E6FE0"))
        painter.drawPolygon([QPointF(12, 9), QPointF(18, 9), QPointF(15, 0)])
        painter.setBrush(QColor("#FFD700"))
        painter.drawEllipse(13, -2, 4, 4)
        painter.setBrush(QColor("#000000"))
        painter.drawRect(10, 16, 2, 2)
        painter.drawRect(18, 16, 2, 2)


# ── Overlay Principal de Celebración ────────────────────────────────────

class BirthdayCelebrationOverlay(QWidget):
    def __init__(self, sounds: SoundManager | None = None, resources=None, parent: QWidget | None = None):
        super().__init__(parent)
        self._sounds = sounds
        self._resources = resources
        self._time_elapsed = 0
        
        # Cargar recursos personalizados de imágenes
        self._custom_mascot = None
        self._custom_chars = None
        if self._resources:
            mascot_path = self._resources.assets_path("images", "birthday_mascot.png")
            chars_path = self._resources.assets_path("images", "birthday_characters.png")
            
            if os.path.exists(mascot_path):
                self._custom_mascot = QPixmap(mascot_path)
            if os.path.exists(chars_path):
                self._custom_chars = QPixmap(chars_path)
        
        # Atributos de transparencia para que el escritorio siempre sea visible
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.hide()

        # Efecto de opacidad global suave
        self._master_opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._master_opacity_effect)
        self._master_opacity_effect.setOpacity(0.0)

        # ── Ventana central estilo Windows XP ─────────────────────────────
        self._win_w = 520
        self._win_h = 330
        self._window = QFrame(self)
        self._window.setFixedSize(self._win_w, self._win_h)
        self._window.setObjectName("main_window")
        self._window.setStyleSheet("""
            QFrame#main_window {
                background-color: #EFE9D8;
                border: 3px solid #0A5FC4;
            }
        """)
        
        w_layout = QVBoxLayout(self._window)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.setSpacing(0)
        
        # Barra de título azul Windows XP
        title_bar = QFrame()
        title_bar.setFixedHeight(34)
        title_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A9EFF, stop:1 #1E6FE0);
            }
            QLabel {
                color: white;
                font-family: "Courier New", "Segoe UI", sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding-left: 10px;
                background: transparent;
            }
        """)
        t_layout = QHBoxLayout(title_bar)
        t_layout.setContentsMargins(0, 0, 6, 0)
        t_layout.setSpacing(4)
        t_layout.addWidget(QLabel("¡Feliz cumpleaños!"))
        t_layout.addStretch()
        
        # Botones decorativos de minimizar/maximizar
        for _ in range(2):
            btn = QFrame()
            btn.setFixedSize(18, 18)
            btn.setStyleSheet("background-color: #3A80DF; border: 1px solid #FFFFFF; border-radius: 2px;")
            t_layout.addWidget(btn)
            
        # Botón de cerrar (X roja)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(18, 18)
        self.btn_close.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #E43D3D;
                color: white;
                border: 1px solid #FFFFFF;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        t_layout.addWidget(self.btn_close)
        w_layout.addWidget(title_bar)
        
        # Contenido interior de la ventana
        content = QFrame()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(20, 16, 20, 16)
        c_layout.setSpacing(12)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Fila superior: Tomate con gorrito + Título
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        row1.addWidget(MascotWidget(pixmap=self._custom_mascot))
        
        lbl_title = QLabel("¡Feliz cumpleaños! ❤️")
        lbl_title.setFont(QFont("Courier New", 20, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1E3A8A; background: transparent;")
        row1.addWidget(lbl_title)
        row1.addStretch()
        c_layout.addLayout(row1)
        
        # Mensaje cariñoso
        lbl_msg = QLabel(
            "Espero que hayas disfrutado el sistema\n"
            "tomatitOS, vuelve pronto."
        )
        lbl_msg.setFont(QFont("Courier New", 11))
        lbl_msg.setStyleSheet("color: #2B2B2B; background: transparent; line-height: 140%;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(lbl_msg)
        c_layout.addStretch()
        
        # Botón de interacción retro
        row_btn = QHBoxLayout()
        self.btn_gracias = PixelButton("¡Gracias! ❤️")
        row_btn.addStretch()
        row_btn.addWidget(self.btn_gracias)
        row_btn.addStretch()
        c_layout.addLayout(row_btn)
        
        w_layout.addWidget(content)

        # Conectar eventos de cierre
        self.btn_gracias.clicked.connect(self._close_celebration)
        self.btn_close.clicked.connect(self._close_celebration)
        
        # Contenedores de partículas y efectos
        self._confetti = []
        self._fireworks = []
        self._stars = []
        
        # Timer de animación (50 FPS)
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(20)
        self._anim_timer.timeout.connect(self._on_tick)

        # Animación de desvanecimiento de entrada suave
        self._scene_anim = QPropertyAnimation(self._master_opacity_effect, b"opacity")
        self._scene_anim.setDuration(1000)
        self._scene_anim.setStartValue(0.0)
        self._scene_anim.setEndValue(1.0)
        self._scene_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _reposition_window(self):
        """Posiciona la ventana centrada horizontalmente y situada elegantemente sobre los personajes."""
        w, h = self.width(), self.height()
        if hasattr(self, '_window'):
            win_x = (w - self._win_w) // 2
            # Deja espacio abajo para los personajes (~75px) y centra la ventana en el espacio restante
            chars_space = 80
            win_y = max(15, (h - chars_space - self._win_h) // 2)
            self._window.setGeometry(win_x, win_y, self._win_w, self._win_h)

    def start_sequence(self):
        """Inicia la celebración con música en bucle y efectos visuales."""
        if os.environ.get("BIRTHDAY_NO_OVERLAY", "0") == "1":
            return

        self._time_elapsed = 0
        self._confetti.clear()
        self._fireworks.clear()
        self._stars.clear()
        
        if self.parent():
            # Cubre el área del escritorio dejando libre la barra de tareas (48px)
            self.setGeometry(0, 0, self.parent().width(), self.parent().height() - 48)
            
        w, h = self.width(), self.height()
        self._stars = [_TwinkleStar(w, h) for _ in range(35)]
        
        self._reposition_window()
        self._window.show()
            
        self.show()
        self.raise_()
        self._anim_timer.start()
        self._scene_anim.start()
        
        # Disparo inicial festivo de confeti
        self._shoot_confetti()
        
        # Reproducir aplausos y música de celebración en bucle
        if self._sounds and os.environ.get("BIRTHDAY_NO_AUDIO", "0") == "0":
            self._sounds.play_birthday_applause()
            self._sounds.play_birthday_music()

    def _shoot_confetti(self):
        w, h = self.width(), self.height()
        for _ in range(35):
            self._confetti.append(_ConfettiParticle(0, h, random.uniform(5, 14), random.uniform(-10, -18)))
        for _ in range(35):
            self._confetti.append(_ConfettiParticle(w, h, random.uniform(-14, -5), random.uniform(-10, -18)))

    def _on_tick(self):
        self._time_elapsed += 20
        w, h = self.width(), self.height()
        
        # Lanzar confeti periódicamente cada 3.5 segundos
        if hasattr(self, '_confetti_timer'):
            self._confetti_timer += 20
            if self._confetti_timer >= 3500:
                self._confetti_timer = 0
                self._shoot_confetti()
        else:
            self._confetti_timer = 0
            
        # Lanzar fuegos artificiales aleatorios
        if random.random() < 0.045:
            self._fireworks.append(_FireworkJS(
                random.uniform(w * 0.05, w * 0.95), h,
                random.uniform(w * 0.1, w * 0.9), random.uniform(h * 0.08, h * 0.45)
            ))
            
        for s in self._stars:
            s.update()
            
        alive_c = []
        for c in self._confetti:
            c.update()
            if c.y < h + 50:
                alive_c.append(c)
        self._confetti = alive_c
        
        alive_fw = []
        for fw in self._fireworks:
            if fw.update():
                if self._sounds and os.environ.get("BIRTHDAY_NO_AUDIO", "0") == "0":
                    self._sounds.play_firework()
            if not fw.is_dead():
                alive_fw.append(fw)
        self._fireworks = alive_fw
        
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_window()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()

        # 1. Overlay oscuro translúcido suave sobre el escritorio (wallpaper e iconos visibles)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 60))

        # 2. Fuegos artificiales y confeti
        for fw in self._fireworks: 
            fw.draw(painter)
        for c in self._confetti: 
            c.draw(painter)

        # 3. Estrellas titilantes
        for s in self._stars: 
            s.draw(painter)

        # 4. Textos decorativos flotantes de la versión original
        try:
            painter.setFont(QFont("Comic Sans MS", 28, QFont.Weight.Bold, italic=True))
        except Exception:
            painter.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        
        # "feliz pumpe" (arriba a la izquierda, amarillo festivo)
        painter.save()
        painter.translate(w * 0.05, h * 0.16)
        painter.rotate(-8)
        painter.setPen(QColor("#FFD93D"))
        painter.drawText(0, 0, "feliz pumpe")
        painter.restore()
        
        # "tomatito" (arriba a la derecha, coral festivo)
        painter.save()
        painter.translate(w * 0.78, h * 0.16)
        painter.rotate(8)
        painter.setPen(QColor("#FF6B6B"))
        painter.drawText(0, 0, "tomatito")
        painter.restore()
        
        # "te amo" (abajo a la derecha, cian alegre)
        painter.save()
        painter.translate(w * 0.78, h * 0.72)
        painter.rotate(-5)
        painter.setPen(QColor("#6BCBEF"))
        painter.drawText(0, 0, "te amo")
        painter.restore()

        # 5. Fila de personajes en la base del overlay (encima del escritorio, bajo la ventana)
        self._draw_characters(painter, w, h)

        painter.end()

    def _draw_characters(self, painter: QPainter, w: int, h: int):
        """Dibuja los personajes con pixel art nítido (FastTransformation) justo sobre la barra de tareas."""
        if self._custom_chars and not self._custom_chars.isNull():
            # Escala con pixel art limpio sin borrosidad
            target_h = 60
            scaled = self._custom_chars.scaledToHeight(target_h, Qt.TransformationMode.FastTransformation)
            char_x = (w - scaled.width()) // 2
            char_y = h - scaled.height() - 10
            painter.drawPixmap(char_x, char_y, scaled)
            return

        # Fallback si no está la imagen
        y = h - 48
        chars = [
            {"c": "#FF4500", "x": w*0.35},
            {"c": "#FFA500", "x": w*0.42},
            {"c": "#2ECC71", "x": w*0.50},
            {"c": "#E67E22", "x": w*0.58},
            {"c": "#E74C3C", "x": w*0.65},
        ]
        for c in chars:
            painter.save()
            painter.translate(c["x"], y)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(c["c"]))
            painter.drawEllipse(-18, -25, 36, 36)
            painter.restore()

    def _close_celebration(self):
        """Cierre seguro: detiene timers, partículas, música y devuelve el control al escritorio."""
        if self._sounds:
            self._sounds.stop_birthday_music()
            
        self._scene_anim.stop()
        self._anim_timer.stop()
        self._confetti.clear()
        self._fireworks.clear()
        self._stars.clear()
        
        self.hide()
