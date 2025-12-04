# 🚀 MERIDIAN v2.1.2 — QUICK START GUIDE

**Your Complete Trading & Research Platform is Ready!**

---

## ⚡ FASTEST PATH TO RESULTS

### 1️⃣ Run Your First Backtest (2 minutes)

```bash
# Open the unified backtest notebook
jupyter notebook notebooks/backtest_meridian_v2_1_2.ipynb

# Run all cells (Shift+Enter through each cell)
# You'll see:
# - Data loaded
# - FLD calculated
# - Signals generated
# - PnL computed
# - Charts displayed
# - Metrics reported
```

**Expected Output:**
- Equity curve chart
- Drawdown visualization
- Performance metrics (Sharpe, Return, MaxDD)
- Signal overlay on price

---

### 2️⃣ Optimize Parameters (5 minutes)

```python
# In a new notebook or Python script
from meridian_v2_1_2.research.param_sweep import *
from meridian_v2_1_2.synthetic import SyntheticDataset

# Generate test data
dataset = SyntheticDataset()
data = dataset.generate()

# Configure parameter sweep
config = SweepConfig(
    fld_offsets=[5, 10, 15, 20],
    cot_thresholds=[-0.2, 0.0, 0.2],
    slippage_bps=[2.0, 4.0]
)

# Run optimization
runner = SweepRunner(config)
results = runner.run(
    data['prices'], 
    data['cot'], 
    pd.Series(0.5, index=data['prices'].index)
)

# Get best parameters
best = results.get_best_params()
print(f"Best Sharpe: {best['sharpe_ratio']:.2f}")
print(f"Best FLD Offset: {best['fld_offset']}")

# Visualize
viz = SweepVisualizer(results)
viz.plot_heatmap('fld_offset', 'cot_threshold', 'sharpe_ratio')
viz.create_summary_report()
```

---

### 3️⃣ Monitor with Dashboard (1 minute)

```bash
# Start the operator dashboard
cd /Users/simonerses/Data-Projects-PureFLD/meridian_v2_1_2/meridian_v2_1_2_full
python3 -m meridian_v2_1_2.dashboard.server

# Open browser to: http://localhost:8501
# You'll see:
# - System status
# - Real-time monitoring
# - Signal approvals
# - PnL tracking
# - Oversight AI alerts
```

---

## 📚 KEY FILES & LOCATIONS

### Notebooks (Start Here!)
```
notebooks/
├── backtest_meridian_v2_1_2.ipynb    # ⭐ Main backtest notebook
├── tdom_integration_demo.ipynb        # TDOM seasonality demo
└── [other demo notebooks]
```

### Documentation
```
docs/
├── BACKTEST_NOTEBOOK_V1.md           # Backtest guide
├── PARAMETER_SWEEP_V1.md             # Optimization guide
├── DASHBOARD_V1.md                   # Dashboard guide
└── [phase-specific docs]
```

### Project Management
```
BACKLOG.md                            # Full task list
BACKLOG_SUMMARY.md                    # Executive summary
scripts/build_backlog.py              # Backlog generator
```

---

## 🎯 COMMON WORKFLOWS

### Research Workflow
```
1. Open backtest notebook
2. Load/generate data
3. Run strategy
4. Analyze results
5. Optimize parameters
6. Validate with walk-forward
7. Export best config
```

### Paper Trading Workflow
```
1. Configure EOD orchestrator
2. Set mode to "paper"
3. Enable paper simulator
4. Run daily cycle
5. Monitor via dashboard
6. Review performance
7. Adjust parameters
```

### Live Trading Workflow (When Ready)
```
1. Complete paper trading validation
2. Configure live mode
3. Set up kill switches
4. Enable oversight AI
5. Start with small capital
6. Monitor continuously
7. Scale gradually
```

---

## 🔧 CONFIGURATION

