"""Regime Classification Page"""
import streamlit as st
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

from components.utils import call_api, load_csv_data

st.title("🔮 Regime Classifier")
st.markdown("**ML-powered market regime detection**")

uploaded = st.file_uploader("Upload CSV", type=["csv"], key="regime")

if uploaded:
    df = load_csv_data(uploaded)
    
    if df is not None:
        with st.spinner("Classifying regime..."):
            result = call_api("regime/classify", {
                "timestamps": df["timestamp"].tolist(),
                "prices": df["price"].tolist()
            })
        
        if 'error' not in result:
            st.success(f"✅ Current Regime: **{result['regime_name']}**")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Regime", result['regime_name'])
            col2.metric("Confidence", f"{result['confidence']:.1%}")
            col3.metric("Trade Suitability", f"{result['trade_suitability']:.0%}")
            
            st.json(result)
        else:
            st.error(result.get('error'))

