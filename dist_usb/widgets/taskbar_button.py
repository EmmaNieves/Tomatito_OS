"""
taskbar_button.py — Botón de aplicación en la barra de tareas.

Representa una aplicación abierta en la barra de tareas.
Al hacer clic: restaura o minimiza la ventana correspondiente.
Estado activo/inactivo refleja si la ventana tiene el foco.
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QPen, QFont

from styles.colors import TASKBAR_BG


class TaskbarButton(QPushButton):
    """Botón de la barra de tareas que representa una ventana abierta."""

    def __init__(self, label: str, emoji: str = "", parent=None):
        super().__init__(parent)
        self._label = label
        self._emoji = emoji
        self._active = False
        self._hovered = False

        display = f"{emoji} {label}" if emoji else label
        self.setText(display)
        self.setFixedHeight(30)
        self.setMinimumWidth(100)
        self.setMaximumWidth(180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Tahoma", 9))
        self._apply_style()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()

    def _apply_style(self):
        if self._active:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #98B8E0, stop:0.4 #6898C8, stop:1 #4878B0);
                    color: white;
                    border: 1px solid #1A4080;
                    border-radius: 3px;
                    padding: 0 6px;
                    font-weight: bold;
                    text-align: left;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #A8C8F0, stop:0.4 #78A8D8, stop:1 #5888C0);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4878B0, stop:1 #98B8E0);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4878D0, stop:0.5 #3060B8, stop:1 #2050A0);
                    color: white;
                    border: 1px solid #1A3070;
                    border-top: 1px solid #6090E0;
                    border-radius: 3px;
                    padding: 0 6px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #6898E0, stop:0.5 #4878C8, stop:1 #3060B0);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2050A0, stop:1 #4878D0);
                }
            """)
