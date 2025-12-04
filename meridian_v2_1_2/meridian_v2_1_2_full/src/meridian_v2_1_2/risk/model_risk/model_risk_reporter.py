"""
Model Risk Reporter for Meridian v2.1.2

Generate comprehensive model risk reports.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from enum import Enum


class ModelRiskRating(str, Enum):
    """Model risk rating levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def generate_model_risk_report(
    overfit_analysis: Dict[str, Any],
    stability_analysis: Dict[str, Any],
    drift_analysis: Dict[str, Any],
    regime_analysis: Dict[str, Any],
    fragility_analysis: Dict[str, Any],
    output_path: str
) -> Dict[str, str]:
    """
    Generate comprehensive model risk report.
    
    Args:
        overfit_analysis: Overfit detection results
        stability_analysis: Stability analysis results
        drift_analysis: Drift detection results
        regime_analysis: Regime dependency results
        fragility_analysis: Fragility assessment
        output_path: Output directory
    
    Returns:
        Dict of report paths
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Compute overall risk rating
    risk_rating = _compute_risk_rating(
        overfit_analysis,
        stability_analysis,
        drift_analysis,
        regime_analysis,
        fragility_analysis
    )
    
    # Generate summary report
    summary_path = output_dir / "MODEL_RISK_SUMMARY.md"
    _generate_summary_report(
        summary_path,
        risk_rating,
        overfit_analysis,
        stability_analysis,
        drift_analysis,
        regime_analysis,
        fragility_analysis
    )
    
    # Generate detailed breakdown
    breakdown_path = output_dir / "MODEL_RISK_BREAKDOWN.md"
    _generate_breakdown_report(
        breakdown_path,
        overfit_analysis,
        stability_analysis,
        drift_analysis,
        regime_analysis,
        fragility_analysis
    )
    
    return {
        'summary': str(summary_path),
        'breakdown': str(breakdown_path),
        'rating': risk_rating.value
    }


def _compute_risk_rating(
    overfit: Dict[str, Any],
    stability: Dict[str, Any],
    drift: Dict[str, Any],
    regime: Dict[str, Any],
    fragility: Dict[str, Any]
) -> ModelRiskRating:
    """Compute overall risk rating"""
    
    risk_score = 0
    
    # Overfit risk
    if overfit.get('overfit_detected', False):
        risk_score += 2
    
    # Stability risk
    if not stability.get('is_stable', True):
        risk_score += 2
    
    # Drift risk
    if drift.get('drift_detected', False):
        risk_score += 1
    
    # Regime dependency risk
    if not regime.get('is_diversified', True):
        risk_score += 1
    
    # Fragility risk
    if not fragility.get('is_robust', True):
        risk_score += 2
    
    # Map score to rating
    if risk_score >= 6:
        return ModelRiskRating.CRITICAL
    elif risk_score >= 4:
        return ModelRiskRating.HIGH
    elif risk_score >= 2:
        return ModelRiskRating.MEDIUM
    else:
        return ModelRiskRating.LOW


def _generate_summary_report(
    path: Path,
    rating: ModelRiskRating,
    overfit: Dict,
    stability: Dict,
    drift: Dict,
    regime: Dict,
    fragility: Dict
) -> None:
    """Generate summary report"""
    
    with open(path, 'w') as f:
        f.write("# MERIDIAN v2.1.2 MODEL RISK SUMMARY\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Overall rating
        f.write("## Overall Risk Rating\n\n")
        
        rating_emoji = {
            ModelRiskRating.LOW: "✅",
            ModelRiskRating.MEDIUM: "⚠️",
            ModelRiskRating.HIGH: "❌",
            ModelRiskRating.CRITICAL: "🚨"
        }
        
        f.write(f"### {rating_emoji[rating]} **{rating.value}**\n\n")
        
        # Risk components
        f.write("## Risk Components\n\n")
        
        f.write("| Component | Status | Score/Value |\n")
        f.write("|-----------|--------|-------------|\n")
        
        # Overfit
        overfit_status = "✅ OK" if not overfit.get('overfit_detected', False) else "❌ DETECTED"
        f.write(f"| Overfit | {overfit_status} | {overfit.get('overfit_ratio', 0):.2f} |\n")
        
        # Stability
        stability_status = "✅ STABLE" if stability.get('is_stable', True) else "❌ UNSTABLE"
        f.write(f"| Stability | {stability_status} | {stability.get('stability_score', 0):.2f} |\n")
        
        # Drift
        drift_status = "✅ NO DRIFT" if not drift.get('drift_detected', False) else "⚠️ DRIFT"
        f.write(f"| Drift | {drift_status} | {drift.get('weight_drift', 0):.3f} |\n")
        
        # Regime dependency
        regime_status = "✅ DIVERSIFIED" if regime.get('is_diversified', True) else "⚠️ CONCENTRATED"
        f.write(f"| Regime Dep. | {regime_status} | {regime.get('dependency_score', 0):.2f} |\n")
        
        # Fragility
        fragility_status = "✅ ROBUST" if fragility.get('is_robust', True) else "❌ FRAGILE"
        f.write(f"| Fragility | {fragility_status} | {fragility.get('fragility_index', 0):.3f} |\n")
        
        f.write("\n## Recommendations\n\n")
        
        if rating == ModelRiskRating.CRITICAL:
            f.write("🚨 **CRITICAL RISK** - Do not deploy to live trading\n\n")
            f.write("- System shows multiple critical risk factors\n")
            f.write("- Requires immediate redesign and revalidation\n")
        
        elif rating == ModelRiskRating.HIGH:
            f.write("❌ **HIGH RISK** - Not suitable for live trading\n\n")
            f.write("- Address identified risk factors before deployment\n")
            f.write("- Recommend additional testing and validation\n")
        
        elif rating == ModelRiskRating.MEDIUM:
            f.write("⚠️ **MEDIUM RISK** - Proceed with caution\n\n")
            f.write("- Monitor identified risk factors closely\n")
            f.write("- Consider additional safeguards\n")
        
        else:
            f.write("✅ **LOW RISK** - Model demonstrates good robustness\n\n")
            f.write("- Continue monitoring during deployment\n")
            f.write("- Maintain regular validation cycles\n")


def _generate_breakdown_report(
    path: Path,
    overfit: Dict,
    stability: Dict,
    drift: Dict,
    regime: Dict,
    fragility: Dict
) -> None:
    """Generate detailed breakdown report"""
    
    with open(path, 'w') as f:
        f.write("# MODEL RISK DETAILED BREAKDOWN\n\n")
        
        f.write("## 1. Overfit Analysis\n\n")
        f.write(f"- **Overfit Detected**: {overfit.get('overfit_detected', False)}\n")
        f.write(f"- **Overfit Ratio**: {overfit.get('overfit_ratio', 0):.2f}\n")
        f.write(f"- **OOS Consistency**: {overfit.get('oos_consistency', 0):.3f}\n")
        f.write(f"- **Number of Windows**: {overfit.get('num_windows', 0)}\n")
        f.write(f"- **Message**: {overfit.get('message', 'N/A')}\n\n")
        
        f.write("## 2. Stability Analysis\n\n")
        f.write(f"- **Is Stable**: {stability.get('is_stable', True)}\n")
        f.write(f"- **Stability Score**: {stability.get('stability_score', 0):.2f}\n")
        f.write(f"- **Weight Volatility**: {stability.get('weight_volatility', 0):.3f}\n")
        f.write(f"- **Parameter Consistency**: {stability.get('param_consistency', 0):.2f}\n")
        f.write(f"- **Message**: {stability.get('message', 'N/A')}\n\n")
        
        f.write("## 3. Drift Detection\n\n")
        f.write(f"- **Drift Detected**: {drift.get('drift_detected', False)}\n")
        f.write(f"- **Weight Drift**: {drift.get('weight_drift', 0):.3f}\n")
        f.write(f"- **Regime Instability**: {drift.get('regime_instability', 0):.2f}\n")
        f.write(f"- **Is Safe**: {drift.get('is_safe', True)}\n")
        f.write(f"- **Message**: {drift.get('message', 'N/A')}\n\n")
        
        f.write("## 4. Regime Dependency\n\n")
        f.write(f"- **Is Diversified**: {regime.get('is_diversified', True)}\n")
        f.write(f"- **Dependency Score**: {regime.get('dependency_score', 0):.2f}\n")
        f.write(f"- **Dominant Regime**: {regime.get('dominant_regime', 'N/A')}\n")
        f.write(f"- **Regime Concentration**: {regime.get('regime_concentration', 0):.2f}\n")
        
        if 'regime_breakdown' in regime:
            f.write("\n### PnL by Regime:\n\n")
            for reg, pnl in regime['regime_breakdown'].items():
                f.write(f"- **{reg}**: ${pnl:,.2f}\n")
        
        f.write(f"\n- **Message**: {regime.get('message', 'N/A')}\n\n")
        
        f.write("## 5. Fragility Assessment\n\n")
        f.write(f"- **Is Robust**: {fragility.get('is_robust', True)}\n")
        f.write(f"- **Fragility Index**: {fragility.get('fragility_index', 0):.3f}\n")
        f.write(f"- **Most Fragile Dimension**: {fragility.get('most_fragile_dimension', 'N/A')}\n")
        f.write(f"- **Tests Passed**: {fragility.get('num_passed', 0)}/{fragility.get('num_tests', 0)}\n")
        
        if fragility.get('fragile_tests'):
            f.write("\n### Failed Tests:\n\n")
            for test in fragility['fragile_tests']:
                f.write(f"- {test}\n")
        
        f.write(f"\n- **Message**: {fragility.get('message', 'N/A')}\n")


