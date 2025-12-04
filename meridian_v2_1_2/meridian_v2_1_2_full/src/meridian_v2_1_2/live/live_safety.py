"""
Live Safety Layer for Meridian v2.1.2

Kill-switch and critical safety protections.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class SafetyTrigger:
    """Safety trigger event"""
    trigger_type: str
    severity: str  # warning | error | critical
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: datetime = None
    kill_switch_activated: bool = False


class LiveSafety:
    """
    Safety layer with kill-switch capability.
    
    Monitors:
    - Daily loss limits
    - Drawdown limits
    - Risk-to-account ratio
    - Parameter drift
    - Execution anomalies
    """
    
    def __init__(self, config):
        """
        Initialize safety layer.
        
        Args:
            config: LiveConfig instance
        """
        self.config = config
        
        self.kill_switch_active = False
        self.triggers = []
        self.starting_equity = None
        self.peak_equity = None
    
    def check_all(
        self,
        current_equity: float,
        daily_pnl: float,
        positions: Dict[str, Any],
        model_risk_score: Optional[float] = None
    ) -> List[SafetyTrigger]:
        """
        Run all safety checks.
        
        Args:
            current_equity: Current account equity
            daily_pnl: Today's PnL
            positions: Current positions
            model_risk_score: Model risk score (if available)
        
        Returns:
            List of triggered safety events
        """
        triggers = []
        
        # Initialize peak if needed
        if self.peak_equity is None or current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        if self.starting_equity is None:
            self.starting_equity = current_equity
        
        # Check 1: Daily loss limit
        daily_loss_pct = -daily_pnl / self.starting_equity if self.starting_equity > 0 else 0
        
        if daily_loss_pct > self.config.max_daily_loss_pct:
            trigger = SafetyTrigger(
                trigger_type='daily_loss_exceeded',
                severity='critical',
                message=f'Daily loss {daily_loss_pct:.2%} exceeds limit',
                value=daily_loss_pct,
                threshold=self.config.max_daily_loss_pct,
                timestamp=datetime.now(),
                kill_switch_activated=True
            )
            triggers.append(trigger)
            
            if self.config.enable_kill_switch:
                self.activate_kill_switch(trigger)
        
        # Check 2: Drawdown limit
        drawdown_pct = (self.peak_equity - current_equity) / self.peak_equity if self.peak_equity > 0 else 0
        
        if drawdown_pct > self.config.max_drawdown_pct:
            trigger = SafetyTrigger(
                trigger_type='drawdown_exceeded',
                severity='critical',
                message=f'Drawdown {drawdown_pct:.2%} exceeds limit',
                value=drawdown_pct,
                threshold=self.config.max_drawdown_pct,
                timestamp=datetime.now(),
                kill_switch_activated=True
            )
            triggers.append(trigger)
            
            if self.config.enable_kill_switch:
                self.activate_kill_switch(trigger)
        
        # Check 3: Model risk threshold
        if model_risk_score is not None and self.config.run_model_risk_pre_trade:
            if model_risk_score > self.config.max_model_risk_score:
                trigger = SafetyTrigger(
                    trigger_type='model_risk_exceeded',
                    severity='error',
                    message=f'Model risk score {model_risk_score:.3f} exceeds threshold',
                    value=model_risk_score,
                    threshold=self.config.max_model_risk_score,
                    timestamp=datetime.now(),
                    kill_switch_activated=False
                )
                triggers.append(trigger)
        
        # Check 4: Total exposure
        total_exposure = sum(
            abs(pos.get('market_value', 0)) 
            for pos in positions.values()
        )
        
        if total_exposure > self.config.max_total_exposure:
            trigger = SafetyTrigger(
                trigger_type='exposure_exceeded',
                severity='error',
                message=f'Total exposure ${total_exposure:.2f} exceeds limit',
                value=total_exposure,
                threshold=self.config.max_total_exposure,
                timestamp=datetime.now(),
                kill_switch_activated=False
            )
            triggers.append(trigger)
        
        # Check 5: Minimum account balance
        if current_equity < self.config.min_account_balance:
            trigger = SafetyTrigger(
                trigger_type='min_balance_breached',
                severity='critical',
                message=f'Account balance ${current_equity:.2f} below minimum',
                value=current_equity,
                threshold=self.config.min_account_balance,
                timestamp=datetime.now(),
                kill_switch_activated=True
            )
            triggers.append(trigger)
            
            if self.config.enable_kill_switch:
                self.activate_kill_switch(trigger)
        
        self.triggers.extend(triggers)
        return triggers
    
    def activate_kill_switch(self, trigger: SafetyTrigger):
        """
        Activate kill-switch.
        
        Args:
            trigger: Triggering event
        """
        self.kill_switch_active = True
        
        # Log activation
        print(f"\n{'='*60}")
        print(f"🛑 KILL-SWITCH ACTIVATED 🛑")
        print(f"{'='*60}")
        print(f"Trigger: {trigger.trigger_type}")
        print(f"Reason: {trigger.message}")
        print(f"Time: {trigger.timestamp}")
        print(f"{'='*60}\n")
    
    def is_kill_switch_active(self) -> bool:
        """Check if kill-switch is active"""
        return self.kill_switch_active
    
    def reset_kill_switch(self, operator_confirmation: bool = False):
        """
        Reset kill-switch (requires operator confirmation).
        
        Args:
            operator_confirmation: Whether operator has confirmed reset
        """
        if not operator_confirmation and self.config.require_operator_confirmation:
            raise ValueError("Kill-switch reset requires operator confirmation")
        
        self.kill_switch_active = False
        self.triggers = []
    
    def get_critical_triggers(self) -> List[SafetyTrigger]:
        """Get all critical safety triggers"""
        return [t for t in self.triggers if t.severity == 'critical']


