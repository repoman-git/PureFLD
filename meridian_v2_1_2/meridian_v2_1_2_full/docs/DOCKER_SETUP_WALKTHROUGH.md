# 🐳 Meridian 3.0 — Docker Setup Walkthrough

**Complete hands-on guide to get Meridian running**

**Platform:** Mac OS, Windows WSL, Linux  
**Time:** 15-20 minutes  
**Difficulty:** Easy  
**Prerequisites:** Docker Desktop installed

---

## ✅ **STEP 1 — Ensure Docker Desktop Is Running**

### **Mac (Intel/M1/M2/M3):**

**Install Docker Desktop:**  
https://www.docker.com/products/docker-desktop/

**Once installed:**
- Make sure it's **running** (you'll see the whale 🐳 in menu bar)
- Open Docker Desktop and ensure engine is started

### **Verify from Terminal:**
```bash
docker --version
# Should show: Docker version 20.x or higher

docker compose version
# Should show: Docker Compose version v2.x or higher
```

**If either fails:**
- Restart your machine
- Relaunch Docker Desktop
- Try again

---

## ✅ **STEP 2 — Navigate to Meridian Project**

```bash
cd /Users/simonerses/Data-Projects-PureFLD/meridian_v2_1_2/meridian_v2_1_2_full
```

### **Verify Directory Structure:**
```bash
ls -la

# Should see:
# - deploy/
# - src/
# - meridian_app/
# - tests/
# - docs/
# - requirements.txt
```

### **Check Deploy Folder:**
```bash
ls deploy/

# Should see:
# - docker-compose.yml
# - Dockerfile.api
# - Dockerfile.app
# - .env.example
# - README_DEPLOY.md
```

**If everything's in place → proceed!**

---

## ✅ **STEP 3 — Create Environment Configuration**

### **Copy Template:**
```bash
cp deploy/.env.example deploy/.env
```

### **Edit Configuration:**
```bash
# Open in your editor
nano deploy/.env

# Or
code deploy/.env
```

### **Minimal Configuration:**
```bash
# Required
MERIDIAN_ENV=production
MERIDIAN_LOG_LEVEL=info

# Data source
DATA_SOURCE=yfinance

# Data policy
MIN_START_YEAR=2000

# Optional: Paper trading (leave blank for now)
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
ALPACA_ENDPOINT=https://paper-api.alpaca.markets
ENABLE_PAPER_TRADING=false
```

**Save and exit.**

---

## ✅ **STEP 4 — Build Docker Containers**

### **Navigate to Deploy:**
```bash
cd deploy
```

### **Build All Containers:**
```bash
docker-compose build
```

**This will:**
- Create the API image (~2-3 minutes)
- Create the Dashboard image (~2-3 minutes)
- Install all Python dependencies
- Set up the runtime environment

**Expected Output:**
```
[+] Building 150.2s (15/15) FINISHED
...
Successfully built xxxxx
Successfully tagged deploy-api:latest
Successfully tagged deploy-app:latest
```

**If you see errors:**
- Check Docker has enough resources (Settings → Resources → 4GB RAM minimum)
- Ensure internet connection is stable
- Try: `docker-compose build --no-cache`

---

## ✅ **STEP 5 — Start the System**

### **Launch Containers:**
```bash
docker-compose up -d
```

**Expected Output:**
```
[+] Running 3/3
 ✔ Network deploy_default    Created
 ✔ Container deploy-api-1    Started
 ✔ Container deploy-app-1    Started
```

### **Verify Running:**
```bash
docker ps

# Should show 2 containers:
# - deploy-api-1 (port 8000)
# - deploy-app-1 (port 8501)
```

---

## ✅ **STEP 6 — Validate Services**

### **Test API:**
```bash
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"2.0.0","uptime_seconds":...}
```

### **Open API Documentation:**
Open browser: http://localhost:8000/docs

**You should see:** FastAPI Swagger UI with 8 endpoints

### **Open Dashboard:**
Open browser: http://localhost:8501

**You should see:** Meridian v2.1.2 - Quant Cycle Intelligence Platform

**If both work → SUCCESS!** ✅

---

## ✅ **STEP 7 — Run First Pipeline Test**

### **Execute Pipeline:**
```bash
docker-compose run --rm meridian-scheduler
```

**This will:**
1. Initialize all engines
2. Fetch real market data (enforces year ≥ 2000)
3. Run cycle phasing
4. Classify regime
5. Store results

**Expected Output:**
```
Phase 1: Cycle Analysis...
Phase 2: Regime Classification...
Phase 3: Storing results...
✅ Pipeline complete!
```

**If successful:**
- Results stored in `../meridian_local/meridian.db`
- Logs in `../meridian_local/logs/`

---

## ✅ **STEP 8 — Explore the Dashboard**

### **Access Dashboard:**
http://localhost:8501

### **Navigate Through All 9 Pages:**
1. **Main Page** - Overview
2. **1_Cycle_Overview** - Upload CSV and analyze
3. **2_Regime_Classifier** - ML regime detection
4. **3_Execution_Monitor** - Trading status
5. **4_Intermarket_Dashboard** - Multi-market analysis
6. **5_Cycle_Health** - Cycle strength monitoring
7. **6_Volatility_Terminal** - ATR and risk metrics
8. **7_Forecast_Terminal** - Ensemble predictions
9. **8_Strategy_Signals** - Trading signals
10. **9_Macro_Regime** - Regime monitoring

