"""
Script auxiliar para generar el wallpaper genérico de Tomatito.
Ejecutar una sola vez después de instalar Pillow:
    python tools/generate_wallpaper.py
"""

import os
from PIL import Image, ImageDraw, ImageFilter

def generate_wallpaper(output_path: str, width: int = 1920, height: int = 1080):
    """Genera un fondo de pantalla con degradado verde-azul estilo XP."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Degradado vertical: verde XP → azul XP
    for y in range(height):
        t = y / height
        r = int(26  + (43  - 26)  * t)
        g = int(110 + (127 - 110) * t)
        b = int(60  + (191 - 60)  * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Añadir suavizado
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    img.save(output_path, "JPEG", quality=95)
    print(f"Wallpaper generado: {output_path}")

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out  = os.path.join(base, "assets", "wallpaper", "default.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    generate_wallpaper(out)
