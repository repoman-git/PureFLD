"""Strategy Evaluator - Fitness function"""
import pandas as pd
import numpy as np

class StrategyEvaluator:
    """Evaluates fitness of a strategy"""
    
    def evaluate(self, equity_curve: pd.Series) -> float:
        """Calculate fitness score"""
        if len(equity_curve) < 2:
            return 0.0
        
        returns = equity_curve.pct_change().dropna()
        if len(returns) == 0:
            return 0.0
        
        # Sharpe ratio
        sharpe = returns.mean() / (returns.std() + 1e-9) * np.sqrt(252)
        
        # Max drawdown
        peak = equity_curve.expanding().max()
        dd = ((equity_curve - peak) / peak).min()
        
        # Total return
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) if equity_curve.iloc[0] > 0 else 0
        
        # Fitness: balance return, Sharpe, and drawdown
        fitness = 0.4 * sharpe + 0.3 * total_return + 0.3 * (1 + dd)
        
        return fitness

