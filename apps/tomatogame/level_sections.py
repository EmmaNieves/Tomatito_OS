import random

import settings
from platform_obj import Platform, MovingPlatform
from enemy import Enemy
from collectible import Collectible
from decoration import Decoration
from checkpoint import Checkpoint
from effects import FireSpot, SteamSpot
from boss import Boss

GROUND_Y = settings.GROUND_Y
GROUND_HEIGHT = settings.GROUND_HEIGHT


def add_flat_ground(platforms, start_x, length, ground_type="ground"):
    """Tramo de suelo solido. Devuelve la x donde termina."""
    platforms.append(Platform(start_x, GROUND_Y, length, GROUND_HEIGHT, ground_type))
    return start_x + length


# =========================================================
# BLOQUES ESPECIFICOS DEL HUERTO (zona 1)
# =========================================================

def add_dirt_ground(platforms, start_x, length):
    """Tramo de suelo de tierra con cesped, para el huerto."""
    platforms.append(Platform(start_x, GROUND_Y, length, GROUND_HEIGHT, "dirt"))
    return start_x + length


def add_dirt_platform(platforms, x, y, width):
    """Plataforma flotante de tierra, para el huerto."""
    platforms.append(Platform(x, y, width, 20, "dirt_platform"))


def add_garden_decorations(decorations, start_x, length, density=90):
    """
    Llena un tramo de suelo con plantas de tomate, flores,
    maleza y piedras. Puramente visual, no afecta jugabilidad.
    """
    rng = random.Random(start_x)
    kinds = (
        ["planta_tomate"] * 2
        + ["flor"] * 3
        + ["maleza"] * 2
        + ["piedra"] * 2
        + ["ramita"] * 1
        + ["cultivo"] * 2
    )
    x = start_x + 15
    while x < start_x + length - 15:
        kind = rng.choice(kinds)
        decorations.append(Decoration(x, GROUND_Y, kind, seed=x))
        x += density + rng.randint(-25, 25)


def add_crate_decoration(decorations, x, count=1):
    """Cajas de madera apiladas, decorativas."""
    y = GROUND_Y
    for i in range(count):
        crate = Decoration(x, y, "caja", seed=x + i)
        decorations.append(crate)
        y = crate.rect.top


def add_fence_decoration(decorations, start_x, length, spacing=45):
    """Cerca de madera decorativa a lo largo de un tramo."""
    x = start_x
    while x < start_x + length:
        decorations.append(Decoration(x, GROUND_Y, "cerca", seed=x))
        x += spacing


def add_tool_decoration(decorations, x, kind="regadera"):
    """Un objeto suelto de jardin: regadera o herramienta."""
    decorations.append(Decoration(x, GROUND_Y, kind, seed=x))


def add_worm(enemies, x, patrol_min, patrol_max, assets, speed=1.2):
    """Gusano pequeno, enemigo introductorio, lento y sencillo."""
    enemies.append(Enemy(x, GROUND_Y - 16, 24, 16, patrol_min, patrol_max, speed, assets, "gusano"))


def add_slug(enemies, x, patrol_min, patrol_max, assets, speed=0.6):
    """Babosa, aun mas lenta que el gusano."""
    enemies.append(Enemy(x, GROUND_Y - 14, 26, 14, patrol_min, patrol_max, speed, assets, "babosa"))


def add_rotten_tomato(enemies, x, patrol_min, patrol_max, assets, speed=1.6):
    """Tomate podrido, un poco mas rapido, mismo tamano que el jugador."""
    enemies.append(Enemy(x, GROUND_Y - 30, 28, 30, patrol_min, patrol_max, speed, assets, "tomate_podrido"))


def add_checkpoint(checkpoints, x, message="Checkpoint alcanzado."):
    """Osito de guardado apoyado sobre el suelo."""
    checkpoint = Checkpoint(x, GROUND_Y - 32, message=message)
    checkpoints.append(checkpoint)
    return checkpoint


def add_gap(platforms, start_x, gap_width, ground_after=260):
    """Hueco en el suelo, requiere saltar. Devuelve la x final."""
    end_of_current = start_x
    cursor = end_of_current + gap_width
    return add_flat_ground(platforms, cursor, ground_after)


def add_gap_with_enemy(platforms, enemies, start_x, before_len, gap_width, after_len, enemy_speed, assets,
                        ground_type="ground", enemy_type="generico"):
    """Hueco seguido de un tramo patrullado por un enemigo."""
    end_before = add_flat_ground(platforms, start_x, before_len, ground_type)
    ground_start = end_before + gap_width
    end_after = add_flat_ground(platforms, ground_start, after_len, ground_type)

    enemy_x = ground_start + 30
    enemies.append(
        Enemy(enemy_x, GROUND_Y - 30, 30, 30, ground_start + 10, end_after - 40, enemy_speed, assets, enemy_type)
    )
    return end_after


