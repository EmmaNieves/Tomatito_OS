import sys
import pygame

import settings
from assets_manager import AssetManager
from audio_manager import AudioManager
from player import Player
from camera import Camera
from physics import resolve_platform_collisions
from messages import MessageManager
from hud import draw_hud, draw_ending, draw_boss_health
from level_builder import build_level
from background import Background
from platform_obj import MovingPlatform
from start_screen import run_start_screen
from effects import MemoryFrame
from ending_scene import run_ending_scene


def current_zone(zones, x):
    for zone in zones:
        if zone["start"] <= x < zone["end"]:
            return zone["name"]
    return zones[-1]["name"] if zones else "huerto"


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()

    # Lienzo logico donde se dibuja todo el juego. Se escala a la
    # ventana real al final de cada cuadro (ver settings.RENDER_SCALE).
    game_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    font = pygame.font.SysFont("couriernew", 24, bold=True)
    font_big = pygame.font.SysFont("couriernew", 44, bold=True)
    font_small = pygame.font.SysFont("couriernew", 20)
    font_boss = pygame.font.SysFont("couriernew", 18, bold=True)
    font_checkpoint = pygame.font.SysFont("couriernew", 14, bold=True)

    assets = AssetManager()
    audio = AudioManager()

    if not run_start_screen(screen, clock, audio):
        pygame.quit()
        sys.exit()

    level = build_level(assets)
    player = Player(level["spawn"][0], level["spawn"][1], assets)
    camera = Camera(level["width"])
    message_manager = MessageManager(level["messages"])
    background = Background()
    boss = level["boss"]

    moving_platforms = [p for p in level["platforms"] if isinstance(p, MovingPlatform)]
    memory_frames = []

    # Largo de cada zona, para que el fondo con foto ajuste su
    # velocidad de paralaje y nunca se repita dentro de la misma zona.
    zone_lengths = {z["name"]: z["end"] - z["start"] for z in level["zones"]}

    current_music_key = None

    def kill_player():
        player.respawn()
        if boss is not None:
            boss.reset_after_player_death()
        audio.play_sfx(settings.SFX_FILES["morir"], assets)

    collected_count = 0
    game_won = False
    tick = 0

    running = True
    while running:
        clock.tick(settings.FPS)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                for checkpoint in level["checkpoints"]:
                    if checkpoint.can_interact(player):
                        checkpoint.show_message()
                        audio.play_sfx(settings.SFX_FILES["checkpoint"], assets)

        keys = pygame.key.get_pressed()

        if not game_won:
            for plat in moving_platforms:
                plat.update()

            player.handle_input(keys)
            if player.just_jumped:
                audio.play_sfx(settings.SFX_FILES["saltar"], assets, volume=0.5)

            player.apply_gravity()
            player.move()

            prev_vel_y = player.vel_y
            resolve_platform_collisions(player, level["platforms"])

            # Arrastrar al jugador si quedo parado sobre una plataforma movil.
            if player.on_ground:
                for plat in moving_platforms:
                    standing = (
                        abs(player.rect.bottom - plat.rect.top) <= 2
                        and player.rect.right > plat.rect.left
                        and player.rect.left < plat.rect.right
                    )
                    if standing:
                        player.rect.x += plat.delta_x
                        player.rect.y += plat.delta_y

            player.update_animation()

            if player.rect.top > settings.SCREEN_HEIGHT + 400:
                kill_player()

            for enemy in level["enemies"]:
                enemy.update()
                if player.rect.colliderect(enemy.rect):
                    kill_player()

            for item in level["collectibles"]:
                if not item.collected and player.rect.colliderect(item.rect):
                    item.collected = True
                    collected_count += 1
                    audio.play_sfx(settings.SFX_FILES["recoger"], assets)
                    image_index = collected_count
                    x = 30 + (image_index * 97) % (settings.SCREEN_WIDTH - 200)
                    y = 20 + (image_index * 61) % (settings.SCREEN_HEIGHT - 180)
                    memory_frames.append(
                        MemoryFrame(
                            x,
                            y,
                            image_name=f"imagen_recuerdo_{image_index}.png",
                            size=(150, 110),
                            life=240,
                        )
                    )
                    memory_frames[-1].x = 30 + __import__("random").randint(0, settings.SCREEN_WIDTH - 220)
                    memory_frames[-1].y = 20 + __import__("random").randint(0, settings.SCREEN_HEIGHT - 180)
                    message_manager.show(item.message)

            for checkpoint in level["checkpoints"]:
                checkpoint.check(player)
                checkpoint.hide_message_if_far(player)

            if boss is not None and not boss.defeated:
                boss.update(player.rect)

                if player.rect.colliderect(boss.rect):
                    prev_bottom = player.rect.bottom - player.vel_y
                    if prev_vel_y >= 0 and prev_bottom <= boss.rect.top + 10:
                        if boss.can_take_hit():
                            boss.take_hit()
                            player.vel_y = settings.JUMP_FORCE * 0.75
                            player.vel_x = -10 if player.rect.centerx < boss.rect.centerx else 10
                            audio.play_sfx(settings.SFX_FILES["golpe_jefe"], assets)
                    else:
                        kill_player()

                for proj in boss.projectiles:
                    if proj.alive and player.rect.colliderect(proj.rect):
                        proj.alive = False
                        kill_player()

            message_manager.update(player.rect.x)
            camera.update(player.rect)

            boss_done = settings.DEBUG_ENDING_AT_START or boss is None or boss.defeated
            if boss_done and player.rect.colliderect(level["goal"].rect):
                if not game_won:
                    audio.play_sfx(settings.SFX_FILES["final"], assets)
                    run_ending_scene(
                        screen,
                        clock,
                        assets,
                        audio,
                        player,
                        font,
                        font_checkpoint,
                    )
                    running = False
                game_won = True

        for item in level["collectibles"]:
            item.update()

        zone = current_zone(level["zones"], player.rect.centerx)
        zone_name = zone["name"] if isinstance(zone, dict) else zone
        if zone_name in settings.MUSIC_FILES and zone_name != current_music_key:
            audio.play_music(settings.MUSIC_FILES[zone_name])
            current_music_key = zone_name

        background.draw(game_surface, camera, zone_name, zone_lengths.get(zone_name))

        for deco in level["decorations"]:
            deco.draw(game_surface, camera)

        for plat in level["platforms"]:
            plat.draw(game_surface, camera)

        for effect in level["effects"]:
            effect.draw(game_surface, camera, tick)

        for frame in memory_frames:
            frame.update()
            frame.draw(game_surface, camera)
        memory_frames = [frame for frame in memory_frames if frame.life > 0]

        for checkpoint in level["checkpoints"]:
            checkpoint.draw(game_surface, camera)

        level["goal"].draw(game_surface, camera)

        for item in level["collectibles"]:
            item.draw(game_surface, camera)

        for enemy in level["enemies"]:
            enemy.draw(game_surface, camera)

        if boss is not None:
            boss.draw(game_surface, camera)

        player.draw(game_surface, camera)

        for checkpoint in level["checkpoints"]:
            checkpoint.draw_message(game_surface, font_checkpoint, camera)

        draw_hud(game_surface, font, collected_count, len(level["collectibles"]))
        boss_in_final_area = (
            boss is not None and not boss.defeated and player.rect.centerx >= level["boss_arena_start"]
        )
        if boss_in_final_area:
            draw_boss_health(game_surface, boss, font_boss)
        message_manager.draw(game_surface, font)

        if game_won:
            draw_ending(
                game_surface, font_big, font_small,
                "Feliz cumpleanos",
                "Gracias por cada paso de esta aventura juntos.",
            )

        scaled = pygame.transform.scale(game_surface, (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()