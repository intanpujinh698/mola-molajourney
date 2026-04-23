#!/usr/bin/env python3
# ============================================================
#  build_exe.py — Export Mola-Mola Journey ke .exe
#
#  Jalankan:
#    pip install pyinstaller
#    python build_exe.py
#
#  Output: dist/MolaMolaJourney/MolaMolaJourney.exe
# ============================================================
import os
import sys
import subprocess
import shutil

# ── Pastikan semua asset sudah di-generate dulu
if not os.path.exists('assets/sprites') or \
   not os.path.exists('assets/sounds'):
    print('ERROR: Folder assets belum ada.')
    print('Jalankan dulu:')
    print('  python generate_sprites.py')
    print('  python generate_sounds.py')
    sys.exit(1)

# ── Cek PyInstaller
try:
    import PyInstaller
    print(f'PyInstaller {PyInstaller.__version__} ditemukan.')
except ImportError:
    print('PyInstaller belum terinstall. Install dulu:')
    print('  pip install pyinstaller')
    sys.exit(1)

# ── Bersihkan build lama
for folder in ('build', 'dist', '__pycache__'):
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f'Cleaned: {folder}')

# ── PyInstaller command
# Windows pakai ; sebagai separator, Linux/Mac pakai :
SEP = ';' if sys.platform == 'win32' else ':'

cmd = [
    'pyinstaller',
    '--onedir',           # satu folder (lebih cepat launch daripada --onefile)
    '--windowed',         # tidak ada console window
    '--name', 'MolaMolaJourney',
    '--add-data', f'assets/sprites{SEP}assets/sprites',
    '--add-data', f'assets/sounds{SEP}assets/sounds',
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
    print('\n' + '='*50)
    print('BUILD BERHASIL!')
    print(f'Output: dist/MolaMolaJourney/MolaMolaJourney.exe')
    print()
    print('Cara distribusi:')
    print('  Zip seluruh folder dist/MolaMolaJourney/')
    print('  Bagikan ke siapapun — tidak perlu install Python/Pygame!')
    print('='*50)
else:
    print('\nBUILD GAGAL. Periksa error di atas.')
    sys.exit(1)