def add_enemy_corridor(platforms, enemies, start_x, length, enemy_count, base_speed, assets,
                        ground_type="ground", enemy_type="generico"):
    """Tramo largo y plano con varios enemigos patrullando."""
    end_x = add_flat_ground(platforms, start_x, length, ground_type)
    step = length // (enemy_count + 1)
    for i in range(enemy_count):
        enemy_x = start_x + step * (i + 1)
        speed = base_speed + i * 0.35
        enemies.append(
            Enemy(enemy_x, GROUND_Y - 30, 30, 30, start_x + 20, end_x - 20, speed, assets, enemy_type)
        )
    return end_x


def add_floating_steps(platforms, collectibles, start_x, steps, step_gap, height_start, height_step, assets,
                        platform_type="platform"):
    """
    Escalera de plataformas flotantes con un coleccionable
    sobre cada una. height_step negativo sube, positivo baja.
    """
    cursor = start_x
    height = height_start
    for _ in range(steps):
        cursor += step_gap
        height += height_step
        height = max(150, min(height, GROUND_Y - 60))
        platforms.append(Platform(cursor, height, 100, 20, platform_type))
        collectibles.append(Collectible(cursor + 35, height - 30, assets))
    return cursor + 150


def add_collectible_row(collectibles, start_x, count, spacing, height_above_ground, assets):
    """Fila de coleccionables sobre el suelo, altura fija."""
    for i in range(count):
        x = start_x + i * spacing
        y = GROUND_Y - height_above_ground
        collectibles.append(Collectible(x, y, assets))
    return start_x + count * spacing


# =========================================================
# ZONA 2: CULTIVO
# =========================================================

def add_cultivo_ground(platforms, start_x, length):
    platforms.append(Platform(start_x, GROUND_Y, length, GROUND_HEIGHT, "cultivo_ground"))
    return start_x + length


def add_cultivo_platform(platforms, x, y, width):
    platforms.append(Platform(x, y, width, 20, "cultivo_platform"))


def add_moving_platform(platforms, x, y, width, axis="y", distance=60, speed=0.03):
    plat = MovingPlatform(x, y, width, 18, "cultivo_platform", axis, distance, speed)
    platforms.append(plat)
    return plat


def add_cultivo_decorations(decorations, start_x, length, density=90):
    rng = random.Random(start_x + 7)
    kinds = (
        ["cultivo"] * 3 + ["planta_tomate"] * 2 + ["maleza"] * 2
        + ["piedra"] * 2 + ["caja"] * 1
    )
    x = start_x + 15
    while x < start_x + length - 15:
        kind = rng.choice(kinds)
        decorations.append(Decoration(x, GROUND_Y, kind, seed=x))
        x += density + rng.randint(-25, 25)


def add_beetle(enemies, x, patrol_min, patrol_max, assets, speed=1.8):
    """Escarabajo, algo mas rapido que el gusano."""
    enemies.append(Enemy(x, GROUND_Y - 18, 24, 18, patrol_min, patrol_max, speed, assets, "escarabajo"))


def add_fruit_fly(enemies, x, patrol_min, patrol_max, assets, speed=1.4, height_above_ground=60):
    """Mosca de la fruta, patrulla en el aire."""
    enemies.append(
        Enemy(x, GROUND_Y - height_above_ground, 18, 14, patrol_min, patrol_max, speed, assets, "mosca_fruta")
    )


# =========================================================
# ZONA 3: PELIGROSA
# =========================================================

def add_peligro_ground(platforms, start_x, length):
    platforms.append(Platform(start_x, GROUND_Y, length, GROUND_HEIGHT, "peligro_ground"))
    return start_x + length


def add_peligro_decorations(decorations, start_x, length, density=100):
    rng = random.Random(start_x + 13)
    kinds = ["roca_oscura"] * 3 + ["planta_oscura"] * 3 + ["piedra"] * 1
    x = start_x + 15
    while x < start_x + length - 15:
        kind = rng.choice(kinds)
        decorations.append(Decoration(x, GROUND_Y, kind, seed=x))
        x += density + rng.randint(-25, 25)


def add_spike_hazard(enemies, x, width=30):
    """Espinas fijas en el suelo. Tocarlas hace respawnear al jugador."""
    enemies.append(Enemy(x, GROUND_Y - 16, width, 16, x, x, 0, None, "espina"))


def add_pepper_enemy(enemies, x, patrol_min, patrol_max, assets, speed=1.3):
    """Pimenton explosivo, patrulla lento pero es peligroso."""
    enemies.append(Enemy(x, GROUND_Y - 24, 22, 24, patrol_min, patrol_max, speed, assets, "pimenton"))


