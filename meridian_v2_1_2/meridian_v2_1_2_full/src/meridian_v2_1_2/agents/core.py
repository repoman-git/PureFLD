"""
AI Agent Core - Base Classes

Foundation for multi-AI agent research system.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentInsight:
    """Single insight from an AI agent"""
    agent_name: str
    category: str  # 'analysis', 'recommendation', 'warning', 'discovery'
    priority: str  # 'critical', 'high', 'medium', 'low'
    title: str
    content: str
    data: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ResearchAgent:
    """
    Base class for AI research agents.
    
    Each agent specializes in analyzing specific aspects of trading strategies.
    Currently rule-based, but designed for easy LLM integration.
    """
    
    def __init__(self, name: str, description: str, specialization: str):
        """
        Initialize research agent.
        
        Args:
            name: Agent name (e.g., "Cycle Analyst")
            description: What this agent does
            specialization: Area of expertise
        """
        self.name = name
        self.description = description
        self.specialization = specialization
        self.insights_generated = 0
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze input data and generate insights.
        
        This is the main method each agent must implement.
        
        Args:
            input_data: Dictionary containing backtest results, metrics, etc.
        
        Returns:
            Dictionary with:
                - insights: List of AgentInsight objects
                - recommendations: List of specific actions
                - summary: High-level summary string
        
        NOTE: Subclasses must override this method.
        """
        raise NotImplementedError("Subclasses must implement analyze()")
    
    def _create_insight(
        self,
        category: str,
        priority: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None
    ) -> AgentInsight:
        """Helper to create insights"""
        self.insights_generated += 1
        
        return AgentInsight(
            agent_name=self.name,
            category=category,
            priority=priority,
            title=title,
            content=content,
            data=data
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'name': self.name,
            'specialization': self.specialization,
            'insights_generated': self.insights_generated
        }
    
    def __repr__(self) -> str:
        return f"<ResearchAgent: {self.name} | {self.specialization}>"

