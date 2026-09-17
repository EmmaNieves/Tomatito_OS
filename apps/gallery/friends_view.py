"""
friends_view.py — Vistas para la sección "Amigos" de Mis Imágenes.

Proporciona:
- FriendsGridView: Lista a las 6 personas con sus contadores de fotos y tarjeta XP.
- PersonDetailView: Muestra la información de info.json (recuerdo, mensaje) y la galería de fotos.
"""

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QFont

from apps.gallery.album_view import _Thumbnail, THUMB_SIZE
from styles.colors import GALLERY_BG, GALLERY_SIDEBAR

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

FRIENDS_CONFIG = [
    {"folder": "hillary",       "name": "Hillary"},
    {"folder": "liz",           "name": "Liz"},
    {"folder": "vladimir",      "name": "Vladimir"},
    {"folder": "andres_julian", "name": "Andrés Julián"},
    {"folder": "eliane",        "name": "Eliane"},
    {"folder": "desireth",      "name": "Desireth"},
]


def _scan_person_photos(person_dir: str) -> list[str]:
    """Devuelve las rutas de las fotos de la carpeta de una persona."""
    if not os.path.isdir(person_dir):
        return []
    photos = []
    for fname in sorted(os.listdir(person_dir)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in SUPPORTED_EXTS:
            photos.append(os.path.join(person_dir, fname))
    return photos


def _load_person_info(person_dir: str, default_name: str) -> dict:
    """Carga info.json si existe en la carpeta de la persona."""
    json_path = os.path.join(person_dir, "info.json")
    info = {"nombre": default_name, "recuerdo": "", "mensaje": ""}
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                info["nombre"]   = data.get("nombre", default_name)
                info["recuerdo"] = data.get("recuerdo", "").strip()
                info["mensaje"]  = data.get("mensaje", "").strip()
        except Exception:
            pass
    return info


class _PersonCard(QWidget):
    """Tarjeta individual para cada persona en la vista de Amigos."""

    clicked = pyqtSignal(dict)  # emite dict de la persona

    def __init__(self, person_data: dict, parent=None):
        super().__init__(parent)
        self._data = person_data
        self._hovered = False
        self.setFixedSize(160, 150)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono avatar estilo XP
        avatar = QLabel("👤")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("font-size: 42px; background: transparent;")
        layout.addWidget(avatar)

        # Nombre
        name_lbl = QLabel(person_data["name"])
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #111111; background: transparent;"
        )
        layout.addWidget(name_lbl)

        # Contador de fotos
        count = len(person_data["photos"])
        txt = "1 foto" if count == 1 else f"{count} fotos"
        count_lbl = QLabel(f"📷 {txt}")
        count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_lbl.setStyleSheet("font-size: 11px; color: #555555; background: transparent;")
        layout.addWidget(count_lbl)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._data)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self._hovered:
            painter.fillRect(self.rect(), QColor("#D8E8FF"))
            painter.setPen(QColor("#316AC5"))
        else:
            painter.fillRect(self.rect(), QColor("#FAFAFA"))
            painter.setPen(QColor("#CCCCCC"))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        painter.end()


