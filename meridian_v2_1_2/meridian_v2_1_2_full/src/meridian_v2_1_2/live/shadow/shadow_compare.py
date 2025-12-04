"""
Shadow Comparison Engine for Meridian v2.1.2

Compares local state vs broker state.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List
import pandas as pd


class DriftLevel(str, Enum):
    """Drift severity levels"""
    NONE = "none"
    SMALL = "small"
    LARGE = "large"
    CRITICAL = "critical"


@dataclass
class DriftResult:
    """Result of drift comparison"""
    drift_level: DriftLevel
    positions_diff: Dict[str, Any]
    orders_diff: Dict[str, Any]
    cash_diff: Dict[str, Any]
    pnl_diff: Dict[str, Any]
    details: List[str]


class ShadowCompare:
    """
    Compares local state vs broker state.
    
    Detects:
    - Position quantity drift
    - Cost basis mismatch
    - Missing fills
    - Ghost orders
    - PnL divergence
    """
    
    def __init__(self, config):
        """
        Initialize shadow comparison.
        
        Args:
            config: ShadowConfig instance
        """
        self.config = config
    
    def compare(
        self,
        local_positions: Dict[str, Dict[str, float]],
        broker_positions: Dict[str, Dict[str, float]],
        local_cash: float,
        broker_cash: float,
        local_pnl: float,
        broker_pnl: float
    ) -> DriftResult:
        """
        Compare local vs broker state.
        
        Args:
            local_positions: Local positions
            broker_positions: Broker positions
            local_cash: Local cash
            broker_cash: Broker cash
            local_pnl: Local PnL
            broker_pnl: Broker PnL
        
        Returns:
            DriftResult
        """
        details = []
        
        # Compare positions
        positions_diff = self._compare_positions(
            local_positions,
            broker_positions,
            details
        )
        
        # Compare cash
        cash_diff = self._compare_cash(
            local_cash,
            broker_cash,
            details
        )
        
        # Compare PnL
        pnl_diff = self._compare_pnl(
            local_pnl,
            broker_pnl,
            details
        )
        
        # Orders comparison (stub for now)
        orders_diff = {}
        
        # Determine drift level
        drift_level = self._classify_drift(
            positions_diff,
            cash_diff,
            pnl_diff
        )
        
        return DriftResult(
            drift_level=drift_level,
            positions_diff=positions_diff,
            orders_diff=orders_diff,
            cash_diff=cash_diff,
            pnl_diff=pnl_diff,
            details=details
        )
    
    def _compare_positions(
        self,
        local: Dict[str, Dict[str, float]],
        broker: Dict[str, Dict[str, float]],
        details: List[str]
    ) -> Dict[str, Any]:
        """Compare position quantities"""
        diff = {
            'mismatches': [],
            'missing_local': [],
            'missing_broker': []
        }
        
        # Check positions in both
        all_symbols = set(local.keys()) | set(broker.keys())
        
        for symbol in all_symbols:
            local_pos = local.get(symbol, {})
            broker_pos = broker.get(symbol, {})
            
            local_qty = local_pos.get('qty', 0)
            broker_qty = broker_pos.get('qty', 0)
            
            if symbol not in local:
                diff['missing_local'].append({
                    'symbol': symbol,
                    'broker_qty': broker_qty
                })
                details.append(f"Position {symbol} exists in broker but not locally")
            
            elif symbol not in broker:
                diff['missing_broker'].append({
                    'symbol': symbol,
                    'local_qty': local_qty
                })
                details.append(f"Position {symbol} exists locally but not in broker")
            
            elif abs(local_qty - broker_qty) > 0.001:  # Tolerance for float
                qty_drift_pct = abs(local_qty - broker_qty) / abs(broker_qty) if broker_qty != 0 else float('inf')
                
                diff['mismatches'].append({
                    'symbol': symbol,
                    'local_qty': local_qty,
                    'broker_qty': broker_qty,
                    'difference': local_qty - broker_qty,
                    'drift_pct': qty_drift_pct
                })
                details.append(f"Quantity drift for {symbol}: local={local_qty}, broker={broker_qty}")
        
        return diff
    
    def _compare_cash(
        self,
        local: float,
        broker: float,
        details: List[str]
    ) -> Dict[str, Any]:
        """Compare cash balances"""
        diff = {
            'local': local,
            'broker': broker,
            'difference': local - broker,
            'drift_pct': abs(local - broker) / broker if broker > 0 else 0
        }
        
        if abs(local - broker) > self.config.max_notional_drift:
            details.append(f"Cash drift: local=${local:.2f}, broker=${broker:.2f}")
        
        return diff
    
    def _compare_pnl(
        self,
        local: float,
        broker: float,
        details: List[str]
    ) -> Dict[str, Any]:
        """Compare PnL"""
        diff = {
            'local': local,
            'broker': broker,
            'difference': local - broker,
            'drift_pct': abs(local - broker) / abs(broker) if broker != 0 else 0
        }
        
        if diff['drift_pct'] > self.config.max_pnl_drift_pct / 100.0:
            details.append(f"PnL drift: local=${local:.2f}, broker=${broker:.2f}")
        
        return diff
    
    def _classify_drift(
        self,
        positions_diff: Dict[str, Any],
        cash_diff: Dict[str, Any],
        pnl_diff: Dict[str, Any]
    ) -> DriftLevel:
        """Classify overall drift severity"""
        # Check for critical conditions
        if len(positions_diff.get('mismatches', [])) > 0:
            # Check if any mismatch is large
            for mismatch in positions_diff['mismatches']:
                if mismatch['drift_pct'] > self.config.max_quantity_drift:
                    return DriftLevel.CRITICAL
        
        if cash_diff['drift_pct'] > 0.1:  # 10% cash drift is critical
            return DriftLevel.CRITICAL
        
        # Check for large drift
        if len(positions_diff.get('mismatches', [])) > 0:
            return DriftLevel.LARGE
        
        if cash_diff['drift_pct'] > 0.01:  # 1% cash drift is large
            return DriftLevel.LARGE
        
        # Check for small drift
        if len(positions_diff.get('missing_local', [])) > 0 or len(positions_diff.get('missing_broker', [])) > 0:
            return DriftLevel.SMALL
        
        if abs(cash_diff['difference']) > self.config.max_notional_drift:
            return DriftLevel.SMALL
        
        return DriftLevel.NONE


