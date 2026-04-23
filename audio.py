# ============================================================
#  audio.py — Audio Manager
#  Mengelola semua sound effect dan musik ambient
# ============================================================
import os
import pygame


class AudioManager:
    """
    Singleton audio manager.
    Muat semua sound sekali, akses via metode semantik.
    """
    SOUND_DIR = os.path.join('assets', 'sounds')

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)

        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.enabled = True

        # Channel khusus
        self.ch_ambient = pygame.mixer.Channel(0)
        self.ch_warning = pygame.mixer.Channel(1)

        self._load_all()

    def _load(self, key: str, filename: str, volume: float = 1.0):
        path = os.path.join(self.SOUND_DIR, filename)
        if os.path.exists(path):
            snd = pygame.mixer.Sound(path)
            snd.set_volume(volume)
            self.sounds[key] = snd
        else:
            print(f'[Audio] Tidak ditemukan: {path}')

    def _load_all(self):
        self._load('eat',        'eat.wav',           volume=0.55)
        self._load('tangle',     'tangle.wav',        volume=0.75)
        self._load('damage',     'damage.wav',        volume=0.80)
        self._load('surface',    'surface.wav',       volume=0.40)
        self._load('gameover',   'gameover.wav',      volume=0.70)
        self._load('ambient',    'ambient_ocean.wav', volume=0.30)
        self._load('warning',    'warning_beep.wav',  volume=0.45)

    def play(self, key: str, loops: int = 0):
        if not self.enabled:
            return
        snd = self.sounds.get(key)
        if snd:
            snd.play(loops=loops)

    def play_eat(self):
        """Dimainkan saat makan ubur-ubur."""
        self.play('eat')

    def play_tangle(self):
        """Dimainkan saat terjerat jaring."""
        self.play('tangle')

    def play_damage(self):
        """Dimainkan saat diserang hiu."""
        self.play('damage')

    def play_surface(self):
        """Dimainkan saat mencapai permukaan untuk pertama kalinya."""
        if 'surface' in self.sounds:
            # hanya satu instance sekaligus
            if not pygame.mixer.Channel(2).get_busy():
                pygame.mixer.Channel(2).play(self.sounds['surface'])

    def play_gameover(self):
        """Dimainkan saat game over."""
        self.stop_ambient()
        self.play('gameover')

    def start_ambient(self):
        """Mulai loop ambient ocean."""
        if not self.enabled:
            return
        snd = self.sounds.get('ambient')
        if snd and not self.ch_ambient.get_busy():
            self.ch_ambient.play(snd, loops=-1)     # loop tak terbatas
            self.ch_ambient.set_volume(0.30)

    def stop_ambient(self):
        self.ch_ambient.stop()

    def start_warning(self):
        """Beep berulang saat energi kritis."""
        if not self.enabled:
            return
        snd = self.sounds.get('warning')
        if snd and not self.ch_warning.get_busy():
            self.ch_warning.play(snd, loops=-1)

    def stop_warning(self):
        self.ch_warning.stop()

    def fade_ambient(self, target_vol: float, speed: float, dt: float):
        """Fade ambient volume perlahan (panggil tiap frame)."""
        if not self.ch_ambient.get_busy():
            return
        cur = self.ch_ambient.get_volume()
        if abs(cur - target_vol) < 0.005:
            self.ch_ambient.set_volume(target_vol)
        else:
            new = cur + (target_vol - cur) * speed * dt
            self.ch_ambient.set_volume(max(0.0, min(1.0, new)))

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()

    def set_master_volume(self, vol: float):
        vol = max(0.0, min(1.0, vol))
        for snd in self.sounds.values():
            snd.set_volume(snd.get_volume() * vol)
