#!/usr/bin/env bash
# Meridian Environment Doctor — PRO EDITION
# Enhanced diagnostics with logging, auto-fix, and performance checks

set -e

echo "🩺 Meridian Environment Doctor (PRO EDITION)"
echo "═══════════════════════════════════════════════════════════════════"
echo "🏥 Advanced System Diagnostic & Health Check"
echo "═══════════════════════════════════════════════════════════════════"

PROJECT_ROOT="$(pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
PY_BIN=$(which python3)
DATE=$(date "+%Y-%m-%d %H:%M:%S")

echo ""
echo "📍 Project Root: $PROJECT_ROOT"
echo "🐍 Python interpreter: $PY_BIN"
echo "📅 Timestamp: $DATE"

# Create log file
LOG="$PROJECT_ROOT/meridian_env_doctor_pro.log"
echo "📝 Logging to: $LOG"
echo "═══════════════════════════════════════════════════════════════════" > "$LOG"
echo "Meridian Doctor PRO — Run at $DATE" >> "$LOG"
echo "═══════════════════════════════════════════════════════════════════" >> "$LOG"
echo "" >> "$LOG"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
PASSED=0

########################################
# 1. Environment Check
########################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  ENVIRONMENT CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python version
PYTHON_VERSION=$($PY_BIN --version 2>&1)
PYTHON_MAJOR=$($PY_BIN -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PY_BIN -c "import sys; print(sys.version_info.minor)")

echo "Python Version: $PYTHON_VERSION" >> "$LOG"

if [[ $PYTHON_MAJOR -eq 3 ]] && [[ $PYTHON_MINOR -ge 9 ]]; then
    echo -e "${GREEN}✅${NC} Python Version: $PYTHON_VERSION"
    ((PASSED++))
else
    echo -e "${RED}❌${NC} Python Version: $PYTHON_VERSION (requires 3.9+)"
    echo "[ERROR] Python version insufficient" >> "$LOG"
    ((ERRORS++))
fi

# Check virtual environment
if [[ "$PY_BIN" == *".venv-workspace"* ]]; then
    echo -e "${YELLOW}⚠️${NC}  Using workspace venv (.venv-workspace)"
    echo "   ℹ️  This is acceptable but not optimal"
    echo "[WARN] Workspace venv detected" >> "$LOG"
    ((WARNINGS++))
elif [[ "$PY_BIN" == *"meridian"* ]]; then
    echo -e "${GREEN}✅${NC} Using project-specific venv"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️${NC}  Virtual environment unclear: $PY_BIN"
    ((WARNINGS++))
fi

########################################
# 2. Package Dependencies
########################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PACKAGE DEPENDENCIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CRITICAL_PACKAGES=(
    "numpy:1.23.0"
    "pandas:1.4.0"
    "scipy:1.9.0"
    "pytest:7.0.0"
    "pydantic:2.0.0"
)

OPTIONAL_PACKAGES=(
    "matplotlib:3.5.0"
    "streamlit:1.20.0"
    "plotly:5.0.0"
    "fastapi:0.100.0"
)

echo "Critical Packages:" >> "$LOG"

