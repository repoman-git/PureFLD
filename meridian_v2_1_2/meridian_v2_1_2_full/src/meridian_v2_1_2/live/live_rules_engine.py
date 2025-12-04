"""
Live Rules Engine for Meridian v2.1.2

Pre-trade validation and rule enforcement.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import pandas as pd


@dataclass
class RuleViolation:
    """Represents a trading rule violation"""
    rule_name: str
    severity: str  # warning | error | critical
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    blocking: bool = True  # Whether this blocks the trade


class LiveRulesEngine:
    """
    Enforces trading rules and pre-trade validation.
    
    All rules must pass for a trade to be allowed.
    """
    
    def __init__(self, config):
        """
        Initialize rules engine.
        
        Args:
            config: LiveConfig instance
        """
        self.config = config
        self.violations = []
    
    def validate_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        price: float,
        account_info: Dict[str, Any],
        current_positions: Dict[str, Any]
    ) -> List[RuleViolation]:
        """
        Validate order against all rules.
        
        Args:
            symbol: Symbol to trade
            qty: Quantity
            side: 'buy' or 'sell'
            price: Estimated price
            account_info: Current account state
            current_positions: Current positions
        
        Returns:
            List of violations (empty if all pass)
        """
        violations = []
        
        # Rule 1: Live trading must be enabled
        if not self.config.enable_live_trading:
            violations.append(RuleViolation(
                rule_name='live_trading_disabled',
                severity='critical',
                message='Live trading is not enabled',
                blocking=True
            ))
            return violations  # Stop immediately
        
        # Rule 2: Forbidden symbols
        if symbol in self.config.forbidden_symbols:
            violations.append(RuleViolation(
                rule_name='forbidden_symbol',
                severity='critical',
                message=f'Symbol {symbol} is forbidden',
                blocking=True
            ))
        
        # Rule 3: Order size limit
        notional = abs(qty * price)
        if notional > self.config.max_single_order_notional:
            violations.append(RuleViolation(
                rule_name='order_size_exceeded',
                severity='error',
                message=f'Order notional ${notional:.2f} exceeds limit',
                value=notional,
                threshold=self.config.max_single_order_notional,
                blocking=True
            ))
        
        # Rule 4: Position size limit
        current_qty = current_positions.get(symbol, {}).get('qty', 0)
        new_qty = current_qty + qty if side == 'buy' else current_qty - qty
        new_notional = abs(new_qty * price)
        
        if new_notional > self.config.max_position_notional:
            violations.append(RuleViolation(
                rule_name='position_size_exceeded',
                severity='error',
                message=f'Position notional ${new_notional:.2f} exceeds limit',
                value=new_notional,
                threshold=self.config.max_position_notional,
                blocking=True
            ))
        
        # Rule 5: Total exposure limit
        total_exposure = sum(
            abs(pos.get('market_value', 0)) 
            for pos in current_positions.values()
        )
        total_exposure += notional
        
        if total_exposure > self.config.max_total_exposure:
            violations.append(RuleViolation(
                rule_name='total_exposure_exceeded',
                severity='error',
                message=f'Total exposure ${total_exposure:.2f} exceeds limit',
                value=total_exposure,
                threshold=self.config.max_total_exposure,
                blocking=True
            ))
        
        # Rule 6: Minimum account balance
        equity = account_info.get('equity', 0)
        if equity < self.config.min_account_balance:
            violations.append(RuleViolation(
                rule_name='insufficient_balance',
                severity='critical',
                message=f'Account balance ${equity:.2f} below minimum',
                value=equity,
                threshold=self.config.min_account_balance,
                blocking=True
            ))
        
        # Rule 7: Validate side
        if side not in ['buy', 'sell']:
            violations.append(RuleViolation(
                rule_name='invalid_side',
                severity='critical',
                message=f'Invalid side: {side}',
                blocking=True
            ))
        
        # Rule 8: NaN check
        if pd.isna(qty) or pd.isna(price):
            violations.append(RuleViolation(
                rule_name='nan_value',
                severity='critical',
                message='Order contains NaN values',
                blocking=True
            ))
        
        self.violations.extend(violations)
        return violations
    
    def has_blocking_violations(self, violations: List[RuleViolation] = None) -> bool:
        """Check if any violations are blocking"""
        check_list = violations if violations is not None else self.violations
        return any(v.blocking for v in check_list)
    
    def get_blocking_violations(self, violations: List[RuleViolation] = None) -> List[RuleViolation]:
        """Get only blocking violations"""
        check_list = violations if violations is not None else self.violations
        return [v for v in check_list if v.blocking]
    
    def clear_violations(self):
        """Clear violation history"""
        self.violations = []


