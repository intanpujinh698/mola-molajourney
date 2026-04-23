# ============================================================
#  world.py — Environment & Background Rendering
# ============================================================
import random
import math
import pygame
from settings import *
from utils import lerp, alpha_surface


# ── Terumbu Karang ──────────────────────────────────────────
class Coral:
    SHAPES = ['branch', 'fan', 'mound']

    def __init__(self, x, y):
        self.x       = x
        self.y       = y
        self.shape   = random.choice(self.SHAPES)
        self.height  = random.randint(30, 70)
        self.width   = random.randint(20, 50)
        self.hue     = random.choice([
            (200, 80, 100),   # merah-pink
            (240, 120, 50),   # oranye
            (80,  180, 160),  # teal
            (180, 100, 200),  # ungu
            (220, 200, 60),   # kuning
        ])
        self.sway    = random.uniform(0, math.pi * 2)
        self.sway_spd= random.uniform(0.5, 1.2)

    def update(self, dt):
        self.sway += self.sway_spd * dt

    def draw(self, surface, time):
        sway_x = math.sin(self.sway) * 2
        r, g, b = self.hue

        if self.shape == 'branch':
            self._draw_branch(surface, sway_x, r, g, b)
        elif self.shape == 'fan':
            self._draw_fan(surface, sway_x, r, g, b)
        else:
            self._draw_mound(surface, r, g, b)

    def _draw_branch(self, surf, sway, r, g, b):
        # batang utama
        for i in range(3):
            ox = self.x + i * self.width // 3
            pygame.draw.line(surf,
                (r//2, g//2, b//2),
                (ox, self.y),
                (ox + sway, self.y - self.height),
                2)
            # cabang
            mid_y = self.y - self.height // 2
            pygame.draw.line(surf,
                (r, g, b),
                (ox + sway//2, mid_y),
                (ox + sway//2 + 12, mid_y - 20),
                1)
            pygame.draw.line(surf,
                (r, g, b),
                (ox + sway//2, mid_y),
                (ox + sway//2 - 12, mid_y - 20),
                1)

    def _draw_fan(self, surf, sway, r, g, b):
        for i in range(7):
            angle = math.pi * 0.15 + i * (math.pi * 0.7 / 6)
            ex = self.x + self.width//2 + math.cos(angle) * self.height + sway
            ey = self.y - math.sin(angle) * self.height
            alpha = 160
            pygame.draw.line(surf, (r, g, b),
                             (self.x + self.width//2 + sway//2, self.y),
                             (int(ex), int(ey)), 1)

    def _draw_mound(self, surf, r, g, b):
        pygame.draw.ellipse(surf, (r//2, g//2, b//2),
                            (self.x, self.y - self.height//2,
                             self.width, self.height//2))
        # polip
        for i in range(5):
            px = self.x + i * self.width // 5 + random.randint(-2,2)
            pygame.draw.circle(surf, (r, g, b), (px, self.y - self.height//2), 3)


# ── Rumput Laut ──────────────────────────────────────────────
class Seaweed:
    def __init__(self, x):
        self.x       = x
        self.y       = SCREEN_H
        self.height  = random.randint(50, 120)
        self.segments= random.randint(4, 8)
        self.phase   = random.uniform(0, math.pi * 2)
        self.color   = (
            random.randint(20, 60),
            random.randint(130, 200),
            random.randint(60, 110),
        )

    def draw(self, surface, time):
        pts = []
        seg_h = self.height / self.segments
        for i in range(self.segments + 1):
            t    = i / self.segments
            wave = math.sin(time * 1.3 + self.phase + t * 3) * (12 * t)
            pts.append((int(self.x + wave), int(self.y - i * seg_h)))
        if len(pts) > 1:
            pygame.draw.lines(surface, self.color, False, pts, 2)


# ── Ambient Bubble ───────────────────────────────────────────
class AmbientBubble:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x     = random.uniform(0, SCREEN_W)
        self.y     = random.uniform(0, SCREEN_H)
        self.r     = random.uniform(1, 3)
        self.vy    = random.uniform(15, 40)
        self.wobble= random.uniform(0, math.pi * 2)
        self.alpha = random.randint(30, 80)

    def update(self, dt):
        self.y      -= self.vy * dt
        self.wobble += dt * 2
        self.x      += math.sin(self.wobble) * 0.4
        if self.y < -5:
            self.reset()
            self.y = SCREEN_H + 5

    def draw(self, surface):
        s = pygame.Surface((int(self.r*2+2)*2, int(self.r*2+2)*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (160, 220, 255, self.alpha),
                           (int(self.r)+2, int(self.r)+2), int(self.r), 1)
        surface.blit(s, (int(self.x - self.r - 2), int(self.y - self.r - 2)))


# ── World ────────────────────────────────────────────────────
class World:
    def __init__(self):
        self.time    = 0.0
        self.corals  = [Coral(
            random.randint(20, SCREEN_W - 40),
            random.randint(SCREEN_H - 80, SCREEN_H - 20)
        ) for _ in range(CORAL_COUNT)]

        self.seaweeds = [Seaweed(random.randint(10, SCREEN_W - 10))
                         for _ in range(18)]

        self.bubbles = [AmbientBubble() for _ in range(40)]

        # Pre-render background gradient surface
        self._bg_cache   = None
        self._build_bg()

        # Surface shimmer line positions
        self._shimmer_pts= []

    def _build_bg(self):
        """Buat gradient background sekali saja."""
        self._bg_cache = pygame.Surface((SCREEN_W, SCREEN_H))
        for y in range(SCREEN_H):
            t   = y / SCREEN_H
            r   = int(lerp(C_BG_TOP[0], C_BG_BOT[0], t))
            g   = int(lerp(C_BG_TOP[1], C_BG_BOT[1], t))
            b   = int(lerp(C_BG_TOP[2], C_BG_BOT[2], t))
            pygame.draw.line(self._bg_cache, (r, g, b), (0, y), (SCREEN_W, y))

    def depth_factor(self, y) -> float:
        """0.0 = permukaan, 1.0 = paling dalam."""
        return max(0.0, min(1.0, y / SCREEN_H))

    def update(self, dt):
        self.time += dt
        for b in self.bubbles:
            b.update(dt)
        for c in self.corals:
            c.update(dt)

    def draw_background(self, surface):
        surface.blit(self._bg_cache, (0, 0))

    def draw_surface_zone(self, surface, surface_glow: float):
        """Cahaya permukaan + garis shimmer."""
        # overlay terang
        glow_s = alpha_surface(SCREEN_W, ZONE_SURFACE + 20)
        base_a = int(30 + surface_glow * 60)
        for y in range(ZONE_SURFACE + 20):
            t = 1 - y / (ZONE_SURFACE + 20)
            a = int(base_a * t)
            pygame.draw.line(glow_s, (120, 200, 255, a), (0, y), (SCREEN_W, y))
        surface.blit(glow_s, (0, 0))

        # garis shimmer
        pts = []
        for x in range(0, SCREEN_W, 3):
            y = 10 + math.sin(x * 0.04 + self.time * 2.0) * 5
            pts.append((x, int(y)))
        if len(pts) > 1:
            a = int(60 + surface_glow * 120)
            shimmer_s = alpha_surface(SCREEN_W, 30)
            pygame.draw.lines(shimmer_s, (200, 240, 255, a), False, pts, 1)
            surface.blit(shimmer_s, (0, 0))

    def draw_god_rays(self, surface, depth_factor: float):
        """God rays dari permukaan."""
        alpha = max(0, int((1 - depth_factor) * 18))
        if alpha < 2:
            return
        ray_s = alpha_surface(SCREEN_W, SCREEN_H)
        for i in range(5):
            rx = int(SCREEN_W * 0.1 + i * SCREEN_W * 0.2
                     + math.sin(self.time * 0.4 + i) * 25)
            pts = [
                (rx, 0),
                (rx + 22, 0),
                (rx + 70, int(SCREEN_H * 0.55)),
                (rx + 38, int(SCREEN_H * 0.55)),
            ]
            ray_surf = alpha_surface(SCREEN_W, SCREEN_H)
            pygame.draw.polygon(ray_surf, (180, 230, 255, alpha), pts)
            surface.blit(ray_surf, (0, 0))

    def draw_depth_vignette(self, surface, depth_factor: float):
        """Gelap di tepi layar makin dalam."""
        alpha = int(depth_factor * 160)
        if alpha < 5:
            return
        vig = alpha_surface(SCREEN_W, SCREEN_H)
        for step, margin in enumerate(range(0, min(SCREEN_W, SCREEN_H)//2, 12)):
            a_step = int(alpha * (1 - margin / (min(SCREEN_W, SCREEN_H)//2)))
            pygame.draw.rect(vig, (2, 8, 20, min(255, a_step)),
                             (margin, margin,
                              SCREEN_W - margin*2, SCREEN_H - margin*2),
                             12)
        surface.blit(vig, (0, 0))

    def draw_zone_hint(self, surface, font_small, mola_y: float):
        """Teks zona kedalaman."""
        depth = self.depth_factor(mola_y)
        if depth > 0.65:
            alpha = int((depth - 0.65) / 0.35 * 180)
            txt   = font_small.render(
                "TERLALU DALAM — NAIK KE PERMUKAAN", True, C_WARNING)
            txt.set_alpha(alpha)
            surface.blit(txt,
                (SCREEN_W//2 - txt.get_width()//2, SCREEN_H - 28))

    def draw_environment(self, surface):
        """Terumbu karang & rumput laut."""
        for sw in self.seaweeds:
            sw.draw(surface, self.time)
        for c in self.corals:
            c.draw(surface, self.time)

    def draw_bubbles(self, surface):
        for b in self.bubbles:
            b.draw(surface)
