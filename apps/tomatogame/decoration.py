import pygame
import pixel_art


class Decoration:
    """
    Elemento visual del huerto. No colisiona con nadie.
    Usa pixel_art.py para generar el sprite, o una imagen
    real si el usuario la coloca en assets/images/decorations/.
    'y_ground' es la linea de suelo donde se apoya el elemento.
    """

    def __init__(self, x, y_ground, kind, seed=None):
        self.kind = kind
        self.image = pixel_art.get_decoration_sprite(kind, seed if seed is not None else x)
        w, h = self.image.get_size()
        self.rect = pygame.Rect(x, y_ground - h, w, h)

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.rect)
        surface.blit(self.image, (sx, sy))
