# -*- mode: python ; coding: utf-8 -*-
"""
build.spec — Configuración de PyInstaller para Tomatito.exe

Para generar el ejecutable:
    pip install pyinstaller
    pyinstaller build.spec

El resultado estará en dist/Tomatito/
Copiar assets/ a dist/Tomatito/assets/ antes de distribuir.

NOTA: Se usa --onedir (no --onefile) para que assets/ sea accesible
junto al ejecutable. Esto es intencional: permite modificar fotos y
recursos sin recompilar.
"""

import sys
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Estilos del SO
        ('styles', 'styles'),
        # Archivos Python del juego (se copian como datos para el subprocess)
        ('apps/tomatogame/*.py', 'apps/tomatogame'),
        # Assets del juego (imagenes, audio, etc.)
        ('apps/tomatogame/assets', 'apps/tomatogame/assets'),
    ],
    hiddenimports=[
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageFile',
        'PIL.JpegImagePlugin',
        'PIL.PngImagePlugin',
        'PIL.WebPImagePlugin',
        'pygame',
        'pygame.mixer',
        'pygame.image',
        'pygame.font',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Tomatito',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,         # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icons/tomatito.ico',  # Descomentar cuando tengas un .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Tomatito',
)
