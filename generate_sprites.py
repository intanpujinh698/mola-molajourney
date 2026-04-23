#!/usr/bin/env python3
# ============================================================
#  generate_sprites.py
#  Jalankan SEKALI untuk generate semua sprite PNG:
#    python generate_sprites.py
#  Output: folder assets/sprites/
# ============================================================
import os
import math
import pygame

# Harus set env SEBELUM pygame.init()
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pygame.init()
# Windows fallback: jika dummy driver gagal, buka window kecil tersembunyi
try:
    screen = pygame.display.set_mode((1, 1))
except Exception:
    os.environ.pop('SDL_VIDEODRIVER', None)
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    pygame.display.iconify()  # minimize otomatis

OUT = 'assets/sprites'
os.makedirs(OUT, exist_ok=True)

def alpha(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    return s

def save(surf, name):
    path = os.path.join(OUT, name)
    pygame.image.save(surf, path)
    print(f'  saved: {path}')

# ═══════════════════════════════════════════════════════════
#  MOLA-MOLA  (4 frame animasi: normal, blink, tangle, damage)
# ═══════════════════════════════════════════════════════════
def draw_mola_frame(size=80, eye_blink=False, damage=False):
    W = size * 3
    H = size * 3
    s = alpha(W, H)
    cx, cy = W // 2, H // 2

    body_col   = (180, 210, 235) if not damage else (255, 130, 130)
    shadow_col = (55, 105, 155)  if not damage else (180, 70, 70)
    fin_col    = (75, 135, 185)  if not damage else (200, 90, 90)
    hl_col     = (220, 240, 255, 55)

    sz = size

    # bayangan
    pygame.draw.ellipse(s, shadow_col,
        (cx-sz+5, cy-int(sz*.82)+5, sz*2, int(sz*1.65)))
    # badan
    pygame.draw.ellipse(s, body_col,
        (cx-sz, cy-int(sz*.82), sz*2, int(sz*1.65)))
    # highlight
    hl = alpha(sz, int(sz*.7))
    pygame.draw.ellipse(hl, hl_col, (0, 0, sz, int(sz*.7)))
    s.blit(hl, (cx-sz//2, cy-int(sz*.6)))

    # tekstur elips
    for i in range(1, 5):
        ew = max(2, int(sz*.28*i))
        eh = max(2, int(sz*.23*i))
        tl = alpha(ew*2+2, int(eh*1.65)*2+2)
        pygame.draw.ellipse(tl, (255,255,255,22),
            (0,0,ew*2,int(eh*1.65)*2), 1)
        s.blit(tl, (cx-ew, cy-int(eh*.82)))

    # sirip dorsal
    pygame.draw.polygon(s, fin_col, [
        (cx-int(sz*.2), cy-int(sz*.82)),
        (cx,            cy-int(sz*1.38)),
        (cx+int(sz*.32),cy-int(sz*.82)),
    ])
    # sirip ventral
    pygame.draw.polygon(s, fin_col, [
        (cx-int(sz*.2), cy+int(sz*.82)),
        (cx,            cy+int(sz*1.38)),
        (cx+int(sz*.32),cy+int(sz*.82)),
    ])
    # clavus (ekor)
    pygame.draw.polygon(s, fin_col, [
        (cx-int(sz*.85), cy-int(sz*.5)),
        (cx-int(sz*1.22),cy-int(sz*.88)),
        (cx-int(sz*.95), cy),
        (cx-int(sz*1.22),cy+int(sz*.88)),
        (cx-int(sz*.85), cy+int(sz*.5)),
    ])
    # outline tipis
    pygame.draw.ellipse(s, (40,80,120),
        (cx-sz, cy-int(sz*.82), sz*2, int(sz*1.65)), 1)

    # mata
    ex = cx + int(sz*.38)
    ey = cy - int(sz*.15)
    er = max(3, int(sz*.1))
    if eye_blink:
        pygame.draw.ellipse(s, (10,25,40),
            (ex-er, ey-2, er*2, 4))
    else:
        pygame.draw.circle(s, (10,25,40), (ex,ey), er)
        pygame.draw.circle(s, (255,255,255),
            (ex+max(1,er//3), ey-max(1,er//3)), max(1,er//3))

    return s

# simpan 4 frame
for name, blink, dmg in [
    ('mola_normal.png',  False, False),
    ('mola_blink.png',   True,  False),
    ('mola_damage.png',  False, True),
]:
    save(draw_mola_frame(80, blink, dmg), name)

print('[Mola-Mola sprites OK]')

# ═══════════════════════════════════════════════════════════
#  JELLYFISH  (5 warna × 1 frame)
# ═══════════════════════════════════════════════════════════
JELLY_COLORS = {
    'purple': (200,100,220),
    'blue'  : (100,180,240),
    'pink'  : (240,120,160),
    'teal'  : (120,220,200),
    'yellow': (240,200,100),
}

def draw_jellyfish(color, r=28):
    W = H = r * 6
    s = alpha(W, H)
    cx, cy = W//2, H//2
    rc, gc, bc = color

    # glow
    for step in range(5):
        gr = r + step * 4
        ga = 18 - step * 3
        glow = alpha(gr*2, gr*2)
        pygame.draw.ellipse(glow, (rc,gc,bc,ga), (0,0,gr*2,int(gr*1.2)))
        s.blit(glow, (cx-gr, cy-int(gr*.6)))

    # bell
    bell = alpha(r*2+4, int(r*1.5)+4)
    pygame.draw.ellipse(bell, (rc,gc,bc,200), (2,2, r*2, int(r*1.4)))
    pygame.draw.ellipse(bell, (255,255,255,35), (r//2,4, r, int(r*.6)))
    pygame.draw.ellipse(bell, (rc,gc,bc,80), (2,2, r*2, int(r*1.4)), 1)
    s.blit(bell, (cx-r-2, cy-int(r*.7)-2))

    # tentakel
    for i in range(-2, 3):
        tx = cx + i * (r//3)
        for k in range(5):
            ty1 = cy + k*(r//2)
            ty2 = cy + (k+1)*(r//2)
            wave = int(math.sin(k*1.2 + i*0.8)*r*.25)
            tent = alpha(abs(wave)*2+4, ty2-ty1+2)
            pygame.draw.line(tent, (rc,gc,bc,90+k*10),
                (abs(wave), 0), (abs(wave)+wave, ty2-ty1), 1)
            s.blit(tent, (tx-abs(wave), ty1))
    return s

for cname, col in JELLY_COLORS.items():
    save(draw_jellyfish(col), f'jelly_{cname}.png')

print('[Jellyfish sprites OK]')

# ═══════════════════════════════════════════════════════════
#  SHARK  (normal + chase)
# ═══════════════════════════════════════════════════════════
def draw_shark(chasing=False):
    W, H = 120, 60
    s = alpha(W, H)
    cx, cy = W//2, H//2

    body_col = (80,110,130) if not chasing else (110,85,85)
    belly    = (200,210,215)
    fin_col  = (60,90,110)  if not chasing else (95,65,65)

    # ekor
    pygame.draw.polygon(s, fin_col, [
        (cx-48, cy-18), (cx-64, cy-28),
        (cx-52, cy),
        (cx-64, cy+28), (cx-48, cy+18),
    ])
    # badan
    pygame.draw.ellipse(s, body_col, (cx-42, cy-16, 84, 32))
    # perut
    pygame.draw.ellipse(s, belly, (cx-24, cy-7, 48, 16))
    # highlight
    hl = alpha(50, 10)
    pygame.draw.ellipse(hl, (255,255,255,40), (0,0,50,10))
    s.blit(hl, (cx-22, cy-13))
    # sirip dorsal
    pygame.draw.polygon(s, fin_col, [
        (cx-6, cy-16),(cx+6, cy-32),(cx+22, cy-16)])
    # sirip pektoral
    pygame.draw.polygon(s, fin_col, [
        (cx-6, cy+6),(cx+10, cy+26),(cx+22, cy+6)])
    # mulut
    if chasing:
        pygame.draw.polygon(s, (20,15,15), [
            (cx+38,cy-5),(cx+52,cy-12),
            (cx+52,cy+12),(cx+38,cy+5)])
        for gi in range(4):
            gx = cx+40+gi*3
            pygame.draw.polygon(s,(230,230,230),[
                (gx,cy-4),(gx+2,cy-10),(gx+4,cy-4)])
    else:
        pygame.draw.line(s,(40,40,50),(cx+38,cy),(cx+52,cy),2)
    # mata
    pygame.draw.circle(s,(10,10,15),(cx+26,cy-4),5)
    pygame.draw.circle(s,(255,255,255),(cx+27,cy-5),1)
    # outline
    pygame.draw.ellipse(s,(40,65,85),(cx-42,cy-16,84,32),1)
    return s

save(draw_shark(False), 'shark_patrol.png')
save(draw_shark(True),  'shark_chase.png')
print('[Shark sprites OK]')

# ═══════════════════════════════════════════════════════════
#  CORAL  (3 tipe × 3 warna)
# ═══════════════════════════════════════════════════════════
CORAL_COLS = [
    (200,80,100), (240,120,50), (80,180,160)
]

def draw_coral_branch(color):
    W, H = 70, 90
    s = alpha(W, H)
    r, g, b = color
    for i in range(3):
        ox = 10 + i*20
        pygame.draw.line(s,(r//2,g//2,b//2),(ox,H-5),(ox+5,H//2),3)
        pygame.draw.line(s,(r,g,b),(ox+5,H//2),(ox-8,H//2-25),2)
        pygame.draw.line(s,(r,g,b),(ox+5,H//2),(ox+18,H//2-25),2)
        pygame.draw.circle(s,(r,g,b),(ox-8,H//2-25),3)
        pygame.draw.circle(s,(r,g,b),(ox+18,H//2-25),3)
        pygame.draw.circle(s,(r,g,b),(ox+5,H//2-35),3)
    return s

def draw_coral_fan(color):
    W, H = 60, 80
    s = alpha(W, H)
    r, g, b = color
    for i in range(8):
        angle = math.pi*0.1 + i*(math.pi*0.8/7)
        ex = int(W//2 + math.cos(angle)*40)
        ey = int(H - math.sin(angle)*55)
        pygame.draw.line(s,(r,g,b),(W//2,H-5),(ex,ey),2)
    return s

def draw_coral_mound(color):
    W, H = 55, 45
    s = alpha(W, H)
    r, g, b = color
    pygame.draw.ellipse(s,(r//2,g//2,b//2),(4,H//2,W-8,H//2))
    for i in range(6):
        px = 6 + i*(W-12)//5
        pygame.draw.circle(s,(r,g,b),(px,H//2),5)
        pygame.draw.circle(s,(min(255,r+40),min(255,g+40),min(255,b+40)),(px,H//2-2),2)
    return s

for ci, col in enumerate(CORAL_COLS):
    save(draw_coral_branch(col), f'coral_branch_{ci}.png')
    save(draw_coral_fan(col),    f'coral_fan_{ci}.png')
    save(draw_coral_mound(col),  f'coral_mound_{ci}.png')

print('[Coral sprites OK]')

# ═══════════════════════════════════════════════════════════
#  UI ELEMENTS
# ═══════════════════════════════════════════════════════════
def draw_bar_bg(w=160, h=8):
    s = alpha(w, h)
    pygame.draw.rect(s, (20,35,60,200), (0,0,w,h), border_radius=4)
    pygame.draw.rect(s, (60,100,160,100), (0,0,w,h), 1, border_radius=4)
    return s

save(draw_bar_bg(), 'ui_bar_bg.png')

# cursor titik
def draw_cursor():
    s = alpha(20, 20)
    pygame.draw.circle(s,(180,230,255,180),(10,10),6,1)
    pygame.draw.circle(s,(255,255,255,240),(10,10),2)
    return s

save(draw_cursor(), 'ui_cursor.png')

print('\n✅ Semua sprite selesai di-generate!')
print(f'   Lokasi: {os.path.abspath(OUT)}')
pygame.quit()