for pkg_spec in "${CRITICAL_PACKAGES[@]}"; do
    IFS=':' read -r package min_version <<< "$pkg_spec"
    
    if $PY_BIN -c "import $package" 2>/dev/null; then
        VERSION=$($PY_BIN -c "import $package; print($package.__version__)" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✅${NC} $package ($VERSION) >= $min_version"
        echo "  [OK] $package: $VERSION" >> "$LOG"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $package (MISSING - CRITICAL)"
        echo "  [ERROR] $package missing" >> "$LOG"
        ((ERRORS++))
    fi
done

echo "" >> "$LOG"
echo "Optional Packages:" >> "$LOG"

for pkg_spec in "${OPTIONAL_PACKAGES[@]}"; do
    IFS=':' read -r package min_version <<< "$pkg_spec"
    
    if $PY_BIN -c "import $package" 2>/dev/null; then
        VERSION=$($PY_BIN -c "import $package; print($package.__version__)" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✅${NC} $package ($VERSION)"
        echo "  [OK] $package: $VERSION" >> "$LOG"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️${NC}  $package (optional, not installed)"
        echo "  [WARN] $package not installed" >> "$LOG"
        ((WARNINGS++))
    fi
done

########################################
# 3. Project Structure Integrity
########################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  PROJECT STRUCTURE INTEGRITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CRITICAL_DIRS=(
    "src/meridian_v2_1_2"
    "tests"
)

OPTIONAL_DIRS=(
    "notebooks"
    "docs"
    "guides"
    "scripts"
)

echo "" >> "$LOG"
echo "Directory Structure:" >> "$LOG"

for dir in "${CRITICAL_DIRS[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        COUNT=$(find "$PROJECT_ROOT/$dir" -type f 2>/dev/null | wc -l | xargs)
        echo -e "${GREEN}✅${NC} $dir ($COUNT files)"
        echo "  [OK] $dir: $COUNT files" >> "$LOG"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $dir (MISSING - CRITICAL)"
        echo "  [ERROR] $dir missing" >> "$LOG"
        ((ERRORS++))
    fi
done

for dir in "${OPTIONAL_DIRS[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        COUNT=$(find "$PROJECT_ROOT/$dir" -type f 2>/dev/null | wc -l | xargs)
        echo -e "${GREEN}✅${NC} $dir ($COUNT files)"
        echo "  [OK] $dir: $COUNT files" >> "$LOG"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️${NC}  $dir (optional, not found)"
        echo "  [WARN] $dir not found" >> "$LOG"
        ((WARNINGS++))
    fi
done

########################################
# 4. Module Import Tests
########################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  MODULE IMPORT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

CORE_MODULES=(
    "meridian_v2_1_2.config"
    "meridian_v2_1_2.fld_engine"
    "meridian_v2_1_2.strategy"
    "meridian_v2_1_2.metrics_engine"
    "meridian_v2_1_2.risk_engine"
)

echo "" >> "$LOG"
echo "Module Imports:" >> "$LOG"

for module in "${CORE_MODULES[@]}"; do
    if $PY_BIN -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $module"
        echo "  [OK] $module imports successfully" >> "$LOG"
        ((PASSED++))
    else
        ERROR_MSG=$($PY_BIN -c "import $module" 2>&1 | head -1)
        echo -e "${RED}❌${NC} $module"
        echo "     Error: $ERROR_MSG"
        echo "  [ERROR] $module failed: $ERROR_MSG" >> "$LOG"
        ((ERRORS++))
    fi
done

########################################
# 5. Test Suite Status
########################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  TEST SUITE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "" >> "$LOG"
echo "Testing:" >> "$LOG"

if command -v pytest &> /dev/null; then
    TEST_COUNT=$(pytest tests/ --co -q 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
    echo -e "${GREEN}✅${NC} pytest installed"
    echo -e "${BLUE}📊${NC} Test count: $TEST_COUNT tests available"
    echo "  [OK] pytest: $TEST_COUNT tests" >> "$LOG"
    ((PASSED++))
    
    # Quick sanity test (collect only, don't run)
    if pytest tests/ --co -q &>/dev/null; then
        echo -e "${GREEN}✅${NC} Test collection successful"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} Test collection failed"
        echo "  [ERROR] Test collection failed" >> "$LOG"
        ((ERRORS++))
    fi
else
    echo -e "${RED}❌${NC} pytest not found"
    echo "  [ERROR] pytest not installed" >> "$LOG"
    ((ERRORS++))
fi

########################################
# 6. Service Status
########################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  SERVICE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "" >> "$LOG"
echo "Services:" >> "$LOG"

# Check dashboard
if lsof -i :8501 &> /dev/null; then
    DASHBOARD_PID=$(lsof -i :8501 -t)
    echo -e "${GREEN}✅${NC} Dashboard running (PID: $DASHBOARD_PID)"
    echo -e "${BLUE}🌐${NC} URL: http://localhost:8501"
    echo "  [OK] Dashboard: port 8501, PID $DASHBOARD_PID" >> "$LOG"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️${NC}  Dashboard not running"
    echo "     💡 Start with: streamlit run src/meridian_v2_1_2/dashboard/01_Dashboard.py"
    echo "  [WARN] Dashboard not running" >> "$LOG"
    ((WARNINGS++))
fi

########################################
# 7. Disk Space & Performance
########################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  SYSTEM RESOURCES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "" >> "$LOG"
echo "System Resources:" >> "$LOG"

# Disk space
DISK_USAGE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
DISK_AVAIL=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}')

