@echo off
@chcp 65001 >nul
title SweepFood AI - Web Mockup and OCR Server
cd /d "%~dp0"
echo ==============================================================
echo   Dang khoi dong SweepFood AI Web Server (FastAPI + GPU)...
echo ==============================================================
"C:\Users\HUYPNG\miniconda3\envs\ocr_env\python.exe" -m uvicorn web.app:app --host 127.0.0.1 --port 8000 --reload
pause
