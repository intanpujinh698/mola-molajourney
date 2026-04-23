# ============================================================
#  hud.py — HUD & UI Overlay
# ============================================================
import math
import pygame
from settings import *
from utils import draw_bar, clamp, lerp, alpha_surface


class HUD:
    def __init__(self):
        pygame.font.init()
        self.font_title  = pygame.font.SysFont('Georgia', 28, bold=True)
        self.font_med    = pygame.font.SysFont('Georgia', 16)
        self.font_small  = pygame.font.SysFont('Consolas', 12)
        self.font_tiny   = pygame.font.SysFont('Consolas', 10)

        self.msg_timer   = 0.0
        self.msg_text    = ''
        self.msg_color   = C_UI_TEXT

        self.score_anim  = 0.0   # animasi saat score naik
        self._prev_score = 0

        self.warning_pulse = 0.0

    def show_message(self, text: str, color=None, duration=2.0):
        self.msg_text  = text
        self.msg_timer = duration
        self.msg_color = color or C_UI_TEXT

    def update(self, dt, mola, score):
        self.msg_timer      = max(0, self.msg_timer - dt)
        self.warning_pulse += dt * 4

        if score > self._prev_score:
            self.score_anim  = 0.5
            self._prev_score = score
        self.score_anim = max(0, self.score_anim - dt)

    def draw(self, surface, mola, score, time):
        self._draw_panel(surface, mola, score, time)
        self._draw_message(surface)
        self._draw_warnings(surface, mola, time)
        self._draw_depth_bar(surface, mola)

    # ── Panel kiri bawah
    def _draw_panel(self, surface, mola, score, time):
        panel_w, panel_h = 200, 100
        px, py = 12, SCREEN_H - panel_h - 12

        # background panel
        panel_s = alpha_surface(panel_w, panel_h)
        pygame.draw.rect(panel_s, (5, 15, 35, 170),
                         (0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(panel_s, (60, 100, 160, 80),
                         (0, 0, panel_w, panel_h), 1, border_radius=8)
        surface.blit(panel_s, (px, py))

        # label
        labels = ['ENERGI', 'VITALITAS', 'UKURAN']
        values = [mola.energy, mola.vitality, (mola.size - 1) / (MOLA_SIZE_MAX - 1) * 100]
        colors_hi = [C_ENERGY_HI, C_VITALITY, C_SIZE_BAR]
        colors_lo = [C_ENERGY_LO, (180, 40, 40), (20, 140, 100)]

        for i, (lbl, val, chi, clo) in enumerate(zip(labels, values, colors_hi, colors_lo)):
            by = py + 12 + i * 28
            # label teks
            lbl_surf = self.font_tiny.render(lbl, True, C_UI_DIM)
            surface.blit(lbl_surf, (px + 8, by))
            # bar
            draw_bar(surface, px + 8, by + 12, panel_w - 16, 7,
                     val, 100, chi, clo)

        # score (kanan atas)
        score_scale = 1 + self.score_anim * 0.5
        sc_surf = self.font_med.render(f'UBUR-UBUR: {score}', True, C_UI_TEXT)
        if score_scale > 1:
            w = int(sc_surf.get_width() * score_scale)
            h = int(sc_surf.get_height() * score_scale)
            sc_surf = pygame.transform.scale(sc_surf, (w, h))
        surface.blit(sc_surf, (SCREEN_W - sc_surf.get_width() - 14, 12))

        # ukuran mola
        sz_txt = self.font_tiny.render(f'UKURAN  {mola.size:.1f}x', True, C_UI_DIM)
        surface.blit(sz_txt, (SCREEN_W - sz_txt.get_width() - 14, 34))

    # ── Pesan tengah
    def _draw_message(self, surface):
        if self.msg_timer <= 0:
            return
        alpha = int(min(255, self.msg_timer * 300))
        txt = self.font_med.render(self.msg_text, True, self.msg_color)
        txt.set_alpha(alpha)
        surface.blit(txt, (SCREEN_W//2 - txt.get_width()//2,
                           SCREEN_H//2 - 60))

    # ── Warning
    def _draw_warnings(self, surface, mola, time):
        warns = []
        if mola.energy < 20:
            warns.append('⚠  ENERGI KRITIS — NAIK KE PERMUKAAN')
        if mola.vitality < 25:
            warns.append('⚠  VITALITAS RENDAH')
        if mola.tangled:
            warns.append('⚠  TERJERAT — TIDAK BISA BERGERAK')

        pulse = abs(math.sin(self.warning_pulse)) * 0.6 + 0.4
        for i, w in enumerate(warns):
            alpha = int(pulse * 220)
            txt   = self.font_small.render(w, True, C_WARNING)
            txt.set_alpha(alpha)
            surface.blit(txt, (SCREEN_W//2 - txt.get_width()//2,
                               SCREEN_H - 55 - i * 18))

    # ── Bar kedalaman (kanan)
    def _draw_depth_bar(self, surface, mola):
        bx = SCREEN_W - 18
        by = 60
        bh = SCREEN_H - 120
        bw = 6

        # background
        bg_s = alpha_surface(bw + 8, bh + 8)
        pygame.draw.rect(bg_s, (5, 15, 35, 150),
                         (0, 0, bw + 8, bh + 8), border_radius=3)
        surface.blit(bg_s, (bx - 4, by - 4))

        # gradient bar
        for y in range(bh):
            t = y / bh
            r = int(lerp(100, 10, t))
            g = int(lerp(190, 30, t))
            b = int(lerp(255, 80, t))
            pygame.draw.line(surface, (r, g, b), (bx, by + y), (bx + bw, by + y))

        # indikator posisi mola
        mola_ratio = clamp((mola.pos.y - 20) / (SCREEN_H - 40), 0, 1)
        ind_y = int(by + mola_ratio * bh)
        pygame.draw.rect(surface, (255, 255, 255),
                         (bx - 2, ind_y - 4, bw + 4, 8), border_radius=2)

        # label
        lbl = self.font_tiny.render('DALAM', True, C_UI_DIM)
        surface.blit(lbl, (bx - 8, by + bh + 4))
        lbl2 = self.font_tiny.render('ATAS', True, C_UI_DIM)
        surface.blit(lbl2, (bx - 4, by - 14))


# ─── Layar Game Over ─────────────────────────────────────────
class GameOverScreen:
    def __init__(self):
        self.font_big   = pygame.font.SysFont('Georgia', 44, bold=True)
        self.font_med   = pygame.font.SysFont('Georgia', 18)
        self.font_small = pygame.font.SysFont('Consolas', 13)
        self.alpha      = 0

    def update(self, dt):
        self.alpha = min(255, self.alpha + int(dt * 300))

    def draw(self, surface, score):
        overlay = alpha_surface(SCREEN_W, SCREEN_H)
        pygame.draw.rect(overlay, (2, 8, 20, min(200, self.alpha)),
                         (0, 0, SCREEN_W, SCREEN_H))
        surface.blit(overlay, (0, 0))

        if self.alpha < 80:
            return

        title = self.font_big.render('TERDAMPAR', True, (220, 100, 80))
        title.set_alpha(min(255, self.alpha))
        surface.blit(title, (SCREEN_W//2 - title.get_width()//2, SCREEN_H//2 - 80))

        sub = self.font_med.render(
            f'Ubur-ubur dimakan: {score}', True, C_UI_TEXT)
        sub.set_alpha(min(255, self.alpha))
        surface.blit(sub, (SCREEN_W//2 - sub.get_width()//2, SCREEN_H//2 - 20))

        hint = self.font_small.render(
            'Tekan R untuk main lagi  |  ESC untuk keluar', True, C_UI_DIM)
        hint.set_alpha(min(200, self.alpha))
        surface.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H//2 + 30))


# ─── Layar Start ─────────────────────────────────────────────
class StartScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('Georgia', 52, bold=True)
        self.font_sub   = pygame.font.SysFont('Georgia', 18)
        self.font_small = pygame.font.SysFont('Consolas', 12)
        self.time       = 0.0

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        overlay = alpha_surface(SCREEN_W, SCREEN_H)
        pygame.draw.rect(overlay, (2, 8, 20, 200), (0, 0, SCREEN_W, SCREEN_H))
        surface.blit(overlay, (0, 0))

        # judul
        pulse = abs(math.sin(self.time * 0.8)) * 30
        col   = (int(100 + pulse), int(190 + pulse*0.5), 255)
        title = self.font_title.render('MOLA-MOLA JOURNEY', True, col)
        surface.blit(title, (SCREEN_W//2 - title.get_width()//2, SCREEN_H//2 - 100))

        sub = self.font_sub.render(
            'Survival Simulation', True, C_UI_DIM)
        surface.blit(sub, (SCREEN_W//2 - sub.get_width()//2, SCREEN_H//2 - 45))

        # instruksi
        instructions = [
            'Gerakkan MOUSE untuk mengarahkan Mola-Mola',
            'Naik ke PERMUKAAN untuk memulihkan energi',
            'Makan UBUR-UBUR untuk tumbuh',
            'Hindari JARING NELAYAN dan HERI HIU',
        ]
        for i, ins in enumerate(instructions):
            txt = self.font_small.render(ins, True, C_UI_TEXT)
            surface.blit(txt, (SCREEN_W//2 - txt.get_width()//2,
                               SCREEN_H//2 + 10 + i * 18))

        blink = math.sin(self.time * 3) > 0
        if blink:
            start = self.font_sub.render('[ Klik untuk Mulai ]', True, (150, 210, 255))
            surface.blit(start, (SCREEN_W//2 - start.get_width()//2,
                                 SCREEN_H//2 + 100))
