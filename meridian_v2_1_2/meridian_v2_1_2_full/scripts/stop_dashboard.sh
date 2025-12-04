#!/usr/bin/env bash
# Meridian v2.1.2 Dashboard Stopper
# Easy one-command dashboard shutdown

set -e

echo "🛑 Stopping Meridian v2.1.2 Dashboard..."
echo "═══════════════════════════════════════════════════════════════════"

# Check if dashboard is running
if lsof -i :8501 &> /dev/null; then
    DASHBOARD_PID=$(lsof -i :8501 -t)
    echo "📍 Found dashboard running (PID: $DASHBOARD_PID)"
    
    pkill -f "streamlit run" || true
    sleep 2
    
    # Verify it's stopped
    if lsof -i :8501 &> /dev/null; then
        echo "❌ Dashboard still running, trying force kill..."
        pkill -9 -f "streamlit run" || true
        sleep 1
    fi
    
    if ! lsof -i :8501 &> /dev/null; then
        echo "✅ Dashboard stopped successfully"
    else
        echo "⚠️  Could not stop dashboard, manual intervention required"
        exit 1
    fi
else
    echo "ℹ️  Dashboard is not running"
fi

echo "═══════════════════════════════════════════════════════════════════"
echo "🏁 Done!"


