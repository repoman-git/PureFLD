"""
Strategy → Notebook Generator

Automatically generate research notebooks from strategy templates.
"""

import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


# Strategy metadata and descriptions
STRATEGY_INFO = {
    "FLD": {
        "title": "FLD (Filtered Line of Demarcation) Strategy",
        "description": """
This notebook implements the FLD geometric strategy combined with COT sentiment 
filtering and seasonal scoring.

**Key Concepts:**
- FLD: Geometric signal generation based on price displacement
- COT: Commitment of Traders sentiment filtering
- Seasonal: TDOM/TDOY monthly and annual seasonality

**Default Parameters:**
- `fld_offset`: Displacement for FLD calculation (default: 10)
- `cot_threshold`: COT filter threshold (default: 0.0)
- `enable_seasonal`: Use seasonal scoring (default: True)
""",
        "default_params": {
            "fld_offset": 10,
            "cot_threshold": 0.0,
            "enable_seasonal": True,
            "initial_capital": 100000.0
        }
    },
    "Generic": {
        "title": "Generic Strategy Template",
        "description": """
This is a template notebook for developing custom trading strategies.

Modify the parameters and logic to suit your research needs.
""",
        "default_params": {
            "initial_capital": 100000.0
        }
    }
}


def generate_notebook_from_strategy(
    strategy_name: str = "FLD",
    params: Optional[Dict[str, Any]] = None,
    include_analysis: bool = True
) -> nbf.NotebookNode:
    """
    Generate a research notebook from a strategy template.
    
    Args:
        strategy_name: Name of the strategy ("FLD", "Generic", etc.)
        params: Custom parameters (merges with defaults)
        include_analysis: Include analysis template cells
    
    Returns:
        NotebookNode: Ready-to-use notebook
    """
    
    # Get strategy info
    info = STRATEGY_INFO.get(strategy_name, STRATEGY_INFO["Generic"])
    
    # Merge parameters
    notebook_params = info["default_params"].copy()
    if params:
        notebook_params.update(params)
    
    # Create notebook
    nb = new_notebook()
    
    # Cell 1: Title and description
    title_cell = new_markdown_cell(f"""# {info['title']}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{info['description']}

---

## 📋 Notebook Structure

1. **Parameters** - Define strategy parameters
2. **Execution** - Run the backtest
3. **Results** - View performance metrics
4. **Analysis** - Deep dive into results
5. **Conclusions** - Document findings

---
""")
    
    # Cell 2: Imports
    imports_cell = new_code_cell("""# Core imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Meridian imports
from meridian_v2_1_2.api import run_backtest
from meridian_v2_1_2.storage import save_run
from meridian_v2_1_2.dashboard.components.backtest_viz import (
    plot_equity_curve,
    plot_equity_with_drawdown,
    metrics_table
)

print("✅ Imports loaded successfully")""")
    
    # Cell 3: Parameters
    params_code = "params = {\n"
    for key, value in notebook_params.items():
        if isinstance(value, str):
            params_code += f"    '{key}': '{value}',\n"
        elif isinstance(value, bool):
            params_code += f"    '{key}': {value},\n"
        else:
            params_code += f"    '{key}': {value},\n"
    params_code += "}\n\nprint('📐 Parameters configured:')\nfor k, v in params.items():\n    print(f'  {k}: {v}')"
    
    params_cell = new_code_cell(params_code)
    
    # Cell 4: Run backtest
    execution_cell = new_code_cell(f"""# Run the backtest
print("🚀 Running backtest...")

result = run_backtest(
    strategy_name="{strategy_name}",
    params=params,
    initial_capital=params.get('initial_capital', 100000.0)
)

if result.success:
    print("✅ Backtest completed successfully!")
    print(f"   Run ID: {{result.run_id}}")
    print(f"   Trades: {{len(result.trades)}}")
    print(f"   Final Equity: ${{result.metrics['final_equity']:,.0f}}")
else:
    print("❌ Backtest failed!")
    print(f"   Error: {{result.error}}")""")
    
    # Cell 5: Display metrics
    metrics_cell = new_code_cell("""# Display performance metrics
if result.success:
    print("📊 Performance Metrics:")
    print("=" * 50)
    metrics_table(result.metrics)
else:
    print("No metrics available (backtest failed)")""")
    
    # Cell 6: Equity curve
    equity_cell = new_code_cell("""# Plot equity curve
if result.success and result.equity_curve:
    plot_equity_with_drawdown(result.equity_curve)
else:
    print("No equity data to plot")""")
    
    # Cell 7: Trade analysis
    trades_cell = new_code_cell("""# Analyze trades
if result.success and result.trades:
    trades_df = pd.DataFrame(result.trades)
    
    print(f"📝 Trade Summary:")
    print(f"   Total Trades: {len(trades_df)}")
    
    if 'action' in trades_df.columns:
        print(f"   Buy Signals: {(trades_df['action'] == 'BUY').sum()}")
        print(f"   Sell Signals: {(trades_df['action'] == 'SELL').sum()}")
    
    print("\\n First 10 trades:")
    display(trades_df.head(10))
else:
    print("No trades to analyze")""")
    
    # Cell 8: Save to registry
    save_cell = new_code_cell("""# Save results to registry
if result.success:
    save_run(result.to_dict())
    print(f"💾 Results saved to registry (Run ID: {result.run_id})")
else:
    print("⚠️ Skipping save (backtest failed)")""")
    
    # Add all cells
    nb.cells = [
        title_cell,
        imports_cell,
        params_cell,
        execution_cell,
        metrics_cell,
        equity_cell,
        trades_cell,
        save_cell
    ]
    
    # Add analysis template cells if requested
    if include_analysis:
        analysis_section = new_markdown_cell("""---

## 🔬 Advanced Analysis

Use the cells below for deeper analysis:
- Parameter sensitivity
- Trade distribution
- Monthly performance
- Risk-adjusted returns
- Custom visualizations
""")
        
        analysis_cell1 = new_code_cell("""# Custom analysis cell 1
# Add your analysis code here

# Example: Monthly returns analysis
# if result.success:
#     # Your code here
#     pass
""")
        
        analysis_cell2 = new_code_cell("""# Custom analysis cell 2
# Add your visualizations here

# Example: Distribution plots
# if result.success:
#     # Your code here
#     pass
""")
        
        conclusions_cell = new_markdown_cell("""---

## 📌 Conclusions

**Key Findings:**
- [Add your observations]

**Parameter Insights:**
- [Add parameter analysis]

**Next Steps:**
- [Add recommendations]

---

*Notebook generated by Meridian v2.1.2*
""")
        
        nb.cells.extend([
            analysis_section,
            analysis_cell1,
            analysis_cell2,
            conclusions_cell
        ])
    
    return nb


def create_strategy_notebook(
    strategy_name: str,
    output_path: Path,
    params: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Create and save a strategy notebook to disk.
    
    Args:
        strategy_name: Name of strategy
        output_path: Where to save the notebook
        params: Custom parameters
    
    Returns:
        bool: Success status
    """
    try:
        nb = generate_notebook_from_strategy(strategy_name, params)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
        
        return True
        
    except Exception as e:
        print(f"Error creating notebook: {e}")
        return False


def add_strategy_info(strategy_name: str, info: Dict[str, Any]):
    """
    Register a new strategy template.
    
    Args:
        strategy_name: Strategy identifier
        info: Dictionary with 'title', 'description', 'default_params'
    """
    STRATEGY_INFO[strategy_name] = info

