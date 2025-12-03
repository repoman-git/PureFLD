"""
Incubation Reporter for Meridian v2.1.2

Generate incubation status reports.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from .incubator_state import StrategyStatus


class IncubationReporter:
    """
    Generates incubation pipeline reports.
    """
    
    def __init__(self, report_path: str = "logs/incubation/"):
        self.report_path = Path(report_path)
        self.report_path.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        status: StrategyStatus,
        cycle_result: Dict[str, Any]
    ) -> str:
        """
        Generate daily incubation report.
        
        Args:
            status: Current strategy status
            cycle_result: Latest cycle results
        
        Returns:
            str: Path to report file
        """
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = self.report_path / f"{date_str}_incubation_{status.strategy_name}.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# Incubation Report - {status.strategy_name}\n")
            f.write(f"**Date**: {date_str}\n\n")
            
            f.write("## Current Status\n\n")
            f.write(f"- **State**: {status.state.value}\n")
            f.write(f"- **Days in State**: {status.days_in_state}\n")
            f.write(f"- **Version**: {status.version}\n")
            f.write(f"- **Last Transition**: {status.last_transition}\n\n")
            
            if 'transition_reason' in status.metadata:
                f.write(f"- **Transition Reason**: {status.metadata['transition_reason']}\n\n")
            
            # WFA metrics
            if 'wfa_metrics' in status.metadata:
                f.write("## WFA Metrics\n\n")
                wfa = status.metadata['wfa_metrics']
                for key, value in wfa.items():
                    if isinstance(value, float):
                        f.write(f"- **{key}**: {value:.4f}\n")
                    else:
                        f.write(f"- **{key}**: {value}\n")
                f.write("\n")
            
            # Paper metrics
            if 'paper_metrics' in status.metadata:
                f.write("## Paper Trading Metrics\n\n")
                paper = status.metadata['paper_metrics']
                for key, value in paper.items():
                    if isinstance(value, float):
                        f.write(f"- **{key}**: {value:.4f}\n")
                    else:
                        f.write(f"- **{key}**: {value}\n")
                f.write("\n")
            
            # Live metrics
            if 'live_metrics' in status.metadata:
                f.write("## Live Trading Metrics\n\n")
                live = status.metadata['live_metrics']
                for key, value in live.items():
                    if isinstance(value, float):
                        f.write(f"- **{key}**: {value:.4f}\n")
                    else:
                        f.write(f"- **{key}**: {value}\n")
                f.write("\n")
            
            # Health status
            if 'health_status' in status.metadata:
                f.write("## Health Status\n\n")
                health = status.metadata['health_status']
                f.write(f"- **Status**: {health.get('status', 'N/A')}\n")
                f.write(f"- **Details**: {health.get('details', 'N/A')}\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            self._write_recommendations(f, status)
        
        return str(report_file)
    
    def _write_recommendations(self, f, status: StrategyStatus):
        """Write recommendations based on state"""
        state = status.state.value
        
        if state == "research":
            f.write("- Complete research and run walk-forward analysis\n")
        elif state == "wfa_passed":
            f.write("- Review WFA results and promote to paper trading if criteria met\n")
        elif state == "paper_trading":
            f.write(f"- Continue monitoring ({status.days_in_state} days completed)\n")
            f.write("- Minimum 45 days required before live promotion\n")
        elif state == "live_trading":
            f.write("- ✅ Strategy is live - monitor daily\n")
            f.write("- Watch for drawdown and drift\n")
        elif state == "disabled":
            f.write("- ⚠️ Strategy is DISABLED\n")
            f.write("- Review failure reason and re-incubate if appropriate\n")


def generate_incubation_report(
    status: StrategyStatus,
    cycle_result: Dict[str, Any],
    report_path: str = "logs/incubation/"
) -> str:
    """
    Simple function to generate incubation report.
    
    Returns:
        str: Path to report file
    """
    reporter = IncubationReporter(report_path)
    return reporter.generate_report(status, cycle_result)

