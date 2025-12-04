"""
Pairs Trading Dashboard

Interactive Streamlit dashboard for pairs trading analysis and monitoring.

Features:
- Pair selection and screening
- Divergence visualization
- Real-time spread monitoring
- Backtest results display
- Trade signal tracking
- Performance analytics

Pages:
1. Pair Screener: Find best pairs
2. Spread Monitor: Real-time divergence tracking
3. Backtest Results: Historical performance
4. Active Signals: Current opportunities

Author: Meridian Team
Date: December 4, 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .pairs_selector import PairsSelector, PairCandidate
from .divergence_detector import DivergenceDetector
from .pairs_strategy import PairsStrategy
from .pairs_backtest import PairsBacktester


class PairsDashboard:
    """
    Streamlit dashboard for pairs trading.
    
    Usage:
        >>> dashboard = PairsDashboard()
        >>> dashboard.run()  # Launches Streamlit app
    """
    
    def __init__(self):
        """Initialize dashboard components."""
        self.selector = PairsSelector(min_correlation=0.6)
        self.detector = DivergenceDetector(threshold_sigma=2.0)
        self.strategy = PairsStrategy(entry_threshold=2.0)
        self.backtester = PairsBacktester(initial_capital=100000)
    
    def run(self):
        """
        Main dashboard entry point.
        
        Call this function to render the dashboard.
        """
        st.set_page_config(
            page_title="Pairs Trading | Meridian",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("🔄 Pairs Trading Dashboard")
        st.markdown("**Cross-Market Arbitrage Engine** | Stage 1 of Roadmap")
        
        # Sidebar navigation
        page = st.sidebar.radio(
            "Navigation",
            ["Pair Screener", "Spread Monitor", "Backtest Results", "Active Signals"]
        )
        
        if page == "Pair Screener":
            self._render_pair_screener()
        elif page == "Spread Monitor":
            self._render_spread_monitor()
        elif page == "Backtest Results":
            self._render_backtest_results()
        elif page == "Active Signals":
            self._render_active_signals()
    
    def _render_pair_screener(self):
        """Render pair screening page."""
        st.header("📈 Pair Screener")
        st.markdown("Find tradable pairs based on cycle synchronization")
        
        # Input: Asset universe
        st.subheader("Asset Universe")
        
        col1, col2 = st.columns(2)
        
        with col1:
            assets_input = st.text_area(
                "Enter symbols (one per line)",
                value="GLD\nSLV\nTLT\nDXY\nGC=F\nSI=F",
                height=150
            )
        
        with col2:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365*2)
            )
            end_date = st.date_input(
                "End Date",
                value=datetime.now()
            )
            top_n = st.number_input("Top N Pairs", min_value=1, max_value=50, value=10)
        
        if st.button("🔍 Screen Pairs", type="primary"):
            assets = [a.strip() for a in assets_input.split('\n') if a.strip()]
            
            with st.spinner("Fetching data and analyzing pairs..."):
                # Fetch data
                price_dict = self._fetch_prices(assets, start_date, end_date)
                
                if not price_dict:
                    st.error("No valid data fetched. Check symbols.")
                    return
                
                # Select pairs
                pairs = self.selector.select_pairs(price_dict, top_n=top_n)
                
                if not pairs:
                    st.warning("No valid pairs found with current criteria.")
                    return
                
                # Display results
                st.success(f"Found {len(pairs)} tradable pairs")
                
                # Convert to DataFrame
                pairs_df = pd.DataFrame([
                    {
                        'Lead Asset': p.lead_asset,
                        'Lag Asset': p.lag_asset,
                        'Correlation': f"{p.correlation:.3f}",
                        'Lead/Lag (days)': p.lead_lag_days,
                        'Half Life (days)': f"{p.half_life:.1f}",
                        'Spread Vol': f"{p.spread_volatility:.2f}",
                        'Score': f"{p.score:.3f}"
                    }
                    for p in pairs
                ])
                
                st.dataframe(pairs_df, use_container_width=True)
                
                # Store in session state for other pages
                st.session_state['screened_pairs'] = pairs
                st.session_state['price_dict'] = price_dict
    
    def _render_spread_monitor(self):
        """Render spread monitoring page."""
        st.header("📊 Spread Monitor")
        st.markdown("Real-time divergence tracking for selected pairs")
        
        # Check if pairs are screened
        if 'screened_pairs' not in st.session_state:
            st.info("👈 Please screen pairs first in the Pair Screener")
            return
        
        pairs = st.session_state['screened_pairs']
        price_dict = st.session_state['price_dict']
        
        # Select pair to monitor
        pair_options = [f"{p.lead_asset}/{p.lag_asset}" for p in pairs]
        selected_pair_str = st.selectbox("Select Pair", pair_options)
        
        if not selected_pair_str:
            return
        
        # Find selected pair
        selected_idx = pair_options.index(selected_pair_str)
        selected_pair = pairs[selected_idx]
        
        # Display pair statistics
        stats = self.selector.get_pair_statistics(selected_pair, price_dict)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Correlation", f"{stats['correlation']:.3f}")
        col2.metric("Lead/Lag", f"{stats['lead_lag_days']} days")
        col3.metric("Half Life", f"{stats['half_life']:.1f} days")
        col4.metric("Score", f"{stats['score']:.3f}")
        
        # Detect divergences
        lead_prices = price_dict[selected_pair.lead_asset]
        lag_prices = price_dict[selected_pair.lag_asset]
        
        with st.spinner("Analyzing divergences..."):
            plot_data = self.detector.plot_divergence_history(
                lead_asset=selected_pair.lead_asset,
                lag_asset=selected_pair.lag_asset,
                lead_prices=lead_prices,
                lag_prices=lag_prices
            )
        
        # Plot spread and signals
        fig = self._plot_spread_analysis(plot_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Current divergence status
        current_div = self.detector.get_current_divergence(
            selected_pair.lead_asset,
            selected_pair.lag_asset,
            lead_prices,
            lag_prices
        )
        
        if current_div:
            st.subheader("🚨 Current Divergence")
            col1, col2, col3 = st.columns(3)
            col1.metric("Type", current_div.divergence_type.value.upper())
            col2.metric("Magnitude", f"{current_div.magnitude:.2f}σ")
            col3.metric("Confidence", f"{current_div.confidence:.1%}")
        else:
            st.info("No significant divergence detected currently")
    
    def _render_backtest_results(self):
        """Render backtest results page."""
        st.header("📉 Backtest Results")
        st.markdown("Historical performance of pairs trading strategy")
        
        # Check if pairs are screened
        if 'screened_pairs' not in st.session_state:
            st.info("👈 Please screen pairs first in the Pair Screener")
            return
        
        pairs = st.session_state['screened_pairs']
        price_dict = st.session_state['price_dict']
        
        # Select pair to backtest
        pair_options = [f"{p.lead_asset}/{p.lag_asset}" for p in pairs]
        selected_pair_str = st.selectbox("Select Pair", pair_options)
        
        if not selected_pair_str:
            return
        
        # Find selected pair
        selected_idx = pair_options.index(selected_pair_str)
        selected_pair = pairs[selected_idx]
        
        # Strategy parameters
        st.subheader("Strategy Parameters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            entry_thresh = st.slider("Entry Threshold (σ)", 1.0, 3.0, 2.0, 0.1)
        with col2:
            exit_thresh = st.slider("Exit Threshold (σ)", 0.0, 1.0, 0.5, 0.1)
        with col3:
            stop_loss = st.slider("Stop Loss (σ)", 3.0, 5.0, 4.0, 0.1)
        
        if st.button("🚀 Run Backtest", type="primary"):
            # Update strategy parameters
            strategy = PairsStrategy(
                entry_threshold=entry_thresh,
                exit_threshold=exit_thresh,
                stop_loss_threshold=stop_loss
            )
            
            lead_prices = price_dict[selected_pair.lead_asset]
            lag_prices = price_dict[selected_pair.lag_asset]
            
            with st.spinner("Running backtest..."):
                result = self.backtester.backtest(
                    pair_candidate=selected_pair,
                    strategy=strategy,
                    lead_prices=lead_prices,
                    lag_prices=lag_prices
                )
            
            # Display results
            if result.total_trades == 0:
                st.warning("No trades generated with these parameters")
                return
            
            st.success(f"Backtest complete: {result.total_trades} trades")
            
            # Performance metrics
            st.subheader("📊 Performance Metrics")
            summary = result.summary()
            
            cols = st.columns(5)
            metrics = list(summary.items())
            for i, (key, value) in enumerate(metrics[:5]):
                cols[i].metric(key, value)
            
            cols2 = st.columns(5)
            for i, (key, value) in enumerate(metrics[5:10]):
                cols2[i].metric(key, value)
            
            # Equity curve
            st.subheader("📈 Equity Curve")
            plot_data = self.backtester.plot_results(result)
            fig = self._plot_backtest_results(plot_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Trade list
            st.subheader("💼 Trade History")
            trades_df = pd.DataFrame([
                {
                    'Entry': t.entry_date.strftime('%Y-%m-%d'),
                    'Exit': t.exit_date.strftime('%Y-%m-%d'),
                    'Days': t.holding_days,
                    'Entry Spread': f"{t.entry_spread:.2f}",
                    'Exit Spread': f"{t.exit_spread:.2f}",
                    'PnL %': f"{t.pnl_net / self.backtester.initial_capital * 100:.2f}%",
                    'Exit Reason': t.exit_reason
                }
                for t in result.trades[-20:]  # Last 20 trades
            ])
            
            st.dataframe(trades_df, use_container_width=True)
    
    def _render_active_signals(self):
        """Render active trading signals page."""
        st.header("🎯 Active Signals")
        st.markdown("Current trading opportunities")
        
        # Check if pairs are screened
        if 'screened_pairs' not in st.session_state:
            st.info("👈 Please screen pairs first in the Pair Screener")
            return
        
        pairs = st.session_state['screened_pairs']
        price_dict = st.session_state['price_dict']
        
        st.subheader("Scanning all pairs for signals...")
        
        active_signals = []
        
        for pair in pairs:
            lead_prices = price_dict[pair.lead_asset]
            lag_prices = price_dict[pair.lag_asset]
            
            # Check current divergence
            current_div = self.detector.get_current_divergence(
                pair.lead_asset,
                pair.lag_asset,
                lead_prices,
                lag_prices
            )
            
            if current_div and current_div.confidence >= 0.7:
                active_signals.append({
                    'Pair': f"{pair.lead_asset}/{pair.lag_asset}",
                    'Type': current_div.divergence_type.value.upper(),
                    'Direction': current_div.direction.name,
                    'Magnitude': f"{current_div.magnitude:.2f}σ",
                    'Confidence': f"{current_div.confidence:.1%}",
                    'Timestamp': current_div.timestamp.strftime('%Y-%m-%d')
                })
        
        if active_signals:
            st.success(f"Found {len(active_signals)} active signals")
            signals_df = pd.DataFrame(active_signals)
            st.dataframe(signals_df, use_container_width=True)
        else:
            st.info("No active signals at the moment")
    
    def _fetch_prices(
        self,
        symbols: List[str],
        start_date,
        end_date
    ) -> Dict[str, pd.Series]:
        """Fetch price data for symbols."""
        price_dict = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                
                if len(hist) > 0:
                    price_dict[symbol] = hist['Close']
            except Exception as e:
                st.warning(f"Failed to fetch {symbol}: {e}")
        
        return price_dict
    
    def _plot_spread_analysis(self, plot_data: Dict) -> go.Figure:
        """Create spread analysis plot."""
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=('Spread Z-Score', 'Raw Spread'),
            vertical_spacing=0.1
        )
        
        # Z-score plot
        fig.add_trace(
            go.Scatter(
                x=plot_data['dates'],
                y=plot_data['spread_zscore'],
                mode='lines',
                name='Spread Z-Score',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        # Thresholds
        fig.add_hline(
            y=plot_data['upper_threshold'],
            line=dict(color='red', dash='dash'),
            row=1, col=1
        )
        fig.add_hline(
            y=-plot_data['upper_threshold'],
            line=dict(color='red', dash='dash'),
            row=1, col=1
        )
        fig.add_hline(y=0, line=dict(color='gray', dash='dot'), row=1, col=1)
        
        # Signal markers
        if plot_data['signal_dates']:
            fig.add_trace(
                go.Scatter(
                    x=plot_data['signal_dates'],
                    y=plot_data['signal_values'],
                    mode='markers',
                    name='Divergence Signals',
                    marker=dict(size=10, color='red', symbol='diamond')
                ),
                row=1, col=1
            )
        
        # Raw spread
        fig.add_trace(
            go.Scatter(
                x=plot_data['dates'],
                y=plot_data['spread'],
                mode='lines',
                name='Raw Spread',
                line=dict(color='green', width=1)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f"Spread Analysis: {plot_data['lead_asset']}/{plot_data['lag_asset']}",
            height=600,
            showlegend=True
        )
        
        return fig
    
    def _plot_backtest_results(self, plot_data: Dict) -> go.Figure:
        """Create backtest results plot."""
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=('Equity Curve', 'Drawdown'),
            vertical_spacing=0.1
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=plot_data['dates'],
                y=plot_data['equity'],
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Initial capital line
        fig.add_hline(
            y=plot_data['initial_capital'],
            line=dict(color='gray', dash='dash'),
            annotation_text='Initial Capital',
            row=1, col=1
        )
        
        # Entry markers
        valid_entries = [(d, e) for d, e in zip(plot_data['entry_dates'], plot_data['entry_equity']) if e is not None]
        if valid_entries:
            entry_dates, entry_equity = zip(*valid_entries)
            fig.add_trace(
                go.Scatter(
                    x=entry_dates,
                    y=entry_equity,
                    mode='markers',
                    name='Entry',
                    marker=dict(size=8, color='green', symbol='triangle-up')
                ),
                row=1, col=1
            )
        
        # Exit markers
        valid_exits = [(d, e) for d, e in zip(plot_data['exit_dates'], plot_data['exit_equity']) if e is not None]
        if valid_exits:
            exit_dates, exit_equity = zip(*valid_exits)
            fig.add_trace(
                go.Scatter(
                    x=exit_dates,
                    y=exit_equity,
                    mode='markers',
                    name='Exit',
                    marker=dict(size=8, color='red', symbol='triangle-down')
                ),
                row=1, col=1
            )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(
                x=plot_data['dates'],
                y=plot_data['drawdown'] * 100,
                mode='lines',
                name='Drawdown %',
                line=dict(color='red', width=1),
                fill='tozeroy'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Backtest Performance",
            height=700,
            showlegend=True
        )
        
        fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
        
        return fig


# Standalone function for running dashboard
def run_pairs_dashboard():
    """
    Run the pairs trading dashboard.
    
    Usage from command line:
        streamlit run pairs_dashboard.py
    """
    dashboard = PairsDashboard()
    dashboard.run()


# Entry point for Streamlit
if __name__ == "__main__":
    run_pairs_dashboard()

