import os
import random
import pygame
import settings

# =============================================================
# UTILIDADES BASE
# =============================================================
def _grid_to_surface(pattern, palette, target_size=None, scale=None):
    """
    Convierte una lista de strings (filas) en un Surface pixel art.
    Cada caracter mapea a un color via 'palette'. '.' es transparente.
    Si se da target_size, escala a ese tamano exacto.
    Si se da scale, escala por ese factor entero.
    """
    rows = len(pattern)
    cols = len(pattern[0])
    small = pygame.Surface((cols, rows), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            color = palette.get(ch)
            if color:
                small.set_at((x, y), color)
    if target_size:
        return pygame.transform.scale(small, target_size)
    if scale:
        return pygame.transform.scale(small, (cols * scale, rows * scale))
    return small

def _load_custom(subfolder, filename):
    """Si existe un sprite real del usuario, lo usa. Si no, devuelve None."""
    path = os.path.join(settings.IMAGES_DIR, subfolder, filename)
    if os.path.isfile(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error:
            return None
    return None

# =============================================================
# TIERRA Y PLATAFORMAS (texturas tileables)
# =============================================================
_GRASS_COLORS = [(95, 158, 78), (110, 175, 90), (80, 140, 65)]
_DIRT_COLORS = [(109, 74, 46), (95, 63, 38), (125, 88, 55)]
_STONE_COLOR = (150, 150, 150)
_ROOT_COLOR = (70, 45, 25)

# Paletas de terreno por zona. "huerto" conserva los colores originales.
_ZONE_TERRAIN_PALETTES = {
    "huerto": {
        "grass": _GRASS_COLORS, "dirt": _DIRT_COLORS,
        "stone": _STONE_COLOR, "root": _ROOT_COLOR,
    },
    "cultivo": {
        "grass": [(66, 150, 64), (82, 168, 78), (54, 128, 56)],
        "dirt": [(88, 68, 40), (72, 54, 32), (102, 80, 48)],
        "stone": (140, 140, 122), "root": (48, 78, 42),
    },
    "peligro": {
        "grass": [(78, 62, 58), (60, 48, 46), (92, 72, 64)],
        "dirt": [(46, 34, 28), (36, 26, 22), (58, 42, 34)],
        "stone": (95, 82, 80), "root": (26, 16, 14),
    },
}

_TERRAIN_TILE_CACHE = {}

def _generate_terrain_tile(width, height, seed, grass_rows_ratio=0.22, zone="huerto"):
    palette_src = _ZONE_TERRAIN_PALETTES.get(zone, _ZONE_TERRAIN_PALETTES["huerto"])
    rng = random.Random(seed)
    grid_w = max(6, width // 4)
    grid_h = max(4, height // 4)
    grass_rows = max(1, int(grid_h * grass_rows_ratio))
    root_columns = rng.sample(range(grid_w), k=min(2, grid_w))
    pattern = []
    
    for y in range(grid_h):
        row_chars = []
        for x in range(grid_w):
            if y < grass_rows:
                row_chars.append("g")
            elif x in root_columns and grass_rows <= y < grass_rows + 3 and rng.random() < 0.55:
                row_chars.append("r")
            elif rng.random() < 0.05:
                row_chars.append("s")
            else:
                row_chars.append(rng.choice(["d", "D", "e"]))
        pattern.append("".join(row_chars))

    palette = {
        "d": palette_src["dirt"][0],
        "D": palette_src["dirt"][1],
        "e": palette_src["dirt"][2],
        "s": palette_src["stone"],
        "r": palette_src["root"],
    }
    surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch == "g":
                color = rng.choice(palette_src["grass"])
            else:
                color = palette[ch]
            surf.set_at((x, y), color)

    return pygame.transform.scale(surf, (width, height))

def get_ground_tiles(zone="huerto"):
    if zone not in _TERRAIN_TILE_CACHE:
        # Nota: asumo que load_custom era _load_custom
        custom = _load_custom("tiles", f"ground{zone}.png") or _load_custom("tiles", "dirt.png")
        if custom:
            tiles = [pygame.transform.scale(custom, (40, settings.GROUND_HEIGHT))]
        else:
            tiles = [
                _generate_terrain_tile(40, settings.GROUND_HEIGHT, seed=hash((zone, i)), zone=zone)
                for i in range(4)
            ]
        _TERRAIN_TILE_CACHE[zone] = tiles
    return _TERRAIN_TILE_CACHE[zone]

_PLATFORM_TILE_CACHE = {}

def get_platform_tiles(zone="huerto"):
    if zone not in _PLATFORM_TILE_CACHE:
        custom = _load_custom("tiles", f"platform{zone}.png") or _load_custom("tiles", "platform.png")
        if custom:
            tiles = [pygame.transform.scale(custom, (40, 20))]
        else:
            tiles = [
                _generate_terrain_tile(40, 20, seed=hash((zone, "p", i)), grass_rows_ratio=0.4, zone=zone)
                for i in range(3)
            ]
        _PLATFORM_TILE_CACHE[zone] = tiles
    return _PLATFORM_TILE_CACHE[zone]

# =============================================================
# INTERIORES: COCINA, ESTUFA Y ARENA DEL JEFE
# =============================================================
_INTERIOR_TILE_CACHE = {}

def _generate_kitchen_floor_tile(width, height, seed):
    rng = random.Random(seed)
    tile_a = (224, 214, 196)
    tile_b = (200, 188, 168)
    grout = (150, 138, 120)
    grid_w, grid_h = 10, 10
    surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    for y in range(grid_h):
        for x in range(grid_w):
            if x == 0 or y == 0:
                color = grout
            else:
                color = tile_a if (x + y) % 2 == 0 else tile_b
            if rng.random() < 0.04:
                color = grout
            surf.set_at((x, y), color)
    return pygame.transform.scale(surf, (width, height))

def _generate_kitchen_counter_tile(width, height, seed):
    rng = random.Random(seed)
    top = (235, 225, 210)
    edge = (180, 145, 95)
    wood = [(150, 110, 65), (135, 98, 58), (162, 122, 74)]
    grid_w, grid_h = 10, 10
    surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    for y in range(grid_h):
        for x in range(grid_w):
            if y < 2:
                surf.set_at((x, y), top if y == 0 else edge)
            else:
                surf.set_at((x, y), rng.choice(wood))
    return pygame.transform.scale(surf, (width, height))

def _generate_stove_tile(width, height, seed):
    rng = random.Random(seed)
    metal = [(70, 70, 78), (55, 55, 62), (85, 85, 92)]
    hot = (220, 90, 40)
    grid_w, grid_h = 10, 10
    surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    for y in range(grid_h):
        for x in range(grid_w):
            if y == 0 and rng.random() < 0.3:
                surf.set_at((x, y), hot)
            else:
                surf.set_at((x, y), rng.choice(metal))
    return pygame.transform.scale(surf, (width, height))

def _generate_arena_tile(width, height, seed):
    rng = random.Random(seed)
    tile_a = (70, 24, 26)
    tile_b = (52, 16, 18)
    line = (110, 40, 36)
    grid_w, grid_h = 10, 10
    surf = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    for y in range(grid_h):
        for x in range(grid_w):
            if x == 0:
                color = line
            else:
                color = tile_a if (x + y) % 2 == 0 else tile_b
            surf.set_at((x, y), color)
    return pygame.transform.scale(surf, (width, height))

_INTERIOR_GENERATORS = {
    "kitchen_floor": (_generate_kitchen_floor_tile, "kitchen_floor.png", settings.GROUND_HEIGHT),
    "kitchen_counter": (_generate_kitchen_counter_tile, "kitchen_counter.png", 20),
    "stove": (_generate_stove_tile, "stove.png", 20),
    "arena": (_generate_arena_tile, "arena.png", settings.GROUND_HEIGHT),
}

def get_interior_tiles(kind):
    if kind not in _INTERIOR_TILE_CACHE:
        generator, filename, height = _INTERIOR_GENERATORS[kind]
        custom = _load_custom("tiles", filename)
        if custom:
            tiles = [pygame.transform.scale(custom, (40, height))]
        else:
            tiles = [generator(40, height, seed=hash((kind, i))) for i in range(3)]
        _INTERIOR_TILE_CACHE[kind] = tiles
    return _INTERIOR_TILE_CACHE[kind]

def draw_goal_flag(surface, rect):
    pole_color = (90, 60, 30)
    flag_color = (255, 200, 40)
    pole_x = rect.x + rect.width // 2 - 3
    pygame.draw.rect(surface, pole_color, (pole_x, rect.y, 6, rect.height))
    flag_points = [
        (pole_x + 6, rect.y + 2),
        (pole_x + 6 + rect.width // 2, rect.y + 12),
        (pole_x + 6, rect.y + 22),
    ]
    pygame.draw.polygon(surface, flag_color, flag_points)

# =============================================================
# DECORACION DEL HUERTO
# =============================================================
_TOMATO_PALETTE = {
    "l": (46, 125, 50),
    "L": (102, 187, 106),
    "t": (211, 47, 47),
    "s": (85, 139, 47),
}
_TOMATO_PATTERNS = [
    ["..LL..", ".lLLl.", ".ltts.", "..ss..", "..ss.."],
    ["..ll.ll.", ".lLLlLL.", ".ltt.tt.", "..ll....", "..ss....", "..ss....", "..ss...."],
    [".lllll.", "lLtttLl", ".lLLLl.", "..sss..", "..sss.."],
]
_WEED_PALETTE = {"l": (70, 130, 60), "s": (60, 90, 40)}
_WEED_PATTERN = ["l.l.l", ".lll.", "..s.."]
_STONE_PALETTE = {"s": (150, 150, 150), "S": (190, 190, 190)}
_STONE_PATTERN = [".ss.", "sSSs", ".ss."]
_TWIG_PALETTE = {"o": (101, 67, 33)}
_TWIG_PATTERN = ["o..", ".o.", "..o"]
_CRATE_PALETTE = {"W": (180, 140, 90), "b": (120, 85, 50)}
_CRATE_PATTERN = ["WWWWWW", "WbWWbW", "WWbbWW", "WbWWbW", "WWWWWW"]
_FENCE_PALETTE = {"w": (150, 120, 90)}
_FENCE_PATTERN = ["w.w", "w.w", "www", "w.w", "w.w"]
_WATERING_CAN_PALETTE = {"m": (120, 140, 150), "h": (90, 70, 50)}
_WATERING_CAN_PATTERN = ["..mm..", ".mmmm.", "mmmmmh", ".mmmm.", "..mm.."]
_TOOL_PALETTE = {"O": (170, 170, 170), "o": (101, 67, 33)}
_TOOL_PATTERN = [".OOO.", "..o..", "..o..", "..o.."]
_CROP_PALETTE = {"g": (110, 170, 90), "d": (101, 74, 46)}
_CROP_PATTERN = ["..g...", ".ggg..", "dddddd"]
_FLOWER_PETAL_COLORS = [(255, 182, 193), (255, 223, 90), (186, 140, 220), (255, 160, 122)]
_FLOWER_PATTERN = [".p.", "pFp", ".p.", ".s.", ".s."]

# --- Zona peligrosa: decoracion oscura ---
_DARK_ROCK_PALETTE = {"r": (70, 62, 60), "R": (95, 85, 82)}
_DARK_ROCK_PATTERN = [".RR.", "rRRr", "rrrr"]
_DARK_PLANT_PALETTE = {"l": (55, 70, 48), "L": (75, 92, 65), "s": (40, 30, 26)}
_DARK_PLANT_PATTERN = ["l.l.l", ".LLL.", ".LLL.", "..s.."]

# --- Entrada a la casa (¡ACTUALIZADO!) ---
_HOUSE_PALETTE = {
    "w": (210, 168, 120), "W": (178, 132, 92),
    "r": (120, 45, 40), "R": (95, 32, 28),
    "d": (96, 62, 40), "y": (255, 224, 120),
    "b": (150, 90, 70),
}
_HOUSE_PATTERN = [
    "...rrrrrrrrrrrr...",
    "..rRRRRRRRRRRRr..",
    ".rRRRRRRRRRRRRRr.",
    "wwwwwwwwwwwwwwwww",
    "wWbWbWyyyWbWbWWWw",
    "wWbWbWyWyWbWbWWWw",
    "wWbWbWyyyWbWbWWWw",
    "wwwwwwwwwwwwwwwww",
    "wwwwwwwwddwwwwwww",
    "wwwwwwwwddwwwwwww",
    "wwwwwwwwddwwwwwww",
]

_PORCH_PALETTE = {"w": (168, 122, 84), "W": (140, 100, 66)}
_PORCH_PATTERN = ["wwwwwwwwww", "WWWWWWWWWW"]
_DOOR_PALETTE = {"d": (96, 62, 40), "k": (220, 190, 90)}
_DOOR_PATTERN = ["dddd", "dddd", "ddkd", "dddd"]
_POT_PALETTE = {"c": (170, 100, 60), "l": (70, 140, 60)}
_POT_PATTERN = [".lll.", "ll.ll", ".ccc.", "cccc."]

_BEAR_PALETTE = {
    "b": (92, 52, 34), "B": (172, 108, 67),
    "d": (35, 25, 22), "p": (238, 157, 145),
}
_BEAR_PATTERN = [
    "..bb..bb..",
    ".bBBBBBBb.",
    "bBBBBBBBBb",
    "bBBdBBdBBb",
    "bBBBBpBBBb",
    ".bBBBBBBb.",
    "..BB..BB..",
    ".bbB..Bbb.",
]

# --- Cocina: props gigantes vistos desde un personaje pequeno ---
_PLATE_PALETTE = {"p": (240, 240, 235), "P": (210, 210, 205)}
_PLATE_PATTERN = [".PPPPPP.", "PppppppP", ".PPPPPP."]
_CUTLERY_PALETTE = {"m": (200, 200, 210)}
_CUTLERY_PATTERN = ["m.m.m", "m.m.m", "m.mmm", "m...."]
_GLASS_PALETTE = {"g": (200, 230, 235)}
_GLASS_PATTERN = ["gggg", "g..g", "g..g", ".gg."]
_POT_BIG_PALETTE = {"m": (90, 90, 98), "M": (130, 130, 138), "h": (60, 60, 66)}
_POT_BIG_PATTERN = ["h.MMMMMM.h", "mmmmmmmmmm", "mmmmmmmmmm", ".mmmmmmmm."]
_SHELF_PALETTE = {"w": (150, 110, 70), "W": (120, 85, 52)}
_SHELF_PATTERN = ["WWWWWWWW", "wwwwwwww", "........", "WWWWWWWW", "wwwwwwww"]
_CABINET_PALETTE = {"w": (196, 150, 108), "W": (160, 118, 80), "k": (90, 60, 40)}
_CABINET_PATTERN = ["WWWWWWWW", "wwkwwkww", "wwkwwkww", "wwkwwkww", "WWWWWWWW"]
_BOTTLE_PALETTE = {"g": (90, 160, 90), "k": (230, 220, 200)}
_BOTTLE_PATTERN = [".k.", ".g.", "ggg", "ggg", "ggg"]
_HANGING_UTENSIL_PALETTE = {"m": (150, 150, 158), "h": (90, 60, 40)}
_HANGING_UTENSIL_PATTERN = ["m...m", "m...m", "mm.mm", ".m.m."]
_OIL_PALETTE = {"o": (40, 30, 20), "O": (60, 46, 30)}
_OIL_PATTERN = [".OOOO.", "OoooooO", ".OOOO."]
_BROKEN_PLATE_PALETTE = {"p": (240, 240, 235), "P": (210, 210, 205)}
_BROKEN_PLATE_PATTERN = ["PP.PP", "P...P", ".P.P."]

_FLOWER_PALETTE_BASE = {"F": (255, 224, 102), "s": (76, 140, 60)}
_DECORATION_CACHE = {}

def get_decoration_sprite(kind, seed):
    """
    Devuelve un sprite decorativo. Usa una imagen real si existe en
    assets/images/decorations/.png, si no, genera pixel art.
    Se cachean pocas variantes por tipo para no repetir memoria.
    """
    custom = _load_custom("decorations", f"{kind}.png")
    if custom:
        return custom
    
    variant = seed % 3
    cache_key = (kind, variant)
    if cache_key in _DECORATION_CACHE:
        return _DECORATION_CACHE[cache_key]

    if kind == "planta_tomate":
        pattern = _TOMATO_PATTERNS[variant % len(_TOMATO_PATTERNS)]
        sprite = _grid_to_surface(pattern, _TOMATO_PALETTE, scale=4)
    elif kind == "flor":
        palette = dict(_FLOWER_PALETTE_BASE)
        palette["p"] = _FLOWER_PETAL_COLORS[variant % len(_FLOWER_PETAL_COLORS)]
        sprite = _grid_to_surface(_FLOWER_PATTERN, palette, scale=4)
    elif kind == "maleza":
        sprite = _grid_to_surface(_WEED_PATTERN, _WEED_PALETTE, scale=4)
    elif kind == "piedra":
        sprite = _grid_to_surface(_STONE_PATTERN, _STONE_PALETTE, scale=4)
    elif kind == "ramita":
        sprite = _grid_to_surface(_TWIG_PATTERN, _TWIG_PALETTE, scale=4)
    elif kind == "caja":
        sprite = _grid_to_surface(_CRATE_PATTERN, _CRATE_PALETTE, scale=4)
    elif kind == "cerca":
        sprite = _grid_to_surface(_FENCE_PATTERN, _FENCE_PALETTE, scale=4)
    elif kind == "regadera":
        sprite = _grid_to_surface(_WATERING_CAN_PATTERN, _WATERING_CAN_PALETTE, scale=4)
    elif kind == "herramienta":
        sprite = _grid_to_surface(_TOOL_PATTERN, _TOOL_PALETTE, scale=4)
    elif kind == "cultivo":
        sprite = _grid_to_surface(_CROP_PATTERN, _CROP_PALETTE, scale=4)
    elif kind == "roca_oscura":
        sprite = _grid_to_surface(_DARK_ROCK_PATTERN, _DARK_ROCK_PALETTE, scale=4)
    elif kind == "planta_oscura":
        sprite = _grid_to_surface(_DARK_PLANT_PATTERN, _DARK_PLANT_PALETTE, scale=4)
    elif kind == "casa":
        sprite = _grid_to_surface(_HOUSE_PATTERN, _HOUSE_PALETTE, scale=7) # ¡ACTUALIZADO A SCALE=7!
    elif kind == "porche":
        sprite = _grid_to_surface(_PORCH_PATTERN, _PORCH_PALETTE, scale=5)
    elif kind == "puerta":
        sprite = _grid_to_surface(_DOOR_PATTERN, _DOOR_PALETTE, scale=6)
    elif kind == "maceta":
        sprite = _grid_to_surface(_POT_PATTERN, _POT_PALETTE, scale=4)
    elif kind == "osito":
        sprite = _grid_to_surface(_BEAR_PATTERN, _BEAR_PALETTE, scale=4)
    elif kind == "plato":
        sprite = _grid_to_surface(_PLATE_PATTERN, _PLATE_PALETTE, scale=4)
    elif kind == "cubiertos":
        sprite = _grid_to_surface(_CUTLERY_PATTERN, _CUTLERY_PALETTE, scale=4)
    elif kind == "vaso":
        sprite = _grid_to_surface(_GLASS_PATTERN, _GLASS_PALETTE, scale=4)
    elif kind == "olla_deco":
        sprite = _grid_to_surface(_POT_BIG_PATTERN, _POT_BIG_PALETTE, scale=5)
    elif kind == "estante":
        sprite = _grid_to_surface(_SHELF_PATTERN, _SHELF_PALETTE, scale=5)
    elif kind == "armario":
        sprite = _grid_to_surface(_CABINET_PATTERN, _CABINET_PALETTE, scale=5)
    elif kind == "botella_deco":
        sprite = _grid_to_surface(_BOTTLE_PATTERN, _BOTTLE_PALETTE, scale=4)
    elif kind == "utensilio_colgante":
        sprite = _grid_to_surface(_HANGING_UTENSIL_PATTERN, _HANGING_UTENSIL_PALETTE, scale=4)
    elif kind == "aceite":
        sprite = _grid_to_surface(_OIL_PATTERN, _OIL_PALETTE, scale=4)
    elif kind == "plato_roto":
        sprite = _grid_to_surface(_BROKEN_PLATE_PATTERN, _BROKEN_PLATE_PALETTE, scale=4)
    else:
        sprite = _grid_to_surface(_STONE_PATTERN, _STONE_PALETTE, scale=4)

    _DECORATION_CACHE[cache_key] = sprite
    return sprite


# =============================================================
# ENEMIGOS (2 cuadros de animacion por tipo)
# =============================================================
_GUSANO_PALETTE = {"o": (150, 100, 60), "O": (120, 80, 45)}
_GUSANO_FRAMES = [
    [".oOoO.", "oOoOoO", ".o..o."],
    ["..oOo.", ".oOoOo", "o..o.."],
]
_BABOSA_PALETTE = {"L": (120, 170, 90), "l": (160, 200, 130), "g": (150, 170, 120)}
_BABOSA_FRAMES = [
    ["..LLLL..", ".LllllL.", "gggggggg"],
    [".LLLL...", "LlllllL.", "gggggggg"],
]
_TOMATE_PODRIDO_PALETTE = {"d": (120, 40, 35), "X": (70, 20, 20)}
_TOMATE_PODRIDO_FRAMES = [
    [".dddd.", "dXddXd", "dd..dd", ".dddd."],
    [".dddd.", "ddXXdd", "dX..Xd", ".dddd."],
]
_ESCARABAJO_PALETTE = {"c": (60, 90, 160), "C": (90, 130, 210), "p": (30, 40, 60)}
_ESCARABAJO_FRAMES = [
    [".CCCC.", "cccccc", "p.pp.p"],
    [".CCCC.", "cccccc", ".p.p.."],
]
_MOSCA_PALETTE = {"w": (230, 230, 240), "b": (40, 40, 50)}
_MOSCA_FRAMES = [
    ["w.b.w", ".bbb.", "w...w"],
    [".b.b.", ".bbb.", "w...w"],
]
_PIMENTON_PALETTE = {"g": (60, 150, 50), "r": (210, 60, 40), "R": (240, 110, 70)}
_PIMENTON_FRAMES = [
    ["..g...", ".rRr..", "rRRRr.", ".rrr.."],
    ["..g...", ".Rrr..", "rrRRr.", ".rrr.."],
]
_ESPINA_PALETTE = {"g": (60, 40, 30), "s": (200, 200, 200)}
_ESPINA_FRAMES = [
    ["s.s.s.s", "gsgsgsg", "ggggggg"],
]
_CUCHILLO_PALETTE = {"m": (200, 200, 210), "h": (90, 60, 40)}
_CUCHILLO_FRAMES = [
    ["mmmmm.", ".mmmh.", "..hh.."],
    ["mmmmm.", ".mmmh.", "..hh.."],
]
_SARTEN_PALETTE = {"m": (60, 60, 65), "M": (100, 100, 108), "h": (80, 55, 35)}
_SARTEN_FRAMES = [
    [".MMMM.", "Mmmmmm", "....hh"],
    [".MMMM.", "mMMMMm", "....hh"],
]
_KETCHUP_PALETTE = {"g": (200, 40, 40), "w": (240, 240, 240), "c": (40, 100, 40)}
_KETCHUP_FRAMES = [
    [".ccc.", "gwwwg", "ggggg", ".ggg."],
    [".ccc.", "gwwwg", "ggggg", "ggggg"],
]
_TOSTADORA_PALETTE = {"m": (190, 190, 200), "M": (150, 150, 160), "b": (210, 120, 60)}
_TOSTADORA_FRAMES = [
    ["b.b..", "MMMMM", "mmmmm"],
    [".b.b.", "MMMMM", "mmmmm"],
]

_ENEMY_LIBRARY = {
    "gusano": (_GUSANO_FRAMES, _GUSANO_PALETTE),
    "babosa": (_BABOSA_FRAMES, _BABOSA_PALETTE),
    "tomate_podrido": (_TOMATE_PODRIDO_FRAMES, _TOMATE_PODRIDO_PALETTE),
    "escarabajo": (_ESCARABAJO_FRAMES, _ESCARABAJO_PALETTE),
    "mosca_fruta": (_MOSCA_FRAMES, _MOSCA_PALETTE),
    "pimenton": (_PIMENTON_FRAMES, _PIMENTON_PALETTE),
    "espina": (_ESPINA_FRAMES, _ESPINA_PALETTE),
    "cuchillo": (_CUCHILLO_FRAMES, _CUCHILLO_PALETTE),
    "sarten": (_SARTEN_FRAMES, _SARTEN_PALETTE),
    "botella_ketchup": (_KETCHUP_FRAMES, _KETCHUP_PALETTE),
    "tostadora": (_TOSTADORA_FRAMES, _TOSTADORA_PALETTE),
}
_ENEMY_FRAME_CACHE = {}

def get_enemy_frames(enemy_type, width, height):
    custom = _load_custom("enemies", f"{enemy_type}.png")
    if custom:
        return [pygame.transform.scale(custom, (width, height))]
    
    cache_key = (enemy_type, width, height)
    if cache_key in _ENEMY_FRAME_CACHE:
        return _ENEMY_FRAME_CACHE[cache_key]

    patterns, palette = _ENEMY_LIBRARY.get(enemy_type, (_GUSANO_FRAMES, _GUSANO_PALETTE))
    frames = [_grid_to_surface(p, palette, target_size=(width, height)) for p in patterns]
    _ENEMY_FRAME_CACHE[cache_key] = frames
    return frames

# =============================================================
# COLECCIONABLES (semilla brillante, 2 cuadros)
# =============================================================
_SEED_PALETTE = {"d": (212, 175, 55), "D": (255, 230, 120), "": (255, 255, 255)}
_SEED_FRAMES = [
    ["..d..", ".dDd.", "dDDDd", ".dDd.", "..d.."],
    [".d..", ".dDd.", "dDDDd", ".dDd.", "..d.*"],
]
_SEED_FRAME_CACHE = {}

# =============================================================
# JUGADOR: personaje pequeno con un tomate sobre la cabeza
# =============================================================
_PLAYER_PALETTE = {
    "t": (211, 47, 47),     # tomate
    "T": (245, 85, 70),     # brillo tomate
    "l": (67, 145, 60),     # hoja tomate
    "e": (25, 25, 25),      # ojos
    "s": (255, 219, 172),   # piel
    "o": (86, 60, 158),     # overol
    "b": (58, 40, 26),      # botas
}
_PLAYER_FRAMES = [
    [
        "...lll...",
        "..tTTt...",
        ".tTTTTt..",
        ".tetettt.",
        ".tttttt..",
        "..ssss...",
        ".oooooo..",
        ".oooooo..",
        "..oo.oo..",
        ".bb...bb.",
    ],
    [
        "...lll...",
        "..tTTt...",
        ".tTTTTt..",
        ".tetettt.",
        ".tttttt..",
        "..ssss...",
        ".oooooo..",
        ".oooooo..",
        ".oo..oo..",
        "bb....bb.",
    ],
]
_PLAYER_FRAME_CACHE = {}

def get_player_frames(w, h):
    custom = _load_custom("player", "player.png")
    if custom:
        return [pygame.transform.scale(custom, (w, h))]
    
    key = (w, h)
    if key in _PLAYER_FRAME_CACHE:
        return _PLAYER_FRAME_CACHE[key]

    frames = [_grid_to_surface(p, _PLAYER_PALETTE, target_size=(w, h)) for p in _PLAYER_FRAMES]
    _PLAYER_FRAME_CACHE[key] = frames
    return frames

def get_collectible_frames(size):
    custom = _load_custom("collectibles", "semilla.png")
    if custom:
        return [pygame.transform.scale(custom, (size, size))]
    
    if size in _SEED_FRAME_CACHE:
        return _SEED_FRAME_CACHE[size]

    frames = [_grid_to_surface(p, _SEED_PALETTE, target_size=(size, size)) for p in _SEED_FRAMES]
    _SEED_FRAME_CACHE[size] = frames
    return frames

# =============================================================
# JEFE FINAL: EL GRAN CHEF, Y SUS PROYECTILES
# =============================================================
_CHEF_PALETTE = {
    "w": (250, 250, 250),   # gorro y chaqueta
    "W": (225, 225, 225),   # sombra chaqueta
    "s": (255, 210, 170),   # piel
    "m": (90, 55, 30),      # bigote
    "b": (30, 30, 35),      # botones / pantalon
    "r": (200, 40, 35),     # panuelo rojo
}
_CHEF_FRAMES = [
    [
        "..wwwwww..",
        ".wwwwwwww.",
        "..wwwwww..",
        "..ssssss..",
        ".ssmmmmss.",
        "..ssssss..",
        ".rrrrrrrr.",
        "wWWWWWWWw",
        "wWWbbbbWw",
        "wWWbbbbWw",
        ".bb....bb.",
    ],
    [
        "..wwwwww..",
        ".wwwwwwww.",
        "..wwwwww..",
        "..ssssss..",
        ".ssmmmmss.",
        "..ssssss..",
        ".rrrrrrrr.",
        "WwwwwwwwW",
        "WwwbbbbwW",
        "WwwbbbbwW",
        "bb....bb..",
    ],
]
_CHEF_FRAME_CACHE = {}

def get_boss_frames(w, h):
    custom = _load_custom("bosses", "chef.png")
    if custom:
        return [pygame.transform.scale(custom, (w, h))]
    
    key = (w, h)
    if key in _CHEF_FRAME_CACHE:
        return _CHEF_FRAME_CACHE[key]

    frames = [_grid_to_surface(p, _CHEF_PALETTE, target_size=(w, h)) for p in _CHEF_FRAMES]
    _CHEF_FRAME_CACHE[key] = frames
    return frames

_PROJECTILE_PALETTE = {"m": (70, 70, 78), "M": (110, 110, 118), "h": (90, 60, 40)}
_PROJECTILE_PATTERN = [".MMM.", "Mmmmm", "..hh."]
_PROJECTILE_CACHE = {}

def get_projectile_frame(size):
    custom = _load_custom("bosses", "proyectil.png")
    if custom:
        return pygame.transform.scale(custom, (size, size))
    
    if size in _PROJECTILE_CACHE:
        return _PROJECTILE_CACHE[size]

    sprite = _grid_to_surface(_PROJECTILE_PATTERN, _PROJECTILE_PALETTE, target_size=(size, size))
    _PROJECTILE_CACHE[size] = sprite
    return sprite

def draw_health_bar(surface, x, y, width, height, ratio, label=None, font=None):
    ratio = max(0.0, min(1.0, ratio))
    pygame.draw.rect(surface, (30, 20, 20), (x - 3, y - 3, width + 6, height + 6), border_radius=6)
    pygame.draw.rect(surface, (70, 20, 20), (x, y, width, height), border_radius=4)
    if ratio > 0:
        fill_color = (210, 60, 40) if ratio > 0.35 else (230, 150, 40)
        pygame.draw.rect(surface, fill_color, (x, y, int(width * ratio), height), border_radius=4)
    if label and font:
        text = font.render(label, True, (255, 255, 255))
        surface.blit(text, (x, y - 22))

# =============================================================
# EFECTOS: FUEGO Y VAPOR (ESTUFA)
# =============================================================
def draw_flame(surface, x, y, w, h, tick):
    flicker = 3 if (tick // 6) % 2 == 0 else 0
    colors = [(255, 140, 20), (255, 190, 60), (255, 230, 120)]
    base = h
    for i, color in enumerate(colors):
        seg_h = base - i * (h // 4) - flicker
        seg_h = max(2, seg_h)
        seg_w = w - i * (w // 4)
        seg_x = x + (w - seg_w) // 2
        pygame.draw.ellipse(surface, color, (seg_x, y + h - seg_h, seg_w, seg_h))

def draw_steam(surface, x, y, tick):
    offset = (tick % 40) / 40
    for i in range(3):
        radius = 5 + i * 2
        puff_y = y - int(offset * 30) - i * 14
        alpha = max(0, 160 - int(offset * 160) - i * 20)
        if alpha <= 0:
            continue
        puff = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(puff, (255, 255, 255, alpha), (radius, radius), radius)
        surface.blit(puff, (x - radius, puff_y - radius))