@echo off
title Relent AI - Setup
echo =====================================================================
echo                 Setting up Relent AI Environment
echo =====================================================================

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    exit /b 1
)

:: Create venv if not exists
if not exist .venv (
    echo Creating Python virtual environment (.venv)...
    python -m venv .venv
)

:: Activate and install Python deps
echo Installing Python dependencies...
call .\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

:: Install Frontend deps
echo Installing Node.js frontend dependencies...
cd frontend
call npm install
cd ..

:: Copy .env if not exists
if not exist .env (
    echo Creating default .env file...
    copy .env.example .env
)

echo =====================================================================
echo Setup Complete! You can now run scripts\run_dev.bat
echo =====================================================================
pause
