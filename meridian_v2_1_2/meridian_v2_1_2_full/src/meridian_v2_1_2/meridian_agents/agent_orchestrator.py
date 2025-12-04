"""
Agent Orchestrator - The Meridian Brain

Coordinates multiple AI agents to analyze and manage the trading system.

Author: Meridian Team
Date: December 4, 2025
"""

import json
from typing import Dict, Optional, Any
from .roles.cycle_analyst import CycleAnalyst
from .roles.harmonic_specialist import HarmonicSpecialist
from .roles.forecaster import Forecaster
from .roles.intermarket_analyst import IntermarketAnalyst
from .roles.risk_manager import RiskManager
from .roles.strategy_writer import StrategyWriter
from .roles.backtest_reviewer import BacktestReviewer
from .roles.execution_monitor import ExecutionMonitor


class AgentOrchestrator:
    """
    Coordinates multiple AI agents for semi-autonomous operation.
    
    This orchestrator runs the complete Meridian pipeline using specialized
    AI agents for each domain, creating a self-analyzing trading system.
    
    Example:
        >>> from openai import OpenAI
        >>> 
        >>> client = OpenAI()
        >>> orchestrator = AgentOrchestrator(llm_client=client)
        >>> 
        >>> daily_report = orchestrator.run_daily_pipeline({
        ...     "price": price_data,
        ...     "phasing": phasing_results,
        ...     "harmonics": harmonics_results
        ... })
        >>> 
        >>> print(daily_report['strategy_notes'])
    """
    
    def __init__(self, llm_client: Any):
        """
        Initialize orchestrator with LLM client.
        
        Args:
            llm_client: OpenAI, Anthropic, or compatible client
        """
        self.client = llm_client
        
        # Initialize specialized agents
        self.cycle_analyst = CycleAnalyst(llm_client)
        self.harmonic_specialist = HarmonicSpecialist(llm_client)
        self.forecaster = Forecaster(llm_client)
        self.intermarket_analyst = IntermarketAnalyst(llm_client)
        self.risk_manager = RiskManager(llm_client)
        self.strategy_writer = StrategyWriter(llm_client)
        self.backtest_reviewer = BacktestReviewer(llm_client)
        self.execution_monitor = ExecutionMonitor(llm_client)
    
    def run_daily_pipeline(self, data: Dict) -> Dict:
        """
        Run complete daily analysis pipeline.
        
        Args:
            data: Dictionary with price, phasing, harmonics, etc.
            
        Returns:
            Comprehensive report from all agents
        """
        report = {}
        
        print("🔄 Running Meridian AI Pipeline...")
        
        # Phase 1: Analysis
        print("  → Cycle Analyst analyzing...")
        report["cycle_analysis"] = self.cycle_analyst.analyze(data)
        
        print("  → Harmonic Specialist scanning...")
        report["harmonic_analysis"] = self.harmonic_specialist.scan(data)
        
        print("  → Forecaster generating predictions...")
        report["forecast"] = self.forecaster.generate(data)
        
        print("  → Intermarket Analyst evaluating...")
        report["intermarket"] = self.intermarket_analyst.evaluate(data)
        
        # Phase 2: Risk & Strategy
        print("  → Risk Manager assessing...")
        report["risk_assessment"] = self.risk_manager.assess(data)
        
        print("  → Strategy Writer explaining...")
        report["strategy_notes"] = self.strategy_writer.explain(report)
        
        # Phase 3: Review
        print("  → Backtest Reviewer critiquing...")
        report["backtest_review"] = self.backtest_reviewer.review_strategy(report)
        
        # Phase 4: Execution
        print("  → Execution Monitor checking status...")
        report["execution_status"] = self.execution_monitor.status()
        
        print("✅ Pipeline complete!")
        
        return report
    
    def quick_analysis(self, data: Dict) -> str:
        """
        Quick analysis using primary agents only.
        
        Args:
            data: Market data
            
        Returns:
            Summary string
        """
        cycle = self.cycle_analyst.analyze(data)
        risk = self.risk_manager.assess(data)
        
        summary = f"""
        Cycle Analysis: {cycle}
        Risk Assessment: {risk}
        """
        
        return summary
    
    def generate_trade_explanation(self, signal_data: Dict) -> str:
        """
        Generate natural language explanation for a trade signal.
        
        Args:
            signal_data: Signal details
            
        Returns:
            Human-readable explanation
        """
        return self.strategy_writer.explain(signal_data)

