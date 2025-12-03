#!/usr/bin/env bash

echo "🩺 Meridian Environment Doctor — Starting Full System Diagnostic..."
echo "═══════════════════════════════════════════════════════════════════"
set -e

PROJECT_ROOT="$(pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
PY_BIN="$(which python3)"

echo ""
echo "📍 Project root: $PROJECT_ROOT"
echo "🐍 System Python: $PY_BIN"
echo ""

# 1. Check Python version
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Checking Python Version..."
PYTHON_VERSION=$($PY_BIN --version 2>&1)
echo "   ✅ $PYTHON_VERSION"

# 2. Check virtual environment
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Checking Virtual Environment..."
if [[ "$PY_BIN" == *".venv-workspace"* ]]; then
    echo "   ⚠️  WARNING: Using GLOBAL workspace venv (.venv-workspace)"
    echo "   ℹ️  This is OK for shared projects, but consider project-specific venv"
else
    echo "   ✅ Using appropriate Python environment"
fi

# 3. Check required packages
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Checking Required Packages..."

REQUIRED_PACKAGES=(
    "numpy"
    "pandas"
    "scipy"
    "pytest"
    "pydantic"
    "matplotlib"
    "streamlit"
    "plotly"
)

MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if $PY_BIN -c "import $package" 2>/dev/null; then
        VERSION=$($PY_BIN -c "import $package; print($package.__version__)" 2>/dev/null || echo "unknown")
        echo "   ✅ $package ($VERSION)"
    else
        echo "   ❌ $package (missing)"
        MISSING_PACKAGES+=("$package")
    fi
done

# 4. Check project structure
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Checking Project Structure..."

REQUIRED_DIRS=(
    "src/meridian_v2_1_2"
    "tests"
    "notebooks"
    "docs"
    "guides"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        COUNT=$(find "$PROJECT_ROOT/$dir" -type f | wc -l | xargs)
        echo "   ✅ $dir ($COUNT files)"
    else
        echo "   ❌ $dir (missing)"
    fi
done

# 5. Check key files
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Checking Key Configuration Files..."

KEY_FILES=(
    "requirements.txt"
    "pytest.ini"
    "README.md"
    "BACKLOG.md"
)

for file in "${KEY_FILES[@]}"; do
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        SIZE=$(ls -lh "$PROJECT_ROOT/$file" | awk '{print $5}')
        echo "   ✅ $file ($SIZE)"
    else
        echo "   ⚠️  $file (missing)"
    fi
done

# 6. Check Meridian modules
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Checking Meridian Modules..."

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

MERIDIAN_MODULES=(
    "meridian_v2_1_2.config"
    "meridian_v2_1_2.fld_engine"
    "meridian_v2_1_2.strategy"
    "meridian_v2_1_2.backtest"
    "meridian_v2_1_2.metrics_engine"
)

for module in "${MERIDIAN_MODULES[@]}"; do
    if $PY_BIN -c "import $module" 2>/dev/null; then
        echo "   ✅ $module"
    else
        echo "   ❌ $module (import failed)"
    fi
done

# 7. Run quick tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Running Quick Test Suite..."

if command -v pytest &> /dev/null; then
    TEST_RESULT=$(pytest tests/ --co -q 2>/dev/null | tail -1 || echo "0 tests")
    echo "   ✅ pytest available: $TEST_RESULT"
else
    echo "   ⚠️  pytest not found"
fi

# 8. Check Dashboard status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  Checking Dashboard Status..."

if lsof -i :8501 &> /dev/null; then
    echo "   ✅ Dashboard running on port 8501"
    echo "   🌐 URL: http://localhost:8501"
else
    echo "   ⚠️  Dashboard not running"
    echo "   💡 Start with: streamlit run src/meridian_v2_1_2/dashboard/01_Dashboard.py"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📊 DIAGNOSTIC SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"

if [[ ${#MISSING_PACKAGES[@]} -eq 0 ]]; then
    echo "✅ All required packages installed"
else
    echo "❌ Missing packages: ${MISSING_PACKAGES[*]}"
    echo "💡 Install with: pip install -r requirements.txt"
fi

echo ""
echo "🏥 Meridian Environment Doctor — Complete!"
echo "═══════════════════════════════════════════════════════════════════"

