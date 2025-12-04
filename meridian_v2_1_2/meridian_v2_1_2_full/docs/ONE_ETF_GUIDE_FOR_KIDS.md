# ⭐ Meridian — How to Use the System

### (One ETF Edition — For Smart 12-Year-Olds)

Welcome to **Meridian**, your super-smart robot helper that studies markets and shows you cool patterns.

Today, we'll learn how to make Meridian study **ONE ETF** — we'll use **GLD** (the Gold ETF) — just to keep things simple and fun.

**You can later try SPY (S&P 500), QQQ, SLV, or anything else you like!**

---

## 🧠 What Is an ETF?

An ETF is sort of like:
- 🎴 A *basket* of stuff (like a Pokémon deck)
- 📈 That trades on the stock market
- 💰 And changes price every day

**GLD** = a basket that tries to follow the price of **gold**.

Meridian helps you "read the waves" of GLD to understand how it moves.

---

## 🐳 Step 1 — Turn On the Meridian Machine

**Open your Terminal** (the black window) and type:

```bash
cd deploy
docker compose up -d
```

**What this does:**
- Starts the **Brain** (API)
- Starts the **Dashboard** (pretty pictures)
- Starts the **Data Loader** (gets market info)
- Starts the **Robot Worker** (does the analysis)

**You'll see:**
```
✔ Container started
✔ Container started
```

**That means success!** 🎉

---

## 🌐 Step 2 — Open Meridian on Your Computer

**Open your web browser** and go to:

👉 **http://localhost:8501**

This is your **Mission Control** for studying markets!

**You'll see different pages like:**
- 🌀 Cycle Health
- 🔮 Forecasts
- 🎯 Strategy Signals
- 📈 Intermarket Dashboard

