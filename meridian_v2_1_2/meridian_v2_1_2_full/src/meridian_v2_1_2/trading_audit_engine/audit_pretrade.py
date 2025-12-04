"""
Pre-Trade Auditor

Validates trading decisions before execution.
Entry signal validity, strategy alignment, sizing checks.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    """Status of a pre-trade check"""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass
class PreTradeCheck:
    """Result from a single pre-trade check"""
    check_name: str
    status: CheckStatus
    message: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    details: Dict[str, Any] = None


class PreTradeAuditor:
    """
    Pre-trade validation system.
    
    Checks trading decisions before execution against strategy rules
    and risk parameters.
    """
    
    def __init__(self, risk_limits: Optional[Dict[str, Any]] = None):
        """
        Initialize pre-trade auditor.
        
        Args:
            risk_limits: Dictionary with risk limits:
                - max_position_size: Maximum position size (default: 0.10)
                - max_risk_per_trade: Maximum risk per trade (default: 0.02)
                - min_reward_risk_ratio: Minimum R:R ratio (default: 2.0)
                - max_correlation: Maximum correlation (default: 0.7)
        """
        self.risk_limits = risk_limits or self._default_risk_limits()
    
    def audit_trade(
        self,
        trade_intent: Dict[str, Any],
        strategy_rules: Dict[str, Any],
        current_portfolio: Optional[Dict[str, Any]] = None
    ) -> List[PreTradeCheck]:
        """
        Audit a proposed trade.
        
        Args:
            trade_intent: Dict with:
                - symbol: Asset symbol
                - direction: 'long' or 'short'
                - size: Position size
                - entry_price: Proposed entry
                - stop_loss: Stop loss level (optional)
                - take_profit: Take profit level (optional)
                - signal_strength: Confidence in signal (0-1)
                - strategy_name: Which strategy generated this
            
            strategy_rules: Dict with strategy configuration
            
            current_portfolio: Current portfolio state (optional)
        
        Returns:
            List of PreTradeCheck results
        """
        checks = []
        
        # Check 1: Signal validity
        checks.append(self._check_signal_validity(trade_intent))
        
        # Check 2: Strategy alignment
        checks.append(self._check_strategy_alignment(trade_intent, strategy_rules))
        
        # Check 3: Position sizing
        checks.append(self._check_position_sizing(trade_intent))
        
        # Check 4: Risk parameters
        checks.append(self._check_risk_parameters(trade_intent))
        
        # Check 5: Volatility appropriateness
        checks.append(self._check_volatility(trade_intent))
        
        # Check 6: Reward/Risk ratio
        checks.append(self._check_reward_risk_ratio(trade_intent))
        
        return checks
    
    def _check_signal_validity(self, trade: Dict[str, Any]) -> PreTradeCheck:
        """Check if entry signal is valid"""
        signal_strength = trade.get('signal_strength', 0)
        
        if signal_strength < 0.3:
            return PreTradeCheck(
                check_name="Signal Validity",
                status=CheckStatus.FAIL,
                message=f"Signal strength too weak: {signal_strength:.2f} < 0.3 threshold",
                severity='high',
                details={'signal_strength': signal_strength}
            )
        elif signal_strength < 0.5:
            return PreTradeCheck(
                check_name="Signal Validity",
                status=CheckStatus.WARNING,
                message=f"Signal strength marginal: {signal_strength:.2f}",
                severity='medium',
                details={'signal_strength': signal_strength}
            )
        else:
            return PreTradeCheck(
                check_name="Signal Validity",
                status=CheckStatus.PASS,
                message=f"Signal strength adequate: {signal_strength:.2f}",
                severity='low',
                details={'signal_strength': signal_strength}
            )
    
    def _check_strategy_alignment(
        self,
        trade: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> PreTradeCheck:
        """Check if trade aligns with strategy rules"""
        
        strategy_name = trade.get('strategy_name', '')
        direction = trade.get('direction', '')
        
        # Check if strategy allows this direction
        allow_short = rules.get('allow_short', False)
        
        if direction == 'short' and not allow_short:
            return PreTradeCheck(
                check_name="Strategy Alignment",
                status=CheckStatus.FAIL,
                message="Strategy does not allow short positions",
                severity='critical'
            )
        
        return PreTradeCheck(
            check_name="Strategy Alignment",
            status=CheckStatus.PASS,
            message="Trade aligns with strategy rules",
            severity='low'
        )
    
    def _check_position_sizing(self, trade: Dict[str, Any]) -> PreTradeCheck:
        """Check if position size is appropriate"""
        
        size = trade.get('size', 0)
        max_size = self.risk_limits['max_position_size']
        
        if size > max_size:
            return PreTradeCheck(
                check_name="Position Sizing",
                status=CheckStatus.FAIL,
                message=f"Position size {size:.2%} exceeds limit {max_size:.2%}",
                severity='critical',
                details={'size': size, 'limit': max_size}
            )
        elif size > max_size * 0.8:
            return PreTradeCheck(
                check_name="Position Sizing",
                status=CheckStatus.WARNING,
                message=f"Position size {size:.2%} approaching limit",
                severity='medium'
            )
        else:
            return PreTradeCheck(
                check_name="Position Sizing",
                status=CheckStatus.PASS,
                message=f"Position size {size:.2%} within limits",
                severity='low'
            )
    
    def _check_risk_parameters(self, trade: Dict[str, Any]) -> PreTradeCheck:
        """Check if stop loss / risk parameters are set"""
        
        stop_loss = trade.get('stop_loss')
        entry_price = trade.get('entry_price', 0)
        
        if not stop_loss:
            return PreTradeCheck(
                check_name="Risk Parameters",
                status=CheckStatus.FAIL,
                message="No stop loss defined - unlimited risk exposure",
                severity='critical'
            )
        
        # Calculate risk amount
        if entry_price > 0:
            risk_pct = abs(entry_price - stop_loss) / entry_price
            max_risk = self.risk_limits['max_risk_per_trade']
            
            if risk_pct > max_risk:
                return PreTradeCheck(
                    check_name="Risk Parameters",
                    status=CheckStatus.FAIL,
                    message=f"Risk {risk_pct:.2%} exceeds limit {max_risk:.2%}",
                    severity='high',
                    details={'risk': risk_pct, 'limit': max_risk}
                )
        
        return PreTradeCheck(
            check_name="Risk Parameters",
            status=CheckStatus.PASS,
            message="Risk parameters acceptable",
            severity='low'
        )
    
    def _check_volatility(self, trade: Dict[str, Any]) -> PreTradeCheck:
        """Check if volatility is appropriate for trade"""
        
        volatility = trade.get('current_volatility', 0)
        
        # High volatility warning
        if volatility > 0.40:  # 40% annualized
            return PreTradeCheck(
                check_name="Volatility Check",
                status=CheckStatus.WARNING,
                message=f"High volatility ({volatility:.1%}) increases risk",
                severity='medium',
                details={'volatility': volatility}
            )
        
        return PreTradeCheck(
            check_name="Volatility Check",
            status=CheckStatus.PASS,
            message="Volatility within normal range",
            severity='low'
        )
    
    def _check_reward_risk_ratio(self, trade: Dict[str, Any]) -> PreTradeCheck:
        """Check reward/risk ratio"""
        
        entry = trade.get('entry_price', 0)
        stop_loss = trade.get('stop_loss', 0)
        take_profit = trade.get('take_profit', 0)
        
        if not (entry and stop_loss and take_profit):
            return PreTradeCheck(
                check_name="Reward/Risk Ratio",
                status=CheckStatus.WARNING,
                message="Cannot calculate R:R - missing parameters",
                severity='medium'
            )
        
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk == 0:
            return PreTradeCheck(
                check_name="Reward/Risk Ratio",
                status=CheckStatus.FAIL,
                message="Zero risk defined - invalid parameters",
                severity='high'
            )
        
        rr_ratio = reward / risk
        min_rr = self.risk_limits['min_reward_risk_ratio']
        
        if rr_ratio < min_rr:
            return PreTradeCheck(
                check_name="Reward/Risk Ratio",
                status=CheckStatus.FAIL,
                message=f"R:R ratio {rr_ratio:.1f}:1 below minimum {min_rr:.1f}:1",
                severity='high',
                details={'rr_ratio': rr_ratio, 'min_rr': min_rr}
            )
        
        return PreTradeCheck(
            check_name="Reward/Risk Ratio",
            status=CheckStatus.PASS,
            message=f"R:R ratio {rr_ratio:.1f}:1 acceptable",
            severity='low',
            details={'rr_ratio': rr_ratio}
        )
    
    def _default_risk_limits(self) -> Dict[str, float]:
        """Default risk limits"""
        return {
            'max_position_size': 0.10,  # 10% max
            'max_risk_per_trade': 0.02,  # 2% max risk
            'min_reward_risk_ratio': 2.0,  # 2:1 minimum
            'max_correlation': 0.7
        }


