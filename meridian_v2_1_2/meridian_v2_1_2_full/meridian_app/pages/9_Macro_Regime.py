"""
Macro Regime Monitor

Market regime classification and trend analysis.

Author: Meridian Team  
Date: December 4, 2025
"""

import streamlit as st
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

from components.utils import call_api, load_csv_data

st.title("🌍 Macro Regime Monitor")
st.markdown("**ML-powered market regime classification**")

st.info("""
### Regime Types:
- **TRENDING:** Strong directional bias (20% trade suitability)
- **CYCLICAL:** Clear oscillatory behavior (100% suitability) ⭐
- **VOLATILE:** High risk, expanding amplitude (40% suitability)
- **COMPRESSED:** Low volatility, pre-breakout (60% suitability)
- **RESETTING:** Post-peak reorganization (30% suitability)
""")

uploaded = st.file_uploader("Upload market CSV", type=["csv"], key="macro")

if uploaded:
    df = load_csv_data(uploaded)
    
    if df is not None and 'timestamp' in df.columns and 'price' in df.columns:
        st.success(f"✅ Analyzing {len(df)} bars")
        
        # Show regime classification UI (reusing Stage 2 dashboard)
        st.info("💡 This page integrates with the Regime Classifier (Page 2)")
        st.markdown("[→ Go to Regime Classifier](http://localhost:8501/2_Regime_Classifier)")
else:
    st.info("Upload market data to classify regime")

