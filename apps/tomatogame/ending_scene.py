import math
import os

import pygame

import pixel_art
import settings
from checkpoint import Checkpoint
from physics import resolve_platform_collisions
from platform_obj import Platform
from camera import Camera

ENDING_WIDTH = settings.SCREEN_WIDTH
ENDING_FLOOR_Y = settings.GROUND_Y


class CelebrationEnemy:
    def __init__(self, x, enemy_type, size, motion, assets=None):
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x, ENDING_FLOOR_Y - size[1], *size)
        self.base_y = self.rect.y
        self.motion = motion
        self.frames = pixel_art.get_enemy_frames(enemy_type, *size)
        self.frame_index = 0
        self.frame_timer = 0
        self.phase = x * 0.07

    def update(self, tick):
        self.frame_timer += 1
        if self.frame_timer >= 14:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        if self.motion == "bounce":
            self.rect.y = self.base_y - int(abs(math.sin(tick * 0.08 + self.phase)) * 10)
        elif self.motion == "sway":
            self.rect.y = self.base_y - int(abs(math.sin(tick * 0.05 + self.phase)) * 4)
        else:
            self.rect.y = self.base_y - int(abs(math.sin(tick * 0.09 + self.phase)) * 7)

    def draw(self, surface, camera):
        x, y = camera.apply(self.rect)
        image = self.frames[self.frame_index]
        surface.blit(image, (x, y))


class Firefly:
    def __init__(self, x, y, phase):
        self.base_x = x
        self.base_y = y
        self.phase = phase

    def pos(self, tick):
        x = self.base_x + math.sin(tick * 0.02 + self.phase) * 22
        y = self.base_y + math.cos(tick * 0.03 + self.phase) * 14
        return x, y

    def draw(self, surface, camera, tick):
        x, y = self.pos(tick)
        sx, sy = camera.apply(pygame.Rect(int(x), int(y), 4, 4))
        glow = 150 + int(abs(math.sin(tick * 0.1 + self.phase)) * 105)
        pygame.draw.circle(surface, (255, 245, glow), (sx + 2, sy + 2), 3)


class Butterfly:
    def __init__(self, x, y, phase, color):
        self.base_x = x
        self.base_y = y
        self.phase = phase
        self.color = color

    def pos(self, tick):
        x = self.base_x + math.sin(tick * 0.015 + self.phase) * 60
        y = self.base_y + math.sin(tick * 0.05 + self.phase * 2) * 16
        return x, y

    def draw(self, surface, camera, tick):
        x, y = self.pos(tick)
        sx, sy = camera.apply(pygame.Rect(int(x), int(y), 12, 10))
        flap = abs(math.sin(tick * 0.3 + self.phase)) * 5 + 3
        pygame.draw.ellipse(surface, self.color, (sx - flap, sy, flap, 8))
        pygame.draw.ellipse(surface, self.color, (sx + 4, sy, flap, 8))
        pygame.draw.line(surface, (70, 50, 40), (sx + 2, sy), (sx + 6, sy + 8), 2)


class EndingDecorations:
    def __init__(self):
        self.items = []
        self._add_many("flor", [45, 110, 175, 240, 700, 770, 840, 910], 0)
        self._add_many("planta_tomate", [80, 210, 730, 875], 0)
        self._add_many("maleza", [35, 145, 250, 680, 805, 925], 0)
        self._add_many("piedra", [275, 675, 900], 0)
        self._add_many("cultivo", [135, 220, 750, 870], 0)

    def _add_many(self, kind, positions, y_offset):
        for index, x in enumerate(positions):
            image = pixel_art.get_decoration_sprite(kind, index)
            self.items.append((x, ENDING_FLOOR_Y - image.get_height() - y_offset, image))

    def draw(self, surface, camera):
        for x, y, image in self.items:
            sx, sy = camera.apply(pygame.Rect(x, y, *image.get_size()))
            surface.blit(image, (sx, sy))


