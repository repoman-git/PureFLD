"""
Forecast Terminal

Ensemble forecast visualization with confidence bands.

Author: Meridian Team
Date: December 4, 2025
"""

import streamlit as st
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

st.title("🔮 Forecast Terminal")
st.markdown("**Ensemble forecast with LSTM, GRU, and Harmonic models**")

st.info("""
### Forecast Engine

Upload historical data to generate multi-model forecasts.

**Models:**
- LSTM (Long Short-Term Memory)
- GRU (Gated Recurrent Unit)
- Harmonic (FFT-based)
- Ensemble (Weighted average)

**Output:**
- 20-period forecast
- Confidence bands
- Model agreement score
""")

uploaded = st.file_uploader("Upload market CSV", type=["csv"], key="forecast")

if uploaded:
    st.warning("⚠️ Forecast generation requires trained models. See Stage 5 for model training.")
    st.info("💡 Use API endpoint: POST /api/v2/forecast/ensemble")
else:
    st.info("Upload historical data to generate forecasts")

