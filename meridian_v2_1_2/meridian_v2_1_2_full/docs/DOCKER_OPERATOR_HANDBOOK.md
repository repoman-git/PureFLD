# 🐳 Meridian 3.0 — Docker Operator Handbook

**Version:** 1.0  
**Scope:** Running, managing, troubleshooting, and maintaining the Meridian Quantitative Trading Platform using Docker  
**Audience:** Operators, Quants, Developers  
**Status:** Production-Ready

---

## 📘 1. Overview

Meridian 3.0 is deployed as a **multi-service Docker environment**:

| Service | Purpose | Port |
|---------|---------|------|
| `meridian-api` | FastAPI backend for forecasts, phasing, volatility, allocation | 8000 |
| `meridian-dashboard` | Streamlit front-end (9-page real-time terminal) | 8501 |
| `meridian-scheduler` | APScheduler-based daily pipeline + paper trading | N/A |
| `registry` (local storage) | Stores data, logs, model outputs | Mounted |
| `database` | SQLite for signals, trades, cycle states | Mounted |

Docker ensures consistent, reproducible, fault-tolerant operation across all environments.

---

## 🟦 2. Directory Structure

### **Deployment Files:**
```
deploy/
├── docker-compose.yml          # Multi-container orchestration
├── Dockerfile.api              # API container definition
├── Dockerfile.app              # Dashboard container definition
├── .env.example                # Environment configuration template
└── README_DEPLOY.md            # Deployment guide
```

### **Runtime State (Persisted):**
```
meridian_local/
├── data/                       # Market data cache
├── logs/                       # All system logs
├── registry/                   # Model versioning
├── meridian.db                 # SQLite database
└── policy_violations.log       # Data integrity violations
```

**Important:** These directories persist across container restarts.

---

## 🟩 3. Starting the System

### **From Project Root:**
```bash
cd /Users/simonerses/Data-Projects-PureFLD/meridian_v2_1_2/meridian_v2_1_2_full/deploy
docker-compose up -d
```

This will launch:
- ✅ API container (port 8000)
- ✅ Dashboard container (port 8501)
- ✅ Shared volumes
- ✅ Network bridge

### **Validate Services Are Up:**
```bash
docker ps

# Should show:
# - deploy-api-1 (or similar)
# - deploy-app-1 (or similar)
```

### **Health Checks:**
- **API:** http://localhost:8000/health
- **API Docs:** http://localhost:8000/docs
- **Dashboard:** http://localhost:8501

**If these all load → the system is healthy.**

---

## 🟫 4. Stopping the System

### **Graceful Shutdown:**
```bash
docker-compose down
```

### **Stop Containers, Keep Data:**
```bash
docker-compose down --remove-orphans
```

### **Nuclear Option (Wipe Everything):**
```bash
docker-compose down -v
rm -rf ../meridian_local/*
```
⚠️ **WARNING:** This deletes all data, models, and logs!

---

## 🟨 5. Rebuilding Containers

### **When to Rebuild:**
- Updated Python dependencies
- Changed dashboard code
- Modified API code
- Updated data validation rules
- Changed any Dockerfile
- After `git pull` with code changes

### **Rebuild All:**
```bash
docker-compose build
docker-compose up -d
```

### **Rebuild Single Service:**
```bash
docker-compose build meridian-api
docker-compose up -d meridian-api

# Or for dashboard:
docker-compose build meridian-dashboard
docker-compose up -d meridian-dashboard
```

### **Force Rebuild (No Cache):**
```bash
docker-compose build --no-cache
```

---

## 🟧 6. Running the Daily Pipeline

The daily pipeline executes:
1. Data fetch (enforces year ≥ 2000)
2. Cycle phasing analysis
3. Regime classification
4. Forecasting (ensemble)
5. Volatility/risk calculation
6. Strategy evolution
7. Portfolio allocation
8. Signal generation
9. Paper trade execution (if configured)

### **Option A: Scheduler Container (Recommended)**
```bash
docker-compose run --rm meridian-scheduler
```

### **Option B: API Trigger**
```bash
curl -X POST http://localhost:8000/api/v2/pipeline/run_daily
```

### **Option C: Manual Inside Container**
```bash
docker exec -it meridian-api python -m meridian_v2_1_2.pipeline.meridian_pipeline
```

---

## 🟦 7. Checking Logs

### **Container Logs:**
```bash
# API logs
docker logs meridian-api -f

# Dashboard logs
docker logs meridian-dashboard -f

# All logs
docker-compose logs -f
```

### **Application Logs (Inside Containers):**
Logs are persisted in mounted volumes:

```bash
# From host machine
tail -f meridian_local/logs/pipeline.log
tail -f meridian_local/logs/policy_violations.log
```

