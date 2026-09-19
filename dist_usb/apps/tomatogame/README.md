# Aventura de Tomate

Juego de plataformas en Python con Pygame.
Un nivel unico dividido en tres actos narrativos.

## Instalar y correr

```
pip install -r requirements.txt
python main.py
```

## Controles

Flechas o WASD para moverte.
Espacio, W o flecha arriba para saltar.
Escape para salir.

## Estructura del codigo

- `main.py` — bucle principal, une todos los sistemas.
- `settings.py` — toda la configuracion numerica y colores.
- `assets_manager.py` — carga imagenes y sonidos, con fallback si faltan.
- `audio_manager.py` — musica y efectos.
- `player.py` — logica del tomate protagonista.
- `enemy.py` — enemigos con patrulla.
- `collectible.py` — objetos recolectables.
- `platform_obj.py` — plataformas y suelo.
- `physics.py` — colisiones.
- `camera.py` — camara que sigue al jugador.
- `messages.py` — mensajes narrativos en pantalla.
- `hud.py` — contador de recuerdos y pantalla final.
- `level_sections.py` — bloques reutilizables para construir tramos.
- `level_builder.py` — arma el nivel completo, acto por acto.

## Agregar tus disenos

Coloca las imagenes en:

```
assets/images/player/
assets/images/enemies/
assets/images/tiles/
assets/images/collectibles/
```

Coloca audio en:

```
assets/audio/music/
assets/audio/sfx/
```

Luego, en `player.py`, `enemy.py`, `collectible.py` o `platform_obj.py`,
cambia el `None` de `assets.load_image(None, ...)` por la ruta real,
por ejemplo:

```
os.path.join(settings.IMAGES_DIR, "player", "tomate.png")
```

Si el archivo no existe todavia, el juego sigue funcionando
con un color solido en su lugar.

## Modificar el largo del nivel

Todo el recorrido esta en `level_builder.py`, hecho de bloques
definidos en `level_sections.py`. Para hacer una fase mas larga,
agrega mas llamadas a esos bloques o sube los valores de longitud.
Nunca se usa espacio vacio, cada bloque trae su propio contenido.

## Cambiar mensajes de la historia

Cada `StoryMessage(x, "texto")` en `level_builder.py` aparece
cuando el jugador llega a esa posicion x. Cambia el texto ahi.

## Integrar en tu otro programa

Este proyecto es independiente, sin dependencias del sistema.
Puedes lanzarlo como un proceso aparte desde tu programa principal,
por ejemplo con `subprocess.Popen(["python", "main.py"], cwd="tomate_game")`.
