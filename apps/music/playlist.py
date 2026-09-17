"""
playlist.py — Lista de canciones del reproductor.

Para agregar o modificar canciones, edita únicamente esta lista.
Cada canción es un diccionario con cuatro campos:

    title  → Nombre de la canción (string)
    artist → Nombre del artista   (string)
    cover  → Ruta relativa a la portada dentro de apps/music/assets/
             Ejemplo: "covers/mi_portada.jpg"
             Deja "" si no hay portada (se mostrará un placeholder).
    file   → Ruta relativa al audio dentro de apps/music/assets/
             Ejemplo: "songs/mi_cancion.mp3"

Formatos de audio soportados: mp3, wav, ogg, flac, m4a.
"""

SONGS = [
    {
        "title":  "Canción de ejemplo 1",
        "artist": "Artista Uno",
        "cover":  "covers/cover1.jpg",
        "file":   "songs/song1.mp3",
    },
    {
        "title":  "Canción de ejemplo 2",
        "artist": "Artista Dos",
        "cover":  "covers/cover2.jpg",
        "file":   "songs/song2.mp3",
    },
    {
        "title":  "Canción de ejemplo 3",
        "artist": "Artista Tres",
        "cover":  "",
        "file":   "songs/song3.mp3",
    },
]
