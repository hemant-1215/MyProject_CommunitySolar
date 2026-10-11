import random
import pygame
from game.player import Player
from game.anvil import Anvil


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.player = Player(width, height)
        self.anvils = []
        self.particles = []

        self.spawn_delay = 700
        self.last_spawn_time = pygame.time.get_ticks()

        self.start_ticks = pygame.time.get_ticks()
        self.survival_time = 0
        self.game_state = "PLAYING"

        self.shake_frames = 0
        self.shake_strength = 0

        self.font_big = pygame.font.SysFont(None, 52)
        self.font_medium = pygame.font.SysFont(None, 34)
        self.font_small = pygame.font.SysFont(None, 24)

    def handle_event(self, event):
        if self.game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

    def _spawn_impact(self, x, y):
        # Small particles burst upward and outward from the ground impact.
        for _ in range(14):
            self.particles.append({
                "x": float(x),
                "y": float(y),
                "vx": random.uniform(-2.8, 2.8),
                "vy": random.uniform(-4.0, -0.5),
                "life": random.randint(16, 28),
                "max_life": 28,
                "radius": random.randint(2, 4),
            })
        self.shake_frames = 7
        self.shake_strength = 3

    def _update_particles(self):
        for particle in self.particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.18
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.particles.remove(particle)

        if self.shake_frames > 0:
            self.shake_frames -= 1
        else:
            self.shake_strength = 0

    def update(self):
        self._update_particles()

        if self.game_state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        self.player.update()
        self.survival_time = (pygame.time.get_ticks() - self.start_ticks) // 1000

        # Dynamic difficulty: anvils speed up and spawn more frequently over time.
        difficulty = min(2.0, 1.0 + self.survival_time * 0.015)
        self.spawn_delay = max(280, 700 - self.survival_time * 8)

        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_delay:
            self.anvils.append(Anvil(self.width, difficulty))
            self.last_spawn_time = now

        player_rect = self.player.rect
        ground_y = self.height - 20

        for anvil in self.anvils[:]:
            anvil.update()

            if player_rect.colliderect(anvil.rect):
                self.game_state = "GAME_OVER"
                break

            if anvil.rect.bottom >= ground_y:
                self._spawn_impact(anvil.x + anvil.width / 2, ground_y)
                self.anvils.remove(anvil)
            elif anvil.is_off_screen(self.height):
                self.anvils.remove(anvil)

    def reset(self):
        self.player = Player(self.width, self.height)
        self.anvils.clear()
        self.particles.clear()
        self.shake_frames = 0
        self.shake_strength = 0
        self.start_ticks = pygame.time.get_ticks()
        self.last_spawn_time = pygame.time.get_ticks()
        self.survival_time = 0
        self.spawn_delay = 700
        self.game_state = "PLAYING"

    def render(self, screen):
        # Draw the frame to a separate surface so impact shake is easy to apply.
        scene = pygame.Surface((self.width, self.height))
        scene.fill((35, 38, 45))

        ground_y = self.height - 20
        pygame.draw.rect(scene, (70, 75, 85), (0, ground_y, self.width, 20))
        pygame.draw.line(scene, (160, 90, 40), (0, ground_y), (self.width, ground_y), 3)

        self.player.render(scene)
        for anvil in self.anvils:
            anvil.render(scene)

        # Dust particles fade by shrinking as their lifetime runs out.
        for particle in self.particles:
            fraction = particle["life"] / particle["max_life"]
            radius = max(1, int(particle["radius"] * fraction))
            pygame.draw.circle(
                scene, (185, 170, 145),
                (int(particle["x"]), int(particle["y"])), radius
            )

        time_surf = self.font_medium.render(
            f"Survival Time: {self.survival_time}s", True, (240, 240, 240)
        )
        scene.blit(time_surf, (20, 20))

        inst_surf = self.font_small.render(
            "Use [A/D] or [Arrow Keys] to Dodge", True, (170, 175, 185)
        )
        scene.blit(inst_surf, (self.width - inst_surf.get_width() - 20, 25))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            scene.blit(overlay, (0, 0))

            over_surf = self.font_big.render("CRUSHED! GAME OVER", True, (235, 65, 65))
            scene.blit(
                over_surf,
                (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 60)
            )

            score_surf = self.font_medium.render(
                f"You survived: {self.survival_time} seconds", True, (255, 255, 255)
            )
            scene.blit(
                score_surf,
                (self.width // 2 - score_surf.get_width() // 2, self.height // 2)
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again", True, (200, 200, 200)
            )
            scene.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50)
            )

        screen.fill((0, 0, 0))
        if self.shake_frames > 0 and self.shake_strength > 0:
            offset_x = random.randint(-self.shake_strength, self.shake_strength)
            offset_y = random.randint(-self.shake_strength, self.shake_strength)
        else:
            offset_x = offset_y = 0
        screen.blit(scene, (offset_x, offset_y))
