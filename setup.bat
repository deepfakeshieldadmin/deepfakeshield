@echo off
title Deep Fake Shield - Complete Setup
color 0A

echo ============================================
echo    DEEP FAKE SHIELD - PROJECT SETUP
echo    Complete Installation Script
echo ============================================
echo.

:: Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://python.org
    echo Make sure to check "Add Python to PATH" during install
    pause
    exit /b 1
)
python --version
echo Python found successfully!
echo.

:: Create Virtual Environment
echo [2/6] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

:: Activate venv
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

:: Install dependencies
echo [4/6] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed!
echo.

:: Create directories
echo [5/6] Creating required directories...
if not exist "media\uploads\images" mkdir "media\uploads\images"
if not exist "media\uploads\videos" mkdir "media\uploads\videos"
if not exist "media\uploads\audio" mkdir "media\uploads\audio"
if not exist "media\frames" mkdir "media\frames"
if not exist "static\css" mkdir "static\css"
if not exist "static\js" mkdir "static\js"
if not exist "staticfiles" mkdir "staticfiles"
echo Directories created!
echo.

:: Run migrations
echo [6/6] Setting up database...
python manage.py makemigrations core
python manage.py migrate
echo Database setup complete!
echo.

echo ============================================
echo    SETUP COMPLETE!
echo ============================================
echo.
echo Next steps:
echo   1. Run: run.bat (to start the server)
echo   2. Or manually:
echo      - python manage.py createsuperuser
echo      - python manage.py runserver
echo.
echo   Admin panel: http://127.0.0.1:8000/admin/
echo   Website:     http://127.0.0.1:8000/
echo.
pause