class FriendsGridView(QWidget):
    """Vista de la sección Amigos con la frase intro y las 6 tarjetas de personas."""

    back_requested = pyqtSignal()
    person_selected = pyqtSignal(dict)

    def __init__(self, amigos_base_dir: str, parent=None):
        super().__init__(parent)
        self._base_dir = amigos_base_dir
        self.setStyleSheet("background: #FFFFFF;")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra de dirección / encabezado
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
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FFFFFF, stop:1 #D4D0C8);
                border: 1px solid #7F9DB9;
                border-radius: 3px;
                padding: 2px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #EEF3FF, stop:1 #C0D4F0);
                border: 1px solid #316AC5;
            }
        """)
        btn_back.clicked.connect(self.back_requested.emit)
        h_layout.addWidget(btn_back)

        title = QLabel("👥 Mis imágenes  >  Amigos")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #222222; background: transparent;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        layout.addWidget(header)

        # Contenido principal con franja intro
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #FFFFFF; }")

        main_container = QWidget()
        main_container.setStyleSheet("background: #FFFFFF;")
        v_container = QVBoxLayout(main_container)
        v_container.setContentsMargins(20, 16, 20, 20)
        v_container.setSpacing(16)

        # Franja emocional intro
        intro_box = QFrame()
        intro_box.setStyleSheet("background: #F4F7fc; border: 1px solid #D0DCF0; border-radius: 4px;")
        ib_layout = QHBoxLayout(intro_box)
        ib_layout.setContentsMargins(14, 10, 14, 10)

        intro_txt = QLabel("“Algunas personas quisieron dejarte un pedacito de sus recuerdos...”")
        intro_txt.setStyleSheet("font-size: 12px; font-style: italic; color: #2C4A7C; background: transparent;")
        ib_layout.addWidget(intro_txt)

        v_container.addWidget(intro_box)

        # Cuadrícula de las 6 personas
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        COLS = 3
        for i, cfg in enumerate(FRIENDS_CONFIG):
            p_dir = os.path.join(self._base_dir, cfg["folder"])
            info = _load_person_info(p_dir, cfg["name"])
            photos = _scan_person_photos(p_dir)

            data = {
                "folder": cfg["folder"],
                "name": info["nombre"],
                "dir": p_dir,
                "info": info,
                "photos": photos,
            }

            card = _PersonCard(data)
            row, col = divmod(i, COLS)
            grid.addWidget(card, row, col)
            card.clicked.connect(self.person_selected.emit)

        v_container.addWidget(grid_widget, stretch=1)
        scroll.setWidget(main_container)
        layout.addWidget(scroll, 1)


class PersonDetailView(QWidget):
    """Vista detallada de una persona (Info.json + Galería de Fotos)."""

    back_requested = pyqtSignal()
    photo_selected = pyqtSignal(list, int)

    def __init__(self, person_data: dict, parent=None):
        super().__init__(parent)
        self._data = person_data
        self.setStyleSheet("background: #FFFFFF;")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Encabezado
        header = QWidget()
        header.setFixedHeight(38)
        header.setStyleSheet("background: #F0EFE7; border-bottom: 1px solid #CCCCCC;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 4, 8, 4)
        h_layout.setSpacing(8)

        btn_back = QPushButton("← Amigos")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FFFFFF, stop:1 #D4D0C8);
                border: 1px solid #7F9DB9;
                border-radius: 3px;
                padding: 2px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #EEF3FF, stop:1 #C0D4F0);
                border: 1px solid #316AC5;
            }
        """)
        btn_back.clicked.connect(self.back_requested.emit)
        h_layout.addWidget(btn_back)

        title = QLabel(f"👤 {self._data['name']}")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #222222; background: transparent;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        layout.addWidget(header)

        # Contenido principal con Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #FFFFFF; }")

        main_w = QWidget()
        main_w.setStyleSheet("background: #FFFFFF;")
        v_main = QVBoxLayout(main_w)
        v_main.setContentsMargins(24, 20, 24, 24)
        v_main.setSpacing(20)

        info = self._data["info"]

        # 💭 Sección Recuerdo (solo si existe y no está vacía)
        recuerdo = info.get("recuerdo", "").strip()
        if recuerdo:
            sec_rec = self._make_info_section("💭 Recuerdo", recuerdo)
            v_main.addWidget(sec_rec)

        # 💌 Sección Mensaje (solo si existe y no está vacía)
        mensaje = info.get("mensaje", "").strip()
        if mensaje:
            sec_msg = self._make_info_section("💌 Mensaje", mensaje)
            v_main.addWidget(sec_msg)

        # 📷 Sección Fotos
        sec_photos_hdr = QLabel("📷 Fotografías")
        sec_photos_hdr.setStyleSheet("font-size: 13px; font-weight: bold; color: #316AC5; background: transparent;")
        v_main.addWidget(sec_photos_hdr)

        photos = self._data["photos"]
        if photos:
            grid_w = QWidget()
            grid = QGridLayout(grid_w)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setSpacing(12)
            grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            COLS = 5
            for i, p_path in enumerate(photos):
                thumb = _Thumbnail(p_path, i)
                thumb.clicked.connect(lambda idx: self.photo_selected.emit(photos, idx))
                row, col = divmod(i, COLS)
                grid.addWidget(thumb, row, col)

            v_main.addWidget(grid_w)
        else:
            empty = QLabel("No hay fotografías guardadas para esta persona en su carpeta.")
            empty.setStyleSheet("font-size: 11px; color: #777777; font-style: italic; background: transparent;")
            v_main.addWidget(empty)

        v_main.addStretch()
        scroll.setWidget(main_w)
        layout.addWidget(scroll, 1)

    def _make_info_section(self, header_title: str, text_content: str) -> QFrame:
        box = QFrame()
        box.setStyleSheet("background: #FAFAFA; border: 1px solid #E0E0E0; border-radius: 4px;")
        v = QVBoxLayout(box)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(6)

        hdr = QLabel(header_title)
        hdr.setStyleSheet("font-size: 12px; font-weight: bold; color: #316AC5; background: transparent;")
        v.addWidget(hdr)

        body = QLabel(text_content)
        body.setWordWrap(True)
        body.setStyleSheet("font-size: 11px; color: #333333; line-height: 1.4; background: transparent;")
        v.addWidget(body)

        return box
