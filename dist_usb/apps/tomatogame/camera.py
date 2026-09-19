import settings


class Camera:
    def __init__(self, level_width):
        self.offset_x = 0
        self.level_width = level_width

    def update(self, target_rect):
        desired = target_rect.centerx - settings.SCREEN_WIDTH // 2
        if target_rect.centerx < settings.SCREEN_WIDTH // 2:
            desired = 0
        self.offset_x = max(0, min(desired, self.level_width - settings.SCREEN_WIDTH))

    def apply(self, rect):
        return rect.x - self.offset_x, rect.y