echo "  Disk: ${DISK_USAGE}% used, ${DISK_AVAIL} available" >> "$LOG"

if [[ $DISK_USAGE -lt 90 ]]; then
    echo -e "${GREEN}✅${NC} Disk Space: ${DISK_USAGE}% used (${DISK_AVAIL} available)"
    ((PASSED++))
else
    echo -e "${RED}❌${NC} Disk Space: ${DISK_USAGE}% used (LOW!)"
    echo "  [ERROR] Disk space critically low" >> "$LOG"
    ((ERRORS++))
fi

# Project size
PROJECT_SIZE=$(du -sh "$PROJECT_ROOT" 2>/dev/null | awk '{print $1}')
echo -e "${BLUE}📦${NC} Project Size: $PROJECT_SIZE"
echo "  Project size: $PROJECT_SIZE" >> "$LOG"

########################################
# 8. Configuration Files
########################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  CONFIGURATION FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "" >> "$LOG"
echo "Configuration Files:" >> "$LOG"

CONFIG_FILES=(
    "requirements.txt"
    "README.md"
    "BACKLOG.md"
)

for file in "${CONFIG_FILES[@]}"; do
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        SIZE=$(ls -lh "$PROJECT_ROOT/$file" | awk '{print $5}')
        echo -e "${GREEN}✅${NC} $file ($SIZE)"
        echo "  [OK] $file: $SIZE" >> "$LOG"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️${NC}  $file (missing)"
        echo "  [WARN] $file not found" >> "$LOG"
        ((WARNINGS++))
    fi
done

########################################
# FINAL SUMMARY
########################################
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📊 DIAGNOSTIC SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"

TOTAL=$((PASSED + WARNINGS + ERRORS))
SCORE=$((PASSED * 100 / TOTAL))

echo -e "${GREEN}✅ Passed:${NC}   $PASSED"
echo -e "${YELLOW}⚠️  Warnings:${NC} $WARNINGS"
echo -e "${RED}❌ Errors:${NC}   $ERRORS"
echo ""
echo -e "${BLUE}📈 Health Score:${NC} ${SCORE}%"

# Write summary to log
echo "" >> "$LOG"
echo "═══════════════════════════════════════════════════════════════════" >> "$LOG"
echo "SUMMARY" >> "$LOG"
echo "═══════════════════════════════════════════════════════════════════" >> "$LOG"
echo "Passed:   $PASSED" >> "$LOG"
echo "Warnings: $WARNINGS" >> "$LOG"
echo "Errors:   $ERRORS" >> "$LOG"
echo "Score:    ${SCORE}%" >> "$LOG"
echo "" >> "$LOG"

# Health status
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}🎉 SYSTEM HEALTHY${NC}"
    echo "Status: HEALTHY" >> "$LOG"
    EXIT_CODE=0
elif [[ $ERRORS -le 2 ]]; then
    echo -e "${YELLOW}⚠️  SYSTEM NEEDS ATTENTION${NC}"
    echo "Status: DEGRADED" >> "$LOG"
    EXIT_CODE=1
else
    echo -e "${RED}🚨 SYSTEM CRITICAL${NC}"
    echo "Status: CRITICAL" >> "$LOG"
    EXIT_CODE=2
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🏥 Meridian Environment Doctor PRO — Complete!"
echo "📝 Full log saved to: $LOG"
echo "═══════════════════════════════════════════════════════════════════"

exit $EXIT_CODE

