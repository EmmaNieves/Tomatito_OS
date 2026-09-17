import pygame
import settings
import pixel_art


class Checkpoint:
    """
    Bandera de guardado. Al tocarla, el jugador respawnea
    ahi en vez de en el inicio del nivel.
    """

    def __init__(self, x, y, w=40, h=32, message="Checkpoint alcanzado."):
        self.rect = pygame.Rect(x, y, w, h)
        self.activated = False
        self.message = message
        self.message_visible = False
        self.image = pixel_art.get_decoration_sprite("osito", x)
        self.spawn_point = (x, y + h - settings.PLAYER_SIZE[1])

    def check(self, player):
        if not self.activated and player.rect.colliderect(self.rect):
            self.activated = True
            player.spawn_point = self.spawn_point
            return True
        return False

    def can_interact(self, player):
        return player.rect.colliderect(self.rect.inflate(24, 8))

    def show_message(self):
        self.message_visible = True

    def hide_message_if_far(self, player):
        if not self.can_interact(player):
            self.message_visible = False

    def draw(self, surface, camera):
        x, y = camera.apply(self.rect)
        image_x = x + (self.rect.width - self.image.get_width()) // 2
        image_y = y + self.rect.height - self.image.get_height()
        surface.blit(self.image, (image_x, image_y))

    def draw_message(self, surface, font, camera):
        if not self.message_visible:
            return

        box_width = 260
        text_width = box_width - 20
        lines = []
        for paragraph in self.message.splitlines() or [""]:
            words = paragraph.split()
            current_line = ""
            for word in words:
                if font.size(word)[0] > text_width:
                    if current_line:
                        lines.append(current_line)
                        current_line = ""
                    remaining = word
                    while remaining:
                        split_at = len(remaining)
                        while split_at > 1 and font.size(remaining[:split_at])[0] > text_width:
                            split_at -= 1
                        lines.append(remaining[:split_at])
                        remaining = remaining[split_at:]
                    continue

                candidate = f"{current_line} {word}".strip()
                if current_line and font.size(candidate)[0] > text_width:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = candidate
            if current_line:
                lines.append(current_line)
            elif not words:
                lines.append("")

        text_surfaces = [font.render(line, True, (255, 255, 255)) for line in lines]
        line_height = font.get_height()
        box_height = len(text_surfaces) * line_height + 12
        x, y = camera.apply(self.rect)
        box_x = x + self.rect.width // 2 - box_width // 2
        box_y = y - box_height - 8
        box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box, (20, 20, 30, 220), box.get_rect(), border_radius=5)
        pygame.draw.rect(box, (255, 215, 0), box.get_rect(), width=2, border_radius=5)
        surface.blit(box, (box_x, box_y))
        for index, text_surface in enumerate(text_surfaces):
            text_x = box_x + (box_width - text_surface.get_width()) // 2
            text_y = box_y + 6 + index * line_height
            surface.blit(text_surface, (text_x, text_y))
