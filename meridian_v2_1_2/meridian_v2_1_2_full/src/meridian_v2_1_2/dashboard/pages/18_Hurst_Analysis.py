"""
Hurst Cycle Analysis Dashboard

Professional J.M. Hurst cycle analysis with:
- Multi-timeframe phasing
- Trough detection
- VTL construction
- VTL break signals
- Cycle diagnostics

⚠️  EDUCATIONAL ONLY - Not investment advice
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from meridian_v2_1_2.hurst import (
    HurstPhasingEngine,
    HurstVTLBuilder,
    HurstVTLBreakDetector,
    HurstDiagnostics,
    plot_hurst_view,
    plot_phase_vs_price
)
from meridian_v2_1_2.paper_trading import LiveDataFeed
from meridian_v2_1_2.strategies.strategy_router import load_strategy

st.set_page_config(
    page_title="Meridian - Hurst Analysis",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Hurst Cycle Analysis")
st.markdown("*Professional J.M. Hurst cycle phasing and VTL analysis*")
st.markdown("---")

# Educational disclaimer
st.info("""
⚠️  **EDUCATIONAL ONLY** - This is cycle analysis for educational purposes.
Not investment advice. Past cycles do not predict future cycles.
""")

# Info panel
with st.expander("ℹ️ What is Hurst Cycle Analysis?", expanded=False):
    st.markdown("""
    ### J.M. Hurst Cycle Analysis
    
    **Core Concepts:**
    
    **1. Cycle Phasing:**
    - Uses Hilbert transform to compute phase (0-1)
    - Phase 0 = cycle trough (potential buy)
    - Phase 0.5 = cycle peak (potential sell)
    - Phase 1 = back to trough
    
    **2. Trough Detection:**
    - Identifies cycle troughs across multiple timeframes
    - Nominal periods: 20-day, 40-day, 80-day cycles
    - Troughs should nest (smaller cycles within larger)
    
    **3. Valid Trend Lines (VTL):**
    - Lines connecting recent troughs
    - Price should stay above VTL in uptrend
    - VTL break = trend change signal
    
    **4. Trading Signals:**
    - **Long:** VTL break down in low phase (near trough)
    - **Exit:** VTL break up in high phase (near peak)
    - Confirm with multi-timeframe alignment
    
    **Best For:** Cyclical assets like GLD, SLV, TLT, commodities
    """)

# Initialize session state
if 'hurst_result' not in st.session_state:
    st.session_state.hurst_result = None

# ═══════════════════════════════════════════════════════════════════
# ANALYSIS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

st.subheader("⚙️ Analysis Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    symbol = st.text_input("Symbol", value="GLD", help="Asset symbol (e.g., GLD, SLV, TLT)")

with col2:
    period_20 = st.number_input("Short Cycle (days)", min_value=5, max_value=50, value=20)
    period_40 = st.number_input("Medium Cycle (days)", min_value=20, max_value=100, value=40)

with col3:
    period_80 = st.number_input("Long Cycle (days)", min_value=40, max_value=200, value=80)
    smooth_factor = st.slider("Smooth Factor", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

nominal_periods = [period_20, period_40, period_80]

st.markdown("---")

# Run analysis button
if st.button("🔄 RUN HURST ANALYSIS", type="primary", use_container_width=True):
    with st.spinner(f"Analyzing {symbol} cycles..."):
        try:
            # Fetch data
            data_feed = LiveDataFeed()
            ohlc = data_feed.fetch_latest_ohlc(symbol, interval='1d')
            
            if ohlc is None or ohlc.empty:
                st.error("Failed to fetch data")
            else:
                # Get enough history for cycle analysis
                price = ohlc['Close'].tail(300)  # Last 300 days
                
                # Initialize Hurst engines
                phasing_engine = HurstPhasingEngine(
                    nominal_periods=nominal_periods,
                    smooth_factor=smooth_factor
                )
                vtl_builder = HurstVTLBuilder()
                break_detector = HurstVTLBreakDetector()
                diagnostics = HurstDiagnostics()
                
                # Phase all cycles
                all_phases = phasing_engine.phase_all(price)
                
                # Build VTLs for each cycle
                vtls = {}
                breaks = {}
                
                for period in nominal_periods:
                    cycle = all_phases[period]
                    troughs = cycle['troughs']
                    
                    if len(troughs) >= 2:
                        vtl = vtl_builder.build_vtl(price, troughs)
                        vtls[period] = vtl
                        
                        # Detect breaks
                        up_breaks = break_detector.find_breaks(price, vtl, "uptrend")
                        down_breaks = break_detector.find_breaks(price, vtl, "downtrend")
                        breaks[period] = {'up': up_breaks, 'down': down_breaks}
                
                # Store result
                st.session_state.hurst_result = {
                    'symbol': symbol,
                    'price': price,
                    'all_phases': all_phases,
                    'vtls': vtls,
                    'breaks': breaks,
                    'nominal_periods': nominal_periods
                }
                
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            import traceback
            st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════════

if st.session_state.hurst_result:
    result = st.session_state.hurst_result
    
    st.markdown("---")
    st.success(f"✅ **Analysis Complete: {result['symbol']}**")
    
    # Current phase metrics
    col1, col2, col3 = st.columns(3)
    
    for i, period in enumerate(result['nominal_periods']):
        cycle = result['all_phases'][period]
        current_phase = cycle['phase'].iloc[-1] if not cycle['phase'].empty else None
        
        with [col1, col2, col3][i]:
            if current_phase is not None and not pd.isna(current_phase):
                phase_pct = current_phase * 100
                st.metric(
                    f"{period}-Day Cycle Phase",
                    f"{phase_pct:.1f}%",
                    help="0% = Trough, 50% = Peak, 100% = Trough"
                )
                
                # Phase interpretation
                if phase_pct < 25:
                    st.success("🟢 Near Trough - Bullish")
                elif phase_pct < 75:
                    st.warning("🟡 Mid-Cycle - Neutral")
                else:
                    st.error("🔴 Near Peak - Bearish")
            else:
                st.metric(f"{period}-Day Cycle Phase", "N/A")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Price & VTL", "🔄 Phase Charts", "📈 Cycle Diagnostics", "🎯 Trading Signals"])
    
    with tab1:
        st.markdown("### Price with Valid Trend Lines")
        
        # Plot each cycle
        for period in result['nominal_periods']:
            cycle = result['all_phases'][period]
            troughs = cycle['troughs']
            vtl = result['vtls'].get(period)
            period_breaks = result['breaks'].get(period, {})
            
            st.markdown(f"#### {period}-Day Cycle")
            
            # Create plot
            fig, ax = plt.subplots(figsize=(14, 6))
            
            # Plot price
            ax.plot(result['price'].index, result['price'].values, label='Price', color='blue')
            
            # Plot troughs
            if troughs:
                trough_prices = [result['price'].loc[t] for t in troughs if t in result['price'].index]
                ax.scatter(troughs, trough_prices, color='red', s=100, label='Troughs', zorder=5)
            
            # Plot VTL
            if vtl is not None and not vtl.isna().all():
                ax.plot(vtl.index, vtl.values, linestyle='--', color='green', label='VTL', linewidth=2)
            
            # Plot breaks
            up_breaks = period_breaks.get('up', [])
            down_breaks = period_breaks.get('down', [])
            
            if up_breaks:
                break_prices = [result['price'].loc[b] for b in up_breaks if b in result['price'].index]
                ax.scatter(up_breaks, break_prices, color='orange', marker='v', s=150, label='VTL Break Down', zorder=5)
            
            if down_breaks:
                break_prices = [result['price'].loc[b] for b in down_breaks if b in result['price'].index]
                ax.scatter(down_breaks, break_prices, color='purple', marker='^', s=150, label='VTL Break Up', zorder=5)
            
            ax.legend()
            ax.set_title(f"{result['symbol']} - {period}-Day Cycle")
            ax.set_xlabel("Date")
            ax.set_ylabel("Price")
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
    
    with tab2:
        st.markdown("### Phase vs Price")
        
        for period in result['nominal_periods']:
            cycle = result['all_phases'][period]
            
            st.markdown(f"#### {period}-Day Cycle Phase")
            
            # Create dual-axis plot
            fig, ax1 = plt.subplots(figsize=(14, 6))
            
            # Price on left axis
            ax1.plot(result['price'].index, result['price'].values, label='Price', color='tab:blue')
            ax1.set_ylabel('Price', color='tab:blue')
            ax1.tick_params(axis='y', labelcolor='tab:blue')
            
            # Phase on right axis
            ax2 = ax1.twinx()
            if not cycle['phase'].empty:
                ax2.plot(cycle['phase'].index, cycle['phase'].values, label='Phase (0-1)', color='tab:orange', alpha=0.7)
                ax2.axhline(y=0.25, color='green', linestyle=':', alpha=0.5, label='Buy Zone')
                ax2.axhline(y=0.75, color='red', linestyle=':', alpha=0.5, label='Sell Zone')
            ax2.set_ylabel('Phase (0-1)', color='tab:orange')
            ax2.tick_params(axis='y', labelcolor='tab:orange')
            ax2.set_ylim([0, 1])
            
            ax1.set_title(f"{result['symbol']} - {period}-Day Phase")
            ax1.grid(True, alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
    
    with tab3:
        st.markdown("### Cycle Diagnostics")
        
        diagnostics = HurstDiagnostics()
        
        for period in result['nominal_periods']:
            cycle = result['all_phases'][period]
            troughs = cycle['troughs']
            
            st.markdown(f"#### {period}-Day Cycle")
            
            if len(troughs) >= 2:
                # Spacing statistics
                spacing_stats = diagnostics.spacing_stats(troughs, period)
                
                st.markdown("**Trough Spacing:**")
                st.dataframe(spacing_stats, use_container_width=True)
                
                avg_spacing = spacing_stats['spacing_days'].mean()
                avg_ratio = spacing_stats['ratio_to_nominal'].mean()
                
                st.markdown(f"- Average spacing: {avg_spacing:.1f} days")
                st.markdown(f"- Ratio to nominal: {avg_ratio:.2f}x")
                
                if 0.8 <= avg_ratio <= 1.2:
                    st.success("✅ Cycle spacing is consistent")
                else:
                    st.warning("⚠️  Cycle spacing varies from nominal")
            else:
                st.info(f"Need at least 2 troughs for diagnostics (found {len(troughs)})")
    
    with tab4:
        st.markdown("### Trading Signals (Hurst-ETF Strategy)")
        
        st.markdown("""
        **Signal Logic:**
        - **LONG:** VTL break down (price crosses below VTL) in low phase (<20%)
        - **EXIT:** VTL break up (price crosses above VTL) in high phase (>80%)
        """)
        
        # Show recent signals
        primary_period = result['nominal_periods'][0]
        primary_breaks = result['breaks'].get(primary_period, {})
        primary_phase = result['all_phases'][primary_period]['phase']
        
        up_breaks = primary_breaks.get('up', [])
        down_breaks = primary_breaks.get('down', [])
        
        signals = []
        
        for break_time in up_breaks:
            if break_time in primary_phase.index:
                phase_val = primary_phase.loc[break_time]
                if phase_val < 0.2:
                    signals.append({
                        'Time': break_time,
                        'Signal': 'LONG',
                        'Phase': f"{phase_val * 100:.1f}%",
                        'Reason': 'VTL break down in low phase'
                    })
        
        for break_time in down_breaks:
            if break_time in primary_phase.index:
                phase_val = primary_phase.loc[break_time]
                if phase_val > 0.8:
                    signals.append({
                        'Time': break_time,
                        'Signal': 'EXIT/SHORT',
                        'Phase': f"{phase_val * 100:.1f}%",
                        'Reason': 'VTL break up in high phase'
                    })
        
        if signals:
            signals_df = pd.DataFrame(signals).sort_values('Time', ascending=False)
            st.dataframe(signals_df, use_container_width=True)
        else:
            st.info("No recent trading signals")
        
        # Current recommendation
        st.markdown("### Current Recommendation")
        
        current_phase = primary_phase.iloc[-1] if not primary_phase.empty else None
        
        if current_phase is not None and not pd.isna(current_phase):
            phase_pct = current_phase * 100
            
            if phase_pct < 25:
                st.success(f"🟢 **BULLISH ZONE** - Phase: {phase_pct:.1f}%")
                st.markdown("Near cycle trough - favorable for long entries")
            elif phase_pct > 75:
                st.error(f"🔴 **BEARISH ZONE** - Phase: {phase_pct:.1f}%")
                st.markdown("Near cycle peak - consider exits or shorts")
            else:
                st.warning(f"🟡 **NEUTRAL ZONE** - Phase: {phase_pct:.1f}%")
                st.markdown("Mid-cycle - wait for clearer signals")

# Footer
st.markdown("---")
st.caption("Phase 12 | Hurst Cycle Analysis Integration")
st.caption("🔄 Multi-timeframe phasing | 📊 VTL construction | 🎯 Professional cycle analysis")
st.caption("⚠️  EDUCATIONAL ONLY - Not investment advice")

