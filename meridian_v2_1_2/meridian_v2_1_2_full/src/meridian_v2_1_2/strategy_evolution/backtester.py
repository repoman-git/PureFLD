"""Strategy Backtester - Simple long-only"""
import pandas as pd

class StrategyBacktester:
    """Simple backtester for evolved strategies"""
    
    def run(self, price: pd.Series, signal: pd.Series) -> pd.Series:
        """Run backtest"""
        df = pd.DataFrame(index=price.index)
        df["price"] = price
        df["signal"] = signal.shift(1).fillna(0)
        df["returns"] = df["price"].pct_change().fillna(0)
        df["strategy_return"] = df["returns"] * df["signal"]
        df["equity"] = (1 + df["strategy_return"]).cumprod()
        return df["equity"]

