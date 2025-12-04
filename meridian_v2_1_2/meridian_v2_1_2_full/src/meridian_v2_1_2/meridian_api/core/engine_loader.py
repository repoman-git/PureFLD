"""Engine Loader - Singleton for all Meridian engines"""
from meridian_v2_1_2.hurst.hurst_phasing import HurstPhasingEngine
from meridian_v2_1_2.hurst.hurst_harmonics import HarmonicsEngine
from meridian_v2_1_2.hurst.cycle_forecaster import CycleForecaster
from meridian_v2_1_2.hurst.intermarket_engine import IntermarketCycleEngine
from meridian_v2_1_2.regimes.cycle_regime_classifier import CycleRegimeClassifier
from meridian_v2_1_2.volatility_risk import *
from meridian_v2_1_2.portfolio_allocation import *
from meridian_v2_1_2.strategy_evolution import GeneticStrategyEngine

class EngineLoader:
    """Singleton loader for all Meridian engines"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize all engines"""
        self.phaser = HurstPhasingEngine()
        self.harmonics = HarmonicsEngine()
        self.forecaster = CycleForecaster()
        self.intermarket = IntermarketCycleEngine()
        self.regime_classifier = CycleRegimeClassifier()
        self.vol_feature_builder = VolFeatureBuilder()
        self.cycle_atr = CycleATR()
        self.vol_model = CycleVolatilityModel()
        self.rws_model = RiskWindowModel()
        self.portfolio_feature_builder = PortfolioFeatureBuilder()
        self.portfolio_allocator = PortfolioAllocator()
        self.portfolio_risk_model = PortfolioRiskModel()
        self.cycle_weighting_model = CycleWeightingModel()
        self.genetic_engine = GeneticStrategyEngine()

# Singleton instance
loader = EngineLoader()

