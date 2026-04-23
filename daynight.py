# ============================================================
#  daynight.py — Sistem Siang/Malam
# ============================================================
import math
import pygame
from settings import DAY_DURATION, SCREEN_W, SCREEN_H
from utils import lerp, alpha_surface


# Palet warna per fase hari
# phase: 0.0=subuh, 0.25=siang, 0.5=sore, 0.75=malam
PHASE_COLORS = {
    # phase: (bg_top, bg_bot, ambient_r, ambient_g, ambient_b, sun_alpha)
    0.00: ((30,  50,  90),  (5,  15,  40),  120, 160, 220, 80),   # subuh
    0.15: ((10,  60, 110),  (2,  20,  55),  160, 210, 255, 120),  # pagi
    0.25: ((10,  80, 140),  (2,  25,  70),  200, 235, 255, 180),  # siang
    0.40: ((15,  70, 120),  (3,  20,  60),  220, 200, 160, 160),  # siang akhir
    0.50: ((40,  50,  90),  (8,  18,  45),  255, 160,  80, 140),  # sore
    0.60: ((60,  35,  70),  (12, 10,  35),  200,  90,  60, 100),  # maghrib
    0.70: ((10,  15,  45),  (2,   5,  20),   60,  60, 120,  40),  # malam awal
    0.75: ((5,   10,  30),  (1,   3,  12),   40,  40,  90,  20),  # malam
    0.90: ((8,   18,  50),  (2,   8,  25),   70,  80, 140,  40),  # dini hari
    1.00: ((30,  50,  90),  (5,  15,  40),  120, 160, 220, 80),   # subuh lagi
}

PHASE_NAMES = {
    0.00: 'Subuh',
    0.15: 'Pagi',
    0.25: 'Siang',
    0.50: 'Sore',
    0.60: 'Maghrib',
    0.75: 'Malam',
}


def _lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def _get_phase_color(phase):
    """Interpolasi warna berdasarkan phase 0..1."""
    keys = sorted(PHASE_COLORS.keys())
    for i in range(len(keys)-1):
        k0, k1 = keys[i], keys[i+1]
        if k0 <= phase <= k1:
            t = (phase - k0) / (k1 - k0) if k1 > k0 else 0
            v0 = PHASE_COLORS[k0]
            v1 = PHASE_COLORS[k1]
            bg_top = _lerp_color(v0[0], v1[0], t)
            bg_bot = _lerp_color(v0[1], v1[1], t)
            amb    = (
                int(lerp(v0[2], v1[2], t)),
                int(lerp(v0[3], v1[3], t)),
                int(lerp(v0[4], v1[4], t)),
                int(lerp(v0[5], v1[5], t)),
            )
            return bg_top, bg_bot, amb
    v = PHASE_COLORS[keys[-1]]
    return v[0], v[1], (v[2], v[3], v[4], v[5])


