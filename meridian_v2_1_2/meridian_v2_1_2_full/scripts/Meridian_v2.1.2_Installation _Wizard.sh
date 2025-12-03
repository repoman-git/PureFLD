#!/usr/bin/env bash

set -e

echo ""
echo "============================================"
echo "🚀 Meridian v2.1.2 Installation Wizard"
echo "============================================"
echo ""

# ---- 1. CHECK PYTHON ---------------------------------------------------------

echo "🔍 Checking for Python 3.10+ ..."
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 not found. Install Python 3.10+ first."
    exit 1
fi

PYVER=$(python3 -c 'import sys; print(sys.version_info.major*10 + sys.version_info.minor)')
if [ "$PYVER" -lt 310 ]; then
    echo "❌ Python version must be 3.10+"
    exit 1
fi
echo "✅ Python version OK"


# ---- 2. CREATE PROJECT ROOT --------------------------------------------------

ROOT="meridian_v2_1_2"
echo "📁 Creating project directory: $ROOT"
mkdir -p $ROOT
cd $ROOT


# ---- 3. CREATE FOLDER STRUCTURE ----------------------------------------------

echo "📂 Building directory structure..."

mkdir -p src/meridian_v2_1_2
mkdir -p notebooks
mkdir -p research
mkdir -p scripts
mkdir -p outputs
mkdir -p data
mkdir -p tests
mkdir -p docs

echo "✅ Directory structure created"


# ---- 4. CREATE VIRTUAL ENV ----------------------------------------------------

echo "🐍 Creating virtual environment..."

python3 -m venv .venv
source .venv/bin/activate

echo "✅ Virtual environment activated"


# ---- 5. CREATE requirements.txt ----------------------------------------------

echo "📦 Writing requirements.txt..."

cat <<EOF > requirements.txt
numpy
pandas
scipy
matplotlib
seaborn
plotly
yfinance
python-dotenv
requests
flask
fastapi
uvicorn
ipykernel
jupyterlab
pytest
EOF

echo "📥 Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed"


# ---- 6. CREATE .env TEMPLATE --------------------------------------------------

echo "🔐 Creating .env template..."

cat <<EOF > .env
# ---------------------------
# Meridian v2.1.2 ENV FILE
# ---------------------------

OPENBB_API_KEY=""
APCA_API_KEY_ID=""
APCA_API_SECRET_KEY=""
APCA_API_BASE_URL="https://paper-api.alpaca.markets"

DATA_PATH="./data"
OUTPUT_PATH="./outputs"

# Add any local secrets below
EOF

echo "⚠️  IMPORTANT: .env created. Fill in API keys before streaming or paper-trading."
echo "❌ DO NOT COMMIT THIS FILE."


# ---- 7. CREATE PLACEHOLDER PYTHON MODULES ------------------------------------

echo "📜 Creating minimal Python package..."

cat <<EOF > src/meridian_v2_1_2/__init__.py
"""
Meridian v2.1.2 — Quant Research & Paper-Trading Platform
"""
EOF

cat <<EOF > src/meridian_v2_1_2/strategy.py
# Placeholder strategy module — will be replaced by full implementation via Cursor
class FLDStrategy:
    pass
EOF

echo "✅ Python package skeleton ready"


# ---- 8. CREATE INITIAL NOTEBOOKS ---------------------------------------------

echo "📓 Creating starter Jupyter notebooks..."

cat <<EOF > notebooks/backtest_meridian_v2_1_2.ipynb
{
 "cells": [
   {
    "cell_type": "markdown",
    "metadata": {},
    "source": ["# Meridian v2.1.2 — Unified Backtest Notebook (Starter Skeleton)"]
   }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 5
}
EOF

echo "🎒 Registering kernel..."
python3 -m ipykernel install --user --name meridian_v2_1_2 --display-name "Meridian v2.1.2"

echo "✅ Notebook kernel installed"


# ---- 9. CREATE DOCUMENTATION FILES -------------------------------------------

echo "📘 Writing documentation stubs..."

cat <<EOF > docs/PHASE_INDEX.md
# Meridian v2.1.2 — PHASE INDEX
(Placeholder — full version will be imported externally)
EOF

cat <<EOF > docs/ROADMAP.md
# Meridian v2.1.2 — ROADMAP
(Placeholder — full version will be imported externally)
EOF

cat <<EOF > docs/BACKLOG.md
# Meridian v2.1.2 — BACKLOG
(Placeholder — full version will be imported externally)
EOF

echo "✅ Documentation placeholders created"


# ----10. CREATE START DASHBOARD SCRIPT ----------------------------------------

cat <<EOF > scripts/start_dashboard.py
#!/usr/bin/env python3

print("Dashboard v2 placeholder — full implementation will be imported via Cursor.")
EOF

chmod +x scripts/start_dashboard.py
echo "🖥️  Dashboard bootstrap script created"


# ----11. CREATE TEST SUITE STARTER --------------------------------------------

cat <<EOF > tests/test_imports.py
def test_imports():
    import meridian_v2_1_2
    assert True
EOF

echo "🧪 Test suite scaffold ready"


# ---- 12. SUCCESS MESSAGE ------------------------------------------------------

echo ""
echo "============================================"
echo "🎉 Meridian v2.1.2 is now installed!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Activate environment:  source .venv/bin/activate"
echo "2. Open project in Cursor."
echo "3. Run: pytest"
echo "4. Import full system implementation via your Cursor Master Bootstrap Prompt."
echo ""
echo "Welcome to your quant platform, Commander."
echo ""
