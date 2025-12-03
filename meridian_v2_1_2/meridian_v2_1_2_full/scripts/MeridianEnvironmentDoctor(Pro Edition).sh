#!/usr/bin/env bash
# Meridian Environment Doctor — PRO EDITION
set -e

echo "🩺 Meridian Environment Doctor (Pro Edition)"
echo "--------------------------------------------"

PROJECT_ROOT="$(pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
PY_IP=$(which python3)
DATE=$(date "+%Y-%m-%d %H:%M:%S")

echo "📍 Project Root: $PROJECT_ROOT"
echo "🐍 Python interpreter: $PY_IP"

# Log file
LOG="$PROJECT_ROOT/meridian_env_doctor.log"
echo "📝 Logging to: $LOG"
echo "Meridian Doctor run at $DATE" >> "$LOG"

########################################
# 1. Detect wrong venv activation
########################################
if [[ "$PY_IP" == *".venv-workspace"* ]]; then
    echo "⚠️ Detected workspace venv. Deactivating..."
    echo "[WARN] Wrong environment
