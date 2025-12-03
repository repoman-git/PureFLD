"""
Health Reporter for Meridian v2.1.2

Generate daily health audit reports.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class HealthReporter:
    """
    Generates daily health audit reports.
    """
    
    def __init__(self, report_path: str = "logs/health/"):
        self.report_path = Path(report_path)
        self.report_path.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        health_status: Any,
        eod_results: Dict[str, Any]
    ) -> str:
        """
        Generate health report.
        
        Args:
            health_status: HealthStatus object
            eod_results: EOD cycle results
        
        Returns:
            str: Path to report file
        """
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = self.report_path / f"{date_str}_health_report.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# Meridian Health Report - {date_str}\n\n")
            f.write(f"**Status**: {health_status.status}\n\n")
            f.write(f"**Checks Passed**: {health_status.checks_passed}\n")
            f.write(f"**Checks Failed**: {health_status.checks_failed}\n")
            f.write(f"**Checks Warned**: {health_status.checks_warned}\n\n")
            
            f.write("## Details\n\n")
            for check, result in health_status.details.items():
                f.write(f"- **{check}**: {result}\n")
            
            if health_status.actions_required:
                f.write("\n## Actions Required\n\n")
                for action in health_status.actions_required:
                    f.write(f"- {action}\n")
        
        return str(report_file)


def generate_health_report(
    health_status: Any,
    eod_results: Dict,
    report_path: str = "logs/health/"
) -> str:
    """
    Simple function to generate health report.
    
    Returns:
        str: Path to report file
    """
    reporter = HealthReporter(report_path)
    return reporter.generate_report(health_status, eod_results)