def add_danger_gap(platforms, start_x, gap_width, ground_after=260):
    """Hueco sobre terreno peligroso, mismo patron que add_gap."""
    cursor = start_x + gap_width
    return add_peligro_ground(platforms, cursor, ground_after)


# =========================================================
# ENTRADA A LA CASA (transicion)
# =========================================================

def add_house_entrance(platforms, decorations, start_x, length=380):
    """Porche tranquilo antes de entrar a la cocina, ajustado al nuevo tamaño."""
    cursor = add_flat_ground(platforms, start_x, length)
    
    # Asumiendo que Decoration está importado y usa la constante GROUND_Y de settings
    from settings import GROUND_Y
    
    # Centramos más la casa y el porche
    decorations.append(Decoration(start_x + 80, GROUND_Y, "casa", seed=1))
    decorations.append(Decoration(start_x + 80, GROUND_Y, "porche", seed=2))
    
    # Repartimos las macetas en el espacio extra
    decorations.append(Decoration(start_x + 240, GROUND_Y, "maceta", seed=3))
    decorations.append(Decoration(start_x + 310, GROUND_Y, "maceta", seed=4))
    
    # Movemos la puerta un poco más al final del nuevo tramo
    decorations.append(Decoration(start_x + length - 60, GROUND_Y, "puerta", seed=5))
    
    return cursor

# =========================================================
# ZONA 4: COCINA
# =========================================================

def add_kitchen_ground(platforms, start_x, length):
    platforms.append(Platform(start_x, GROUND_Y, length, GROUND_HEIGHT, "kitchen_floor"))
    return start_x + length


def add_kitchen_counter(platforms, x, y, width):
    platforms.append(Platform(x, y, width, 24, "kitchen_counter"))


def add_kitchen_decorations(decorations, start_x, length, density=100):
    rng = random.Random(start_x + 21)
    kinds = (
        ["plato"] * 2 + ["cubiertos"] * 2 + ["vaso"] * 2
        + ["estante"] * 1 + ["armario"] * 1 + ["botella_deco"] * 2
        + ["utensilio_colgante"] * 1
    )
    x = start_x + 15
    while x < start_x + length - 15:
        kind = rng.choice(kinds)
        decorations.append(Decoration(x, GROUND_Y, kind, seed=x))
        x += density + rng.randint(-20, 20)


def add_knife(enemies, x, patrol_min, patrol_max, assets, speed=2.0):
    enemies.append(Enemy(x, GROUND_Y - 22, 26, 10, patrol_min, patrol_max, speed, assets, "cuchillo"))


def add_pan(enemies, x, patrol_min, patrol_max, assets, speed=1.6):
    enemies.append(Enemy(x, GROUND_Y - 20, 26, 18, patrol_min, patrol_max, speed, assets, "sarten"))


def add_pan_on_platform(enemies, x, platform_y, patrol_min, patrol_max, assets, speed=1.2):
    enemies.append(Enemy(x, platform_y - 18, 26, 18, patrol_min, patrol_max, speed, assets, "sarten"))


def add_ketchup(enemies, x, patrol_min, patrol_max, assets, speed=1.0):
    enemies.append(Enemy(x, GROUND_Y - 28, 20, 28, patrol_min, patrol_max, speed, assets, "botella_ketchup"))


def add_toaster(enemies, x, patrol_min, patrol_max, assets, speed=0.9):
    enemies.append(Enemy(x, GROUND_Y - 20, 26, 20, patrol_min, patrol_max, speed, assets, "tostadora"))


# =========================================================
# ZONA 5: ESTUFA
# =========================================================

def add_stove_ground(platforms, start_x, length):
    platforms.append(Platform(start_x, GROUND_Y, length, GROUND_HEIGHT, "stove"))
    return start_x + length


def add_stove_platform(platforms, x, y, width):
    platforms.append(Platform(x, y, width, 20, "stove"))


def add_fire_spot(effects, x, y, w=30, h=42):
    effects.append(FireSpot(x, y, w, h))


def add_steam_spot(effects, x, y):
    effects.append(SteamSpot(x, y))


# =========================================================
# ZONA 6: JEFE — EL GRAN CHEF
# =========================================================

def add_boss_arena_ground(platforms, start_x, length):
    platforms.append(Platform(start_x, GROUND_Y, length, GROUND_HEIGHT, "arena_floor"))
    return start_x + length


def add_boss_arena_decorations(decorations, start_x, length):
    decorations.append(Decoration(start_x + 30, GROUND_Y, "olla_deco", seed=1))
    decorations.append(Decoration(start_x + length - 60, GROUND_Y, "olla_deco", seed=2))
    decorations.append(Decoration(start_x + length // 2, GROUND_Y, "utensilio_colgante", seed=3))


def create_boss(x, arena_left, arena_right, assets):
    y = GROUND_Y - settings.BOSS_SIZE[1]
    return Boss(x, y, arena_left, arena_right, assets)
