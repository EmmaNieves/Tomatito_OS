import pygame
import settings
import pixel_art


class Projectile:
    """Sarten que el jefe lanza hacia el jugador. Vuela en linea recta."""

    def __init__(self, x, y, direction):
        w, h = settings.PROJECTILE_SIZE
        self.rect = pygame.Rect(x, y, w, h)
        self.vel_x = settings.PROJECTILE_SPEED * direction
        self.image = pixel_art.get_projectile_frame(w)
        self.alive = True

    def update(self, level_left, level_right):
        self.rect.x += int(self.vel_x)
        if self.rect.right < level_left or self.rect.left > level_right:
            self.alive = False

    def draw(self, surface, camera):
        if not self.alive:
            return
        x, y = camera.apply(self.rect)
        surface.blit(self.image, (x, y))


class Boss:
    """
    EL GRAN CHEF. Patrulla la arena y lanza sartenes.
    El jugador le quita vida saltandole encima (estilo Mario).
    Tocarlo de costado hace que el jugador respawnee.
    """

    def __init__(self, x, y, arena_left, arena_right, assets):
        w, h = settings.BOSS_SIZE
        self.rect = pygame.Rect(x, y, w, h)
        self.arena_left = arena_left
        self.arena_right = arena_right
        self.vel_x = settings.BOSS_SPEED
        self.health = settings.BOSS_HEALTH
        self.max_health = settings.BOSS_HEALTH
        self.defeated = False
        self.hit_flash = 0
        self.hit_cooldown = 0
        self.throw_timer = settings.BOSS_THROW_COOLDOWN

        self.frames = pixel_art.get_boss_frames(w, h)
        self.frame_index = 0
        self.frame_timer = 0
        self.facing = 1

        self.projectiles = []

    def update(self, player_rect):
        if self.defeated:
            return

        self.rect.x += int(self.vel_x)
        if self.rect.left < self.arena_left or self.rect.right > self.arena_right:
            self.vel_x *= -1
        self.facing = 1 if self.vel_x >= 0 else -1

        self.frame_timer += 1
        if self.frame_timer >= 20:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        player_dx = player_rect.centerx - self.rect.centerx
        player_dy = abs(player_rect.centery - self.rect.centery)
        player_detected = (
            abs(player_dx) <= settings.BOSS_DETECTION_RANGE
            and player_dy <= settings.SCREEN_HEIGHT // 2
        )
        self.throw_timer -= 1
        if player_detected and self.throw_timer <= 0:
            self.throw_timer = settings.BOSS_THROW_COOLDOWN
            direction = 1 if player_dx >= 0 else -1
            self.projectiles.append(
                Projectile(self.rect.centerx, self.rect.centery, direction)
            )

        for proj in self.projectiles:
            proj.update(self.arena_left - 200, self.arena_right + 200)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def take_hit(self):
        if self.hit_cooldown > 0:
            return False
        self.health -= 1
        self.hit_flash = 12
        self.hit_cooldown = settings.BOSS_HIT_COOLDOWN
        if self.health <= 0:
            self.defeated = True
        return True

    def can_take_hit(self):
        return self.hit_cooldown <= 0 and not self.defeated

    def reset_after_player_death(self):
        self.health = self.max_health
        self.defeated = False
        self.hit_flash = 0
        self.hit_cooldown = 0
        self.throw_timer = settings.BOSS_THROW_COOLDOWN
        self.projectiles.clear()

    def draw(self, surface, camera):
        if self.defeated:
            return
        x, y = camera.apply(self.rect)
        image = self.frames[self.frame_index]
        if self.facing == -1:
            image = pygame.transform.flip(image, True, False)
        if self.hit_flash > 0 and self.hit_flash % 4 < 2:
            flash = image.copy()
            flash.fill((255, 255, 255, 120), special_flags=pygame.BLEND_RGBA_ADD)
            image = flash
        surface.blit(image, (x, y))
        for proj in self.projectiles:
            proj.draw(surface, camera)
