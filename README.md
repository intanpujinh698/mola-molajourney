# 🐟 Mola-Mola Journey
**Survival Simulation Game — Python + Pygame**

---

## Setup (1 menit)

### 1. Pastikan Python terinstall
```
python --version
```
Minimal Python 3.9+

### 2. Install Pygame
```
pip install pygame
```

### 3. Jalankan game
```
cd MolaMolaJourney
python main.py
```

---

## Cara Bermain

| Aksi | Kontrol |
|------|---------|
| Gerak | Geser Mouse |
| Berjemur | Arahkan ke area permukaan (atas layar) |
| Makan | Dekati ubur-ubur |
| Hindari | Jaring nelayan & hiu |
| Restart | Tekan R (saat game over) |
| Keluar | ESC |

---

## Mekanika Game

### Status Bar
- **Energi** 🟡 — Terus berkurang. Pulih saat berjemur di permukaan.
  Makin dalam → makin cepat terkuras.
- **Vitalitas** 🔴 — Berkurang saat energi habis atau kena serangan hiu.
  Kalau habis → GAME OVER.
- **Ukuran** 🟢 — Bertambah tiap makan ubur-ubur.
  Makin besar → makin lambat, tapi jangkauan makan lebih luas.

### Ancaman
- **Jaring Nelayan** — Bergerak melintasi layar. Jika kena → Terjerat (tidak bisa bergerak, energi terkuras cepat).
- **Hiu** — Berpatroli dan mengejar jika mendeteksi Mola-Mola. Menyerang saat dekat, mengurangi vitalitas langsung.

### Zona Kedalaman
- **Permukaan** (0–80px) — Zona berjemur, energi pulih
- **Dangkal** (80–200px) — Aman, banyak ubur-ubur
- **Dalam** (200–380px) — Energi terkuras lebih cepat
- **Abyss** (380px+) — Sangat berbahaya, hindari

---

## Struktur Proyek

```
MolaMolaJourney/
├── main.py          ← Entry point & game loop
├── settings.py      ← Semua konstanta & konfigurasi
├── entities.py      ← MolaMola, Jellyfish, FishingNet, Shark
├── world.py         ← Environment, background, terumbu karang
├── particles.py     ← Sistem partikel visual
├── hud.py           ← UI overlay, status bars, layar menu
└── utils.py         ← Helper functions (lerp, clamp, dll)
```

---

## Pengembangan Selanjutnya (Roadmap)

- [ ] Sprite asli (mengganti procedural drawing)
- [ ] Sistem siang/malam (pencahayaan dinamis)
- [ ] Lebih banyak jenis ubur-ubur (efek berbeda)
- [ ] Boss encounter (kapal nelayan)
- [ ] Save & highscore
- [ ] Sound effects & musik
- [ ] Export ke executable (PyInstaller)