### **Key Log Files:**
| File | Purpose |
|------|---------|
| `pipeline.log` | Full daily pipeline output |
| `api.log` | API errors, warnings |
| `dashboard.log` | UI-level errors |
| `scheduler.log` | Trading + signal generation |
| `policy_violations.log` | Data integrity violations |
| `trades.log` | Execution engine activity |

---

## 🟥 8. Handling Errors

### **API Container Crashes:**
```bash
docker restart meridian-api

# Check logs
docker logs meridian-api --tail 100
```

### **Dashboard Blank or Broken:**
```bash
docker restart meridian-dashboard

# Check logs
docker logs meridian-dashboard --tail 100
```

### **Pipeline Fails:**
1. Check logs:
   ```bash
   cat meridian_local/logs/pipeline.log
   ```

2. Common causes:
   - ❌ Insufficient history (violates year ≥ 2000 rule)
   - ❌ Missing environment variables
   - ❌ Bad symbol
   - ❌ Network outage
   - ❌ Corrupted local cache

3. Fix corrupted caches:
   ```bash
   rm -rf meridian_local/cache/*
   docker-compose restart
   ```

### **Database Issues:**
```bash
# Backup current database
cp meridian_local/meridian.db meridian_local/meridian.db.backup

# Reinitialize if corrupted
rm meridian_local/meridian.db
docker-compose restart meridian-api
```

### **Out of Memory:**
```bash
# Check Docker resources
docker stats

# Increase Docker memory (Docker Desktop → Settings → Resources)
# Recommended: 4GB RAM minimum
```

---

## 🟧 9. Paper Trading Setup (Alpaca)

### **Prerequisites:**
1. Get FREE paper trading account: https://alpaca.markets
2. Get paper trading API keys from Alpaca dashboard

### **Configuration:**
Create `deploy/.env` from template:
```bash
cp deploy/.env.example deploy/.env
```

Edit `.env`:
```bash
ALPACA_API_KEY=your_paper_api_key_here
ALPACA_SECRET_KEY=your_paper_secret_key_here
ALPACA_ENDPOINT=https://paper-api.alpaca.markets
ENABLE_PAPER_TRADING=true
```

### **Execute Paper Trading:**
```bash
docker-compose run --rm meridian-scheduler
```

### **Verify Orders:**
- Check Alpaca dashboard: https://app.alpaca.markets
- Check logs: `meridian_local/logs/trades.log`
- Check database: Query `trades` table

---

## 🟪 10. Updating the System

### **Pull Latest Changes:**
```bash
cd /path/to/meridian_v2_1_2
git pull origin main
```

### **Rebuild and Restart:**
```bash
cd meridian_v2_1_2_full/deploy
docker-compose build
docker-compose up -d
```

### **Verify Update:**
```bash
curl http://localhost:8000/ | grep version
```

---

## 🟩 11. Monitoring System Health

### **Health Endpoints:**
```bash
# Overall health
curl http://localhost:8000/health

# API root
curl http://localhost:8000/

# Dashboard status
curl http://localhost:8501
```

### **Container Resource Usage:**
```bash
docker stats

# Watch in real-time
docker stats --no-stream
```

### **Dashboard Indicators:**
Navigate through all 9 pages:
1. Cycle Overview
2. Regime Classifier
3. Execution Monitor
4. Intermarket Dashboard
5. Cycle Health
6. Volatility Terminal
7. Forecast Terminal
8. Strategy Signals
9. Macro Regime

**All pages should load without errors.**

---

## 🟫 12. Data Integrity Enforcement

Meridian automatically enforces strict data quality:

### **Mandatory Rules:**
- ✅ Start date ≥ **January 1, 2000**
- ✅ Minimum bars by component:
  - Regime: 252 bars (1 year)
  - Volatility: 500 bars (2 years)
  - Phasing: 1500 bars (6 years)
  - Harmonics: 1500 bars (6 years)
  - Forecasting: 1500 bars (6 years)
  - Backtesting: 2500 bars (10 years)
  - Intermarket: 2500 bars (10 years)

### **Violation Response:**
- ❌ Pipeline aborts immediately
- ❌ Clear error message displayed
- ❌ Logged to `policy_violations.log`
- ❌ Dashboard shows warning

### **Check Policy Compliance:**
```bash
cat meridian_local/logs/policy_violations.log
```

**If this file is empty → all data is compliant!**

---

## 🟦 13. Developer Mode: Working Inside Containers

### **Interactive Shell in API Container:**
```bash
docker exec -it meridian-api bash

# Once inside:
python
>>> from meridian_v2_1_2.regimes import CycleRegimeClassifier
>>> # Test modules interactively
```

### **Interactive Shell in Dashboard:**
```bash
docker exec -it meridian-dashboard bash
```

### **Run Integration Tests Inside Container:**
```bash
docker exec -it meridian-api python tests/integration/meridian_integration_test_v2.py
```

