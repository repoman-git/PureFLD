"""
Live Trading Reports for Meridian v2.1.2

Daily trading activity reporting.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def generate_live_report(
    date_str: str,
    results: Dict[str, Any],
    config
) -> Path:
    """
    Generate live trading report.
    
    Args:
        date_str: Date string
        results: Live trading results
        config: LiveConfig instance
    
    Returns:
        Path to report file
    """
    # Create report directory
    report_dir = Path(config.report_path)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Build report
    report_lines = []
    report_lines.append(f"# LIVE TRADING REPORT - {date_str}")
    report_lines.append(f"\nGenerated: {datetime.now().isoformat()}")
    report_lines.append(f"\n⚠️  **LIVE MODE - REAL MONEY** ⚠️")
    report_lines.append("\n---\n")
    
    # Status
    report_lines.append("## Status")
    report_lines.append(f"- Success: {results.get('success', False)}")
    report_lines.append(f"- Heartbeat: {'✓' if results.get('heartbeat_ok') else '✗'}")
    report_lines.append(f"- Reconciliation: {'✓' if results.get('reconciliation_ok') else '✗'}")
    
    # Trades Executed
    report_lines.append("\n## Trades Executed")
    trades = results.get('trades_executed', [])
    
    if trades:
        for trade in trades:
            symbol = trade.get('symbol')
            side = trade.get('side')
            qty = trade.get('qty')
            result = trade.get('result', {})
            success = '✓' if result.get('success') else '✗'
            
            report_lines.append(f"- {symbol}: {side.upper()} {abs(qty):.2f} - {success}")
            
            if result.get('error'):
                report_lines.append(f"  Error: {result['error']}")
    else:
        report_lines.append("- No trades executed")
    
    # Rule Violations
    violations = results.get('violations', [])
    if violations:
        report_lines.append("\n## Rule Violations")
        for v in violations:
            report_lines.append(f"- [{v.get('severity', 'unknown').upper()}] {v.get('message', 'Unknown')}")
    
    # Safety Triggers
    triggers = results.get('safety_triggers', [])
    if triggers:
        report_lines.append("\n## ⚠️ Safety Triggers ⚠️")
        for t in triggers:
            msg = t.get('message', 'Unknown')
            severity = t.get('severity', 'unknown').upper()
            report_lines.append(f"- [{severity}] {msg}")
            
            if t.get('kill_switch_activated'):
                report_lines.append("  **🛑 KILL-SWITCH ACTIVATED 🛑**")
    
    # Reconciliation
    if 'drift_pct' in results:
        report_lines.append(f"\n## Reconciliation")
        report_lines.append(f"- Drift: {results['drift_pct']:.4%}")
    
    # Errors
    if 'error' in results:
        report_lines.append(f"\n## ❌ ERROR")
        report_lines.append(f"```\n{results['error']}\n```")
    
    report_lines.append("\n---\n*End of Live Trading Report*\n")
    
    # Write report
    report_file = report_dir / f"LIVE_{date_str.replace('-', '')}.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    return report_file

