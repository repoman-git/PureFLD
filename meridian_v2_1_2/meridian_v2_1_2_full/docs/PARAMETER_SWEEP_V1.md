# PARAMETER SWEEP ENGINE v1

**Hyperparameter Optimization System for Meridian v2.1.2**

## Overview

The Parameter Sweep Engine provides comprehensive hyperparameter optimization capabilities for Meridian. It enables systematic exploration of strategy parameters to find optimal configurations.

## Architecture

### Components

#### 1. SweepConfig
Defines the search space and sweep settings.

```python
from meridian_v2_1_2.research.param_sweep import SweepConfig

config = SweepConfig(
    mode="grid",  # or "random"
    fld_offsets=[5, 10, 15],
    cot_thresholds=[-0.2, 0.0, 0.2],
    random_samples=50
)
```

#### 2. SweepGrid
Generates parameter combinations.

- **Grid Search**: Cartesian product of all parameter values
- **Random Search**: Random sampling from parameter space

#### 3. SweepRunner
Executes backtests for all parameter combinations.

```python
from meridian_v2_1_2.research.param_sweep import SweepRunner

runner = SweepRunner(config)
results = runner.run(prices, cot, seasonal, initial_capital=100000)
```

#### 4. SweepResults
Stores, ranks, and analyzes results.

```python
# Get best parameters
best = results.get_best_params('sharpe_ratio')

# Get top N
top_10 = results.get_top_n(n=10)

# Export
results.export('outputs/sweeps/')
```

#### 5. SweepVisualizer
Creates charts and heatmaps.

```python
from meridian_v2_1_2.research.param_sweep import SweepVisualizer

viz = SweepVisualizer(results)
viz.plot_heatmap('fld_offset', 'cot_threshold', 'sharpe_ratio')
viz.plot_pareto_frontier()
viz.create_summary_report()
```

## Usage

### Basic Grid Search

```python
from meridian_v2_1_2.research.param_sweep import *

# Configure sweep
config = SweepConfig(
    mode="grid",
    fld_offsets=[5, 10, 15],
    fld_smoothing=[3, 5, 7],
    cot_thresholds=[-0.2, 0.0, 0.2]
)

# Run sweep
runner = SweepRunner(config)
results = runner.run(prices, cot, seasonal)

# Analyze
best_params = results.get_best_params()
print(f"Best Sharpe: {best_params['sharpe_ratio']:.2f}")
print(f"Best FLD offset: {best_params['fld_offset']}")

# Export
results.export()
```

### Random Search

```python
config = SweepConfig(
    mode="random",
    random_samples=100,
    random_seed=42
)

runner = SweepRunner(config)
results = runner.run(prices, cot, seasonal)
```

### Visualizations

```python
viz = SweepVisualizer(results)

# Parameter vs metric scatter
viz.plot_parameter_vs_metric('fld_offset', 'sharpe_ratio')

# Heatmap
viz.plot_heatmap('fld_offset', 'cot_threshold', 'sharpe_ratio')

# Metric distribution
viz.plot_metric_distribution('sharpe_ratio')

# Pareto frontier
viz.plot_pareto_frontier('total_return', 'max_drawdown')

# Full report
viz.create_summary_report('outputs/sweeps/')
```

## Parameter Ranges

### FLD Parameters
- `fld_offsets`: FLD offset values (default: [5, 10, 15])
- `fld_smoothing`: Smoothing window (default: [3, 5, 7])

### COT Parameters
- `cot_thresholds`: COT filter thresholds (default: [-0.2, 0.0, 0.2])
- `cot_lookback`: COT lookback periods (default: [50, 100, 150])

### TDOM Parameters
- `tdom_filter_enabled`: Enable/disable (default: [True, False])
- `tdom_threshold`: Threshold values (default: [0.3, 0.5, 0.7])

### Execution Parameters
- `slippage_bps`: Slippage in basis points (default: [2.0, 4.0, 8.0])

## Optimization Metrics

### Primary Metrics
- **sharpe_ratio**: Risk-adjusted returns
- **total_return**: Absolute returns
- **max_drawdown**: Maximum peak-to-trough decline

