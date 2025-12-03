"""
Sweep Runner for Meridian v2.1.2

Executes parameter sweep across all combinations.
"""

from typing import List, Dict, Any
import pandas as pd
from tqdm import tqdm

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.strategy import FLDStrategy
from meridian_v2_1_2 import fld_engine

from .sweep_config import SweepConfig
from .sweep_grid import SweepGrid
from .sweep_results import SweepResults


class SweepRunner:
    """
    Executes parameter sweep.
    
    Runs full backtest for each parameter combination
    and collects performance metrics.
    """
    
    def __init__(self, config: SweepConfig):
        """
        Initialize sweep runner.
        
        Args:
            config: SweepConfig instance
        """
        self.config = config
        self.grid = SweepGrid(config)
    
    def run(
        self,
        prices: pd.DataFrame,
        cot: pd.Series,
        seasonal_score: pd.Series,
        initial_capital: float = 100000
    ) -> SweepResults:
        """
        Run parameter sweep.
        
        Args:
            prices: Price data
            cot: COT data
            seasonal_score: Seasonal scores
            initial_capital: Starting capital
        
        Returns:
            SweepResults instance
        """
        # Generate parameter combinations
        combinations = self.grid.generate()
        
        print(f"🔍 Running sweep: {len(combinations)} combinations")
        
        results = SweepResults(self.config)
        
        # Run backtest for each combination
        for idx, params in enumerate(tqdm(combinations, desc="Sweep Progress")):
            try:
                metrics = self._run_single_backtest(
                    params,
                    prices,
                    cot,
                    seasonal_score,
                    initial_capital
                )
                
                results.add_result(params, metrics)
            
            except Exception as e:
                print(f"Error in combination {idx}: {e}")
                continue
        
        print(f"✅ Sweep complete: {len(results.results)} successful runs")
        
        return results
    
    def _run_single_backtest(
        self,
        params: Dict[str, Any],
        prices: pd.DataFrame,
        cot: pd.Series,
        seasonal_score: pd.Series,
        initial_capital: float
    ) -> Dict[str, float]:
        """Run single backtest with given parameters"""
        # Create config with parameters
        config = MeridianConfig()
        config.fld.offset = params['fld_offset']
        config.fld.smoothing = params['fld_smoothing']
        config.strategy.cot_threshold = params['cot_threshold']
        config.strategy.enable_tdom_filter = params['tdom_filter']
        
        # Calculate FLD
        fld_result = fld_engine.calculate_fld(
            prices['close'], 
            params['fld_offset'], 
            params['fld_smoothing']
        )
        
        # Generate signals
        strategy = FLDStrategy(config.strategy)
        result = strategy.generate_signals(
            prices=prices['close'],
            fld=fld_result,
            cot_series=cot.iloc[:len(prices)],
            seasonal_score=seasonal_score
        )
        
        signals = result['signal']
        
        # Calculate PnL
        positions = signals.shift(1).fillna(0)
        returns = prices['close'].pct_change()
        strategy_returns = positions * returns
        
        # Apply slippage
        slippage_cost = params['slippage_bps'] / 10000
        strategy_returns = strategy_returns - abs(positions.diff()) * slippage_cost
        
        equity_curve = initial_capital * (1 + strategy_returns).cumprod()
        
        # Calculate metrics
        total_return = (equity_curve.iloc[-1] / initial_capital - 1)
        sharpe = (strategy_returns.mean() / strategy_returns.std() * (252 ** 0.5)
                  if strategy_returns.std() > 0 else 0)
        max_dd = ((equity_curve / equity_curve.expanding().max()) - 1).min()
        
        num_trades = abs(positions.diff()).sum() / 2
        win_rate = (strategy_returns[strategy_returns > 0].count() / 
                   len(strategy_returns[strategy_returns != 0]) 
                   if len(strategy_returns[strategy_returns != 0]) > 0 else 0)
        
        return {
            'total_return': float(total_return),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_dd),
            'num_trades': float(num_trades),
            'win_rate': float(win_rate),
            'final_equity': float(equity_curve.iloc[-1])
        }

