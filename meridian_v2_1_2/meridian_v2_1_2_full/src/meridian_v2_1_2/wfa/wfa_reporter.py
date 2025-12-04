"""
WFA Reporter for Meridian v2.1.2

Generate comprehensive walk-forward analysis reports.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class WFAReporter:
    """
    Generates walk-forward analysis reports.
    """
    
    def __init__(self, report_path: str = "logs/wfa/"):
        self.report_path = Path(report_path)
        self.report_path.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        wfa_results: List[Dict[str, Any]],
        wfa_metrics: Dict[str, float]
    ) -> str:
        """
        Generate comprehensive WFA report.
        
        Args:
            wfa_results: List of window results
            wfa_metrics: Aggregate metrics
        
        Returns:
            str: Path to report file
        """
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = self.report_path / f"{date_str}_wfa_report.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# Walk-Forward Analysis Report - {date_str}\n\n")
            
            f.write("## Summary Metrics\n\n")
            for metric, value in wfa_metrics.items():
                if isinstance(value, float):
                    f.write(f"- **{metric}**: {value:.4f}\n")
                else:
                    f.write(f"- **{metric}**: {value}\n")
            
            f.write("\n## Window Results\n\n")
            f.write("| Window | Train Start | Test Start | OOS Sharpe | OOS Return |\n")
            f.write("|--------|-------------|------------|------------|------------|\n")
            
            for i, result in enumerate(wfa_results):
                f.write(
                    f"| {i+1} | {result['train_start'].date()} | "
                    f"{result['test_start'].date()} | "
                    f"{result['oos_sharpe']:.2f} | "
                    f"{result['oos_return']:.4f} |\n"
                )
            
            f.write("\n## Interpretation\n\n")
            
            # Overfit warning
            if 'overfit_index' in wfa_metrics and wfa_metrics['overfit_index'] > 2.0:
                f.write("⚠️ **OVERFIT RISK**: Training performance significantly exceeds OOS performance.\n\n")
            
            # Stability assessment
            if wfa_metrics.get('stability_score', 0) > 1.0:
                f.write("✅ **STABLE**: System shows consistent OOS performance.\n\n")
            else:
                f.write("⚠️ **UNSTABLE**: High variance in OOS results.\n\n")
            
            # Win rate
            win_rate = wfa_metrics.get('win_rate', 0)
            if win_rate > 0.6:
                f.write(f"✅ **ROBUST**: {win_rate*100:.1f}% positive windows.\n\n")
            else:
                f.write(f"⚠️ **LOW WIN RATE**: Only {win_rate*100:.1f}% positive windows.\n\n")
        
        return str(report_file)


def generate_wfa_report(
    wfa_results: List[Dict],
    wfa_metrics: Dict,
    report_path: str = "logs/wfa/"
) -> str:
    """
    Simple function to generate WFA report.
    
    Returns:
        str: Path to report file
    """
    reporter = WFAReporter(report_path)
    return reporter.generate_report(wfa_results, wfa_metrics)


