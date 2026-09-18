# -*- coding: utf-8 -*-
"""
music_app.py — Reproductor de música tomatitOS
Estética Windows XP / retro 2000s.
Pantalla de bienvenida + reproductor con shuffle, repeat, visualizador.
"""

import os
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QListWidget, QListWidgetItem,
    QFrame, QStackedWidget, QSizePolicy, QTextEdit, QScrollArea,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QUrl, QTimer, QPropertyAnimation,
    QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QPainter, QBrush,
    QPen, QLinearGradient
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from apps.base_app import BaseApp
from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager

try:
    from apps.music.playlist import SONGS, PLAYLIST_NAME, PLAYLIST_DESC
except ImportError:
    SONGS = []
    PLAYLIST_NAME = "tomatitOS Media Player"
    PLAYLIST_DESC = ""

_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "assets")

# ─── Paleta de colores ────────────────────────────────────────────────────────
C_BG        = "#0c182b"
C_BG2       = "#060e1a"
C_BG3       = "#0a1428"
C_PANEL     = "#102444"
C_BORDER    = "#1c3d6e"
C_BORDER2   = "#285494"
C_ACCENT    = "#4a90d9"
C_ACCENT2   = "#55aaff"
C_GREEN     = "#39d353"
C_TEXT      = "#d0e0ff"
C_TEXT2     = "#8aabcc"
C_ACTIVE    = "#1f6fd9"
C_HOVER     = "#1a5ab8"
C_BTN       = "#1c4278"
C_BTN2      = "#163560"

