# ============================================================
#  particles.py — sistem partikel efek visual
# ============================================================
import random
import math
import pygame
from utils import lerp


class Particle:
    __slots__ = ('x','y','vx','vy','life','max_life','r','color','fade')

    def __init__(self, x, y, vx, vy, life, r, color, fade=True):
        self.x, self.y   = x, y
        self.vx, self.vy = vx, vy
        self.life        = life
        self.max_life    = life
        self.r           = r
        self.color       = color
        self.fade        = fade

    def update(self, dt):
        self.x    += self.vx * dt
        self.y    += self.vy * dt
        self.vx   *= 0.92
        self.vy   *= 0.92
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        ratio = self.life / self.max_life
        alpha = int(255 * ratio) if self.fade else 200
        r, g, b = self.color
        col = (clamp_col(r), clamp_col(g), clamp_col(b), alpha)
        rad = max(1, int(self.r * ratio))
        s = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (rad, rad), rad)
        surface.blit(s, (int(self.x) - rad, int(self.y) - rad))


def clamp_col(v):
    return max(0, min(255, int(v)))


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit_eat(self, x, y, hue_rgb):
        """Partikel saat memakan ubur-ubur."""
        for _ in range(14):
            angle = random.uniform(0, math.pi * 2)
            spd   = random.uniform(60, 160)
            life  = random.uniform(0.35, 0.75)
            r     = random.uniform(2, 6)
            # warna dari ubur-ubur + putih
            c = (
                min(255, hue_rgb[0] + random.randint(-20, 40)),
                min(255, hue_rgb[1] + random.randint(-20, 40)),
                min(255, hue_rgb[2] + random.randint(-20, 60)),
            )
            self.particles.append(Particle(
                x, y,
                math.cos(angle)*spd, math.sin(angle)*spd,
                life, r, c
            ))

    def emit_bubble(self, x, y, count=3):
        """Gelembung kecil."""
        for _ in range(count):
            self.particles.append(Particle(
                x + random.uniform(-8, 8),
                y,
                random.uniform(-15, 15),
                random.uniform(-60, -30),
                random.uniform(0.6, 1.4),
                random.uniform(1.5, 3.5),
                (160, 220, 255),
                fade=True
            ))

    def emit_damage(self, x, y):
        """Partikel merah saat terkena serangan."""
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            spd   = random.uniform(50, 120)
            self.particles.append(Particle(
                x, y,
                math.cos(angle)*spd, math.sin(angle)*spd,
                random.uniform(0.3, 0.7),
                random.uniform(2, 5),
                (220, 60, 60)
            ))

    def emit_surface(self, x, y):
        """Percikan saat berjemur."""
        for _ in range(4):
            self.particles.append(Particle(
                x + random.uniform(-20, 20),
                y,
                random.uniform(-30, 30),
                random.uniform(-80, -40),
                random.uniform(0.4, 0.9),
                random.uniform(1, 3),
                (200, 240, 255)
            ))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