class DayNightSystem:
    def __init__(self):
        self.time       = 0.0      # detik absolut
        self.phase      = 0.15     # mulai dari pagi
        self._bg_cache  = None
        self._last_phase= -1
        self._stars     = self._gen_stars()

    def _gen_stars(self):
        import random
        return [(random.randint(0, SCREEN_W),
                 random.randint(0, int(SCREEN_H*0.5)),
                 random.uniform(0.5, 2.0)) for _ in range(80)]

    def update(self, dt):
        self.time  += dt
        self.phase  = (self.time / DAY_DURATION) % 1.0

    @property
    def is_night(self) -> bool:
        return 0.65 < self.phase < 0.95

    @property
    def is_dawn(self) -> bool:
        return self.phase < 0.12 or self.phase > 0.95

    @property
    def phase_name(self) -> str:
        keys = sorted(PHASE_NAMES.keys())
        best = keys[0]
        for k in keys:
            if self.phase >= k:
                best = k
        return PHASE_NAMES[best]

    @property
    def ambient_mult(self) -> float:
        """Pengali pencahayaan: 1.0 = siang terang, 0.3 = malam gelap."""
        if 0.25 <= self.phase <= 0.45:
            return 1.0
        elif self.is_night:
            return 0.3
        else:
            # interpolasi
            if self.phase < 0.25:
                return lerp(0.5, 1.0, self.phase / 0.25)
            elif self.phase < 0.65:
                return lerp(1.0, 0.3, (self.phase - 0.45) / 0.20)
            else:
                return lerp(0.3, 0.5, (self.phase - 0.95) / 0.05) \
                       if self.phase > 0.95 else 0.3

    def get_colors(self):
        return _get_phase_color(self.phase)

    def draw_sky_overlay(self, surface):
        """Overlay warna langit + bintang malam + efek matahari/bulan."""
        bg_top, bg_bot, amb = self.get_colors()

        # gradient background
        bg = pygame.Surface((SCREEN_W, SCREEN_H))
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(lerp(bg_top[0], bg_bot[0], t))
            g = int(lerp(bg_top[1], bg_bot[1], t))
            b = int(lerp(bg_top[2], bg_bot[2], t))
            pygame.draw.line(bg, (r, g, b), (0, y), (SCREEN_W, y))
        surface.blit(bg, (0, 0))

        # bintang (muncul malam)
        star_alpha = 0
        if self.phase > 0.60:
            star_alpha = int(min(1, (self.phase - 0.60)/0.10) * 180)
        elif self.phase < 0.12:
            star_alpha = int(max(0, 1 - self.phase/0.12) * 180)

        if star_alpha > 5:
            star_s = alpha_surface(SCREEN_W, SCREEN_H)
            for sx, sy, sr in self._stars:
                twinkle = int(star_alpha * (0.7 + 0.3*math.sin(
                    self.time*2 + sx*0.1)))
                pygame.draw.circle(star_s, (255,255,255,twinkle),
                                   (sx,sy), int(sr))
            surface.blit(star_s, (0,0))

        # matahari / bulan
        sun_x = int(SCREEN_W * 0.15 + SCREEN_W * 0.70 * self.phase)
        if not self.is_night:
            # matahari
            sun_y  = int(80 - math.sin(self.phase * math.pi) * 60)
            sun_a  = amb[3]
            sun_col= (255, int(lerp(200, 255, self.phase*2)),
                      int(lerp(60, 200, self.phase)))
            sun_s  = alpha_surface(80, 80)
            # glow — gunakan fill+set_alpha bukan tuple 4 nilai
            for gr in range(30, 5, -5):
                ga  = int(sun_a * (1 - gr/30) * 0.4)
                g_s = alpha_surface(gr*2, gr*2)
                pygame.draw.circle(g_s, sun_col, (gr, gr), gr)
                g_s.set_alpha(ga)
                sun_s.blit(g_s, (40-gr, 40-gr))
            pygame.draw.circle(sun_s, sun_col, (40,40), 14)
            sun_s.set_alpha(sun_a)
            surface.blit(sun_s, (sun_x-40, sun_y-40))
        else:
            # bulan
            moon_phase = (self.phase - 0.65) / 0.30
            moon_y = int(50 - math.sin(moon_phase * math.pi) * 40)
            moon_s = alpha_surface(60, 60)
            pygame.draw.circle(moon_s, (220,230,255), (30,30), 18)
            moon_s.set_alpha(160)
            surface.blit(moon_s, (sun_x-30, moon_y-30))
            # shadow crescent
            cres = alpha_surface(60, 60)
            pygame.draw.circle(cres, (10,15,35), (36,30), 16)
            cres.set_alpha(140)
            surface.blit(cres, (sun_x-30, moon_y-30))

        # ambient color wash (tint air)
        wash = alpha_surface(SCREEN_W, SCREEN_H)
        wash_alpha = int(30 * (1 - self.ambient_mult))
        pygame.draw.rect(wash, (amb[0]//4, amb[1]//4, amb[2]//3, wash_alpha),
                         (0, 0, SCREEN_W, SCREEN_H))
        surface.blit(wash, (0,0))

    def draw_phase_label(self, surface, font):
        """Label fase hari di pojok kanan atas."""
        txt = font.render(self.phase_name, True, (180, 210, 255))
        txt.set_alpha(120)
        surface.blit(txt, (SCREEN_W - txt.get_width() - 14, 52))