def _draw_garland(surface, camera, tick):
    colors = [(255, 99, 110), (255, 200, 87), (108, 201, 165), (108, 172, 255), (200, 130, 255)]
    y_base = 26
    span = 200
    count = ENDING_WIDTH // span + 2
    prev = None
    for i in range(count):
        x = i * span
        sag = 22 + math.sin(tick * 0.02 + i) * 2
        p1 = camera.apply(pygame.Rect(x, y_base, 1, 1))
        p2 = camera.apply(pygame.Rect(x + span, y_base, 1, 1))
        mid_x = (p1[0] + p2[0]) // 2
        mid_y = int(p1[1] + sag)
        pygame.draw.lines(surface, (90, 65, 50), False, [p1, (mid_x, mid_y), p2], 2)
        for t in (0.25, 0.5, 0.75):
            fx = p1[0] + (p2[0] - p1[0]) * t
            fy = p1[1] + sag * (1 - (t - 0.5) ** 2 * 4)
            color = colors[(i + int(t * 4)) % len(colors)]
            pygame.draw.polygon(
                surface, color,
                [(fx - 6, fy), (fx + 6, fy), (fx, fy + 12)]
            )


def _draw_ending_background(surface, camera, image=None):
    if image is not None:
        surface.blit(image, (0, 0))
        return

    width, height = surface.get_size()

    top_color = (120, 190, 235)
    bottom_color = (200, 232, 250)
    for y in range(0, 300):
        ratio = y / 300
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    sun_center = (width - 140, 80)
    for radius, alpha_color in ((70, (255, 250, 210)), (50, (255, 244, 180)), (32, (255, 236, 140))):
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*alpha_color, 120), (radius, radius), radius)
        surface.blit(glow, (sun_center[0] - radius, sun_center[1] - radius))
    pygame.draw.circle(surface, (255, 246, 190), sun_center, 30)

    for cloud_x, cloud_y, scale in (
        (90, 60, 1.0), (360, 100, 0.8), (640, 55, 1.1),
        (880, 120, 0.7),
    ):
        w, h = int(110 * scale), int(26 * scale)
        pygame.draw.ellipse(surface, (255, 255, 255), (cloud_x, cloud_y, w, h))
        pygame.draw.circle(surface, (255, 255, 255), (cloud_x + int(28 * scale), cloud_y), int(20 * scale))
        pygame.draw.circle(surface, (255, 255, 255), (cloud_x + int(66 * scale), cloud_y - 6), int(26 * scale))

    far_hill_color = (150, 205, 150)
    pygame.draw.polygon(
        surface, far_hill_color,
            [(0, 300), (160, 235), (320, 280), (480, 220), (650, 270),
             (800, 210), (960, 260), (960, 420), (0, 420)]
    )
    near_hill_color = (112, 177, 94)
    pygame.draw.polygon(
        surface, near_hill_color,
        [(0, 340), (180, 275), (360, 320), (540, 260), (700, 315),
         (840, 250), (960, 300), (960, 460), (0, 460)]
    )

    pygame.draw.rect(surface, (95, 170, 78), (0, ENDING_FLOOR_Y - 8, width, 8))

    for x in range(-20, ENDING_WIDTH + 60, 70):
        trunk_h = 90 + (x % 3) * 12
        pygame.draw.rect(surface, (115, 75, 42), (x, 104, 6, trunk_h + 25))
        pygame.draw.circle(surface, (76, 152, 70), (x + 3, 100), 28)
        pygame.draw.circle(surface, (90, 168, 82), (x - 12, 112), 20)
        pygame.draw.circle(surface, (90, 168, 82), (x + 18, 112), 20)

    pygame.draw.rect(surface, (115, 75, 42), (0, 116, ENDING_WIDTH, 5))

    for fence_x in range(-10, ENDING_WIDTH + 40, 90):
        pygame.draw.rect(surface, (222, 198, 160), (fence_x, ENDING_FLOOR_Y - 46, 8, 46))
        pygame.draw.rect(surface, (222, 198, 160), (fence_x + 40, ENDING_FLOOR_Y - 46, 8, 46))
        pygame.draw.rect(surface, (204, 176, 138), (fence_x, ENDING_FLOOR_Y - 38, 56, 8))
        pygame.draw.rect(surface, (204, 176, 138), (fence_x, ENDING_FLOOR_Y - 20, 56, 8))


