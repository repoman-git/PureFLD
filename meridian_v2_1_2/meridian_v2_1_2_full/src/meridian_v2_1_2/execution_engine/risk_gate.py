"""Risk Gate - Pre-trade validation"""
import pandas as pd
from typing import Dict, Optional
from .broker_base import Order

class RiskGate:
    """Pre-trade risk validation"""
    
    def __init__(
        self,
        max_position_size: float = 0.25,
        max_portfolio_risk: float = 1.0,
        max_rws_threshold: float = 1.5,
        blocked_regimes: list = None
    ):
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.max_rws_threshold = max_rws_threshold
        self.blocked_regimes = blocked_regimes or [0, 4]  # TRENDING, RESETTING
    
    def validate_order(
        self,
        order: Order,
        account_value: float,
        vol_df: Optional[pd.DataFrame] = None,
        regime_state: Optional[Dict] = None,
        current_positions: Optional[Dict] = None
    ) -> tuple[bool, str]:
        """
        Validate order against risk rules.
        
        Returns:
            (allowed: bool, reason: str)
        """
        # Check position size
        order_value = order.qty * 100  # Simplified
        if order_value > account_value * self.max_position_size:
            return False, f"Position size exceeds {self.max_position_size:.0%} of account"
        
        # Check risk window score
        if vol_df is not None and 'risk_window_score' in vol_df.columns:
            if vol_df['risk_window_score'].iloc[-1] > self.max_rws_threshold:
                return False, f"Risk window score too high: {vol_df['risk_window_score'].iloc[-1]:.2f}"
        
        # Check regime
        if regime_state is not None and 'regime' in regime_state:
            current_regime = regime_state['regime'].iloc[-1] if isinstance(regime_state['regime'], pd.Series) else regime_state['regime']
            if current_regime in self.blocked_regimes:
                return False, f"Trading blocked in regime {current_regime}"
        
        return True, "Approved"
    
    def validate_portfolio(
        self,
        proposed_orders: list,
        current_positions: Dict,
        account_value: float
    ) -> tuple[bool, str]:
        """Validate entire portfolio risk"""
        # Calculate total exposure after orders
        total_exposure = sum(abs(pos.qty) for pos in current_positions.values())
        total_exposure += sum(order.qty for order in proposed_orders)
        
        # Check against max portfolio risk
        exposure_ratio = total_exposure / (account_value + 1)
        if exposure_ratio > self.max_portfolio_risk:
            return False, f"Portfolio risk {exposure_ratio:.1%} exceeds limit {self.max_portfolio_risk:.0%}"
        
        return True, "Approved"
