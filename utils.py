# ============================================================
#  utils.py — helper functions
# ============================================================
import math
import pygame


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def lerp_vec(v1: pygame.Vector2, v2: pygame.Vector2, t: float) -> pygame.Vector2:
    return pygame.Vector2(lerp(v1.x, v2.x, t), lerp(v1.y, v2.y, t))


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def dist(ax, ay, bx, by) -> float:
    return math.hypot(ax - bx, ay - by)


def normalise(vx: float, vy: float):
    """Return unit vector; safe for zero vector."""
    mag = math.hypot(vx, vy)
    if mag == 0:
        return 0.0, 0.0
    return vx / mag, vy / mag


def draw_bar(surface, x, y, w, h, value, max_val, color_hi, color_lo=None, bg=(30, 30, 50)):
    """Draw a simple status bar."""
    ratio = clamp(value / max_val, 0, 1)
    pygame.draw.rect(surface, bg, (x, y, w, h), border_radius=3)
    if color_lo:
        r = lerp(color_lo[0], color_hi[0], ratio)
        g = lerp(color_lo[1], color_hi[1], ratio)
        b = lerp(color_lo[2], color_hi[2], ratio)
        bar_color = (int(r), int(g), int(b))
    else:
        bar_color = color_hi
    fill_w = int(w * ratio)
    if fill_w > 0:
        pygame.draw.rect(surface, bar_color, (x, y, fill_w, h), border_radius=3)
    pygame.draw.rect(surface, (60, 80, 120), (x, y, w, h), 1, border_radius=3)


def alpha_surface(w, h) -> pygame.Surface:
    """Create a transparent surface."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    return s
