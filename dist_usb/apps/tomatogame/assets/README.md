# Donde cambiar cada cosa

Todo lo que sigue son rutas de archivo. Reemplaza el archivo
y el juego lo usa automaticamente, sin tocar codigo.

## Texturas (assets/images/)

| Que es | Archivo |
|---|---|
| Suelo huerto | tiles/ground_huerto.png |
| Suelo cultivo | tiles/ground_cultivo.png |
| Suelo zona peligrosa | tiles/ground_peligro.png |
| Plataforma huerto | tiles/platform_huerto.png |
| Plataforma cultivo | tiles/platform_cultivo.png |
| Plataforma peligro | tiles/platform_peligro.png |
| Piso cocina | tiles/kitchen_floor.png |
| Mesada/encimera cocina | tiles/kitchen_counter.png |
| Estufa | tiles/stove.png |
| Piso arena del jefe | tiles/arena.png |
| Personaje jugador | player/player.png |
| Jefe (El Gran Chef) | bosses/chef.png |
| Proyectil del jefe | bosses/proyectil.png |
| Semilla (coleccionable) | collectibles/semilla.png |
| Fondo pantalla de inicio | ui/start_screen.png |

Enemigos, en `enemies/<nombre>.png`:
gusano, babosa, tomate_podrido, escarabajo, mosca_fruta,
pimenton, espina, cuchillo, sarten, botella_ketchup, tostadora.

Decoraciones, en `decorations/<nombre>.png`:
planta_tomate, flor, maleza, piedra, ramita, caja, cerca,
regadera, herramienta, cultivo, roca_oscura, planta_oscura,
casa, porche, puerta, maceta, plato, cubiertos, vaso,
olla_deco, estante, armario, botella_deco, utensilio_colgante,
aceite, plato_roto.

## Mensajes de la historia (a lo largo del mapa)

Se definen en `level_builder.py`, buscando `StoryMessage(x, "texto")`.
El primer numero es la posicion en el mapa (en pixeles) donde
aparece. Edita el texto ahi mismo.

## Mensajes al recoger una moneda/semilla

Lista general en `settings.py`, `COLLECTIBLE_MESSAGES`. Se elige
uno al azar por cada semilla. Si quieres un mensaje especifico
para una semilla puntual, en `level_builder.py` o `level_sections.py`
donde se crea con `Collectible(x, y, assets)`, agrega el texto:
`Collectible(x, y, assets, message="Tu mensaje aqui")`.

## Sonidos

Nombres de archivo centralizados en `settings.py`, diccionarios
`MUSIC_FILES` y `SFX_FILES`. Coloca los archivos en:

- assets/audio/music/tema_principal.ogg (musica del nivel)
- assets/audio/music/menu.ogg (musica de la pantalla de inicio)
- assets/audio/sfx/saltar.wav (al saltar)
- assets/audio/sfx/morir.wav (al perder una vida/respawnear)
- assets/audio/sfx/recoger.wav (al recoger una semilla)
- assets/audio/sfx/final.wav (al ganar)
- assets/audio/sfx/golpe_jefe.wav (al golpear al jefe)

Si un archivo no existe, el juego sigue funcionando sin ese sonido.

## Pantalla de inicio

Base en `start_screen.py`. Para poner tu propio diseno completo,
solo coloca la imagen en `assets/images/ui/start_screen.png`
(se estira al tamano del lienzo del juego). El titulo y el texto
"Presiona ENTER o ESPACIO" se dibujan encima; si quieres quitarlos
o cambiarlos, edita `start_screen.py`.

## Tamano general

`settings.py`, variable `RENDER_SCALE` (hoy en 1.5). Subela para
que todo se vea mas grande sin mover ninguna coordenada del juego.
