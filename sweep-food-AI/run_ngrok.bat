@echo off
@chcp 65001 >nul
title SweepFood AI - ngrok Public Tunnel
cd /d "%~dp0"
echo ==============================================================
echo   Dang khoi dong ngrok public tunnel cho SweepFood Web va OCR...
echo ==============================================================
"C:\Users\HUYPNG\miniconda3\envs\ocr_env\python.exe" scripts/host_ngrok.py
pause
