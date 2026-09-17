import pygame


class StoryMessage:
    def __init__(self, trigger_x, text):
        self.trigger_x = trigger_x
        self.text = text
        self.triggered = False


class MessageManager:
    def __init__(self, story_messages, duration_frames=200):
        self.messages = story_messages
        self.duration = duration_frames
        self.timer = 0
        self.current_text = ""

    def update(self, player_x):
        for msg in self.messages:
            if not msg.triggered and player_x >= msg.trigger_x:
                msg.triggered = True
                self.current_text = msg.text
                self.timer = self.duration

        if self.timer > 0:
            self.timer -= 1

    def show(self, text, duration_frames=90):
        """Muestra un mensaje inmediato, sin esperar a una posicion
        del mapa. Usado por ejemplo al recoger un coleccionable."""
        self.current_text = text
        self.timer = duration_frames

    def draw(self, surface, font):
        if self.timer <= 0:
            return

        max_text_width = surface.get_width() - 60
        words = self.current_text.split()
        font_size = 18
        while (
            words
            and max(pygame.font.SysFont("couriernew", font_size, bold=True).size(word)[0] for word in words)
            > max_text_width
            and font_size > 10
        ):
            font_size -= 1
        small_font = pygame.font.SysFont("couriernew", font_size, bold=True)
        lines = []
        current_line = ""
        for word in words:
            candidate = f"{current_line} {word}".strip()
            if current_line and small_font.size(candidate)[0] > max_text_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate
        if current_line:
            lines.append(current_line)

        text_surfaces = [
            small_font.render(line, True, (255, 255, 255))
            for line in lines
        ]
        box_width = min(
            max(surface.get_width() - 20, 1),
            max(text_surface.get_width() for text_surface in text_surfaces) + 40,
        )
        box_height = len(text_surfaces) * small_font.get_height() + 20
        box_x = surface.get_width() // 2 - box_width // 2
        box_y = surface.get_height() - box_height - 35

        box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box, (20, 20, 30, 220), box.get_rect(), border_radius=8)
        pygame.draw.rect(box, (255, 215, 0), box.get_rect(), width=3, border_radius=8)
        surface.blit(box, (box_x, box_y))
        for index, text_surface in enumerate(text_surfaces):
            text_x = box_x + (box_width - text_surface.get_width()) // 2
            text_y = box_y + 10 + index * small_font.get_height()
            surface.blit(text_surface, (text_x, text_y))
