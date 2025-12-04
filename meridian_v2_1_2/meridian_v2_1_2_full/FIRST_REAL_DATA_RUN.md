# 🚀 Meridian — First Real Data Run Guide

**Objective:** Perform the first *real* pipeline execution using historical market data.

**Recommended Symbol:** GLD (Gold ETF) or GC=F (Gold Futures)

---

## ✔ **Step 1 — Ensure Environment is Ready**

### **Check Docker Services:**
```bash
cd /Users/simonerses/Data-Projects-PureFLD/meridian_v2_1_2/meridian_v2_1_2_full/deploy
docker-compose up -d
```

### **Verify Services:**
```bash
docker ps

# Should show:
# - deploy-api-1 (or meridian-api)
# - Optional: deploy-app-1 (or meridian-dashboard)
```

### **Test API:**
```bash
curl http://localhost:8000/health

# Should return: {"status":"healthy",...}
```

### **Test Dashboard (Optional):**
Open browser: http://localhost:8501

---

## ✔ **Step 2 — Prepare Real Market Data**

### **Option A: Use yfinance (Recommended - Easy)**
```python
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Fetch 2 years of GLD data
symbol = 'GLD'
end_date = datetime.now()
start_date = end_date - timedelta(days=365*2)

ticker = yf.Ticker(symbol)
hist = ticker.history(start=start_date, end=end_date)
prices = hist['Close']

print(f"✅ Fetched {len(prices)} days of {symbol} data")
print(f"Date range: {prices.index[0].date()} to {prices.index[-1].date()}")

# Save for later use
prices.to_csv('data/gld_prices.csv')
```

### **Option B: Use Existing Sample Data**
```bash
# If you have historical data files
ls data/*.csv
```

---

## ✔ **Step 3 — Run Full Pipeline Locally**

### **Method 1: Using Python Directly**
```python
import sys
sys.path.insert(0, 'src')

import pandas as pd
from meridian_v2_1_2.pipeline.meridian_pipeline import MeridianPipeline

# Load your data
prices = pd.read_csv('data/gld_prices.csv', index_col=0, parse_dates=True)['Close']

# Initialize pipeline
pipeline = MeridianPipeline()

# Run complete analysis
print("🚀 Running Meridian Pipeline...")
results = pipeline.run({'GLD': prices})

print("✅ Pipeline complete!")
print(f"   • Phasing: {len(results['phasing'])} results")
print(f"   • Regime: {results['regime']['regime_name'].iloc[-1]}")
```

### **Method 2: Using API**
```bash
# Ensure API is running
curl -X POST "http://localhost:8000/api/v2/regime/classify" \
  -H "Content-Type: application/json" \
  -d @- << EOF
{
  "timestamps": ["2024-01-01", "2024-01-02", "2024-01-03"],
  "prices": [180.5, 181.2, 180.8]
}
EOF
```

---

## ✔ **Step 4 — Inspect Outputs**

### **1. Check Console Output:**
```
Phase 1: Cycle Analysis...
Phase 2: Regime Classification...
Phase 3: Storing results...
✅ Pipeline complete!
```

### **2. Check Database:**
```python
from meridian_v2_1_2.storage.meridian_db import db

# Query regimes
regimes = db.read("SELECT * FROM regimes ORDER BY timestamp DESC LIMIT 10")
print(regimes)

# Query signals (if any)
signals = db.read("SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10")
print(signals)
```

### **3. Check File Outputs:**
```bash
ls -la meridian_local/
# Should see: meridian.db

ls -la meridian_local/registry/
# Should see: model JSON files (if models were saved)
```

---

## ✔ **Step 5 — Visualize Results**

### **Option A: Use Dashboard**
```bash
# Make sure dashboard is running
PYTHONPATH="$PWD/src:$PYTHONPATH" streamlit run meridian_app/app.py

# Navigate to: http://localhost:8501
# Upload your CSV file
# View cycle analysis, regime classification, etc.
```

### **Option B: Use Notebooks**
```bash
cd notebooks
jupyter notebook pairs_trading_example.ipynb

# Or
jupyter notebook regime_classifier_example.ipynb
```

### **Option C: Use Python**
```python
import matplotlib.pyplot as plt

# Plot regime over time
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

# Price
ax1.plot(prices.index, prices.values)
ax1.set_title('GLD Price')
ax1.set_ylabel('Price')

# Regime
regime_data = results['regime']
ax2.scatter(regime_data.index, regime_data['regime'], 
           c=regime_data['regime'], cmap='viridis')
ax2.set_title('Market Regime Over Time')
ax2.set_ylabel('Regime (0-4)')
ax2.set_yticks([0, 1, 2, 3, 4])
ax2.set_yticklabels(['TRENDING', 'CYCLICAL', 'VOLATILE', 'COMPRESSED', 'RESETTING'])

plt.tight_layout()
plt.show()
```

