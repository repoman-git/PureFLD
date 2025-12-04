"""
Cycle Regime Dashboard (Stage 2)

Interactive Streamlit dashboard for regime analysis and monitoring.

Features:
- Real-time regime classification
- Historical regime distribution
- Feature importance visualization
- Regime performance analysis
- Strategy filtering demonstration

Author: Meridian Team
Date: December 4, 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Optional

from .cycle_regime_classifier import CycleRegimeClassifier, RegimeType
from .regime_filter import RegimeFilter


class RegimeDashboard:
    """
    Streamlit dashboard for regime analysis.
    
    Usage:
        >>> dashboard = RegimeDashboard()
        >>> dashboard.run()
    """
    
    def __init__(self):
        """Initialize dashboard"""
        self.classifier = None
        self.regime_filter = None
    
    def run(self):
        """Main dashboard entry point"""
        st.set_page_config(
            page_title="Cycle Regime Classifier | Meridian",
            page_icon="🔮",
            layout="wide"
        )
        
        st.title("🔮 Cycle Regime Classifier")
        st.markdown("**Stage 2:** ML-powered market regime detection for context-aware trading")
        
        # Sidebar
        page = st.sidebar.radio(
            "Navigation",
            ["Regime Analysis", "Model Training", "Strategy Filter", "Performance"]
        )
        
        if page == "Regime Analysis":
            self._render_regime_analysis()
        elif page == "Model Training":
            self._render_model_training()
        elif page == "Strategy Filter":
            self._render_strategy_filter()
        elif page == "Performance":
            self._render_performance()
    
    def _render_regime_analysis(self):
        """Render regime analysis page"""
        st.header("📊 Regime Analysis")
        st.markdown("Analyze current and historical market regimes")
        
        # Input section
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Symbol", value="SPY")
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365*2)
            )
        
        with col2:
            model_type = st.selectbox(
                "Model Type",
                ["random_forest", "gradient_boost", "xgboost"]
            )
            n_estimators = st.slider("N Estimators", 50, 500, 300, 50)
        
        if st.button("🔍 Analyze Regime", type="primary"):
            with st.spinner("Fetching data and analyzing..."):
                # Fetch data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=datetime.now())
                
                if len(hist) == 0:
                    st.error("No data fetched. Check symbol.")
                    return
                
                prices = hist['Close']
                
                # Initialize classifier
                classifier = CycleRegimeClassifier(
                    model_type=model_type,
                    n_estimators=n_estimators
                )
                
                # Extract features (basic only, no cycle data for demo)
                features = classifier.extract_features(prices)
                
                # Label regimes
                labels = classifier.label_regimes(features)
                
                # Train model
                metrics = classifier.train(features, labels, verbose=False)
                
                # Predict
                predictions = classifier.predict(features)
                
                # Store in session state
                st.session_state['classifier'] = classifier
                st.session_state['predictions'] = predictions
                st.session_state['features'] = features
                st.session_state['prices'] = prices
                
                # Display results
                st.success(f"✅ Analysis complete: {len(predictions)} periods analyzed")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Train Accuracy", f"{metrics['train_accuracy']:.1%}")
                col2.metric("Test Accuracy", f"{metrics['test_accuracy']:.1%}")
                
                current_regime = predictions['regime_name'].iloc[-1]
                current_suitability = predictions['trade_suitability'].iloc[-1]
                col3.metric("Current Regime", current_regime)
                col4.metric("Trade Suitability", f"{current_suitability:.0%}")
                
                # Plot
                fig = self._plot_regime_analysis(prices, predictions)
                st.plotly_chart(fig, use_container_width=True)
                
                # Regime distribution
                st.subheader("📊 Regime Distribution")
                regime_counts = predictions['regime_name'].value_counts()
                
                fig_dist = go.Figure(data=[
                    go.Bar(x=regime_counts.index, y=regime_counts.values)
                ])
                fig_dist.update_layout(
                    title="Regime Frequency",
                    xaxis_title="Regime",
                    yaxis_title="Count",
                    height=400
                )
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Feature importance
                if hasattr(classifier, 'get_feature_importance'):
                    st.subheader("🎯 Feature Importance")
                    importance = classifier.get_feature_importance(top_n=10)
                    
                    fig_imp = go.Figure(data=[
                        go.Bar(
                            x=importance['importance'],
                            y=importance['feature'],
                            orientation='h'
                        )
                    ])
                    fig_imp.update_layout(
                        title="Top 10 Features",
                        xaxis_title="Importance",
                        height=400
                    )
                    st.plotly_chart(fig_imp, use_container_width=True)
    
    def _render_model_training(self):
        """Render model training page"""
        st.header("🎓 Model Training")
        st.markdown("Train and evaluate regime classification models")
        
        st.info("💡 Upload your own data or use the Regime Analysis page to train a model")
        
        # Check if model exists in session
        if 'classifier' in st.session_state:
            classifier = st.session_state['classifier']
            
            st.success("✅ Model loaded from session")
            
            # Model info
            col1, col2 = st.columns(2)
            col1.metric("Model Type", classifier.model_type)
            col2.metric("Status", "Trained" if classifier.is_trained else "Not Trained")
            
            # Save/load
            st.subheader("💾 Save/Load Model")
            
            col1, col2 = st.columns(2)
            
            with col1:
                save_path = st.text_input("Save Path", value="models/regime_classifier.pkl")
                if st.button("💾 Save Model"):
                    try:
                        classifier.save(save_path)
                        st.success(f"Model saved to {save_path}")
                    except Exception as e:
                        st.error(f"Error saving: {e}")
            
            with col2:
                load_path = st.text_input("Load Path", value="models/regime_classifier.pkl")
                if st.button("📂 Load Model"):
                    try:
                        classifier.load(load_path)
                        st.success(f"Model loaded from {load_path}")
                        st.session_state['classifier'] = classifier
                    except Exception as e:
                        st.error(f"Error loading: {e}")
        else:
            st.warning("No model in session. Use Regime Analysis to train a model first.")
    
    def _render_strategy_filter(self):
        """Render strategy filter demonstration"""
        st.header("🎯 Strategy Filter")
        st.markdown("Demonstrate regime-aware signal filtering")
        
        # Check for regime predictions
        if 'predictions' not in st.session_state:
            st.warning("👈 Run Regime Analysis first to see filtering in action")
            return
        
        predictions = st.session_state['predictions']
        prices = st.session_state['prices']
        
        st.success("✅ Using regime predictions from analysis")
        
        # Filter settings
        col1, col2 = st.columns(2)
        
        with col1:
            min_suitability = st.slider(
                "Minimum Trade Suitability",
                0.0, 1.0, 0.6, 0.1
            )
        
        with col2:
            min_confidence = st.slider(
                "Minimum Regime Confidence",
                0.0, 1.0, 0.6, 0.1
            )
        
        # Create regime filter
        regime_filter = RegimeFilter(min_confidence=min_confidence)
        
        # Generate dummy signals (simple SMA crossover)
        sma_fast = prices.rolling(20).mean()
        sma_slow = prices.rolling(60).mean()
        
        signals = pd.DataFrame(index=prices.index)
        signals['signal'] = 0
        signals.loc[sma_fast > sma_slow, 'signal'] = 1
        signals.loc[sma_fast < sma_slow, 'signal'] = -1
        
        # Filter signals
        filtered_signals = regime_filter.filter_signals(
            signals=signals,
            regime_predictions=predictions,
            min_suitability=min_suitability
        )
        
        # Plot comparison
        fig = self._plot_signal_comparison(prices, signals, filtered_signals)
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.subheader("📊 Signal Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        original_signals = (signals['signal'] != 0).sum()
        filtered_signals_count = (filtered_signals['signal'] != 0).sum()
        reduction = (1 - filtered_signals_count / original_signals) * 100 if original_signals > 0 else 0
        
        col1.metric("Original Signals", original_signals)
        col2.metric("Filtered Signals", filtered_signals_count)
        col3.metric("Reduction", f"{reduction:.1f}%")
        
        # Show regime filtering breakdown
        st.subheader("🔍 Filtering Breakdown")
        
        filter_stats = predictions.groupby('regime_name').agg({
            'trade_suitability': 'mean',
            'regime_confidence': 'mean'
        }).round(3)
        
        # Add signal counts
        for regime in filter_stats.index:
            regime_mask = filtered_signals['regime_name'] == regime
            filter_stats.loc[regime, 'signals_allowed'] = (
                filtered_signals.loc[regime_mask, 'signal'] != 0
            ).sum()
        
        st.dataframe(filter_stats, use_container_width=True)
    
    def _render_performance(self):
        """Render performance analysis"""
        st.header("📈 Performance Analysis")
        st.markdown("Compare performance with and without regime filtering")
        
        if 'predictions' not in st.session_state:
            st.warning("👈 Run Regime Analysis first")
            return
        
        st.info("💡 Performance analysis coming soon! Integrate with backtest engine for full metrics.")
    
    def _plot_regime_analysis(
        self,
        prices: pd.Series,
        predictions: pd.DataFrame
    ) -> go.Figure:
        """Plot regime analysis"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            subplot_titles=[
                "Price",
                "Regime Classification",
                "Trade Suitability & Confidence"
            ],
            vertical_spacing=0.08,
            row_heights=[0.4, 0.3, 0.3]
        )
        
        # Price with regime background colors
        fig.add_trace(
            go.Scatter(
                x=prices.index,
                y=prices.values,
                mode='lines',
                name='Price',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Regime classification
        regime_colors = {
            'TRENDING': 'gray',
            'CYCLICAL': 'green',
            'VOLATILE': 'red',
            'COMPRESSED': 'yellow',
            'RESETTING': 'orange'
        }
        
        fig.add_trace(
            go.Scatter(
                x=predictions.index,
                y=predictions['regime'],
                mode='markers',
                name='Regime',
                marker=dict(
                    size=8,
                    color=[regime_colors.get(r, 'gray') for r in predictions['regime_name']],
                    line=dict(width=1, color='white')
                ),
                text=predictions['regime_name'],
                hovertemplate='%{text}<br>Confidence: %{customdata:.2f}',
                customdata=predictions['regime_confidence']
            ),
            row=2, col=1
        )
        
        # Suitability and confidence
        fig.add_trace(
            go.Scatter(
                x=predictions.index,
                y=predictions['trade_suitability'],
                mode='lines',
                name='Trade Suitability',
                line=dict(color='green', width=2)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=predictions.index,
                y=predictions['regime_confidence'],
                mode='lines',
                name='Regime Confidence',
                line=dict(color='blue', width=1, dash='dash')
            ),
            row=3, col=1
        )
        
        # Thresholds
        fig.add_hline(y=0.6, line=dict(color='red', dash='dot'), row=3, col=1)
        
        fig.update_layout(
            title="Cycle Regime Analysis",
            height=900,
            showlegend=True,
            template="plotly_white"
        )
        
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Regime", row=2, col=1)
        fig.update_yaxes(title_text="Score", row=3, col=1)
        
        return fig
    
    def _plot_signal_comparison(
        self,
        prices: pd.Series,
        original_signals: pd.DataFrame,
        filtered_signals: pd.DataFrame
    ) -> go.Figure:
        """Plot signal comparison"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=[
                "Original Signals",
                "Regime-Filtered Signals"
            ],
            vertical_spacing=0.1
        )
        
        # Original signals
        fig.add_trace(
            go.Scatter(
                x=prices.index,
                y=prices.values,
                mode='lines',
                name='Price',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        buy_mask = original_signals['signal'] > 0
        sell_mask = original_signals['signal'] < 0
        
        if buy_mask.any():
            fig.add_trace(
                go.Scatter(
                    x=prices[buy_mask].index,
                    y=prices[buy_mask].values,
                    mode='markers',
                    name='Buy (Original)',
                    marker=dict(size=8, color='green', symbol='triangle-up')
                ),
                row=1, col=1
            )
        
        if sell_mask.any():
            fig.add_trace(
                go.Scatter(
                    x=prices[sell_mask].index,
                    y=prices[sell_mask].values,
                    mode='markers',
                    name='Sell (Original)',
                    marker=dict(size=8, color='red', symbol='triangle-down')
                ),
                row=1, col=1
            )
        
        # Filtered signals
        fig.add_trace(
            go.Scatter(
                x=prices.index,
                y=prices.values,
                mode='lines',
                name='Price',
                line=dict(color='blue', width=1),
                showlegend=False
            ),
            row=2, col=1
        )
        
        buy_mask_f = filtered_signals['signal'] > 0
        sell_mask_f = filtered_signals['signal'] < 0
        
        if buy_mask_f.any():
            fig.add_trace(
                go.Scatter(
                    x=prices[buy_mask_f].index,
                    y=prices[buy_mask_f].values,
                    mode='markers',
                    name='Buy (Filtered)',
                    marker=dict(size=10, color='darkgreen', symbol='triangle-up')
                ),
                row=2, col=1
            )
        
        if sell_mask_f.any():
            fig.add_trace(
                go.Scatter(
                    x=prices[sell_mask_f].index,
                    y=prices[sell_mask_f].values,
                    mode='markers',
                    name='Sell (Filtered)',
                    marker=dict(size=10, color='darkred', symbol='triangle-down')
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title="Signal Filtering Comparison",
            height=700,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig


# Standalone function
def run_regime_dashboard():
    """Run the regime dashboard"""
    dashboard = RegimeDashboard()
    dashboard.run()


if __name__ == "__main__":
    run_regime_dashboard()

