#!/usr/bin/env bash
# ==============================================================================
# Relent AI - Unix Dev Launcher
# ==============================================================================

echo "====================================================================="
echo "                Starting Relent AI Services"
echo "====================================================================="

# 1. Start Ollama
echo "[1/3] Starting Ollama Server..."
ollama serve &
OLLAMA_PID=$!

# 2. Start Backend
echo "[2/3] Starting Backend API Server..."
source .venv/bin/activate 2>/dev/null || true
python server.py &
BACKEND_PID=$!

# 3. Start Frontend
echo "[3/3] Starting React Vite Frontend..."
cd frontend && npm run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!
cd ..

echo "====================================================================="
echo "  All services launched!"
echo "  - Frontend: http://127.0.0.1:5173"
echo "  - Backend:  http://127.0.0.1:8000"
echo "====================================================================="

trap "kill $OLLAMA_PID $BACKEND_PID $FRONTEND_PID" EXIT
wait
