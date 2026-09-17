"""
camera_app.py — Aplicación de cámara estilo Cyber-shot 2000s.

Muestra la vista en vivo de la cámara usando QVideoWidget,
permite capturar fotos con flash, agrega la estampa de fecha naranja de los 2000s,
y las guarda en assets/photos/Camara/ para que aparezcan en Mis imágenes.
"""

import os
import random
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QPainter, QPen, QImage
)
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QImageCapture
from PyQt6.QtMultimediaWidgets import QVideoWidget

from apps.base_app import BaseApp
from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager

_CYBER_QSS = """
QWidget#camera_root {
    background-color: #101010;
    color: #ffffff;
    font-family: "Courier New", monospace;
}

QFrame#viewfinder_box {
    background-color: #000000;
    border: 3px solid #2e2e2e;
    border-radius: 4px;
}

QFrame#control_bar {
    background: qlineargradiant(x1:0, y1:0, x2:0, y2:1, stop:0 #383838, stop:1 #1c1c1c);
    border-top: 2px solid #505050;
}

QPushButton#btn_shutter {
    background: qradialgradient(cx:0.5, cy:0.4, radius:0.7, fx:0.5, fy:0.2, stop:0 #ffffff, stop:0.5 #d8d8d8, stop:1 #888888);
    color: #111111;
    border: 2px solid #ffffff;
    border-radius: 20px;
    font-weight: bold;
    font-size: 13px;
    font-family: "Segoe UI", sans-serif;
    padding: 6px 24px;
}

QPushButton#btn_shutter:hover {
    background: qradialgradient(cx:0.5, cy:0.4, radius:0.7, fx:0.5, fy:0.2, stop:0 #ffffff, stop:0.5 #f0f0f0, stop:1 #aaaaaa);
    border-color: #ffaa00;
}

QPushButton#btn_shutter:pressed {
    background: #777777;
}

QLabel#osd_top_left {
    color: #ffcc00;
    font-size: 11px;
    font-weight: bold;
    background: transparent;
}

QLabel#osd_top_right {
    color: #00ff78;
    font-size: 11px;
    font-weight: bold;
    background: transparent;
}

QLabel#osd_date_stamp {
    color: #ff8800;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
}
"""


