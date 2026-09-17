"""
splash_screen.py — Pantalla de inicio animada estilo Windows XP.

Muestra una secuencia de arranque antes de que aparezca el escritorio:
  1. Fade-in del fondo negro con el logo "Tomatito".
  2. Barra de progreso animada estilo XP (bloques que se desplazan).
  3. Fade-out y señal de "listo" al Desktop.

Se reproduce el startup.wav de fondo durante la animación.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QRect, QPoint
)
from PyQt6.QtGui import (
    QPainter, QColor, QLinearGradient, QFont, QPen, QRadialGradient
)


# ── Barra de progreso XP ──────────────────────────────────────────────────

class _XPProgressBar(QWidget):
    """
    Barra de progreso estilo Windows XP: bloques azules que se desplazan
    infinitamente de izquierda a derecha.
    """
    BAR_HEIGHT   = 14
    BLOCK_WIDTH  = 12
    BLOCK_GAP    = 3
    BLOCK_COUNT  = 5
    SPEED_PX     = 2     # píxeles que avanza por tick

    def __init__(self, width: int = 220, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, self.BAR_HEIGHT + 4)
        self._offset = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self._timer.start(16)   # ~60fps

    def stop(self):
        self._timer.stop()

    def _tick(self):
        stride = self.BLOCK_WIDTH + self.BLOCK_GAP
        self._offset = (self._offset + self.SPEED_PX) % stride
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.BAR_HEIGHT

        # Fondo de la barra (hueco oscuro)
        painter.fillRect(0, 2, w, h, QColor("#111111"))
        # Borde
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawRect(0, 2, w - 1, h - 1)

        # Bloques azules desplazables
        stride = self.BLOCK_WIDTH + self.BLOCK_GAP
        x = -stride + self._offset
        while x < w:
            grad = QLinearGradient(x, 2, x, 2 + h)
            grad.setColorAt(0.0, QColor("#6AACE8"))
            grad.setColorAt(0.5, QColor("#2070C8"))
            grad.setColorAt(1.0, QColor("#1050A0"))
            painter.fillRect(int(x) + 2, 4, self.BLOCK_WIDTH, h - 4, grad)
            x += stride

        painter.end()


# ── Splash Screen principal ───────────────────────────────────────────────

class SplashScreen(QWidget):
    """
    Pantalla de inicio de Tomatito.

    Señales:
        finished — emitida cuando la animación completa y el escritorio debe aparecer.
    """

    finished = pyqtSignal()

    # Duración total de la animación en ms
    FADE_IN_MS    = 600
    HOLD_MS       = 2800
    FADE_OUT_MS   = 500

    def __init__(self, sounds=None, parent=None):
        super().__init__(parent)
        self._sounds   = sounds
        self._opacity  = 0.0      # 0.0 → 1.0
        self._phase    = "fade_in"
        self._elapsed  = 0

        # Sin decoración, siempre encima
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()
        self.showFullScreen()
        self._start_animation()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Barra de progreso
        self._progress = _XPProgressBar(220, self)

        # Etiqueta "Iniciando..." debajo de la barra
        self._hint_label = QLabel("Iniciando el sistema…", self)
        self._hint_label.setStyleSheet(
            "color: #AAAAAA; font-family: Tahoma; font-size: 11px;"
        )
        self._hint_label.adjustSize()

    def _reposition_widgets(self):
        cx = self.width()  // 2
        cy = self.height() // 2

        # Barra de progreso: centrada, en el tercio inferior
        bw = self._progress.width()
        bh = self._progress.height()
        by = cy + 140
        self._progress.move(cx - bw // 2, by)

        # Hint label debajo de la barra
        self._hint_label.move(
            cx - self._hint_label.width() // 2,
            by + bh + 8
        )

    # ── Animación ─────────────────────────────────────────────────────────

    def _start_animation(self):
        # Reproducir sonido de inicio
        if self._sounds:
            self._sounds.play_startup()

        self._progress.start()

        # Timer principal de 16ms (~60fps) para el fade
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._step)
        self._anim_timer.start(16)

    def _step(self):
        self._elapsed += 16

        if self._phase == "fade_in":
            self._opacity = min(1.0, self._elapsed / self.FADE_IN_MS)
            if self._elapsed >= self.FADE_IN_MS:
                self._phase   = "hold"
                self._elapsed = 0

        elif self._phase == "hold":
            self._opacity = 1.0
            if self._elapsed >= self.HOLD_MS:
                self._phase   = "fade_out"
                self._elapsed = 0

        elif self._phase == "fade_out":
            self._opacity = max(0.0, 1.0 - self._elapsed / self.FADE_OUT_MS)
            if self._elapsed >= self.FADE_OUT_MS:
                self._anim_timer.stop()
                self._progress.stop()
                self.close()
                self.finished.emit()
                return

        self.update()

    # ── Pintura ───────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        alpha = int(self._opacity * 255)
        cx = self.width()  // 2
        cy = self.height() // 2

        # Fondo negro con opacidad animada
        bg = QColor(0, 0, 0, alpha)
        painter.fillRect(self.rect(), bg)

        if alpha < 10:
            painter.end()
            return

        painter.setOpacity(self._opacity)

        # ── Logo "Tomatito" ─────────────────────────────────────────────
        from PyQt6.QtGui import QPixmap
        import os
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons", "tomatito.png")
        if os.path.isfile(logo_path):
            pix = QPixmap(logo_path)
            if not pix.isNull():
                scaled_pix = pix.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(cx - scaled_pix.width() // 2, cy - 140, scaled_pix)
        else:
            emoji_font = QFont("Segoe UI Emoji", 64)
            painter.setFont(emoji_font)
            painter.setPen(QColor(255, 255, 255, alpha))
            painter.drawText(QRect(cx - 60, cy - 140, 120, 100),
                             Qt.AlignmentFlag.AlignCenter, "🍅")

        # Nombre "Tomatito"
        title_font = QFont("Tahoma", 32, QFont.Weight.Light)
        painter.setFont(title_font)

        # Sombra del texto
        painter.setPen(QColor(0, 0, 0, alpha // 2))
        painter.drawText(QRect(cx - 202, cy - 42, 404, 60),
                         Qt.AlignmentFlag.AlignCenter, "tomatitOS")

        # Texto principal con degradado
        grad = QLinearGradient(cx - 200, cy - 40, cx - 200, cy + 20)
        grad.setColorAt(0.0, QColor(255, 255, 255, alpha))
        grad.setColorAt(0.5, QColor(200, 225, 255, alpha))
        grad.setColorAt(1.0, QColor(150, 190, 255, alpha))
        painter.setPen(QPen(QColor(255, 255, 255, alpha), 0))
        painter.setFont(title_font)
        # Dibujamos relleno con degradado usando fillPath no disponible directamente;
        # usamos color sólido blanco limpio para el título
        painter.setPen(QColor(255, 255, 255, alpha))
        painter.drawText(QRect(cx - 200, cy - 40, 400, 60),
                         Qt.AlignmentFlag.AlignCenter, "Tomatito")

        # Línea decorativa bajo el título
        line_y = cy + 28
        line_grad = QLinearGradient(cx - 120, line_y, cx + 120, line_y)
        line_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        line_grad.setColorAt(0.3, QColor(100, 150, 255, alpha))
        line_grad.setColorAt(0.7, QColor(100, 150, 255, alpha))
        line_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(QPen(line_grad, 1))
        painter.drawLine(cx - 120, line_y, cx + 120, line_y)

        painter.end()

        # Reposicionar widgets hijos con opacidad
        self._reposition_widgets()
        self._progress.setWindowOpacity(self._opacity)

    # ── Resize ────────────────────────────────────────────────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_widgets()
