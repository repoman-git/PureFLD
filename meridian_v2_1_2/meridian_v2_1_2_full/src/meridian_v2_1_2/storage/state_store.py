"""
State Store for Meridian v2.1.2

High-level API for persistent state management.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from .local_db import LocalDB


class StateStore:
    """
    High-level state persistence API.
    
    Provides simple save/load operations for:
    - Strategy state
    - Portfolio positions
    - Risk metrics
    - Incubation state
    """
    
    def __init__(self, db: Optional[LocalDB] = None):
        """
        Initialize state store.
        
        Args:
            db: LocalDB instance (creates default if None)
        """
        if db is None:
            db = LocalDB()
        self.db = db
    
    # Strategy State
    
    def save_strategy_state(
        self,
        strategy_name: str,
        date: str,
        params: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Save strategy state.
        
        Args:
            strategy_name: Strategy name
            date: Date string (YYYY-MM-DD)
            params: Strategy parameters
            weights: Strategy weights (optional)
        """
        params_json = json.dumps(params)
        weights_json = json.dumps(weights) if weights else None
        
        self.db.execute("""
            INSERT OR REPLACE INTO state_strategy 
            (strategy_name, date, params, weights)
            VALUES (?, ?, ?, ?)
        """, (strategy_name, date, params_json, weights_json))
        
        self.db.commit()
    
    def load_strategy_state(
        self,
        strategy_name: str,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load strategy state.
        
        Args:
            strategy_name: Strategy name
            date: Date string (loads latest if None)
        
        Returns:
            Dict with params and weights, or None
        """
        if date:
            query = """
                SELECT params, weights FROM state_strategy
                WHERE strategy_name = ? AND date = ?
            """
            params = (strategy_name, date)
        else:
            query = """
                SELECT params, weights FROM state_strategy
                WHERE strategy_name = ?
                ORDER BY created_at DESC LIMIT 1
            """
            params = (strategy_name,)
        
        result = self.db.execute(query, params).fetchone()
        
        if result:
            return {
                'params': json.loads(result['params']) if result['params'] else {},
                'weights': json.loads(result['weights']) if result['weights'] else None
            }
        
        return None
    
    # Portfolio State
    
    def save_portfolio_state(
        self,
        date: str,
        positions: Dict[str, Dict[str, float]]
    ):
        """
        Save portfolio positions.
        
        Args:
            date: Date string
            positions: Dict of {symbol: {qty, cost_basis, market_value}}
        """
        for symbol, pos in positions.items():
            self.db.execute("""
                INSERT OR REPLACE INTO state_portfolio
                (date, symbol, qty, cost_basis, market_value)
                VALUES (?, ?, ?, ?, ?)
            """, (
                date,
                symbol,
                pos.get('qty', 0),
                pos.get('cost_basis', 0),
                pos.get('market_value', 0)
            ))
        
        self.db.commit()
    
    def load_portfolio_state(
        self,
        date: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Load portfolio positions for a date.
        
        Args:
            date: Date string
        
        Returns:
            Dict of positions
        """
        results = self.db.execute("""
            SELECT symbol, qty, cost_basis, market_value
            FROM state_portfolio
            WHERE date = ?
        """, (date,)).fetchall()
        
        positions = {}
        for row in results:
            positions[row['symbol']] = {
                'qty': row['qty'],
                'cost_basis': row['cost_basis'],
                'market_value': row['market_value']
            }
        
        return positions
    
    # Risk Metrics
    
    def save_risk_metrics(
        self,
        date: str,
        sharpe: Optional[float] = None,
        max_drawdown: Optional[float] = None,
        var_95: Optional[float] = None,
        volatility: Optional[float] = None
    ):
        """
        Save risk metrics.
        
        Args:
            date: Date string
            sharpe: Sharpe ratio
            max_drawdown: Maximum drawdown
            var_95: 95% VaR
            volatility: Portfolio volatility
        """
        self.db.execute("""
            INSERT OR REPLACE INTO risk_metrics
            (date, sharpe, max_drawdown, var_95, volatility)
            VALUES (?, ?, ?, ?, ?)
        """, (date, sharpe, max_drawdown, var_95, volatility))
        
        self.db.commit()
    
    def load_risk_metrics(
        self,
        date: str
    ) -> Optional[Dict[str, float]]:
        """Load risk metrics for a date"""
        result = self.db.execute("""
            SELECT sharpe, max_drawdown, var_95, volatility
            FROM risk_metrics
            WHERE date = ?
        """, (date,)).fetchone()
        
        if result:
            return {
                'sharpe': result['sharpe'],
                'max_drawdown': result['max_drawdown'],
                'var_95': result['var_95'],
                'volatility': result['volatility']
            }
        
        return None
    
    # Incubation State
    
    def save_incubation_state(
        self,
        strategy_name: str,
        state: str,
        days_in_state: int = 0
    ):
        """
        Save incubation state.
        
        Args:
            strategy_name: Strategy name
            state: State label (research/wfa_passed/paper/live/disabled)
            days_in_state: Days in current state
        """
        self.db.execute("""
            INSERT OR REPLACE INTO incubation
            (strategy_name, state, days_in_state, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (strategy_name, state, days_in_state))
        
        self.db.commit()
    
    def load_incubation_state(
        self,
        strategy_name: str
    ) -> Optional[Dict[str, Any]]:
        """Load incubation state"""
        result = self.db.execute("""
            SELECT state, days_in_state, last_updated
            FROM incubation
            WHERE strategy_name = ?
        """, (strategy_name,)).fetchone()
        
        if result:
            return {
                'state': result['state'],
                'days_in_state': result['days_in_state'],
                'last_updated': result['last_updated']
            }
        
        return None
    
    def close(self):
        """Close database connection"""
        self.db.close()

