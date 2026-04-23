# ============================================================
#  boss.py — Boss: Kapal Nelayan
# ============================================================
import math
import random
import pygame
from settings import *
from utils import alpha_surface, lerp, clamp
from entities import FishingNet


class BossShip:
    """
    Kapal nelayan muncul dari salah satu sisi layar,
    bergerak pelan, dan menjatuhkan jaring secara periodik.
    Pemain tidak bisa membunuhnya — hanya menghindari.
    Boss pergi setelah melewati layar.
    """
    STATE_ENTER   = 'enter'
    STATE_ACTIVE  = 'active'
    STATE_LEAVING = 'leaving'
    STATE_DONE    = 'done'

    def __init__(self):
        # muncul dari kiri atau kanan
        self.from_left = random.choice([True, False])
        if self.from_left:
            self.x  = -BOSS_W - 20
            self.vx =  BOSS_SPEED
        else:
            self.x  = SCREEN_W + 20
            self.vx = -BOSS_SPEED

        self.y          = random.randint(12, 35)   # di permukaan
        self.w          = BOSS_W
        self.h          = BOSS_H
        self.state      = self.STATE_ENTER
        self.net_timer  = BOSS_NET_INTERVAL * 0.5  # jaring pertama lebih cepat
        self.nets: list[FishingNet] = []
        self.time       = 0.0
        self.alpha      = 0            # fade in
        self.warn_timer = 3.0          # detik peringatan sebelum masuk
        self.warned     = False        # sudah tampil warning?
        self.active_x_start = 60
        self.active_x_end   = SCREEN_W - 60

    @property
    def done(self):
        return self.state == self.STATE_DONE

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, dropped_nets: list):
        self.time      += dt
        self.net_timer -= dt

        if self.state == self.STATE_ENTER:
            self.x     += self.vx * dt
            self.alpha  = min(255, self.alpha + int(dt * 400))
            # sudah masuk layar?
            if (self.from_left and self.x > 10) or \
               (not self.from_left and self.x < SCREEN_W - self.w - 10):
                self.state = self.STATE_ACTIVE

        elif self.state == self.STATE_ACTIVE:
            self.x    += self.vx * dt * 0.4   # gerak lebih lambat saat aktif
            self.alpha = 255
            # jatuhkan jaring
            if self.net_timer <= 0:
                self._drop_net(dropped_nets)
                self.net_timer = BOSS_NET_INTERVAL

            # mulai pergi setelah melewati tengah layar
            cx = self.x + self.w/2
            if (self.from_left  and cx > SCREEN_W * 0.75) or \
               (not self.from_left and cx < SCREEN_W * 0.25):
                self.state = self.STATE_LEAVING

        elif self.state == self.STATE_LEAVING:
            self.x    += self.vx * dt * 1.5
            self.alpha = max(0, self.alpha - int(dt * 200))
            if self.x < -self.w - 50 or self.x > SCREEN_W + 50:
                self.state = self.STATE_DONE

        # update jaring milik boss
        for n in self.nets:
            n.update(dt)
        self.nets = [n for n in self.nets
                     if -200 < n.pos.x < SCREEN_W+200]

    def _drop_net(self, dropped_nets: list):
        """Jatuhkan jaring tepat di bawah kapal."""
        drop_x = self.x + random.uniform(10, self.w - NET_W - 10)
        n = FishingNet()
        n.pos.x = drop_x
        n.pos.y = self.y + self.h + 5
        n.vx    = self.vx * 0.1        # sedikit ikut gerak kapal
        n.vy    = random.uniform(15, 30)  # jatuh ke bawah
        dropped_nets.append(n)
        self.nets.append(n)

    def draw(self, surface):
        if self.alpha < 5:
            return
        x, y  = int(self.x), int(self.y)
        w, h  = self.w, self.h
        alpha = self.alpha

        spr = alpha_surface(w + 40, h + 60)
        ox, oy = 20, 10

        # lambung kapal
        hull_pts = [
            (ox,        oy+h//2),
            (ox+10,     oy+h),
            (ox+w-10,   oy+h),
            (ox+w,      oy+h//2),
            (ox+w,      oy+h//3),
            (ox,        oy+h//3),
        ]
        pygame.draw.polygon(spr, (80, 60, 40), hull_pts)
        pygame.draw.polygon(spr, (60, 45, 28), hull_pts, 2)

        # dek atas
        pygame.draw.rect(spr, (100, 80, 55),
                         (ox+10, oy+h//3-10, w-20, h//3+10))

        # kabin
        pygame.draw.rect(spr, (120, 100, 70),
                         (ox+w//2-20, oy, 40, h//3))
        pygame.draw.rect(spr, (60, 180, 220, 160),
                         (ox+w//2-14, oy+4, 12, 10))   # jendela
        pygame.draw.rect(spr, (60, 180, 220, 160),
                         (ox+w//2+2, oy+4, 12, 10))

        # cerobong
        pygame.draw.rect(spr, (50, 50, 50),
                         (ox+w//2+5, oy-14, 10, 18))
        # asap
        for si in range(3):
            sa = int(60 * (1 - si/3))
            sr = 6 + si*4
            smoke = alpha_surface(sr*2, sr*2)
            pygame.draw.circle(smoke, (180,180,180,sa), (sr,sr), sr)
            spr.blit(smoke, (ox+w//2+10-sr,
                             oy-14-si*10-sr))

        # tali jaring di sisi kapal
        rope_col = (160, 140, 80, 180)
        for ri in range(0, w, 18):
            pygame.draw.line(spr, rope_col,
                             (ox+ri, oy+h),
                             (ox+ri+4, oy+h+20), 1)

        # flag
        flag_pts = [
            (ox+w//2-18, oy-6),
            (ox+w//2-18+20, oy-6+8),
            (ox+w//2-18, oy-6+16),
        ]
        pygame.draw.polygon(spr, (200, 50, 50), flag_pts)
        pygame.draw.line(spr, (80,60,40),
                         (ox+w//2-18, oy-16),
                         (ox+w//2-18, oy+h//3), 2)

        spr.set_alpha(alpha)
        surface.blit(spr, (x - 20, y - 10))

    def draw_warning(self, surface, font, time):
        """Tampilkan peringatan sebelum boss masuk."""
        pulse = abs(math.sin(time * 4)) * 0.7 + 0.3
        side  = 'KIRI' if self.from_left else 'KANAN'
        lines = [
            '! KAPAL NELAYAN TERDETEKSI !',
            f'Datang dari {side}',
            'Hindari jaring yang dijatuhkan',
        ]
        for i, line in enumerate(lines):
            alpha = int(pulse * 220)
            col   = (255, 120, 40) if i == 0 else (220, 180, 100)
            txt   = font.render(line, True, col)
            txt.set_alpha(alpha)
            surface.blit(txt, (SCREEN_W//2 - txt.get_width()//2,
                               SCREEN_H//2 - 40 + i*22))


# ── Manager boss
class BossManager:
    def __init__(self):
        self.boss          = None
        self.boss_defeated = 0      # berapa kali kapal sudah lewat
        self.warn_timer    = 0.0
        self.showing_warn  = False
        self._next_score   = BOSS_SPAWN_SCORE

    @property
    def active(self):
        return self.boss is not None and not self.boss.done

    def check_spawn(self, score: int):
        """Spawn boss tiap kelipatan BOSS_SPAWN_SCORE."""
        if self.boss is None or self.boss.done:
            if score >= self._next_score:
                self.boss         = BossShip()
                self.showing_warn = True
                self.warn_timer   = 3.0
                self._next_score += BOSS_SPAWN_SCORE

    def update(self, dt, dropped_nets: list, score: int):
        self.check_spawn(score)
        if self.warn_timer > 0:
            self.warn_timer -= dt
            if self.warn_timer <= 0:
                self.showing_warn = False

        if self.boss and not self.boss.done:
            self.boss.update(dt, dropped_nets)
            if self.boss.done:
                self.boss_defeated += 1

    def draw(self, surface):
        if self.boss and not self.boss.done:
            self.boss.draw(surface)

    def draw_warning(self, surface, font, time):
        if self.showing_warn and self.boss:
            self.boss.draw_warning(surface, font, time)
