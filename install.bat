@echo off
title Deep Fake Shield - Full Install + Superuser
color 0E

echo ============================================
echo    DEEP FAKE SHIELD - FULL INSTALLATION
echo    (Setup + Superuser + Run)
echo ============================================
echo.

:: Run setup first
call setup.bat

:: Create superuser
echo.
echo ============================================
echo    Creating Admin Superuser Account
echo ============================================
echo.
echo Please enter admin credentials below:
echo.
call venv\Scripts\activate.bat
python manage.py createsuperuser

echo.
echo ============================================
echo    INSTALLATION COMPLETE!
echo ============================================
echo.
echo Starting server now...
echo.

python manage.py runserver

pause