"""
album_view.py — Vista de miniaturas de un álbum de fotos.

Muestra todas las imágenes del álbum en una cuadrícula de miniaturas.
Al hacer clic en una miniatura, emite una señal para abrir el visor.
Incluye botón de "Volver" para regresar a la lista de álbumes.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image


THUMB_SIZE = 120  # px


import io

def _make_thumbnail(path: str, size: int) -> QPixmap:
    """Genera una miniatura de forma 100% segura sin punteros corruptos."""
    if not path or not os.path.exists(path):
        return QPixmap()
    try:
        pix = QPixmap(path)
        if not pix.isNull():
            return pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        img = Image.open(path)
        img.thumbnail((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pix = QPixmap()
        pix.loadFromData(buf.getvalue())
        return pix
    except Exception:
        return QPixmap()


class _Thumbnail(QWidget):
    """Widget de miniatura individual con efecto hover."""

    clicked = pyqtSignal(int)  # índice dentro del álbum

    def __init__(self, path: str, index: int, parent=None):
        super().__init__(parent)
        self._index = index
        self._hovered = False
        self.setFixedSize(THUMB_SIZE + 8, THUMB_SIZE + 8)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Imagen
        self._img_label = QLabel()
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_label.setFixedSize(THUMB_SIZE, THUMB_SIZE)
        self._img_label.setStyleSheet(
            "border: 2px solid #CCCCCC; background: #FFFFFF;"
        )

        px = _make_thumbnail(path, THUMB_SIZE)
        if not px.isNull():
            self._img_label.setPixmap(
                px.scaled(THUMB_SIZE - 4, THUMB_SIZE - 4,
                          Qt.AspectRatioMode.KeepAspectRatio,
                          Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self._img_label.setText("?")

        layout.addWidget(self._img_label, 0, Qt.AlignmentFlag.AlignCenter)

    def enterEvent(self, event):
        self._hovered = True
        self._img_label.setStyleSheet(
            "border: 2px solid #316AC5; background: #EEF3FF;"
        )
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._img_label.setStyleSheet(
            "border: 2px solid #CCCCCC; background: #FFFFFF;"
        )
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._index)
        super().mousePressEvent(event)


class AlbumView(QWidget):
    """
    Vista de cuadrícula de un álbum. Emite señales para navegar.
    """

    back_requested  = pyqtSignal()              # volver a la lista de álbumes
    photo_selected  = pyqtSignal(list, int)     # (lista_paths, índice)

    def __init__(self, album_name: str, photo_paths: list[str], parent=None):
        super().__init__(parent)
        self._album_name = album_name
        self._paths = photo_paths
        self.setStyleSheet("background: #FFFFFF;")
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barra superior del álbum
        header = QWidget()
        header.setFixedHeight(38)
        header.setStyleSheet("background: #F0EFE7; border-bottom: 1px solid #CCCCCC;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 4, 8, 4)
        h_layout.setSpacing(8)

        btn_back = QPushButton("← Álbumes")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #FFFFFF, stop:1 #D4D0C8);
                border: 1px solid #7F9DB9;
                border-radius: 3px;
                padding: 2px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #EEF3FF, stop:1 #C0D4F0);
                border: 1px solid #316AC5;
            }
        """)
        btn_back.clicked.connect(self.back_requested)
        h_layout.addWidget(btn_back)

        title = QLabel(f"📁 {self._album_name}")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #222222; background: transparent;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        count = QLabel(f"{len(self._paths)} foto(s)")
        count.setStyleSheet("font-size: 11px; color: #666666; background: transparent;")
        h_layout.addWidget(count)

        main_layout.addWidget(header)

        # Scroll con cuadrícula
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #FFFFFF; }")

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: #FFFFFF;")
        self._grid = QGridLayout(grid_widget)
        self._grid.setContentsMargins(12, 12, 12, 12)
        self._grid.setSpacing(8)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._populate_grid()

        scroll.setWidget(grid_widget)
        main_layout.addWidget(scroll, 1)

        # Mensaje si vacío
        if not self._paths:
            empty = QLabel("No hay fotos en este álbum.\nCopia imágenes a la carpeta correspondiente.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888888; font-size: 12px; background: #FFFFFF;")
            self._grid.addWidget(empty, 0, 0)

    def _populate_grid(self):
        COLS = 5
        for i, path in enumerate(self._paths):
            thumb = _Thumbnail(path, i)
            thumb.clicked.connect(lambda idx: self.photo_selected.emit(self._paths, idx))
            row, col = divmod(i, COLS)
            self._grid.addWidget(thumb, row, col)
