"""
Meridian Cycle Dashboard Web App (Stage 8)

Main application launcher for the complete Meridian dashboard.

Launch: streamlit run meridian_app/app.py

Author: Meridian Team
Date: December 4, 2025
Stage: 8 of 10
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

st.set_page_config(
    page_title="Meridian v2 - Cycle Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page
st.title("📊 Meridian v2.1.2 - Quant Cycle Intelligence Platform")

st.markdown("""
### **Welcome to Meridian**

A unified institutional-grade platform for:

- 🔄 **Hurst Cycle Analysis** (Phasing, FLD, VTL)
- 🎼 **Harmonic Spectrum Analysis**
- 📈 **Ensemble Forecasting** (LSTM, GRU, Harmonic)
- 🌐 **Intermarket Intelligence**
- 🔮 **Regime Classification** (ML-powered)
- ⚠️ **Volatility & Risk Management**
- 💼 **Portfolio Allocation**
- 🧬 **Strategy Evolution** (Genetic Programming)
- 🚀 **Live Execution** (Alpaca, IBKR)

---

### **Navigation**
Use the sidebar to access different modules.

### **Status**
- **Stages Complete:** 8 of 10 (80%)
- **API Status:** Check at http://localhost:8000/health
- **Version:** 2.1.2

---

### **Quick Start**
1. Upload market data (CSV with timestamp, price columns)
2. Navigate to desired analysis module
3. View results and charts
4. Export or execute strategies

""")

st.info("💡 **Tip:** Start with 'Cycle Overview' for a comprehensive view")

# System status
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Stages Complete", "8 of 10")
with col2:
    st.metric("Modules", "50+")
with col3:
    st.metric("Status", "✅ Operational")

st.success("🎊 Meridian v2.1.2 - 80% Complete - Web App Operational!")

