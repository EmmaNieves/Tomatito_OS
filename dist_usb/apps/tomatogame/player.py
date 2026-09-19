import pygame
import settings
import pixel_art


class Player:
    def __init__(self, x, y, assets):
        self.rect = pygame.Rect(x, y, *settings.PLAYER_SIZE)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing = 1
        self.spawn_point = (x, y)
        self.just_jumped = False

        self.frames = pixel_art.get_player_frames(*settings.PLAYER_SIZE)
        self.frame_index = 0
        self.frame_timer = 0

    def handle_input(self, keys):
        self.just_jumped = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -settings.MOVE_SPEED
            self.facing = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = settings.MOVE_SPEED
            self.facing = 1
        else:
            self.vel_x *= settings.FRICTION

        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        if jump_pressed and self.on_ground:
            self.vel_y = settings.JUMP_FORCE
            self.on_ground = False
            self.just_jumped = True

    def apply_gravity(self):
        self.vel_y += settings.GRAVITY
        if self.vel_y > settings.MAX_FALL_SPEED:
            self.vel_y = settings.MAX_FALL_SPEED

    def move(self):
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

    def respawn(self):
        self.rect.topleft = self.spawn_point
        self.vel_x = 0
        self.vel_y = 0

    def update_animation(self):
        if abs(self.vel_x) > 0.5 and self.on_ground:
            self.frame_timer += 1
            if self.frame_timer >= 8:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.frame_index = 0
            self.frame_timer = 0

    def draw(self, surface, camera):
        x, y = camera.apply(self.rect)
        image = self.frames[self.frame_index]
        if self.facing == 1:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, (x, y))
