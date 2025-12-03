"""
Risk Limit Checker

Hard and soft risk limit enforcement for trading decisions.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ViolationSeverity(Enum):
    """Risk violation severity levels"""
    CRITICAL = "CRITICAL"  # Trade must be blocked
    HIGH = "HIGH"          # Strong warning
    MEDIUM = "MEDIUM"      # Caution advised
    LOW = "LOW"            # Informational


@dataclass
class RiskViolation:
    """Risk limit violation"""
    rule_name: str
    violated: bool
    severity: ViolationSeverity
    message: str
    current_value: Any
    limit_value: Any
    action: str  # 'BLOCK', 'WARN', 'PROCEED'


class RiskLimitChecker:
    """
    Enforces hard and soft risk limits on trading decisions.
    
    Professional trading desk-style risk gating.
    """
    
    def __init__(self, risk_config: Optional[Dict[str, Any]] = None):
        """
        Initialize risk limit checker.
        
        Args:
            risk_config: Risk configuration dictionary
        """
        self.config = risk_config or self._default_config()
    
    def check_all_limits(
        self,
        trade: Dict[str, Any],
        portfolio: Optional[Dict[str, Any]] = None
    ) -> List[RiskViolation]:
        """
        Check all risk limits for a trade.
        
        Args:
            trade: Trade intent dictionary
            portfolio: Current portfolio state
        
        Returns:
            List of risk violations (empty if all pass)
        """
        violations = []
        
        # Hard limits (critical - must block)
        violations.extend(self._check_hard_limits(trade, portfolio))
        
        # Soft limits (warnings)
        violations.extend(self._check_soft_limits(trade, portfolio))
        
        return violations
    
    def _check_hard_limits(
        self,
        trade: Dict[str, Any],
        portfolio: Optional[Dict[str, Any]]
    ) -> List[RiskViolation]:
        """Check hard limits that must block trades"""
        violations = []
        
        # Maximum position size
        size = trade.get('size', 0)
        max_size = self.config['hard_limits']['max_position_size']
        
        if size > max_size:
            violations.append(RiskViolation(
                rule_name="Maximum Position Size",
                violated=True,
                severity=ViolationSeverity.CRITICAL,
                message=f"Position size {size:.2%} exceeds hard limit {max_size:.2%}",
                current_value=size,
                limit_value=max_size,
                action='BLOCK'
            ))
        
        # Maximum risk per trade
        entry = trade.get('entry_price', 0)
        stop = trade.get('stop_loss', 0)
        
        if entry and stop:
            risk_pct = abs(entry - stop) / entry * size
            max_risk = self.config['hard_limits']['max_risk_per_trade']
            
            if risk_pct > max_risk:
                violations.append(RiskViolation(
                    rule_name="Maximum Risk Per Trade",
                    violated=True,
                    severity=ViolationSeverity.CRITICAL,
                    message=f"Trade risk {risk_pct:.2%} exceeds limit {max_risk:.2%}",
                    current_value=risk_pct,
                    limit_value=max_risk,
                    action='BLOCK'
                ))
        
        # No stop loss = auto block
        if not stop:
            violations.append(RiskViolation(
                rule_name="Stop Loss Required",
                violated=True,
                severity=ViolationSeverity.CRITICAL,
                message="No stop loss defined - unlimited risk not allowed",
                current_value=None,
                limit_value='required',
                action='BLOCK'
            ))
        
        return violations
    
    def _check_soft_limits(
        self,
        trade: Dict[str, Any],
        portfolio: Optional[Dict[str, Any]]
    ) -> List[RiskViolation]:
        """Check soft limits that generate warnings"""
        violations = []
        
        # Signal strength warning
        signal = trade.get('signal_strength', 0)
        if signal < 0.6:
            violations.append(RiskViolation(
                rule_name="Signal Strength",
                violated=True,
                severity=ViolationSeverity.MEDIUM,
                message=f"Signal strength {signal:.2f} below recommended 0.6",
                current_value=signal,
                limit_value=0.6,
                action='WARN'
            ))
        
        # Reward/risk ratio warning
        entry = trade.get('entry_price', 0)
        stop = trade.get('stop_loss', 0)
        target = trade.get('take_profit', 0)
        
        if entry and stop and target:
            risk = abs(entry - stop)
            reward = abs(target - entry)
            
            if risk > 0:
                rr_ratio = reward / risk
                min_rr = self.config['soft_limits']['min_reward_risk']
                
                if rr_ratio < min_rr:
                    violations.append(RiskViolation(
                        rule_name="Reward/Risk Ratio",
                        violated=True,
                        severity=ViolationSeverity.MEDIUM,
                        message=f"R:R {rr_ratio:.1f}:1 below recommended {min_rr:.1f}:1",
                        current_value=rr_ratio,
                        limit_value=min_rr,
                        action='WARN'
                    ))
        
        return violations
    
    def _default_config(self) -> Dict[str, Any]:
        """Default risk configuration"""
        return {
            'hard_limits': {
                'max_position_size': 0.10,     # 10% max
                'max_risk_per_trade': 0.02,    # 2% max risk
                'max_portfolio_risk': 0.06,    # 6% total risk
                'max_leverage': 1.0,           # No leverage
                'require_stop_loss': True
            },
            'soft_limits': {
                'recommended_position_size': 0.05,  # 5% recommended
                'min_signal_strength': 0.6,
                'min_reward_risk': 2.0,
                'max_correlated_exposure': 0.30
            }
        }
    
    def get_trade_verdict(self, violations: List[RiskViolation]) -> str:
        """
        Get final verdict based on violations.
        
        Returns:
            'APPROVED', 'BLOCKED', or 'WARNING'
        """
        # Any critical violation = BLOCKED
        if any(v.severity == ViolationSeverity.CRITICAL for v in violations):
            return 'BLOCKED'
        
        # High severity violations = WARNING
        if any(v.severity == ViolationSeverity.HIGH for v in violations):
            return 'WARNING'
        
        # Only medium/low = APPROVED with caution
        if any(v.severity in [ViolationSeverity.MEDIUM, ViolationSeverity.HIGH] for v in violations):
            return 'WARNING'
        
        return 'APPROVED'

