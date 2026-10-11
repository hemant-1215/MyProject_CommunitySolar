import random
import pygame


class Anvil:
    def __init__(self, screen_width, difficulty=1.0):
        self.screen_width = screen_width
        self.width = 40
        self.height = 32
        self.x = random.randint(20, screen_width - self.width - 20)
        self.y = -self.height
        self.speed = random.uniform(4.5, 7.0) * difficulty

    def update(self):
        self.y += self.speed

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 10

    @property
    def warning_color(self):
        # Faster anvils use hotter colours to communicate higher danger.
        if self.speed >= 10:
            return (245, 55, 55)       # red: very fast
        if self.speed >= 7:
            return (255, 145, 45)      # orange: fast
        return (120, 120, 130)         # grey: normal

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def render(self, surface):
        color = self.warning_color
        base_color = tuple(max(0, int(channel * 0.67)) for channel in color)

        top_rect = pygame.Rect(int(self.x) + 4, int(self.y), self.width - 8, 14)
        pygame.draw.rect(surface, color, top_rect, border_radius=2)

        base_rect = pygame.Rect(int(self.x), int(self.y) + 14, self.width, 18)
        pygame.draw.rect(surface, base_color, base_rect, border_radius=3)
        pygame.draw.rect(surface, (200, 200, 210), base_rect, width=1, border_radius=3)