### **View Environment Variables:**
```bash
docker exec -it meridian-api printenv | grep MERIDIAN
```

---

## 🟧 14. Backup and Restore

### **Backup Everything:**
```bash
# Stop containers
docker-compose down

# Backup data
tar -czf meridian_backup_$(date +%Y%m%d).tar.gz meridian_local/

# Restart
docker-compose up -d
```

### **Restore from Backup:**
```bash
docker-compose down
rm -rf meridian_local/
tar -xzf meridian_backup_YYYYMMDD.tar.gz
docker-compose up -d
```

### **Backup Database Only:**
```bash
cp meridian_local/meridian.db meridian_local/meridian_backup_$(date +%Y%m%d).db
```

---

## 🟥 15. Performance Optimization

### **Increase Container Resources:**
Edit `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

### **Enable Caching:**
Ensure these directories are mounted:
```
- ./meridian_local/cache:/app/meridian_local/cache
```

### **Optimize Database:**
```bash
docker exec -it meridian-api python -c "
from meridian_v2_1_2.storage.meridian_db import db
# Database automatically optimizes on startup
"
```

---

## 🟩 16. Troubleshooting Common Issues

### **Issue: "Container exits immediately"**
**Solution:**
```bash
docker logs meridian-api
# Check for Python import errors or missing dependencies
docker-compose build --no-cache
```

### **Issue: "Cannot connect to API"**
**Solution:**
```bash
# Check if API is running
docker ps | grep api

# Check port binding
netstat -an | grep 8000

# Restart API
docker restart meridian-api
```

### **Issue: "Dashboard shows errors"**
**Solution:**
```bash
# Check if API is accessible FROM dashboard container
docker exec -it meridian-dashboard curl http://api:8000/health

# If fails, check Docker network
docker network ls
docker network inspect deploy_default
```

### **Issue: "Data validation failures"**
**Solution:**
```bash
# Check policy violations
cat meridian_local/logs/policy_violations.log

# Ensure data starts from ≥2000
# Fetch longer history from data source
```

### **Issue: "Out of disk space"**
**Solution:**
```bash
# Clean Docker system
docker system prune -a

