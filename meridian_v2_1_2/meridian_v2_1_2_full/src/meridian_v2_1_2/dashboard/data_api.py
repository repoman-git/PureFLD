"""
Dashboard Data API for Meridian v2.1.2

Backend API for dashboard data queries.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json


class DashboardAPI:
    """
    Backend API for dashboard data.
    
    Provides data to UI components from local sources only.
    """
    
    def __init__(self, config, state_store=None):
        """
        Initialize dashboard API.
        
        Args:
            config: DashboardConfig instance
            state_store: StateStore for persistence
        """
        self.config = config
        self.state_store = state_store
    
    def get_portfolio_state(self) -> Dict[str, Any]:
        """
        Get current portfolio state.
        
        Returns:
            Dict with positions, cash, equity, PnL
        """
        # In full implementation, would query state_store
        return {
            'timestamp': datetime.now().isoformat(),
            'positions': [
                {
                    'symbol': 'GLD',
                    'qty': 100,
                    'cost_basis': 18000,
                    'market_value': 19500,
                    'pnl': 1500,
                    'pnl_pct': 8.33
                }
            ],
            'cash': 50000,
            'equity': 69500,
            'total_pnl': 1500
        }
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders, optionally filtered by status.
        
        Args:
            status: Filter by status (open, filled, rejected, etc.)
        
        Returns:
            List of order dicts
        """
        orders = [
            {
                'id': 'ord_001',
                'symbol': 'GLD',
                'side': 'buy',
                'qty': 10,
                'type': 'market',
                'status': 'filled',
                'filled_qty': 10,
                'avg_fill_price': 195.50,
                'submitted_at': (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
        
        if status:
            orders = [o for o in orders if o['status'] == status]
        
        return orders
    
    def get_fills(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get fill history.
        
        Args:
            since: Only return fills since this time
        
        Returns:
            List of fill dicts
        """
        return [
            {
                'id': 'fill_001',
                'order_id': 'ord_001',
                'symbol': 'GLD',
                'side': 'buy',
                'qty': 10,
                'price': 195.50,
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'slippage_bps': 3.2
            }
        ]
    
    def get_signals(self) -> Dict[str, Any]:
        """
        Get current strategy signals.
        
        Returns:
            Dict with signals by strategy
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'signals': {
                'fld': {'GLD': 1, 'LTPZ': 0},
                'cot': {'GLD': 1, 'LTPZ': -1},
                'tdom': {'GLD': 1, 'LTPZ': 0},
                'regime': {'GLD': 1, 'LTPZ': 0},
                'combined': {'GLD': 1, 'LTPZ': 0}
            }
        }
    
    def get_risk_state(self) -> Dict[str, Any]:
        """
        Get current risk metrics.
        
        Returns:
            Dict with risk scores and metrics
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'model_risk_score': 0.23,
            'exposure': {
                'gross': 19500,
                'net': 19500,
                'max_allowed': 100000
            },
            'volatility_regime': 'medium',
            'kill_switch_active': False
        }
    
    def get_oversight_state(self) -> Dict[str, Any]:
        """
        Get oversight AI state.
        
        Returns:
            Dict with anomaly scores, risk assessment, advisories
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'anomaly_scores': {
                'strategy': 0.21,
                'execution': 0.15,
                'shadow': 0.08,
                'portfolio': 0.19,
                'overall': 0.16
            },
            'risk_assessment': {
                'level': 'low',
                'score': 0.25,
                'should_halt': False
            },
            'advisories': []
        }
    
    def get_shadow_state(self) -> Dict[str, Any]:
        """
        Get broker shadow/drift state.
        
        Returns:
            Dict with drift status and reconciliation
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'drift_detected': False,
            'drift_level': 'none',
            'last_check': datetime.now().isoformat(),
            'positions_synced': True
        }
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """
        Get pending approval requests.
        
        Returns:
            List of approval request dicts
        """
        # In full implementation, would query approval queue
        return []
    
    def approve_request(self, request_id: str, approved_by: str = 'operator') -> bool:
        """
        Approve a pending request.
        
        Args:
            request_id: Request ID to approve
            approved_by: Operator identifier
        
        Returns:
            True if successful
        """
        # In full implementation, would update approval queue
        return True
    
    def reject_request(self, request_id: str, reason: str = '', rejected_by: str = 'operator') -> bool:
        """
        Reject a pending request.
        
        Args:
            request_id: Request ID to reject
            reason: Rejection reason
            rejected_by: Operator identifier
        
        Returns:
            True if successful
        """
        # In full implementation, would update approval queue
        return True
    
    def get_run_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent run logs.
        
        Args:
            limit: Max number of logs to return
        
        Returns:
            List of run log dicts
        """
        return [
            {
                'timestamp': datetime.now().isoformat(),
                'run_id': 'run_001',
                'status': 'success',
                'signals_generated': 2,
                'orders_submitted': 1,
                'pnl': 150.50
            }
        ]
    
    def get_pnl_timeseries(self, days: int = 30) -> Dict[str, Any]:
        """
        Get PnL time series.
        
        Args:
            days: Number of days to return
        
        Returns:
            Dict with dates and PnL values
        """
        # Generate sample data
        dates = []
        pnl = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            dates.append(date.strftime('%Y-%m-%d'))
            pnl.append(1000 + i * 50)  # Sample increasing PnL
        
        return {
            'dates': dates,
            'pnl': pnl
        }


