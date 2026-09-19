import pygame
import pixel_art


class Enemy:
    def __init__(self, x, y, w, h, range_min, range_max, speed, assets, enemy_type="generico"):
        self.rect = pygame.Rect(x, y, w, h)
        self.vel_x = speed
        self.range_min = range_min
        self.range_max = range_max
        self.enemy_type = enemy_type

        self.frames = pixel_art.get_enemy_frames(enemy_type, w, h)
        self.frame_index = 0
        self.frame_timer = 0
        self.facing = 1 if speed >= 0 else -1

    def update(self):
        self.rect.x += int(self.vel_x)
        if self.rect.left < self.range_min or self.rect.right > self.range_max:
            self.vel_x *= -1
        self.facing = 1 if self.vel_x >= 0 else -1

        self.frame_timer += 1
        if self.frame_timer >= 18:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface, camera):
        x, y = camera.apply(self.rect)
        image = self.frames[self.frame_index]
        if self.facing == -1:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, (x, y))
