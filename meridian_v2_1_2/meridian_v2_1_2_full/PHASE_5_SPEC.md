# 🚀 PHASE 5 — Quant Intelligence & Monte Carlo Engine

**Status:** 📋 READY FOR IMPLEMENTATION  
**Prerequisites:** Phase 4A + 4B Complete  
**Estimated Time:** 2-3 hours  
**Complexity:** Medium-High

---

## 🎯 **PHASE 5 GOALS:**

Transform Meridian from deterministic engine → **probabilistic research tool**

**New Capabilities:**
- Stress-test strategies under uncertainty
- Understand confidence intervals
- Score robustness systematically
- Blend multiple strategies
- Test stability under structural change
- Generate new strategies with AI prompting
- Rank and recommend best candidate versions

---

## 📦 **DELIVERABLES**

### **1️⃣ Monte Carlo Simulator**

**File:** `src/meridian_v2_1_2/simulation/monte_carlo.py`

**Function:**
```python
def monte_carlo_equity_simulation(equity_curve, n=500, block_size=20):
    """
    Perform block-bootstrap Monte Carlo simulations.
    
    Args:
        equity_curve: list or Series of equity values
        n: number of simulations
        block_size: number of consecutive steps per bootstrap block
    
    Returns:
        sims: list of simulated equity curves
        stats: confidence intervals, median final equity, drawdown distribution
    """
```

**Features:**
- Block bootstrap (preserves autocorrelation)
- Return simulations + distribution stats
- 95% confidence intervals
- Risk-of-ruin calculation
- Worst-case drawdown distribution

---

### **2️⃣ Walk-Forward Robustness Engine**

**File:** `src/meridian_v2_1_2/simulation/walk_forward.py`

**Function:**
```python
def walk_forward_validation(strategy_name, params, windows):
    """
    Iteratively train/test over rolling windows.
    
    Returns:
        results = {
            'train_metrics': [...],
            'test_metrics': [...],
            'windows': [...],
        }
    """
```

**Must Support:**
- Fixed-window validation
- Expanding-window validation
- Uses backtester inside each window
- Compares in-sample vs out-of-sample performance

---

### **3️⃣ Multi-Strategy Fusion**

**File:** `src/meridian_v2_1_2/strategy/fusion.py`

**Function:**
```python
def blend_equity_curves(curves, weights):
    """
    Combine multiple strategies using weights.
    Normalize weights.
    Return blended equity curve + combined metrics.
    """
```

**Features:**
- Weighted return fusion
- Weighted drawdown calculation
- Combined metrics
- Correlation-aware blending
- Portfolio-level statistics

---

### **4️⃣ Strategy Scoring Engine**

**File:** `src/meridian_v2_1_2/scoring/strategy_score.py`

**Function:**
```python
def score_strategy(metrics, mc_stats, wf_stats):
    """
    Calculate a composite score from:
      - CAGR
      - Max Drawdown
      - Sharpe-like ratio
      - Monte Carlo downside probability
      - Walk-forward stability
    
    Returns: float score (0-100)
    """
```

**Requirements:**
- Normalize all metrics
- Produce 0–100 score
- Make scoring weights editable
- Document scoring formula
- Penalize high variance
- Reward stability

---

### **5️⃣ Dashboard Page — "Monte Carlo & Robustness"**

**File:** `src/meridian_v2_1_2/dashboard/pages/07_Robustness.py`

**Features:**
- Select run from registry
- Monte Carlo simulation controls (n sims, block size)
- Visualizations:
  - **Confidence Interval Fan Chart** (Plotly)
  - **Risk-of-Ruin** gauge
  - **Distribution of worst-case drawdowns** (histogram)
- Walk-forward analysis:
  - Train/test windows selector
  - Bar charts for stability comparison
  - In-sample vs out-of-sample overlay
- **Strategy Score** display (0-100)
- Export robustness report (PDF/CSV)

**UI Components:**
```python
# Monte Carlo section
st.subheader("🎲 Monte Carlo Analysis")
n_sims = st.slider("Simulations", 100, 1000, 500)
block_size = st.slider("Block Size", 5, 50, 20)

if st.button("Run Monte Carlo"):
    # Run simulation
    # Display results
    pass

# Walk-forward section
st.subheader("📊 Walk-Forward Validation")
# Window controls
# Run and display
```

---

### **6️⃣ Notebook Editor Integration**

**File:** `src/meridian_v2_1_2/dashboard/pages/04_Notebook_Editor.py`

