"""
AI Model Audit Profiles

Define audit personas for different AI models.
Each model has unique strengths for verification.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ModelProfile:
    """Profile for an AI model's audit capabilities"""
    model_name: str
    audit_persona: str
    strengths: List[str]
    focus_areas: List[str]
    verification_style: str
    prompt_prefix: str


# Claude Profile - Deep Epistemic Scrutiny
CLAUDE_PROFILE = ModelProfile(
    model_name="claude",
    audit_persona="Deep Epistemic Scrutiny",
    strengths=[
        "Logical consistency checking",
        "Identifying hidden assumptions",
        "Detecting circular reasoning",
        "Evaluating evidence quality"
    ],
    focus_areas=[
        "Architectural soundness",
        "Assumption validity",
        "Logical coherence",
        "Evidence gaps"
    ],
    verification_style="systematic_analysis",
    prompt_prefix="As a rigorous analytical auditor, examine this strategy critically..."
)

# Gemini Profile - Logic Tree Consistency
GEMINI_PROFILE = ModelProfile(
    model_name="gemini",
    audit_persona="Logic Tree Consistency Checker",
    strengths=[
        "Hierarchical reasoning validation",
        "Step-by-step verification",
        "Dependency chain analysis",
        "Consistency across layers"
    ],
    focus_areas=[
        "Logic flow validity",
        "Parameter interactions",
        "Constraint satisfaction",
        "Consistency checks"
    ],
    verification_style="structured_logic_tree",
    prompt_prefix="Verify the logical consistency and dependencies in this strategy..."
)

# Grok Profile - Adversarial Stress Testing
GROK_PROFILE = ModelProfile(
    model_name="grok",
    audit_persona="Adversarial Stress Tester",
    strengths=[
        "Finding edge cases",
        "Stress scenario generation",
        "Contrarian analysis",
        "Failure mode identification"
    ],
    focus_areas=[
        "Breaking assumptions",
        "Edge case hunting",
        "Failure scenarios",
        "Robustness gaps"
    ],
    verification_style="adversarial_probing",
    prompt_prefix="Challenge this strategy aggressively and find its weaknesses..."
)

# ChatGPT Profile - Structured Engineering Review
CHATGPT_PROFILE = ModelProfile(
    model_name="chatgpt",
    audit_persona="Structured Engineering Reviewer",
    strengths=[
        "Implementation feasibility",
        "Best practice validation",
        "Code quality assessment",
        "Integration checking"
    ],
    focus_areas=[
        "Implementation details",
        "Engineering standards",
        "Integration points",
        "Maintainability"
    ],
    verification_style="engineering_review",
    prompt_prefix="Review this strategy from an engineering perspective..."
)


def get_model_profile(model_name: str) -> ModelProfile:
    """
    Get audit profile for specified model.
    
    Args:
        model_name: Name of AI model
    
    Returns:
        ModelProfile for that model
    """
    profiles = {
        'claude': CLAUDE_PROFILE,
        'gemini': GEMINI_PROFILE,
        'grok': GROK_PROFILE,
        'chatgpt': CHATGPT_PROFILE
    }
    
    return profiles.get(model_name.lower(), CLAUDE_PROFILE)


def get_all_profiles() -> Dict[str, ModelProfile]:
    """Get all model profiles"""
    return {
        'claude': CLAUDE_PROFILE,
        'gemini': GEMINI_PROFILE,
        'grok': GROK_PROFILE,
        'chatgpt': CHATGPT_PROFILE
    }

