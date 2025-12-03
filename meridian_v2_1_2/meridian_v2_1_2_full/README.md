# Meridian v2.1.2

**FLD + COT + TDOM Trading Research Framework**

A Python-based research framework for analyzing and backtesting Future Line of Demarcation (FLD) strategies with COT filtering and seasonal overlays on commodity futures and ETF series.

---

## 🎯 Features

- ✅ **FLD (Future Line of Demarcation)** - Displaced moving average crossover strategies
- ✅ **COT Integration** - Commitment of Traders filtering for entry timing
- ✅ **TDOM v1** - Time Day of Month seasonal overlays (favourable/unfavourable days)
- ✅ **Config-Driven** - All parameters controlled via `MeridianConfig`
- ✅ **Deterministic** - Fully reproducible results
- ✅ **Modular Architecture** - Clean separation of concerns
- ✅ **Comprehensive Tests** - pytest suite included

---

## 📁 Project Structure

```
meridian_v2_1_2_full/
├── src/meridian_v2_1_2/        # Core Python package
│   ├── __init__.py
│   ├── config.py               # Configuration system
│   ├── fld_engine.py           # FLD calculations
│   ├── strategy.py             # Trading signal generation
│   ├── backtester.py           # Backtest execution
│   ├── orchestrator.py         # Main workflow controller
│   ├── cot_factors.py          # COT data loading
│   └── seasonality.py          # TDOM logic
├── scripts/                    # CLI utilities
│   ├── meridian_control.py     # Main CLI interface
│   └── validate_tdom.py        # Quick validation script
├── configs/                    # JSON configuration files
│   └── gold_default.json
├── tests/                      # pytest test suite
│   ├── test_placeholder.py
│   └── test_seasonality_integration.py
├── notebooks/                  # Jupyter research notebooks
│   ├── tdom_fld_example.ipynb
│   └── tdom_integration_demo.ipynb
├── data/                       # Sample data files
│   ├── gc_sample.csv           # Gold futures prices
│   └── cot_sample.csv          # COT factors
├── docs/                       # Documentation
│   └── architecture.md
├── ai/                         # AI assistant configs
│   ├── prompts/
│   └── assistants/
├── TDOM_INTEGRATION_COMPLETE.md
└── README.md
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone or extract the repository
cd meridian_v2_1_2_full

# Install dependencies (requires pandas)
pip install pandas matplotlib pytest
```

### Basic Usage

#### Python API

```python
from meridian_v2_1_2 import MeridianConfig, run_backtest
import pandas as pd

# Load price data
prices = pd.read_csv('data/gc_sample.csv', parse_dates=['date'], index_col='date')['close']

# Configure with TDOM enabled
config = MeridianConfig()
config.seasonality.use_tdom = True
config.seasonality.favourable_days = [1, 2, 3, 4, 5]
config.seasonality.unfavourable_days = [15, 16]
config.strategy.use_tdom = True

# Run backtest
results = run_backtest(config, prices)

# View results
print(f"Total Signals: {results['stats']['total_trades']}")
print(f"TDOM Flags:\n{results['tdom'].value_counts()}")
```

#### Command Line Interface

```bash
# Run with TDOM enabled
python scripts/meridian_control.py \
    --price-data data/gc_sample.csv \
    --use-tdom

# Run with custom config
python scripts/meridian_control.py \
    --price-data data/gc_sample.csv \
    --config configs/gold_default.json

# View help
python scripts/meridian_control.py --help
```

#### Jupyter Notebooks

```bash
# Launch Jupyter
jupyter notebook

# Open notebooks/tdom_integration_demo.ipynb
```

---

## 🧪 Testing

### Quick Validation

```bash
# Run quick validation (no pytest required)
python scripts/validate_tdom.py
```

### Full Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_seasonality_integration.py -v

# Run with coverage
pytest tests/ --cov=meridian_v2_1_2 --cov-report=html
```

---

## ⚙️ Configuration

### Configuration Structure

```python
from meridian_v2_1_2 import MeridianConfig

config = MeridianConfig()

# FLD parameters
config.fld.cycle_length = 40        # FLD cycle length
config.fld.displacement = 20        # FLD displacement

# Seasonality (TDOM)
config.seasonality.use_tdom = True
config.seasonality.favourable_days = [1, 2, 3, 4, 5]
config.seasonality.unfavourable_days = [15, 16]

# Strategy behavior
config.strategy.use_tdom = True     # Enable TDOM gating
config.strategy.use_cot = False     # Enable COT filtering
config.strategy.allow_shorts = True # Allow short positions

