"""
resource_manager.py — Gestor de rutas y recursos externos.

Responsabilidades:
- Resolver rutas relativas a assets/ en tiempo de ejecución.
- Compatible con entorno de desarrollo (Python directo) y empaquetado (PyInstaller).
- Proveer métodos de acceso a fotos, sonidos, iconos y wallpaper.
- Detectar automáticamente imágenes en álbumes sin lista hardcodeada.
"""

import os
import sys


# Extensiones admitidas
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
SUPPORTED_MEDIA_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS


def _get_base_dir() -> str:
    """
    Devuelve el directorio base de la aplicación.
    - En desarrollo: directorio donde está este archivo (src/).
    - Empaquetado con PyInstaller (--onedir): directorio del ejecutable.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller: el exe está en la misma carpeta que assets/
        return os.path.dirname(sys.executable)
    else:
        # Desarrollo: subir desde core/ hasta la raíz del proyecto
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ResourceManager:
    """
    Punto único de acceso a todos los recursos externos de Tomatito.
    Instanciar una vez y pasar la referencia a quien la necesite.
    """

    def __init__(self):
        self._base = _get_base_dir()
        self._assets = os.path.join(self._base, "assets")

    # ── Rutas base ──────────────────────────────────────────────────────

    def assets_path(self, *parts: str) -> str:
        """Construye una ruta dentro de assets/."""
        return os.path.join(self._assets, *parts)

    # ── Wallpaper ────────────────────────────────────────────────────────

    def get_wallpaper(self) -> str | None:
        """
        Devuelve la ruta del wallpaper activo.
        Busca 'wallpaper/default.*' con cualquier extensión de imagen.
        Devuelve None si no existe ninguno.
        """
        wp_dir = self.assets_path("wallpaper")
        if not os.path.isdir(wp_dir):
            return None
        for fname in os.listdir(wp_dir):
            ext = os.path.splitext(fname)[1].lower()
            if ext in SUPPORTED_IMAGE_EXTENSIONS and fname.startswith("default"):
                return os.path.join(wp_dir, fname)
        return None

    # ── Iconos ────────────────────────────────────────────────────────────

    def get_icon_path(self, name: str) -> str | None:
        """
        Devuelve la ruta de un icono por nombre (sin extensión).
        Busca en assets/icons/ con cualquier extensión de imagen.
        """
        icons_dir = self.assets_path("icons")
        if not os.path.isdir(icons_dir):
            return None
        for fname in os.listdir(icons_dir):
            stem, ext = os.path.splitext(fname)
            if stem == name and ext.lower() in SUPPORTED_IMAGE_EXTENSIONS | {".svg", ".ico"}:
                return os.path.join(icons_dir, fname)
        return None

    # ── Sonidos ───────────────────────────────────────────────────────────

    def get_sound_path(self, name: str) -> str | None:
        """
        Devuelve la ruta de un sonido por nombre (sin extensión).
        Busca .wav, .mp3, .ogg en assets/sounds/.
        Devuelve None si no existe (el SoundManager fallará silenciosamente).
        """
        sounds_dir = self.assets_path("sounds")
        if not os.path.isdir(sounds_dir):
            return None
        audio_exts = {".wav", ".mp3", ".ogg", ".m4a", ".aac", ".flac"}
        for fname in os.listdir(sounds_dir):
            stem, ext = os.path.splitext(fname)
            if stem == name and ext.lower() in audio_exts:
                return os.path.join(sounds_dir, fname)
        return None

    # ── Galería de fotos ──────────────────────────────────────────────────

    def get_photo_albums(self) -> list[dict]:
        """
        Devuelve la lista de álbumes disponibles.
        Cada álbum es un dict con claves:
          - 'id':    nombre de la carpeta (clave interna)
          - 'name':  nombre para mostrar (capitalizado)
          - 'path':  ruta absoluta a la carpeta
          - 'cover': ruta de la primera imagen (para miniatura), o None
        """
        photos_dir = self.assets_path("photos")
        albums: list[dict] = []

        if not os.path.isdir(photos_dir):
            return albums

        for entry in sorted(os.scandir(photos_dir), key=lambda e: e.name):
            if not entry.is_dir():
                continue
            photos = self._scan_images(entry.path)
            albums.append(
                {
                    "id": entry.name,
                    "name": entry.name.capitalize(),
                    "path": entry.path,
                    "cover": photos[0] if photos else None,
                }
            )
        return albums

    @staticmethod
    def _get_media_date(path: str) -> float:
        import os
        ext = os.path.splitext(path)[1].lower()
        if ext not in {".mp4", ".avi", ".mkv", ".mov"}:
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                import datetime
                img = Image.open(path)
                exif_data = img.getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag in ("DateTimeOriginal", "DateTime"):
                            dt = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                            return dt.timestamp()
            except Exception:
                pass
        try:
            return min(os.path.getmtime(path), os.path.getctime(path))
        except Exception:
            return 0.0

    def get_photos_in_album(self, album_path: str) -> list[str]:
        """
        Devuelve las rutas de todas las imágenes en un álbum.
        """
        paths = self._scan_images(album_path)
        return paths

    # ── Helpers internos ──────────────────────────────────────────────────

    @staticmethod
    def _scan_images(directory: str) -> list[str]:
        """Escanea un directorio y devuelve rutas de archivos multimedia soportados."""
        if not os.path.isdir(directory):
            return []
        results = []
        for root, _, files in os.walk(directory):
            for fname in sorted(files):
                ext = os.path.splitext(fname)[1].lower()
                if ext in SUPPORTED_MEDIA_EXTENSIONS:
                    results.append(os.path.join(root, fname))
        return results
