"""
Paper Trading Orchestrator

Main controller for paper trading system.
Coordinates: data → strategy → audit → execution → PnL → history

⚠️  PAPER TRADING ONLY - NO REAL MONEY
"""

from typing import Dict, Any, Optional
import pandas as pd

from .data_feed import LiveDataFeed
from .portfolio_state import PortfolioState
from .fill_simulator import FillSimulator
from .pnl_engine import PnLEngine
from .signal_scheduler import SignalScheduler, SignalTiming
from .trade_history import TradeHistory

# Import strategy router
from meridian_v2_1_2.strategies.strategy_router import load_strategy, list_strategies

# Import Trading Audit Engine (Phase X-Trading)
try:
    from meridian_v2_1_2.trading_audit_engine import TradingAuditOrchestrator
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False


class PaperTradingOrchestrator:
    """
    Paper trading orchestration engine.
    
    Complete workflow:
    1. Pull live data
    2. Run strategy signals
    3. Audit through Trading Audit Engine
    4. Simulate fills
    5. Update portfolio
    6. Calculate PnL
    7. Log trades
    
    ⚠️  100% SIMULATED - EDUCATIONAL ONLY
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        slippage_bps: float = 5.0
    ):
        """
        Initialize paper trading orchestrator.
        
        Args:
            initial_capital: Starting capital
            slippage_bps: Slippage in basis points
        """
        self.data_feed = LiveDataFeed()
        self.portfolio = PortfolioState(initial_capital)
        self.fill_simulator = FillSimulator(slippage_bps)
        self.pnl_engine = PnLEngine()
        self.scheduler = SignalScheduler()
        self.history = TradeHistory()
        
        # Trading Audit integration
        if AUDIT_AVAILABLE:
            self.audit_engine = TradingAuditOrchestrator()
        else:
            self.audit_engine = None
        
        self.initial_capital = initial_capital
    
    def run_instrument_pipeline(
        self,
        symbol: str,
        strategy_name: str,
        advanced_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete analysis pipeline for one instrument.
        
        Pipeline:
        1. Fetch live data
        2. Load strategy
        3. Generate signal
        4. Run trading audit
        5. Generate commentary
        
        Args:
            symbol: Asset symbol (e.g., 'GLD')
            strategy_name: Strategy to use
            advanced_mode: Include advanced diagnostics
        
        Returns:
            Dictionary with complete analysis
        """
        result = {
            'symbol': symbol,
            'strategy': strategy_name,
            'status': 'running',
            'data': None,
            'signal': None,
            'audit': None,
            'commentary': None
        }
        
        # Step 1: Fetch live data
        try:
            price = self.data_feed.fetch_latest_price(symbol)
            ohlc = self.data_feed.fetch_latest_ohlc(symbol)
            
            if price is None or ohlc is None or ohlc.empty:
                result['status'] = 'error'
                result['error'] = 'Failed to fetch data'
                return result
            
            result['data'] = {
                'current_price': price,
                'ohlc': ohlc.tail(50).to_dict()  # Last 50 bars
            }
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f'Data fetch error: {e}'
            return result
        
        # Step 2: Load strategy
        try:
            strategy = load_strategy(strategy_name)
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f'Strategy load error: {e}'
            return result
        
        # Step 3: Generate signal
        try:
            signals_df = strategy.generate_signals(ohlc)
            latest_signal = signals_df.iloc[-1].to_dict()
            
            result['signal'] = {
                'long_signal': int(latest_signal.get('long_signal', 0)),
                'short_signal': int(latest_signal.get('short_signal', 0)),
                'signal_strength': float(latest_signal.get('signal_strength', 0)),
                'current_price': price
            }
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f'Signal generation error: {e}'
            return result
        
        # Step 4: Run trading audit (if signal is actionable)
        if result['signal']['long_signal'] or result['signal']['short_signal']:
            try:
                trade_intent = {
                    'symbol': symbol,
                    'direction': 'long' if result['signal']['long_signal'] else 'short',
                    'size': 0.05,  # 5% position
                    'entry_price': price,
                    'stop_loss': price * 0.98,  # 2% stop
                    'signal_strength': result['signal']['signal_strength'],
                    'strategy_name': strategy_name
                }
                
                if self.audit_engine:
                    audit_result = self.audit_engine.audit_trade(
                        trade_intent,
                        {'allow_short': True},
                        self.portfolio.to_dict(),
                        run_ai_review=False  # Skip AI for speed
                    )
                    
                    result['audit'] = {
                        'final_status': audit_result.final_status,
                        'should_execute': audit_result.should_execute,
                        'summary': audit_result.summary
                    }
                else:
                    result['audit'] = {
                        'final_status': 'APPROVED',
                        'should_execute': True,
                        'summary': 'Audit engine not available'
                    }
            
            except Exception as e:
                result['audit'] = {
                    'final_status': 'ERROR',
                    'should_execute': False,
                    'summary': f'Audit error: {e}'
                }
        
        # Step 5: Generate commentary
        result['commentary'] = self._generate_commentary(
            symbol,
            strategy_name,
            result['signal'],
            result.get('audit'),
            advanced_mode
        )
        
        result['status'] = 'complete'
        return result
    
    def execute_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        strategy_name: str
    ) -> Dict[str, Any]:
        """
        Execute a simulated trade.
        
        Full pipeline:
        1. Get current price
        2. Run trading audit
        3. Simulate fill
        4. Update portfolio
        5. Calculate PnL
        6. Log trade
        
        Args:
            symbol: Asset symbol
            side: 'BUY' or 'SELL'
            quantity: Number of shares
            strategy_name: Strategy name
        
        Returns:
            Dictionary with execution result
        """
        # Get current price
        price = self.data_feed.fetch_latest_price(symbol)
        
        if price is None:
            return {
                'success': False,
                'error': 'Failed to fetch current price'
            }
        
        # Run trading audit
        trade_intent = {
            'symbol': symbol,
            'direction': 'long' if side == 'BUY' else 'short',
            'size': (quantity * price) / self.portfolio.get_total_value(),
            'entry_price': price,
            'stop_loss': price * 0.98,
            'signal_strength': 0.7,
            'strategy_name': strategy_name
        }
        
        audit_result = None
        if self.audit_engine:
            audit = self.audit_engine.audit_trade(
                trade_intent,
                {},
                self.portfolio.to_dict(),
                run_ai_review=False
            )
            audit_result = {
                'final_status': audit.final_status,
                'should_execute': audit.should_execute
            }
        
        # Simulate fill
        fill = self.fill_simulator.simulate_market_order(
            symbol, quantity, price, side, audit_result
        )
        
        if not fill.success:
            return {
                'success': False,
                'error': f'Fill blocked: {fill.audit_status}'
            }
        
        # Update portfolio
        success = self.portfolio.apply_fill(
            symbol, quantity, fill.fill_price, side
        )
        
        if not success:
            return {
                'success': False,
                'error': 'Insufficient funds/shares'
            }
        
        # Log trade
        self.history.add_trade(
            symbol=symbol,
            side=side,
            quantity=quantity,
            fill_price=fill.fill_price,
            audit_status=fill.audit_status,
            audit_flags=[],
            strategy=strategy_name
        )
        
        # Calculate PnL
        pnl_report = self.pnl_engine.calculate_pnl(
            self.portfolio.to_dict(),
            self.initial_capital
        )
        
        return {
            'success': True,
            'fill': fill,
            'portfolio': self.portfolio.to_dict(),
            'pnl': pnl_report
        }
    
    def _generate_commentary(
        self,
        symbol: str,
        strategy: str,
        signal: Dict[str, Any],
        audit: Optional[Dict[str, Any]],
        advanced: bool
    ) -> Dict[str, Any]:
        """Generate AI-style commentary (rule-based for now)"""
        
        commentary = {
            'summary': f"{strategy} analysis for {symbol}",
            'signal_interpretation': '',
            'risk_notes': [],
            'market_context': ''
        }
        
        # Signal interpretation
        if signal.get('long_signal'):
            commentary['signal_interpretation'] = f"Strategy indicates LONG signal with {signal.get('signal_strength', 0):.2%} strength"
        elif signal.get('short_signal'):
            commentary['signal_interpretation'] = f"Strategy indicates SHORT signal with {signal.get('signal_strength', 0):.2%} strength"
        else:
            commentary['signal_interpretation'] = "No active signal - FLAT position recommended"
        
        # Audit notes
        if audit:
            if audit['final_status'] == 'BLOCKED':
                commentary['risk_notes'].append("⛔ Trading Audit BLOCKED this trade")
            elif audit['final_status'] == 'WARNING':
                commentary['risk_notes'].append("⚠️  Trading Audit flagged concerns")
            else:
                commentary['risk_notes'].append("✅ Trading Audit approved")
        
        # Market context (simplified)
        commentary['market_context'] = f"Current price: ${signal.get('current_price', 0):.2f}"
        
        return commentary

