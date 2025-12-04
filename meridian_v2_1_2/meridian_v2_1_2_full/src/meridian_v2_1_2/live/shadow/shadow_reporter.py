"""
Shadow Reporter for Meridian v2.1.2

Generates shadow check reports.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def generate_shadow_report(
    timestamp: str,
    shadow_result: Dict[str, Any],
    config
) -> Path:
    """
    Generate shadow check report.
    
    Args:
        timestamp: Timestamp string
        shadow_result: Shadow check result
        config: ShadowConfig instance
    
    Returns:
        Path to report file
    """
    # Create report directory
    report_dir = Path(config.report_path)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Build report
    report_lines = []
    report_lines.append(f"# BROKER SHADOW CHECK REPORT")
    report_lines.append(f"\nTimestamp: {timestamp}")
    report_lines.append(f"Mode: {config.mode.upper()}")
    report_lines.append("\n---\n")
    
    # Status
    report_lines.append("## Status")
    drift_detected = shadow_result.get('drift_detected', False)
    drift_level = shadow_result.get('drift_level', 'none')
    
    status_emoji = '✓' if not drift_detected else '⚠️'
    report_lines.append(f"- Drift Detected: {status_emoji} {drift_detected}")
    report_lines.append(f"- Drift Level: {drift_level.upper()}")
    
    # Events
    events = shadow_result.get('events', [])
    if events:
        report_lines.append("\n## Events")
        for event in events:
            severity = event.get('severity', 'info').upper()
            message = event.get('message', 'Unknown')
            report_lines.append(f"- [{severity}] {message}")
    
    # Repairs
    repairs = shadow_result.get('repairs_applied', [])
    if repairs:
        report_lines.append("\n## Repairs Applied")
        for repair in repairs:
            repair_type = repair.get('type', 'unknown')
            symbol = repair.get('symbol', 'N/A')
            details = repair.get('details', {})
            report_lines.append(f"- {repair_type}: {symbol}")
            for key, value in details.items():
                report_lines.append(f"  {key}: {value}")
    
    # Warnings
    if drift_level == 'critical':
        report_lines.append("\n## ⚠️ CRITICAL WARNING ⚠️")
        report_lines.append("Critical drift detected. Trading should be halted until resolved.")
    
    # Error
    if 'error' in shadow_result:
        report_lines.append("\n## ❌ ERROR")
        report_lines.append(f"```\n{shadow_result['error']}\n```")
    
    report_lines.append("\n---\n*End of Shadow Check Report*\n")
    
    # Write report
    report_file = report_dir / f"SHADOW_{timestamp.replace(':', '').replace('-', '')[:15]}.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    return report_file


