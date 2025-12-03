"""
Trading Audit Orchestrator

Coordinates complete pre-trade validation:
- Pre-trade checks
- Risk limit verification
- Portfolio impact analysis
- Multi-AI review
- Final verdict generation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from .audit_pretrade import PreTradeAuditor, PreTradeCheck, CheckStatus
from .audit_risk import RiskLimitChecker, RiskViolation
from .audit_portfolio_impact import PortfolioImpactAnalyzer, ImpactAssessment
from .audit_ai_review import MultiAITradeReviewer, AITradeVerdict


@dataclass
class TradingAuditResult:
    """Complete trading audit result"""
    audit_id: str
    timestamp: str
    trade_intent: Dict[str, Any]
    
    # Pre-trade checks
    pretrade_checks: List[PreTradeCheck]
    pretrade_passed: bool
    
    # Risk violations
    risk_violations: List[RiskViolation]
    risk_passed: bool
    
    # Portfolio impact
    portfolio_impacts: List[ImpactAssessment]
    high_impact: bool
    
    # AI review
    ai_reviews: Dict[str, Any]
    ai_consensus: str
    ai_confidence: float
    
    # Final verdict
    final_status: str  # 'APPROVED', 'BLOCKED', 'WARNING'
    summary: str
    should_execute: bool
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self):
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)


class TradingAuditOrchestrator:
    """
    Orchestrates complete trading decision audit.
    
    Professional trading desk compliance system with:
    - Pre-trade validation
    - Risk limit checks
    - Portfolio impact analysis
    - Multi-AI consensus
    - Final go/no-go decision
    """
    
    def __init__(
        self,
        risk_config: Optional[Dict[str, Any]] = None,
        ai_models: Optional[List[str]] = None
    ):
        """
        Initialize trading audit orchestrator.
        
        Args:
            risk_config: Risk limit configuration
            ai_models: List of AI models to use for review
        """
        self.pretrade_auditor = PreTradeAuditor()
        self.risk_checker = RiskLimitChecker(risk_config)
        self.impact_analyzer = PortfolioImpactAnalyzer()
        self.ai_reviewer = MultiAITradeReviewer(ai_models)
        
        self.audits_performed = 0
    
    def audit_trade(
        self,
        trade_intent: Dict[str, Any],
        strategy_rules: Dict[str, Any],
        current_portfolio: Optional[Dict[str, Any]] = None,
        run_ai_review: bool = True
    ) -> TradingAuditResult:
        """
        Perform complete trading audit.
        
        Args:
            trade_intent: Proposed trade details:
                - symbol: Asset symbol (e.g., 'GLD', 'SPY')
                - direction: 'long' or 'short'
                - size: Position size as % of portfolio (e.g., 0.05 for 5%)
                - entry_price: Proposed entry price
                - stop_loss: Stop loss price
                - take_profit: Take profit price (optional)
                - signal_strength: Confidence in signal (0-1)
                - strategy_name: Strategy generating signal
            
            strategy_rules: Strategy configuration
            
            current_portfolio: Current portfolio state (optional)
            
            run_ai_review: Whether to run AI consensus review
        
        Returns:
            TradingAuditResult with complete audit
        
        Example:
            >>> trade = {
            ...     'symbol': 'GLD',
            ...     'direction': 'long',
            ...     'size': 0.05,
            ...     'entry_price': 180.0,
            ...     'stop_loss': 175.0,
            ...     'take_profit': 190.0,
            ...     'signal_strength': 0.75,
            ...     'strategy_name': 'FLD-ETF'
            ... }
            >>> orchestrator = TradingAuditOrchestrator()
            >>> result = orchestrator.audit_trade(trade, strategy_rules={})
            >>> print(f"Status: {result.final_status}")
            >>> print(f"Should execute: {result.should_execute}")
        """
        
        audit_id = f"trade_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Step 1: Pre-trade checks
        pretrade_checks = self.pretrade_auditor.audit_trade(
            trade_intent,
            strategy_rules,
            current_portfolio
        )
        
        pretrade_passed = all(
            check.status != CheckStatus.FAIL
            for check in pretrade_checks
        )
        
        # Step 2: Risk limit checks
        risk_violations = self.risk_checker.check_all_limits(
            trade_intent,
            current_portfolio
        )
        
        risk_passed = len([v for v in risk_violations if v.action == 'BLOCK']) == 0
        
        # Step 3: Portfolio impact
        portfolio_impacts = []
        high_impact = False
        
        if current_portfolio:
            portfolio_impacts = self.impact_analyzer.analyze_impact(
                trade_intent,
                current_portfolio
            )
            
            high_impact = any(
                impact.severity in ['critical', 'high']
                for impact in portfolio_impacts
            )
        
        # Step 4: Multi-AI review (optional, can be slow)
        ai_reviews = {}
        ai_consensus = 'NEUTRAL'
        ai_confidence = 50.0
        
        if run_ai_review:
            ai_reviews = self.ai_reviewer.review_trade(
                trade_intent,
                strategy_rules
            )
            ai_consensus = ai_reviews.get('consensus', 'NEUTRAL')
            ai_confidence = ai_reviews.get('confidence', 50.0)
        
        # Final verdict
        final_status, should_execute, summary = self._determine_final_verdict(
            pretrade_passed,
            risk_passed,
            high_impact,
            ai_consensus,
            ai_confidence,
            pretrade_checks,
            risk_violations
        )
        
        self.audits_performed += 1
        
        return TradingAuditResult(
            audit_id=audit_id,
            timestamp=datetime.now().isoformat(),
            trade_intent=trade_intent,
            pretrade_checks=pretrade_checks,
            pretrade_passed=pretrade_passed,
            risk_violations=risk_violations,
            risk_passed=risk_passed,
            portfolio_impacts=portfolio_impacts,
            high_impact=high_impact,
            ai_reviews=ai_reviews,
            ai_consensus=ai_consensus,
            ai_confidence=ai_confidence,
            final_status=final_status,
            summary=summary,
            should_execute=should_execute
        )
    
    def _determine_final_verdict(
        self,
        pretrade_passed: bool,
        risk_passed: bool,
        high_impact: bool,
        ai_consensus: str,
        ai_confidence: float,
        checks: List[PreTradeCheck],
        violations: List[RiskViolation]
    ) -> tuple[str, bool, str]:
        """Determine final trading verdict"""
        
        # Any critical violation = BLOCKED
        if not risk_passed:
            return (
                'BLOCKED',
                False,
                f"Trade BLOCKED: {len([v for v in violations if v.action == 'BLOCK'])} critical violations"
            )
        
        # Pre-trade checks failed
        if not pretrade_passed:
            failed_checks = [c for c in checks if c.status == CheckStatus.FAIL]
            return (
                'BLOCKED',
                False,
                f"Trade BLOCKED: {len(failed_checks)} pre-trade check failures"
            )
        
        # AI consensus rejects
        if ai_consensus == 'REJECT':
            return (
                'WARNING',
                False,
                f"AI consensus REJECTS trade (confidence: {ai_confidence:.0f}%)"
            )
        
        # High portfolio impact
        if high_impact:
            return (
                'WARNING',
                False,
                "Trade creates HIGH portfolio impact - proceed with caution"
            )
        
        # Any warnings?
        warnings = [c for c in checks if c.status == CheckStatus.WARNING]
        if warnings or len(violations) > 0:
            return (
                'WARNING',
                True,
                f"Trade APPROVED with {len(warnings)} warnings"
            )
        
        # All clear
        return (
            'APPROVED',
            True,
            "Trade APPROVED - all checks passed"
        )

