"""
Stream Reporter for Meridian v2.1.2

Generates streaming activity reports.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def generate_stream_report(
    stream_status: Dict[str, Any],
    event_summary: Dict[str, int],
    config
) -> Path:
    """
    Generate streaming report.
    
    Args:
        stream_status: Stream engine status
        event_summary: Event counts by type
        config: StreamerConfig instance
    
    Returns:
        Path to report file
    """
    # Create report directory
    report_dir = Path(config.log_path)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    
    # Build report
    report_lines = []
    report_lines.append("# 📡 DATA STREAMING REPORT")
    report_lines.append(f"\nTimestamp: {timestamp}")
    report_lines.append("\n---\n")
    
    # Status
    report_lines.append("## Stream Status")
    report_lines.append(f"- Running: {'✓' if stream_status.get('running') else '✗'}")
    report_lines.append(f"- Enabled: {'✓' if stream_status.get('enabled') else '✗'}")
    
    # Safety
    safety = stream_status.get('safety', {})
    if safety:
        report_lines.append("\n## Safety Status")
        report_lines.append(f"- Healthy: {'✓' if safety.get('healthy') else '✗'}")
        report_lines.append(f"- Paused: {'✓' if safety.get('paused') else '✗'}")
        
        failure_counts = safety.get('failure_counts', {})
        if failure_counts:
            report_lines.append("\n### Failure Counts")
            for source, count in failure_counts.items():
                report_lines.append(f"- {source}: {count}")
    
    # OpenBB
    openbb = stream_status.get('openbb', {})
    if openbb:
        report_lines.append("\n## OpenBB Streaming")
        report_lines.append(f"- Enabled: {'✓' if openbb.get('enabled') else '✗'}")
        report_lines.append(f"- Interval: {openbb.get('interval')}s")
    
    # Alpaca
    alpaca = stream_status.get('alpaca', {})
    if alpaca:
        report_lines.append("\n## Alpaca Streaming")
        report_lines.append(f"- Enabled: {'✓' if alpaca.get('enabled') else '✗'}")
        report_lines.append(f"- Interval: {alpaca.get('interval')}s")
    
    # Event Summary
    if event_summary:
        report_lines.append("\n## Event Summary")
        for event_type, count in event_summary.items():
            report_lines.append(f"- {event_type}: {count}")
    
    report_lines.append("\n---\n*End of Streaming Report*\n")
    
    # Write report
    timestamp_clean = timestamp.replace(':', '').replace('-', '')[:15]
    report_file = report_dir / f"STREAM_{timestamp_clean}.md"
    
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    return report_file

