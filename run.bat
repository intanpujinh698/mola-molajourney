@echo off
title Mola-Mola Journey

echo ================================
echo   Mola-Mola Journey
echo ================================
echo.

:: Cek apakah pygame sudah terinstall
python -c "import pygame" 2>nul
if errorlevel 1 (
    echo Pygame belum terinstall. Menginstall sekarang...
    pip install pygame numpy
    echo.
)

:: Generate asset jika belum ada
if not exist "assets\sprites" (
    echo Membuat sprite...
    python generate_sprites.py
    echo.
)
if not exist "assets\sounds" (
    echo Membuat sound...
    python generate_sounds.py
    echo.
)

echo Memulai game...
python main.py

pause
