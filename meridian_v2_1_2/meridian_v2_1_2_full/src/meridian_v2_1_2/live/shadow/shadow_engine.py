"""
Shadow Engine for Meridian v2.1.2

Main broker position shadowing loop.
"""

import time
from typing import Dict, Any, List
from datetime import datetime

from .shadow_config import ShadowConfig
from .shadow_compare import ShadowCompare, DriftLevel
from .shadow_repair import ShadowRepair
from .shadow_events import ShadowEvent, ShadowEventType


class ShadowEngine:
    """
    Main broker position shadowing engine.
    
    Continuously monitors and syncs local state with broker.
    """
    
    def __init__(
        self,
        config: ShadowConfig,
        alpaca_adapter,
        state_store=None
    ):
        """
        Initialize shadow engine.
        
        Args:
            config: ShadowConfig instance
            alpaca_adapter: AlpacaAdapter for broker queries
            state_store: StateStore for local state
        """
        self.config = config
        self.alpaca = alpaca_adapter
        self.state_store = state_store
        
        self.compare = ShadowCompare(config)
        self.repair = ShadowRepair(config, state_store)
        
        self.events = []
        self.last_check = None
        self.running = False
    
    def check_shadow(
        self,
        local_positions: Dict[str, Dict[str, float]],
        local_cash: float = 0.0,
        local_pnl: float = 0.0
    ) -> Dict[str, Any]:
        """
        Perform shadow check.
        
        Args:
            local_positions: Local positions
            local_cash: Local cash
            local_pnl: Local PnL
        
        Returns:
            Dict with check results
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'drift_detected': False,
            'drift_level': 'none',
            'repairs_applied': [],
            'events': []
        }
        
        try:
            # Fetch broker state
            broker_positions = self._fetch_broker_positions()
            broker_account = self.alpaca.get_account()
            broker_cash = broker_account.get('cash', 0)
            broker_equity = broker_account.get('equity', 0)
            
            # Compare
            drift_result = self.compare.compare(
                local_positions=local_positions,
                broker_positions=broker_positions,
                local_cash=local_cash,
                broker_cash=broker_cash,
                local_pnl=local_pnl,
                broker_pnl=0.0  # Stub
            )
            
            result['drift_level'] = drift_result.drift_level.value
            result['drift_detected'] = drift_result.drift_level != DriftLevel.NONE
            
            # Create events
            if drift_result.drift_level != DriftLevel.NONE:
                event = ShadowEvent(
                    event_type=ShadowEventType.POSITION_DRIFT,
                    timestamp=datetime.now(),
                    message=f"Drift detected: {drift_result.drift_level.value}",
                    severity='error' if drift_result.drift_level == DriftLevel.CRITICAL else 'warning',
                    details={'drift_result': drift_result.details}
                )
                self.events.append(event)
                result['events'].append(event.to_dict())
            
            # Apply repairs if needed
            if self.config.auto_repair and drift_result.drift_level in [DriftLevel.SMALL, DriftLevel.LARGE]:
                repairs = self.repair.repair(
                    drift_result,
                    local_positions,
                    broker_positions
                )
                result['repairs_applied'] = [
                    {'type': r.action_type, 'symbol': r.symbol, 'details': r.details}
                    for r in repairs
                ]
                
                if repairs:
                    event = ShadowEvent(
                        event_type=ShadowEventType.REPAIR_APPLIED,
                        timestamp=datetime.now(),
                        message=f"Applied {len(repairs)} repair(s)",
                        severity='info',
                        details={'repairs': result['repairs_applied']}
                    )
                    self.events.append(event)
                    result['events'].append(event.to_dict())
            
            # Critical drift warning
            if drift_result.drift_level == DriftLevel.CRITICAL:
                event = ShadowEvent(
                    event_type=ShadowEventType.CRITICAL_DRIFT,
                    timestamp=datetime.now(),
                    message="CRITICAL DRIFT DETECTED - Trading should be halted",
                    severity='critical',
                    details={'drift_result': drift_result.details}
                )
                self.events.append(event)
                result['events'].append(event.to_dict())
            
            # Success event
            if drift_result.drift_level == DriftLevel.NONE:
                event = ShadowEvent(
                    event_type=ShadowEventType.SHADOW_CHECK_OK,
                    timestamp=datetime.now(),
                    message="Shadow check passed - no drift",
                    severity='info'
                )
                self.events.append(event)
                result['events'].append(event.to_dict())
            
            self.last_check = datetime.now()
            result['success'] = True
            
        except Exception as e:
            event = ShadowEvent(
                event_type=ShadowEventType.SHADOW_CHECK_FAILED,
                timestamp=datetime.now(),
                message=f"Shadow check failed: {e}",
                severity='error',
                details={'error': str(e)}
            )
            self.events.append(event)
            result['events'].append(event.to_dict())
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def _fetch_broker_positions(self) -> Dict[str, Dict[str, float]]:
        """Fetch positions from broker"""
        try:
            positions_list = self.alpaca.get_positions()
            
            positions = {}
            for pos in positions_list:
                symbol = pos.get('symbol')
                if symbol:
                    positions[symbol] = {
                        'qty': float(pos.get('qty', 0)),
                        'cost_basis': float(pos.get('cost_basis', 0)),
                        'market_value': float(pos.get('market_value', 0))
                    }
            
            return positions
            
        except Exception:
            return {}
    
    def get_events(self, severity: str = None) -> List[ShadowEvent]:
        """Get shadow events, optionally filtered by severity"""
        if severity:
            return [e for e in self.events if e.severity == severity]
        return self.events
    
    def clear_events(self):
        """Clear event history"""
        self.events = []

