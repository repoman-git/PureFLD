"""
Performance Reporter for Meridian v2.1.2

Generate comprehensive performance attribution reports.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class PerformanceReporter:
    """
    Generates performance attribution reports.
    """
    
    def __init__(self, report_path: str = "logs/performance/"):
        self.report_path = Path(report_path)
        self.report_path.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        strategy_attribution: Dict[str, float],
        asset_attribution: Dict[str, float],
        regime_attribution: Dict[str, float],
        cycle_attribution: Dict[str, float]
    ) -> str:
        """
        Generate comprehensive attribution report.
        
        Returns:
            str: Path to report file
        """
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = self.report_path / f"{date_str}_attribution.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# Performance Attribution Report - {date_str}\n\n")
            
            f.write("## Strategy Attribution\n\n")
            for strategy, pnl in strategy_attribution.items():
                f.write(f"- **{strategy}**: ${pnl:,.2f}\n")
            
            f.write("\n## Asset Attribution\n\n")
            for asset, pnl in asset_attribution.items():
                f.write(f"- **{asset}**: ${pnl:,.2f}\n")
            
            f.write("\n## Regime Attribution\n\n")
            for regime, pnl in regime_attribution.items():
                f.write(f"- **{regime}**: ${pnl:,.2f}\n")
            
            f.write("\n## Cycle Attribution\n\n")
            for cycle_cond, pnl in cycle_attribution.items():
                f.write(f"- **{cycle_cond}**: ${pnl:,.2f}\n")
        
        return str(report_file)


def generate_attribution_report(
    strategy_attr: Dict,
    asset_attr: Dict,
    regime_attr: Dict,
    cycle_attr: Dict,
    report_path: str = "logs/performance/"
) -> str:
    """
    Simple function to generate attribution report.
    
    Returns:
        str: Path to report file
    """
    reporter = PerformanceReporter(report_path)
    return reporter.generate_report(strategy_attr, asset_attr, regime_attr, cycle_attr)


