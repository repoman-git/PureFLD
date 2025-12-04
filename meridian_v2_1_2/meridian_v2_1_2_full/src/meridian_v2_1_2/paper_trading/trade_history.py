"""
Trade History

Persistent storage for paper trading history.

⚠️  SIMULATED TRADES ONLY - Educational records
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path


@dataclass
class TradeRecord:
    """Single trade record"""
    timestamp: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: float
    fill_price: float
    audit_status: str  # 'APPROVED', 'WARNING', 'BLOCKED'
    audit_flags: List[str]
    strategy: str
    notes: str
    pnl: Optional[float] = None
    
    # Educational disclaimer
    is_simulated: bool = True


class TradeHistory:
    """
    Persistent trade history for paper trading.
    
    Stores all trades to local JSON file.
    
    ⚠️  EDUCATIONAL RECORDS ONLY
    """
    
    def __init__(self, storage_path: str = "meridian_local/paper_trades.json"):
        """
        Initialize trade history.
        
        Args:
            storage_path: Path to JSON storage file
        """
        self.storage_path = Path(storage_path)
        self.trades: List[TradeRecord] = []
        
        # Create directory if needed
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self.load()
    
    def add_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        fill_price: float,
        audit_status: str,
        audit_flags: List[str],
        strategy: str,
        notes: str = "",
        pnl: Optional[float] = None
    ) -> TradeRecord:
        """
        Add a trade to history.
        
        Args:
            symbol: Asset symbol
            side: 'BUY' or 'SELL'
            quantity: Trade quantity
            fill_price: Fill price
            audit_status: Audit result
            audit_flags: List of audit warnings/flags
            strategy: Strategy name
            notes: Optional notes
            pnl: Optional realized PnL
        
        Returns:
            Created TradeRecord
        """
        trade = TradeRecord(
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            side=side,
            quantity=quantity,
            fill_price=fill_price,
            audit_status=audit_status,
            audit_flags=audit_flags,
            strategy=strategy,
            notes=notes,
            pnl=pnl
        )
        
        self.trades.append(trade)
        self.save()
        
        return trade
    
    def get_trades(
        self,
        symbol: Optional[str] = None,
        strategy: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[TradeRecord]:
        """
        Get trades with optional filtering.
        
        Args:
            symbol: Filter by symbol (optional)
            strategy: Filter by strategy (optional)
            limit: Max number of trades to return
        
        Returns:
            List of TradeRecords (most recent first)
        """
        trades = self.trades[::-1]  # Reverse for most recent first
        
        # Apply filters
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        
        if strategy:
            trades = [t for t in trades if t.strategy == strategy]
        
        # Apply limit
        if limit:
            trades = trades[:limit]
        
        return trades
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get trade statistics.
        
        Returns:
            Dictionary with stats
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'total_buys': 0,
                'total_sells': 0,
                'approved_pct': 0.0,
                'blocked_pct': 0.0
            }
        
        total = len(self.trades)
        buys = sum(1 for t in self.trades if t.side == 'BUY')
        sells = sum(1 for t in self.trades if t.side == 'SELL')
        approved = sum(1 for t in self.trades if t.audit_status == 'APPROVED')
        blocked = sum(1 for t in self.trades if t.audit_status == 'BLOCKED')
        
        return {
            'total_trades': total,
            'total_buys': buys,
            'total_sells': sells,
            'approved_pct': (approved / total) * 100,
            'blocked_pct': (blocked / total) * 100
        }
    
    def save(self):
        """Save trade history to JSON"""
        data = {
            'trades': [asdict(t) for t in self.trades],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load trade history from JSON"""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.trades = [
                TradeRecord(**t)
                for t in data.get('trades', [])
            ]
        except Exception as e:
            print(f"Error loading trade history: {e}")
            self.trades = []
    
    def clear_history(self):
        """Clear all trade history"""
        self.trades = []
        self.save()


