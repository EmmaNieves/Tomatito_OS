import os

# ------------------------------------------------------------
# RUTAS. Todo relativo, funciona en cualquier maquina.
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

# ------------------------------------------------------------
# VENTANA
# El juego dibuja todo en un lienzo logico de SCREEN_WIDTH x
# SCREEN_HEIGHT (aqui abajo). RENDER_SCALE agranda ese lienzo
# en la ventana real, sin tocar ninguna coordenada del juego.
# Sube RENDER_SCALE si todo se ve muy chico.
# ------------------------------------------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
RENDER_SCALE = 1.5
WINDOW_WIDTH = int(SCREEN_WIDTH * RENDER_SCALE)
WINDOW_HEIGHT = int(SCREEN_HEIGHT * RENDER_SCALE)
FPS = 40
TITLE = "TOMÁte Salvajes"
# Temporalmente acerca la meta para probar la escena final desde el inicio.
DEBUG_ENDING_AT_START = False

# ------------------------------------------------------------
# FISICA
# ------------------------------------------------------------
GRAVITY = 0.7
JUMP_FORCE = -14
MOVE_SPEED = 3.5
FRICTION = 0.82
MAX_FALL_SPEED = 16

# ------------------------------------------------------------
# TAMANOS
# ------------------------------------------------------------
TILE_SIZE = 40
PLAYER_SIZE = (34, 34)
GROUND_Y = 380
GROUND_HEIGHT = 70

# ------------------------------------------------------------
# COLORES PLACEHOLDER. Se usan si falta un sprite real.
# ------------------------------------------------------------
GROUND_COLOR = (74, 55, 40)
PLATFORM_COLOR = (139, 111, 71)
PLAYER_COLOR = (230, 57, 70)
ENEMY_COLOR = (106, 13, 173)
COLLECTIBLE_COLOR = (255, 215, 0)
GOAL_COLOR = (0, 255, 136)

PHASE_COLORS = {
    1: (135, 206, 235),
    2: (90, 74, 106),
    3: (45, 27, 78),
}

# ------------------------------------------------------------
# ENEMIGOS POR TIPO (placeholder, cambia al llegar sprites)
# ------------------------------------------------------------
ENEMY_COLORS = {
    "gusano": (150, 90, 60),
    "babosa": (120, 160, 90),
    "tomate_podrido": (90, 40, 40),
    "generico": ENEMY_COLOR,
}

# ------------------------------------------------------------
# HUERTO (zona 1). Colores placeholder de decoracion.
# ------------------------------------------------------------
HUERTO_DIRT_COLOR = (109, 74, 46)
HUERTO_GRASS_COLOR = (95, 158, 78)
HUERTO_CROP_COLOR = (76, 130, 56)
HUERTO_FLOWER_COLORS = [(255, 182, 193), (255, 223, 90), (200, 120, 220)]
HUERTO_STONE_COLOR = (140, 140, 140)
HUERTO_CRATE_COLOR = (150, 111, 51)

# ------------------------------------------------------------
# ZONAS DEL NIVEL COMPLETO
# huerto -> cultivo -> peligro -> casa -> cocina -> estufa -> jefe
# ------------------------------------------------------------
ZONE_SKY_COLORS = {
    "huerto": ((135, 206, 235), (215, 240, 255)),
    "cultivo": ((110, 180, 150), (200, 235, 210)),
    "peligro": ((70, 60, 80), (130, 95, 95)),
    "casa": ((200, 140, 110), (250, 200, 150)),
}
ZONE_INTERIOR = {
    "cocina": {"wall": (222, 200, 170), "wall_dark": (200, 175, 145), "trim": (150, 110, 70)},
    "estufa": {"wall": (90, 45, 40), "wall_dark": (65, 28, 26), "trim": (40, 18, 16)},
    "jefe": {"wall": (55, 20, 22), "wall_dark": (35, 12, 14), "trim": (20, 8, 8)},
}

# ------------------------------------------------------------
# JEFE FINAL: EL GRAN CHEF
# ------------------------------------------------------------
BOSS_SIZE = (76, 96)
BOSS_HEALTH = 5
BOSS_SPEED = 1.6
BOSS_THROW_COOLDOWN = 90
BOSS_DETECTION_RANGE = 520
BOSS_HIT_COOLDOWN = 35
PROJECTILE_SIZE = (22, 22)
PROJECTILE_SPEED = 6

# ------------------------------------------------------------
# SONIDO
# Archivos esperados en assets/audio/music/ y assets/audio/sfx/.
# Cambia solo el nombre de archivo aqui, no busques en el codigo.
# Si el archivo no existe, el juego sigue sin sonido, sin error.
# ------------------------------------------------------------
MUSIC_FILES = {
    "menu": "menu.ogg",
    "huerto": "huerto.mp3",
    "cultivo": "cultivo.mp3",
    "peligro": "peligro.mp3",
    "casa": "casa.mp3",
    "cocina": "cocina.mp3",
    "estufa": "estufa.mp3",
    "jefe": "jefe.mp3",
}
ENDING_MUSIC_FILE = os.path.join("audio", "music", "ending_theme.mp3")
ENDING_DIALOGUE_SFX_FILE = os.path.join("audio", "sfx", "checkpoint.mp3")
SFX_FILES = {
    "saltar": "saltar.wav",
    "morir": "morir.wav",
    "recoger": "recoger.wav",
    "checkpoint": "checkpoint.mp3",
    "final": "final.wav",
    "golpe_jefe": "golpe_jefe.wav",
}

# ------------------------------------------------------------
# MENSAJES AL RECOGER UN COLECCIONABLE
# Se elige uno al azar (segun la posicion) salvo que el
# coleccionable tenga su propio mensaje (ver level_builder.py).
# ------------------------------------------------------------
COLLECTIBLE_MESSAGES = [
    "Un recuerdo mas.",
    "Esto tambien lo guardamos.",
    "Otra semilla de esta historia.",
    "Nunca lo vamos a olvidar.",
]