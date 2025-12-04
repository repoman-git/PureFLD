# 🌟 Meridian — Quick Start Guide for Two ETFs

### (For Smart 12-Year-Olds Who Want to Compare Markets)

Welcome back, Junior Quant Navigator! 🧠🚀

Now that you learned how to study **one** ETF (like GLD), today we're **leveling up**:

**You're going to study TWO ETFs at the same time.**

This teaches you how markets "talk to each other" — something even adults struggle with.

**Let's go!** 💪📈

---

## 🧠 What You Need to Know First

ETFs are like baskets of things:

- **GLD** 🥇 = a basket that follows gold
- **SPY** 📈 = a basket of the biggest U.S. companies (S&P 500)
- **QQQ** 💻 = tech companies (like Apple, Google, Microsoft)
- **SLV** 🥈 = silver
- **DXY** 💵 = US dollar strength
- **TLT** 📊 = long-term bonds (safe investments)

### **Why Study TWO ETFs?**

When you study TWO ETFs together, you discover:
- How they **move together** (correlation)
- How they **move opposite** (inverse relationship)
- Which one **leads** and which one **follows**
- Which one is acting **weird** today

**Meridian helps you discover these patterns automatically!**

---

## 🎮 The Classic Pairs to Try

### **🥇 GLD vs 📈 SPY** (Gold vs Stocks)
- **The classic "fear vs optimism" pair**
- When people are scared → buy gold (GLD up)
- When people are confident → buy stocks (SPY up)
- They often move opposite!

### **🥇 GLD vs 🥈 SLV** (Gold vs Silver)
- **The precious metal siblings**
- Usually move together
- When they disagree → something interesting is happening!

### **💻 QQQ vs 📊 TLT** (Tech vs Bonds)
- **Risk-on vs Risk-off**
- Tech = exciting but risky
- Bonds = boring but safe
- Shows market confidence level

### **📈 SPY vs 💵 DXY** (Stocks vs Dollar)
- The dollar affects everything
- Strong dollar → stocks might struggle
- Weak dollar → stocks might rise

---

## 🐳 Step 1 — Start the Meridian Machine

**Open Terminal** and type:

```bash
cd deploy
docker compose up -d
```

**This wakes up:**
- The **Brain** (API)
- The **Dashboard** (charts)
- The **Robot Worker** (analyzer)

**Wait 5-10 seconds for everything to start.**

---

## 🌐 Step 2 — Open Mission Control

**Open your browser** and go to:

👉 **http://localhost:8501**

This is where you'll see everything Meridian discovers!

---

## 🎯 Step 3 — Tell Meridian to Study TWO ETFs

We'll use **GLD** (gold) and **SPY** (stocks) — the classic pair!

**In Terminal, run:**

```bash
docker compose run --rm meridian-scheduler
```

**What happens:**

Meridian automatically analyzes multiple symbols:
- Downloads GLD data
- Downloads SPY data
- Compares their cycles
- Checks correlations
- Forecasts both
- Finds patterns

**You'll see:**
```
✅ LOADING DATA FOR: GLD
✅ LOADING DATA FOR: SPY
✅ CYCLE ANALYSIS OK
✅ INTERMARKET OK
✅ FORECAST OK
✅ PIPELINE COMPLETE
```

**You just ran a multi-market analysis like a pro!** 🙌

---

## 📊 Step 4 — Explore Two-ETF Analysis

**Go back to:** http://localhost:8501

**Now the fun part - exploring the comparisons!**

---

### 🌀 **1. Cycle Health (Compare Both)**

**What to look for:**
- Are both in strong cycles? (good!)
- Is one choppy while the other is smooth? (interesting!)
- Is one hitting a peak while the other hits a trough? (opportunity!)

**Example:**
```
GLD: Strong cycle (80%)
SPY: Weak cycle (35%)
```
**Meaning:** Gold patterns are clearer than stock patterns right now.

**This reveals cross-market timing!**

---

### 📈 **2. Intermarket Dashboard** ⭐ **THE MAGIC PAGE!**

This is where comparing two ETFs becomes **AWESOME**.

**What you'll see:**

#### 🔹 **Correlation Heatmap**
Shows how markets move together:
- **+1.0** = Perfect positive (move together)
- **0.0** = No relationship
- **-1.0** = Perfect negative (move opposite)

**Example:**
```
GLD vs SPY: -0.65 (often opposite)
```
**Meaning:** When gold rises, stocks often fall!