**(All super cool. We'll explore them in a minute.)**

---

## 🎯 Step 3 — Tell Meridian to Study GLD

**Back in your Terminal**, type this magic command:

```bash
docker compose run --rm meridian-scheduler
```

**What Meridian does now:**
1. 📥 Downloads GLD's price history (going back to year 2000!)
2. 🔄 Looks for cycles (repeating patterns)
3. 🔮 Builds a forecast (guesses where it might go)
4. ⚠️ Measures risk (how "bouncy" it is)
5. 🎯 Creates signals (buy/sell ideas)
6. 💾 Saves everything so you can see it

**You'll see messages:**
```
✅ PHASING OK
✅ FORECAST OK
✅ STRATEGY OK
✅ PIPELINE COMPLETE
```

**That means: Meridian finished studying GLD!** 🎓🤖

---

## 📊 Step 4 — See What Meridian Discovered About GLD

**Go back to your browser:** http://localhost:8501

**Let's explore the coolest pages:**

---

### 🌀 **Page: Cycle Health**

**What it shows:** How strong GLD's "waves" are

**How to read it:**
- 🟢 High strength = clear patterns
- 🟡 Medium strength = okay patterns
- 🔴 Low strength = messy, hard to predict

**Why it matters:**  
When cycles are strong, Meridian's predictions are more reliable!

---

### 🔮 **Page: Forecast Terminal**

**What it shows:** Where GLD **might** go in the future

**How to read it:**
- You'll see a chart with a "cone" shape
- The middle line = most likely path
- The cone = range of possibilities
- Bigger cone = more uncertainty

**Remember:**  
This is like a weather forecast - helpful but not perfect!

---

### 🎯 **Page: Strategy Signals**

**What it shows:** Trading ideas from Meridian

**Possible signals:**
- 🟢 "Maybe Buy" - GLD might go up
- 🔴 "Maybe Sell" - GLD might go down
- 🟡 "Maybe Hold" - wait and see

**Important:**  
These are just *ideas*, not orders. Always learn first!

---

### ⚠️ **Page: Volatility & Risk**

**What it shows:** How "jumpy" GLD is

**Numbers to watch:**
- **ATR** - Average True Range (how much it moves daily)
- **Volatility** - How wild the price swings are
- **Risk Score** - Overall riskiness

**Think of it like:**
- Low volatility = calm ocean 🌊
- High volatility = stormy seas ⛈️

---

### 🌍 **Page: Macro Regime Monitor**

**What it shows:** The overall "mood" of the market

**5 Possible Moods:**
1. 📈 **TRENDING** - Going strong in one direction
2. 🌀 **CYCLICAL** - Moving in waves (best for analysis!)
3. 🌪️ **VOLATILE** - Wild and jumpy
4. 😴 **COMPRESSED** - Quiet, building up energy
5. 🔄 **RESETTING** - Taking a break, reorganizing

**Why it matters:**  
Meridian works best when markets are CYCLICAL!

---

## 🔁 Step 5 — Study GLD Every Day

**Make it a habit!**

Each morning (or evening), run:

```bash
docker compose run --rm meridian-scheduler
```

**This updates:**
- Latest GLD price
- New cycle analysis
- Updated forecasts
- Fresh strategy ideas
- Current risk levels

**It's like giving Meridian's brain new information to think about!**

---

## 🧪 Fun Experiments to Try

### **Experiment #1: Can You Predict the Mood?**
Before checking the Macro Regime page, look at the price chart and guess:
- Is it trending?
- Is it choppy?
- Is it risky?

Then check if you match Meridian! 🎯

### **Experiment #2: Test the Forecast**
Look at today's forecast cone. Write down where you think GLD will be in 1 week.  
Check back next week - were you (and Meridian) close?

### **Experiment #3: Cycle Detective**
Look at the Cycle Health page. Can you see the "waves" in the price chart?  
Try to spot where cycles are strongest!

### **Experiment #4: Compare to Reality**
When Meridian says "Maybe Buy", track what actually happens over the next few days.  
Keep a journal of hits and misses!

---

## 📝 Important Safety Rules

### 🛡️ **Remember:**
- ✅ Meridian does **NOT** trade real money automatically
- ✅ Everything is in **"practice mode"** by default
- ✅ This is a **learning tool**, not a money machine
- ✅ Markets can be surprising - no robot is perfect!
- ✅ Always ask a grown-up before using real money

### 🎓 **Learning Mode:**
Think of Meridian like:
- 🎮 A flight simulator (practice flying without crashing)
- 🎯 A sports coach (gives you plays to try)
- 🧪 A science lab (experiment safely!)

**You're learning real skills - that's the valuable part!**

---

## 🎮 Make It More Fun

### **Give GLD a Nickname:**
Call it "Goldie" and track its adventures!

### **Create a Journal:**
Write down:
- Date
- What Meridian predicted
- What actually happened
- What you learned

### **Set Goals:**
- Can you spot 3 cycles in one month?
- Can you correctly identify the regime?
- Can you understand the forecast cone?

### **Challenge Yourself:**
Once you master GLD, try:
- SLV (Silver)
- SPY (S&P 500)
- QQQ (Nasdaq tech stocks)

---

## 🔧 Quick Fixes (When Things Go Wrong)

### ❓ **Dashboard won't open?**
```bash
docker restart meridian-dashboard
```
Then try http://localhost:8501 again

### ❓ **Says "Cannot load GLD"?**
The internet might be slow. Wait 30 seconds and try again.

### ❓ **Red error message?**
Don't worry! It usually means:
- Not enough history loaded
- Internet hiccup
- Docker needs restart

**Fix:** Run the scheduler command again

### ❓ **Everything is broken?**
**Emergency reset:**
```bash
docker-compose down
docker-compose up -d
```
This is like turning it off and on again - usually fixes everything!

---

## 🏆 Your Mission (If You Choose to Accept)

### **Week 1: Learn the Basics**
- [ ] Start Meridian
- [ ] Load GLD data
- [ ] Explore all 9 dashboard pages
- [ ] Understand what each page shows

### **Week 2: Become a Pattern Detective**
- [ ] Run Meridian daily
- [ ] Try to spot cycles yourself
- [ ] Compare your predictions to Meridian's
- [ ] Keep a journal

### **Week 3: Go Multi-Market**
- [ ] Try a second ETF (SPY or SLV)
- [ ] Compare how they move differently
- [ ] Look at correlations

### **Week 4: Junior Analyst**
- [ ] Understand all 5 regime types
- [ ] Make your own forecasts
- [ ] See how accurate Meridian is
- [ ] Decide if you want to learn more!

---

## 🎓 What You're Actually Learning

By using Meridian with GLD, you're learning:

1. **Data Science** - How to analyze big datasets
2. **Pattern Recognition** - Seeing cycles and trends
3. **Critical Thinking** - Testing predictions
4. **Risk Management** - Understanding danger vs safety
5. **Technology** - Using Docker, APIs, dashboards
6. **Finance** - How markets actually work

**These skills are super valuable for your future!**

---

## 🌟 Pro Tips

### **Tip #1: Be Patient**
Markets don't move on your schedule. Some days are boring!

### **Tip #2: Ask Questions**
If something doesn't make sense, ask! That's how you learn.

### **Tip #3: Compare to Real News**
When gold prices jump, check the news. What caused it?

### **Tip #4: Don't Rush**
Spend a month just watching before making any decisions.

### **Tip #5: Have Fun!**
Markets are like puzzles. Enjoy solving them!

---

## 🎉 You're Ready!

**You now know how to:**
- ✅ Start Meridian
- ✅ Study ONE ETF (GLD)
- ✅ Read cycles and forecasts
- ✅ Understand signals
- ✅ Use the dashboard
- ✅ Update daily
- ✅ Fix problems

**Welcome to the world of quantitative analysis!**

**You're now a Junior Market Scientist!** 🔬📈

---

## 🚀 Next Adventures

Once you're comfortable with GLD:

### **Easy:**
- Try SLV (Silver) - it's like GLD's cousin
- Try SPY (whole stock market) - bigger and more famous
- Compare GLD and SLV together (intermarket!)

### **Medium:**
- Learn about the 5 regime types
- Understand what cycles mean
- Read about forecasting

### **Hard:**
- Try pairs trading (comparing two markets)
- Learn about the code
- Build your own strategy ideas

**Level up at your own pace!**

---

## 💡 Remember

**Meridian is a tool, not magic.**

It can't predict the future perfectly - nobody can!

But it CAN:
- Show you patterns
- Help you think clearly
- Teach you how markets work
- Make learning fun

**Use it wisely, learn lots, and enjoy the journey!**

---

## 🎊 One More Thing

**Why GLD?**
- Gold has been around forever
- It has clear cycles
- It's easy to understand ("shiny metal")
- It doesn't move TOO crazy
- It's a great learning market

**Perfect for beginners!**

---

**Guide Version:** One ETF Edition  
**Target Age:** 12+  
**Difficulty:** Beginner  
**Market:** GLD (Gold ETF)  
**Time:** 10 minutes per day  
**Fun Level:** 🌟🌟🌟🌟🌟

**Happy Trading (Paper Mode)!** 🎉

---

**P.S.** Always remember: Real trading = real risk. Learn first, trade later (with grown-up permission)!

