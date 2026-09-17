import os
import pygame

import settings
from background import Background


def _load_custom_background():
    """
    Si existe assets/images/ui/start_screen.png, se usa tal cual
    como fondo completo de la pantalla de inicio (reemplaza el
    fondo generado). Ponla ahi cuando tengas tu propio diseno.
    """
    path = os.path.join(settings.IMAGES_DIR, "ui", "start_screen.png")
    if os.path.isfile(path):
        try:
            img = pygame.image.load(path).convert()
            return pygame.transform.scale(img, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except pygame.error:
            return None
    return None


class _StaticCamera:
    offset_x = 0


def run_start_screen(screen, clock, audio):
    """
    Pantalla de inicio. Usa el mismo motor visual del juego
    (mismo lienzo logico y el mismo Background), asi que reemplazar
    la imagen de assets/images/ui/start_screen.png alcanza para
    tener tu propio diseno, sin tocar este archivo.

    Devuelve True si el jugador quiere empezar, False si cerro
    la ventana.
    """
    virtual = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    background = Background()
    custom_bg = _load_custom_background()
    camera = _StaticCamera()

    font_title = pygame.font.SysFont("couriernew", 46, bold=True)
    font_sub = pygame.font.SysFont("couriernew", 20)
    font_controls = pygame.font.SysFont("couriernew", 16)

    audio.play_music(settings.MUSIC_FILES["menu"], volume=0.4)

    blink_timer = 0
    show_prompt = True

    while True:
        clock.tick(settings.FPS)
        blink_timer += 1
        if blink_timer >= 30:
            blink_timer = 0
            show_prompt = not show_prompt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return True

        if custom_bg:
            virtual.blit(custom_bg, (0, 0))
        else:
            background.draw(virtual, camera, "huerto")

        title_surf = font_title.render(settings.TITLE, True, (255, 255, 255))
        shadow_surf = font_title.render(settings.TITLE, True, (30, 20, 15))
        center_x = settings.SCREEN_WIDTH // 2
        center_y = settings.SCREEN_HEIGHT // 2 - 40
        virtual.blit(shadow_surf, shadow_surf.get_rect(center=(center_x + 3, center_y + 3)))
        virtual.blit(title_surf, title_surf.get_rect(center=(center_x, center_y)))

        if show_prompt:
            sub_surf = font_sub.render("Presiona ENTER o ESPACIO para jugar", True, (255, 255, 255))
            virtual.blit(sub_surf, sub_surf.get_rect(center=(center_x, center_y + 70)))

        controls = [
            "Controles",
            "W / ARRIBA: saltar",
            "A / IZQUIERDA: ir a la izquierda",
            "D / DERECHA: ir a la derecha",
            "S / ABAJO: agacharse",
            "ESPACIO: saltar    T: hablar con el osito",
        ]
        for index, control_text in enumerate(controls):
            control_surface = font_controls.render(control_text, True, (255, 255, 255))
            virtual.blit(
                control_surface,
                control_surface.get_rect(center=(center_x, center_y + 106 + index * 20)),
            )

        scaled = pygame.transform.scale(virtual, (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
