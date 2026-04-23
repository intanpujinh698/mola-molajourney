import sys, os, math, random
import pygame

from settings  import *
from utils     import clamp
from world     import World
from entities  import MolaMola, Jellyfish, FishingNet, Shark
from particles import ParticleSystem
from hud       import HUD, GameOverScreen, StartScreen
from audio     import AudioManager
from daynight  import DayNightSystem
from boss      import BossManager
import save as SaveSystem


class SpriteCache:
    DIR = os.path.join('assets', 'sprites')
    def __init__(self):
        self._c = {}
        for key, fn in [
            ('mola_normal','mola_normal.png'),('mola_blink','mola_blink.png'),
            ('mola_damage','mola_damage.png'),('shark_patrol','shark_patrol.png'),
            ('shark_chase','shark_chase.png'),('ui_cursor','ui_cursor.png'),
        ] + [(f'jelly_{c}',f'jelly_{c}.png') for c in
             ('purple','blue','pink','teal','yellow')]:
            p = os.path.join(self.DIR, fn)
            self._c[key] = pygame.image.load(p).convert_alpha() \
                           if os.path.exists(p) else None
    def get(self, k): return self._c.get(k)


JELLY_COLOR_MAP = {
    (200,100,220):'purple',(100,180,240):'blue',(240,120,160):'pink',
    (120,220,200):'teal',(240,200,100):'yellow',
    (255,210,50):'yellow',(100,230,160):'teal',(180,100,255):'purple',
    (180,220,80):'teal',
}


