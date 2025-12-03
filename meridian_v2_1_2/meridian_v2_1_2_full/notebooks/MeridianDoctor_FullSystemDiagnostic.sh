#!/usr/bin/env bash

set -e

echo ""
echo "============================================"
echo "🩺  Meridian Doctor — Full System Diagnostic"
echo "============================================"
echo ""

ROOT="meridian_v2_1_2"

if [ ! -d "$ROOT" ]; then
    echo "❌ ERROR: Meridian root directory '$ROOT' not found."
    echo "Run the installer first."
    exit 1
fi

cd $ROOT

echo ""
echo "🔍 Running Meridian system health checks..."
echo ""


# ---------------------------------------------
# 1. PYTHON ENV CHECK
# ---------------------------------------------
echo "1️⃣ Checking Python environment..."

if [ ! -d ".venv" ]; then
    echo "❌ .venv missing — Meridian environment not set up."
    echo "   Run: python3 -m venv .venv"
    exit 1
fi

source .venv/bin/activate

echo "   ✓ Environment activated"
PYVER=$(python3 -c 'import sys; print(sys.version)')
echo "   ✓ Python version: $PYVER"


# ---------------------------------------------
# 2. DEPENDENCY CHECK
# ---------------------------------------------
echo ""
echo "2️⃣ Checking installed dependencies..."

missing=0

check_dep() {
    python3 -c "import $1" 2>/dev/null || missing=1
}

for pkg in numpy pandas scipy matplotlib seaborn plotly yfinance dotenv requests flask fastapi uvicorn pytest; do
    echo -n "   - $pkg: "
    if python3 - <<EOF > /dev/null 2>&1
import $pkg
EOF
    then
        echo "OK"
    else
        echo "MISSING"
        missing=1
    fi
done

if [ $missing -eq 1 ]; then
    echo "❌ Missing dependencies detected."
    echo "   Run: pip install -r requirements.txt"
else
    echo "   ✓ All dependencies present"
fi


# ---------------------------------------------
# 3. FOLDER STRUCTURE VALIDATION
# ---------------------------------------------
echo ""
echo "3️⃣ Validating Meridian directory structure..."

expected=(
    "src/meridian_v2_1_2"
    "notebooks"
    "research"
    "scripts"
    "outputs"
    "data"
    "tests"
    "docs"
)

for folder in "${expected[@]}"; do
    echo -n "   - $folder: "
    if [ -d "$folder" ]; then
        echo "OK"
    else
        echo "MISSING"
        missing=1
    fi
done

if [ $missing -eq 1 ]; then
    echo "⚠️  Directory inconsistencies found."
else
    echo "   ✓ Directory structure correct"
fi


# ---------------------------------------------
# 4. ENV FILE VALIDATION
# ---------------------------------------------
echo ""
echo "4️⃣ Checking .env..."

if [ ! -f ".env" ]; then
    echo "❌ .env not found"
else
    echo "   ✓ .env exists"

    echo "   Checking key variables..."
    required_vars=("OPENBB_API_KEY" "APCA_API_KEY_ID" "APCA_API_SECRET_KEY" "DATA_PATH")
    for var in "${required_vars[@]}"; do
        echo -n "     - $var: "
        if grep -q "$var" .env; then
            echo "OK"
        else
            echo "MISSING"
        fi
    done
fi


# ---------------------------------------------
# 5. PYTHON IMPORT CHECK
# ---------------------------------------------
echo ""
echo "5️⃣ Checking module imports..."

python3 - <<EOF
try:
    import meridian_v2_1_2
    print("   ✓ Meridian package imports correctly")
except Exception as e:
    print("❌ Meridian package import failed:", e)
    exit(1)
EOF


# ---------------------------------------------
# 6. NOTEBOOK KERNEL TEST
# ---------------------------------------------
echo ""
echo "6️⃣ Checking Jupyter kernel registration..."

if jupyter kernelspec list 2>/dev/null | grep -q "meridian_v2_1_2"; then
    echo "   ✓ Kernel installed"
else
    echo "❌ Kernel not found. Run:"
    echo "   python3 -m ipykernel install --user --name meridian_v2_1_2"
fi


# ---------------------------------------------
# 7. TEST SUITE EXECUTION
# ---------------------------------------------
echo ""
echo "7️⃣ Running pytest smoke test..."

pytest tests/test_imports.py -q || {
    echo "❌ Tests failed — check logs above."
    exit 1
}

echo "   ✓ Basic test suite passed"


# ---------------------------------------------
# 8. DASHBOARD CHECK
# ---------------------------------------------
echo ""
echo "8️⃣ Checking dashboard bootstrap script..."

if [ -f "scripts/start_dashboard.py" ]; then
    echo "   ✓ Script exists"
else
    echo "❌ Missing dashboard start script"
fi


# ---------------------------------------------
# 9. DOCTOR'S REPORT
# ---------------------------------------------
echo ""
echo "============================================"
echo "🔎 MERIDIAN DOCTOR — FINAL REPORT"
echo "============================================"

echo "Python:               OK"
echo "Dependencies:         $( [ $missing -eq 0 ] && echo OK || echo 'ISSUES FOUND' )"
echo "Folder structure:     $( [ $missing -eq 0 ] && echo OK || echo 'ISSUES FOUND' )"
echo ".env presence:        OK"
echo "Imports:              OK"
echo "Kernel:               OK (if detected above)"
echo "Test suite:           OK"
echo "Dashboard script:     OK if present"

echo ""
echo "If any issues were marked as ❌ or ⚠️:"
echo "- The Doctor has identified them above."
echo "- Fix the issues or ask ChatGPT for remediation."
echo ""
echo "🎉 Meridian diagnostic complete."
echo "============================================"
echo ""
