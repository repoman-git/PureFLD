# 📚 MERIDIAN v2.1.2 — PROJECT INDEX

**Complete navigation guide for the entire project.**

---

## 🗺️ **START HERE**

### **For New Agents/Sessions:**
1. ⭐ **`QUICK_START_FOR_NEW_AGENT.md`** - Read this FIRST (5 min)
2. 📋 **`SESSION_SUMMARY.md`** - Last session's work (15 min)
3. 📌 **`BACKLOG.md`** - Current tasks and priorities
4. 📖 **`README.md`** - Project overview

### **For Users:**
1. 📘 **`guides/quickstart_full.pdf`** - Getting started
2. 📕 **`guides/operator_handbook_full.pdf`** - Complete manual
3. 📄 **`guides/cheat_sheet_full.pdf`** - Quick reference

---

## 📂 **DIRECTORY STRUCTURE**

```
meridian_v2_1_2_full/
├── src/meridian_v2_1_2/          # Core source code
│   ├── api/                       # API layer (Phase 4A)
│   ├── backlog/                   # Task management (Phase 37)
│   ├── config/                    # Configuration
│   ├── dashboard/                 # Dashboard (main + v2)
│   │   ├── components/            # Reusable UI components
│   │   ├── pages/                 # Dashboard pages (Streamlit)
│   │   └── utils/                 # Dashboard utilities
│   ├── dashboard_v2/              # Multi-strategy dashboard (Phase 41)
│   ├── fld_engine/                # FLD calculations
│   ├── metrics_engine/            # Performance metrics
│   ├── notebook_generation/       # Bidirectional conversion (Phase 4B)
│   ├── research/                  # Research tools
│   │   └── param_sweep/           # Parameter optimization (Phase 39)
│   ├── risk_engine/               # Risk management
│   ├── storage/                   # Persistence layer (Phase 4A)
│   ├── strategy/                  # Strategy modules
│   │   └── generated/             # Auto-generated strategies
│   └── synthetic/                 # Synthetic data generation
│
├── tests/                         # Test suites (682 tests)
│   ├── test_backlog_system.py
│   ├── test_param_sweep.py
│   ├── test_dashboard_v2.py
│   └── ...
│
├── notebooks/                     # Jupyter notebooks
│   ├── backtest_meridian_v2_1_2.ipynb
│   ├── tdom_integration_demo.ipynb
│   └── ...
│
├── docs/                          # Technical documentation
│   ├── PHASE_4_FOUNDATION.md
│   ├── PHASE_4B_COMPLETE.md
│   ├── BACKLOG_SYSTEM_V1.md
│   ├── PARAMETER_SWEEP_V1.md
│   └── ...
│
├── guides/                        # User guides
│   ├── quickstart_full.pdf
│   ├── operator_handbook_full.pdf
│   ├── cheat_sheet_full.pdf
│   ├── README.md
│   └── INDEX.md
│
├── scripts/                       # Utility scripts
│   ├── start_dashboard.sh
│   ├── stop_dashboard.sh
│   └── MeridianEnvironmentDoctor_ProEdition.sh
│
├── data/                          # Data storage
│   └── backtest_runs.json        # Registry (Phase 4A)
│
├── templates/                     # Templates
│
├── requirements.txt               # Dependencies
├── BACKLOG.md                     # Current tasks
├── README.md                      # Project overview
├── SESSION_SUMMARY.md             # Last session
├── QUICK_START_FOR_NEW_AGENT.md  # Quick reference
└── PROJECT_INDEX.md               # This file
```

---

## 🧩 **PHASE REFERENCE**

### **Completed Phases:**
- ✅ Phase 1-36: Core system (pre-session)
- ✅ **Phase 37:** Backlog Manager
- ✅ **Phase 38:** Unified Backtest Notebook
- ✅ **Phase 39:** Parameter Sweep Engine
- ✅ **Phase 41:** Dashboard v2 (Multi-Strategy)
- ✅ **Phase 3.1:** Advanced Notebook Viewer
- ✅ **Phase 3 Lite:** Full Notebook Editor
- ✅ **Phase 4A:** Backtest Integration Foundation
- ✅ **Phase 4B:** Bidirectional Generation

### **In Progress:**
- 🔨 Phase 4: Integration (90% complete)
  - Missing: `05_Backtest_Results.py`
  - Missing: "Run as Backtest" button

### **Planned:**
- 📋 Phase 5: TBD (Monte Carlo OR AI Generator OR Live Data)

---

## 📄 **DOCUMENTATION MAP**

### **Session/Handoff Docs:**
- `SESSION_SUMMARY.md` - Complete session recap
- `QUICK_START_FOR_NEW_AGENT.md` - Quick reference
- `PROJECT_INDEX.md` - This file

### **Technical Docs:**
- `docs/PHASE_4_FOUNDATION.md` - API architecture
- `docs/PHASE_4B_COMPLETE.md` - Generation features
- `docs/BACKLOG_SYSTEM_V1.md` - Backlog manager
- `docs/PARAMETER_SWEEP_V1.md` - Sweep engine
- `docs/DASHBOARD_V2_MULTI_STRATEGY.md` - Multi-strategy

