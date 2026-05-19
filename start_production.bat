@echo off
title Predictive Maintenance Production Suite
echo ========================================================
echo ⚙️  LAUNCHING PREDICTIVE MAINTENANCE SYSTEM ONLINE...
echo ========================================================
echo.

:: 1. Launch the production WSGI server
echo [1/2] Starting Waitress server on port 5000...
start "Predictive Maintenance - Production Server" cmd /k ".venv\Scripts\python.exe run_production.py"

:: Small delay to let the server bind to the port
timeout /t 3 /nobreak >nul

:: 2. Launch the secure tunnel
echo [2/2] Launching Localhost.run tunnel...
start "Localhost.run Secure Tunnel" cmd /k "echo Exposing system to the internet... && ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:5000 nokey@localhost.run"

echo.
echo ========================================================
echo 🎉 SUCCESS! Both services are starting:
echo.
echo - Window 1: Runs the Flask & React Production Server
echo - Window 2: Connects to the secure tunnel and prints your 
echo             public online URL (look for the '.lhr.life' link)
echo.
echo To stop them, simply close the two command windows.
echo ========================================================
echo.
pause
