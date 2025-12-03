from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SeasonalityConfig:
    """Configuration for seasonal overlays (TDOM, TDOY, etc.)"""
    # TDOM (Time Day of Month) - days 1-31
    use_tdom: bool = False
    favourable_days: list[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    unfavourable_days: list[int] = field(default_factory=list)
    
    # TDOY (Trading Day of Year) - days 1-366
    use_tdoy: bool = False
    tdoy_favourable: list[int] = field(default_factory=list)
    tdoy_unfavourable: list[int] = field(default_factory=list)

@dataclass
class FLDConfig:
    """FLD calculation parameters"""
    cycle_length: int = 40
    displacement: int = 20

@dataclass
class COTConfig:
    """COT filtering parameters"""
    use_cot: bool = False
    threshold: float = 0.0

@dataclass
class CycleStrategyConfig:
    """Configuration for cycle-aware strategy filters"""
    enable_cycle_filters: bool = False
    
    # Phase-based filtering (0.0 to 1.0, where 0.0=trough, 0.5=peak)
    allowed_phase_ranges: list[tuple[float, float]] = field(
        default_factory=lambda: [(0.0, 0.33), (0.66, 1.0)]  # Trough zones
    )
    
    # Turning point alignment
    require_turning_point_alignment: bool = False
    max_bars_from_turning_point: int = 8
    
    # Amplitude filter
    min_cycle_amplitude: float = 0.0
    
    # FLD timing windows
    enable_fld_timing_windows: bool = False
    fld_max_bars_before_tp: int = 8
    fld_max_bars_after_tp: int = 8
    
    # Cycle score threshold
    min_cycle_score: float = -999.0

@dataclass
class StrategyConfig:
    """Strategy behavior configuration"""
    use_tdom: bool = False
    use_cot: bool = False
    allow_shorts: bool = True
    cot_long_threshold: float = 0.0    # Long entries allowed when COT >= threshold
    cot_short_threshold: float = 0.0   # Short entries allowed when COT <= threshold
    contracts: int = 1                 # Number of contracts per position
    cycle_strategy: CycleStrategyConfig = field(default_factory=CycleStrategyConfig)

@dataclass
class BacktestConfig:
    """Backtesting parameters"""
    initial_capital: float = 100000.0
    commission: float = 0.0
    slippage: float = 0.0

@dataclass
class SweepConfig:
    """Configuration for parameter sweep engine"""
    enable_sweep: bool = False
    
    # FLD parameters to sweep
    cycle_lengths: list[int] = field(default_factory=list)
    displacements: list[int] = field(default_factory=list)
    
    # COT parameters to sweep
    cot_long_thresholds: list[float] = field(default_factory=list)
    cot_short_thresholds: list[float] = field(default_factory=list)
    
    # Seasonal parameters to sweep
    seasonal_score_minimums: list[int] = field(default_factory=lambda: [0])
    
    # Output configuration
    output_path: str = "sweep_results"
    output_format: str = "csv"  # Options: "csv", "json", "parquet"

@dataclass
class WalkForwardConfig:
    """Configuration for walk-forward testing"""
    enable_walkforward: bool = False
    
    # Window sizes
    in_sample_years: int = 5        # Training window size (years)
    out_sample_years: int = 1       # Testing window size (years)
    step_years: int = 1             # Slide amount (years)
    
    # Constraints
    min_bars: int = 200             # Minimum bars required
    allow_partial_final_window: bool = True
    
    # Optimization metric for parameter selection
    optimization_metric: str = 'calmar_ratio'  # Options: 'calmar_ratio', 'cagr', 'sharpe_ratio'

@dataclass
class CycleConfig:
    """Configuration for cycle phasing engine"""
    enable_cycles: bool = False
    
    # Cycle detection range
    min_cycle: int = 20
    max_cycle: int = 200
    step: int = 5
    
    # Smoothing parameters
    smoothing_window: int = 5
    turning_point_window: int = 3
    
    # Projection
    projection_bars: int = 40
    
    # Nominal model (Hurst-style)
    use_nominal_model: bool = True
    nominal_cycles: list[int] = field(default_factory=lambda: [20, 40, 80, 160])

@dataclass
class RegimeConfig:
    """Configuration for regime classification engine"""
    enable_regimes: bool = False
    
    # Volatility regime settings
    vol_lookback: int = 20
    vol_threshold_low: float = 0.01
    vol_threshold_high: float = 0.03
    
    # Trend regime settings
    trend_lookback: int = 50
    trend_threshold: float = 0.0
    
    # Cycle regime settings
    amplitude_threshold: float = 0.5
    cycle_slope_threshold: float = 0.0
    
    # Composite scoring
    enable_composite: bool = True
    composite_weights: dict = field(default_factory=lambda: {
        "vol": 0.33,
        "trend": 0.33,
        "cycle": 0.34
    })
    
    # Smoothing for classification
    smoothing_window: int = 5

@dataclass
class PortfolioConfig:
    """Configuration for portfolio engine"""
    enable_portfolio: bool = False
    
    # Capital allocation
    starting_capital: float = 100000.0
    allocation_method: str = "equal_weight"  # equal_weight, vol_parity, risk_parity
    
    # Leverage / exposure limits
    max_gross_exposure: float = 2.0    # 200% max gross
    max_net_exposure: float = 1.0      # 100% max net
    max_single_asset_weight: float = 0.3  # 30% per asset
    max_sector_weight: float = 0.5     # 50% per sector
    
    # Correlation controls
    use_correlation_matrix: bool = True
    correlation_lookback: int = 90
    max_correlation: float = 0.75
    
    # Portfolio-level risk
    target_volatility: float = 0.12    # 12% annual
    vol_lookback: int = 20
    
    # Rebalancing
    rebalance_frequency: str = "monthly"  # daily, weekly, monthly
    
    # Mode separation
    enforce_live_constraints: bool = True

@dataclass
class MetaStrategyConfig:
    """Configuration for multi-strategy engine"""
    enable_multi_strategy: bool = False
    
    # Blend mode: how strategies are combined
    blend_mode: str = "weighted"  # weighted, voting, override, gating
    
    # Strategy weights (for weighted mode)
    strategy_weights: dict = field(default_factory=dict)
    
    # Strategy participation
    strategies_enabled: list[str] = field(default_factory=list)
    
    # Voting configuration
    voting_threshold: float = 0.5  # % of strategies required to agree
    
    # Risk budgeting per strategy
    strategy_risk_budgets: dict = field(default_factory=dict)

@dataclass
class MetaLearningConfig:
    """Configuration for meta-learning engine"""
    enable_meta_learning: bool = False
    
    # Weight adaptation mode
    adaptation_mode: str = "performance"  # performance, regime, cycle, hybrid
    
    # Learning parameters
    learning_rate: float = 0.05
    min_weight: float = 0.05
    max_weight: float = 0.70
    
    # Reward model
    reward_lookback: int = 100
    reward_metric: str = "mar"  # sharpe, mar, winrate, expectancy
    
    # Confidence scoring
    use_confidence_model: bool = True
    confidence_smoothing: int = 10
    
    # Regime responsiveness
    enable_regime_adaptation: bool = True
    regime_transition_sensitivity: float = 0.3
    
    # Cycle responsiveness
    enable_cycle_adaptation: bool = True
    cycle_amplitude_weight: float = 0.2
    cycle_phase_weight: float = 0.1
    
    # Live mode safety
    allow_live_reweighting: bool = False

@dataclass
class HealthConfig:
    """Configuration for health monitoring engine"""
    enable_health_engine: bool = True
    
    # Thresholds
    max_gross_exposure: float = 2.0
    max_net_exposure: float = 1.0
    max_position_drift_pct: float = 0.05
    max_missing_bars: int = 0
    max_order_age_days: int = 1
    
    # Kill-switch
    enable_kill_switch: bool = True
    drawdown_kill_pct: float = 0.10
    
    # Alpaca connection
    require_connection: bool = True
    
    # Reporting
    write_reports: bool = True
    report_path: str = "logs/health/"

@dataclass
class PerformanceConfig:
    """Configuration for performance attribution engine"""
    enable_performance_attribution: bool = True
    
    # Granularity
    attribution_frequency: str = "daily"  # daily, weekly, monthly
    
    # Include components
    include_strategy: bool = True
    include_asset: bool = True
    include_regime: bool = True
    include_cycle: bool = True
    include_risk: bool = True
    include_execution: bool = True
    
    # Reporting
    write_reports: bool = True
    report_path: str = "logs/performance/"

@dataclass
class WFAConfig:
    """Configuration for Walk-Forward Analysis with EOD integration"""
    enable_wfa: bool = True
    
    # Splitting
    training_window: str = "3Y"     # rolling window
    testing_window: str = "6M"
    step_size: str = "1M"
    
    # Hyperparameters allowed to change
    allow_meta_learning: bool = True
    allow_strategy_weights: bool = True
    allow_risk_params: bool = False   # fixed risk during OOS
    
    # Execution realism
    use_slippage: bool = True
    use_delay: bool = True
    
    # Only EOD signals
    enforce_eod_only: bool = True
    
    # Reporting
    write_reports: bool = True
    report_path: str = "logs/wfa/"

@dataclass
class IncubationConfig:
    """Configuration for strategy incubation and promotion"""
    enable_incubation: bool = True
    
    # Promotion thresholds: WFA → Paper
    min_wfa_sharpe: float = 0.8
    min_wfa_mar: float = 0.5
    max_wfa_overfit_ratio: float = 2.0
    min_wfa_winrate: float = 0.45
    min_wfa_stability: float = 1.0
    
    # Promotion thresholds: Paper → Live
    min_paper_days: int = 45
    min_paper_sharpe: float = 0.8
    max_paper_drawdown: float = 0.10
    min_paper_consistency: float = 0.6
    
    # Demotion thresholds
    max_live_drawdown: float = 0.12
    min_live_sharpe: float = 0.5
    max_live_drift_pct: float = 0.10
    consecutive_failures_limit: int = 3
    
    # Mode controls
    allow_auto_promotion: bool = True
    allow_auto_demotion: bool = True
    require_manual_live_approval: bool = True
    
    # State persistence
    state_path: str = "state/strategy_status.json"
    
    # Reporting
    report_path: str = "logs/incubation/"

@dataclass
class OpenBBConfig:
    """Configuration for OpenBB data integration (Phase 22 - offline mode)"""
    enable_openbb: bool = True
    
    # Mode: 'synthetic' (no API calls) or 'live' (future)
    mode: str = "synthetic"
    
    # Caching
    cache_enabled: bool = True
    cache_path: str = "cache/openbb/"
    cache_expiry_days: int = 1
    
    # Data sources (fallback for synthetic testing)
    price_source: str = "yahoo"
    
    # Synthetic data parameters
    synthetic_start_price: float = 100.0
    synthetic_volatility: float = 0.02
    synthetic_drift: float = 0.0001

@dataclass
class PaperSimConfig:
    """Configuration for paper trading simulation (Phase 23)"""
    enable_paper_sim: bool = True
    
    # Execution behavior
    fill_mode: str = "EOD"  # EOD (end-of-day) or MOO (market-on-open)
    slippage_bps: float = 5.0  # basis points of slippage
    gap_model: bool = True  # model overnight gaps
    partial_fill_probability: float = 0.0  # probability of partial fills
    
    # Starting capital
    starting_capital: float = 100000.0
    
    # OMS / Logging
    log_path: str = "logs/paper_sim/"
    write_logs: bool = True
    
    # Reconciliation
    enforce_reconciliation: bool = True
    reconciliation_tolerance: float = 0.01  # 1% tolerance

@dataclass
class SyntheticConfig:
    """Configuration for synthetic market generation (Phase 24)"""
    enable_synthetic: bool = True
    
    # Data length
    length_days: int = 2000
    seed: int = 42
    
    # Volatility parameters
    vol_mode: str = "regime"  # regime / constant / stochastic
    vol_low: float = 0.005
    vol_high: float = 0.02
    
    # Trend parameters
    trend_strength: float = 0.4
    trend_mode: str = "alternating"  # random / alternating / structural
    
    # Cycle parameters
    cycle_amp: float = 0.03
    cycle_period: int = 120
    cycle_deform: bool = True
    
    # Macro real-yield model
    real_yield_amp: float = 0.5
    real_yield_shock_probability: float = 0.02
    
    # Gold-yield correlation
    gold_yield_corr: float = -0.65
    
    # COT patterns
    cot_noise: float = 0.3
    cot_trendiness: float = 0.2
    
    # Regime sequencing
    regime_switch_prob: float = 0.1

@dataclass
class StressConfig:
    """Configuration for stress testing and chaos engineering (Phase 26)"""
    enable_stress_engine: bool = True
    
    # Shock types
    enable_price_shocks: bool = True
    enable_yield_shocks: bool = True
    enable_cot_shocks: bool = True
    enable_macro_shocks: bool = True
    
    # Operational failures
    enable_fill_failures: bool = True
    enable_order_duplication: bool = True
    enable_missing_bars: bool = True
    enable_nan_injection: bool = True
    enable_regime_breaks: bool = True
    enable_cycle_breaks: bool = True
    
    # Severity (0-1 scale)
    severity: float = 0.7
    
    # Test runs
    num_runs: int = 50
    
    # Reporting
    report_path: str = "logs/stress/"

@dataclass
class ModelRiskConfig:
    """Configuration for model risk analysis (Phase 27)"""
    enable_model_risk: bool = True
    
    # Thresholds
    max_overfit_ratio: float = 2.0
    min_stability_score: float = 0.6
    max_meta_drift: float = 0.15
    max_regime_dependency: float = 0.5
    max_fragility_index: float = 0.35
    
    # Sensitivity tests
    shock_pct: float = 0.01  # +/-1% data perturbation
    cycle_perturb_pct: float = 0.1
    cot_noise_pct: float = 0.15
    
    # Reporting
    write_reports: bool = True
    report_path: str = "logs/model_risk/"

@dataclass
class EODConfig:
    """Configuration for EOD trading orchestrator (Phase 29)"""
    mode: str = "dry_live"  # research | paper | dry_live
    
    # Features
    run_model_risk: bool = True
    run_stress_checks: bool = True
    run_wfa: bool = False
    
    # Simulated time advancement
    simulate_clock: bool = True
    start_date: str = "2010-01-01"
    end_date: str = "2025-01-01"
    
    # Safety
    enable_safety_layer: bool = True
    max_daily_loss_pct: float = 0.05  # 5% max daily loss
    
    # Reporting
    write_reports: bool = True
    report_path: str = "logs/eod/"

@dataclass
class MeridianConfig:
    """Master configuration object for Meridian v2.1.2"""
    # Operating mode: research (backtesting) | paper (simulation) | live (real trading)
    mode: str = "research"
    
    fld: FLDConfig = field(default_factory=FLDConfig)
    cot: COTConfig = field(default_factory=COTConfig)
    seasonality: SeasonalityConfig = field(default_factory=SeasonalityConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    sweep: SweepConfig = field(default_factory=SweepConfig)
    walkforward: WalkForwardConfig = field(default_factory=WalkForwardConfig)
    cycles: CycleConfig = field(default_factory=CycleConfig)
    regimes: RegimeConfig = field(default_factory=RegimeConfig)
    portfolio: PortfolioConfig = field(default_factory=PortfolioConfig)
    meta_strategy: MetaStrategyConfig = field(default_factory=MetaStrategyConfig)
    meta_learning: MetaLearningConfig = field(default_factory=MetaLearningConfig)
    health: HealthConfig = field(default_factory=HealthConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    wfa: WFAConfig = field(default_factory=WFAConfig)
    incubation: IncubationConfig = field(default_factory=IncubationConfig)
    openbb: OpenBBConfig = field(default_factory=OpenBBConfig)
    paper_sim: PaperSimConfig = field(default_factory=PaperSimConfig)
    synthetic: SyntheticConfig = field(default_factory=SyntheticConfig)
    stress: StressConfig = field(default_factory=StressConfig)
    model_risk: ModelRiskConfig = field(default_factory=ModelRiskConfig)
    eod: EODConfig = field(default_factory=EODConfig)
    
    # External integration (Phase 30)
    def get_external_config(self):
        """Get external config (imported on demand to avoid circular imports)"""
        from .external.external_config import ExternalConfig
        return ExternalConfig()
    
    # Live trading (Phase 31)
    def get_live_config(self):
        """Get live config (imported on demand to avoid circular imports)"""
        from .live.live_config import LiveConfig
        return LiveConfig()
    
    def __post_init__(self):
        """Validate mode after initialization"""
        if self.mode not in ["research", "paper", "live"]:
            raise ValueError(f"mode must be one of: research, paper, live. Got: {self.mode}")
    
    @property
    def risk(self):
        """Risk config imported from risk_engine"""
        from .risk_engine.risk_config import RiskConfig
        if not hasattr(self, '_risk'):
            self._risk = RiskConfig()
        return self._risk
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MeridianConfig':
        """Load config from dictionary (e.g., from JSON)"""
        return cls(
            fld=FLDConfig(**data.get('fld', {})) if 'fld' in data else FLDConfig(),
            cot=COTConfig(**data.get('cot', {})) if 'cot' in data else COTConfig(),
            seasonality=SeasonalityConfig(**data.get('seasonality', {})) if 'seasonality' in data else SeasonalityConfig(),
            strategy=StrategyConfig(**data.get('strategy', {})) if 'strategy' in data else StrategyConfig(),
            backtest=BacktestConfig(**data.get('backtest', {})) if 'backtest' in data else BacktestConfig(),
        )
