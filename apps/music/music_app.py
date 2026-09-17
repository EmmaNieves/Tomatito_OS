"""
music_app.py — Reproductor de música limpio estilo Windows Media Player.

Sin pestañas extra innecesarias. Colores de alto contraste
que previenen interferencia del tema global XP.
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QListWidget, QListWidgetItem,
    QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from apps.base_app import BaseApp
from core.resource_manager import ResourceManager
from core.sound_manager import SoundManager

try:
    from apps.music.playlist import SONGS
except ImportError:
    SONGS = []

_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "assets")

_WMP_STYLES = """
QWidget#music_app_root {
    background-color: #0c182b;
    color: #ffffff;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}

QFrame#screen_header {
    background-color: #060e1a;
    border-bottom: 1px solid #1c3d6e;
}

QLabel#lbl_title {
    color: #55aaff;
    font-size: 13px;
    font-weight: bold;
    background: transparent;
}

QLabel#lbl_artist {
    color: #b0c4de;
    font-size: 11px;
    background: transparent;
}

QLabel#cover_display {
    background-color: #040810;
    border: 1px solid #1c3d6e;
}

QListWidget#playlist {
    background-color: #060e1a;
    color: #ffffff;
    border: 1px solid #1c3d6e;
    font-size: 11px;
}

QListWidget#playlist::item {
    padding: 8px;
    border-bottom: 1px solid #0f2038;
    color: #d0e0ff;
    background-color: #060e1a;
}

QListWidget#playlist::item:hover {
    background-color: #122848;
    color: #ffffff;
}

QListWidget#playlist::item:selected {
    background-color: #1f4b8e;
    color: #ffffff;
    font-weight: bold;
}

QFrame#bottom_controls {
    background-color: #102444;
    border-top: 1px solid #285494;
}

QPushButton.control_btn {
    background-color: #1c4278;
    color: #ffffff;
    border: 1px solid #4a7cb8;
    border-radius: 14px;
    font-size: 11px;
    font-weight: bold;
}

QPushButton.control_btn:hover {
    background-color: #28589c;
    border-color: #70a0e0;
}

QPushButton.control_btn:pressed {
    background-color: #0e2648;
}

QPushButton#btn_play {
    border-radius: 17px;
    font-size: 13px;
    background-color: #205090;
}

QSlider#progress_bar::groove:horizontal {
    height: 4px;
    background: #060e1a;
    border: 1px solid #1c3d6e;
    border-radius: 2px;
}

QSlider#progress_bar::sub-page:horizontal {
    background: #39d353;
    border-radius: 2px;
}

QSlider#progress_bar::handle:horizontal {
    background: #ffffff;
    width: 10px;
    height: 10px;
    margin: -3px 0;
    border-radius: 5px;
    border: 1px solid #102444;
}

QSlider#vol_slider::groove:horizontal {
    height: 3px;
    background: #060e1a;
    border-radius: 1px;
}

QSlider#vol_slider::sub-page:horizontal {
    background: #55aaff;
    border-radius: 1px;
}

QSlider#vol_slider::handle:horizontal {
    background: #ffffff;
    width: 8px;
    height: 8px;
    margin: -2px 0;
    border-radius: 4px;
}

QLabel#time_lbl {
    color: #39d353;
    font-family: "Consolas", monospace;
    font-size: 11px;
    font-weight: bold;
    background: transparent;
}

