"""
photo_viewer.py — Visor de fotografías a pantalla completa (dentro del sistema).

Características:
- Muestra la foto ajustada al espacio disponible (sin deformar).
- Navegación: botones anterior / siguiente + teclado (← →).
- Botón para volver a la galería/álbum sin tener que cerrar la ventana.
- Nombre del archivo visible en la barra inferior.
- Se integra dentro de un WindowFrame del sistema de ventanas.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl
from PyQt6.QtGui import QPixmap, QKeyEvent, QImage
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PIL import Image


import io

def _load_pixmap_with_pillow(path: str) -> QPixmap:
    """Carga una imagen de forma 100% segura (soporta WEBP, JPEG, PNG y EXIF)."""
    if not path or not os.path.exists(path):
        return QPixmap()
    
    try:
        from PyQt6.QtGui import QImageReader
        reader = QImageReader(path)
        reader.setAutoTransform(True) # Aplica rotación EXIF automáticamente
        img = reader.read()
        if not img.isNull():
            from PyQt6.QtGui import QPixmap
            return QPixmap.fromImage(img)
            
        from PIL import Image, ImageOps
        import io
        img_pil = Image.open(path)
        img_pil = ImageOps.exif_transpose(img_pil)
        buf = io.BytesIO()
        img_pil.save(buf, format="PNG")
        from PyQt6.QtGui import QPixmap
        pix = QPixmap()
        pix.loadFromData(buf.getvalue())
        return pix
    except Exception:
        from PyQt6.QtGui import QPixmap
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
    """Visor de fotografías con botón de retorno y navegación."""

    back_requested = pyqtSignal()

    def __init__(self, photo_paths: list[str], start_index: int = 0, album_name: str = "", parent=None):
        super().__init__(parent)
        self._paths = photo_paths
        self._index = max(0, min(start_index, len(photo_paths) - 1))
        self._album_name = album_name
        self._cache: dict[str, QPixmap] = {}

        self.setStyleSheet("background: #1a1a1a;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._build_ui()
        self._load_current()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra superior con botón Volver
        header = QFrame()
        header.setFixedHeight(36)
        header.setStyleSheet("background: #111111; border-bottom: 1px solid #333333;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 4, 8, 4)

        btn_back = QPushButton("← Volver a la galería")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #3a3a3a;
                border-color: #777777;
            }
        """)
        btn_back.clicked.connect(self._go_back)
        h_layout.addWidget(btn_back)
        h_layout.addStretch()

        layout.addWidget(header)

        # Área principal de imagen
        self._img_area = QWidget()
        self._img_area.setStyleSheet("background: #1a1a1a;")
        img_layout = QHBoxLayout(self._img_area)
        img_layout.setContentsMargins(8, 8, 8, 8)
        img_layout.setSpacing(8)

        # Botón anterior
        self._btn_prev = _NavButton("◀")
        self._btn_prev.clicked.connect(self._go_prev)
        img_layout.addWidget(self._btn_prev, 0, Qt.AlignmentFlag.AlignVCenter)

        # Contenedor de visualización (Imagen o Video)
        self._media_stack = QStackedWidget()
        
        # 1. Imagen
        self._photo_label = QLabel()
        self._photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._photo_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._photo_label.setStyleSheet("background: transparent;")
        self._media_stack.addWidget(self._photo_label)

        # 2. Video
        self._video_widget = QVideoWidget(self)
        self._media_player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._media_player.setAudioOutput(self._audio_output)
        self._media_player.setVideoOutput(self._video_widget)
        self._media_stack.addWidget(self._video_widget)

        img_layout.addWidget(self._media_stack, 1)

        # Botón siguiente
        self._btn_next = _NavButton("▶")
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
        elif event.key() == Qt.Key.Key_Escape:
            self._go_back()
        else:
            super().keyPressEvent(event)

    def cleanup(self):
        """Detiene y desconecta el reproductor de video de forma 100% segura para evitar bloqueos."""
        if hasattr(self, '_media_player') and self._media_player is not None:
            try:
                self._media_player.stop()
                self._media_player.setSource(QUrl())
                self._media_player.setVideoOutput(None)
                self._media_player.setAudioOutput(None)
            except Exception:
                pass
        self._resume_music_if_needed()

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

    def hideEvent(self, event):
        if hasattr(self, '_media_player') and self._media_player is not None:
            try:
                self._media_player.stop()
            except Exception:
                pass
        self._resume_music_if_needed()
        super().hideEvent(event)

    def _resume_music_if_needed(self):
        if getattr(self, "_music_paused_by_video", False):
            self._music_paused_by_video = False
            try:
                from PyQt6.QtWidgets import QApplication
                for w in QApplication.topLevelWidgets():
                    if hasattr(w, "_open_apps") and "music" in w._open_apps:
                        music_app = w._open_apps["music"]._content_layout.itemAt(0).widget()
                        if hasattr(music_app, "_player") and music_app._player:
                            music_app._player.play()
                            if hasattr(music_app, "_btn_play"): music_app._btn_play.setText("⏸")
                            if hasattr(music_app, "_lbl_now"): music_app._lbl_now.setText("▶  REPRODUCIENDO")
                            if hasattr(music_app, "_visualizer"): music_app._visualizer.set_playing(True)
            except Exception:
                pass

    def _go_back(self):
        self.cleanup()
        self.back_requested.emit()

    def _load_current(self):
        # Detener video previo de forma limpia
        if hasattr(self, '_media_player') and self._media_player is not None:
            try:
                self._media_player.stop()
                self._media_player.setSource(QUrl())
            except Exception:
                pass

        if not self._paths:
            self._media_stack.setCurrentIndex(0)
            self._photo_label.setText("Sin imágenes")
            return

        path = self._paths[self._index]
        
        if self._album_name and self._album_name.lower() == "nosotros":
            import datetime
            ext = os.path.splitext(path)[1].lower()
            dt = None
            
            if ext not in {".mp4", ".avi", ".mkv", ".mov"}:
                try:
                    from PIL import Image
                    from PIL.ExifTags import TAGS
                    img = Image.open(path)
                    exif_data = img.getexif()
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag == "DateTimeOriginal" or tag == "DateTime":
                                # Formato EXIF típico: "YYYY:MM:DD HH:MM:SS"
                                dt = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                                break
                except Exception:
                    pass
            
            if dt is None:
                try:
                    mtime = os.path.getmtime(path)
                    ctime = os.path.getctime(path)
                    oldest_time = min(mtime, ctime)
                    dt = datetime.datetime.fromtimestamp(oldest_time)
                except Exception:
                    pass

            if dt:
                meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                display_text = f"{dt.day} de {meses[dt.month - 1]}, {dt.year}"
            else:
                display_text = "Fecha desconocida"
        else:
            display_text = os.path.basename(path)

        self._filename_label.setText(display_text)
        self._counter_label.setText(f"{self._index + 1} / {len(self._paths)}")

        self._btn_prev.setEnabled(self._index > 0)
        self._btn_next.setEnabled(self._index < len(self._paths) - 1)

        ext = os.path.splitext(path)[1].lower()
        if ext in {".mp4", ".avi", ".mov", ".mkv"}:
            self._media_stack.setCurrentIndex(1)
            self._media_player.setSource(QUrl.fromLocalFile(path))
            self._media_player.play()
            
            # Pausar la música del reproductor si está en segundo plano
            try:
                from PyQt6.QtWidgets import QApplication
                from PyQt6.QtMultimedia import QMediaPlayer
                for w in QApplication.topLevelWidgets():
                    if hasattr(w, "_open_apps") and "music" in w._open_apps:
                        music_app = w._open_apps["music"]._content_layout.itemAt(0).widget()
                        if hasattr(music_app, "_player") and music_app._player:
                            if music_app._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                                music_app._player.pause()
                                self._music_paused_by_video = True
            except Exception:
                pass
        else:
            self._resume_music_if_needed()
            
            self._media_stack.setCurrentIndex(0)
            if path not in self._cache:
                px = _load_pixmap_with_pillow(path)
                if px.isNull():
                    px = QPixmap(path)
                self._cache[path] = px

            self._display_pixmap(self._cache[path])

    def _display_pixmap(self, pixmap: QPixmap):
        if pixmap.isNull():
            self._photo_label.setText("No se pudo cargar la imagen")
            return
        available = self._photo_label.size()
        if available.width() < 10 or available.height() < 10:
            available = QSize(600, 400)
        scaled = pixmap.scaled(
            available,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._photo_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Solo actualizamos el pixmap si estamos en modo foto
        if getattr(self, '_media_stack', None) and self._media_stack.currentIndex() == 0:
            if self._paths and self._paths[self._index] in self._cache:
                self._display_pixmap(self._cache[self._paths[self._index]])
