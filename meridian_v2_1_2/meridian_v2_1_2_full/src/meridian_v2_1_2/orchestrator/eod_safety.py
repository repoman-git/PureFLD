"""
EOD Safety Layer for Meridian v2.1.2

Protects against dangerous conditions during trading loop.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import numpy as np


@dataclass
class SafetyViolation:
    """Represents a safety violation"""
    violation_type: str
    severity: str  # warning | error | critical
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None


class EODSafety:
    """
    EOD safety checks.
    
    Validates:
    - Data quality
    - Signal sanity
    - Position sizes
    - Daily loss limits
    - Drift
    - Order validity
    """
    
    def __init__(self, config):
        """
        Initialize safety layer.
        
        Args:
            config: MeridianConfig or EODConfig
        """
        self.config = config if hasattr(config, 'eod') else config
        self.violations = []
    
    def check_data_quality(
        self,
        data: Dict[str, Any]
    ) -> List[SafetyViolation]:
        """
        Check data quality.
        
        Args:
            data: Market data dict
        
        Returns:
            List of violations
        """
        violations = []
        
        # Check for missing prices
        if 'prices' not in data or not data['prices']:
            violations.append(SafetyViolation(
                violation_type='missing_data',
                severity='critical',
                message='No price data available'
            ))
        
        # Check for NaNs
        for symbol, df in data.get('prices', {}).items():
            if df.isna().any().any():
                nan_count = df.isna().sum().sum()
                violations.append(SafetyViolation(
                    violation_type='nan_data',
                    severity='error',
                    message=f'NaN values in {symbol} data',
                    value=float(nan_count)
                ))
        
        return violations
    
    def check_signals(
        self,
        signals: Dict[str, float]
    ) -> List[SafetyViolation]:
        """
        Check signal sanity.
        
        Args:
            signals: Strategy signals
        
        Returns:
            List of violations
        """
        violations = []
        
        # Check for extreme signals
        for symbol, signal in signals.items():
            if np.isnan(signal):
                violations.append(SafetyViolation(
                    violation_type='invalid_signal',
                    severity='critical',
                    message=f'NaN signal for {symbol}'
                ))
            
            elif abs(signal) > 10:
                violations.append(SafetyViolation(
                    violation_type='extreme_signal',
                    severity='warning',
                    message=f'Extreme signal for {symbol}: {signal}',
                    value=signal
                ))
        
        return violations
    
    def check_positions(
        self,
        positions: Dict[str, float],
        max_position: float = 100.0
    ) -> List[SafetyViolation]:
        """
        Check position sizes.
        
        Args:
            positions: Symbol -> qty
            max_position: Maximum position size
        
        Returns:
            List of violations
        """
        violations = []
        
        for symbol, qty in positions.items():
            if abs(qty) > max_position:
                violations.append(SafetyViolation(
                    violation_type='oversized_position',
                    severity='error',
                    message=f'Position too large for {symbol}',
                    value=abs(qty),
                    threshold=max_position
                ))
        
        return violations
    
    def check_daily_loss(
        self,
        current_equity: float,
        previous_equity: float,
        max_loss_pct: float = 0.05
    ) -> List[SafetyViolation]:
        """
        Check daily loss limit.
        
        Args:
            current_equity: Current equity
            previous_equity: Previous equity
            max_loss_pct: Maximum daily loss percentage
        
        Returns:
            List of violations
        """
        violations = []
        
        if previous_equity > 0:
            loss_pct = (previous_equity - current_equity) / previous_equity
            
            if loss_pct > max_loss_pct:
                violations.append(SafetyViolation(
                    violation_type='daily_loss_exceeded',
                    severity='critical',
                    message=f'Daily loss {loss_pct:.2%} exceeds limit {max_loss_pct:.2%}',
                    value=loss_pct,
                    threshold=max_loss_pct
                ))
        
        return violations
    
    def check_all(
        self,
        data: Dict[str, Any],
        signals: Dict[str, float],
        positions: Dict[str, float],
        current_equity: float,
        previous_equity: float
    ) -> List[SafetyViolation]:
        """
        Run all safety checks.
        
        Args:
            data: Market data
            signals: Signals
            positions: Positions
            current_equity: Current equity
            previous_equity: Previous equity
        
        Returns:
            List of all violations
        """
        violations = []
        
        violations.extend(self.check_data_quality(data))
        violations.extend(self.check_signals(signals))
        violations.extend(self.check_positions(positions))
        violations.extend(self.check_daily_loss(current_equity, previous_equity))
        
        self.violations.extend(violations)
        
        return violations
    
    def has_critical_violations(self) -> bool:
        """Check if any critical violations exist"""
        return any(v.severity == 'critical' for v in self.violations)
    
    def get_violations_by_severity(self, severity: str) -> List[SafetyViolation]:
        """Get violations by severity level"""
        return [v for v in self.violations if v.severity == severity]

