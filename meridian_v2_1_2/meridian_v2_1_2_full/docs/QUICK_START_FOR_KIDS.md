# 🌟 Meridian — Quick Start Guide (for 12-Year-Olds)

Welcome to **Meridian**, your very own *super-smart robot* that studies markets, finds patterns, and helps you understand how prices move — like a weather forecast, but for gold, stocks, and other markets.

This guide teaches you how to start it, use it, and see what it finds.

**No fancy math needed. Just follow the steps.** 👍

---

## 🧠 What Is Meridian?

Meridian is a **market analyzer**.

Think of it like:
- 🕵️ A **detective** looking for clues in price charts
- 🔬 A **scientist** measuring waves in the market
- 🔮 A **time traveler** guessing what might happen next
- 🏀 A **coach** whispering: "Buy here… maybe sell there…"

**Important:** Meridian never risks real money unless *you* decide. It's a learning tool!

---

## 🚀 How Do I Use Meridian?

Meridian runs inside **Docker**, which is like a magical box that keeps all the tools safe and organized.

**Before we start:** Make sure Docker is open.  
(You should see a little blue whale 🐳 icon on your screen.)

---

## 🔥 Step 1 — Start the System

**Open your Terminal** (the black window where you type commands) and type:

```bash
cd deploy
docker compose up -d
```

**What this does:**
- Turns on the **Brain** (API - the smart computer)
- Turns on the **Dashboard** (the pretty pictures you can see)
- Turns on the **Scheduler** (the thing that runs tasks every day)

**You'll see:**
```
✔ Container started
✔ Container started
```

That means it worked! 🎉

---

## 🌍 Step 2 — Open the Dashboard

**Open your web browser** (Chrome, Safari, Firefox) and go to:

👉 **http://localhost:8501**

**What you'll see:**
A cool-looking website with charts, numbers, and buttons!

It's like a little **NASA mission control**, but for trading markets.

---

## 🔍 Step 3 — Run a Market Analysis

**Back in your Terminal**, type this magic command:

```bash
docker compose run --rm meridian-scheduler
```

**What happens:**
- Meridian downloads REAL market data (like gold prices!)
- Checks for patterns and waves
- Predicts where prices might go
- Creates "signals" (suggestions)

**You'll see messages like:**
```
✅ PHASING OK
✅ FORECAST OK
✅ STRATEGY OK
✅ PIPELINE COMPLETE
```

**That means the robot finished its homework!** 🎓🤖

---

## 📊 Step 4 — Explore What Meridian Found

