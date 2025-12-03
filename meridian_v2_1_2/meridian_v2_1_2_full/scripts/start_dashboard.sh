#!/usr/bin/env bash
# Meridian v2.1.2 Dashboard Launcher
# Easy one-command dashboard startup

set -e

echo "🚀 Starting Meridian v2.1.2 Dashboard..."
echo "═══════════════════════════════════════════════════════════════════"

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📍 Project Root: $PROJECT_ROOT"
echo "🐍 Python: $(which python3)"
echo ""

# Set PYTHONPATH to include src directory
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not installed!"
    echo "💡 Install with: pip install streamlit plotly"
    exit 1
fi

# Check if port 8501 is already in use
if lsof -i :8501 &> /dev/null; then
    echo "⚠️  Port 8501 already in use!"
    echo "💡 Stop existing dashboard with: pkill -f 'streamlit run'"
    echo ""
    read -p "Stop existing dashboard and restart? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "streamlit run" || true
        sleep 2
        echo "✅ Stopped existing dashboard"
    else
        echo "❌ Aborting..."
        exit 1
    fi
fi

echo "🎯 Launching Dashboard..."
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Launch Streamlit dashboard
python3 -m streamlit run src/meridian_v2_1_2/dashboard/01_Dashboard.py \
    --server.port 8501 \
    --server.headless true \
    --server.address localhost

# Note: Remove --server.headless if you want browser to auto-open

