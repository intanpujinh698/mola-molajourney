# ============================================================
#  settings.py — Mola-Mola Journey
# ============================================================

# ── Window
SCREEN_W       = 900
SCREEN_H       = 560
FPS            = 60
TITLE          = "Mola-Mola Journey"

# ── Zona kedalaman (pixel Y)
ZONE_SURFACE   = 80
ZONE_SHALLOW   = 200
ZONE_DEEP      = 380
ZONE_ABYSS     = 560

# ── Mola-Mola
MOLA_BASE_SPEED     = 220
MOLA_SIZE_MIN       = 1.0
MOLA_SIZE_MAX       = 4.0
MOLA_SIZE_GROWTH    = 0.10
MOLA_LERP           = 0.10

# Feel santai: drain lebih lambat, regen lebih cepat
ENERGY_MAX          = 100.0
ENERGY_DRAIN_BASE   = 2.5
ENERGY_DRAIN_DEEP   = 1.8
ENERGY_REGEN_BASK   = 32.0
ENERGY_FROM_JELLY   = 15.0

VITALITY_MAX        = 100.0
VITALITY_DRAIN      = 5.0
VITALITY_FROM_JELLY = 0.5

TANGLED_DURATION    = 2.0
TANGLED_DRAIN       = 25.0

# ── Ubur-ubur
JELLY_COUNT         = 12
JELLY_RESPAWN_MS    = 1000
JELLY_SIZE_MIN      = 10
JELLY_SIZE_MAX      = 24
JELLY_SPEED         = 0.35

# Tipe ubur-ubur: color, energy, vitality, size_bonus, label
JELLY_TYPES = {
    'normal':  {'color': (200,100,220), 'energy': 15,  'vitality': 0.5, 'size': 0.10, 'label': ''},
    'golden':  {'color': (255,210,50),  'energy': 35,  'vitality': 5.0, 'size': 0.05, 'label': '+ENERGI'},
    'healing': {'color': (100,230,160), 'energy': 8,   'vitality': 18,  'size': 0.05, 'label': '+VITALITAS'},
    'giant':   {'color': (180,100,255), 'energy': 20,  'vitality': 2.0, 'size': 0.25, 'label': '+UKURAN'},
    'poison':  {'color': (180,220,80),  'energy': -10, 'vitality': -8,  'size': 0.0,  'label': '! RACUN'},
    'blue':    {'color': (100,180,240), 'energy': 12,  'vitality': 1.0, 'size': 0.08, 'label': ''},
    'pink':    {'color': (240,120,160), 'energy': 10,  'vitality': 1.0, 'size': 0.08, 'label': ''},
    'teal':    {'color': (120,220,200), 'energy': 12,  'vitality': 1.5, 'size': 0.08, 'label': ''},
}
JELLY_TYPE_WEIGHTS = [60, 8, 8, 8, 6, 20, 20, 20]

# ── Jaring Nelayan (lebih sedikit & lebih lambat)
NET_COUNT           = 2
NET_SPEED_MIN       = 40
NET_SPEED_MAX       = 70
NET_W               = 75
NET_H               = 90

# ── Hiu (lebih jinak)
SHARK_COUNT         = 1
SHARK_SPEED_BASE    = 75
SHARK_DETECT_RANGE  = 140
SHARK_ATTACK_RANGE  = 30
SHARK_VITALITY_DMG  = 14
SHARK_COOLDOWN      = 2.5

# ── Boss Kapal Nelayan
BOSS_SPAWN_SCORE    = 15
BOSS_SPEED          = 50
BOSS_NET_INTERVAL   = 3.5
BOSS_W              = 160
BOSS_H              = 60

# ── Sistem Siang/Malam
DAY_DURATION        = 90.0    # detik per siklus penuh

# ── Terumbu Karang
CORAL_COUNT         = 15

# ── Highscore
SAVE_FILE           = 'save.json'

# ── Warna
C_BG_TOP        = (10,  40,  80)
C_BG_BOT        = (2,   10,  22)
C_SURFACE       = (100, 200, 255)
C_UI_TEXT       = (180, 220, 255)
C_UI_DIM        = (80,  130, 180)
C_ENERGY_HI     = (240, 200,  40)
C_ENERGY_LO     = (220,  80,  30)
C_VITALITY      = (220,  60,  60)
C_SIZE_BAR      = (30,  180, 140)
C_WARNING       = (255, 100,  40)