**Add Buttons:**
- **"🎲 Run Monte Carlo"** - Run MC on last backtest result
- **"📊 Insert Robustness Analysis"** - Add new cells with analysis
- **"🔀 Insert Walk-Forward"** - Add WF validation cells

**Implementation:**
```python
if st.button("🎲 Run Monte Carlo", key=f"mc_{idx}"):
    # Run MC on result stored in session
    from meridian_v2_1_2.simulation.monte_carlo import monte_carlo_equity_simulation
    mc_results = monte_carlo_equity_simulation(result.equity_curve)
    
    # Insert new cell with results
    new_cell = new_code_cell(f"# Monte Carlo Results\n{mc_results}")
    nb.cells.insert(idx + 1, new_cell)
    st.rerun()
```

---

### **7️⃣ AI Strategy Generator Scaffolding**

**File:** `src/meridian_v2_1_2/ai/strategy_suggester.py`

**Function:**
```python
def suggest_strategy_improvements(metrics, mc_stats, wf_stats):
    """
    Returns a dict of recommended improvements.
    
    Rule-based suggestions (NO external LLM calls yet):
    - If drawdown > 20% → "Tighten stop-loss"
    - If WF degradation > 30% → "Increase parameter stability"
    - If MC downside > 25% → "Add filtering rules"
    - If low Sharpe → "Review entry/exit logic"
    
    Returns:
        {
            'recommendations': List[str],
            'severity': 'low' | 'medium' | 'high',
            'score_impact': float
        }
    """
```

**This is a PLACEHOLDER for future GPT/Claude integration.**

For now, implement simple rule-based logic.

---

### **8️⃣ Visualization Components**

**File:** `src/meridian_v2_1_2/dashboard/components/mc_viz.py`

**Functions:**
```python
def plot_mc_fan_chart(simulations, actual_curve):
    """Plot MC simulations with confidence bands"""

def plot_drawdown_distribution(mc_drawdowns):
    """Histogram of MC drawdown scenarios"""

def plot_walk_forward_comparison(train_metrics, test_metrics):
    """Bar chart comparing in-sample vs out-of-sample"""

def plot_risk_gauge(risk_of_ruin):
    """Gauge chart showing risk level"""
```

Use **Plotly** for all charts.

---

### **9️⃣ Requirements Update**

Ensure in `requirements.txt`:
```
scipy>=1.11.0
```

No new dependencies required (all already present).

---

## ✔ **ACCEPTANCE CRITERIA**

### **Monte Carlo Engine:**
- ✅ Runs 500+ simulations
- ✅ Block bootstrap implemented
- ✅ Returns confidence intervals (5%, 50%, 95%)
- ✅ Calculates risk-of-ruin
- ✅ Deterministic with random seed

### **Walk-Forward Engine:**
- ✅ Supports fixed and expanding windows
- ✅ Compares train vs test metrics
- ✅ Detects overfitting (degradation > threshold)
- ✅ Returns window-by-window results

### **Strategy Fusion:**
- ✅ Blends multiple equity curves
- ✅ Calculates portfolio metrics
- ✅ Handles weights properly

### **Scoring Engine:**
- ✅ Produces 0-100 score
- ✅ Incorporates all metrics
- ✅ Configurable weights

### **Dashboard Page:**
- ✅ MC fan chart displays
- ✅ Risk gauge works
- ✅ WF charts display
- ✅ Score calculation visible
- ✅ Export functionality

### **Notebook Integration:**
- ✅ Can insert MC analysis
- ✅ Can insert WF analysis
- ✅ Results render properly

### **AI Suggester:**
- ✅ Rule-based suggestions work
- ✅ Returns actionable recommendations
- ✅ Ready for LLM integration (Phase 5B)

---

## 📊 **EXPECTED OUTPUTS**

### **Monte Carlo:**
- Simulated equity curves (500 paths)
- Confidence bands (5th, 50th, 95th percentile)
- Risk-of-ruin probability
- Expected final equity distribution
- Worst-case scenario identification

### **Walk-Forward:**
- Train/test split metrics per window
- Stability score
- Overfitting detection flag
- Degradation percentage
- Window-by-window visualization

### **Strategy Score:**
- Composite score (0-100)
- Component breakdown
- Ranking vs other strategies
- Improvement suggestions

---

## 🧪 **TESTING REQUIREMENTS**

Create: `tests/test_monte_carlo.py`

**Tests:**
1. Monte Carlo runs deterministically
2. Confidence intervals are reasonable
3. Block bootstrap preserves structure
4. Risk metrics calculated correctly

