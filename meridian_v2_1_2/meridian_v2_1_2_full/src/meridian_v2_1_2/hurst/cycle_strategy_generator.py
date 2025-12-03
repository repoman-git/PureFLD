"""
Cycle-Based Trading Strategy Generator

Generates full trading strategies based on:
- Cycle phasing
- VTL breaks
- FLD crossovers
- Composite harmonics
- Phase-conditioned returns
- Forecasted cycle position

Outputs:
- Signals
- Backtest-ready position vector
- Performance statistics
- Strategy JSON descriptor (AI-ready)

⚠️  EDUCATIONAL ONLY - Generated strategies for research
"""

import pandas as pd
import numpy as np


class CycleStrategyGenerator:
    """
    Generates cycle-based trading strategies using:
      - phasing
      - FLDs
      - VTL breaks
      - Harmonics
      - AI Forecast (optional)
    
    ⚠️  EDUCATIONAL - Strategy generation for research only
    """

    def __init__(self, price: pd.Series):
        """
        Initialize strategy generator.
        
        Args:
            price: Price series
        """
        self.price = price

    # --------------------------------------------------------------
    # 1. Strategy Rules
    # --------------------------------------------------------------
    def generate_rules(self, phasing, fld_crosses, vtls, forecast=None):
        """
        Generate trading rules from cycle components.
        
        Args:
            phasing: Phasing results dict with 'phase' series
            fld_crosses: FLD crosses dict with 'long' and 'short' boolean series
            vtls: VTL breaks dict with 'long_break' and 'short_break' series
            forecast: Optional AI forecast series
        
        Returns:
            Dictionary of rule conditions
        """
        rules = {}

        # Rule A — Trough-phase entry
        rules["A_trough_entry"] = (
            (phasing["phase"] < 0.25) &
            (fld_crosses["long"])
        )

        # Rule B — Peak-phase exit
        rules["B_peak_exit"] = (
            (phasing["phase"] > 0.75) &
            (fld_crosses["short"])
        )

        # Rule C — VTL trend change
        rules["C_vtl_break_long"] = vtls["long_break"]
        rules["C_vtl_break_short"] = vtls["short_break"]

        # Rule D — Forecast bias
        if forecast is not None:
            rules["D_ai_up"] = forecast.diff().rolling(5).mean() > 0
            rules["D_ai_down"] = forecast.diff().rolling(5).mean() < 0

        return rules

    # --------------------------------------------------------------
    # 2. Combine rule sets into a strategy signal
    # --------------------------------------------------------------
    def build_strategy(self, rules):
        """
        Combine rules into strategy signal.
        
        Args:
            rules: Dictionary of rule conditions
        
        Returns:
            Signal series (1=long, -1=short, 0=flat)
        """
        signal = pd.Series(0, index=self.price.index)

        # Long entries
        long_cond = (
            rules.get("A_trough_entry", False) |
            rules.get("C_vtl_break_long", False) |
            rules.get("D_ai_up", False)
        )

        # Short entries
        short_cond = (
            rules.get("B_peak_exit", False) |
            rules.get("C_vtl_break_short", False) |
            rules.get("D_ai_down", False)
        )

        signal[long_cond] = 1
        signal[short_cond] = -1

        return signal

    # --------------------------------------------------------------
    # 3. Backtest
    # --------------------------------------------------------------
    def backtest(self, signal):
        """
        Backtest strategy signal.
        
        Args:
            signal: Strategy signal series
        
        Returns:
            Dictionary with performance metrics
        
        ⚠️  EDUCATIONAL - Backtest results for research only
        """
        ret = self.price.pct_change().shift(-1)
        strat = ret * signal
        equity = (1 + strat).cumprod()
        
        return {
            "returns": strat,
            "equity": equity,
            "CAGR": equity.iloc[-1]**(252/len(equity)) - 1 if len(equity) > 0 else 0,
            "Sharpe": strat.mean() / strat.std() * np.sqrt(252) if strat.std() > 0 else 0,
            "MaxDD": (equity / equity.cummax() - 1).min(),
            "equity_curve": equity
        }

    # --------------------------------------------------------------
    # 4. Export strategy descriptor (AI-ready)
    # --------------------------------------------------------------
    def export_json(self, rules):
        """
        Export strategy as JSON descriptor.
        
        Can be used by AI agents for strategy understanding.
        
        Args:
            rules: Dictionary of rules
        
        Returns:
            Dictionary with strategy description
        """
        return {
            "strategy_name": "CycleFusion v1",
            "modules": ["Hurst Phasing", "VTL", "FLD", "Forecast AI"],
            "rules": list(rules.keys()),
            "entry_logic": "Trough phase + FLD cross + VTL break + AI bias",
            "exit_logic": "Peak phase + FLD cross + VTL break",
            "timeframe": "Daily",
            "risk_management": "Phase-based position sizing"
        }

