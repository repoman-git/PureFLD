"""
Live Orchestrator for Meridian v2.1.2

Complete live trading workflow coordination.
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

from ..config import MeridianConfig
from ..external import AlpacaAdapter, ExternalConfig
from ..storage import StateStore, LocalDB, RunRegistry
from .live_config import LiveConfig
from .live_rules_engine import LiveRulesEngine
from .live_heartbeat import LiveHeartbeat
from .live_execution import LiveExecution
from .live_reconciliation import LiveReconciliation
from .live_safety import LiveSafety
from .live_reports import generate_live_report


class LiveOrchestrator:
    """
    Complete live trading orchestrator.
    
    Coordinates:
    - Real-time data loading
    - Signal generation
    - Rules validation
    - Model risk checks
    - Order execution
    - Reconciliation
    - Safety monitoring
    - Heartbeat checks
    """
    
    def __init__(self, config: MeridianConfig):
        """
        Initialize live orchestrator.
        
        Args:
            config: Meridian configuration
        """
        self.config = config
        self.live_config = config.get_live_config()
        
        # Initialize components
        ext_config = config.get_external_config()
        ext_config.use_alpaca = True  # Enable Alpaca for live mode
        
        self.alpaca = AlpacaAdapter(ext_config)
        self.db = LocalDB()
        self.state_store = StateStore(self.db)
        self.run_registry = RunRegistry()
        
        # Live components
        self.rules_engine = LiveRulesEngine(self.live_config)
        self.heartbeat = LiveHeartbeat(self.live_config, self.alpaca)
        self.execution = LiveExecution(self.live_config, self.alpaca, self.state_store)
        self.reconciliation = LiveReconciliation(self.live_config, self.alpaca, self.state_store)
        self.safety = LiveSafety(self.live_config)
        
        # State
        self.portfolio_state = {}
    
    def run_live_day(self, date: pd.Timestamp) -> Dict[str, Any]:
        """
        Run complete live trading cycle for one day.
        
        Args:
            date: Trading date
        
        Returns:
            Dict with results
        """
        date_str = date.strftime('%Y-%m-%d')
        
        results = {
            'date': date_str,
            'live_mode': True,
            'success': False,
            'trades_executed': [],
            'violations': [],
            'heartbeat_ok': False,
            'reconciliation_ok': False,
            'safety_triggers': []
        }
        
        try:
            # 1. Check heartbeat
            heartbeat_status = self.heartbeat.check()
            results['heartbeat_ok'] = heartbeat_status.is_alive
            
            if not heartbeat_status.is_alive:
                results['error'] = 'Heartbeat check failed'
                return results
            
            # 2. Check kill-switch
            if self.safety.is_kill_switch_active():
                results['error'] = 'Kill-switch is active'
                return results
            
            # 3. Load market data
            data = self._load_market_data(date)
            
            # 4. Generate signals (stub - would integrate full strategy engine)
            signals = self._generate_signals(data)
            
            # 5. Get account info
            account_info = self.alpaca.get_account()
            current_equity = account_info.get('equity', 0)
            
            # 6. Validate each signal with rules engine
            for symbol, signal_qty in signals.items():
                if abs(signal_qty) < 0.01:
                    continue  # Skip near-zero signals
                
                side = 'buy' if signal_qty > 0 else 'sell'
                price = 100.0  # Stub price
                
                # Validate order
                violations = self.rules_engine.validate_order(
                    symbol=symbol,
                    qty=abs(signal_qty),
                    side=side,
                    price=price,
                    account_info=account_info,
                    current_positions=self.portfolio_state
                )
                
                if violations:
                    results['violations'].extend([vars(v) for v in violations])
                
                # Check if blocking
                if self.rules_engine.has_blocking_violations(violations):
                    continue  # Skip this order
                
                # 7. Execute order
                exec_result = self.execution.execute_order(
                    symbol=symbol,
                    qty=abs(signal_qty),
                    side=side
                )
                
                results['trades_executed'].append({
                    'symbol': symbol,
                    'qty': signal_qty,
                    'side': side,
                    'result': exec_result
                })
                
                # 8. Update portfolio state
                if exec_result['success'] and exec_result['filled']:
                    self._update_portfolio_state(symbol, signal_qty, price)
            
            # 9. Reconcile positions
            recon_result = self.reconciliation.reconcile(self.portfolio_state)
            results['reconciliation_ok'] = recon_result.success
            
            if recon_result.drift_detected:
                results['drift_pct'] = recon_result.drift_pct
            
            # 10. Run safety checks
            daily_pnl = 0.0  # Stub
            safety_triggers = self.safety.check_all(
                current_equity=current_equity,
                daily_pnl=daily_pnl,
                positions=self.portfolio_state
            )
            
            results['safety_triggers'] = [vars(t) for t in safety_triggers]
            
            # 11. Generate report
            if self.live_config.write_live_reports:
                generate_live_report(date_str, results, self.live_config)
            
            # 12. Log run
            self.run_registry.log_run(
                run_type='live',
                config={'date': date_str},
                performance={'equity': current_equity}
            )
            
            results['success'] = True
            
        except Exception as e:
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def _load_market_data(self, date: pd.Timestamp) -> Dict[str, Any]:
        """Load market data from Alpaca"""
        # In real implementation, would fetch from Alpaca
        # For now, return stub
        return {'prices': {}}
    
    def _generate_signals(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Generate trading signals"""
        # Stub - would integrate full strategy engine
        return {}
    
    def _update_portfolio_state(self, symbol: str, qty: float, price: float):
        """Update internal portfolio state"""
        current_qty = self.portfolio_state.get(symbol, {}).get('qty', 0)
        new_qty = current_qty + qty
        
        self.portfolio_state[symbol] = {
            'qty': new_qty,
            'cost_basis': price * abs(new_qty),
            'market_value': price * abs(new_qty)
        }
    
    def close(self):
        """Cleanup resources"""
        self.db.close()


def run_live_day(config: MeridianConfig, date: str) -> Dict[str, Any]:
    """
    Convenience function to run single live day.
    
    Args:
        config: Configuration
        date: Date string
    
    Returns:
        Results dict
    """
    orchestrator = LiveOrchestrator(config)
    date_ts = pd.Timestamp(date)
    results = orchestrator.run_live_day(date_ts)
    orchestrator.close()
    
    return results


