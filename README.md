# Tomatito 🍅

Aplicación de escritorio que simula un pequeño sistema operativo inspirado en Windows XP.

## Estructura del proyecto

```
tomatito/
├── main.py                    ← Punto de entrada
├── build.spec                 ← Configuración PyInstaller
├── requirements.txt
│
├── core/                      ← Sistema operativo virtual
│   ├── desktop.py             ← Escritorio principal
│   ├── taskbar.py             ← Barra de tareas
│   ├── start_menu.py          ← Menú Inicio
│   ├── window_manager.py      ← Gestor de ventanas
│   ├── sound_manager.py       ← Sistema de audio
│   ├── resource_manager.py    ← Carga de recursos
│   └── app_registry.py        ← Registro de aplicaciones
│
├── widgets/                   ← Componentes visuales reutilizables
│   ├── window_frame.py        ← Marco de ventana XP
│   ├── desktop_icon.py        ← Iconos del escritorio
│   └── taskbar_button.py      ← Botones de la barra de tareas
│
├── apps/                      ← Aplicaciones del sistema
│   ├── base_app.py            ← Clase base
│   └── gallery/               ← Galería de fotos (Fase 1)
│       ├── gallery_app.py
│       ├── album_view.py
│       └── photo_viewer.py
│
├── styles/                    ← Tema visual XP
│   ├── colors.py
│   └── xp_theme.py
│
├── tools/                     ← Scripts de desarrollo
│   ├── generate_wallpaper.py
│   └── build_exe.py
│
└── assets/                    ← Recursos externos (NO dentro del .exe)
    ├── photos/
    │   ├── amigos/            ← Copia aquí tus fotos
    │   ├── familia/
    │   └── nosotros/
    ├── sounds/                ← .wav/.mp3 opcionales
    ├── icons/                 ← Iconos opcionales
    └── wallpaper/             ← default.jpg (se genera automáticamente)
```

---

## Instalación y ejecución en desarrollo

### 1. Requisitos previos

Instalar Python 3.11+ desde https://www.python.org/downloads/

> **Importante**: Marcar la opción "Add Python to PATH" durante la instalación.

### 2. Instalar dependencias

```cmd
cd tomatito
python -m pip install -r requirements.txt
```

### 3. Generar el wallpaper (solo la primera vez)

```cmd
python tools/generate_wallpaper.py
```

### 4. Ejecutar en modo desarrollo

```cmd
python main.py
```

> Presiona `Escape` o usa Alt+F4 del sistema real para salir (en desarrollo).

---

## Añadir fotografías

Simplemente copia las imágenes a la carpeta del álbum correspondiente:

```
assets/photos/amigos/     → Fotos de amigos
assets/photos/familia/    → Fotos de familia
assets/photos/nosotros/   → Fotos de nosotros
```

Formatos admitidos: **JPG, JPEG, PNG, WEBP**

No es necesario modificar el código ni recompilar.

---

## Generar el ejecutable (.exe)

```cmd
python -m pip install pyinstaller
python tools/build_exe.py
```

El ejecutable se generará en `dist/Tomatito/`. Para distribuir, copia **toda la carpeta**:

```
dist/Tomatito/
├── Tomatito.exe
├── assets/
│   ├── photos/
│   ├── sounds/
│   └── wallpaper/
└── (dependencias del sistema)
```

---

## Añadir una nueva aplicación (Fase 2+)

1. Crear `apps/nueva_app/nueva_app.py` con una clase que herede de `BaseApp`
2. En `main.py`, dentro de `_register_apps()`, añadir:

```python
from apps.nueva_app.nueva_app import NuevaApp
registry.register(AppDefinition(
    app_id="nueva_app",
    name="Mi Nueva App",
    icon_key="nueva_app_icon",
    emoji="🎵",
    app_class=NuevaApp,
    desktop_icon=True,
    start_menu=True,
    description="Descripción corta",
))
```

---

## Sonidos

Coloca archivos de audio en `assets/sounds/` con los nombres:

| Archivo           | Evento                    |
|-------------------|---------------------------|
| `startup.wav`     | Al iniciar Tomatito        |
| `click.wav`       | Clic en botones           |
| `window_open.wav` | Al abrir una ventana      |
| `window_close.wav`| Al cerrar una ventana     |
| `error.wav`       | Errores del sistema       |

Si no existe el archivo, el sistema continúa sin sonido (no hay error).

---

## Atajos de teclado (en el visor de fotos)

| Tecla   | Acción             |
|---------|--------------------|
| `←`     | Foto anterior      |
| `→`     | Foto siguiente     |
