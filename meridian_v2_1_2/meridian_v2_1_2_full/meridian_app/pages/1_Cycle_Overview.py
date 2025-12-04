"""Cycle Overview Page"""
import streamlit as st
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

from components.utils import call_api, to_series, load_csv_data
from components.charts import price_chart

st.title("📊 Cycle Overview Board")
st.markdown("**Complete cycle analysis dashboard**")

uploaded = st.file_uploader("Upload CSV (columns: timestamp, price)", type=["csv"])

if uploaded:
    df = load_csv_data(uploaded)
    
    if df is not None and 'timestamp' in df.columns and 'price' in df.columns:
        price = to_series(df["timestamp"].tolist(), df["price"].tolist())
        
        st.subheader("Price Chart")
        st.plotly_chart(price_chart(price))
        
        with st.spinner("Computing cycle analysis..."):
            # Call API endpoints
            phasing = call_api("phasing/compute", {
                "price_series": {
                    "timestamps": df["timestamp"].tolist(),
                    "prices": df["price"].tolist()
                }
            })
            
            harmonics = call_api("harmonics/compute", {
                "timestamps": df["timestamp"].tolist(),
                "prices": df["price"].tolist()
            })
        
        if 'error' not in phasing:
            st.success("✅ Cycle analysis complete")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Phasing Results")
                st.json(phasing)
            
            with col2:
                st.subheader("Harmonics Results")
                st.json(harmonics)
        else:
            st.error(f"API Error: {phasing.get('error', 'Unknown error')}")
            st.info("💡 Make sure the API server is running: uvicorn meridian_v2_1_2.meridian_api.main:app --port 8000")
    else:
        st.error("CSV must have 'timestamp' and 'price' columns")

