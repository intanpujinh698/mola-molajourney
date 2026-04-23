# ============================================================
#  entities.py — Semua entitas game
# ============================================================
import random
import math
import pygame
from settings import *
from utils import lerp, lerp_vec, clamp, dist, normalise


# ═══════════════════════════════════════════════════════════
#  MOLA-MOLA (Player)
# ═══════════════════════════════════════════════════════════
class MolaMola:
    def __init__(self, x, y):
        self.pos      = pygame.Vector2(x, y)
        self.vel      = pygame.Vector2(0, 0)
        self.energy   = ENERGY_MAX
        self.vitality = VITALITY_MAX
        self.size     = MOLA_SIZE_MIN

        self.tangled        = False
        self.tangle_timer   = 0.0
        self.blink_timer    = 0.0
        self.surface_timer  = 0.0   # akumulasi waktu di permukaan
        self.damage_flash   = 0.0   # timer flash merah saat kena

        self.alive     = True
        self.facing_r  = True       # True = menghadap kanan

    # ── radius collision
    @property
    def radius(self) -> float:
        return self.size * 16

    # ── Update utama
    def update(self, dt: float, target: pygame.Vector2, depth_factor: float,
               particle_sys, at_surface: bool):
        if not self.alive:
            return

        self.blink_timer  += dt
        self.damage_flash  = max(0, self.damage_flash - dt)

        # ── Tangle
        if self.tangled:
            self.tangle_timer -= dt
            self.energy       -= TANGLED_DRAIN * dt
            if self.tangle_timer <= 0:
                self.tangled = False
        else:
            # ── Movement
            direction = target - self.pos
            if direction.length() > 1:
                direction = direction.normalize()
            speed   = MOLA_BASE_SPEED / (self.size * 0.6 + 0.4)
            target_vel = direction * speed
            self.vel   = lerp_vec(self.vel, target_vel, MOLA_LERP)

        self.pos += self.vel * dt
        self._clamp_to_screen()

        if self.vel.x > 0.5:
            self.facing_r = True
        elif self.vel.x < -0.5:
            self.facing_r = False

        # ── Energi
        if at_surface and not self.tangled:
            self.energy       = min(ENERGY_MAX, self.energy + ENERGY_REGEN_BASK * dt)
            self.surface_timer += dt
            if self.surface_timer > 0.15:
                particle_sys.emit_surface(self.pos.x, self.pos.y)
                self.surface_timer = 0
        else:
            self.surface_timer = 0
            drain = ENERGY_DRAIN_BASE + depth_factor * ENERGY_DRAIN_DEEP * 2.5
            self.energy -= drain * dt

        self.energy = clamp(self.energy, 0, ENERGY_MAX)

        # ── Vitalitas
        if self.energy <= 0:
            self.vitality -= VITALITY_DRAIN * dt

        if self.vitality <= 0:
            self.vitality = 0
            self.alive    = False

    def eat_jellyfish(self, particle_sys, jelly_color):
        self.size    = min(MOLA_SIZE_MAX, self.size + MOLA_SIZE_GROWTH)
        self.energy  = min(ENERGY_MAX, self.energy + ENERGY_FROM_JELLY)
        particle_sys.emit_eat(self.pos.x, self.pos.y, jelly_color)
        particle_sys.emit_bubble(self.pos.x, self.pos.y, 5)

    def take_damage(self, amount: float, particle_sys):
        self.vitality    -= amount
        self.damage_flash = 0.4
        particle_sys.emit_damage(self.pos.x, self.pos.y)

    def get_tangled(self):
        if not self.tangled:
            self.tangled      = True
            self.tangle_timer = TANGLED_DURATION
            self.vel.update(0, 0)

    def _clamp_to_screen(self):
        r = self.radius
        self.pos.x = clamp(self.pos.x, r, SCREEN_W - r)
        self.pos.y = clamp(self.pos.y, r, SCREEN_H - r)

    # ── Draw
    def draw(self, surface, time: float):
        x, y = int(self.pos.x), int(self.pos.y)
        s    = int(self.size * 18)

        # flash merah saat kena serangan
        use_damage = self.damage_flash > 0

        # tilt berdasarkan kecepatan
        tilt = clamp(self.vel.x * 0.04, -0.35, 0.35)

        # buat surface temp untuk rotasi
        sprite_w = s * 3
        sprite_h = s * 3
        spr = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)
        cx, cy = sprite_w // 2, sprite_h // 2

        self._draw_body(spr, cx, cy, s, time, use_damage)

        # flip jika menghadap kiri
        if not self.facing_r:
            spr = pygame.transform.flip(spr, True, False)

        # rotate tilt
        if abs(tilt) > 0.02:
            spr = pygame.transform.rotate(spr, -math.degrees(tilt))

        rect = spr.get_rect(center=(x, y))
        surface.blit(spr, rect)

        # tangle overlay
        if self.tangled:
            self._draw_tangle(surface, x, y, s, time)

    def _draw_body(self, spr, cx, cy, s, time, use_damage):
        # warna dasar
        body_col   = (180, 210, 235) if not use_damage else (255, 120, 120)
        shadow_col = (60, 110, 160)  if not use_damage else (180, 60, 60)
        fin_col    = (80, 140, 190)  if not use_damage else (200, 80, 80)

        # bayangan badan
        pygame.draw.ellipse(spr, shadow_col,
                            (cx - s + 4, cy - int(s*0.82) + 4,
                             s*2, int(s*1.65)))

        # badan utama
        pygame.draw.ellipse(spr, body_col,
                            (cx - s, cy - int(s*0.82),
                             s*2, int(s*1.65)))

        # highlight
        hl = pygame.Surface((s, int(s*0.7)), pygame.SRCALPHA)
        hl.fill((0,0,0,0))
        pygame.draw.ellipse(hl, (255, 255, 255, 40),
                            (0, 0, s, int(s*0.7)))
        spr.blit(hl, (cx - s//2, cy - int(s*0.6)))

        # sirip dorsal (atas)
        pts_d = [
            (cx - int(s*0.2), cy - int(s*0.82)),
            (cx,              cy - int(s*1.35)),
            (cx + int(s*0.3), cy - int(s*0.82)),
        ]
        pygame.draw.polygon(spr, fin_col, pts_d)

        # sirip ventral (bawah)
        pts_v = [
            (cx - int(s*0.2), cy + int(s*0.82)),
            (cx,              cy + int(s*1.35)),
            (cx + int(s*0.3), cy + int(s*0.82)),
        ]
        pygame.draw.polygon(spr, fin_col, pts_v)

        # sirip ekor (clavus)
        pts_c = [
            (cx - int(s*0.85), cy - int(s*0.5)),
            (cx - int(s*1.2),  cy - int(s*0.85)),
            (cx - int(s*0.95), cy),
            (cx - int(s*1.2),  cy + int(s*0.85)),
            (cx - int(s*0.85), cy + int(s*0.5)),
        ]
        pygame.draw.polygon(spr, fin_col, pts_c)

        # tekstur badan (garis elips)
        for i in range(1, 4):
            ew = max(2, int(s * 0.3 * i))
            eh = max(2, int(s * 0.25 * i))
            surf_line = pygame.Surface((ew*2, int(eh*1.65)*2), pygame.SRCALPHA)
            pygame.draw.ellipse(surf_line, (255, 255, 255, 18),
                                (0, 0, ew*2, int(eh*1.65)*2), 1)
            spr.blit(surf_line, (cx - ew, cy - int(eh*0.82)))

        # mata
        eye_x = cx + int(s * 0.38)
        eye_y = cy - int(s * 0.15)
        eye_r = max(2, int(s * 0.09))
        blink = math.sin(self.blink_timer * 0.7) > 0.97
        if blink:
            pygame.draw.ellipse(spr, (10, 25, 40),
                                (eye_x - eye_r, eye_y - 2, eye_r*2, 4))
        else:
            pygame.draw.circle(spr, (10, 25, 40), (eye_x, eye_y), eye_r)
            pygame.draw.circle(spr, (255, 255, 255),
                               (eye_x + max(1, eye_r//3),
                                eye_y - max(1, eye_r//3)),
                               max(1, eye_r//3))

    def _draw_tangle(self, surface, x, y, s, time):
        rope_col = (180, 130, 60, 160)
        rope_s   = alpha_surface_local(SCREEN_W, SCREEN_H)
        for i in range(3):
            start = (x - s + int(math.sin(time*8+i)*6),
                     int(y + (-s + i*s)*0.6))
            end   = (x + s//2, y - s//2 + i*s//2)
            pygame.draw.line(rope_s, rope_col, start, end, 2)
        surface.blit(rope_s, (0, 0))


def alpha_surface_local(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0,0,0,0))
    return s


# ═══════════════════════════════════════════════════════════
#  JELLYFISH
# ═══════════════════════════════════════════════════════════
class Jellyfish:
    COLORS = [
        (200, 100, 220),  # ungu
        (100, 180, 240),  # biru
        (240, 120, 160),  # pink
        (120, 220, 200),  # teal
        (240, 200, 100),  # kuning
    ]

    def __init__(self, x=None, y=None):
        self.pos     = pygame.Vector2(
            x if x else random.uniform(40, SCREEN_W - 40),
            y if y else random.uniform(80, SCREEN_H - 60)
        )
        self.r       = random.uniform(JELLY_SIZE_MIN, JELLY_SIZE_MAX)
        self.vel     = pygame.Vector2(
            random.uniform(-JELLY_SPEED, JELLY_SPEED),
            random.uniform(0.1, 0.3)
        )
        self.bob     = random.uniform(0, math.pi * 2)
        self.bob_spd = random.uniform(0.8, 1.6)
        self.pulse   = random.uniform(0, math.pi * 2)
        self.alive   = True
        self.eaten_at = 0.0
        self._assign_type()

    def _assign_type(self):
        from settings import JELLY_TYPES, JELLY_TYPE_WEIGHTS
        keys    = list(JELLY_TYPES.keys())
        weights = JELLY_TYPE_WEIGHTS
        self.jtype        = random.choices(keys, weights=weights, k=1)[0]
        data              = JELLY_TYPES[self.jtype]
        self.color        = data['color']
        self.effect_energy= data['energy']
        self.effect_vita  = data['vitality']
        self.effect_size  = data['size']
        self.label        = data['label']
        if self.jtype == 'giant':
            self.r = random.uniform(22, 30)
        elif self.jtype == 'golden':
            self.r = random.uniform(14, 20)
        elif self.jtype == 'poison':
            self.r = random.uniform(8, 14)

    def update(self, dt, time):
        self.bob   += self.bob_spd * dt
        self.pulse += dt * 2.0
        self.pos.x += self.vel.x + math.sin(time * 0.8 + self.bob) * 0.4
        self.pos.y += self.vel.y + math.sin(time * 1.2 + self.bob) * 0.3

        # wrap horizontal
        if self.pos.x < -50: self.pos.x = SCREEN_W + 50
        if self.pos.x > SCREEN_W + 50: self.pos.x = -50
        # wrap vertical
        if self.pos.y > SCREEN_H + 50: self.pos.y = -50
        if self.pos.y < -50: self.pos.y = SCREEN_H + 50

    def draw(self, surface, time):
        x, y   = int(self.pos.x), int(self.pos.y)
        r      = int(self.r)
        pulse  = 1 + math.sin(self.pulse) * 0.08
        rp     = int(r * pulse)
        rh     = int(r * 0.7 * pulse)
        rc, gc, bc = self.color

        # glow
        glow_s = alpha_surface_local(rp*6, rp*6)
        pygame.draw.ellipse(glow_s, (rc, gc, bc, 30),
                            (rp, rp//2, rp*4, rp*2))
        surface.blit(glow_s, (x - rp*3, y - rp*3//2))

        # bell (setengah lingkaran atas)
        bell_s = alpha_surface_local(rp*2+4, rh+4)
        pygame.draw.ellipse(bell_s, (rc, gc, bc, 180),
                            (2, 2, rp*2, rh*2))
        surface.blit(bell_s, (x - rp - 2, y - rh - 2))

        # garis dalam bell
        inner_s = alpha_surface_local(rp*2, rh)
        pygame.draw.ellipse(inner_s, (255, 255, 255, 40),
                            (rp//3, 2, rp, rh-4), 1)
        surface.blit(inner_s, (x - rp, y - rh))

        # tentakel
        for i in range(-2, 3):
            tx = x + i * (rp // 3)
            for k in range(4):
                ty1 = y + k * (r // 2)
                ty2 = y + (k+1) * (r // 2)
                wave = int(math.sin(time * 2 + i + k) * rp * 0.25)
                tent_s = alpha_surface_local(abs(wave)*2+4, ty2-ty1+2)
                pygame.draw.line(tent_s, (rc, gc, bc, 100),
                                 (abs(wave), 0), (abs(wave)+wave, ty2-ty1), 1)
                surface.blit(tent_s, (tx - abs(wave), ty1))


# ═══════════════════════════════════════════════════════════
#  JARING NELAYAN
# ═══════════════════════════════════════════════════════════
class FishingNet:
    def __init__(self):
        self.respawn()

    def respawn(self):
        side       = random.choice(['left', 'right'])
        self.w     = NET_W
        self.h     = NET_H
        if side == 'left':
            self.pos = pygame.Vector2(-self.w - 10,
                                      random.uniform(60, SCREEN_H - 60))
            self.vx  = random.uniform(NET_SPEED_MIN, NET_SPEED_MAX)
        else:
            self.pos = pygame.Vector2(SCREEN_W + 10,
                                      random.uniform(60, SCREEN_H - 60))
            self.vx  = -random.uniform(NET_SPEED_MIN, NET_SPEED_MAX)

        self.vy    = random.uniform(-20, 20)
        self.time  = 0.0
        self.alive = True

    def update(self, dt):
        self.time   += dt
        self.pos.x  += self.vx * dt
        self.pos.y  += self.vy * dt + math.sin(self.time * 0.8) * 0.3

        # bouncing vertical
        if self.pos.y < 40 or self.pos.y > SCREEN_H - 40:
            self.vy *= -1

        # respawn jika keluar layar
        if self.pos.x < -200 or self.pos.x > SCREEN_W + 200:
            self.respawn()

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.w, self.h)

    def draw(self, surface):
        x, y = int(self.pos.x), int(self.pos.y)
        cell_w = self.w // 5
        cell_h = self.h // 5
        rope_col  = (200, 175, 95, 180)
        float_col = (255, 140, 30)

        net_s = alpha_surface_local(self.w + 20, self.h + 20)
        ox, oy = 10, 10

        # grid
        for r in range(6):
            pygame.draw.line(net_s, rope_col,
                             (ox, oy + r*cell_h), (ox + self.w, oy + r*cell_h), 1)
        for c in range(6):
            pygame.draw.line(net_s, rope_col,
                             (ox + c*cell_w, oy), (ox + c*cell_w, oy + self.h), 1)

        # tali atas
        pygame.draw.line(net_s, (220, 185, 80, 230),
                         (ox - 5, oy), (ox + self.w + 5, oy), 2)

        # pelampung
        for c in range(6):
            pygame.draw.circle(net_s, float_col, (ox + c*cell_w, oy), 5)

        surface.blit(net_s, (x - 10, y - 10))


# ═══════════════════════════════════════════════════════════
#  HARE / PREDATOR (Hiu)
# ═══════════════════════════════════════════════════════════
class Shark:
    STATE_PATROL  = 'patrol'
    STATE_CHASE   = 'chase'
    STATE_RETREAT = 'retreat'

    def __init__(self):
        self.respawn()

    def respawn(self):
        self.pos      = pygame.Vector2(
            random.choice([random.uniform(-100, -50),
                           random.uniform(SCREEN_W+50, SCREEN_W+100)]),
            random.uniform(SCREEN_H * 0.3, SCREEN_H * 0.85)
        )
        self.vel      = pygame.Vector2(0, 0)
        self.state    = self.STATE_PATROL
        self.patrol_target = self._rand_patrol()
        self.attack_cd    = 0.0
        self.retreat_timer= 0.0
        self.facing_r = self.pos.x < SCREEN_W / 2
        self.alive    = True

    def _rand_patrol(self):
        return pygame.Vector2(
            random.uniform(80, SCREEN_W - 80),
            random.uniform(SCREEN_H * 0.25, SCREEN_H * 0.9)
        )

    def update(self, dt, mola: MolaMola, particle_sys):
        self.attack_cd = max(0, self.attack_cd - dt)

        d = dist(self.pos.x, self.pos.y, mola.pos.x, mola.pos.y)

        # state machine
        if self.state == self.STATE_PATROL:
            if d < SHARK_DETECT_RANGE and mola.alive:
                self.state = self.STATE_CHASE
            else:
                # bergerak ke patrol target
                direction = self.patrol_target - self.pos
                if direction.length() < 20:
                    self.patrol_target = self._rand_patrol()
                elif direction.length() > 0:
                    direction = direction.normalize()
                    target_v = direction * SHARK_SPEED_BASE * 0.5
                    self.vel = lerp_vec(self.vel, target_v, 0.05)

        elif self.state == self.STATE_CHASE:
            if d > SHARK_DETECT_RANGE * 1.5 or not mola.alive:
                self.state = self.STATE_PATROL
                self.patrol_target = self._rand_patrol()
            else:
                # kejar mola
                direction = mola.pos - self.pos
                if direction.length() > 0:
                    direction = direction.normalize()
                target_v  = direction * SHARK_SPEED_BASE
                self.vel  = lerp_vec(self.vel, target_v, 0.08)

                # serang jika dekat
                if d < SHARK_ATTACK_RANGE and self.attack_cd <= 0 and mola.alive:
                    mola.take_damage(SHARK_VITALITY_DMG, particle_sys)
                    self.attack_cd = SHARK_COOLDOWN
                    self.state     = self.STATE_RETREAT
                    self.retreat_timer = 0.8

        elif self.state == self.STATE_RETREAT:
            self.retreat_timer -= dt
            direction = self.pos - mola.pos
            if direction.length() > 0:
                direction = direction.normalize()
            target_v  = direction * SHARK_SPEED_BASE * 0.7
            self.vel  = lerp_vec(self.vel, target_v, 0.06)
            if self.retreat_timer <= 0:
                self.state = self.STATE_CHASE

        self.pos += self.vel * dt

        if self.vel.x > 0.5:  self.facing_r = True
        elif self.vel.x < -0.5: self.facing_r = False

        # keluar layar → respawn
        margin = 200
        if (self.pos.x < -margin or self.pos.x > SCREEN_W + margin or
                self.pos.y < -margin or self.pos.y > SCREEN_H + margin):
            self.respawn()

    def draw(self, surface, time):
        x, y = int(self.pos.x), int(self.pos.y)
        chasing = self.state == self.STATE_CHASE

        spr_w, spr_h = 100, 50
        spr = alpha_surface_local(spr_w, spr_h)
        cx, cy = spr_w // 2, spr_h // 2

        body_col = (80, 110, 130) if not chasing else (100, 80, 80)
        belly    = (200, 210, 215)
        fin_col  = (60, 90, 110)  if not chasing else (90, 60, 60)

        # ekor
        tail_pts = [
            (cx - 40, cy - 15),
            (cx - 55, cy - 25),
            (cx - 45, cy),
            (cx - 55, cy + 25),
            (cx - 40, cy + 15),
        ]
        pygame.draw.polygon(spr, fin_col, tail_pts)

        # badan
        pygame.draw.ellipse(spr, body_col, (cx - 35, cy - 14, 70, 28))
        # perut
        pygame.draw.ellipse(spr, belly,    (cx - 20, cy - 6, 40, 14))

        # sirip dorsal
        pts_d = [(cx - 5, cy - 14), (cx + 5, cy - 28), (cx + 18, cy - 14)]
        pygame.draw.polygon(spr, fin_col, pts_d)

        # sirip pektoral
        pts_p = [(cx - 5, cy + 5), (cx + 8, cy + 22), (cx + 18, cy + 5)]
        pygame.draw.polygon(spr, fin_col, pts_p)

        # mulut (menganga saat mengejar)
        if chasing:
            mouth_pts = [
                (cx + 32, cy - 4),
                (cx + 44, cy - 10),
                (cx + 44, cy + 10),
                (cx + 32, cy + 4),
            ]
            pygame.draw.polygon(spr, (20, 15, 15), mouth_pts)
            # gigi
            for i in range(3):
                gx = cx + 34 + i * 3
                pygame.draw.polygon(spr, (230, 230, 230), [
                    (gx, cy - 3), (gx+2, cy - 8), (gx+4, cy - 3)
                ])
        else:
            pygame.draw.line(spr, (40, 40, 50),
                             (cx + 32, cy), (cx + 44, cy), 2)

        # mata
        pygame.draw.circle(spr, (10, 10, 15), (cx + 22, cy - 4), 4)
        pygame.draw.circle(spr, (255,255,255), (cx + 23, cy - 5), 1)

        if not self.facing_r:
            spr = pygame.transform.flip(spr, True, False)

        # indicator lingkaran deteksi (debug — bisa di-disable)
        # pygame.draw.circle(surface, (255,0,0,40), (x,y), SHARK_DETECT_RANGE, 1)

        rect = spr.get_rect(center=(x, y))
        surface.blit(spr, rect)