class Game:
    S_START    = 'start'
    S_PLAY     = 'play'
    S_GAMEOVER = 'gameover'

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock   = pygame.time.Clock()
        self.sprites = SpriteCache()
        self.audio   = AudioManager()
        self.save_data = SaveSystem.load()
        self.state   = self.S_START
        self.start_screen    = StartScreen()
        self.gameover_screen = GameOverScreen()
        self.shake = 0.0; self.sx = 0; self.sy = 0
        self._init_session()

    def _init_session(self):
        self.world      = World()
        self.particles  = ParticleSystem()
        self.hud        = HUD()
        self.daynight   = DayNightSystem()
        self.boss_mgr   = BossManager()
        self.mola       = MolaMola(SCREEN_W//2, SCREEN_H//3)
        self.jellies    = [Jellyfish() for _ in range(JELLY_COUNT)]
        self.nets       = [FishingNet() for _ in range(NET_COUNT)]
        self.sharks     = [Shark()     for _ in range(SHARK_COUNT)]
        self.boss_nets: list[FishingNet] = []
        self.score      = 0
        self.time       = 0.0
        self.surface_glow = 0.0
        self.respawn_q: list[int] = []
        self.gameover_screen = GameOverScreen()
        self._was_warn  = False
        self._was_surf  = False
        self._dmg_play  = False
        self.best_size  = 1.0
        self.audio.start_ambient()
        pygame.mouse.set_visible(False)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS)/1000.0, 0.05)
            self._events()
            if   self.state == self.S_START:    self._upd_start(dt);    self._drw_start()
            elif self.state == self.S_PLAY:     self._upd_play(dt);     self._drw_play()
            elif self.state == self.S_GAMEOVER: self._upd_over(dt);     self._drw_over()
            pygame.display.flip()

    def _events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if ev.key == pygame.K_r and self.state == self.S_GAMEOVER:
                    self._init_session(); self.state = self.S_PLAY
                if ev.key == pygame.K_m: self.audio.toggle()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if self.state == self.S_START: self.state = self.S_PLAY

    # ── START ─────────────────────────────────────────────
    def _upd_start(self, dt):
        self.start_screen.update(dt)
        self.world.update(dt)
        self.daynight.update(dt)
        self.audio.fade_ambient(0.15, 2.0, dt)

    def _drw_start(self):
        self.daynight.draw_sky_overlay(self.screen)
        self.world.draw_god_rays(self.screen, 0.3)
        self.world.draw_environment(self.screen)
        self.world.draw_bubbles(self.screen)
        self.start_screen.draw(self.screen)
        # highscore di start screen
        hs = self.save_data.get('highscore', 0)
        if hs > 0:
            txt = self.hud.font_small.render(
                f'Rekor: {hs} ubur-ubur', True, C_UI_DIM)
            self.screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2,
                                   SCREEN_H//2 + 128))

    # ── PLAY ──────────────────────────────────────────────
    def _upd_play(self, dt):
        self.time += dt
        mx, my  = pygame.mouse.get_pos()
        target  = pygame.Vector2(mx, my)
        depth_f = self.world.depth_factor(self.mola.pos.y)
        at_surf = self.mola.pos.y < ZONE_SURFACE

        self.daynight.update(dt)

        # ambient vol berdasarkan kedalaman & waktu
        night_mult = 0.8 if self.daynight.is_night else 1.0
        self.audio.fade_ambient((0.18 + depth_f*0.22) * night_mult, 2.0, dt)

        # surface
        if at_surf:
            self.surface_glow = min(1.0, self.surface_glow + dt*3)
            if not self._was_surf: self.audio.play_surface()
            self._was_surf = True
        else:
            self.surface_glow = max(0.0, self.surface_glow - dt*2)
            self._was_surf = False

        # warning energi
        crit = self.mola.energy < 20
        if crit and not self._was_warn:   self.audio.start_warning()
        elif not crit and self._was_warn: self.audio.stop_warning()
        self._was_warn = crit

        # update
        self.world.update(dt)
        self.mola.update(dt, target, depth_f, self.particles, at_surf)
        self.particles.update(dt)
        self.hud.update(dt, self.mola, self.score)
        for j in self.jellies: j.update(dt, self.time)
        for n in self.nets:    n.update(dt)
        for n in self.boss_nets: n.update(dt)
        for s in self.sharks:  s.update(dt, self.mola, self.particles)
        self.boss_mgr.update(dt, self.boss_nets, self.score)

        # boss_nets cleanup
        self.boss_nets = [n for n in self.boss_nets
                          if -200 < n.pos.x < SCREEN_W+200]

        # makan ubur-ubur
        for j in self.jellies:
            if not j.alive: continue
            if (self.mola.pos - j.pos).length() < self.mola.radius + j.r:
                j.alive = False
                self.score += 1
                # efek tipe
                e  = j.effect_energy
                v  = j.effect_vita
                sz = j.effect_size
                self.mola.energy   = clamp(self.mola.energy   + e, 0, ENERGY_MAX)
                self.mola.vitality = clamp(self.mola.vitality + v, 0, VITALITY_MAX)
                self.mola.size     = clamp(self.mola.size     + sz, MOLA_SIZE_MIN, MOLA_SIZE_MAX)
                self.particles.emit_eat(self.mola.pos.x, self.mola.pos.y, j.color)
                self.particles.emit_bubble(self.mola.pos.x, self.mola.pos.y, 4)
                self.audio.play_eat()
                lbl = j.label or f'+{e:.0f} energi' if e > 0 else j.label
                if j.label:
                    self.hud.show_message(j.label,
                        color=(255,80,80) if 'RACUN' in j.label else (180,255,180),
                        duration=1.0)
                self.respawn_q.append(pygame.time.get_ticks() + JELLY_RESPAWN_MS)
                if self.mola.size > self.best_size:
                    self.best_size = self.mola.size

        # respawn
        now = pygame.time.get_ticks()
        while self.respawn_q and self.respawn_q[0] <= now:
            self.respawn_q.pop(0)
            self.jellies.append(Jellyfish())
        self.jellies = [j for j in self.jellies if j.alive]

        # collision jaring (reguler + boss)
        all_nets = self.nets + self.boss_nets
        if not self.mola.tangled:
            for n in all_nets:
                mr  = self.mola.radius * 0.75
                mr2 = pygame.Rect(int(self.mola.pos.x-mr), int(self.mola.pos.y-mr),
                                  int(mr*2), int(mr*2))
                if n.get_rect().colliderect(mr2):
                    self.mola.get_tangled()
                    self.shake = 5.0
                    self.audio.play_tangle()
                    self.hud.show_message('Terjerat jaring!',
                                          color=C_WARNING, duration=2.0)
                    break

        # damage sound hiu
        if self.mola.damage_flash > 0.38 and not self._dmg_play:
            self.audio.play_damage(); self._dmg_play = True
        if self.mola.damage_flash <= 0: self._dmg_play = False

        # shake decay
        if self.shake > 0.1:
            self.sx = int(random.uniform(-self.shake, self.shake))
            self.sy = int(random.uniform(-self.shake, self.shake))
            self.shake *= 0.86
        else:
            self.sx = self.sy = 0

        # game over
        if not self.mola.alive:
            self.audio.stop_warning()
            self.audio.play_gameover()
            self.save_data = SaveSystem.update_after_game(
                self.score, self.best_size)
            self.state = self.S_GAMEOVER
            pygame.mouse.set_visible(True)

    def _drw_play(self):
        # sky (siang/malam)
        self.daynight.draw_sky_overlay(self.screen)
        depth_f = self.world.depth_factor(self.mola.pos.y)
        self.world.draw_god_rays(self.screen, depth_f)
        self.world.draw_surface_zone(self.screen, self.surface_glow)
        self.world.draw_environment(self.screen)
        self.world.draw_bubbles(self.screen)

        # jellyfish
        for j in self.jellies:
            key = 'jelly_' + JELLY_COLOR_MAP.get(tuple(j.color[:3]),'purple')
            spr = self.sprites.get(key)
            if spr: self._blit_c(spr, j.pos, j.r/28)
            else:   j.draw(self.screen, self.time)

        # nets
        for n in self.nets + self.boss_nets:
            n.draw(self.screen)

        # sharks
        for s in self.sharks:
            key = 'shark_chase' if s.state=='chase' else 'shark_patrol'
            spr = self.sprites.get(key)
            if spr:
                if not s.facing_r: spr = pygame.transform.flip(spr, True, False)
                self._blit_c(spr, s.pos)
            else: s.draw(self.screen, self.time)

        # boss
        self.boss_mgr.draw(self.screen)
        self.boss_mgr.draw_warning(self.screen, self.hud.font_med, self.time)

        self.particles.draw(self.screen)
        self._draw_mola()

        self.world.draw_depth_vignette(self.screen, depth_f)
        self.world.draw_zone_hint(self.screen, self.hud.font_small, self.mola.pos.y)

        # label fase hari
        self.daynight.draw_phase_label(self.screen, self.hud.font_small)

        # HUD
        self.hud.draw(self.screen, self.mola, self.score, self.time)

        # highscore indicator
        hs = self.save_data.get('highscore', 0)
        if hs > 0 and self.score > 0:
            col = (255, 210, 50) if self.score >= hs else C_UI_DIM
            txt = self.hud.font_tiny.render(
                f'Rekor: {hs}', True, col)
            self.screen.blit(txt, (SCREEN_W - txt.get_width() - 14, 58))

        # cursor
        mx, my = pygame.mouse.get_pos()
        cur = self.sprites.get('ui_cursor')
        if cur: self.screen.blit(cur, (mx-10, my-10))
        else:
            pygame.draw.circle(self.screen,(180,230,255),(mx,my),4,1)
            pygame.draw.circle(self.screen,(255,255,255),(mx,my),1)

        hint = self.hud.font_tiny.render('M = mute', True, C_UI_DIM)
        self.screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 5))

    def _draw_mola(self):
        m = self.mola
        key = 'mola_damage' if m.damage_flash > 0 \
              else 'mola_blink' if math.sin(m.blink_timer*0.7) > 0.97 \
              else 'mola_normal'
        spr = self.sprites.get(key)
        if spr:
            w = max(1, int(spr.get_width()  * m.size))
            h = max(1, int(spr.get_height() * m.size))
            sc = pygame.transform.scale(spr, (w, h))
            tilt = clamp(m.vel.x*0.04, -0.35, 0.35)
            if abs(tilt) > 0.02:
                sc = pygame.transform.rotate(sc, -math.degrees(tilt))
            if not m.facing_r:
                sc = pygame.transform.flip(sc, True, False)
            self.screen.blit(sc, sc.get_rect(
                center=(int(m.pos.x), int(m.pos.y))))
        else:
            m.draw(self.screen, self.time)

    # ── GAME OVER ─────────────────────────────────────────
    def _upd_over(self, dt):
        self.gameover_screen.update(dt)
        self.world.update(dt)
        self.daynight.update(dt)
        self.audio.fade_ambient(0.08, 1.0, dt)

    def _drw_over(self):
        self.daynight.draw_sky_overlay(self.screen)
        self.world.draw_environment(self.screen)
        self.world.draw_bubbles(self.screen)
        self.mola.draw(self.screen, self.time)
        self.gameover_screen.draw(self.screen, self.score)
        # stats
        hs   = self.save_data.get('highscore', 0)
        total= self.save_data.get('total_games', 0)
        new_record = self.score >= hs and self.score > 0
        if new_record:
            txt = self.hud.font_med.render(
                '★ REKOR BARU! ★', True, (255, 210, 50))
            self.screen.blit(txt,
                (SCREEN_W//2 - txt.get_width()//2, SCREEN_H//2 + 65))
        stats = self.hud.font_tiny.render(
            f'Rekor tertinggi: {hs}  |  Total sesi: {total}',
            True, C_UI_DIM)
        self.screen.blit(stats,
            (SCREEN_W//2 - stats.get_width()//2, SCREEN_H//2 + 90))

    def _blit_c(self, spr, pos, scale=1.0):
        if scale != 1.0:
            w = max(1, int(spr.get_width()*scale))
            h = max(1, int(spr.get_height()*scale))
            spr = pygame.transform.scale(spr, (w, h))
        self.screen.blit(spr, spr.get_rect(
            center=(int(pos.x), int(pos.y))))


if __name__ == '__main__':
    Game().run()