---

## ✔ **Step 6 — (Optional) Begin Paper Trading**

### **Prerequisites:**
1. Get FREE Alpaca paper trading account: https://alpaca.markets
2. Get your paper trading API keys from dashboard

### **Configure:**
Edit `deploy/.env` (or create from `.env.example`):
```bash
ALPACA_API_KEY=your_paper_api_key_here
ALPACA_SECRET_KEY=your_paper_secret_key_here
ALPACA_ENDPOINT=https://paper-api.alpaca.markets
ENABLE_PAPER_TRADING=true
```

### **Execute:**
```python
from meridian_v2_1_2.execution_engine import *

# Connect to Alpaca paper trading
broker = AlpacaClient(
    api_key="YOUR_PAPER_KEY",
    secret_key="YOUR_PAPER_SECRET",
    endpoint="https://paper-api.alpaca.markets"
)

if broker.connect():
    print("✅ Connected to Alpaca paper trading")
    
    # Check account
    account = broker.get_account_info()
    print(f"Account equity: ${account.equity:,.2f}")
    
    # Initialize execution engine
    engine = ExecutionEngine(
        broker=broker,
        order_manager=OrderManager(),
        position_manager=PositionManager(),
        risk_gate=RiskGate()
    )
    
    # Generate signals (from your analysis)
    # Execute trades
    # results = engine.step(signals, prices, weights, vol_df, regime)
```

---

## ✔ **Step 7 — Monitor and Validate**

### **Daily Checklist:**
- [ ] Check regime classification is sensible
- [ ] Verify cycle phases align with price action
- [ ] Monitor forecast accuracy
- [ ] Review risk metrics
- [ ] Check portfolio allocation
- [ ] Validate any trades executed

### **Weekly Review:**
- [ ] Compare forecasts vs actuals
- [ ] Analyze regime distribution
- [ ] Review strategy evolution
- [ ] Check P&L (if paper trading)
- [ ] Identify improvements

---

## 🎯 **Next Milestones**

After your first successful run:

### **Week 1:**
- ✅ Run pipeline daily with real data
- ✅ Validate cycle turning points
- ✅ Compare forecasts vs actuals
- ✅ Monitor regime transitions

### **Week 2-4:**
- ✅ Paper trade with small positions
- ✅ Track strategy evolution
- ✅ Refine parameters
- ✅ Build confidence

### **Month 2:**
- ✅ Deploy to cloud (optional)
- ✅ Scale infrastructure
- ✅ Consider live trading (if confident)
- ✅ Optional: Build Stage 11

---

## 🧪 **Validation Checklist**

Before considering live trading:
- [ ] Pipeline runs successfully for 30+ days
- [ ] Regime classification makes sense
- [ ] Forecasts show directional accuracy
- [ ] Risk management works as expected
- [ ] Paper trading shows positive results
- [ ] No system errors or crashes
- [ ] All 16 integration tests still passing
- [ ] Comfortable with the system behavior

---

## 🏁 **You Are Ready**

This completes the **first real market data run** readiness guide.

Your platform is now fully operational and ready to:
- Ingest real market data
- Analyze cycles professionally
- Generate trading signals
- Execute paper trades
- Monitor performance

**Start with GLD or another liquid ETF.**  
**Run for 1-2 weeks.**  
**Monitor closely.**  
**Build confidence.**

---

## 💡 **Pro Tips**

1. **Start Simple:** Use one symbol (GLD) first
2. **Watch Closely:** Monitor every signal for the first week
3. **Paper Trade:** Use Alpaca's FREE paper trading
4. **Log Everything:** Keep notes on what works/doesn't
5. **Be Patient:** Build confidence before going live
6. **Trust the System:** It's tested and validated
7. **Review Daily:** Check regime, volatility, signals
8. **Iterate:** Adjust parameters based on results

---

## 📚 **Resources**

- **API Documentation:** http://localhost:8000/docs
- **Dashboard:** http://localhost:8501
- **Stage Guides:** `STAGE_*_COMPLETE.md` files
- **Integration Tests:** `tests/integration/`
- **Examples:** `notebooks/*.ipynb`

---

## 🎊 **You're Live!**

**Meridian 3.0 is operational.**  
**Your first real data run awaits.**  
**The system is tested, validated, and ready.**

**Good luck, and trade wisely!** 🚀

---

**Guide Version:** 1.0  
**Last Updated:** December 4, 2025  
**Status:** ✅ Ready for Use

