# OpenBB COT Data Integration Plan

## 🎯 **OBJECTIVE**

Integrate real COT (Commitment of Traders) data from OpenBB to replace synthetic data.

---

## 📊 **CURRENT STATUS**

### **What We Have:**
- ✅ OpenBB adapter scaffolded (`external/openbb_adapter.py`)
- ✅ COT data methods defined
- ✅ Fallback to synthetic working
- ❌ Real OpenBB API calls NOT implemented yet

### **Current Code:**
```python
def get_cot_data(self, symbol, start_date, end_date):
    # Fallback for now (real API would be called here)
    return self._fallback_to_synthetic_cot(symbol, start_date, end_date)
```

---

## 🔧 **IMPLEMENTATION PLAN**

### **Step 1: Install OpenBB SDK**
```bash
pip install openbb
```

### **Step 2: Implement Real COT Fetching**

Update `openbb_adapter.py`:

```python
def get_cot_data(self, symbol, start_date, end_date):
    if not self.enabled:
        return self._fallback_to_synthetic_cot(symbol, start_date, end_date)
    
    try:
        from openbb import obb
        
        # Map symbol to CFTC commodity code
        cftc_code = self._map_symbol_to_cftc(symbol)
        
        # Fetch COT data
        cot_data = obb.futures.cot(
            id=cftc_code,
            start_date=start_date,
            end_date=end_date
        )
        
        # Normalize to our format
        df = self._normalize_cot_data(cot_data)
        
        return df
        
    except Exception as e:
        if self.config.fallback_to_synthetic_if_failed:
            return self._fallback_to_synthetic_cot(symbol, start_date, end_date)
        raise ExternalDataException(f"Failed to fetch COT data: {e}")
```

### **Step 3: Symbol Mapping**

```python
def _map_symbol_to_cftc(self, symbol: str) -> str:
    """Map trading symbol to CFTC commodity code"""
    mapping = {
        'GLD': '088691',  # Gold
        'SLV': '084691',  # Silver
        'SPY': '13874+',  # S&P 500
        'TLT': '020601',  # 10-Year Treasury
        'QQQ': '209742',  # NASDAQ 100
        # Add more mappings
    }
    
    if symbol not in mapping:
        raise ValueError(f"No CFTC mapping for {symbol}")
    
    return mapping[symbol]
```

### **Step 4: Data Normalization**

```python
def _normalize_cot_data(self, cot_data) -> pd.DataFrame:
    """Normalize OpenBB COT data to Meridian format"""
    df = pd.DataFrame({
        'commercials_long': cot_data['comm_long'],
        'commercials_short': cot_data['comm_short'],
        'commercials_net': cot_data['comm_long'] - cot_data['comm_short'],
        'non_commercials_long': cot_data['noncomm_long'],
        'non_commercials_short': cot_data['noncomm_short'],
        'non_commercials_net': cot_data['noncomm_long'] - cot_data['noncomm_short'],
        'open_interest': cot_data['open_interest']
    })
    
    return df
```

---

## 📋 **COT DATA AVAILABILITY**

### **From CFTC via OpenBB:**

| Asset | CFTC Code | Data Start | Years Available |
|-------|-----------|------------|-----------------|
| Gold | 088691 | 2006 | ~19 years |
| Silver | 084691 | 2006 | ~19 years |
| S&P 500 | 13874+ | 1986 | ~38 years |
| 10-Year Treasury | 020601 | 2006 | ~19 years |
| NASDAQ 100 | 209742 | 2010 | ~15 years |
| Crude Oil | 067651 | 2006 | ~19 years |
| Euro | 099741 | 2007 | ~18 years |

**Frequency:** Weekly (Tuesdays)

---

## ✅ **BENEFITS**

### **Real COT Data:**
- ✅ Actual trader positioning
- ✅ Commercial vs Speculator sentiment
- ✅ Historical validation possible
- ✅ Real market signals
- ✅ Professional-grade analysis

### **vs Synthetic:**
- ❌ Synthetic is just simulated
- ❌ No real market correlation
- ❌ Can't validate strategies
- ❌ Not suitable for live trading

---

## 🔐 **SETUP REQUIREMENTS**

### **1. OpenBB API Key:**
- Free tier available
- Sign up at: openbb.co
- Add to `.env`:
```bash
OPENBB_API_KEY=your_key_here
```

### **2. Rate Limits:**
- Free tier: ~100 requests/day
- Paid tier: Unlimited
- COT data updates weekly (not real-time)

---

## 🎯 **NEXT STEPS**

1. **Install OpenBB SDK**
2. **Get API key** (free at openbb.co)
3. **Implement real COT fetching**
4. **Add symbol mappings**
5. **Test with GLD, SPY, TLT**
6. **Verify data matches price history**

---

## 📊 **DATA ALIGNMENT**

### **Price Data (Yahoo Finance):**
- GLD: 2004-2025 (21 years)
- Daily frequency

### **COT Data (CFTC via OpenBB):**
- GLD: 2006-2025 (19 years)
- Weekly frequency (Tuesdays)

**Overlap:** 2006-2025 = **19 years of aligned data** ✅

---

## 💡 **USAGE AFTER IMPLEMENTATION**

```python
from meridian_v2_1_2.external import OpenBBAdapter

# Initialize with API key
adapter = OpenBBAdapter()

# Fetch real COT data
cot_data = adapter.get_cot_data('GLD', '2006-01-01', '2025-12-31')

# Returns:
# - commercials_long/short/net
# - non_commercials_long/short/net
# - open_interest
# - Weekly frequency
# - 19 years of data
```

---

**Status:** Ready to implement  
**Estimated Time:** 1-2 hours  
**Dependencies:** OpenBB SDK, API key  
**Priority:** HIGH (needed for real COT analysis)


