# UNIFIED BACKTEST NOTEBOOK v1

**Production-Grade Backtesting Engine for Meridian v2.1.2**

## Overview

The Unified Backtest Notebook (`backtest_meridian_v2_1_2.ipynb`) is the canonical research interface for Meridian. It provides a complete end-to-end backtesting workflow using all production modules.

## Features

### ✅ Complete Integration
- Uses production modules directly (no reimplementation)
- FLD calculation
- Strategy signal generation
- PnL calculation
- Risk metrics
- Professional visualizations

### ✅ Environment Flexibility
- Runs locally in Jupyter Lab/VS Code
- Runs in Google Colab
- Automatic environment detection
- Path configuration handling

### ✅ Production-Ready Workflow
1. Environment setup
2. Data loading (synthetic or real)
3. FLD calculation
4. Signal generation
5. PnL calculation
6. Visualization
7. Results export

## Usage

### Local Execution

```bash
jupyter notebook notebooks/backtest_meridian_v2_1_2.ipynb
```

### Google Colab

1. Upload notebook to Colab
2. Run cells sequentially
3. Notebook auto-detects Colab environment

## Sections

### Section 00: Environment Setup
- Detects Colab vs local
- Configures paths
- Loads project root

### Section 01: Module Loading
- Imports all production modules
- Sets up plotting style
- Validates imports

### Section 02: Configuration & Data
- Sets backtest parameters
- Loads data (synthetic or real)
- Configures strategy

### Section 03: Signal Generation & PnL
- Calculates FLD
- Generates strategy signals
- Computes PnL and metrics
- Calculates Sharpe ratio and drawdown

### Section 04: Visualizations
- Equity curve
- Drawdown chart
- Signal overlay
- Performance metrics

### Section 05: Summary
- Next steps guidance
- Export options
- Research recommendations

## Customization

### Data Sources

Replace synthetic data with real data:

```python
# Instead of synthetic
from meridian_v2_1_2.data_providers.openbb import load_prices

prices = load_prices('GLD', START_DATE, END_DATE)
```

### Strategy Configuration

```python
config = MeridianConfig()
config.strategy.enable_fld = True
config.strategy.enable_cot_filter = True
config.strategy.enable_tdom_filter = True
config.fld.offset = 10  # Tune parameters
```

### Multiple Assets

```python
symbols = ['GLD', 'LTPZ', 'UUP']
for symbol in symbols:
    # Run backtest for each
    ...
```

## Outputs

### Generated Files
- `outputs/equity_curve.csv` - Equity time series
- `outputs/signals.csv` - Signal history
- `outputs/metrics.json` - Performance metrics
- Charts (displayed inline)

### Metrics Calculated
- Total return
- Sharpe ratio
- Maximum drawdown
- Win rate
- Average trade PnL
- Number of signals

## Integration with Other Phases

### Phase 39: Parameter Sweep
Use this notebook as the base for parameter optimization

### Phase 19: Attribution Engine
Add attribution breakdown to understand factor contributions

### Phase 23: Paper Simulator
Connect to paper execution for realistic fills

### Phase 35: Dashboard
View results in the Operator Dashboard

## Best Practices

### Research Workflow
1. Start with synthetic data for quick iteration
2. Validate logic with known scenarios
3. Switch to real data for final testing
4. Use Parameter Sweep for optimization
5. Run paper trading before live

### Performance Validation
- Always check for lookahead bias
- Verify signal alignment
- Validate execution assumptions
- Compare to buy-and-hold benchmark
- Test across different market regimes

### Reproducibility
- Set random seeds for synthetic data
- Document parameter choices
- Export all configurations
- Version control notebooks

## Troubleshooting

### Module Import Errors
```python
# Verify path
import sys
print(sys.path)

# Add project root manually
sys.path.insert(0, '/path/to/meridian_v2_1_2/src')
```

### Data Loading Issues
- Check data format (OHLCV required)
- Verify date alignment
- Ensure no missing values
- Validate index is DatetimeIndex

### Performance Issues
- Reduce backtest period
- Use fewer bars for testing
- Profile slow sections
- Consider vectorization

## Future Enhancements

### Planned Features
- [ ] Multi-asset portfolio mode
- [ ] Walk-forward analysis integration
- [ ] Regime-specific reporting
- [ ] Automated parameter tuning
- [ ] Execution cost modeling
- [ ] Factor attribution charts

### Optional Extensions
- Monte Carlo simulation
- Confidence intervals
- Sensitivity analysis
- Scenario testing
- Stress testing

## References

- Phase 1-7: Core strategy modules
- Phase 22: Data integration layer
- Phase 23: Execution simulator
- Phase 39: Parameter sweep engine
- Phase 19: Performance attribution

## Support

For issues or questions:
1. Check test suite: `pytest tests/`
2. Review phase documentation
3. Validate configuration
4. Test with synthetic data first

---

**Status**: ✅ Complete  
**Phase**: 38  
**Version**: 1.0  
**Last Updated**: 2025-12-03