_STYLES = f"""
QWidget#music_root {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: "Tahoma", "Segoe UI", sans-serif;
    font-size: 11px;
}}

/* ── Bienvenida ── */
QWidget#welcome_page {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #071020, stop:0.5 {C_BG}, stop:1 #071020);
}}

QLabel#wlc_title {{
    color: {C_ACCENT2};
    font-size: 18px;
    font-weight: bold;
    background: transparent;
    letter-spacing: 1px;
}}

QLabel#wlc_subtitle {{
    color: {C_TEXT2};
    font-size: 11px;
    background: transparent;
}}

QLabel#wlc_msg {{
    color: {C_TEXT};
    font-size: 13px;
    font-style: italic;
    background: transparent;
    padding: 0px 24px;
}}

QPushButton#btn_enter {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #2468c8, stop:1 #153e8a);
    color: #ffffff;
    border: 2px solid {C_ACCENT};
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 36px;
    letter-spacing: 1px;
}}
QPushButton#btn_enter:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #3a7ae0, stop:1 #1f56b0);
    border-color: {C_ACCENT2};
}}
QPushButton#btn_enter:pressed {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0e2a60, stop:1 #1a4080);
}}

/* ── Reproductor ── */
QWidget#player_page {{
    background-color: {C_BG};
}}

QFrame#header_frame {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0a1a38, stop:1 {C_BG2});
    border-bottom: 2px solid {C_BORDER2};
}}

QLabel#lbl_now_playing {{
    color: {C_GREEN};
    font-size: 9px;
    font-weight: bold;
    background: transparent;
    letter-spacing: 2px;
}}

QLabel#lbl_song_title {{
    color: {C_ACCENT2};
    font-size: 14px;
    font-weight: bold;
    background: transparent;
}}

QLabel#lbl_artist {{
    color: {C_TEXT2};
    font-size: 11px;
    background: transparent;
}}

QLabel#cover_lbl {{
    background-color: {C_BG2};
    border: 2px solid {C_BORDER};
}}

QTextEdit#lyrics_box {{
    background-color: transparent;
    color: {C_TEXT2};
    border: none;
    font-size: 12px;
    padding: 8px;
    selection-background-color: {C_ACTIVE};
}}

/* ── Playlist ── */
QListWidget#playlist_widget {{
    background-color: {C_BG2};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 0px;
    font-size: 11px;
    font-family: "Tahoma", "Segoe UI", sans-serif;
    outline: none;
}}
QListWidget#playlist_widget::item {{
    padding: 7px 10px;
    border-bottom: 1px solid #0d1e36;
    color: {C_TEXT};
}}
QListWidget#playlist_widget::item:alternate {{
    background-color: #090f1e;
}}
QListWidget#playlist_widget::item:hover {{
    background-color: #122848;
    color: #ffffff;
}}
QListWidget#playlist_widget::item:selected {{
    background-color: {C_ACTIVE};
    color: #ffffff;
}}

/* ── Panel de controles ── */
QFrame#controls_frame {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0e2040, stop:1 {C_PANEL});
    border-top: 2px solid {C_BORDER2};
}}

/* ── Barra de progreso ── */
QSlider#progress_slider::groove:horizontal {{
    height: 5px;
    background: {C_BG2};
    border: 1px solid {C_BORDER};
    border-radius: 2px;
}}
QSlider#progress_slider::sub-page:horizontal {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #1a8c3a, stop:1 {C_GREEN});
    border-radius: 2px;
}}
QSlider#progress_slider::handle:horizontal {{
    background: #ffffff;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
    border: 2px solid {C_GREEN};
}}
QSlider#progress_slider::handle:horizontal:hover {{
    background: {C_GREEN};
}}

/* ── Volumen ── */
QSlider#vol_slider::groove:horizontal {{
    height: 3px;
    background: {C_BG2};
    border-radius: 1px;
    border: 1px solid {C_BORDER};
}}
QSlider#vol_slider::sub-page:horizontal {{
    background: {C_ACCENT};
    border-radius: 1px;
}}
QSlider#vol_slider::handle:horizontal {{
    background: #ffffff;
    width: 9px;
    height: 9px;
    margin: -3px 0;
    border-radius: 4px;
    border: 1px solid {C_ACCENT};
}}

/* ── Botones de control ── */
QPushButton.ctrl {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #2060b0, stop:1 {C_BTN2});
    color: #ffffff;
    border: 1px solid {C_BORDER2};
    border-radius: 4px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton.ctrl:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #2e78d0, stop:1 #1a4888);
    border-color: {C_ACCENT};
}}
QPushButton.ctrl:pressed {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0c2050, stop:1 #162e60);
    border-color: {C_ACCENT2};
}}

QPushButton#btn_play {{
    border-radius: 18px;
    font-size: 15px;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #2878e0, stop:1 #144898);
    border: 2px solid {C_ACCENT};
}}
QPushButton#btn_play:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #3a90f0, stop:1 #1e60c0);
}}
QPushButton#btn_play:pressed {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0e2858, stop:1 #1a4898);
}}

QPushButton.mode_btn {{
    background: transparent;
    color: {C_TEXT2};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    font-size: 11px;
    padding: 2px 8px;
}}
QPushButton.mode_btn:hover {{
    background: #0e2040;
    color: {C_TEXT};
    border-color: {C_ACCENT};
}}
QPushButton.mode_btn[active="true"] {{
    background: #0d2d6b;
    color: {C_ACCENT2};
    border-color: {C_ACCENT};
    font-weight: bold;
}}

QLabel#time_lbl {{
    color: {C_GREEN};
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
    background: transparent;
}}
QLabel#vol_icon_lbl {{
    color: {C_TEXT2};
    font-size: 13px;
    background: transparent;
}}
QLabel#playlist_header {{
    color: {C_ACCENT};
    font-size: 11px;
    font-weight: bold;
    background: {C_BG2};
    padding: 4px 10px;
    border-bottom: 1px solid {C_BORDER};
}}
"""


