#!/usr/bin/env bash

echo "🩺 Meridian Environment Doctor — Starting..."
set -e

PROJECT_ROOT="$(pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
PY_BIN="$(which python3)"

echo "📍 Project root: $PROJECT_ROOT"
echo "🐍 System Python: $PY_BIN"

# 1. Detect if wrong venv is active
if [[ "$PY_BIN" == *".venv-workspace"* ]]; then
    echo "⚠️ WARNING: You are using the GLOBAL workspace venv (.venv-workspace)"
    echo "❌
