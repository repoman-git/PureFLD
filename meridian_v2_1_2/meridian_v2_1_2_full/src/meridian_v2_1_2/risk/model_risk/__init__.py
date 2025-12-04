"""
Model Risk Engine for Meridian v2.1.2

Detect overfitting, instability, and fragility in trading strategies.
"""

from .overfit_detector import detect_overfit, compute_overfit_ratio
from .stability_analyzer import analyze_stability, compute_stability_score
from .drift_detector import detect_drift, compute_weight_drift
from .regime_dependency import analyze_regime_dependency, compute_dependency_score
from .sensitivity_tests import run_sensitivity_tests, SensitivityResult
from .fragility_index import compute_fragility_index
from .model_risk_reporter import generate_model_risk_report, ModelRiskRating

__all__ = [
    'detect_overfit',
    'compute_overfit_ratio',
    'analyze_stability',
    'compute_stability_score',
    'detect_drift',
    'compute_weight_drift',
    'analyze_regime_dependency',
    'compute_dependency_score',
    'run_sensitivity_tests',
    'SensitivityResult',
    'compute_fragility_index',
    'generate_model_risk_report',
    'ModelRiskRating',
]