def _draw_picnic(surface, camera, tick):
    center_x = ENDING_WIDTH // 2
    blanket = pygame.Rect(center_x - 135, ENDING_FLOOR_Y - 62, 270, 56)
    x, y = camera.apply(blanket)
    pygame.draw.rect(surface, (225, 90, 105), (x, y, blanket.width, blanket.height), border_radius=6)
    for stripe_x in range(x + 12, x + blanket.width, 32):
        pygame.draw.rect(surface, (255, 205, 145), (stripe_x, y, 12, blanket.height))
    for stripe_y in range(y + 12, y + blanket.height, 22):
        pygame.draw.rect(surface, (255, 205, 145), (x, stripe_y, blanket.width, 8))

    basket = pygame.Rect(center_x - 55, ENDING_FLOOR_Y - 105, 55, 43)
    bx, by = camera.apply(basket)
    pygame.draw.rect(surface, (174, 108, 52), (bx, by, basket.width, basket.height), border_radius=5)
    pygame.draw.arc(surface, (115, 67, 38), (bx + 8, by - 23, 39, 38), math.pi, math.tau, 5)
    pygame.draw.rect(surface, (230, 165, 72), (bx + 5, by + 8, 45, 5))

    for fruit_x, color in (
        (center_x - 100, (225, 50, 45)),
        (center_x - 8, (245, 180, 45)),
        (center_x + 65, (205, 45, 55)),
    ):
        fx, fy = camera.apply(pygame.Rect(fruit_x, ENDING_FLOOR_Y - 94, 18, 18))
        pygame.draw.circle(surface, color, (fx + 9, fy + 9), 9)
        pygame.draw.rect(surface, (65, 140, 55), (fx + 8, fy - 3, 4, 6))

    for plate_x in (center_x - 130, center_x + 95):
        px, py = camera.apply(pygame.Rect(plate_x, ENDING_FLOOR_Y - 35, 28, 8))
        pygame.draw.ellipse(surface, (245, 245, 235), (px, py, 28, 8))
        pygame.draw.ellipse(surface, (120, 185, 210), (px + 5, py + 2, 18, 4))

    cake = pygame.Rect(center_x - 12, ENDING_FLOOR_Y - 100, 60, 34)
    cx, cy = camera.apply(cake)
    pygame.draw.rect(surface, (250, 225, 235), (cx, cy + 14, cake.width, 20), border_radius=4)
    pygame.draw.rect(surface, (240, 180, 200), (cx, cy + 14, cake.width, 8))
    for candle_i in range(3):
        candle_x = cx + 12 + candle_i * 18
        pygame.draw.rect(surface, (255, 230, 120), (candle_x, cy, 4, 16))
        flame_wave = 2 + int(abs(math.sin(tick * 0.2 + candle_i)) * 2)
        pygame.draw.circle(surface, (255, 170, 60), (candle_x + 2, cy - flame_wave), 3)


