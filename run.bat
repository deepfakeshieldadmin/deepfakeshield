@echo off
title Deep Fake Shield - Server
color 0B

echo ============================================
echo    DEEP FAKE SHIELD - RUNNING SERVER
echo ============================================
echo.

:: Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated!
) else (
    echo WARNING: Virtual environment not found!
    echo Run setup.bat first.
    pause
    exit /b 1
)

echo.
echo Starting Django development server...
echo.
echo ============================================
echo   Website:  http://127.0.0.1:8000/
echo   Admin:    http://127.0.0.1:8000/admin/
echo   Landing:  http://127.0.0.1:8000/
echo   Home:     http://127.0.0.1:8000/home/
echo ============================================
echo.
echo Press Ctrl+C to stop the server.
echo.

python manage.py runserver

pause