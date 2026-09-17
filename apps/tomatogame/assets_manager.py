import os
import pygame


class AssetManager:
    """
    Carga imagenes y sonidos desde rutas relativas.
    Si un recurso no existe todavia, genera un placeholder
    de color solido para que el juego siga siendo jugable.
    Reemplaza los archivos en assets/ y todo se actualiza solo.
    """

    def __init__(self):
        self.images = {}
        self.sounds = {}

    def load_image(self, path, fallback_color, size):
        key = (path, size)
        if key in self.images:
            return self.images[key]

        surface = None
        if path and os.path.isfile(path):
            try:
                surface = pygame.image.load(path).convert_alpha()
                surface = pygame.transform.scale(surface, size)
            except pygame.error:
                surface = None

        if surface is None:
            surface = pygame.Surface(size, pygame.SRCALPHA)
            surface.fill(fallback_color)

        self.images[key] = surface
        return surface

    def load_sound(self, path):
        if path in self.sounds:
            return self.sounds[path]

        sound = None
        if path and os.path.isfile(path):
            try:
                sound = pygame.mixer.Sound(path)
            except pygame.error:
                sound = None

        self.sounds[path] = sound
        return sound