### Additional Metrics
- **num_trades**: Trade frequency
- **win_rate**: Percentage of winning trades
- **final_equity**: Ending portfolio value

## Advanced Features

### Parallel Execution
```python
config = SweepConfig(
    enable_parallel=True,
    n_jobs=4  # Use 4 CPU cores
)
```

### Max Combinations Limit
```python
config = SweepConfig(
    max_combinations=1000  # Limit to first 1000 combos
)
```

### Custom Metrics
Results include all standard metrics automatically.

## Output Files

When you run `results.export()`:

```
outputs/sweeps/
├── sweep_results.csv      # Full results table
├── top_results.csv        # Top N parameter sets
├── best_params.json       # Best single configuration
├── summary_stats.json     # Statistical summary
└── charts/
    ├── sharpe_ratio_distribution.png
    ├── total_return_distribution.png
    ├── max_drawdown_distribution.png
    └── pareto_frontier.png
```

## Best Practices

### 1. Start Small
Begin with coarse grid, then refine around best regions:
```python
# Coarse sweep
config = SweepConfig(fld_offsets=[5, 10, 15, 20])
results = runner.run(...)
best = results.get_best_params()

# Refined sweep around best
config = SweepConfig(fld_offsets=[8, 9, 10, 11, 12])
```

### 2. Use Random Search for Large Spaces
When parameter space is huge (>10,000 combinations), use random search.

### 3. Consider Multiple Metrics
Don't optimize only Sharpe - check:
- Drawdown
- Trade frequency
- Win rate

### 4. Out-of-Sample Validation
Always test best parameters on held-out data.

### 5. Avoid Overfitting
- Use conservative parameter ranges
- Validate with walk-forward analysis
- Check robustness across regimes

## Integration with Other Phases

### With Phase 38 (Backtest Notebook)
Use sweep results to configure the unified backtest.

### With Phase 20 (WFA)
Combine parameter sweep with walk-forward analysis for robust optimization.

### With Phase 19 (Attribution)
Analyze which parameters drive performance.

### With Phase 21 (Incubation)
Use sweep results to identify promotion-worthy configurations.

## Performance Tips

### Memory Optimization
For long sweeps, save intermediate results:
```python
results.export_every_n = 100  # Save every 100 runs
```

### Speed Optimization
- Use smaller datasets for initial sweeps
- Enable parallel execution
- Limit max combinations

## Troubleshooting

### Long Runtime
- Reduce parameter ranges
- Use random search
- Enable parallel execution

### Memory Issues
- Process smaller chunks
- Save intermediate results
- Reduce backtest period

### No Clear Winner
- Expand parameter ranges
- Try different metrics
- Check for regime sensitivity

## Example Workflow

```python
# 1. Load data
prices = load_prices('GLD', '2020-01-01', '2024-01-01')
cot = load_cot('GLD')
seasonal = compute_seasonal_scores()

# 2. Configure sweep
config = SweepConfig(
    mode="grid",
    fld_offsets=[5, 10, 15, 20],
    cot_thresholds=[-0.3, -0.1, 0.0, 0.1, 0.3],
    slippage_bps=[2.0, 4.0, 8.0]
)

# 3. Run sweep
runner = SweepRunner(config)
results = runner.run(prices, cot, seasonal)

# 4. Analyze
print(results.summary_statistics())
best = results.get_best_params()
top_10 = results.get_top_n(10)

# 5. Visualize
viz = SweepVisualizer(results)
viz.plot_heatmap('fld_offset', 'cot_threshold', 'sharpe_ratio')
viz.plot_pareto_frontier()

# 6. Export
results.export('outputs/sweeps/')

# 7. Validate best params with WFA
# Use walk-forward analysis to confirm robustness
```

## Limitations

- Computational cost grows exponentially with parameters
- Risk of overfitting to historical data
- No guarantee of future performance
- May miss non-linear parameter interactions

## Future Enhancements

Planned for future versions:
- Bayesian optimization
- Multi-objective optimization
- Adaptive sampling
- Cross-validation
- Regime-specific sweeps

---

**Status**: ✅ Complete  
**Phase**: 39  
**Version**: 1.0  
**Last Updated**: 2025-12-03