# Clean Meridian cache
rm -rf meridian_local/cache/*

# Check disk usage
du -sh meridian_local/*
```

---

## 🟦 17. Daily Operator Workflow

### **Morning Routine (5 minutes):**
1. ✅ Start Docker:
   ```bash
   cd deploy && docker-compose up -d
   ```

2. ✅ Check API health:
   ```bash
   curl http://localhost:8000/health
   ```

3. ✅ Check Dashboard:
   - Open: http://localhost:8501
   - Navigate through key pages

4. ✅ Run daily pipeline:
   ```bash
   docker-compose run --rm meridian-scheduler
   ```

5. ✅ Review signals:
   - Check dashboard Strategy Signals page
   - Review any trade recommendations

6. ✅ Check logs:
   ```bash
   tail -20 meridian_local/logs/pipeline.log
   ```

7. ✅ If paper trading:
   - Check Alpaca dashboard
   - Review trades in Execution Monitor

### **Evening Routine (2 minutes):**
- Review P&L (if paper trading)
- Check for any errors in logs
- Verify data integrity
- Backup if needed

---

## 🟧 18. Weekly Maintenance Workflow

### **Every Sunday (15 minutes):**

1. ✅ Update codebase:
   ```bash
   cd /path/to/meridian_v2_1_2
   git pull origin main
   ```

2. ✅ Rebuild containers:
   ```bash
   cd meridian_v2_1_2_full/deploy
   docker-compose build
   ```

3. ✅ Restart services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. ✅ Prune unused images:
   ```bash
   docker system prune -f
   ```

5. ✅ Run system health check:
   ```bash
   cd ..
   PYTHONPATH="$PWD/src:$PYTHONPATH" python tests/integration/meridian_integration_test_v2.py
   ```

6. ✅ Backup data:
   ```bash
   tar -czf backups/meridian_backup_$(date +%Y%m%d).tar.gz meridian_local/
   ```

7. ✅ Review performance:
   - Check integration test results
   - Review weekly P&L (if trading)
   - Analyze regime distribution
   - Validate forecast accuracy

---

## 🟦 19. Advanced Operations

### **Multi-Symbol Pipeline:**
```bash
# Run pipeline for multiple markets
docker-compose run --rm meridian-api python -c "
from meridian_v2_1_2.pipeline.meridian_pipeline import pipeline
import yfinance as yf

# Fetch multiple symbols
symbols = ['GLD', 'SLV', 'TLT', 'SPY']
price_dict = {}
for sym in symbols:
    data = yf.Ticker(sym).history(period='max')
    price_dict[sym] = data['Close']

# Run pipeline
results = pipeline.run(price_dict)
"
```

### **Custom Job Scheduling:**
```bash
# Add to scheduler/jobs.py
# Then run specific job
docker-compose run --rm meridian-scheduler python -c "
from meridian_v2_1_2.scheduler.jobs import daily_pipeline_job
daily_pipeline_job()
"
```

### **Export Results:**
```bash
# Export database to CSV
docker exec -it meridian-api python -c "
from meridian_v2_1_2.storage.meridian_db import db
import pandas as pd

signals = db.read('SELECT * FROM signals')
signals.to_csv('/app/meridian_local/exports/signals.csv')
"
```

---

## 🟩 20. Cloud Deployment Preparation

### **Before Deploying to Cloud:**

1. ✅ Run full integration tests:
   ```bash
   ./docker_integration_test.sh
   ```

2. ✅ Verify all services work locally

3. ✅ Configure production environment variables

4. ✅ Set up cloud storage (replace local volumes)

5. ✅ Configure SSL certificates

6. ✅ Set up monitoring/alerting

### **Cloud Deployment Commands:**

**GCP Cloud Run:**
```bash
gcloud run deploy meridian-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Azure Container Apps:**
```bash
az containerapp up \
  --name meridian-api \
  --source . \
  --resource-group meridian-rg
```

**AWS ECS:**
See `deploy/README_DEPLOY.md` for ECS instructions

---

## 🟫 21. Security Best Practices

### **API Keys:**
- ✅ Never commit API keys
- ✅ Use `.env` file (gitignored)
- ✅ Rotate keys quarterly
- ✅ Use separate keys for paper vs live

### **Network Security:**
```bash
# Restrict API access (production)
# Edit docker-compose.yml:
ports:
  - "127.0.0.1:8000:8000"  # Only localhost

# Use reverse proxy (nginx) for SSL
```

### **Container Security:**
- Run as non-root user
- Use read-only volumes where possible
- Keep Docker updated
- Scan images for vulnerabilities:
  ```bash
  docker scan meridian-api
  ```

---

## 🟦 22. Monitoring and Alerting

### **System Metrics:**
```bash
# Container resource usage
docker stats --no-stream

# Disk usage
df -h

# Check mounted volumes
docker volume ls
```

### **Application Metrics:**
- API response times (via `/health`)
- Pipeline execution time
- Trade success rate
- Signal generation frequency

### **Set Up Alerts (Optional):**
- Use Prometheus + Grafana
- Set up email/SMS alerts
- Monitor for:
  - Container crashes
  - Pipeline failures
  - Data integrity violations
  - High error rates

---

## 🟧 23. Disaster Recovery

### **Container Won't Start:**
```bash
# Remove and recreate
docker-compose down
docker-compose up -d --force-recreate
```

### **Data Corruption:**
```bash
# Restore from backup
docker-compose down
rm -rf meridian_local/
tar -xzf backups/meridian_backup_YYYYMMDD.tar.gz
docker-compose up -d
```

### **Complete System Failure:**
```bash
# Nuclear reset
docker-compose down -v
docker system prune -a -f
rm -rf meridian_local/*

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# Run integration tests
PYTHONPATH="$PWD/src:$PYTHONPATH" python tests/integration/meridian_integration_test_v2.py
```

---

## 🟩 24. Production Checklist

Before going to production:
- [ ] All integration tests passing (16/16)
- [ ] Docker containers build successfully
- [ ] API endpoints responding
- [ ] Dashboard accessible
- [ ] Paper trading tested for 2+ weeks
- [ ] Broker API keys configured and tested
- [ ] Backup strategy implemented
- [ ] Monitoring set up
- [ ] SSL certificates configured (cloud)
- [ ] Firewall rules set (cloud)
- [ ] Disaster recovery plan documented
- [ ] Team trained on operations

---

## 🏁 25. Final Notes

This handbook ensures:
- ✅ Consistency across deployments
- ✅ Reliability in production
- ✅ Reproducibility of results
- ✅ Safety in operations
- ✅ Traceability of all actions
- ✅ Minimal downtime
- ✅ No "works on my machine" issues

Meridian 3.0 is now ready for **daily real-market operation** using Docker as the backbone.

**Operate with confidence.**

---

## 📞 Support Resources

- **Documentation:** All `STAGE_*_COMPLETE.md` files
- **Integration Tests:** `tests/integration/`
- **Deployment Guide:** `deploy/README_DEPLOY.md`
- **Data Policy:** `docs/DATA_POLICY.md`
- **Release Notes:** `RELEASE_NOTES_v3.0.0.md`
- **First Data Run:** `FIRST_REAL_DATA_RUN.md`

---

**Handbook Version:** 1.0  
**Last Updated:** December 4, 2025  
**Status:** Production-Ready

**Meridian 3.0: Professional Docker Operations** 🐳🏆

