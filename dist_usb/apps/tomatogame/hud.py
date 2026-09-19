from pydoc import text

import pygame
import pixel_art


def draw_boss_health(surface, boss, font):
    if boss is None or boss.defeated:
        return

    width = 300
    pos = {
        "x": surface.get_width() // 2 - width // 2,
        "y": 48
    }

    ratio = boss.health / boss.max_health
    pixel_art.draw_health_bar(
        surface,
        pos["x"],
        pos["y"],
        width,
        22,
        ratio,
        label="EL GRAN CHEF",
        font=font
    )


def draw_hud(surface, font, collected, total):
    text = f"Recuerdos: {collected} / {total}"
    font = pygame.font.SysFont("couriernew", 18, bold=True)
    text_surface = font.render(text, True, (255, 255, 255))
    pos = { "x": 85, "y": 40
    }
    surface.blit(text_surface, (pos["x"], pos["y"]))


def draw_ending(surface, font_big, font_small, main_text, sub_text):
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 210))
    surface.blit(overlay, (0, 0))

    main_surface = font_big.render(main_text, True, (255, 215, 0))
    main_rect = main_surface.get_rect(
        center=(surface.get_width() // 2, surface.get_height() // 2 - 20)
    )
    surface.blit(main_surface, main_rect)

    sub_surface = font_small.render(sub_text, True, (255, 255, 255))
    sub_rect = sub_surface.get_rect(
        center=(surface.get_width() // 2, surface.get_height() // 2 + 30)
    )
    surface.blit(sub_surface, sub_rect)
