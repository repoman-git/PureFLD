"""Strategy Writer Agent"""
from ..prompts.system_prompts import STRATEGY_WRITER_PROMPT

class StrategyWriter:
    def __init__(self, client):
        self.client = client
    
    def explain(self, report: dict) -> str:
        return "Strategy explanation: Cycle-confirmed entry with regime support"