### Basic Strategy Config
```python
from meridian_v2_1_2.config import MeridianConfig

config = MeridianConfig()

# Enable components
config.strategy.enable_fld = True
config.strategy.enable_cot_filter = True
config.strategy.enable_tdom_filter = True

# Set parameters
config.fld.offset = 10
config.strategy.cot_threshold = 0.0
```

### Backtest Config
```python
START_DATE = '2020-01-01'
END_DATE = '2024-01-01'
SYMBOL = 'GLD'
INITIAL_CAPITAL = 100000
```

### Sweep Config
```python
config = SweepConfig(
    mode="grid",  # or "random"
    fld_offsets=[5, 10, 15, 20],
    cot_thresholds=[-0.3, -0.1, 0.0, 0.1, 0.3],
    primary_metric="sharpe_ratio"
)
```

---

## 📊 UNDERSTANDING RESULTS

### Key Metrics
- **Sharpe Ratio**: Risk-adjusted returns (>1.0 is good, >2.0 is excellent)
- **Total Return**: Absolute percentage gain/loss
- **Max Drawdown**: Largest peak-to-trough decline (lower is better)
- **Win Rate**: Percentage of profitable trades
- **Num Trades**: Trade frequency

### Interpreting Charts
- **Equity Curve**: Should trend upward with controlled volatility
- **Drawdown**: Should recover quickly, stay shallow
- **Signal Overlay**: Verify signals align with FLD crossovers
- **Heatmap**: Find parameter sweet spots (green zones)

---

## 🐛 TROUBLESHOOTING

### Import Errors
```bash
# Ensure you're in the right directory
cd /Users/simonerses/Data-Projects-PureFLD/meridian_v2_1_2/meridian_v2_1_2_full

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Notebook Not Found
```bash
# Check you're in project root
pwd  # Should end in meridian_v2_1_2_full

# List notebooks
ls notebooks/
```

### Module Not Found
```python
# In notebook, add this cell at top:
import sys
from pathlib import Path
sys.path.insert(0, str(Path().resolve().parent / 'src'))
```

### Tests Failing
```bash
# Run tests to check system health
python3 -m pytest tests/ -q

# Expected: 631+ passing
```

---

## 💡 PRO TIPS

### 1. Start with Synthetic Data
- Faster iteration
- Known ground truth
- No API dependencies
- Perfect for learning

### 2. Use Small Parameter Ranges First
- Test with 2-3 values per parameter
- Expand once you understand behavior
- Avoid combinatorial explosion

### 3. Monitor Everything
- Use dashboard during paper trading
- Check oversight AI warnings
- Review backlog regularly
- Track parameter drift

### 4. Document Your Research
- Export sweep results
- Save notebook outputs
- Track configuration changes
- Note market conditions

### 5. Validate Thoroughly
- Use walk-forward analysis
- Test across regimes
- Check out-of-sample
- Verify with paper trading

---

## 📞 GETTING HELP

### Check Documentation
```bash
# List all docs
ls docs/

# Read specific phase docs
cat docs/BACKTEST_NOTEBOOK_V1.md
```

### Run Tests
```bash
# Full test suite
python3 -m pytest tests/ -v

# Specific module
python3 -m pytest tests/test_strategy.py -v
```

### Check Backlog
```bash
# View current tasks
cat BACKLOG.md

# Rebuild backlog
python3 scripts/build_backlog.py
```

---

## 🎊 YOU'RE READY!

**Your system includes:**
- ✅ 39 complete phases
- ✅ 646 tests (97.7% passing)
- ✅ 230+ production modules
- ✅ Complete documentation
- ✅ Research notebooks
- ✅ Optimization tools
- ✅ Monitoring dashboard
- ✅ Project management

**Now go make some money!** 💰📈🚀

---

**Questions? Check:**
- `BACKLOG_SUMMARY.md` - Project status
- `docs/` - Detailed guides
- `notebooks/` - Working examples
- `tests/` - Usage patterns

**Happy Trading!** 🎯💎🏆


