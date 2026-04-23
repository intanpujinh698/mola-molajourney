@echo off
title Build Mola-Mola Journey EXE

echo ================================
echo   Build Mola-Mola Journey .exe
echo ================================
echo.

:: Pastikan asset sudah ada
if not exist "assets\sprites" (
    echo Membuat sprite dulu...
    python generate_sprites.py
)
if not exist "assets\sounds" (
    echo Membuat sound dulu...
    python generate_sounds.py
)

:: Cek PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Menginstall PyInstaller...
    pip install pyinstaller
)

echo.
echo Memulai build...
python build_exe.py

echo.
echo Selesai! Cek folder dist\MolaMolaJourney\
pause
