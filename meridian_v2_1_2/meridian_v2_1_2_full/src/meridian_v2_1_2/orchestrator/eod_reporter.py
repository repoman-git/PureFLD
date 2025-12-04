"""
EOD Reporter for Meridian v2.1.2

Generates daily trading reports.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def generate_eod_report(
    date_str: str,
    results: Dict[str, Any],
    config
) -> Path:
    """
    Generate EOD report.
    
    Args:
        date_str: Date string
        results: EOD results dict
        config: Configuration
    
    Returns:
        Path to report file
    """
    # Create report directory
    report_dir = Path(config.eod.report_path if hasattr(config, 'eod') else "logs/eod/")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Build report
    report_lines = []
    report_lines.append(f"# EOD TRADING REPORT - {date_str}")
    report_lines.append(f"\nGenerated: {datetime.now().isoformat()}")
    report_lines.append(f"\nMode: {config.eod.mode if hasattr(config, 'eod') else 'unknown'}")
    report_lines.append("\n---\n")
    
    # Status
    report_lines.append("## Status")
    report_lines.append(f"- Success: {results.get('success', False)}")
    report_lines.append(f"- State Sequence: {' → '.join(results.get('state_sequence', []))}")
    
    # Violations
    if results.get('violations'):
        report_lines.append("\n## Safety Violations")
        for v in results['violations']:
            report_lines.append(f"- [{v.get('severity', 'unknown').upper()}] {v.get('message', 'Unknown')}")
    
    # Signals
    report_lines.append("\n## Signals")
    signals = results.get('signals', {})
    if signals:
        for symbol, signal in signals.items():
            report_lines.append(f"- {symbol}: {signal:.4f}")
    else:
        report_lines.append("- No signals generated")
    
    # Positions
    report_lines.append("\n## Positions")
    positions = results.get('positions', {})
    if positions:
        for symbol, pos in positions.items():
            qty = pos.get('qty', 0)
            mv = pos.get('market_value', 0)
            report_lines.append(f"- {symbol}: {qty:.2f} units (${mv:.2f})")
    else:
        report_lines.append("- No positions")
    
    # Performance
    report_lines.append("\n## Performance")
    report_lines.append(f"- Daily PnL: ${results.get('pnl', 0):.2f}")
    report_lines.append(f"- Total Equity: ${results.get('equity', 0):.2f}")
    
    # Model Risk
    if 'model_risk_score' in results:
        report_lines.append(f"\n## Model Risk Score: {results['model_risk_score']:.3f}")
    
    # Errors
    if 'error' in results:
        report_lines.append(f"\n## ERROR\n```\n{results['error']}\n```")
    
    report_lines.append("\n---\n*End of Report*\n")
    
    # Write report
    report_file = report_dir / f"EOD_{date_str.replace('-', '')}.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    return report_file


