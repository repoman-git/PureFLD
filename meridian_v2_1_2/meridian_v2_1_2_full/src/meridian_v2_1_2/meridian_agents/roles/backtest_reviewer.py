"""Backtest Reviewer Agent"""
from ..prompts.system_prompts import BACKTEST_REVIEW_PROMPT

class BacktestReviewer:
    def __init__(self, client):
        self.client = client
    
    def review_strategy(self, report: dict) -> str:
        return "Backtest review: Strong performance in cyclical regimes, avoid trending periods"

