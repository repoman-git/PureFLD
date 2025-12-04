"""
Oversight Reporter for Meridian v2.1.2

Generates AI supervision reports.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def generate_oversight_report(
    oversight_results: Dict[str, Any],
    config
) -> Path:
    """
    Generate oversight report.
    
    Args:
        oversight_results: Oversight check results
        config: OversightConfig instance
    
    Returns:
        Path to report file
    """
    # Create report directory
    report_dir = Path(config.report_path)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = oversight_results.get('timestamp', datetime.now().isoformat())
    
    # Build report
    report_lines = []
    report_lines.append("# 🤖 STRATEGY OVERSIGHT AI REPORT")
    report_lines.append(f"\nTimestamp: {timestamp}")
    report_lines.append("\n---\n")
    
    # Status
    report_lines.append("## System Status")
    success = oversight_results.get('success', False)
    report_lines.append(f"- Check Status: {'✓' if success else '✗'}")
    
    # Anomaly Scores
    anomaly_scores = oversight_results.get('anomaly_scores', {})
    if anomaly_scores:
        report_lines.append("\n## Anomaly Scores")
        report_lines.append(f"- Strategy: {anomaly_scores.get('strategy', 0):.2f}")
        report_lines.append(f"- Execution: {anomaly_scores.get('execution', 0):.2f}")
        report_lines.append(f"- Shadow/Drift: {anomaly_scores.get('shadow', 0):.2f}")
        report_lines.append(f"- Portfolio: {anomaly_scores.get('portfolio', 0):.2f}")
        report_lines.append(f"- **Overall: {anomaly_scores.get('overall', 0):.2f}**")
    
    # Risk Assessment
    risk = oversight_results.get('risk_assessment', {})
    if risk:
        report_lines.append("\n## Risk Assessment")
        risk_level = risk.get('level', 'unknown').upper()
        risk_score = risk.get('score', 0)
        should_halt = risk.get('should_halt', False)
        
        # Add emoji indicators
        risk_emoji = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🟠',
            'CRITICAL': '🔴'
        }.get(risk_level, '⚪')
        
        report_lines.append(f"- Risk Level: {risk_emoji} **{risk_level}**")
        report_lines.append(f"- Risk Score: {risk_score:.2f}")
        
        if should_halt:
            report_lines.append("\n⚠️ **RECOMMENDATION: HALT TRADING** ⚠️")
        
        # Recommendations
        recs = risk.get('recommendations', [])
        if recs:
            report_lines.append("\n### Recommendations")
            for rec in recs:
                report_lines.append(f"- {rec}")
    
    # AI Advisories
    advisories = oversight_results.get('advisories', [])
    if advisories:
        report_lines.append("\n## 🤖 AI Advisor Messages")
        
        # Group by priority
        urgent = [a for a in advisories if a['priority'] == 'urgent']
        warning = [a for a in advisories if a['priority'] == 'warning']
        info = [a for a in advisories if a['priority'] == 'info']
        
        if urgent:
            report_lines.append("\n### 🚨 URGENT")
            for adv in urgent:
                report_lines.append(f"\n**{adv['category'].upper()}**: {adv['message']}")
                report_lines.append(f"*Action*: {adv['action']}")
        
        if warning:
            report_lines.append("\n### ⚠️ WARNINGS")
            for adv in warning:
                report_lines.append(f"\n**{adv['category'].upper()}**: {adv['message']}")
                report_lines.append(f"*Action*: {adv['action']}")
        
        if info:
            report_lines.append("\n### ℹ️ INFORMATION")
            for adv in info:
                report_lines.append(f"- {adv['message']}")
    
    # Behavioral Deviations
    deviations = oversight_results.get('behavioral_deviations', [])
    if deviations:
        report_lines.append("\n## Behavioral Deviations")
        for dev in deviations:
            report_lines.append(f"- {dev}")
    
    # Error
    if 'error' in oversight_results:
        report_lines.append(f"\n## ❌ ERROR")
        report_lines.append(f"```\n{oversight_results['error']}\n```")
    
    report_lines.append("\n---\n*End of Oversight Report*\n")
    
    # Write report
    timestamp_clean = timestamp.replace(':', '').replace('-', '')[:15]
    report_file = report_dir / f"OVERSIGHT_{timestamp_clean}.md"
    
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    return report_file


