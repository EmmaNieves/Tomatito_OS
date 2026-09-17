"""
xp_theme.qss — Hoja de estilos Qt que recrea la estética Windows XP Luna.
Se carga en main.py y se aplica globalmente a la aplicación.
"""

QSS_THEME = """
/* ─── Fuente base ─── */
* {
    font-family: "Tahoma", "Segoe UI", sans-serif;
    font-size: 11px;
}

/* ─── Scrollbars ─── */
QScrollBar:vertical {
    background: #F0EFE7;
    width: 16px;
    border: 1px solid #ACA899;
}
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #D8D5CC, stop:0.4 #EFEDEA, stop:1 #C8C5BC);
    border: 1px solid #ACA899;
    min-height: 20px;
    border-radius: 2px;
}
QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #B8CFEF, stop:0.4 #D0E4FF, stop:1 #A8BFDF);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: #D4D0C8;
    border: 1px solid #ACA899;
    height: 16px;
    subcontrol-origin: margin;
}
QScrollBar::add-line:vertical { subcontrol-position: bottom; }
QScrollBar::sub-line:vertical { subcontrol-position: top; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: #F0EFE7;
}

QScrollBar:horizontal {
    background: #F0EFE7;
    height: 16px;
    border: 1px solid #ACA899;
}
QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #D8D5CC, stop:0.4 #EFEDEA, stop:1 #C8C5BC);
    border: 1px solid #ACA899;
    min-width: 20px;
    border-radius: 2px;
}

/* ─── Tooltips ─── */
QToolTip {
    background-color: #FFFFE1;
    color: #000000;
    border: 1px solid #000000;
    padding: 2px 4px;
    font-size: 11px;
}

/* ─── QMessageBox ─── */
QMessageBox {
    background-color: #ECE9D8;
}
QMessageBox QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF, stop:1 #D4D0C8);
    border: 1px solid #7F9DB9;
    border-radius: 3px;
    padding: 3px 12px;
    min-width: 60px;
}
QMessageBox QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #EEF3FF, stop:1 #C0D4F0);
    border: 1px solid #316AC5;
}
QMessageBox QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #C0C8E0, stop:1 #E8ECF8);
}
"""
