"""
GPT-Based Strategy Explainer

Converts technical trading signals into human-readable narratives.

Features:
- Reads trades (entries, exits, reversals)
- Reads strategy logic (FLD, VTL, phasing, forecast, harmonics)
- Writes natural-language explanations
- Multiple tone options (institutional PM, quant analyst, retail)
- Risk justification
- "What changed?" analysis

This is what hedge-fund PMs expect from quant teams:
"Explain the trade in English, not math."

⚠️  EXPERIMENTAL - Requires OpenAI API key
"""

from typing import Dict, Any, Optional


class StrategyExplainer:
    """
    Turns technical strategy events into human-readable
    narrative explanations using GPT.
    
    ⚠️  Requires OpenAI API key
    """

    def __init__(self, client=None, model="gpt-4o-mini"):
        """
        client = OpenAI client instance (or ChatGPT client)
        model = OpenAI model to use
        """
        self.client = client
        self.model = model
        
        if self.client is None:
            print("⚠️  Warning: No OpenAI client provided. Explainer in stub mode.")

    def explain_trade(
        self,
        trade_event: Dict[str, Any],
        context: Dict[str, Any],
        tone: str = "institutional"
    ) -> str:
        """
        Explain a trade in natural language.
        
        Args:
            trade_event: Trade details
                {
                    "timestamp": "...",
                    "type": "LONG_ENTRY",
                    "price": 2374.50,
                    "symbol": "GLD"
                }
            
            context: Strategy context
                {
                    "phase": 0.18,
                    "vtl_signal": True,
                    "fld_cross": True,
                    "forecast_bias": "UP",
                    "cycle_cluster": [40, 80, 160],
                    "harmonics": {40: [...], ...}
                }
            
            tone: 'institutional', 'quant', 'retail', 'coach'
        
        Returns:
            Natural language explanation
        
        ⚠️  EXPERIMENTAL - Requires OpenAI API key
        """
        
        if self.client is None:
            return self._stub_explanation(trade_event, context)
        
        prompt = f"""
        You are an expert quant and cycle analyst. Explain the following trade
        in clear, human-readable form with {tone} tone.

        TRADE:
        {trade_event}

        CONTEXT:
        {context}

        Your explanation must include:
        - Why the trade triggered
        - How cycle structure (phase, trough/peak proximity) influenced the signal
        - Any VTL or FLD confirmation
        - Harmonic or dominant cycle evidence
        - Forecast bias (AI ensemble)
        - Risk framing (what would invalidate the trade)
        - A simple takeaway

        Return the explanation as a concise paragraph.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating explanation: {e}"

    def explain_backtest(
        self,
        signals: Any,
        equity_curve: Any,
        strategy_name: str = "Cycle Strategy"
    ) -> str:
        """
        Provide narrative summary for entire strategy performance.
        
        Args:
            signals: Strategy signals series
            equity_curve: Equity curve series
            strategy_name: Name of strategy
        
        Returns:
            PM-ready summary narrative
        
        ⚠️  EXPERIMENTAL - Requires OpenAI API key
        """
        
        if self.client is None:
            return self._stub_backtest_explanation(signals, equity_curve, strategy_name)
        
        cagr = equity_curve.iloc[-1]**(252/len(equity_curve))-1 if len(equity_curve) > 0 else 0
        max_dd = (equity_curve/equity_curve.cummax()-1).min() if len(equity_curve) > 0 else 0
        
        prompt = f"""
        Summarize the '{strategy_name}' performance for a portfolio manager.

        RECENT SIGNALS:
        {signals.tail(20)}

        PERFORMANCE METRICS:
        - CAGR: {cagr:.3f}
        - Max Drawdown: {max_dd:.3f}

        Highlight:
        - Why the strategy works
        - When it struggles
        - How cycle conditions influence edge
        - Strength of FLD/VTL confirmation
        - How the AI forecaster adds value
        - Clear PM-ready takeaway

        Write in professional institutional tone.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating explanation: {e}"
    
    def _stub_explanation(self, trade_event: Dict, context: Dict) -> str:
        """Stub explanation when no GPT client available"""
        return f"""
        **Trade Explanation (Stub Mode - Add OpenAI key for full analysis)**
        
        Trade: {trade_event.get('type', 'UNKNOWN')} at ${trade_event.get('price', 0):.2f}
        
        Cycle Context:
        - Phase: {context.get('phase', 'N/A')}
        - FLD Cross: {'Yes' if context.get('fld_cross') else 'No'}
        - VTL Signal: {'Yes' if context.get('vtl_signal') else 'No'}
        - Forecast Bias: {context.get('forecast_bias', 'N/A')}
        
        Add OpenAI API key to get detailed natural-language explanations.
        """
    
    def _stub_backtest_explanation(self, signals, equity_curve, strategy_name) -> str:
        """Stub backtest summary when no GPT client available"""
        try:
            cagr = equity_curve.iloc[-1]**(252/len(equity_curve))-1 if len(equity_curve) > 0 else 0
            max_dd = (equity_curve/equity_curve.cummax()-1).min() if len(equity_curve) > 0 else 0
            
            return f"""
            **Strategy Summary (Stub Mode - Add OpenAI key for detailed analysis)**
            
            Strategy: {strategy_name}
            CAGR: {cagr:.2%}
            Max Drawdown: {max_dd:.2%}
            
            Add OpenAI API key to get PM-ready narrative summaries.
            """
        except:
            return "Strategy summary unavailable (add OpenAI key for analysis)"