# Backtest parameters
config.backtest.initial_capital = 100000.0
config.backtest.commission = 0.0
config.backtest.slippage = 0.0
```

### JSON Configuration

```json
{
  "fld": {
    "cycle_length": 40,
    "displacement": 20
  },
  "seasonality": {
    "use_tdom": true,
    "favourable_days": [1, 2, 3, 4, 5],
    "unfavourable_days": [15, 16]
  },
  "strategy": {
    "use_tdom": true,
    "use_cot": false,
    "allow_shorts": true
  },
  "backtest": {
    "initial_capital": 100000.0,
    "commission": 0.0,
    "slippage": 0.0
  }
}
```

Load from JSON:

```python
import json
from meridian_v2_1_2 import MeridianConfig

with open('configs/gold_default.json', 'r') as f:
    config_dict = json.load(f)

config = MeridianConfig.from_dict(config_dict)
```

---

## 📊 TDOM (Time Day of Month) Integration

### What is TDOM?

TDOM is a seasonal filter that marks specific days of the month as:
- **+1**: Favourable (allow entries)
- **0**: Neutral (allow entries)
- **-1**: Unfavourable (block entries)

### How It Works

1. **Configuration**: Define favourable and unfavourable days in `SeasonalityConfig`
2. **Computation**: `orchestrator.py` calls `compute_tdom_flags()` to generate flags
3. **Gating**: `strategy.py` blocks entry signals when TDOM = -1
4. **Results**: TDOM series included in backtest results

### Example

```python
config = MeridianConfig()
config.seasonality.use_tdom = True
config.seasonality.favourable_days = [1, 2, 3, 4, 5]  # First 5 days
config.seasonality.unfavourable_days = [15, 16]       # Mid-month
config.strategy.use_tdom = True

results = run_backtest(config, prices)

# View TDOM distribution
print(results['tdom'].value_counts())
```

---

## 🏗️ Architecture

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `config.py` | Configuration management |
| `fld_engine.py` | FLD calculation logic |
| `seasonality.py` | TDOM flag computation |
| `strategy.py` | Signal generation with filters |
| `backtester.py` | Trade execution and PnL |
| `orchestrator.py` | End-to-end workflow coordination |
| `cot_factors.py` | COT data loading |

### Workflow

```
orchestrator.run_backtest()
    ↓
1. Load price data
    ↓
2. Compute FLD (fld_engine.py)
    ↓
3. Compute TDOM flags (seasonality.py) [if enabled]
    ↓
4. Generate signals (strategy.py)
    ├─ FLD crossovers
    ├─ TDOM gating [if enabled]
    └─ COT filtering [if enabled]
    ↓
5. Execute backtest (backtester.py)
    ↓
6. Return results
```

---

## 📚 Documentation

- **[TDOM_INTEGRATION_COMPLETE.md](TDOM_INTEGRATION_COMPLETE.md)** - Detailed TDOM v1 implementation guide
- **[docs/architecture.md](docs/architecture.md)** - System architecture documentation
- **Notebooks** - Interactive examples and demonstrations

---

## 🔜 Roadmap

### Implemented
- ✅ TDOM v1 (Time Day of Month)
- ✅ Configuration system
- ✅ Strategy framework
- ✅ Orchestrator workflow
- ✅ CLI interface
- ✅ Test suite

### Planned
- ⏳ Full FLD engine implementation
- ⏳ Complete backtester with PnL tracking
- ⏳ COT factor loading and filtering
- ⏳ TDOY (Trading Day of Year) seasonality
- ⏳ Risk overlays and position sizing
- ⏳ Walk-forward analysis
- ⏳ Multi-market support
- ⏳ Performance reporting

---

## 🧠 Development Guidelines

### Core Principles

1. **Config-Driven**: All parameters through `MeridianConfig`
2. **Module Boundaries**: Each file has specific domain
3. **Deterministic**: No randomness, fully reproducible
4. **Testable**: Comprehensive test coverage
5. **No Refactoring**: Unless explicitly requested

### Adding New Features

1. Add configuration fields to appropriate config class
2. Implement logic in correct module
3. Wire through orchestrator if needed
4. Add tests in `tests/`
5. Update documentation

### Testing Requirements

- Use synthetic data (≤20 rows)
- Test determinism
- Test edge cases
- Test integration points

---

## 📝 License

This is a research framework. Use at your own risk.

---

## 🤝 Contributing

This project follows strict architectural guidelines. See the Master Project Prompt in `ai/prompts/` for development standards.

---

## 📧 Support

For issues or questions, refer to the documentation in `docs/` or the example notebooks in `notebooks/`.

---

**Version**: 2.1.2  
**Status**: TDOM v1 Integration Complete ✅  
**Last Updated**: December 3, 2025

