import random
import pygame
import pixel_art
import settings


class Collectible:
    def __init__(self, x, y, assets, size=20, message=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.collected = False
        self.frames = pixel_art.get_collectible_frames(size)
        self.frame_index = 0
        self.frame_timer = 0
        # Mensaje que aparece al recogerlo. Si no se especifica uno
        # al crearlo, se elige uno al azar de settings.COLLECTIBLE_MESSAGES.
        self.message = message or random.Random(x).choice(settings.COLLECTIBLE_MESSAGES)

    def update(self):
        if self.collected:
            return
        self.frame_timer += 1
        if self.frame_timer >= 22:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface, camera):
        if self.collected:
            return
        x, y = camera.apply(self.rect)
        surface.blit(self.frames[self.frame_index], (x, y))
