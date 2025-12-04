"""
Risk Configuration for Meridian v2.1.2

Configuration for adaptive position sizing and risk management.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RiskConfig:
    """Configuration for risk engine and position sizing"""
    enable_risk_engine: bool = False
    
    # Volatility sizing
    vol_lookback: int = 20
    target_vol: float = 0.02  # 2% target volatility
    use_volatility_sizing: bool = True
    
    # Regime sizing
    use_regime_sizing: bool = True
    regime_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "low_vol": 1.2,
        "mid_vol": 1.0,
        "high_vol": 0.6,
        "uptrend": 1.2,
        "downtrend": 0.8,
        "cycle_rising": 1.3,
        "cycle_falling": 0.7
    })
    
    # Cycle intensity
    use_cycle_sizing: bool = True
    cycle_amplitude_multiplier: float = 1.0
    cycle_score_multiplier: float = 1.0
    
    # Kelly fraction
    use_kelly: bool = False
    kelly_fraction: float = 0.25  # 25% Kelly
    min_trades_for_kelly: int = 30  # Minimum trades needed
    
    # Hard risk limits
    max_position: float = 10.0
    max_daily_risk_pct: float = 0.02
    max_trade_risk_pct: float = 0.01
    min_position: float = 0.1
    
    # Smoothing
    smoothing_window: int = 3