class OSDOverlay(QWidget):
    """Capa superior transparente para la retícula y OSD estilo 2000s."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.show_flash = False
        self.flash_timer = QTimer(self)
        self.flash_timer.setInterval(70)
        self.flash_timer.timeout.connect(self._end_flash)

        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(1000)
        self.clock_timer.timeout.connect(self.update)
        self.clock_timer.start()

    def trigger_flash(self):
        self.show_flash = True
        self.flash_timer.start()
        self.update()

    def _end_flash(self):
        self.show_flash = False
        self.flash_timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()

        if self.show_flash:
            painter.fillRect(self.rect(), QColor(255, 255, 255, 230))
            painter.end()
            return

        # Retícula central de enfoque [  ]
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(0, 255, 120, 210), 2))
        cw, ch = 80, 60
        cx, cy = (w - cw) // 2, (h - ch) // 2
        s = 12

        painter.drawLine(cx, cy, cx + s, cy)
        painter.drawLine(cx, cy, cx, cy + s)
        painter.drawLine(cx + cw, cy, cx + cw - s, cy)
        painter.drawLine(cx + cw, cy, cx + cw, cy + s)
        painter.drawLine(cx, cy + ch, cx + s, cy + ch)
        painter.drawLine(cx, cy + ch, cx, cy + ch - s)
        painter.drawLine(cx + cw, cy + ch, cx + cw - s, cy + ch)
        painter.drawLine(cx + cw, cy + ch, cx + cw, cy + ch - s)

        painter.setBrush(QColor(0, 255, 120, 200))
        painter.drawEllipse(w // 2 - 2, h // 2 - 2, 4, 4)

        # OSD Top Left
        painter.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 220, 0))
        painter.drawText(14, 24, "📷 3.2 MP")
        painter.drawText(14, 42, "ISO 100")

        # OSD Top Right
        painter.setPen(QColor(0, 255, 120))
        painter.drawText(w - 90, 24, "🔋 [III]")
        painter.drawText(w - 90, 42, "FINE 4:3")

        # Estampa de Fecha en Vivo estilo 2000s abajo a la derecha
        now = datetime.now()
        date_str = now.strftime("'%y %m %d")
        time_str = now.strftime("%H:%M")
        stamp_text = f"{date_str}  {time_str}"

        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        # Sombra negra
        painter.setPen(QColor(0, 0, 0, 220))
        painter.drawText(w - 188, h - 18, stamp_text)
        # Naranja fosforescente icónico de cámaras 2000s
        painter.setPen(QColor(255, 140, 0))
        painter.drawText(w - 190, h - 20, stamp_text)

        painter.end()


def stamp_date_on_image(pixmap: QPixmap) -> QPixmap:
    """Estampa la fecha y hora naranja fosforescente en la esquina de la foto guardada."""
    img = pixmap.toImage()
    res = QPixmap.fromImage(img)
    painter = QPainter(res)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    w, h = res.width(), res.height()
    font_size = max(16, int(h * 0.045))
    painter.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))

    now = datetime.now()
    date_str = now.strftime("'%y %m %d")
    time_str = now.strftime("%H:%M")
    stamp_text = f"{date_str}  {time_str}"

    tx = int(w * 0.62)
    ty = int(h * 0.92)

    # Sombra negra
    painter.setPen(QColor(0, 0, 0, 240))
    painter.drawText(tx + 2, ty + 2, stamp_text)

    # Naranja brillante 2000s
    painter.setPen(QColor(255, 140, 0))
    painter.drawText(tx, ty, stamp_text)

    painter.end()
    return res


class CameraApp(BaseApp):
    """Aplicación de Cámara Digital estilo Cyber-shot 2000s."""

    def __init__(self, resources: ResourceManager, sounds: SoundManager, parent=None):
        self._camera: QCamera | None = None
        self._session: QMediaCaptureSession | None = None
        self._image_capture: QImageCapture | None = None
        super().__init__(resources, sounds, parent)
        self._start_camera()

    def _build_ui(self) -> None:
        self.setObjectName("camera_root")
        self.setMinimumSize(560, 440)
        self.setStyleSheet(_CYBER_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Contenedor del visor de cámara (QVideoWidget + Overlay)
        view_box = QFrame()
        view_box.setObjectName("viewfinder_box")

        # Layout superpuesto para tener el VideoWidget abajo y el OSD arriba
        self._stacked_container = QWidget(view_box)
        stacked = QStackedLayout(self._stacked_container)
        stacked.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self._video_widget = QVideoWidget()
        stacked.addWidget(self._video_widget)

        self._osd_overlay = OSDOverlay()
        stacked.addWidget(self._osd_overlay)

        box_layout = QVBoxLayout(view_box)
        box_layout.setContentsMargins(2, 2, 2, 2)
        box_layout.addWidget(self._stacked_container)

        root.addWidget(view_box, stretch=1)

        # Barra de control inferior
        ctrl = QFrame()
        ctrl.setObjectName("control_bar")
        ctrl.setFixedHeight(64)
        h = QHBoxLayout(ctrl)
        h.setContentsMargins(16, 8, 16, 8)

        self._status_lbl = QLabel("FLASH: AUTO")
        self._status_lbl.setObjectName("osd_top_left")
        h.addWidget(self._status_lbl)

        h.addStretch()

        self._btn_shutter = QPushButton("📷  TOMAR FOTO")
        self._btn_shutter.setObjectName("btn_shutter")
        self._btn_shutter.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_shutter.clicked.connect(self._take_photo)
        h.addWidget(self._btn_shutter)

        h.addStretch()

        self._counter_lbl = QLabel("MEMORIA: OK")
        self._counter_lbl.setObjectName("osd_top_right")
        h.addWidget(self._counter_lbl)

        root.addWidget(ctrl)

    def _start_camera(self) -> None:
        try:
            self._camera = QCamera(self)
            self._session = QMediaCaptureSession(self)
            self._image_capture = QImageCapture(self)

            self._session.setCamera(self._camera)
            self._session.setVideoOutput(self._video_widget)
            self._session.setImageCapture(self._image_capture)

            self._image_capture.imageCaptured.connect(self._on_image_captured)

            self._camera.start()
        except Exception:
            self._camera = None

    def _take_photo(self) -> None:
        self._osd_overlay.trigger_flash()
        if self.sounds:
            self.sounds.play_click()

        if self._image_capture and self._camera and self._camera.isActive():
            self._image_capture.capture()
        else:
            self._capture_fallback()

    def _on_image_captured(self, id: int, image: QImage) -> None:
        px = QPixmap.fromImage(image)
        stamped = stamp_date_on_image(px)
        self._save_to_gallery(stamped)

    def _capture_fallback(self) -> None:
        # Captura desde la pantalla del video widget o foto generada
        px = self._video_widget.grab()
        if px.isNull() or px.width() < 50:
            w, h = 640, 480
            px = QPixmap(w, h)
            p = QPainter(px)
            p.fillRect(0, 0, w, h, QColor(25, 40, 60))
            p.setPen(QPen(QColor(0, 200, 255), 3))
            p.drawRect(40, 40, w - 80, h - 80)
            p.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
            p.setPen(QColor(255, 255, 255))
            p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "📷 Cyber-Shot Foto 2000s")
            p.end()

        stamped = stamp_date_on_image(px)
        self._save_to_gallery(stamped)

    def _save_to_gallery(self, pixmap: QPixmap) -> None:
        # Guardar en la carpeta "Camara" dentro de photos para que aparezca en "Mis imágenes"
        photos_dir = self.resources.assets_path("photos", "Camara")
        os.makedirs(photos_dir, exist_ok=True)
        filename = f"PHOTO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        save_path = os.path.join(photos_dir, filename)
        pixmap.save(save_path, "JPEG", 92)

    def closeEvent(self, event) -> None:
        if self._camera:
            self._camera.stop()
        super().closeEvent(event)
