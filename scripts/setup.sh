#!/usr/bin/env bash
# ==============================================================================
# Relent AI - Unix Setup Script
# ==============================================================================

set -e

echo "====================================================================="
echo "                Setting up Relent AI Environment"
echo "====================================================================="

# 1. Create venv
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

# 2. Install Python deps
echo "Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install Frontend deps
echo "Installing Node.js frontend dependencies..."
cd frontend
npm install
cd ..

# 4. Copy .env
if [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    cp .env.example .env
fi

echo "====================================================================="
echo "Setup Complete! You can now run ./scripts/run_dev.sh"
echo "====================================================================="
