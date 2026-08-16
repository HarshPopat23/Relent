@echo off
title Relent AI - Development Launcher
echo =====================================================================
echo                 Starting Relent AI Services
echo =====================================================================

:: 1. Start Ollama Server
echo [1/3] Launching Ollama Server (CPU Safe Mode)...
start "Relent - Ollama Server" cmd /k "set OLLAMA_NUM_GPU=0 && ollama serve"

:: 2. Start Backend API Server
echo [2/3] Launching Backend API Server (Port 8000)...
start "Relent - Backend Server" cmd /k ".\.venv\Scripts\python.exe server.py"

:: 3. Start Modern React Frontend
echo [3/3] Launching React Vite Frontend (Port 5173)...
cd frontend
start "Relent - React Frontend" cmd /k "npm run dev -- --host 127.0.0.1 --port 5173"
cd ..

echo =====================================================================
echo  All services launched!
echo  - Frontend: http://127.0.0.1:5173
echo  - Backend:  http://127.0.0.1:8000
echo =====================================================================
