import pygame
class DialogueScene:

    def __init__(self, screen, text, next_scene_factory=None, duration=2600):
        self.screen = screen
        self.text = text
        self.next_scene_factory = next_scene_factory
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 50)
        self.small_font = pygame.font.Font("assets/fonts/Pixeltype.ttf", 28)

    def handle_events(self, event):
        return None
    
    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed >= self.duration:
            if callable(self.next_scene_factory):
                try:
                    return ("switch_scene", self.next_scene_factory())
                except Exception:
                    return "loading_done"
            return "loading_done"
        return None
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        screen_w, screen_h = self.screen.get_size()

        lines = [self.text[i:i+48] for i in range(0, len(self.text), 48)]
        y_offset = screen_h // 2 - len(lines) * 30

        for line in lines:
            rendered = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(
                rendered,
                rendered.get_rect(center=(screen_w // 2, y_offset))
            )
            y_offset += 60

        hint = self.small_font.render(
            "The adventure begins soon...",
            True,
            (180, 180, 180)
        )
        self.screen.blit(
            hint,
            hint.get_rect(center=(screen_w // 2, screen_h // 2 + 120))
        )