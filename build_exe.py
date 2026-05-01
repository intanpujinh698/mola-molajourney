#!/usr/bin/env python3
# ============================================================
#  build_exe.py - Export Mola-Mola Journey ke .exe
#
#  Jalankan:
#    python -m pip install -r requirements.txt
#    python build_exe.py
#
#  Output: dist/MolaMolaJourney/MolaMolaJourney.exe
# ============================================================
import os
import shutil
import subprocess
import sys


def run_step(args):
    result = subprocess.run(args, capture_output=False)
    if result.returncode != 0:
        sys.exit(result.returncode)


# Pastikan semua asset sudah di-generate dulu.
if not os.path.exists('assets/sprites'):
    print('Folder assets/sprites belum ada. Membuat sprite...')
    run_step([sys.executable, 'generate_sprites.py'])

if not os.path.exists('assets/sounds'):
    print('Folder assets/sounds belum ada. Membuat sound...')
    run_step([sys.executable, 'generate_sounds.py'])

# Cek PyInstaller.
try:
    import PyInstaller
    print(f'PyInstaller {PyInstaller.__version__} ditemukan.')
except ImportError:
    print('PyInstaller belum terinstall. Install dulu:')
    print('  python -m pip install pyinstaller')
    sys.exit(1)

# Bersihkan build lama.
for folder in ('build', 'dist', '__pycache__'):
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f'Cleaned: {folder}')

# Windows pakai ; sebagai separator, Linux/Mac pakai :
sep = ';' if sys.platform == 'win32' else ':'

cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--onedir',
    '--windowed',
    '--name', 'MolaMolaJourney',
    '--add-data', f'assets/sprites{sep}assets/sprites',
    '--add-data', f'assets/sounds{sep}assets/sounds',
    '--hidden-import', 'pygame',
    '--hidden-import', 'pygame.mixer',
    '--hidden-import', 'pygame.font',
    '--hidden-import', 'pygame.image',
    '--collect-all', 'pygame',
    'main.py',
]

print('\nMemulai build...')
print(' '.join(cmd))
print()

result = subprocess.run(cmd, capture_output=False)

if result.returncode == 0:
    print('\n' + '=' * 50)
    print('BUILD BERHASIL!')
    print('Output: dist/MolaMolaJourney/MolaMolaJourney.exe')
    print()
    print('Cara distribusi:')
    print('  Zip seluruh folder dist/MolaMolaJourney/')
    print('  Bagikan ke siapapun - tidak perlu install Python/Pygame!')
    print('=' * 50)
else:
    print('\nBUILD GAGAL. Periksa error di atas.')
    sys.exit(result.returncode)
