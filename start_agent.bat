@echo off
title Sarvam AI Push-to-Wake Desktop Agent
cd /d "%~dp0"
echo ===================================================================
echo   Starting Sarvam AI Push-to-Wake Desktop Agent
echo ===================================================================
.\venv\Scripts\python.exe main.py
pause
