# Mola-Mola Journey

Survival simulation game sederhana yang dibuat dengan Python dan Pygame. Pemain mengendalikan mola-mola, mencari makanan, berjemur untuk memulihkan energi, dan menghindari jaring nelayan serta hiu.

## Fitur

- Kontrol berbasis mouse yang mudah dimainkan.
- Sistem energi, vitalitas, ukuran, dan kedalaman.
- Musuh dan rintangan: jaring nelayan, hiu, dan boss encounter.
- Sistem siang/malam dengan pencahayaan dinamis.
- Asset sprite dan sound dibuat otomatis dari script generator.
- Bisa dibuild menjadi aplikasi Windows `.exe` memakai PyInstaller.

## Menjalankan Game dari Source

Pastikan Python 3.9 atau lebih baru sudah terinstall.

```powershell
git clone https://github.com/intanpujinh698/mola-molajourney.git
cd mola-molajourney
python -m pip install -r requirements.txt
python generate_sprites.py
python generate_sounds.py
python main.py
```

Di Windows, kamu juga bisa menjalankan:

```powershell
run.bat
```

## Cara Bermain

| Aksi | Kontrol |
| --- | --- |
| Gerak | Geser mouse |
| Berjemur | Arahkan mola-mola ke area permukaan |
| Makan | Dekati ubur-ubur |
| Hindari | Jaring nelayan dan hiu |
| Restart | Tekan `R` saat game over |
| Keluar | Tekan `Esc` |

## Mekanika Game

- Energi berkurang seiring waktu dan pulih saat berjemur di permukaan.
- Vitalitas berkurang saat energi habis atau terkena serangan.
- Ukuran bertambah saat memakan ubur-ubur.
- Area yang lebih dalam membuat energi terkuras lebih cepat.
- Jika vitalitas habis, permainan berakhir.

## Build Menjadi Aplikasi Windows

Install dependency lalu jalankan script build:

```powershell
python -m pip install -r requirements.txt
python build_exe.py
```

Atau cukup jalankan:

```powershell
build.bat
```

Hasil build ada di:

```text
dist/MolaMolaJourney/MolaMolaJourney.exe
```

Untuk membagikan game ke PC lain, zip seluruh folder:

```text
dist/MolaMolaJourney
```

Jangan hanya mengirim file `.exe`, karena mode build `--onedir` membutuhkan file pendamping di folder yang sama.

## Struktur Proyek

```text
mola-molajourney/
├── main.py              # Entry point dan game loop
├── settings.py          # Konstanta dan konfigurasi
├── entities.py          # MolaMola, Jellyfish, FishingNet, Shark
├── boss.py              # Boss encounter
├── world.py             # Environment dan background
├── particles.py         # Sistem partikel visual
├── daynight.py          # Sistem siang/malam
├── hud.py               # UI overlay dan layar menu
├── audio.py             # Audio manager
├── save.py              # Save data
├── generate_sprites.py  # Generator sprite
├── generate_sounds.py   # Generator sound
├── build_exe.py         # Build aplikasi Windows
└── requirements.txt     # Dependency Python
```
