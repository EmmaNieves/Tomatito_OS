import os
import math
import pygame

import settings

# Extensiones que se prueban, en este orden, al buscar una foto por zona.
PHOTO_EXTENSIONS = (".jpg", ".jpeg", ".png")


class Background:
    """
    Fondo del nivel. Cambia segun la zona en la que esta el jugador.

    Si existe una foto en assets/images/backgrounds/<zona>.jpg (o .png),
    esa foto se usa como fondo completo de la zona, con un parallax leve.
    Si no existe, se usa el fondo dibujado de siempre: zonas exteriores
    (huerto/cultivo/peligro/casa) con cielo en gradiente y capas de
    paralaje; zonas interiores (cocina/estufa/jefe) con pared e interior.
    """

    def __init__(self):
        self._sky_cache = {}
        self._photo_cache = {}

    def _get_photo(self, zone):
        """
        Carga y escala la foto de la zona una sola vez, la guarda en
        cache. Si no hay foto, guarda None para no volver a buscar en
        disco en cada cuadro. Devuelve (superficie, ancho) o None.
        """
        if zone in self._photo_cache:
            return self._photo_cache[zone]

        photo_dir = os.path.join(settings.IMAGES_DIR, "backgrounds")
        path = None
        for ext in PHOTO_EXTENSIONS:
            candidate = os.path.join(photo_dir, zone + ext)
            if os.path.isfile(candidate):
                path = candidate
                break

        if path is None:
            self._photo_cache[zone] = None
            return None

        try:
            img = pygame.image.load(path).convert()
        except pygame.error:
            self._photo_cache[zone] = None
            return None

        # Se escala por altura, para que la foto llene el alto de la
        # pantalla sin deformarse. El ancho queda proporcional, y puede
        # ser mayor que la pantalla: eso permite el efecto de paralaje.
        scale = settings.SCREEN_HEIGHT / img.get_height()
        new_w = max(int(img.get_width() * scale), settings.SCREEN_WIDTH)
        scaled = pygame.transform.smoothscale(img, (new_w, settings.SCREEN_HEIGHT))
        flipped = pygame.transform.flip(scaled, True, False)

        result = {"normal": scaled, "flipped": flipped, "width": new_w}
        self._photo_cache[zone] = result
        return result

    def _draw_photo(self, surface, offset_x, photo, zone_length=None):
        """
        Repite la foto en mosaico horizontal, alternando normal y
        volteada, para que la union entre copias no se note tanto.

        El factor de paralaje se ajusta segun el largo de la zona:
        si la zona es corta, la foto casi no se mueve y nunca llega
        a repetirse. Si la zona es muy larga, se limita a un maximo
        (BASE_FACTOR) para que igual se sienta profundidad.
        """
        width = photo["width"]
        base_factor = 0.3

        if zone_length and zone_length > 0:
            factor = min(base_factor, width / zone_length)
        else:
            factor = base_factor

        world = offset_x * factor
        start_i = int(world // width) - 1
        count = settings.SCREEN_WIDTH // width + 3

        for i in range(start_i, start_i + count):
            x = i * width - world
            tile = photo["normal"] if i % 2 == 0 else photo["flipped"]
            surface.blit(tile, (x, 0))

    def _get_sky(self, zone):
        if zone not in self._sky_cache:
            top, bottom = settings.ZONE_SKY_COLORS.get(zone, settings.ZONE_SKY_COLORS["huerto"])
            self._sky_cache[zone] = self._build_gradient(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, top, bottom)
        return self._sky_cache[zone]

    def _build_gradient(self, w, h, top, bottom):
        surf = pygame.Surface((w, h))
        for y in range(h):
            t = y / h
            color = (
                int(top[0] + (bottom[0] - top[0]) * t),
                int(top[1] + (bottom[1] - top[1]) * t),
                int(top[2] + (bottom[2] - top[2]) * t),
            )
            pygame.draw.line(surf, color, (0, y), (w, y))
        return surf

    def draw(self, surface, camera, zone="huerto", zone_length=None):
        photo = self._get_photo(zone)
        if photo is not None:
            self._draw_photo(surface, camera.offset_x, photo, zone_length)
            return

        if zone in settings.ZONE_INTERIOR:
            self._draw_interior(surface, camera, zone)
        else:
            surface.blit(self._get_sky(zone), (0, 0))
            self._draw_clouds(surface, camera.offset_x)
            self._draw_far_trees(surface, camera.offset_x)
            self._draw_hills(surface, camera.offset_x)
            self._draw_mid_trees(surface, camera.offset_x)
            self._draw_far_fence(surface, camera.offset_x)
            self._draw_near_bushes(surface, camera.offset_x)

    # ---------------------------------------------------
    # INTERIOR: cocina / estufa / arena del jefe
    # ---------------------------------------------------
    def _draw_interior(self, surface, camera, zone):
        colors = settings.ZONE_INTERIOR[zone]
        surface.fill(colors["wall"])

        # linea de zocalo a media altura
        mid_y = settings.SCREEN_HEIGHT - 220
        pygame.draw.rect(surface, colors["wall_dark"], (0, mid_y, settings.SCREEN_WIDTH, 220))

        # paneles de pared lejanos (paralaje suave)
        factor = 0.35
        period = 160
        world = camera.offset_x * factor
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            pygame.draw.rect(surface, colors["trim"], (x, 30, 6, mid_y - 60))

        # estantes/silueta media
        factor2 = 0.55
        period2 = 210
        world2 = camera.offset_x * factor2
        start_i2 = int(world2 // period2) - 1
        count2 = settings.SCREEN_WIDTH // period2 + 3
        for i in range(start_i2, start_i2 + count2):
            x = i * period2 - world2
            y = mid_y - 90
            pygame.draw.rect(surface, colors["wall_dark"], (x, y, 90, 14))
            pygame.draw.rect(surface, colors["trim"], (x, y + 14, 90, 4))

        if zone in ("estufa", "jefe"):
            self._draw_glow(surface, camera.offset_x, colors)

    def _draw_glow(self, surface, offset_x, colors):
        factor = 0.7
        period = 260
        world = offset_x * factor
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        glow_color = (255, 120, 40)
        for i in range(start_i, start_i + count):
            x = i * period - world
            y = settings.SCREEN_HEIGHT - 260
            glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*glow_color, 40), (60, 60), 60)
            surface.blit(glow, (x, y))

    # ---------------------------------------------------
    # CAPA LEJANA: nubes y siluetas de arboles
    # ---------------------------------------------------
    def _draw_clouds(self, surface, offset_x):
        factor = 0.15
        period = 260
        world = offset_x * factor
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            y = 50 + (i % 3) * 25
            self._draw_cloud(surface, x, y)

    def _draw_cloud(self, surface, x, y):
        color = (255, 255, 255)
        pygame.draw.ellipse(surface, color, (x, y, 50, 20))
        pygame.draw.ellipse(surface, color, (x + 15, y - 10, 40, 24))
        pygame.draw.ellipse(surface, color, (x + 35, y, 35, 18))

    def _draw_far_trees(self, surface, offset_x):
        factor = 0.3
        period = 150
        world = offset_x * factor
        color = (110, 150, 165)
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            y = settings.SCREEN_HEIGHT - 230
            trunk_w = 8
            pygame.draw.rect(surface, color, (x + 26, y + 90, trunk_w, 30))
            pygame.draw.polygon(surface, color, [(x, y + 100), (x + 30, y), (x + 60, y + 100)])

    # ---------------------------------------------------
    # CAPA MEDIA: colinas, arboles y cerca lejana
    # ---------------------------------------------------
    def _draw_hills(self, surface, offset_x):
        factor = 0.5
        world = offset_x * factor
        color = (120, 172, 95)
        base_y = settings.SCREEN_HEIGHT - 155
        step = 40
        points = [(0, settings.SCREEN_HEIGHT)]
        for sx in range(-step, settings.SCREEN_WIDTH + step * 2, step):
            wave = math.sin((sx + world) / 90) * 16
            points.append((sx, base_y + wave))
        points.append((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.draw.polygon(surface, color, points)

    def _draw_mid_trees(self, surface, offset_x):
        factor = 0.5
        period = 190
        world = offset_x * factor
        trunk_color = (95, 65, 42)
        leaf_color = (78, 138, 66)
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            y = settings.SCREEN_HEIGHT - 215
            pygame.draw.rect(surface, trunk_color, (x + 14, y + 40, 10, 40))
            pygame.draw.circle(surface, leaf_color, (x + 19, y + 28), 26)
            pygame.draw.circle(surface, leaf_color, (x + 4, y + 40), 18)
            pygame.draw.circle(surface, leaf_color, (x + 34, y + 40), 18)

    def _draw_far_fence(self, surface, offset_x):
        factor = 0.5
        period = 70
        world = offset_x * factor
        color = (150, 118, 88)
        y = settings.SCREEN_HEIGHT - 168
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            pygame.draw.rect(surface, color, (x, y, 6, 26))
        rail_y = y + 8
        pygame.draw.line(surface, color, (0, rail_y), (settings.SCREEN_WIDTH, rail_y), 3)

    # ---------------------------------------------------
    # CAPA CERCANA: arbustos del huerto
    # ---------------------------------------------------
    def _draw_near_bushes(self, surface, offset_x):
        factor = 0.8
        period = 130
        world = offset_x * factor
        dark = (58, 118, 54)
        light = (85, 150, 75)
        y = settings.SCREEN_HEIGHT - 128
        start_i = int(world // period) - 1
        count = settings.SCREEN_WIDTH // period + 3
        for i in range(start_i, start_i + count):
            x = i * period - world
            pygame.draw.ellipse(surface, dark, (x, y, 60, 30))
            pygame.draw.ellipse(surface, light, (x + 10, y - 8, 40, 26))