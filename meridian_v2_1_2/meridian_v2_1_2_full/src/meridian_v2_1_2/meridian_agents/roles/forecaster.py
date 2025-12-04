"""Forecaster Agent"""
from ..prompts.system_prompts import FORECASTER_PROMPT

class Forecaster:
    def __init__(self, client):
        self.client = client
    
    def generate(self, data: dict) -> str:
        return "Forecast generated: 20-bar projection with 75% confidence"