Create: `tests/test_walk_forward.py`

**Tests:**
1. Fixed window validation works
2. Expanding window works
3. Overfitting detection triggers correctly
4. Metrics align with backtester

Create: `tests/test_strategy_fusion.py`

**Tests:**
1. Blending weights normalized
2. Combined equity correct
3. Multiple strategies handled

---

## 📓 **NOTEBOOK INTEGRATION**

Phase 5 enables notebook cells like:

```python
# Run Monte Carlo Analysis
from meridian_v2_1_2.simulation.monte_carlo import monte_carlo_equity_simulation

mc_results = monte_carlo_equity_simulation(result.equity_curve, n=500)

print(f"95% CI: {mc_results['ci_95']}")
print(f"Risk of Ruin: {mc_results['risk_of_ruin']:.2%}")

# Plot results
from meridian_v2_1_2.dashboard.components.mc_viz import plot_mc_fan_chart
plot_mc_fan_chart(mc_results['simulations'], result.equity_curve)
```

---

## 🎯 **PHASE 5 ARCHITECTURE**

```
Phase 4 (Backtest Integration)
         ↓
Phase 5 (Robustness & Intelligence)
         ↓
    Monte Carlo ← equity curve
    Walk-Forward ← parameters
    Strategy Fusion ← multiple runs
    Scoring ← all metrics
         ↓
    Dashboard visualization
    Notebook embedding
    AI suggestions (rule-based)
         ↓
Phase 5B: Connect to GPT/Claude
```

---

## 🚀 **WHAT PHASE 5 ENABLES**

### **For Traders:**
- Understand strategy uncertainty
- See worst-case scenarios
- Validate robustness
- Compare strategies objectively

### **For Researchers:**
- Test parameter stability
- Identify overfitting
- Blend strategies scientifically
- Get automated improvement suggestions

### **For the Platform:**
- Probabilistic modeling foundation
- Ready for AI integration
- Portfolio optimization ready
- Risk management enhanced

---

## 📋 **IMPLEMENTATION ORDER**

**Cursor should build in this sequence:**

1. Monte Carlo module (core logic)
2. Walk-Forward module (validation)
3. Strategy Fusion (blending)
4. Scoring Engine (ranking)
5. Visualization components
6. Dashboard page (07_Robustness.py)
7. Notebook editor integration
8. AI suggester scaffolding
9. Tests
10. Documentation

**Estimated time:** 2-3 hours for full implementation

---

## 🎓 **LEARNING RESOURCES**

### **Monte Carlo:**
- Block bootstrap preserves time-series structure
- Critical for strategies with autocorrelated returns
- Standard in institutional quant research

### **Walk-Forward:**
- Gold standard for avoiding overfitting
- Used by professional systematic traders
- Separates luck from skill

### **Strategy Scoring:**
- Multi-objective optimization
- Combines return, risk, and stability
- Enables automated strategy selection

---

## ⚠️ **IMPORTANT NOTES**

### **Do NOT:**
- Call external APIs (GPT, Claude, etc.) yet
- Implement actual LLM integration (Phase 5B)
- Break backward compatibility
- Create new dependencies beyond scipy

### **DO:**
- Use existing backtester infrastructure
- Reuse visualization patterns
- Follow established architecture
- Write comprehensive tests
- Document everything

---

## 🎯 **PHASE 5B (FUTURE)**

After Phase 5 is complete, Phase 5B will:
- Connect to GPT-4/Claude API
- Generate actual strategy code
- Provide intelligent parameter suggestions
- Auto-document strategies
- Learn from backtest results

**But Phase 5 must work WITHOUT AI first!**

---

## ✅ **READY TO IMPLEMENT**

**When next agent is ready:**

1. Read `QUICK_START_FOR_NEW_AGENT.md`
2. Read `SESSION_SUMMARY.md`
3. Complete Phase 4 integration (1-2 hours)
4. Read this Phase 5 spec
5. Implement Phase 5 (2-3 hours)

---

## 🏆 **AFTER PHASE 5**

**Meridian becomes:**
- A complete quant intelligence platform
- Probabilistic research engine
- Multi-strategy optimizer
- Robustness validator
- AI-ready foundation

**Then Phase 6:** AI-Assisted Strategy Evolution

---

*Phase 5 Spec prepared: 2025-12-03*  
*Ready for: Next Implementation Session*  
*Status: ✅ SPECIFICATION COMPLETE*

