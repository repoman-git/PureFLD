"""
EOD Orchestrator Core for Meridian v2.1.2

Complete daily trading loop coordination.
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

from ..config import MeridianConfig
from ..synthetic.synthetic_dataset import SyntheticDataset
from ..storage import StateStore, RunRegistry, LocalDB
from .eod_states import EODState, EODStateMachine
from .eod_scheduler import EODScheduler
from .eod_safety import EODSafety
from .eod_reporter import generate_eod_report


class EODOrchestrator:
    """
    Complete EOD trading loop orchestrator.
    
    Coordinates:
    - Data loading
    - Signal generation
    - Model risk
    - Order execution
    - Portfolio management
    - PnL calculation
    - State persistence
    """
    
    def __init__(self, config: MeridianConfig):
        """
        Initialize orchestrator.
        
        Args:
            config: Meridian configuration
        """
        self.config = config
        
        # Initialize components
        self.state_machine = EODStateMachine()
        self.scheduler = EODScheduler(
            start_date=config.eod.start_date,
            end_date=config.eod.end_date,
            simulate_clock=config.eod.simulate_clock
        )
        self.safety = EODSafety(config)
        
        # Storage
        self.db = LocalDB()
        self.state_store = StateStore(self.db)
        self.run_registry = RunRegistry()
        
        # State tracking
        self.current_date = None
        self.portfolio_state = {}
        self.equity_history = []
        self.signals_history = []
    
    def run_eod_day(self, date: pd.Timestamp) -> Dict[str, Any]:
        """
        Run complete EOD cycle for one day.
        
        Args:
            date: Trading date
        
        Returns:
            Dict with results
        """
        self.current_date = date
        date_str = date.strftime('%Y-%m-%d')
        
        results = {
            'date': date_str,
            'success': False,
            'state_sequence': [],
            'violations': [],
            'signals': {},
            'positions': {},
            'pnl': 0.0,
            'equity': 0.0
        }
        
        try:
            # INIT
            self.state_machine.transition(EODState.INIT)
            
            # LOAD DATA
            self.state_machine.transition(EODState.LOAD_DATA)
            data = self._load_data(date)
            
            # Data safety check
            violations = self.safety.check_data_quality(data)
            if any(v.severity == 'critical' for v in violations):
                self.state_machine.transition(EODState.SAFE_MODE, 'Critical data violations')
                results['violations'] = [vars(v) for v in violations]
                return results
            
            # GENERATE SIGNALS
            self.state_machine.transition(EODState.GENERATE_SIGNALS)
            signals = self._generate_signals(data)
            results['signals'] = signals
            
            # Signal safety check
            violations = self.safety.check_signals(signals)
            if any(v.severity == 'critical' for v in violations):
                self.state_machine.transition(EODState.SAFE_MODE, 'Critical signal violations')
                results['violations'] = [vars(v) for v in violations]
                return results
            
            # MODEL RISK (optional)
            if self.config.eod.run_model_risk:
                self.state_machine.transition(EODState.RUN_MODEL_RISK)
                model_risk_score = self._run_model_risk(data, signals)
                results['model_risk_score'] = model_risk_score
            
            # EXECUTE ORDERS
            self.state_machine.transition(EODState.EXECUTE_ORDERS)
            fills = self._execute_orders(signals, data)
            
            # UPDATE PORTFOLIO
            self.state_machine.transition(EODState.UPDATE_PORTFOLIO)
            self._update_portfolio(fills)
            results['positions'] = self.portfolio_state.copy()
            
            # CALCULATE PNL
            self.state_machine.transition(EODState.CALCULATE_PNL)
            pnl, equity = self._calculate_pnl(data)
            results['pnl'] = pnl
            results['equity'] = equity
            
            # WRITE LOGS
            self.state_machine.transition(EODState.WRITE_LOGS)
            self._write_logs(date_str, results)
            
            # END
            self.state_machine.transition(EODState.END)
            results['success'] = True
            results['state_sequence'] = self.state_machine.get_state_sequence()
            
        except Exception as e:
            self.state_machine.transition(EODState.SAFE_MODE, str(e))
            results['error'] = str(e)
            results['state_sequence'] = self.state_machine.get_state_sequence()
        
        return results
    
    def run_period(self, num_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Run EOD loop for multiple days.
        
        Args:
            num_days: Number of days to run (None for all)
        
        Returns:
            Dict with aggregated results
        """
        results_list = []
        day_count = 0
        
        while self.scheduler.has_more_days():
            if num_days and day_count >= num_days:
                break
            
            date = self.scheduler.next_trading_day()
            if date is None:
                break
            
            day_results = self.run_eod_day(date)
            results_list.append(day_results)
            day_count += 1
        
        # Aggregate results
        return {
            'total_days': len(results_list),
            'successful_days': sum(1 for r in results_list if r['success']),
            'total_equity': results_list[-1]['equity'] if results_list else 0,
            'daily_results': results_list
        }
    
    def _load_data(self, date: pd.Timestamp) -> Dict[str, Any]:
        """Load market data for date"""
        # Generate synthetic data
        synth = SyntheticDataset(self.config.synthetic)
        dataset = synth.generate()
        
        # Filter to current date
        data = {
            'prices': {},
            'date': date
        }
        
        # Extract price slice
        for symbol, df in dataset['prices'].items():
            if date in df.index:
                data['prices'][symbol] = df.loc[:date].tail(100)  # Last 100 bars
        
        return data
    
    def _generate_signals(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Generate trading signals"""
        signals = {}
        
        # Simple signal generation (stub for now)
        for symbol in data.get('prices', {}).keys():
            # Generate random signal for demonstration
            signals[symbol] = 0.0  # Flat for safety
        
        return signals
    
    def _run_model_risk(
        self,
        data: Dict[str, Any],
        signals: Dict[str, float]
    ) -> float:
        """Run model risk analysis"""
        # Stub - would integrate Phase 27 model risk engine
        return 0.2  # Low risk score
    
    def _execute_orders(
        self,
        signals: Dict[str, float],
        data: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """Execute orders based on signals"""
        fills = {}
        
        for symbol, signal in signals.items():
            if abs(signal) > 0.01:  # Threshold
                fills[symbol] = {
                    'qty': signal,
                    'price': 100.0,  # Stub price
                    'filled': True
                }
        
        return fills
    
    def _update_portfolio(self, fills: Dict[str, Dict[str, float]]):
        """Update portfolio state with fills"""
        for symbol, fill in fills.items():
            if fill['filled']:
                current_qty = self.portfolio_state.get(symbol, {}).get('qty', 0)
                new_qty = current_qty + fill['qty']
                
                self.portfolio_state[symbol] = {
                    'qty': new_qty,
                    'cost_basis': fill['price'] * abs(new_qty),
                    'market_value': fill['price'] * abs(new_qty)
                }
    
    def _calculate_pnl(self, data: Dict[str, Any]) -> tuple:
        """Calculate daily PnL and equity"""
        total_value = 0.0
        
        for symbol, position in self.portfolio_state.items():
            # Use latest price
            if symbol in data['prices']:
                latest_price = data['prices'][symbol]['close'].iloc[-1]
                market_value = position['qty'] * latest_price
                total_value += market_value
        
        # Calculate PnL
        prev_equity = self.equity_history[-1] if self.equity_history else 100000.0
        pnl = total_value - prev_equity
        
        self.equity_history.append(total_value)
        
        return pnl, total_value
    
    def _write_logs(self, date_str: str, results: Dict[str, Any]):
        """Write logs and state"""
        # Save portfolio state
        self.state_store.save_portfolio_state(date_str, self.portfolio_state)
        
        # Save to run registry
        self.run_registry.log_run(
            run_type=self.config.eod.mode,
            config={'date': date_str},
            performance={'pnl': results['pnl'], 'equity': results['equity']}
        )
        
        # Generate report if enabled
        if self.config.eod.write_reports:
            generate_eod_report(date_str, results, self.config)
    
    def close(self):
        """Cleanup resources"""
        self.db.close()


def run_eod_day(config: MeridianConfig, date: str) -> Dict[str, Any]:
    """
    Convenience function to run single EOD day.
    
    Args:
        config: Configuration
        date: Date string
    
    Returns:
        Results dict
    """
    orchestrator = EODOrchestrator(config)
    date_ts = pd.Timestamp(date)
    results = orchestrator.run_eod_day(date_ts)
    orchestrator.close()
    
    return results