#### 🔹 **Cycle Phase Alignment**
Shows if markets are in sync:
- Both at peak = risky time
- One peak, one trough = normal
- Both at trough = potential opportunity

#### 🔹 **Lead/Lag Ranking**
The most powerful feature! Shows:
- Which ETF moves **first** (the leader)
- Which ETF reacts **later** (the follower)
- Which one is doing something **unexpected**

**Example:**
```
LEADER:   GLD (moves first)
FOLLOWER: SPY (reacts 2-3 days later)
```

**This page alone teaches more about markets than most adults know!**

---

### 🔮 **3. Forecast Terminal (Both ETFs)**

Meridian shows forecast cones for **BOTH** ETFs!

**Cool questions to ask:**
- Does GLD look like it wants to rise while SPY falls?
- Are both heading up together?
- Are both uncertain (wide cones)?
- Is one forecast confident while the other is uncertain?

**Example interpretation:**
```
GLD forecast: Narrow cone pointing up (confident bullish)
SPY forecast: Wide cone pointing down (uncertain bearish)
```
**Meaning:** Gold looks more predictable and positive right now!

---

### 🎯 **4. Strategy Signals (Compare Both)**

Shows buy/sell ideas for **BOTH** ETFs.

**You might see:**

| ETF | Signal | Confidence |
|-----|--------|------------|
| GLD | 🟢 Maybe BUY | High |
| SPY | 🟡 Maybe HOLD | Medium |

**What this means:**
- Gold has a better opportunity right now
- Stocks are uncertain - wait and watch

**Signals differ when ETFs behave differently — that's the valuable insight!**

---

### 🌍 **5. Macro Regime Monitor (Compare Both)**

Shows the "mood" of each market:

**Possible combinations:**
```
GLD: TRENDING (strong move)
SPY: CHOPPY (indecisive)
```
**Meaning:** Gold has clear direction, stocks are confused.

```
GLD: VOLATILE (risky)
SPY: COMPRESSED (calm)
```
**Meaning:** Gold is wild, stocks are quiet.

**You can see which market is safer or more interesting!**

---

## 🔁 Step 5 — Run It Daily

**Make it a habit!**

Every morning, run:

```bash
docker compose run --rm meridian-scheduler
```

**This updates BOTH ETFs:**
- Latest prices
- New cycles
- Updated forecasts
- Fresh correlations
- New signals
- Current relationships

**Now you're doing what real hedge funds do!**

---

## 🧪 Super Fun Experiments

### **Experiment #1: The Correlation Detective**
1. Write down GLD and SPY's correlation today
2. Track it for a week
3. When does it change?
4. What news caused it?

### **Experiment #2: Lead/Lag Investigation**
1. Check which ETF is the leader
2. Watch the leader for signals
3. See if the follower copies it 2-3 days later
4. Count how many times it works!

### **Experiment #3: Opposite Day**
1. Find two ETFs with negative correlation
2. When one says "BUY", does the other say "SELL"?
3. Track how often they disagree
4. Learn why they move opposite!

### **Experiment #4: Forecast Race**
1. Look at both forecasts on Monday
2. Guess which will be more accurate
3. Check on Friday
4. Score yourself!

### **Experiment #5: Regime Mix**
1. GLD = TRENDING, SPY = CHOPPY
2. Which one should you watch more?
3. Track your decision
4. See if you were right!

---

## 🎓 What You're Learning

By comparing two ETFs, you're learning:

1. **Correlation** - How markets relate to each other
2. **Lead/Lag** - Which markets move first
3. **Divergence** - When markets disagree
4. **Regime Differences** - Why some markets are clearer
5. **Portfolio Thinking** - Not putting all eggs in one basket
6. **Risk Management** - Understanding market relationships
7. **Advanced Analytics** - Multi-market thinking

**These are professional quant skills!**

---

## 📝 Pro Tips for Market Detectives

### **✔ Tip #1: Gold vs Stocks = Classic Combo**
They often move opposite — like fire and ice.  
When scared → people buy gold  
When confident → people buy stocks

### **✔ Tip #2: Silver vs Gold = Siblings**
Usually move together.  
When they disagree → dig deeper, something's up!

### **✔ Tip #3: Tech vs Bonds = Fear Index**
Tech up + Bonds down = Confidence!  
Tech down + Bonds up = Fear!

### **✔ Tip #4: Dollar vs Everything**
The US Dollar (DXY) affects almost everything.  
Strong dollar → Gold might fall  
Weak dollar → Gold might rise

