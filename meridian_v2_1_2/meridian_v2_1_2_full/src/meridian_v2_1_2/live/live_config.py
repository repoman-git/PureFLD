"""
Live Trading Configuration for Meridian v2.1.2

Master safety layer for real-money trading.
"""

from dataclasses import dataclass


@dataclass
class LiveConfig:
    """
    Live trading configuration.
    
    SAFETY PRINCIPLE: All real trading is OFF by default.
    Multiple explicit flags must be enabled.
    """
    
    # Master switch (OFF by default)
    enable_live_trading: bool = False
    
    # Operator confirmation (REQUIRED by default)
    require_operator_confirmation: bool = True
    
    # Risk limits
    max_daily_loss_pct: float = 2.0  # 2% max daily loss
    max_drawdown_pct: float = 5.0  # 5% max drawdown from peak
    max_position_notional: float = 50000.0  # $50k max per position
    max_single_order_notional: float = 10000.0  # $10k max per order
    max_total_exposure: float = 100000.0  # $100k max total exposure
    
    # Execution parameters
    max_slippage_pct: float = 0.15  # 0.15% max slippage
    order_timeout_seconds: int = 30
    max_retry_attempts: int = 3
    
    # Monitoring
    heartbeat_interval_sec: int = 60
    heartbeat_max_failures: int = 3
    
    # Reconciliation
    reconciliation_required: bool = True
    max_drift_pct: float = 0.01  # 1% max position drift
    reconcile_after_every_order: bool = True
    
    # Model risk integration
    run_model_risk_pre_trade: bool = True
    max_model_risk_score: float = 0.5
    
    # Logging & reporting
    log_all_orders: bool = True
    write_live_reports: bool = True
    report_path: str = "logs/live/"
    
    # Safety features
    enable_kill_switch: bool = True
    forbidden_symbols: list = None  # List of forbidden symbols
    
    # Account limits
    min_account_balance: float = 10000.0  # Minimum balance required
    max_leverage: float = 1.0  # No leverage by default
    
    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.forbidden_symbols is None:
            self.forbidden_symbols = []