**Go back to your browser** (http://localhost:8501) and click through the pages in the sidebar:

### 🌀 **Cycle Health**
Shows how strong the market's "waves" are.  
(Markets move in waves, like ocean water!)

### 📈 **Intermarket Dashboard**
Shows how different markets affect each other.  
(Gold and the US Dollar often move opposite directions - cool, right?)

### 🔮 **Forecast Panel**
Shows where prices **might** go in the future.  
(Like a weather forecast - not perfect, but helpful!)

### 🎯 **Strategy Signals**
Shows suggestions:
- 🟢 "Maybe Buy"
- 🔴 "Maybe Sell"
- 🟡 "Maybe Hold" (do nothing)

### 🌍 **Macro Regime**
Tells you if the market is:
- 📈 **Trending** (going up or down strongly)
- 🌀 **Choppy** (bouncing back and forth)
- 🌪️ **Risky** (moving a lot!)
- 😴 **Calm** (not doing much)

---

## 🧪 Step 5 — Run It Again Tomorrow

**Every day**, you can run this again to update Meridian's "brain":

```bash
docker compose run --rm meridian-scheduler
```

The more you run it, the smarter it gets!

---

## 📝 Important Safety Notes

### 🛡️ **Safety First:**
- ✅ Meridian does **NOT** trade real money automatically
- ✅ Everything starts in **"practice mode"** (no real money)
- ✅ It's a tool for **learning**, not a get-rich-quick scheme
- ✅ No predictions are perfect — markets can be surprising!
- ✅ Always ask a grown-up before trading real money

### 🎓 **Learning Mode:**
Meridian is like a **flight simulator** for trading:
- You can practice without risk
- Learn how markets work
- Understand patterns
- Build skills
- Have fun!

---

## 🧊 Troubleshooting (Kid-Friendly)

### ❓ **Dashboard not showing anything?**
**Fix:** Restart it!
```bash
docker restart meridian-dashboard
```
Then reload your browser: http://localhost:8501

### ❓ **API not working?**
**Fix:** Restart it!
```bash
docker restart meridian-api
```

### ❓ **Got a red error message?**
**Don't panic!** It probably means:
- Not enough data loaded
- Docker needs more power
- Internet hiccup

**Try:** Run the scheduler command again

### ❓ **Everything is broken?**
**Nuclear option** (safe - just resets everything):
```bash
docker-compose down
docker-compose up -d
```

---

## 🎮 Fun Things to Try

### **Experiment #1: Compare Different Markets**
Upload multiple CSV files in the Intermarket Dashboard to see how they move together!

### **Experiment #2: Watch Cycles**
Look at the Cycle Health page and see if you can spot the waves in the price chart.

### **Experiment #3: Check Predictions**
Use the Forecast Terminal to see where Meridian thinks prices might go, then check back next week to see if it was right!

### **Experiment #4: Regime Detective**
Try to guess what regime the market is in (trending, choppy, risky?) BEFORE checking the Macro Regime page. See if you agree with the robot!

---

## 🏆 You Did It!

**You now know how to:**
- ✅ Turn on the system
- ✅ Analyze real markets
- ✅ View cycles & forecasts
- ✅ Explore trading signals
- ✅ Use the dashboard
- ✅ Run it every day

**You're officially a Junior Quant Operator!**

**Nice work!** 🚀📈

---

## 🎓 What You're Learning

By using Meridian, you're learning:
- 📊 How markets work
- 🔄 What cycles are
- 🤖 How AI can help analyze data
- 📈 How trading works (safely!)
- 💡 Critical thinking about money
- 🧪 Scientific method (test ideas!)

**These are valuable skills for life!**

---

## 📚 Want to Learn More?

### **Easy Level:**
- Play with the dashboard every day
- Watch how predictions turn out
- Learn to spot cycles in charts

### **Medium Level:**
- Read `FIRST_REAL_DATA_RUN.md`
- Try different market symbols
- Understand regime types

### **Hard Level:**
- Read the stage guides
- Learn about the code
- Try modifying strategies

**Start easy, level up when ready!**

---

## 🎨 Make It Your Own

Meridian is **open source** - that means you can:
- Change how it looks
- Add new features
- Create your own strategies
- Share improvements
- Learn by building

**Coding is creating. Have fun with it!**

---

## 🌟 One More Thing

**Meridian was built to be:**
- Educational 🎓
- Safe 🛡️
- Powerful 💪
- Fun 🎉

**Use it to learn, not to gamble.**

**Markets are cool to study, risky to trade.**

**Always learn first, trade later (with grown-up permission!).**

---

## 🎊 You're Ready!

**Meridian is waiting for you.**

**Go explore!** 🚀

---

**Guide Version:** Kid-Friendly 1.0  
**Age:** 12+  
**Difficulty:** Easy  
**Time:** 10 minutes to start  
**Fun Level:** 🌟🌟🌟🌟🌟

**Made with ❤️ by the Meridian Team**

````

---

Want me to also generate:

👉 **A one-page PDF cheat sheet** (printable)

👉 **A Meridian "Explain Like I'm 5" version** (even simpler!)

👉 **A YouTube script** (if you wanted to make a video tutorial)

👉 **An interactive web tutorial** (HTML+CSS)

Just say the word!

