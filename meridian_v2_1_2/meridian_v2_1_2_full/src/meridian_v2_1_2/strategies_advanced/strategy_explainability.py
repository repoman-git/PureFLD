"""
Strategy Explainability (Scaffold)

Future: Natural language strategy explanations.

⚠️  STUB - Placeholder for AI explanation generation
"""

from typing import Dict, Any, List


def explain_strategy_decision(
    strategy_obj: Any,
    current_data: Any,
    signal: Dict[str, Any]
) -> str:
    """
    Generate natural language explanation of strategy decision.
    
    Future implementation will:
    - Explain WHY signal was generated
    - Detail which rules triggered
    - Describe market conditions
    - Provide reasoning chain
    
    Args:
        strategy_obj: Strategy instance
        current_data: Current market data
        signal: Generated signal
    
    Returns:
        Natural language explanation
    
    ⚠️  STUB - Returns placeholder
    """
    return "Strategy explanation not yet implemented (stub)."


def generate_rule_breakdown(strategy_name: str) -> List[str]:
    """
    Generate detailed breakdown of strategy rules.
    
    Future: Interactive rule explorer.
    
    Args:
        strategy_name: Strategy name
    
    Returns:
        List of rule descriptions
    
    ⚠️  STUB - Returns placeholders
    """
    return [
        f"Rule breakdown for {strategy_name} (stub)",
        "Entry rules: (not yet implemented)",
        "Exit rules: (not yet implemented)",
        "Risk management: (not yet implemented)"
    ]


