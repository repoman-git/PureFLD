# 🚀 Meridian 3.0 Deployment Guide

## Overview
Complete deployment guide for Meridian 3.0 across multiple environments.

---

## 🐳 **Docker Deployment (Recommended)**

### Prerequisites:
- Docker Desktop installed
- 4GB RAM minimum
- 10GB disk space

### Quick Start:
```bash
cd deploy
docker-compose up -d

# Access:
# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

### Test Deployment:
```bash
# Run integration test
chmod +x ../docker_integration_test.sh
../docker_integration_test.sh
```

### Stop:
```bash
docker-compose down
```

---

## ☁️ **Cloud Deployment**

### Google Cloud Platform (GCP):
```bash
# Install gcloud CLI
# Authenticate: gcloud auth login

# Deploy API
gcloud run deploy meridian-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy Dashboard
gcloud run deploy meridian-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure:
```bash
# Install Azure CLI
# Login: az login

# Create resource group
az group create --name meridian-rg --location eastus

# Deploy API
az containerapp up \
  --name meridian-api \
  --source . \
  --resource-group meridian-rg \
  --environment meridian-env
```

### AWS:
```bash
# Using ECS/Fargate
aws ecr create-repository --repository-name meridian-api
docker tag meridian-api:latest [YOUR_ECR_URL]/meridian-api:latest
docker push [YOUR_ECR_URL]/meridian-api:latest

# Deploy via ECS console or CLI
```

---

## 💻 **Local Development**

### Run Services:
```bash
# Terminal 1: API
cd meridian_v2_1_2_full
source .venv/bin/activate
PYTHONPATH="$PWD/src:$PYTHONPATH" uvicorn meridian_v2_1_2.meridian_api.main:app --reload --port 8000

# Terminal 2: Dashboard
PYTHONPATH="$PWD/src:$PYTHONPATH" streamlit run meridian_app/app.py

# Terminal 3: Scheduler (optional)
PYTHONPATH="$PWD/src:$PYTHONPATH" python -c "from meridian_v2_1_2.scheduler.jobs import start_scheduler; start_scheduler()"
```

---

## 🧪 **Testing**

### Integration Tests:
```bash
# Local tests
PYTHONPATH="$PWD/src:$PYTHONPATH" python tests/integration/meridian_integration_test.py

# Docker tests
./docker_integration_test.sh
```

---

## 🔧 **Configuration**

### Environment Variables:
```bash
# API
export MERIDIAN_ENV=production
export MERIDIAN_LOG_LEVEL=info

# Brokers (for live trading)
export ALPACA_API_KEY=your_key
export ALPACA_SECRET_KEY=your_secret
export ALPACA_ENDPOINT=https://paper-api.alpaca.markets

# IBKR
export IBKR_HOST=127.0.0.1
export IBKR_PORT=7497
```

### Database:
- Default: SQLite at `meridian_local/meridian.db`
- Production: Configure PostgreSQL connection

---

## 📊 **Monitoring**

### Logs:
```bash
# Docker logs
docker-compose logs -f api
docker-compose logs -f app

# Local logs
tail -f meridian_local/logs/*.log
```

### Health Checks:
```bash
# API
curl http://localhost:8000/health

# Containers
docker ps
docker stats
```

---

## 🔒 **Security**

### API Keys:
- Never commit API keys
- Use environment variables
- Rotate keys regularly

### Network:
- Use reverse proxy (nginx) for production
- Enable HTTPS
- Restrict API access

---

## 🚀 **Production Checklist**

- [ ] Integration tests passing
- [ ] Docker build successful
- [ ] API endpoints responding
- [ ] Dashboard accessible
- [ ] Broker API keys configured
- [ ] Monitoring set up
- [ ] Backup strategy defined
- [ ] SSL certificates configured
- [ ] Firewall rules set
- [ ] Start with paper trading

---

## 🎯 **Next Steps**

1. **Test locally** - Run all services
2. **Test Docker** - Run docker_integration_test.sh
3. **Paper trade** - Connect Alpaca paper account
4. **Monitor** - Watch for 1-2 weeks
5. **Go live** - When confident

---

## 📚 **Resources**

- Integration Test Results: `../INTEGRATION_TEST_RESULTS.md`
- Stage Documentation: `../STAGE_*_COMPLETE.md`
- API Reference: http://localhost:8000/docs

**Status:** ✅ Ready for deployment

