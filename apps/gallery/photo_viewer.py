"""
photo_viewer.py — Visor de fotografías a pantalla completa (dentro del sistema).

Características:
- Muestra la foto ajustada al espacio disponible (sin deformar).
- Navegación: botones anterior / siguiente + teclado (← →).
- Nombre del archivo visible en la barra inferior.
- Fondo negro con la foto centrada.
- Se integra dentro de un WindowFrame del sistema de ventanas.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QKeyEvent, QImage
from PIL import Image
import io


def _load_pixmap_with_pillow(path: str) -> QPixmap:
    """
    Carga una imagen usando Pillow (soporta WEBP, JPEG, PNG) y la convierte a QPixmap.
    """
    try:
        img = Image.open(path).convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimg)
    except Exception:
        return QPixmap()


class _NavButton(QPushButton):
    """Botón de navegación (anterior/siguiente)."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(44, 44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 140);
                color: white;
                font-size: 22px;
                border: 1px solid rgba(255,255,255,60);
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,40);
                border: 1px solid rgba(255,255,255,120);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,20);
            }
            QPushButton:disabled {
                color: rgba(255,255,255,60);
                background: rgba(0,0,0,60);
            }
        """)


class PhotoViewer(QWidget):
    """
    Visor de fotografías. Recibe una lista de rutas y un índice inicial.
    """

    def __init__(self, photo_paths: list[str], start_index: int = 0, parent=None):
        super().__init__(parent)
        self._paths = photo_paths
        self._index = max(0, min(start_index, len(photo_paths) - 1))
        self._cache: dict[str, QPixmap] = {}

        self.setStyleSheet("background: #1a1a1a;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._build_ui()
        self._load_current()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Área principal de imagen
        self._img_area = QWidget()
        self._img_area.setStyleSheet("background: #1a1a1a;")
        img_layout = QHBoxLayout(self._img_area)
        img_layout.setContentsMargins(8, 8, 8, 8)
        img_layout.setSpacing(8)

        # Botón anterior
        self._btn_prev = _NavButton("‹")
        self._btn_prev.clicked.connect(self._go_prev)
        img_layout.addWidget(self._btn_prev, 0, Qt.AlignmentFlag.AlignVCenter)

        # Imagen
        self._photo_label = QLabel()
        self._photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._photo_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._photo_label.setStyleSheet("background: transparent;")
        img_layout.addWidget(self._photo_label, 1)

        # Botón siguiente
        self._btn_next = _NavButton("›")
        self._btn_next.clicked.connect(self._go_next)
        img_layout.addWidget(self._btn_next, 0, Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self._img_area, 1)

        # Barra inferior con info
        info_bar = QWidget()
        info_bar.setFixedHeight(30)
        info_bar.setStyleSheet("background: #111111; border-top: 1px solid #333333;")
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(12, 0, 12, 0)

        self._filename_label = QLabel()
        self._filename_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        info_layout.addWidget(self._filename_label)

        info_layout.addStretch()

        self._counter_label = QLabel()
        self._counter_label.setStyleSheet("color: #888888; font-size: 11px;")
        info_layout.addWidget(self._counter_label)

        layout.addWidget(info_bar)

    # ── Navegación ────────────────────────────────────────────────────────

    def _go_prev(self):
        if self._index > 0:
            self._index -= 1
            self._load_current()

    def _go_next(self):
        if self._index < len(self._paths) - 1:
            self._index += 1
            self._load_current()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Left:
            self._go_prev()
        elif event.key() == Qt.Key.Key_Right:
            self._go_next()
        else:
            super().keyPressEvent(event)

    # ── Carga y display de imagen ─────────────────────────────────────────

    def _load_current(self):
        if not self._paths:
            self._photo_label.setText("Sin imágenes")
            return

        path = self._paths[self._index]
        import os
        fname = os.path.basename(path)

        # Actualizar info
        self._filename_label.setText(fname)
        self._counter_label.setText(f"{self._index + 1} / {len(self._paths)}")

        # Botones de navegación
        self._btn_prev.setEnabled(self._index > 0)
        self._btn_next.setEnabled(self._index < len(self._paths) - 1)

        # Cargar pixmap (con cache)
        if path not in self._cache:
            px = _load_pixmap_with_pillow(path)
            if px.isNull():
                # Fallback: QPixmap directo (JPG/PNG sin WEBP)
                px = QPixmap(path)
            self._cache[path] = px

        self._display_pixmap(self._cache[path])

    def _display_pixmap(self, pixmap: QPixmap):
        """Escala la imagen para caber en el label sin deformar."""
        if pixmap.isNull():
            self._photo_label.setText("No se pudo cargar la imagen")
            return
        available = self._photo_label.size()
        if available.width() < 10 or available.height() < 10:
            # Aún no se ha pintado: usar un tamaño razonable por defecto
            available = QSize(600, 400)
        scaled = pixmap.scaled(
            available,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._photo_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reescalar la imagen actual al nuevo tamaño
        if self._paths and self._paths[self._index] in self._cache:
            self._display_pixmap(self._cache[self._paths[self._index]])
