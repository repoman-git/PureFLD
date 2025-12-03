# API Keys Setup Guide

**Quick guide for adding OpenBB and Alpaca API keys to Meridian**

---

## 🎯 **WHAT YOU NEED:**

1. **OpenBB API Key** (for real COT data)
2. **Alpaca API Keys** (for broker monitoring)

---

## 📝 **STEP 1: GET YOUR API KEYS**

### **OpenBB (Free Tier):**
1. Go to: https://my.openbb.co/app/platform/credentials
2. Sign up for free account
3. Generate API key
4. Copy the key (looks like: `pak_...`)

**What it enables:**
- ✅ Real CFTC COT data (19 years for GLD)
- ✅ Historical price data
- ✅ Economic indicators
- ✅ Free tier: ~100 requests/day

### **Alpaca (Paper Trading):**
1. Go to: https://alpaca.markets
2. Sign up for free account
3. Go to: Paper Trading → API Keys
4. Generate new API key pair
5. Copy both: API Key + Secret Key

**What it enables:**
- ✅ Read-only broker connection
- ✅ Real-time position monitoring
- ✅ Paper trading account access
- ✅ Historical fills import

**⚠️  START WITH PAPER TRADING KEYS!**

---

## 🔧 **STEP 2: ADD KEYS TO MERIDIAN**

### **Option A: Via Dashboard UI (EASIEST)**

1. **Start Meridian dashboard:**
   ```bash
   cd meridian_v2_1_2_full
   source .venv/bin/activate
   streamlit run src/meridian_v2_1_2/dashboard/01_Dashboard.py
   ```

2. **Navigate to Providers page** (Page 11)

3. **Find OpenBB section:**
   - Click to expand
   - Check "Enable" checkbox
   - Paste your API key in "API Key" field
   - Click "Save Configuration"

4. **Find Alpaca section:**
   - Click to expand
   - Check "Enable" checkbox
   - Paste API Key in "API Key" field
   - Paste Secret Key in "API Secret" field
   - Verify Base URL is: `https://paper-api.alpaca.markets`
   - Click "Save Configuration"

5. **Test Connections:**
   - Click "Test All Providers" button
   - Should see ✅ for both OpenBB and Alpaca

### **Option B: Via Environment File**

1. **Create `.env` file:**
   ```bash
   cd meridian_v2_1_2_full
   touch .env
   ```

2. **Add your keys:**
   ```bash
   # OpenBB
   OPENBB_API_KEY=pak_your_key_here
   
   # Alpaca (Paper Trading)
   ALPACA_API_KEY=your_alpaca_key_here
   ALPACA_SECRET_KEY=your_alpaca_secret_here
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ```

3. **Restart dashboard** to load keys

---

## ✅ **STEP 3: VERIFY IT WORKS**

### **Test OpenBB COT Data:**

```python
from meridian_v2_1_2.data_providers import fetch_cot_data

# This will now use OpenBB (real data!)
df = fetch_cot_data('GLD', '2010-01-01', '2025-12-31', source='auto')

print(f"Got {len(df)} weeks of COT data")
print(f"Source: Real CFTC data via OpenBB!")
```

### **Test Alpaca Connection:**

```python
from meridian_v2_1_2.brokers import AlpacaBroker

broker = AlpacaBroker()
broker.connect(api_key, secret_key, paper=True)

account = broker.get_account_info()
print(f"Account value: ${account['account_value']:,.2f}")

positions = broker.get_positions()
print(f"Positions: {len(positions)}")
```

---

## 🎯 **WHAT HAPPENS AUTOMATICALLY:**

### **When You Add OpenBB Key:**
1. ✅ Unified COT Provider detects it
2. ✅ Switches from synthetic to real CFTC data
3. ✅ All strategies get real COT data
4. ✅ 19 years of historical data available
5. ✅ No code changes needed!

### **When You Add Alpaca Keys:**
1. ✅ Broker monitoring becomes available
2. ✅ Can sync real portfolio positions
3. ✅ Read-only access (safe)
4. ✅ Paper trading account accessible

---

## 📊 **DATA YOU'LL GET:**

### **With OpenBB:**
```
GLD COT Data:
- Start: 2006
- End: 2025
- Weeks: ~990
- Years: 19
- Format: Weekly (Tuesdays)
- Columns: commercials_long/short, non_commercials_long/short, open_interest
```

### **With Alpaca:**
```
Paper Trading Account:
- Real-time positions
- Order history
- Account balance
- Buying power
- P&L tracking
```

---

## 🔐 **SECURITY:**

- ✅ Keys stored in `.env` (not committed to git)
- ✅ Keys encrypted in UI
- ✅ Keys never logged
- ✅ Paper trading by default
- ✅ Read-only broker access

---

## ⚠️ **IMPORTANT:**

1. **Use PAPER trading keys for Alpaca** (not live!)
2. **Never commit `.env` file** (already in .gitignore)
3. **Test with small amounts first**
4. **OpenBB free tier = 100 requests/day** (plenty for COT data)

---

## 🚀 **WHEN READY:**

Just add your keys and everything will work automatically!

**The system is already wired to:**
- ✅ Detect when keys are present
- ✅ Switch to real data sources
- ✅ Fall back gracefully if keys missing
- ✅ Show status in Providers page

**No additional setup needed!** 🎯

---

## 📞 **SUPPORT:**

**OpenBB Issues:** https://docs.openbb.co
**Alpaca Issues:** https://alpaca.markets/docs

---

**Status:** ✅ READY FOR YOUR API KEYS  
**When Added:** ✅ AUTOMATIC ACTIVATION  
**Fallback:** ✅ WORKS WITHOUT KEYS (synthetic)

