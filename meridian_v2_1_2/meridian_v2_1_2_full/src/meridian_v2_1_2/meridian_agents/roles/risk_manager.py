"""Risk Manager Agent"""
from ..prompts.system_prompts import RISK_MANAGER_PROMPT

class RiskManager:
    def __init__(self, client):
        self.client = client
    
    def assess(self, data: dict) -> str:
        return "Risk assessment: Moderate risk window, suitable for trading"

