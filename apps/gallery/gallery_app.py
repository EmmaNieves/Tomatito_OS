"""
gallery_app.py — Aplicación principal de la Galería de fotografías.

Flujo de navegación:
  Vista de álbumes → (doble clic) → Vista de fotos del álbum → (clic) → Visor de foto

Gestiona el stack de vistas mediante QStackedWidget.
Carga álbumes dinámicamente desde ResourceManager sin lista hardcodeada.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QGridLayout, QPushButton, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QLinearGradient

from apps.base_app import BaseApp
from apps.gallery.album_view import AlbumView
from apps.gallery.photo_viewer import PhotoViewer
from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager
from styles.colors import GALLERY_BG, GALLERY_SIDEBAR, GALLERY_ALBUM_HOVER


class _AlbumCard(QWidget):
    """Tarjeta de álbum en la vista de álbumes (carpeta con nombre y portada)."""

    double_clicked = pyqtSignal()

    def __init__(self, album: dict, parent=None):
        super().__init__(parent)
        self._hovered = False
        self.setFixedSize(150, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono de carpeta con miniatura (o emoji si no hay cover)
        icon_area = QLabel()
        icon_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_area.setFixedSize(80, 70)

        if album.get("cover"):
            from PyQt6.QtGui import QPixmap, QImage
            from PIL import Image
            try:
                img = Image.open(album["cover"]).convert("RGBA")
                img.thumbnail((72, 62), Image.LANCZOS)
                data = img.tobytes("raw", "RGBA")
                qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
                px = QPixmap.fromImage(qimg)
                icon_area.setPixmap(px)
                icon_area.setStyleSheet(
                    "border: 2px solid #CCCCCC; background: #FFFFFF; border-radius: 2px;"
                )
            except Exception:
                icon_area.setText("📁")
                icon_area.setStyleSheet("font-size: 48px; background: transparent;")
        else:
            icon_area.setText("📁")
            icon_area.setStyleSheet("font-size: 48px; background: transparent;")

        layout.addWidget(icon_area, 0, Qt.AlignmentFlag.AlignCenter)

        # Nombre
        name_lbl = QLabel(album["name"])
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #222222; background: transparent;"
        )
        layout.addWidget(name_lbl)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self._hovered:
            painter.fillRect(self.rect(), QColor("#D8E8FF"))
            painter.setPen(QColor("#316AC5"))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        painter.end()


class _AlbumListView(QWidget):
    """Vista inicial: lista de álbumes disponibles."""

    album_opened = pyqtSignal(dict)  # dict del álbum seleccionado

    def __init__(self, albums: list[dict], parent=None):
        super().__init__(parent)
        self._albums = albums
        self.setStyleSheet(f"background: {GALLERY_BG};")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra de dirección (estilo explorador XP)
        addr_bar = QWidget()
        addr_bar.setFixedHeight(36)
        addr_bar.setStyleSheet("background: #F0EFE7; border-bottom: 1px solid #CCCCCC;")
        addr_layout = QHBoxLayout(addr_bar)
        addr_layout.setContentsMargins(8, 4, 8, 4)

        addr_icon = QLabel("📁")
        addr_icon.setStyleSheet("font-size: 16px; background: transparent;")
        addr_layout.addWidget(addr_icon)

        addr_text = QLabel("Mis imágenes")
        addr_text.setStyleSheet("font-size: 12px; font-weight: bold; color: #222222; background: transparent;")
        addr_layout.addWidget(addr_text)
        addr_layout.addStretch()

        layout.addWidget(addr_bar)

        # Área principal dividida: panel lateral + contenido
        content = QWidget()
        content.setStyleSheet(f"background: {GALLERY_BG};")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Panel lateral
        sidebar = QWidget()
        sidebar.setFixedWidth(160)
        sidebar.setStyleSheet(f"background: {GALLERY_SIDEBAR}; border-right: 1px solid #CCCCCC;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 12, 8, 8)
        sb_layout.setSpacing(4)

        sb_title = QLabel("Tareas de imagen")
        sb_title.setStyleSheet("color: #316AC5; font-weight: bold; font-size: 11px; background: transparent;")
        sb_layout.addWidget(sb_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #316AC5;")
        sb_layout.addWidget(sep)

        hint = QLabel("Haz doble clic\nen un álbum\npara abrirlo.")
        hint.setStyleSheet("color: #444444; font-size: 10px; background: transparent;")
        hint.setWordWrap(True)
        sb_layout.addWidget(hint)
        sb_layout.addStretch()

        content_layout.addWidget(sidebar)

        # Cuadrícula de álbumes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #FFFFFF; }")

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: #FFFFFF;")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(16)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        if self._albums:
            COLS = 4
            for i, album in enumerate(self._albums):
                card = _AlbumCard(album)
                row, col = divmod(i, COLS)
                grid.addWidget(card, row, col)
                album_data = album
                card.double_clicked.connect(
                    lambda a=album_data: self.album_opened.emit(a)
                )
        else:
            empty = QLabel(
                "No se encontraron álbumes.\n\n"
                "Crea carpetas dentro de:\nassets/photos/"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888888; font-size: 12px;")
            grid.addWidget(empty, 0, 0)

        scroll.setWidget(grid_widget)
        content_layout.addWidget(scroll, 1)
        layout.addWidget(content, 1)


# ── Aplicación principal ──────────────────────────────────────────────────

class GalleryApp(BaseApp):
    """
    Galería de fotografías. Primera aplicación de Tomatito.
    Navega entre:
      0 → Lista de álbumes
      1 → Vista de fotos del álbum seleccionado
      2 → Visor de fotografía individual
    """

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        # Vista 0: lista de álbumes
        albums = self.resources.get_photo_albums()
        self._album_list = _AlbumListView(albums)
        self._album_list.album_opened.connect(self._open_album)
        self._stack.addWidget(self._album_list)

        self._album_view: AlbumView | None = None
        self._photo_viewer: PhotoViewer | None = None

    # ── Navegación entre vistas ───────────────────────────────────────────

    def _open_album(self, album: dict) -> None:
        """Cambia a la vista de miniaturas del álbum."""
        photos = self.resources.get_photos_in_album(album["path"])

        # Crear (o reemplazar) la vista del álbum
        if self._album_view is not None:
            self._stack.removeWidget(self._album_view)
            self._album_view.deleteLater()

        self._album_view = AlbumView(album["name"], photos)
        self._album_view.back_requested.connect(self._go_to_albums)
        self._album_view.photo_selected.connect(self._open_photo_viewer)
        self._stack.addWidget(self._album_view)
        self._stack.setCurrentWidget(self._album_view)

    def _go_to_albums(self) -> None:
        self._stack.setCurrentWidget(self._album_list)

    def _open_photo_viewer(self, paths: list, index: int) -> None:
        """Abre el visor de foto para la imagen seleccionada."""
        if self._photo_viewer is not None:
            self._stack.removeWidget(self._photo_viewer)
            self._photo_viewer.deleteLater()

        self._photo_viewer = PhotoViewer(paths, index)
        self._stack.addWidget(self._photo_viewer)
        self._stack.setCurrentWidget(self._photo_viewer)