def _load_cover(rel_path: str, size: int = 160) -> QPixmap:
    """Carga portada o genera placeholder."""
    if rel_path:
        path = os.path.join(ASSETS_DIR, rel_path)
        if os.path.exists(path):
            from PyQt6.QtGui import QImageReader
            reader = QImageReader(path)
            reader.setAutoTransform(True)
            img = reader.read()
            if not img.isNull():
                from PyQt6.QtGui import QPixmap as QP
                px = QP.fromImage(img)
                return px.scaled(size, size,
                                 Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
    # Placeholder
    px = QPixmap(size, size)
    px.fill(QColor(C_BG2))
    p = QPainter(px)
    p.setPen(QColor(C_BORDER))
    p.drawRect(0, 0, size - 1, size - 1)
    p.setFont(QFont("Segoe UI", size // 4))
    p.setPen(QColor(C_BORDER2))
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "🎵")
    p.end()
    return px


def _fmt_ms(ms: int) -> str:
    s = max(ms, 0) // 1000
    return f"{s // 60:02d}:{s % 60:02d}"


# ─── Visualizador ─────────────────────────────────────────────────────────────

class _Visualizer(QWidget):
    """12 barras animadas estilo WMP clásico."""

    BARS = 12
    TIMER_MS = 55

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self._heights = [0.1] * self.BARS
        self._targets = [0.1] * self.BARS
        self._playing = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TIMER_MS)

    def set_playing(self, playing: bool):
        self._playing = playing
        if not playing:
            self._targets = [0.05] * self.BARS

    def _tick(self):
        if self._playing:
            for i in range(self.BARS):
                if random.random() < 0.35:
                    self._targets[i] = random.uniform(0.1, 1.0)
        changed = False
        for i in range(self.BARS):
            diff = self._targets[i] - self._heights[i]
            step = diff * 0.25
            if abs(step) > 0.005:
                self._heights[i] += step
                changed = True
            elif abs(diff) > 0.005:
                self._heights[i] = self._targets[i]
                changed = True
        if changed:
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        bar_w = max(1, (w - (self.BARS + 1) * 2) // self.BARS)
        for i, height_ratio in enumerate(self._heights):
            x = 2 + i * (bar_w + 2)
            bar_h = max(2, int(height_ratio * (h - 4)))
            y = h - 2 - bar_h
            # Gradiente azul→verde
            grad = QLinearGradient(x, y + bar_h, x, y)
            grad.setColorAt(0.0, QColor(C_ACCENT))
            grad.setColorAt(1.0, QColor(C_GREEN))
            p.fillRect(x, y, bar_w, bar_h, QBrush(grad))
        p.end()


# ─── Pantalla de bienvenida ───────────────────────────────────────────────────

class _WelcomePage(QWidget):
    """Pantalla de bienvenida retro."""

    def __init__(self, name: str, desc: str, parent=None):
        super().__init__(parent)
        self.setObjectName("welcome_page")
        self._build(name, desc)

    def _build(self, name: str, desc: str):
        v = QVBoxLayout(self)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(0)
        v.addStretch(1)

        # Título
        title = QLabel(f"🎵  {name}")
        title.setObjectName("wlc_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(title)

        v.addSpacing(6)

        subtitle = QLabel("tomatitOS Media Player  •  v1.0")
        subtitle.setObjectName("wlc_subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(subtitle)

        v.addSpacing(28)

        # Separador visual
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C_BORDER2}; background: {C_BORDER2}; max-height: 1px;")
        v.addWidget(sep)

        v.addSpacing(28)

        # Mensaje preparado
        msg = QLabel(f'"{desc}"')
        msg.setObjectName("wlc_msg")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setMaximumWidth(440)
        msg.setMinimumHeight(80)
        v.addWidget(msg, alignment=Qt.AlignmentFlag.AlignCenter)

        v.addSpacing(32)

        # Visualizador decorativo (estático)
        viz_lbl = QLabel("♪  ♫  ♪  ♫  ♪  ♫  ♪  ♫  ♪  ♫")
        viz_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        viz_lbl.setStyleSheet(f"color: {C_ACCENT}; font-size: 16px; background: transparent; letter-spacing: 4px;")
        v.addWidget(viz_lbl)

        v.addSpacing(32)

        # Botón entrar
        self.btn_enter = QPushButton("▶   ENTRAR")
        self.btn_enter.setObjectName("btn_enter")
        self.btn_enter.setFixedSize(200, 46)
        v.addWidget(self.btn_enter, alignment=Qt.AlignmentFlag.AlignCenter)

        v.addStretch(1)

        # Pie
        foot = QLabel("❤  hecho con amor  ❤")
        foot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        foot.setStyleSheet(f"color: {C_BORDER2}; font-size: 10px; background: transparent;")
        v.addWidget(foot)

    def paintEvent(self, event):
        """Fondo degradado + borde sutil."""
        p = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#071020"))
        grad.setColorAt(0.5, QColor(C_BG))
        grad.setColorAt(1.0, QColor("#071020"))
        p.fillRect(self.rect(), grad)
        p.setPen(QPen(QColor(C_BORDER2), 1))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.end()


# ─── App principal ────────────────────────────────────────────────────────────

class MusicApp(BaseApp):
    """Reproductor de música tomatitOS con estética Windows XP."""

    def __init__(self, resources: ResourceManager, sounds: SoundManager, parent=None):
        # Estado antes de super().__init__ (que llama _build_ui)
        self._current_index: int = -1
        self._duration_ms: int = 0
        self._is_seeking: bool = False
        self._player: QMediaPlayer | None = None
        self._audio_out: QAudioOutput | None = None
        # Shuffle
        self._shuffle: bool = False
        self._shuffle_order: list[int] = []
        self._shuffle_pos: int = 0
        # Repeat: 0=off, 1=playlist, 2=song
        self._repeat: int = 0
        super().__init__(resources, sounds, parent)
        self._init_audio()
        if SONGS:
            self._load_song(0, autoplay=False)

    # ─── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("music_root")
        self.setMinimumSize(600, 420)
        self.setStyleSheet(_STYLES)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Stack: página 0 = bienvenida, página 1 = reproductor
        self._stack = QStackedWidget()
        self._stack.setObjectName("music_root")

        # ── Página 0: Bienvenida ──
        self._welcome = _WelcomePage(PLAYLIST_NAME, PLAYLIST_DESC)
        self._welcome.btn_enter.clicked.connect(self._enter_player)
        self._stack.addWidget(self._welcome)

        # ── Página 1: Reproductor ──
        self._player_page = self._build_player_page()
        self._stack.addWidget(self._player_page)

        root.addWidget(self._stack)

    def _build_player_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("player_page")
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # ── Header: info canción ──
        header = QFrame()
        header.setObjectName("header_frame")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 8, 12, 8)
        h_layout.setSpacing(12)

        # Portada
        self._cover_lbl = QLabel()
        self._cover_lbl.setObjectName("cover_lbl")
        self._cover_lbl.setFixedSize(80, 80)
        self._cover_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_lbl.setPixmap(_load_cover("", 80))
        h_layout.addWidget(self._cover_lbl)

        # Info texto
        info_v = QVBoxLayout()
        info_v.setSpacing(2)

        self._lbl_now = QLabel("◼  DETENIDO")
        self._lbl_now.setObjectName("lbl_now_playing")
        info_v.addWidget(self._lbl_now)

        self._lbl_title = QLabel("—")
        self._lbl_title.setObjectName("lbl_song_title")
        info_v.addWidget(self._lbl_title)

        self._lbl_artist = QLabel("—")
        self._lbl_artist.setObjectName("lbl_artist")
        info_v.addWidget(self._lbl_artist)

        info_v.addStretch()
        h_layout.addLayout(info_v, 1)

        # Visualizador en header
        self._visualizer = _Visualizer()
        h_layout.addWidget(self._visualizer)

        v.addWidget(header)

        # ── Cuerpo: portada grande + letras | playlist ──
        body = QWidget()
        body_h = QHBoxLayout(body)
        body_h.setContentsMargins(0, 0, 0, 0)
        body_h.setSpacing(0)

        # Panel izquierdo: letras (sin portada grande)
        left = QWidget()
        left.setStyleSheet(f"background: {C_BG3};")
        left_v = QVBoxLayout(left)
        left_v.setContentsMargins(16, 16, 16, 16)
        left_v.setSpacing(12)

        self._lyrics_box = QTextEdit()
        self._lyrics_box.setObjectName("lyrics_box")
        self._lyrics_box.setReadOnly(True)
        self._lyrics_box.setPlaceholderText("Sin letra disponible.")
        # Make the font a little larger since it takes up the whole space now
        self._lyrics_box.setStyleSheet(f"font-size: 14px; background-color: transparent; color: {C_TEXT2}; border: none;")
        self._lyrics_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_v.addWidget(self._lyrics_box, 1)

        body_h.addWidget(left, 2)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {C_BORDER}; background: {C_BORDER};")
        body_h.addWidget(sep)

        # Panel derecho: playlist
        right = QWidget()
        right.setStyleSheet(f"background: {C_BG2};")
        right_v = QVBoxLayout(right)
        right_v.setContentsMargins(0, 0, 0, 0)
        right_v.setSpacing(0)

        pl_header = QLabel(f"  ♪  {PLAYLIST_NAME}")
        pl_header.setObjectName("playlist_header")
        right_v.addWidget(pl_header)

        self._playlist_widget = QListWidget()
        self._playlist_widget.setObjectName("playlist_widget")
        self._playlist_widget.setAlternatingRowColors(True)
        self._populate_playlist()
        self._playlist_widget.itemClicked.connect(self._on_item_clicked)
        right_v.addWidget(self._playlist_widget, 1)

        body_h.addWidget(right, 3)

        v.addWidget(body, 1)

        # ── Controles ──
        v.addWidget(self._build_controls())
        return page

    def _build_controls(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("controls_frame")
        frame.setFixedHeight(90)
        v = QVBoxLayout(frame)
        v.setContentsMargins(14, 8, 14, 8)
        v.setSpacing(6)

        # Barra de progreso
        prog_row = QHBoxLayout()
        prog_row.setSpacing(8)
        self._lbl_pos = QLabel("00:00")
        self._lbl_pos.setObjectName("time_lbl")
        self._lbl_pos.setFixedWidth(38)
        prog_row.addWidget(self._lbl_pos)

        self._progress = QSlider(Qt.Orientation.Horizontal)
        self._progress.setObjectName("progress_slider")
        self._progress.setRange(0, 1000)
        self._progress.sliderPressed.connect(self._seek_start)
        self._progress.sliderReleased.connect(self._seek_end)
        prog_row.addWidget(self._progress, 1)

        self._lbl_dur = QLabel("00:00")
        self._lbl_dur.setObjectName("time_lbl")
        self._lbl_dur.setFixedWidth(38)
        self._lbl_dur.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prog_row.addWidget(self._lbl_dur)
        v.addLayout(prog_row)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        # ◀◀ Anterior
        self._btn_prev = QPushButton("⏮")
        self._btn_prev.setProperty("class", "ctrl")
        self._btn_prev.setFixedSize(32, 32)
        self._btn_prev.setToolTip("Anterior")
        self._btn_prev.clicked.connect(self._prev)
        btn_row.addWidget(self._btn_prev)

        # ▶/⏸ Play/Pause
        self._btn_play = QPushButton("▶")
        self._btn_play.setObjectName("btn_play")
        self._btn_play.setFixedSize(36, 36)
        self._btn_play.setToolTip("Reproducir / Pausar")
        self._btn_play.clicked.connect(self._play_pause)
        btn_row.addWidget(self._btn_play)

        # ▶▶ Siguiente
        self._btn_next = QPushButton("⏭")
        self._btn_next.setProperty("class", "ctrl")
        self._btn_next.setFixedSize(32, 32)
        self._btn_next.setToolTip("Siguiente")
        self._btn_next.clicked.connect(self._next)
        btn_row.addWidget(self._btn_next)

        btn_row.addSpacing(10)

        # 🔀 Shuffle
        self._btn_shuffle = QPushButton("🔀")
        self._btn_shuffle.setProperty("class", "mode_btn")
        self._btn_shuffle.setFixedSize(36, 24)
        self._btn_shuffle.setToolTip("Reproducción aleatoria")
        self._btn_shuffle.setCheckable(False)
        self._btn_shuffle.clicked.connect(self._toggle_shuffle)
        btn_row.addWidget(self._btn_shuffle)

        # 🔁 Repeat
        self._btn_repeat = QPushButton("🔁")
        self._btn_repeat.setProperty("class", "mode_btn")
        self._btn_repeat.setFixedSize(36, 24)
        self._btn_repeat.setToolTip("Repetir: OFF")
        self._btn_repeat.clicked.connect(self._toggle_repeat)
        btn_row.addWidget(self._btn_repeat)

        btn_row.addStretch()

        # 🔊 Volumen
        self._vol_icon = QLabel("🔊")
        self._vol_icon.setObjectName("vol_icon_lbl")
        btn_row.addWidget(self._vol_icon)

        self._vol_slider = QSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setObjectName("vol_slider")
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(80)
        self._vol_slider.setFixedWidth(80)
        self._vol_slider.valueChanged.connect(self._set_volume)
        btn_row.addWidget(self._vol_slider)

        v.addLayout(btn_row)
        return frame

    # ─── Transición ──────────────────────────────────────────────────────────

    def _enter_player(self):
        """Fade-out bienvenida → fade-in reproductor."""
        eff_out = QGraphicsOpacityEffect(self._welcome)
        self._welcome.setGraphicsEffect(eff_out)
        anim_out = QPropertyAnimation(eff_out, b"opacity", self)
        anim_out.setDuration(350)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)
        anim_out.setEasingCurve(QEasingCurve.Type.InQuad)

        def _switch():
            self._stack.setCurrentIndex(1)
            self._welcome.setGraphicsEffect(None)
            eff_in = QGraphicsOpacityEffect(self._player_page)
            self._player_page.setGraphicsEffect(eff_in)
            anim_in = QPropertyAnimation(eff_in, b"opacity", self)
            anim_in.setDuration(350)
            anim_in.setStartValue(0.0)
            anim_in.setEndValue(1.0)
            anim_in.setEasingCurve(QEasingCurve.Type.OutQuad)
            anim_in.finished.connect(lambda: self._player_page.setGraphicsEffect(None))
            anim_in.start()
            if self._current_index >= 0:
                self._player.play()
                self._btn_play.setText("⏸")
                self._lbl_now.setText("▶  REPRODUCIENDO")
                self._visualizer.set_playing(True)

        anim_out.finished.connect(_switch)
        anim_out.start()

    # ─── Audio ───────────────────────────────────────────────────────────────

    def _init_audio(self) -> None:
        self._player = QMediaPlayer(self)
        self._audio_out = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)
        self._audio_out.setVolume(0.8)

        self._player.positionChanged.connect(self._on_position)
        self._player.durationChanged.connect(self._on_duration)
        self._player.mediaStatusChanged.connect(self._on_media_status)
        self._player.playbackStateChanged.connect(self._on_playback_state)

    # ─── Gestión de canciones ─────────────────────────────────────────────────

    def _load_song(self, index: int, autoplay: bool = True) -> None:
        if not SONGS or not (0 <= index < len(SONGS)):
            return
        self._current_index = index
        song = SONGS[index]

        self._lbl_title.setText(song.get("title", "—"))
        self._lbl_artist.setText(song.get("artist", "—"))

        cover = _load_cover(song.get("cover", ""), 80)
        self._cover_lbl.setPixmap(cover)

        lyrics = song.get("lyrics", "")
        self._lyrics_box.setText(lyrics)
        self._lyrics_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        audio_path = os.path.join(ASSETS_DIR, song.get("file", ""))
        if os.path.exists(audio_path):
            self._player.setSource(QUrl.fromLocalFile(audio_path))
        else:
            self._player.setSource(QUrl())

        # Actualizar playlist visual
        self._update_playlist_indicator(index)

        self._progress.setValue(0)
        self._lbl_pos.setText("00:00")
        self._lbl_dur.setText("00:00")

        if autoplay and self._stack.currentIndex() == 1:
            self._player.play()
            self._btn_play.setText("⏸")
            self._lbl_now.setText("▶  REPRODUCIENDO")
            self._visualizer.set_playing(True)

    def _populate_playlist(self) -> None:
        self._playlist_widget.clear()
        for i, s in enumerate(SONGS):
            title = s.get("title", "—")
            artist = s.get("artist", "—")
            item = QListWidgetItem(f"  {i+1:02d}   {title}  —  {artist}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self._playlist_widget.addItem(item)

    def _update_playlist_indicator(self, index: int) -> None:
        for i in range(self._playlist_widget.count()):
            item = self._playlist_widget.item(i)
            idx = item.data(Qt.ItemDataRole.UserRole)
            song = SONGS[idx]
            title = song.get("title", "—")
            artist = song.get("artist", "—")
            if idx == index:
                item.setText(f"▶ {idx+1:02d}   {title}  —  {artist}")
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QColor(C_ACCENT2))
            else:
                item.setText(f"  {idx+1:02d}   {title}  —  {artist}")
                font = item.font()
                font.setBold(False)
                item.setFont(font)
                item.setForeground(QColor(C_TEXT))
        self._playlist_widget.setCurrentRow(index)
        self._playlist_widget.scrollToItem(
            self._playlist_widget.item(index),
            QListWidget.ScrollHint.EnsureVisible
        )

    # ─── Controles ───────────────────────────────────────────────────────────

    def _play_pause(self) -> None:
        if self.sounds:
            self.sounds.play_click()
        if not self._player:
            return
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self._btn_play.setText("▶")
            self._lbl_now.setText("❚❚  PAUSADO")
            self._visualizer.set_playing(False)
        else:
            if self._current_index < 0 and SONGS:
                self._load_song(0, autoplay=False)
            self._player.play()
            self._btn_play.setText("⏸")
            self._lbl_now.setText("▶  REPRODUCIENDO")
            self._visualizer.set_playing(True)

    def _next(self) -> None:
        """Siguiente canción (llamado por botón → con sonido click)."""
        if self.sounds:
            self.sounds.play_click()
        self._go_next()

    def _prev(self) -> None:
        if self.sounds:
            self.sounds.play_click()
        if not SONGS:
            return
        if self._player and self._player.position() > 3000:
            self._player.setPosition(0)
            return
        self._go_prev()

    def _advance_auto(self) -> None:
        """Avance automático al terminar una canción — SIN sonido de click."""
        if self._repeat == 2:
            # Repetir canción
            self._player.setPosition(0)
            self._player.play()
            return
        self._go_next(wrap=self._repeat == 1)

    def _go_next(self, wrap: bool = True) -> None:
        if not SONGS:
            return
        if self._shuffle:
            self._shuffle_pos = (self._shuffle_pos + 1) % len(self._shuffle_order)
            next_idx = self._shuffle_order[self._shuffle_pos]
        else:
            next_idx = self._current_index + 1
            if next_idx >= len(SONGS):
                if wrap:
                    next_idx = 0
                else:
                    self._player.stop()
                    self._btn_play.setText("▶")
                    self._lbl_now.setText("◼  DETENIDO")
                    self._visualizer.set_playing(False)
                    return
        self._load_song(next_idx)

    def _go_prev(self) -> None:
        if not SONGS:
            return
        if self._shuffle:
            self._shuffle_pos = (self._shuffle_pos - 1) % len(self._shuffle_order)
            prev_idx = self._shuffle_order[self._shuffle_pos]
        else:
            prev_idx = (self._current_index - 1) % len(SONGS)
        self._load_song(prev_idx)

    # ─── Shuffle ─────────────────────────────────────────────────────────────

    def _toggle_shuffle(self) -> None:
        self._shuffle = not self._shuffle
        if self._shuffle:
            order = list(range(len(SONGS)))
            random.shuffle(order)
            # Poner la canción actual al inicio del orden
            if self._current_index in order:
                order.remove(self._current_index)
                order.insert(0, self._current_index)
            self._shuffle_order = order
            self._shuffle_pos = 0
            self._btn_shuffle.setProperty("active", "true")
        else:
            self._btn_shuffle.setProperty("active", "false")
        # Refrescar estilo del botón
        self._btn_shuffle.style().unpolish(self._btn_shuffle)
        self._btn_shuffle.style().polish(self._btn_shuffle)

    # ─── Repeat ──────────────────────────────────────────────────────────────

    def _toggle_repeat(self) -> None:
        self._repeat = (self._repeat + 1) % 3
        labels = {0: "🔁", 1: "🔁 ∞", 2: "🔂"}
        tips = {0: "Repetir: OFF", 1: "Repetir: Playlist", 2: "Repetir: Canción"}
        active = {0: "false", 1: "true", 2: "true"}
        self._btn_repeat.setText(labels[self._repeat])
        self._btn_repeat.setToolTip(tips[self._repeat])
        self._btn_repeat.setProperty("active", active[self._repeat])
        self._btn_repeat.style().unpolish(self._btn_repeat)
        self._btn_repeat.style().polish(self._btn_repeat)

    # ─── Volumen ─────────────────────────────────────────────────────────────

    def _set_volume(self, val: int) -> None:
        if self._audio_out:
            self._audio_out.setVolume(val / 100.0)
        if val == 0:
            self._vol_icon.setText("🔇")
        elif val < 40:
            self._vol_icon.setText("🔉")
        else:
            self._vol_icon.setText("🔊")

    # ─── Señales del player ───────────────────────────────────────────────────

    def _seek_start(self) -> None:
        self._is_seeking = True

    def _seek_end(self) -> None:
        self._is_seeking = False
        if self._player and self._duration_ms > 0:
            target = int((self._progress.value() / 1000) * self._duration_ms)
            self._player.setPosition(target)

    def _on_position(self, pos: int) -> None:
        if not self._is_seeking and self._duration_ms > 0:
            self._progress.setValue(int(pos / self._duration_ms * 1000))
        self._lbl_pos.setText(_fmt_ms(pos))

    def _on_duration(self, dur: int) -> None:
        self._duration_ms = dur
        self._lbl_dur.setText(_fmt_ms(dur))

    def _on_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._advance_auto()   # ← Sin play_click() → sin beep

    def _on_playback_state(self, state: QMediaPlayer.PlaybackState) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self._visualizer.set_playing(playing)
        if playing:
            self._btn_play.setText("⏸")
            self._lbl_now.setText("▶  REPRODUCIENDO")
        else:
            if state == QMediaPlayer.PlaybackState.PausedState:
                self._btn_play.setText("▶")
                self._lbl_now.setText("❚❚  PAUSADO")

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx == self._current_index:
            # Click en canción actual → play/pause
            self._play_pause()
        else:
            if self.sounds:
                self.sounds.play_click()
            self._load_song(idx)

    # ─── Cierre ──────────────────────────────────────────────────────────────

    def showEvent(self, event) -> None:
        super().showEvent(event)
        frame = self.parentWidget()
        if frame and hasattr(frame, "hide_on_close"):
            # Ocultar (minimizar) en lugar de cerrar SI la música está sonando
            frame.hide_on_close = lambda: self._player and self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def closeEvent(self, event) -> None:
        try:
            if hasattr(self, "_visualizer"):
                self._visualizer._timer.stop()
            if hasattr(self, "_player") and self._player:
                self._player.stop()
                self._player = None
            if hasattr(self, "_audio_out") and self._audio_out:
                self._audio_out = None
        except Exception:
            pass
        super().closeEvent(event)