**Test:** Upload a sample CSV (timestamp, price columns) to see charts!

---

## ✅ **STEP 9 — (Optional) Configure Paper Trading**

### **Get Alpaca Account (FREE):**
1. Visit: https://alpaca.markets
2. Sign up for paper trading (free)
3. Get API keys from dashboard

### **Configure Meridian:**
Edit `deploy/.env`:
```bash
ENABLE_PAPER_TRADING=true
ALPACA_API_KEY=your_paper_key_here
ALPACA_SECRET_KEY=your_paper_secret_here
ALPACA_ENDPOINT=https://paper-api.alpaca.markets
```

### **Restart Services:**
```bash
docker-compose down
docker-compose up -d
```

### **Execute Paper Trade:**
```bash
docker-compose run --rm meridian-scheduler
```

**Check Alpaca dashboard for orders!**

---

## ✅ **STEP 10 — View Logs**

### **Application Logs:**
```bash
cd ..  # Back to project root
tail -f meridian_local/logs/pipeline.log
```

### **Container Logs:**
```bash
cd deploy
docker logs meridian-api -f

# Or
docker logs meridian-dashboard -f
```

### **Check for Errors:**
```bash
grep ERROR meridian_local/logs/*.log
```

**If empty → all good!**

---

## 🧪 **STEP 11 — Run Integration Tests**

### **Test Everything:**
```bash
cd ..  # Project root
source .venv/bin/activate
PYTHONPATH="$PWD/src:$PYTHONPATH" python tests/integration/meridian_integration_test_v2.py
```

**Expected:**
```
✅ Passed: 16
❌ Failed: 0
📊 Total: 16

🎊 ALL TESTS PASSED!
```

---

## 🔧 **QUICK TROUBLESHOOTING**

### **Problem:** Containers won't start
**Solution:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **Problem:** API returns errors
**Solution:**
```bash
docker restart meridian-api
docker logs meridian-api --tail 50
```

### **Problem:** Dashboard shows blank pages
**Solution:**
```bash
docker restart meridian-dashboard
# Check API is accessible: curl http://localhost:8000/health
```

### **Problem:** Port already in use
**Solution:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

---

## 📋 **Daily Operations Checklist**

### **Morning Startup:**
```bash
# 1. Start Docker Desktop (if not running)
# 2. Start containers
cd deploy && docker-compose up -d

# 3. Verify health
curl http://localhost:8000/health

# 4. Run daily pipeline
docker-compose run --rm meridian-scheduler

# 5. Check dashboard
# Open http://localhost:8501
```

### **Evening Shutdown (Optional):**
```bash
# Save resources when not in use
docker-compose down
```

---

## 🎯 **Success Criteria**

**You've successfully set up Meridian 3.0 when:**
- ✅ Docker containers build without errors
- ✅ API responds at http://localhost:8000
- ✅ Dashboard loads at http://localhost:8501
- ✅ Pipeline executes successfully
- ✅ Logs show no errors
- ✅ Integration tests pass
- ✅ All 9 dashboard pages load

---

## 🚀 **Next Steps**

### **Now That It's Running:**
1. ✅ Review `FIRST_REAL_DATA_RUN.md` for detailed workflow
2. ✅ Read `DOCKER_OPERATOR_HANDBOOK.md` for operations
3. ✅ Experiment with different markets
4. ✅ Test regime classification
5. ✅ Try pairs trading analysis
6. ✅ Configure paper trading
7. ✅ Monitor performance

### **Advanced:**
- Deploy to GCP/Azure (see `deploy/README_DEPLOY.md`)
- Set up monitoring
- Configure automated scheduling
- Build Stage 11 (Cycle-Liquidity Model)

---

## 🏆 **You're Live!**

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🎊 MERIDIAN 3.0 IS OPERATIONAL 🎊                        ║
║                                                                  ║
║    Docker: Running ✅                                            ║
║    API: Healthy ✅                                               ║
║    Dashboard: Loaded ✅                                          ║
║    Pipeline: Executing ✅                                        ║
║                                                                  ║
║         READY FOR REAL MARKET ANALYSIS                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**Congratulations! Meridian 3.0 is now running on your machine!**

**You have a professional quantitative trading platform at your fingertips.**

---

## 📞 **Support**

**If you encounter issues:**
- Check logs: `meridian_local/logs/*.log`
- Review Docker logs: `docker logs meridian-api`
- Run integration tests
- Consult `DOCKER_OPERATOR_HANDBOOK.md`
- Check `INTEGRATION_TEST_RESULTS.md`

**For questions:**
- Review stage guides: `STAGE_*_COMPLETE.md`
- Check API docs: http://localhost:8000/docs
- Read data policy: `docs/DATA_POLICY.md`

---

**Setup Guide Version:** 1.0  
**Last Updated:** December 4, 2025  
**Status:** Production-Ready

**Welcome to Meridian 3.0!** 🚀

