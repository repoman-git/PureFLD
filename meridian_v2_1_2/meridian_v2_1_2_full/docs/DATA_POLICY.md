# 📄 Meridian 3.0 — Data Handling Policy

**Version:** 1.0  
**Scope:** Data ingestion, validation, pipelines, backtests, APIs, execution engine  
**Author:** Meridian Core Team  
**Status:** Mandatory

---

## 1. Purpose

This document defines **mandatory data quality rules** for all components of the Meridian 3.0 Quantitative Trading Platform.

**Goals:**
- Multi-decade consistency
- Cycle integrity (requires long histories)
- Forecasting stability
- Real data as default
- Reproducible backtesting
- Platform-wide minimum historical depth

---

## 2. Real Data Requirement

Meridian 3.0 **must always use real historical market data** except where explicitly marked as synthetic for testing purposes.

### **Approved Data Sources:**
- ✅ Yahoo Finance (yfinance)
- ✅ Tiingo
- ✅ Polygon.io
- ✅ OpenBB data loaders
- ✅ Alpaca Market Data (when keys configured)
- ✅ CME/CBOE/CFTC feeds (when available)
- ✅ Interactive Brokers historical data

### **Prohibited in Production:**
- ❌ Synthetic datasets
- ❌ Random walk generators
- ❌ Manually constructed arrays (except tests)
- ❌ Data shorter than minimum requirements

---

## 3. Minimum Historical Requirement

**MANDATORY RULE:**  
All real-data operations must load history extending back to **≥ January 1st, 2000**.

**Rationale:**
- Hurst cycles require multi-decade context
- Regime classification needs diverse market conditions
- Intermarket relationships require secular trend data
- Backtests must include multiple market cycles

**Preference:**  
Use data from 1990s when available for even better cycle context.

**Enforcement:**  
Short datasets **must fail** with a clear error message.

---

## 4. Minimum Bar Requirements by Component

| Component | Minimum Bars | Rationale |
|----------|--------------|-----------|
| **Regime Classifier** | ≥ 252 | 1 year for rolling windows |
| **Volatility/Risk Engine** | ≥ 500 | 2 years for envelope stability |
| **Hurst Phasing Engine** | ≥ 1500 | 6+ years for cycle detection |
| **Harmonics Engine** | ≥ 1500 | FFT requires long series |
| **Forecasting Models** | ≥ 1500 | Training data for LSTM/GRU |
| **Cycle Discovery** | ≥ 1500 | Multiple cycle periods |
| **Backtesting** | ≥ 2500 | 10+ years for robustness |
| **Intermarket Engine** | ≥ 2500 | Secular relationships |

**Enforcement:** If requirements not met → execution **must stop** with clear error.

---

## 5. Synthetic Data Policy

### **Synthetic Data Allowed ONLY In:**
- ✅ Unit tests
- ✅ Integration tests (clearly marked)
- ✅ Regression tests
- ✅ Fail-state behavior tests
- ✅ Pipeline smoke tests
- ✅ Decorator/validation tests

### **Requirements for Synthetic Data:**
- Must be self-contained in test files
- Must be clearly labeled as synthetic
- Never imported into production modules
- Must use `SyntheticDataGenerator` class
- Must be ≥250 bars if testing cycle engines

---

## 6. Data Quality Checks

### **Pre-Flight Validation:**
Every data load must check:
- [ ] No NaN values in critical columns (close, open)
- [ ] No extreme outliers (>10σ moves)
- [ ] Monotonic timestamp ordering
- [ ] No duplicate timestamps
- [ ] Sufficient history (≥2000-01-01)
- [ ] Sufficient bar count (per component)

### **Runtime Monitoring:**
- Log all data quality issues
- Track data source reliability
- Monitor for gaps or missing data
- Alert on data integrity violations

---

## 7. Enforcement Mechanisms

The system enforces these rules via:

1. **`@minimum_history_required` decorator** - Function-level validation
2. **`DataIntegrityEnforcer` module** - Runtime validation
3. **Data loader constraints** - Source-level checks
4. **Integration tests** - Validates enforcement
5. **Cursor project rules** - Development-time guidance
6. **CI/CD checks** - Build-time validation

---

## 8. Violations

Any violation of this policy must:

1. ✅ Raise a clear `ValueError` with explanation
2. ✅ Log violation in `meridian_local/logs/policy_violations.log`
3. ✅ Abort pipeline execution immediately
4. ✅ Return error via API (if triggered through API)
5. ✅ Display in dashboard (if triggered through UI)

### **Example Violation Message:**
```
[DATA INTEGRITY VIOLATION]
Module: HurstPhasingEngine
Issue: Dataset starts at 2015-01-01 but requires ≥2000-01-01
Bars: 500 (requires ≥1500)
Action: Pipeline aborted
```

---

## 9. Exception Handling

### **Grandfathered Exceptions:**
- Quick demos with < 1 year data (must be marked as demo)
- Unit tests with minimal synthetic data
- Documentation examples

### **Requesting Exception:**
Exceptions require:
- Written justification
- Code review approval
- Clear marking in code comments
- Cannot be used in production

---

## 10. Review Cycle

This policy must be reviewed:
- ✅ Quarterly (every 3 months)
- ✅ When new data vendors added
- ✅ When cycle engines modified
- ✅ When new markets added (futures, crypto, etc.)

---

## 11. Compliance Tracking

### **Automated Checks:**
- Integration tests validate policy enforcement
- CI/CD pipeline checks for violations
- Doctor script verifies data availability

### **Manual Reviews:**
- Quarterly code review for data handling
- Annual audit of data sources
- Performance review of data quality

---

## ✔ Policy Status

**Approved:** December 4, 2025  
**Effective:** Immediately  
**Mandatory:** All Meridian 3.0 components

**This policy ensures Meridian maintains institutional-grade data quality.**

