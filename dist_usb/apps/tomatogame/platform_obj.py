import math
import pygame
import pixel_art

# Cada tipo de plataforma mapea a un set de texturas.
# "zone" se usa para elegir la paleta de tierra/plataforma flotante.
_GROUND_ZONE_TYPES = {
    "ground": "huerto",
    "dirt": "huerto",
    "cultivo_ground": "cultivo",
    "peligro_ground": "peligro",
}
_PLATFORM_ZONE_TYPES = {
    "platform": "huerto",
    "dirt_platform": "huerto",
    "cultivo_platform": "cultivo",
    "peligro_platform": "peligro",
}
_INTERIOR_TYPES = {
    "kitchen_floor": "kitchen_floor",
    "kitchen_counter": "kitchen_counter",
    "stove": "stove",
    "arena_floor": "arena",
}


class Platform:
    def __init__(self, x, y, w, h, platform_type="ground"):
        self.rect = pygame.Rect(x, y, w, h)
        self.type = platform_type

    def draw(self, surface, camera):
        x, y = camera.apply(self.rect)
        screen_rect = pygame.Rect(x, y, self.rect.width, self.rect.height)

        if self.type == "goal":
            pixel_art.draw_goal_flag(surface, screen_rect)
            return

        if self.type in _INTERIOR_TYPES:
            tiles = pixel_art.get_interior_tiles(_INTERIOR_TYPES[self.type])
        elif self.type in _PLATFORM_ZONE_TYPES:
            tiles = pixel_art.get_platform_tiles(_PLATFORM_ZONE_TYPES[self.type])
        else:
            zone = _GROUND_ZONE_TYPES.get(self.type, "huerto")
            tiles = pixel_art.get_ground_tiles(zone)

        self._draw_tiled(surface, tiles, x, y, screen_rect)

    def _draw_tiled(self, surface, tiles, x, y, clip_rect):
        tile_w = tiles[0].get_width()
        prev_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        variant_offset = self.rect.x // tile_w
        count = clip_rect.width // tile_w + 2
        for i in range(count):
            tile = tiles[(variant_offset + i) % len(tiles)]
            surface.blit(tile, (x + i * tile_w, y))

        surface.set_clip(prev_clip)


class MovingPlatform(Platform):
    """
    Plataforma que oscila entre dos puntos con movimiento senoidal.
    'axis' es 'x' o 'y'. Guarda delta_x/delta_y de cada frame para
    que main.py pueda arrastrar al jugador si esta parado encima.
    """

    def __init__(self, x, y, w, h, platform_type, axis, distance, speed):
        super().__init__(x, y, w, h, platform_type)
        self.axis = axis
        self.origin = x if axis == "x" else y
        self.distance = distance
        self.speed = speed
        self.t = 0.0
        self.delta_x = 0
        self.delta_y = 0

    def update(self):
        self.t += self.speed
        offset = math.sin(self.t) * self.distance
        prev_x, prev_y = self.rect.x, self.rect.y
        if self.axis == "x":
            self.rect.x = int(self.origin + offset)
        else:
            self.rect.y = int(self.origin + offset)
        self.delta_x = self.rect.x - prev_x
        self.delta_y = self.rect.y - prev_y