def _load_ending_image():
    candidates = (
        os.path.join(settings.ASSETS_DIR, "images", "backgrounds", "ending_image.png"),
        os.path.join(settings.ASSETS_DIR, "images", "backgrounds", "ending_image.jpg"),
        os.path.join(settings.ASSETS_DIR, "ending", "images", "ending_image.png"),
        os.path.join(settings.ASSETS_DIR, "ending", "images", "ending_image.jpg"),
    )
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            image = pygame.image.load(path).convert()
            return pygame.transform.scale(image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except pygame.error:
            return None
    return None


def _fade_to_ending(screen, clock):
    overlay = pygame.Surface(screen.get_size())
    for alpha in range(0, 256, 32):
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(settings.FPS)


def run_ending_scene(screen, clock, assets, audio, player, font, font_checkpoint):
    _fade_to_ending(screen, clock)

    ending_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    camera = Camera(ENDING_WIDTH)
    floor = Platform(0, ENDING_FLOOR_Y, ENDING_WIDTH, settings.GROUND_HEIGHT, "dirt")

    player.rect.topleft = (ENDING_WIDTH // 2 + 130, ENDING_FLOOR_Y - settings.PLAYER_SIZE[1])
    player.spawn_point = player.rect.topleft

    bear = Checkpoint(
        ENDING_WIDTH // 2 - 150,
        ENDING_FLOOR_Y - 32,
        message="",
    )

    bear_dialogue = [
        "Osito: ¡Lo lograste! Nunca subestimes a un tomate.",
        "Tomatito: ...",
        "Osito: Despues de estos 19 años, merecías una celebración.",
        "Osito: Feliz cumpleaños, mi tomate, no podría estar más feliz de vivir esta vida contigo",
        "Osito: Quiero acompañarte en todas las etapas de tu vida, y sean 19 o 40 años, deseo estar a tu lado",
        "Osito: Gracias por ser mi compañero, mi amigo, mi confidente, y mi amor.",
        "Osito: ¡Ahora celebremos! será divertido.",
        "Osito: Y mira... hasta ellos vinieron!",
        "Osito: Gracias por llegar hasta aqui.",
    ]

    decorations = EndingDecorations()

    celebration_enemies = [
        CelebrationEnemy(70, "gusano", (34, 24), "sway"),
        CelebrationEnemy(145, "babosa", (34, 18), "sway"),
        CelebrationEnemy(235, "tomate_podrido", (34, 30), "bounce"),
        CelebrationEnemy(705, "escarabajo", (34, 24), "bounce"),
        CelebrationEnemy(785, "mosca_fruta", (30, 22), "float"),
        CelebrationEnemy(875, "pimenton", (30, 38), "sway"),
        CelebrationEnemy(105, "espina", (34, 24), "bounce"),
        CelebrationEnemy(680, "cuchillo", (34, 22), "sway"),
        CelebrationEnemy(755, "sarten", (38, 25), "bounce"),
        CelebrationEnemy(850, "botella_ketchup", (26, 34), "sway"),
        CelebrationEnemy(620, "tostadora", (32, 24), "bounce"),
    ]

    fireflies = [Firefly(55 + i * 60, 180 + (i % 4) * 30, i * 1.3) for i in range(15)]
    butterflies = [
        Butterfly(150, 220, 0.0, (255, 190, 60)),
        Butterfly(480, 190, 1.4, (255, 120, 150)),
        Butterfly(700, 230, 2.6, (150, 200, 255)),
        Butterfly(850, 200, 3.8, (255, 220, 100)),
        Butterfly(920, 240, 5.0, (200, 150, 255)),
    ]

    ending_image = _load_ending_image()
    audio.play_ending_music()

    tick = 0
    dialogue_index = 0
    dialogue_timer = 0
    dialogue_duration = int(settings.FPS * 4.6)

    running = True
    while running:
        clock.tick(settings.FPS)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                if bear.can_interact(player):
                    if bear.message_visible:
                        if dialogue_index < len(bear_dialogue) - 1:
                            bear.message = bear_dialogue[dialogue_index]
                            dialogue_index += 1
                            dialogue_timer = dialogue_duration
                            audio.play_ending_sfx()
                        else:
                            bear.message_visible = False
                            dialogue_index = 0
                            audio.stop_ending_sfx()
                    else:
                        bear.message = bear_dialogue[dialogue_index]
                        dialogue_index += 1
                        bear.show_message()
                        dialogue_timer = dialogue_duration
                        audio.play_ending_sfx()

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.apply_gravity()
        player.move()
        resolve_platform_collisions(player, [floor])
        player.rect.x = max(24, min(player.rect.x, ENDING_WIDTH - player.rect.width - 24))
        player.update_animation()

        bear.hide_message_if_far(player)
        if bear.message_visible:
            dialogue_timer -= 1
            if dialogue_timer <= 0:
                bear.message_visible = False
                if dialogue_index >= len(bear_dialogue):
                    dialogue_index = 0
        if not bear.message_visible:
            audio.stop_ending_sfx()

        for enemy in celebration_enemies:
            enemy.update(tick)

        _draw_ending_background(ending_surface, camera, ending_image)
        _draw_garland(ending_surface, camera, tick)
        for butterfly in butterflies:
            butterfly.draw(ending_surface, camera, tick)
        decorations.draw(ending_surface, camera)
        _draw_picnic(ending_surface, camera, tick)
        floor.draw(ending_surface, camera)

        for enemy in celebration_enemies:
            enemy.draw(ending_surface, camera)

        bear.draw(ending_surface, camera)
        player.draw(ending_surface, camera)
        bear.draw_message(ending_surface, font_checkpoint, camera)

        for firefly in fireflies:
            firefly.draw(ending_surface, camera, tick)

        shadow = font.render("FELIZ CUMPLEAÑOS TOMATITO", True, (60, 40, 20))
        title = font.render("FELIZ CUMPLEAÑOS TOMATITO", True, (255, 215, 90))
        title_pos = title.get_rect(center=(settings.SCREEN_WIDTH // 2, 92))
        ending_surface.blit(shadow, (title_pos.x + 3, title_pos.y + 3))
        ending_surface.blit(title, title_pos)

        scaled = pygame.transform.scale(ending_surface, screen.get_size())
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

    audio.stop_ending_sfx()
    return False