QLabel#vol_icon {
    color: #b0c4de;
    font-size: 12px;
    background: transparent;
}
"""


def _load_cover_image(cover_rel: str) -> QPixmap:
    if cover_rel:
        path = os.path.join(ASSETS_DIR, cover_rel)
        if os.path.exists(path):
            px = QPixmap(path)
            if not px.isNull():
                return px.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    px = QPixmap(200, 200)
    px.fill(QColor("#040810"))
    p = QPainter(px)
    p.setPen(QColor("#1c3d6e"))
    p.drawRect(0, 0, 199, 199)
    p.setFont(QFont("Segoe UI", 48))
    p.setPen(QColor("#285494"))
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "🎵")
    p.end()
    return px


def _fmt(ms: int) -> str:
    s = max(ms, 0) // 1000
    return f"{s // 60:02d}:{s % 60:02d}"


class MusicApp(BaseApp):
    """Reproductor de música con estética Windows Media Player."""

    def __init__(self, resources: ResourceManager, sounds: SoundManager, parent=None):
        self._current_index: int = -1
        self._duration_ms: int = 0
        self._is_seeking: bool = False
        self._player: QMediaPlayer | None = None
        self._audio_out: QAudioOutput | None = None
        super().__init__(resources, sounds, parent)
        self._init_audio()
        if SONGS:
            self._load_song(0)

    def _build_ui(self) -> None:
        self.setObjectName("music_app_root")
        self.setMinimumSize(540, 400)
        self.setStyleSheet(_WMP_STYLES)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Divisor principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        # Panel izquierdo: Pantalla de reproducción
        screen_panel = QWidget()
        screen_v = QVBoxLayout(screen_panel)
        screen_v.setContentsMargins(0, 0, 0, 0)
        screen_v.setSpacing(0)

        # Encabezado con información de la canción
        header = QFrame()
        header.setObjectName("screen_header")
        header_v = QVBoxLayout(header)
        header_v.setContentsMargins(12, 8, 12, 8)
        header_v.setSpacing(2)

        self._lbl_artist = QLabel("Artista")
        self._lbl_artist.setObjectName("lbl_artist")
        header_v.addWidget(self._lbl_artist)

        self._lbl_title = QLabel("Título de la canción")
        self._lbl_title.setObjectName("lbl_title")
        header_v.addWidget(self._lbl_title)

        screen_v.addWidget(header)

        # Área central de portada
        cover_container = QWidget()
        cover_container.setStyleSheet("background-color: #040810;")
        cover_layout = QVBoxLayout(cover_container)
        cover_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._cover_display = QLabel()
        self._cover_display.setObjectName("cover_display")
        self._cover_display.setFixedSize(200, 200)
        self._cover_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_display.setPixmap(_load_cover_image(""))
        cover_layout.addWidget(self._cover_display)

        screen_v.addWidget(cover_container, stretch=1)
        splitter.addWidget(screen_panel)

        # Panel derecho: Playlist
        self._playlist_widget = QListWidget()
        self._playlist_widget.setObjectName("playlist")
        self._populate_playlist()
        self._playlist_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        splitter.addWidget(self._playlist_widget)

        splitter.setSizes([340, 200])
        root.addWidget(splitter, stretch=1)

        # Panel inferior de controles
        root.addWidget(self._build_controls())

    def _build_controls(self) -> QFrame:
        controls = QFrame()
        controls.setObjectName("bottom_controls")
        v = QVBoxLayout(controls)
        v.setContentsMargins(12, 8, 12, 10)
        v.setSpacing(8)

        # Barra de progreso
        self._progress = QSlider(Qt.Orientation.Horizontal)
        self._progress.setObjectName("progress_bar")
        self._progress.setRange(0, 1000)
        self._progress.sliderPressed.connect(self._on_seek_start)
        self._progress.sliderReleased.connect(self._on_seek_end)
        v.addWidget(self._progress)

        # Botones y controles
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        self._btn_prev = QPushButton("⏮")
        self._btn_prev.setProperty("class", "control_btn")
        self._btn_prev.setFixedSize(28, 28)
        self._btn_prev.clicked.connect(self._prev)
        h.addWidget(self._btn_prev)

        self._btn_play = QPushButton("▶")
        self._btn_play.setObjectName("btn_play")
        self._btn_play.setProperty("class", "control_btn")
        self._btn_play.setFixedSize(34, 34)
        self._btn_play.clicked.connect(self._play_pause)
        h.addWidget(self._btn_play)

        self._btn_next = QPushButton("⏭")
        self._btn_next.setProperty("class", "control_btn")
        self._btn_next.setFixedSize(28, 28)
        self._btn_next.clicked.connect(self._next)
        h.addWidget(self._btn_next)

        h.addSpacing(10)

        self._lbl_time = QLabel("00:00 / 00:00")
        self._lbl_time.setObjectName("time_lbl")
        h.addWidget(self._lbl_time)

        h.addStretch()

        vol_icon = QLabel("🔊")
        vol_icon.setObjectName("vol_icon")
        h.addWidget(vol_icon)

        self._vol_slider = QSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setObjectName("vol_slider")
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(80)
        self._vol_slider.setFixedWidth(70)
        self._vol_slider.valueChanged.connect(self._set_volume)
        h.addWidget(self._vol_slider)

        v.addLayout(h)
        return controls

    def _populate_playlist(self) -> None:
        self._playlist_widget.clear()
        for i, s in enumerate(SONGS):
            item = QListWidgetItem(f"{i+1:02d}. {s['title']}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self._playlist_widget.addItem(item)

    def _init_audio(self) -> None:
        self._player = QMediaPlayer(self)
        self._audio_out = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)
        self._audio_out.setVolume(0.8)

        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status)

    def _load_song(self, index: int) -> None:
        if not SONGS or not (0 <= index < len(SONGS)):
            return

        self._current_index = index
        song = SONGS[index]

        self._lbl_title.setText(song.get("title", "Desconocido"))
        self._lbl_artist.setText(song.get("artist", "Artista desconocido"))

        px = _load_cover_image(song.get("cover", ""))
        self._cover_display.setPixmap(px)

        audio_path = os.path.join(ASSETS_DIR, song.get("file", ""))
        if os.path.exists(audio_path):
            self._player.setSource(QUrl.fromLocalFile(audio_path))
        else:
            self._player.setSource(QUrl())

        self._playlist_widget.setCurrentRow(index)

    def _play_pause(self) -> None:
        if not self._player:
            return
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self._btn_play.setText("▶")
        else:
            if self._current_index == -1 and SONGS:
                self._load_song(0)
            self._player.play()
            self._btn_play.setText("⏸")

    def _next(self) -> None:
        if not SONGS:
            return
        next_idx = (self._current_index + 1) % len(SONGS)
        self._load_song(next_idx)
        self._player.play()
        self._btn_play.setText("⏸")

    def _prev(self) -> None:
        if not SONGS:
            return
        if self._player and self._player.position() > 3000:
            self._player.setPosition(0)
            return
        prev_idx = (self._current_index - 1) % len(SONGS)
        self._load_song(prev_idx)
        self._player.play()
        self._btn_play.setText("⏸")

    def _set_volume(self, val: int) -> None:
        if self._audio_out:
            self._audio_out.setVolume(val / 100.0)

    def _on_seek_start(self) -> None:
        self._is_seeking = True

    def _on_seek_end(self) -> None:
        self._is_seeking = False
        if self._player and self._duration_ms > 0:
            target = int((self._progress.value() / 1000) * self._duration_ms)
            self._player.setPosition(target)

    def _on_position_changed(self, pos: int) -> None:
        if not self._is_seeking and self._duration_ms > 0:
            self._progress.setValue(int(pos / self._duration_ms * 1000))
        self._lbl_time.setText(f"{_fmt(pos)} / {_fmt(self._duration_ms)}")

    def _on_duration_changed(self, dur: int) -> None:
        self._duration_ms = dur
        pos = self._player.position() if self._player else 0
        self._lbl_time.setText(f"{_fmt(pos)} / {_fmt(dur)}")

    def _on_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._next()

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        idx = item.data(Qt.ItemDataRole.UserRole)
        self._load_song(idx)
        self._player.play()
        self._btn_play.setText("⏸")

    def closeEvent(self, event) -> None:
        if self._player:
            self._player.stop()
        super().closeEvent(event)
