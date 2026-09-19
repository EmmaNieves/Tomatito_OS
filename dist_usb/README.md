# tomatitOS 🍅

**tomatitOS** es un sistema operativo virtual interactivo con estética nostálgica Windows XP / años 2000, diseñado como una experiencia multimedia y regalo interactivo.

---

## 🚀 Aplicaciones Incluidas

- **📁 Mis imágenes (Galería):** Visor de fotografías y recuerdos con soporte para fotos, videos y perfiles de amigos.
- **🎵 Reproductor:** Reproductor de música retro con playlist personalizada, código QR para escanear y escuchar en el celular, visualizador de audio, soporte de letras y reproducción continua sin interrupciones.
- **📷 Cámara:** Simulador de cámara digital Cyber-shot 2000s con flash en pantalla, filtros vintage (Sepia, B&N, Píxeles, etc.), marcos, stickers y herramienta de dibujo/edición.
- **🍅 TOMÁte Salvajes:** Videojuego de aventuras y plataformas en Pygame con adaptación de pantalla panorámica.
- **🎉 Celebración de Cumpleaños:** Secuencia festiva con efectos de confeti, fuegos artificiales, ventana clásica XP, música y personajes animados.

---

## 💾 Versión Portable / USB (dist_usb/)

La versión lista para copiar a una memoria USB y ejecutar directamente sin instalar nada se encuentra en la carpeta **dist_usb/**.

### Cómo usar en una memoria USB:
1. Copia la carpeta dist_usb/ (o todo su contenido) a tu memoria USB (D:, E:, etc.).
2. Abre la carpeta y ejecuta **Iniciar.bat** (o **Iniciar.vbs** para inicio silencioso).
3. **100% Autónomo y Portable:** Contiene un entorno Python 3.11 embebido y todas las dependencias preinstaladas (PyQt6, Pygame, Pillow). No requiere tener Python instalado en la computadora destino ni conexión a internet.

---

## 💻 Ejecución en Modo Desarrollo

### Requisitos:
- Python 3.11 o superior.
- Instalar dependencias:
  `cmd
  pip install -r requirements.txt
  `

### Iniciar:
`cmd
python main.py
`

---

## 🛠️ Estructura del Proyecto

`
tomatito_so/
├── main.py              # Punto de entrada del sistema
├── requirements.txt     # Dependencias de Python (PyQt6, pygame, Pillow)
├── build.spec           # Especificación PyInstaller
├── core/                # Núcleo del SO (desktop, taskbar, sound, resources, window manager)
├── apps/                # Módulos de aplicaciones (gallery, music, camera, tomatogame)
├── widgets/             # Componentes UI (marcos de ventana XP, iconos, celebración)
├── styles/              # Paleta y temas QSS de Windows XP
├── assets/              # Recursos multimedia (imágenes, sonidos, iconos, wallpaper)
└── dist_usb/            # Distribución portable autónoma lista para USB
`
