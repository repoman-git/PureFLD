"""
Health Checks for Meridian v2.1.2

Orchestrates all health validation checks.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

from ..config import HealthConfig


@dataclass
class HealthStatus:
    """Health check status result"""
    status: str  # 'OK', 'WARN', 'FAIL'
    timestamp: datetime
    checks_passed: int
    checks_failed: int
    checks_warned: int
    details: Dict[str, str]
    actions_required: List[str]


def run_all_health_checks(
    eod_data: Dict,
    positions: Dict,
    orders: List,
    config: HealthConfig
) -> HealthStatus:
    """
    Run complete health check suite.
    
    Executes all validation checks and aggregates results.
    
    Args:
        eod_data: EOD market data
        positions: Current positions
        orders: Pending orders
        config: Health configuration
    
    Returns:
        HealthStatus: Aggregated health status
    """
    details = {}
    actions = []
    passed = 0
    failed = 0
    warned = 0
    
    # Check 1: Data integrity
    if len(eod_data) == 0:
        details['data'] = 'FAIL: No EOD data'
        failed += 1
        actions.append('Fetch EOD data')
    else:
        details['data'] = 'OK'
        passed += 1
    
    # Check 2: Positions
    if len(positions) == 0:
        details['positions'] = 'OK: Flat'
        passed += 1
    else:
        # Check exposure (placeholder)
        total_exposure = sum(abs(p) for p in positions.values())
        if total_exposure > config.max_gross_exposure:
            details['positions'] = f'WARN: High exposure ({total_exposure:.2f})'
            warned += 1
            actions.append('Review exposure')
        else:
            details['positions'] = 'OK'
            passed += 1
    
    # Check 3: Orders
    if len(orders) > config.max_order_age_days * 10:
        details['orders'] = f'WARN: Many orders ({len(orders)})'
        warned += 1
    else:
        details['orders'] = 'OK'
        passed += 1
    
    # Determine overall status
    if failed > 0:
        overall_status = 'FAIL'
    elif warned > 0:
        overall_status = 'WARN'
    else:
        overall_status = 'OK'
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(),
        checks_passed=passed,
        checks_failed=failed,
        checks_warned=warned,
        details=details,
        actions_required=actions
    )


