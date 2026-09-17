import settings
from platform_obj import Platform
from collectible import Collectible
from messages import StoryMessage
from level_sections import (
    add_flat_ground,
    add_gap_with_enemy,
    add_enemy_corridor,
    add_floating_steps,
    add_collectible_row,
    add_dirt_ground,
    add_dirt_platform,
    add_garden_decorations,
    add_crate_decoration,
    add_fence_decoration,
    add_tool_decoration,
    add_worm,
    add_slug,
    add_rotten_tomato,
    add_checkpoint,
    add_cultivo_ground,
    add_cultivo_platform,
    add_moving_platform,
    add_cultivo_decorations,
    add_beetle,
    add_fruit_fly,
    add_peligro_ground,
    add_peligro_decorations,
    add_spike_hazard,
    add_pepper_enemy,
    add_house_entrance,
    add_kitchen_ground,
    add_kitchen_counter,
    add_kitchen_decorations,
    add_knife,
    add_pan,
    add_pan_on_platform,
    add_ketchup,
    add_toaster,
    add_stove_ground,
    add_stove_platform,
    add_fire_spot,
    add_steam_spot,
    add_boss_arena_ground,
    add_boss_arena_decorations,
    create_boss,
)


def build_level(assets):
    """
    Construye el nivel completo, en el orden:
    HUERTO -> CULTIVO -> ZONA PELIGROSA -> ENTRADA A LA CASA
    -> COCINA -> ESTUFA -> JEFE (EL GRAN CHEF).
    Cada zona concatena secciones, sin espacio vacio de por medio.
    Ajusta longitudes y repeticiones aqui para cambiar el ritmo.
    """
    platforms = []
    enemies = []
    collectibles = []
    decorations = []
    checkpoints = []
    effects = []
    story_messages = []
    cursor = 0
    ground_y = settings.GROUND_Y

    # =====================================================
    # ZONA 1: HUERTO — comienzo tranquilo, funciona de tutorial
    # =====================================================
    huerto_start = cursor

    intro_start = cursor
    cursor = add_dirt_ground(platforms, cursor, 420)
    add_garden_decorations(decorations, intro_start, 420, density=80)
    add_fence_decoration(decorations, intro_start + 10, 60)
    add_checkpoint(checkpoints, intro_start + 200, "Hola! soy el osito, bienvenido a esta aventura, este es el huerto, aqui todo es tranquilo, claramente, porque eres un tomate jaja.Espero que te guste el lugar, nos vemos en el camino.")
    story_messages.append(StoryMessage(huerto_start + 40, "Así empezó todo, en un huerto lleno de vida."))

    enemy1_start = cursor
    cursor = add_dirt_ground(platforms, cursor, 320)
    add_garden_decorations(decorations, enemy1_start, 320, density=90)
    add_worm(enemies, enemy1_start + 180, enemy1_start + 30, cursor - 30, assets)
    story_messages.append(StoryMessage(enemy1_start + 20, "Encontrarte fue inesperado, pero llegaste en el momento indicado"))

    plat_start = cursor
    cursor = add_dirt_ground(platforms, cursor, 260)
    add_dirt_platform(platforms, plat_start + 40, ground_y - 90, 90)
    add_dirt_platform(platforms, plat_start + 150, ground_y - 140, 90)
    collectibles.append(Collectible(plat_start + 70, ground_y - 120, assets))
    collectibles.append(Collectible(plat_start + 180, ground_y - 170, assets))
    add_garden_decorations(decorations, plat_start, 260, density=110)

    gap_edge = cursor
    cursor += 90
    gap_after_start = cursor
    cursor = add_dirt_ground(platforms, cursor, 260)
    add_garden_decorations(decorations, gap_after_start, 260, density=90)
    story_messages.append(StoryMessage(gap_edge - 60, "Cada paso se sintio mas ligero contigo cerca."))

    multi_start = cursor
    cursor = add_dirt_ground(platforms, cursor, 480)
    add_garden_decorations(decorations, multi_start, 480, density=120)
    add_worm(enemies, multi_start + 90, multi_start + 20, multi_start + 210, assets)
    add_slug(enemies, multi_start + 270, multi_start + 220, multi_start + 350, assets)
    add_rotten_tomato(enemies, multi_start + 400, multi_start + 360, cursor - 30, assets)
    story_messages.append(StoryMessage(multi_start + 40, "Aprendimos a saltar, esquivar y avanzar juntos."))

    explore_start = cursor
    cursor = add_dirt_ground(platforms, cursor, 380)
    add_crate_decoration(decorations, explore_start + 60, count=2)
    add_crate_decoration(decorations, explore_start + 260, count=1)
    add_tool_decoration(decorations, explore_start + 320, kind="regadera")
    add_tool_decoration(decorations, explore_start + 200, kind="herramienta")
    add_garden_decorations(decorations, explore_start, 380, density=130)

    secret_gap_edge = cursor
    cursor += 110
    secret_after_start = cursor
    cursor = add_dirt_ground(platforms, cursor, 300)
    add_dirt_platform(platforms, secret_gap_edge + 15, ground_y - 120, 80)
    collectibles.append(Collectible(secret_gap_edge + 45, ground_y - 150, assets))
    add_garden_decorations(decorations, secret_after_start, 300, density=110)
    story_messages.append(StoryMessage(secret_after_start + 20, "Hay recuerdos escondidos si sabes donde mirar."))

    final_start = cursor
    cursor = add_dirt_ground(platforms, cursor, 260)
    add_garden_decorations(decorations, final_start, 260, density=90)
    add_checkpoint(checkpoints, final_start + 130, "Ten cuidado al pasar por el huerto, hay bichos que pueden hacerte daño.")
    story_messages.append(StoryMessage(final_start + 30, "Así empezó nuestra vida juntos"))

    huerto_end = cursor

    # =====================================================
    # ZONA 2: CULTIVO — plantas altas, puentes, plataformas moviles
    # =====================================================
    cultivo_start = cursor
    story_messages.append(StoryMessage(cultivo_start + 30, "Pasamos a un cultivo, donde todo crecia mas alto que nosotros."))

    for i in range(4):
        enemy_type = "escarabajo" if i % 2 == 0 else "mosca_fruta"
        cursor = add_gap_with_enemy(
            platforms, enemies, cursor,
            before_len=220, gap_width=80 + i * 10, after_len=260,
            enemy_speed=1.5 + i * 0.25, assets=assets,
            ground_type="cultivo_ground", enemy_type=enemy_type,
        )
        add_cultivo_decorations(decorations, cursor - 480, 480, density=110)
        if i % 2 == 0:
            cursor = add_collectible_row(
                collectibles, cursor - 200, count=2, spacing=90,
                height_above_ground=130, assets=assets,
            )

    bridge_start = cursor
    cursor = add_cultivo_ground(platforms, cursor, 260)
    add_cultivo_decorations(decorations, bridge_start, 260, density=100)
    add_moving_platform(platforms, bridge_start + 100, ground_y - 90, 90, axis="y", distance=55, speed=0.035)
    add_moving_platform(platforms, bridge_start + 260, ground_y - 130, 90, axis="x", distance=70, speed=0.03)
    collectibles.append(Collectible(bridge_start + 100, ground_y - 130, assets))
    story_messages.append(StoryMessage(bridge_start + 30, "Aprendimos a movernos juntos y ser más fuerte que los cambios"))

    cursor = add_enemy_corridor(
        platforms, enemies, cursor,
        length=600, enemy_count=3, base_speed=1.8, assets=assets,
        ground_type="cultivo_ground", enemy_type="babosa",
    )
    add_cultivo_decorations(decorations, cursor - 600, 600, density=130)
    add_fruit_fly(enemies, cursor - 300, cursor - 500, cursor - 100, assets)

    cursor = add_flat_ground(platforms, cursor, 200, ground_type="cultivo_ground")
    add_checkpoint(checkpoints, cursor - 100, "Hola de nuevo, me alegra volver a verte, estás a punto de entrar al bosque de espinas, por momentos se hace más difícil, sé que lo lograrás.")
    cultivo_end = cursor

    # =====================================================
    # ZONA 3: PELIGROSA — transicion oscura hacia la casa
    # =====================================================
    peligro_start = cursor
    story_messages.append(StoryMessage(peligro_start + 30, "El camino se volvio oscuro y afilado."))

    danger_start = cursor
    cursor = add_peligro_ground(platforms, cursor, 300)
    add_peligro_decorations(decorations, danger_start, 300, density=110)
    add_spike_hazard(enemies, danger_start + 150)
    add_spike_hazard(enemies, danger_start + 220)

    for i in range(3):
        cursor = add_gap_with_enemy(
            platforms, enemies, cursor,
            before_len=200, gap_width=110 + i * 15, after_len=260,
            enemy_speed=1.6 + i * 0.3, assets=assets,
            ground_type="peligro_ground", enemy_type="pimenton",
        )
        add_peligro_decorations(decorations, cursor - 460, 460, density=120)
        add_spike_hazard(enemies, cursor - 200)

    pepper_start = cursor
    cursor = add_peligro_ground(platforms, cursor, 320)
    add_peligro_decorations(decorations, pepper_start, 320, density=100)
    add_pepper_enemy(enemies, pepper_start + 120, pepper_start + 40, pepper_start + 260, assets)
    add_pepper_enemy(enemies, pepper_start + 220, pepper_start + 160, cursor - 30, assets)
    story_messages.append(StoryMessage(pepper_start + 30, "Por momentos nos sentimos atrapados, pero seguimos adelante."))

    cursor = add_flat_ground(platforms, cursor, 180, ground_type="peligro_ground")
    peligro_end = cursor

    # =====================================================
    # ENTRADA A LA CASA — transicion visual, tramo tranquilo
    # =====================================================
    casa_start = cursor
    # ¡AQUÍ ESTÁ EL CAMBIO A 380!
    cursor = add_house_entrance(platforms, decorations, cursor, length=380)
    add_checkpoint(checkpoints, casa_start + 130, "¿No adoras estos momentos de calma en los que podemos solo estar en nuestro hogar? El que formamos juntos, es hermoso estar en tus brazos, tenerte cerca, y que todo lo demás desaparezca. Digo, auuuu, soy un osito. ¿Cocinamos?;)")
    story_messages.append(StoryMessage(casa_start + 20, "La puerta de la cocina nos esperaba."))
    casa_end = cursor

    # =====================================================
    # ZONA 4: COCINA — el protagonista es pequeno, todo es enorme
    # =====================================================
    cocina_start = cursor
    story_messages.append(StoryMessage(cocina_start + 30, "Todo aqui era gigante, hasta los platos, parece un ramen hecho por nosotros."))

    kitchen_intro_start = cursor
    cursor = add_kitchen_ground(platforms, cursor, 340)
    add_kitchen_decorations(decorations, kitchen_intro_start, 340, density=110)
    add_knife(enemies, kitchen_intro_start + 200, kitchen_intro_start + 40, cursor - 30, assets)

    for i in range(3):
        enemy_type = ["sarten", "botella_ketchup", "tostadora"][i % 3]
        cursor = add_gap_with_enemy(
            platforms, enemies, cursor,
            before_len=210, gap_width=90 + i * 10, after_len=270,
            enemy_speed=1.4 + i * 0.3, assets=assets,
            ground_type="kitchen_floor", enemy_type=enemy_type,
        )
        add_kitchen_decorations(decorations, cursor - 480, 480, density=120)

    counter_start = cursor
    cursor = add_kitchen_ground(platforms, cursor, 420)
    add_kitchen_counter(platforms, counter_start + 40, ground_y - 100, 110)
    add_kitchen_counter(platforms, counter_start + 220, ground_y - 150, 110)
    collectibles.append(Collectible(counter_start + 75, ground_y - 130, assets))
    collectibles.append(Collectible(counter_start + 255, ground_y - 180, assets))
    add_knife(enemies, counter_start + 340, counter_start + 260, cursor - 30, assets, speed=1.8)
    add_kitchen_decorations(decorations, counter_start, 420, density=130)

    cursor = add_enemy_corridor(
        platforms, enemies, cursor,
        length=500, enemy_count=2, base_speed=1.6, assets=assets,
        ground_type="kitchen_floor", enemy_type="tostadora",
    )
    add_kitchen_decorations(decorations, cursor - 500, 500, density=130)
    add_checkpoint(checkpoints, cursor - 60, "Esto se puso más difícil de lo que creí, ¿qué está pasando en esa cocina? ¿por qué tantas cosas vuelan? en fin, no sé de que hablo, soy un oso que habla, mejor vamos a la estufa.")
    cocina_end = cursor

    # =====================================================
    # ZONA 5: ESTUFA — la parte mas peligrosa antes del jefe
    # =====================================================
    estufa_start = cursor
    story_messages.append(StoryMessage(estufa_start + 30, "Ya casi llegamos, un poco mas."))

    stove_intro = cursor
    cursor = add_stove_ground(platforms, cursor, 260)
    add_fire_spot(effects, stove_intro + 60, ground_y - 40)
    add_fire_spot(effects, stove_intro + 160, ground_y - 40)
    add_steam_spot(effects, stove_intro + 110, ground_y - 60)
    add_pan(enemies, stove_intro + 200, stove_intro + 40, cursor - 30, assets, speed=2.0)

    for i in range(2):
        cursor = add_gap_with_enemy(
            platforms, enemies, cursor,
            before_len=190, gap_width=120 + i * 20, after_len=240,
            enemy_speed=2.0 + i * 0.3, assets=assets,
            ground_type="stove", enemy_type="sarten",
        )
        add_fire_spot(effects, cursor - 380, ground_y - 40)
        add_steam_spot(effects, cursor - 300, ground_y - 55)

    cursor = add_floating_steps(
        platforms, collectibles, cursor - 35,
        steps=5, step_gap=125, height_start=ground_y - 85,
        height_step=-14, assets=assets, platform_type="stove",
    )
    stair_start = cursor - 35
    stair_middle_x = stair_start + 375
    stair_middle_y = ground_y - 85 - (3 * 14)
    add_pan_on_platform(
        enemies, stair_middle_x + 30, stair_middle_y,
        stair_middle_x + 10, stair_middle_x + 74, assets,
    )
    story_messages.append(StoryMessage(cursor - 400, "El fuego no nos detuvo nunca."))

    knife_start = cursor
    cursor = add_stove_ground(platforms, cursor, 320)
    add_fire_spot(effects, knife_start + 80, ground_y - 40)
    add_fire_spot(effects, knife_start + 220, ground_y - 40)
    add_pan(
        enemies, knife_start + 250,
        knife_start + 20, cursor - 20, assets, speed=2.2,
    )
    add_knife(enemies, knife_start + 150, knife_start + 30, cursor - 30, assets, speed=2.4)
    add_checkpoint(checkpoints, cursor - 80, "JAJAJA, eso si fue intenso, pero lo paasaste, ahora, ten cuidado, el chef está molesto porque se comieron su ramen y ahora está buscando tomates para una salsa, ¡no dejes que te atrape!.")
    estufa_end = cursor

    # =====================================================
    # ZONA 6: JEFE — EL GRAN CHEF
    # =====================================================
    jefe_start = cursor
    story_messages.append(StoryMessage(jefe_start + 20, "¡¡¡¡¡¡¡SÍ CHEF!!!!!!!!"))

    arena_length = 680
    cursor = add_boss_arena_ground(platforms, cursor, arena_length)
    add_boss_arena_decorations(decorations, jefe_start, arena_length)
    add_fire_spot(effects, jefe_start + 40, ground_y - 40)
    add_fire_spot(effects, cursor - 70, ground_y - 40)

    boss = create_boss(jefe_start + arena_length // 2, jefe_start + 40, cursor - 40, assets)

    goal_x = 140 if settings.DEBUG_ENDING_AT_START else cursor + 80
    goal = Platform(goal_x, ground_y - 60, 40, 60, "goal")
    level_width = cursor + 300

    zones = [
        {"name": "huerto", "start": huerto_start, "end": huerto_end},
        {"name": "cultivo", "start": cultivo_start, "end": cultivo_end},
        {"name": "peligro", "start": peligro_start, "end": peligro_end},
        {"name": "casa", "start": casa_start, "end": casa_end},
        {"name": "cocina", "start": cocina_start, "end": cocina_end},
        {"name": "estufa", "start": estufa_start, "end": estufa_end},
        {"name": "jefe", "start": jefe_start, "end": level_width},
    ]

    return {
        "platforms": platforms,
        "enemies": enemies,
        "collectibles": collectibles,
        "decorations": decorations,
        "checkpoints": checkpoints,
        "effects": effects,
        "messages": story_messages,
        "goal": goal,
        "boss": boss,
        "boss_arena_start": jefe_start,
        "width": level_width,
        "zones": zones,
        "spawn": (50, 300),
    }