### **User Guides:**
- `guides/README.md` - Guide navigation
- `guides/INDEX.md` - Complete doc index
- `guides/*.pdf` - PDF manuals

### **Code Documentation:**
- Every module has docstrings
- API functions fully documented
- Type hints throughout

---

## 🎯 **KEY MODULES REFERENCE**

### **API Layer:**
```python
from meridian_v2_1_2.api import run_backtest
result = run_backtest(strategy_name, params)
```

### **Storage Layer:**
```python
from meridian_v2_1_2.storage import save_run, load_all_runs
save_run(result.to_dict())
runs = load_all_runs()
```

### **Notebook Generation:**
```python
from meridian_v2_1_2.notebook_generation import (
    generate_notebook_from_strategy,
    extract_strategy_template
)
```

### **Visualization:**
```python
from meridian_v2_1_2.dashboard.components.backtest_viz import (
    plot_equity_curve,
    metrics_table,
    backtest_summary
)
```

### **Parameter Tools:**
```python
from meridian_v2_1_2.dashboard.utils.param_extractor import (
    extract_params,
    update_params_in_cell
)
```

---

## 🧪 **TESTING**

### **Test Files:**
- `tests/test_backlog_system.py` - Backlog manager tests
- `tests/test_param_sweep.py` - Sweep engine tests
- `tests/test_dashboard_v2.py` - Dashboard v2 tests
- *Plus 89 other test files*

### **Run Tests:**
```bash
# All tests
pytest tests/ -v

# Specific suite
pytest tests/test_backlog_system.py -v

# With coverage
pytest tests/ --cov=meridian_v2_1_2 --cov-report=html
```

---

## 🛠️ **COMMON TASKS**

### **Start Dashboard:**
```bash
./scripts/start_dashboard.sh
# Or:
cd /path/to/meridian_v2_1_2_full
PYTHONPATH="$PWD/src:$PYTHONPATH" streamlit run src/meridian_v2_1_2/dashboard/ui.py
```

### **Run Diagnostics:**
```bash
./scripts/MeridianEnvironmentDoctor_ProEdition.sh
```

### **Check Registry:**
```bash
cat data/backtest_runs.json | python3 -m json.tool
```

### **Generate Notebook:**
```python
from meridian_v2_1_2.notebook_generation import create_strategy_notebook
from pathlib import Path
create_strategy_notebook("FLD", Path("notebooks/research.ipynb"))
```

---

## 🔗 **EXTERNAL LINKS**

### **Dashboard:**
- Local: http://localhost:8501
- Network: http://192.168.178.96:8501

### **Documentation:**
- Project README: `README.md`
- API Docs: `docs/`
- User Guides: `guides/`

---

## 📞 **GETTING HELP**

### **For Code Understanding:**
1. Check module docstrings
2. Review test files for examples
3. Read `docs/PHASE_*.md` files
4. Check this index

### **For Architecture:**
1. Read `SESSION_SUMMARY.md`
2. Review `docs/PHASE_4_FOUNDATION.md`
3. Check directory structure above

### **For Tasks:**
1. Check `BACKLOG.md`
2. Read `QUICK_START_FOR_NEW_AGENT.md`
3. Review `SESSION_SUMMARY.md` next steps

---

## 📊 **PROJECT STATS**

- **Total Files:** 454+ source files
- **Tests:** 682 available
- **Dashboard Pages:** 6
- **Phases Complete:** 41+ (8 in last session)
- **Lines of Code:** ~55,000+
- **Documentation Pages:** 20+
- **Health Score:** 96%

---

## 🎓 **LEARNING PATH**

### **For New Developers:**
1. Start with `QUICK_START_FOR_NEW_AGENT.md`
2. Read `SESSION_SUMMARY.md`
3. Review `guides/quickstart_full.pdf`
4. Explore dashboard pages
5. Read `docs/PHASE_4_FOUNDATION.md`
6. Review test files for examples

### **For Continuing Work:**
1. Check `BACKLOG.md` for priorities
2. Review `SESSION_SUMMARY.md` next steps
3. Verify system with diagnostic script
4. Complete Phase 4 integration
5. Plan Phase 5 with user

---

## ✅ **QUICK VERIFICATION**

**System is healthy when:**
- ✅ Dashboard loads on port 8501
- ✅ All 6 pages display without errors
- ✅ Can create/edit notebooks
- ✅ Backtest API works
- ✅ Registry saves/loads
- ✅ Tests pass

**Quick check:**
```bash
./scripts/MeridianEnvironmentDoctor_ProEdition.sh
```

---

## 🚀 **NEXT ACTIONS**

**Immediate (1-2 hours):**
1. Create `05_Backtest_Results.py`
2. Add "Run as Backtest" button
3. Test end-to-end

**Short-term (1-2 days):**
1. Complete Phase 4 integration
2. Choose Phase 5 direction
3. Plan implementation

**Long-term:**
- Phase 5: Advanced features
- Live data integration
- Production deployment
- User training

---

**This index is your map to the entire Meridian v2.1.2 project!** 🗺️

*Updated: 2025-12-03*  
*Version: v2.1.2*  
*Status: ✅ PRODUCTION-READY (90%)*


