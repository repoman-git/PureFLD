"""
Stress Test Reporter for Meridian v2.1.2

Generate comprehensive stress test reports.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from .stress_runner import StressTestResult


def generate_stress_report(
    results: List[StressTestResult],
    output_path: str
) -> Dict[str, str]:
    """
    Generate comprehensive stress test reports.
    
    Args:
        results: List of stress test results
        output_path: Output directory
    
    Returns:
        Dict of report paths
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate summary report
    summary_path = output_dir / "STRESS_SUMMARY.md"
    _generate_summary_report(results, summary_path)
    
    # Generate individual run reports
    run_reports = []
    for result in results:
        run_path = output_dir / f"STRESS_RUN_{result.run_id:03d}.md"
        _generate_run_report(result, run_path)
        run_reports.append(str(run_path))
    
    # Generate weakness analysis
    weakness_path = output_dir / "WEAKNESS_ANALYSIS.md"
    _generate_weakness_analysis(results, weakness_path)
    
    return {
        'summary': str(summary_path),
        'weakness_analysis': str(weakness_path),
        'run_reports': run_reports
    }


def _generate_summary_report(
    results: List[StressTestResult],
    output_path: Path
) -> None:
    """Generate summary report"""
    
    total_runs = len(results)
    completed = sum(1 for r in results if r.completed)
    crashed = sum(1 for r in results if r.crashed)
    kill_switches = sum(1 for r in results if r.kill_switch_triggered)
    
    # Scenario breakdown
    scenarios = {}
    for result in results:
        scenarios[result.scenario_name] = scenarios.get(result.scenario_name, 0) + 1
    
    # Weakness frequency
    weakness_counts = {}
    for result in results:
        for weakness in result.weaknesses:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
    
    with open(output_path, 'w') as f:
        f.write("# MERIDIAN v2.1.2 STRESS TEST SUMMARY\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Overall Results\n\n")
        f.write(f"- **Total Runs**: {total_runs}\n")
        f.write(f"- **Completed**: {completed} ({completed/total_runs*100:.1f}%)\n")
        f.write(f"- **Crashed**: {crashed} ({crashed/total_runs*100:.1f}%)\n")
        f.write(f"- **Kill Switches**: {kill_switches} ({kill_switches/total_runs*100:.1f}%)\n\n")
        
        f.write("## Scenario Breakdown\n\n")
        for scenario, count in sorted(scenarios.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{scenario}**: {count} runs\n")
        
        f.write("\n## Weakness Frequency\n\n")
        if weakness_counts:
            for weakness, count in sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{weakness}**: {count} occurrences ({count/total_runs*100:.1f}%)\n")
        else:
            f.write("No weaknesses detected ✅\n")
        
        f.write("\n## Performance Metrics\n\n")
        avg_equity = sum(r.final_equity for r in results if r.completed) / max(completed, 1)
        avg_dd = sum(r.max_drawdown for r in results if r.completed) / max(completed, 1)
        
        f.write(f"- **Average Final Equity**: ${avg_equity:,.2f}\n")
        f.write(f"- **Average Max Drawdown**: {avg_dd:.2%}\n")
        
        f.write("\n## Recommendation\n\n")
        if crashed / total_runs > 0.1:
            f.write("⚠️  **HIGH CRASH RATE** - System requires hardening\n")
        elif weakness_counts:
            f.write("⚠️  Weaknesses detected - review detailed analysis\n")
        else:
            f.write("✅ System demonstrated good resilience under stress\n")


def _generate_run_report(
    result: StressTestResult,
    output_path: Path
) -> None:
    """Generate individual run report"""
    
    with open(output_path, 'w') as f:
        f.write(f"# Stress Test Run {result.run_id}\n\n")
        
        f.write("## Scenario\n\n")
        f.write(f"- **Name**: {result.scenario_name}\n")
        f.write(f"- **Severity**: {result.severity:.2f}\n\n")
        
        f.write("## Injected Failures\n\n")
        if result.injected_failures:
            for failure in result.injected_failures:
                f.write(f"- {failure}\n")
        else:
            f.write("None\n")
        
        f.write("\n## System Behavior\n\n")
        f.write(f"- **Completed**: {'✅ Yes' if result.completed else '❌ No'}\n")
        f.write(f"- **Crashed**: {'❌ Yes' if result.crashed else '✅ No'}\n")
        f.write(f"- **Kill Switch**: {'⚠️  Triggered' if result.kill_switch_triggered else '✅ Not triggered'}\n\n")
        
        f.write("## Metrics\n\n")
        f.write(f"- **Final Equity**: ${result.final_equity:,.2f}\n")
        f.write(f"- **Max Drawdown**: {result.max_drawdown:.2%}\n")
        f.write(f"- **Position Drift**: {result.position_drift:.2%}\n")
        f.write(f"- **OMS Errors**: {result.oms_errors}\n")
        f.write(f"- **NaN Count**: {result.nan_count}\n\n")
        
        f.write("## Weaknesses Identified\n\n")
        if result.weaknesses:
            for weakness in result.weaknesses:
                f.write(f"- ⚠️  {weakness}\n")
        else:
            f.write("✅ No weaknesses detected\n")
        
        if result.error_messages:
            f.write("\n## Error Messages\n\n")
            for error in result.error_messages:
                f.write(f"```\n{error}\n```\n\n")


def _generate_weakness_analysis(
    results: List[StressTestResult],
    output_path: Path
) -> None:
    """Generate weakness analysis report"""
    
    # Categorize weaknesses
    critical = []
    high = []
    medium = []
    
    weakness_counts = {}
    for result in results:
        for weakness in result.weaknesses:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
    
    total_runs = len(results)
    
    for weakness, count in weakness_counts.items():
        frequency = count / total_runs
        
        if frequency > 0.3:
            critical.append((weakness, count, frequency))
        elif frequency > 0.15:
            high.append((weakness, count, frequency))
        else:
            medium.append((weakness, count, frequency))
    
    with open(output_path, 'w') as f:
        f.write("# WEAKNESS ANALYSIS\n\n")
        
        f.write("## Critical Weaknesses (>30% frequency)\n\n")
        if critical:
            for weakness, count, freq in sorted(critical, key=lambda x: x[2], reverse=True):
                f.write(f"### ❌ {weakness}\n\n")
                f.write(f"- **Frequency**: {freq:.1%} ({count}/{total_runs} runs)\n")
                f.write(f"- **Severity**: CRITICAL\n")
                f.write(f"- **Recommendation**: Immediate fix required\n\n")
        else:
            f.write("✅ None\n\n")
        
        f.write("## High Priority Weaknesses (15-30% frequency)\n\n")
        if high:
            for weakness, count, freq in sorted(high, key=lambda x: x[2], reverse=True):
                f.write(f"### ⚠️  {weakness}\n\n")
                f.write(f"- **Frequency**: {freq:.1%} ({count}/{total_runs} runs)\n")
                f.write(f"- **Severity**: HIGH\n")
                f.write(f"- **Recommendation**: Address in next development cycle\n\n")
        else:
            f.write("✅ None\n\n")
        
        f.write("## Medium Priority Weaknesses (<15% frequency)\n\n")
        if medium:
            for weakness, count, freq in sorted(medium, key=lambda x: x[2], reverse=True):
                f.write(f"### ℹ️  {weakness}\n\n")
                f.write(f"- **Frequency**: {freq:.1%} ({count}/{total_runs} runs)\n")
                f.write(f"- **Severity**: MEDIUM\n")
                f.write(f"- **Recommendation**: Monitor and address if frequency increases\n\n")
        else:
            f.write("✅ None\n\n")
        
        f.write("## Overall Assessment\n\n")
        if critical:
            f.write("⚠️  **CRITICAL** - System has critical weaknesses requiring immediate attention\n")
        elif high:
            f.write("⚠️  **MODERATE** - System has notable weaknesses requiring attention\n")
        elif medium:
            f.write("✅ **GOOD** - System shows good resilience with minor issues\n")
        else:
            f.write("✅ **EXCELLENT** - System demonstrates exceptional resilience\n")

