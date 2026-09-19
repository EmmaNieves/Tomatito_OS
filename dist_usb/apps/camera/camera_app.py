"""
camera_app.py — Aplicación de cámara estilo Cyber-shot 2000s con edición Y2K.
"""

import os
import random
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedLayout, QScrollArea, QGridLayout,
    QLineEdit, QColorDialog, QInputDialog, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QPainter, QPen, QImage, QMouseEvent
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
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #383838, stop:1 #1c1c1c);
    border-top: 2px solid #505050;
}
QPushButton.action_btn {
    background: qradialgradient(cx:0.5, cy:0.4, radius:0.7, fx:0.5, fy:0.2, stop:0 #ffffff, stop:0.5 #d8d8d8, stop:1 #888888);
    color: #111111;
    border: 2px solid #ffffff;
    border-radius: 20px;
    font-weight: bold;
    font-size: 13px;
    font-family: "Segoe UI", sans-serif;
    padding: 6px 24px;
}
QPushButton.action_btn:hover {
    background: qradialgradient(cx:0.5, cy:0.4, radius:0.7, fx:0.5, fy:0.2, stop:0 #ffffff, stop:0.5 #f0f0f0, stop:1 #aaaaaa);
    border-color: #ffaa00;
}
QPushButton.action_btn:pressed {
    background: #777777;
}
QPushButton.filter_btn {
    background: #2e2e2e;
    color: #ffffff;
    border: 2px solid #444444;
    border-radius: 8px;
    padding: 6px;
    font-size: 10px;
    font-weight: bold;
}
QPushButton.filter_btn:hover {
    border-color: #ffaa00;
    background: #3e3e3e;
}
QPushButton.tool_btn {
    background: #111111;
    color: #00ff78;
    border: 2px solid #00ff78;
    border-radius: 12px;
    padding: 6px;
    font-size: 12px;
}
QPushButton.tool_btn:hover {
    background: #00ff78;
    color: #111111;
}
QColorDialog { background-color: #f0f0f0; color: #000000; }
QColorDialog QLabel { color: #000000; }
QLabel#osd_text {
    color: #ffcc00;
    font-size: 11px;
    font-weight: bold;
    background: transparent;
}
"""

class DraggableLabel(QLabel):
    def __init__(self, text=None, pixmap=None, is_frame=False, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.is_frame = is_frame
        if pixmap:
            if is_frame and parent:
                self.setPixmap(pixmap.scaled(parent.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.setPixmap(pixmap)
            self.setStyleSheet("background: transparent;")
        else:
            self.setText(text)
            if len(text) < 5:
                self.setFont(QFont("Segoe UI Emoji", 32))
            else:
                self.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
            self.setStyleSheet("background: transparent; color: white; padding: 4px;")
            
        self.adjustSize()
        if text and not pixmap:
            self.resize(self.width() + 24, self.height() + 8)
        self._dragging = False
        self._drag_start_pos = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and not self.is_frame:
            self._dragging = True
            self._drag_start_pos = event.position().toPoint()
            self.raise_()
        elif event.button() == Qt.MouseButton.RightButton:
            self.deleteLater()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging and not self.is_frame:
            self.move(self.pos() + event.position().toPoint() - self._drag_start_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

class OSDOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.show_flash = False
        self.flash_timer = QTimer(self)
        self.flash_timer.setInterval(70)
        self.flash_timer.timeout.connect(self._end_flash)

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

        painter.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 220, 0))
        painter.drawText(14, 24, "📷 3.2 MP")
        painter.setPen(QColor(0, 255, 120))
        painter.drawText(w - 90, 24, "🔋 [III]")
        painter.end()

def apply_filter(img: QImage, filter_name: str) -> QImage:
    res = img.copy()
    if filter_name == "Normal":
        return res
    if filter_name == "B & N":
        return res.convertToFormat(QImage.Format.Format_Grayscale8).convertToFormat(QImage.Format.Format_ARGB32)
    
    res = res.convertToFormat(QImage.Format.Format_ARGB32)
    
    if filter_name in ["Sepia", "Old JPEG", "VHS"]:
        if filter_name == "Sepia":
            res = res.convertToFormat(QImage.Format.Format_Grayscale8).convertToFormat(QImage.Format.Format_ARGB32)
            
    if filter_name in ["Píxeles", "8-Bit", "Old JPEG"]:
        w, h = res.width(), res.height()
        factor = 8 if filter_name == "Píxeles" else (4 if filter_name == "Old JPEG" else 6)
        small = res.scaled(max(1, w // factor), max(1, h // factor), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
        res = small.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)

    if filter_name in ["Dreamy", "Soft Focus", "VHS", "Angel"]:
        w, h = res.width(), res.height()
        small = res.scaled(max(1, w // 4), max(1, h // 4), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        res = small.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)

    painter = QPainter(res)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
    
    if filter_name == "Sepia":
        painter.fillRect(res.rect(), QColor(112, 66, 20, 80))
    elif filter_name == "Frío":
        painter.fillRect(res.rect(), QColor(0, 100, 255, 60))
    elif filter_name == "Cálido":
        painter.fillRect(res.rect(), QColor(255, 150, 0, 50))
    elif filter_name == "Rosado" or filter_name == "Soft Girl":
        painter.fillRect(res.rect(), QColor(255, 50, 150, 60))
    elif filter_name == "MySpace":
        painter.fillRect(res.rect(), QColor(0, 50, 200, 40))
    elif filter_name == "Night MSN":
        painter.fillRect(res.rect(), QColor(0, 0, 50, 100))
    elif filter_name == "Flash":
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
        painter.fillRect(res.rect(), QColor(255, 255, 255, 80))
    elif filter_name == "Dreamy":
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
        painter.fillRect(res.rect(), QColor(255, 200, 255, 40))
    elif filter_name == "Emo":
        painter.fillRect(res.rect(), QColor(0, 0, 0, 80))
    elif filter_name == "Old JPEG":
        painter.fillRect(res.rect(), QColor(200, 150, 50, 40))
        
    painter.end()
    return res

class PreviewEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_pixmap = QPixmap()
        self.current_filter = "Normal"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        center = QWidget()
        center_layout = QHBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setStyleSheet("QScrollArea { border: none; background: #000; }")
        
        self.canvas_container = QFrame()
        self.canvas_container.setObjectName("viewfinder_box")
        c_layout = QVBoxLayout(self.canvas_container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        
        self.canvas = QLabel()
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setStyleSheet("background: transparent;")
        c_layout.addWidget(self.canvas, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.canvas_scroll.setWidget(self.canvas_container)
        center_layout.addWidget(self.canvas_scroll, 1)

        # Panel derecho: Herramientas (ahora con pestañas)
        tools = QFrame()
        tools.setFixedWidth(180)
        tools.setStyleSheet("background: #1c1c1c; border-left: 2px solid #505050;")
        t_layout = QVBoxLayout(tools)
        
        self.tool_stack = QStackedWidget()
        
        # Pagina 1: Filtros
        p_filtros = QWidget()
        pf_layout = QVBoxLayout(p_filtros)
        pf_layout.setContentsMargins(0,0,0,0)
        grid_f = QGridLayout()
        grid_f.setSpacing(4)
        filters = ["Normal", "B & N", "Sepia", "Frío", "Cálido", "Rosado", "Píxeles", "MySpace", "Dreamy", "Night MSN", "Flash", "Old JPEG", "Emo"]
        for i, fname in enumerate(filters):
            btn = QPushButton(fname)
            btn.setProperty("class", "filter_btn")
            btn.clicked.connect(lambda checked, f=fname: self.set_filter(f))
            grid_f.addWidget(btn, i//2, i%2)
        pf_layout.addLayout(grid_f)
        pf_layout.addStretch()
        self.tool_stack.addWidget(p_filtros)
        
        # Pagina 2: Stickers/Marcos
        p_stickers = QWidget()
        ps_layout = QVBoxLayout(p_stickers)
        ps_layout.setContentsMargins(0,0,0,0)
        btn_txt = QPushButton("📝 Agregar Texto")
        btn_txt.setProperty("class", "tool_btn")
        btn_txt.clicked.connect(self.add_text)
        ps_layout.addWidget(btn_txt)
        
        grid_e = QGridLayout()
        emojis = ['❤️', '🎉', '⭐', '🍅', '🥳', '✨', '💀', '🔥']
        for i, emj in enumerate(emojis):
            btn = QPushButton(emj)
            btn.setProperty("class", "tool_btn")
            btn.clicked.connect(lambda checked, e=emj: self.add_emoji(e))
            grid_e.addWidget(btn, i//4, i%4)
        ps_layout.addLayout(grid_e)
        
        ps_layout.addSpacing(10)
        lbl_st = QLabel("Stickers & Marcos")
        lbl_st.setStyleSheet("color: #ffaa00; font-size: 10px; font-weight: bold;")
        ps_layout.addWidget(lbl_st)
        
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sw = QWidget()
        sw_layout = QGridLayout(sw)
        
        # Cargar stickers
        base_dir = "assets/camera_assets"
        row = 0
        col = 0
        if os.path.exists(base_dir):
            for cat in ["stickers", "frames", "overlays"]:
                cat_dir = os.path.join(base_dir, cat)
                if os.path.exists(cat_dir):
                    for f in os.listdir(cat_dir):
                        if f.endswith(".png"):
                            path = os.path.join(cat_dir, f)
                            btn = QPushButton()
                            btn.setFixedSize(50, 50)
                            btn.setStyleSheet("background: #2e2e2e; border: 1px solid #444;")
                            px = QPixmap(path).scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            from PyQt6.QtGui import QIcon
                            btn.setIcon(QIcon(px))
                            btn.setIconSize(QSize(40, 40))
                            btn.clicked.connect(lambda checked, p=path, is_f=(cat=="frames"): self.add_image_sticker(p, is_f))
                            sw_layout.addWidget(btn, row, col)
                            col += 1
                            if col > 2:
                                col = 0
                                row += 1
                                
        sa.setWidget(sw)
        ps_layout.addWidget(sa, 1)
        self.tool_stack.addWidget(p_stickers)
        
        # Pestañas
        tab_layout = QHBoxLayout()
        btn_tab1 = QPushButton("Filtros")
        btn_tab2 = QPushButton("Decorar")
        btn_tab1.setStyleSheet("background: #333; color: white; border: 1px solid #555;")
        btn_tab2.setStyleSheet("background: #333; color: white; border: 1px solid #555;")
        btn_tab1.clicked.connect(lambda: self.tool_stack.setCurrentIndex(0))
        btn_tab2.clicked.connect(lambda: self.tool_stack.setCurrentIndex(1))
        tab_layout.addWidget(btn_tab1)
        tab_layout.addWidget(btn_tab2)
        
        t_layout.addLayout(tab_layout)
        t_layout.addWidget(self.tool_stack, 1)
        
        lbl_hint = QLabel("Click derecho\npara borrar item")
        lbl_hint.setStyleSheet("color: #777777; font-size: 9px;")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t_layout.addWidget(lbl_hint)

        center_layout.addWidget(tools)
        layout.addWidget(center, 1)

        ctrl = QFrame()
        ctrl.setObjectName("control_bar")
        ctrl.setFixedHeight(64)
        h = QHBoxLayout(ctrl)
        h.setContentsMargins(16, 8, 16, 8)
        
        self.btn_cancel = QPushButton("✖ REINTENTAR")
        self.btn_cancel.setProperty("class", "action_btn")
        h.addWidget(self.btn_cancel)
        h.addStretch()
        
        self.btn_save = QPushButton("💾 GUARDAR")
        self.btn_save.setProperty("class", "action_btn")
        self.btn_save.setStyleSheet(self.btn_save.styleSheet() + " color: #004400;")
        h.addWidget(self.btn_save)

        layout.addWidget(ctrl)

    def load_image(self, pixmap: QPixmap):
        if pixmap.width() > 800 or pixmap.height() > 600:
            self.original_pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        elif pixmap.width() < 100:
            self.original_pixmap = pixmap.scaled(640, 480, Qt.AspectRatioMode.IgnoreAspectRatio)
        else:
            self.original_pixmap = pixmap
            
        self.current_filter = "Normal"
        
        for child in self.canvas.children():
            if isinstance(child, DraggableLabel):
                child.deleteLater()
                
        self.canvas.setFixedSize(self.original_pixmap.size())
        self._update_preview()

    def set_filter(self, filter_name: str):
        self.current_filter = filter_name
        self._update_preview()

    def _update_preview(self):
        if self.original_pixmap.isNull(): return
        img = self.original_pixmap.toImage()
        img = apply_filter(img, self.current_filter)
        self.canvas.setPixmap(QPixmap.fromImage(img))

    def add_text(self):
        input_dialog = QInputDialog(self)
        input_dialog.setWindowTitle("Agregar Texto")
        input_dialog.setLabelText("Escribe tu mensaje:")
        input_dialog.setStyleSheet("""
            QInputDialog { background-color: #ECE9D8; color: #000000; }
            QLabel { color: #000000 !important; font-family: "Segoe UI", sans-serif; font-size: 13px; font-weight: bold; }
            QLineEdit { background-color: #ffffff; color: #000000 !important; border: 1px solid #7f9db9; padding: 4px; font-size: 14px; }
            QPushButton { background-color: #0A5FC4; color: #ffffff !important; border: 1px solid #003399; border-radius: 4px; padding: 4px 14px; font-weight: bold; }
            QPushButton:hover { background-color: #1E6FE0; }
        """)
        if input_dialog.exec():
            text = input_dialog.textValue().strip()
            if text:
                color_dialog = QColorDialog(Qt.GlobalColor.white, self)
                color_dialog.setWindowTitle("Color del Texto")
                color_dialog.setStyleSheet("""
                    QColorDialog { background-color: #ECE9D8; color: #000000; }
                    QLabel, QGroupBox { color: #000000 !important; font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: bold; background: transparent; }
                    QPushButton { background-color: #0A5FC4; color: #ffffff !important; border: 1px solid #003399; border-radius: 4px; padding: 4px 12px; font-weight: bold; }
                    QPushButton:hover { background-color: #1E6FE0; }
                    QLineEdit, QSpinBox { background-color: #ffffff; color: #000000 !important; border: 1px solid #7f9db9; padding: 2px; }
                """)
                if color_dialog.exec():
                    color = color_dialog.selectedColor()
                    if color.isValid():
                        lbl = DraggableLabel(text=text, parent=self.canvas)
                        lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
                        lbl.setStyleSheet(f"background: transparent; color: {color.name()}; padding: 4px;")
                        lbl.adjustSize()
                        lbl.resize(lbl.width() + 24, lbl.height() + 8)
                        lbl.move(self.canvas.width() // 2 - lbl.width() // 2, self.canvas.height() // 2)
                        lbl.show()

    def add_emoji(self, emoji_char: str):
        lbl = DraggableLabel(text=emoji_char, parent=self.canvas)
        lbl.move(self.canvas.width() // 2 - 20, self.canvas.height() // 2 - 20)
        lbl.show()

    def add_image_sticker(self, path: str, is_frame: bool):
        px = QPixmap(path)
        if not px.isNull():
            if not is_frame:
                px = px.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl = DraggableLabel(pixmap=px, is_frame=is_frame, parent=self.canvas)
            if not is_frame:
                lbl.move(self.canvas.width() // 2 - px.width() // 2, self.canvas.height() // 2 - px.height() // 2)
            else:
                lbl.move(0, 0)
                lbl.lower() # Marco debe estar atras de los textos? O adelante?
            lbl.show()

    def get_final_image(self) -> QPixmap:
        res = self.canvas.grab()
        img = res.toImage()
        res = QPixmap.fromImage(img)
        painter = QPainter(res)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = res.width(), res.height()
        font_size = max(12, int(h * 0.045))
        painter.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))

        now = datetime.now()
        date_str = now.strftime("'%y %m %d")
        time_str = now.strftime("%H:%M")
        stamp_text = f"{date_str}  {time_str}"

        tx = int(w * 0.62)
        ty = int(h * 0.92)

        painter.setPen(QColor(0, 0, 0, 240))
        painter.drawText(tx + 2, ty + 2, stamp_text)
        painter.setPen(QColor(255, 140, 0))
        painter.drawText(tx, ty, stamp_text)
        painter.end()
        
        return res

class CameraApp(BaseApp):
    def __init__(self, resources: ResourceManager, sounds: SoundManager, parent=None):
        self._camera: QCamera | None = None
        self._session: QMediaCaptureSession | None = None
        self._image_capture: QImageCapture | None = None
        super().__init__(resources, sounds, parent)
        self._start_camera()

    def _build_ui(self) -> None:
        self.setObjectName("camera_root")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(_CYBER_QSS)

        self.main_stack = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.main_stack)

        page_capture = QWidget()
        c_layout = QVBoxLayout(page_capture)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)

        view_box = QFrame()
        view_box.setObjectName("viewfinder_box")

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

        c_layout.addWidget(view_box, stretch=1)

        ctrl = QFrame()
        ctrl.setObjectName("control_bar")
        ctrl.setFixedHeight(64)
        h = QHBoxLayout(ctrl)
        h.setContentsMargins(16, 8, 16, 8)

        lbl_status = QLabel("FLASH: AUTO")
        lbl_status.setObjectName("osd_text")
        h.addWidget(lbl_status)
        h.addStretch()

        self._btn_shutter = QPushButton("📷  TOMAR FOTO")
        self._btn_shutter.setProperty("class", "action_btn")
        self._btn_shutter.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_shutter.clicked.connect(self._take_photo)
        h.addWidget(self._btn_shutter)

        h.addStretch()
        lbl_mem = QLabel("MEMORIA: OK")
        lbl_mem.setObjectName("osd_text")
        h.addWidget(lbl_mem)

        c_layout.addWidget(ctrl)
        self.main_stack.addWidget(page_capture)

        self.editor = PreviewEditor()
        self.editor.btn_cancel.clicked.connect(self._cancel_edit)
        self.editor.btn_save.clicked.connect(self._save_edit)
        self.main_stack.addWidget(self.editor)

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
        self._show_editor(px)

    def _capture_fallback(self) -> None:
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
        self._show_editor(px)

    def _show_editor(self, pixmap: QPixmap):
        self.editor.load_image(pixmap)
        self.main_stack.setCurrentIndex(1)
        if hasattr(self, "_camera") and self._camera:
            self._camera.stop()

    def _cancel_edit(self):
        if self.sounds:
            self.sounds.play_click()
        if hasattr(self, "_camera") and self._camera:
            self._camera.start()
        self.main_stack.setCurrentIndex(0)

    def _save_edit(self):
        if self.sounds:
            self.sounds.play_click()
            
        final_px = self.editor.get_final_image()
        
        photos_dir = self.resources.assets_path("photos", "Camara")
        os.makedirs(photos_dir, exist_ok=True)
        filename = f"PHOTO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        save_path = os.path.join(photos_dir, filename)
        final_px.save(save_path, "JPEG", 92)
        
        if hasattr(self, "_camera") and self._camera:
            self._camera.start()
        self.main_stack.setCurrentIndex(0)

    def closeEvent(self, event) -> None:
        try:
            if hasattr(self, "_camera") and self._camera:
                self._camera.stop()
                self._camera = None
            if hasattr(self, "_session") and self._session:
                self._session = None
            if hasattr(self, "_osd_overlay") and self._osd_overlay:
                if hasattr(self._osd_overlay, "flash_timer") and self._osd_overlay.flash_timer:
                    self._osd_overlay.flash_timer.stop()
        except Exception:
            pass
        super().closeEvent(event)