### **✔ Tip #5: Watch the Leader**
If GLD leads SPY, watch GLD first!  
It might tell you where SPY is going next.

---

## 🧊 Quick Troubleshooting

### ❓ **One ETF is missing?**
```bash
# Run scheduler again
docker compose run --rm meridian-scheduler
```

### ❓ **Cycles look empty?**
Data might not have downloaded. Try once more!

### ❓ **Dashboard blank?**
```bash
docker restart meridian-dashboard
```
Then reload: http://localhost:8501

### ❓ **"DATA ERROR" for an ETF?**
You picked an ETF without data back to year 2000.

**Safe choices:**
- SPY ✅
- GLD ✅
- QQQ ✅
- SLV ✅
- TLT ✅

### ❓ **Intermarket page empty?**
Make sure you ran the scheduler with multiple symbols!

---

## 🏆 Achievement Unlocked!

**You learned how to:**
- ✅ Start Meridian
- ✅ Analyze TWO ETFs simultaneously
- ✅ Compare market movements
- ✅ Read cycle differences
- ✅ Understand correlations
- ✅ Identify lead/lag relationships
- ✅ Spot divergences
- ✅ Compare forecasts
- ✅ See regime differences
- ✅ Think like a portfolio manager

**You're now a Junior Quant Analyst Level 2!**

**Fantastic work!** 🚀📈✨

---

## 🎮 Level Up Challenges

### **Level 2: Easy**
- Compare GLD and SLV (the metal siblings)
- Track their correlation for a week
- Spot when they disagree

### **Level 3: Medium**
- Add QQQ (tech) to your GLD/SPY analysis
- Find which one leads
- Predict movements

### **Level 4: Hard**
- Study GLD, SPY, TLT, and DXY together
- Map their relationships
- Build a correlation web
- Understand the full market picture

---

## 🌟 The Best ETF Pairs for Learning

### **Beginner Pairs:**
1. **GLD vs SLV** - Similar metals (easy)
2. **SPY vs QQQ** - Broad vs tech stocks (medium)

### **Intermediate Pairs:**
3. **GLD vs SPY** - Safe vs risky (classic!)
4. **QQQ vs TLT** - Growth vs safety
5. **SPY vs DXY** - Stocks vs dollar

### **Advanced Pairs:**
6. **GLD vs DXY** - Gold vs dollar (inverse!)
7. **QQQ vs VIX** - Tech vs fear index
8. **TLT vs DXY** - Bonds vs dollar

**Start easy, level up when ready!**

---

## 💡 Real-World Applications

### **What Professionals Do:**
- Hedge funds compare 100+ markets
- They find opportunities in relationships
- They spot when correlations break
- They use lead/lag for timing

### **What You're Learning:**
- The exact same concepts!
- Just starting with 2 ETFs
- Building to more complex analysis
- Developing professional skills

**You're on the path to becoming a real quant!**

---

## 🎊 One More Thing

**Comparing markets is powerful because:**

1. **Diversification** - Don't put all eggs in one basket
2. **Opportunity** - When one market is unclear, another might be obvious
3. **Confirmation** - When both agree, the signal is stronger
4. **Divergence** - When they disagree, something interesting is happening
5. **Risk** - Understanding correlations helps manage risk

**This is how professional traders think!**

---

## 📚 Next Steps

**Master Two ETFs First:**
- Spend 2-3 weeks on GLD vs SPY
- Really understand their relationship
- Get comfortable with all the pages

**Then Expand:**
- Add a third ETF
- Try different pairs
- Build your own theories
- Test your predictions

**Eventually:**
- Study 5+ markets
- Build a full dashboard
- Track your accuracy
- Maybe even paper trade!

---

## 🏁 You're Ready!

**You now have the tools to:**
- Compare any two markets
- Understand their relationships
- Spot opportunities
- Think like a portfolio manager
- Build real quantitative skills

**This is serious stuff - and you're learning it at 12!**

**Amazing work!** 🎉🏆🚀

---

**Guide Version:** Two ETF Edition  
**Target Age:** 12+  
**Difficulty:** Intermediate  
**Markets:** GLD + SPY (or any pair)  
**Time:** 15 minutes per day  
**Fun Level:** 🌟🌟🌟🌟🌟

**Happy Multi-Market Exploring!** 🚀

---

**P.S.** Want the "Three ETF Guide" next? Or a "Top 10 ETF Cheat Sheet"?  
Just ask - I'll make it! 😊

