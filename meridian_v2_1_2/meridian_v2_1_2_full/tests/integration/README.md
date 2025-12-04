# Meridian 3.0 Integration Tests

## Overview
Comprehensive integration tests validating all 10 stages working together.

## Test Suites

### 1. Local Integration Test
**File:** `meridian_integration_test.py`

**Tests:**
- All module imports (Stages 1-10)
- Core functionality (pairs, regime, portfolio, volatility, evolution)
- Database operations
- Model registry
- Pipeline execution

**Run:**
```bash
cd /path/to/meridian_v2_1_2_full
source .venv/bin/activate
PYTHONPATH="$PWD/src:$PYTHONPATH" python tests/integration/meridian_integration_test.py
```

**Expected Output:**
```
✅ All tests pass
📊 Passed: 15+
❌ Failed: 0
```

### 2. Docker Integration Test
**File:** `docker_integration_test.py`

**Tests:**
- Docker containers running
- API endpoint accessibility
- Dashboard accessibility
- Container health checks

**Prerequisites:**
```bash
cd deploy
docker-compose up -d
```

**Run:**
```bash
python tests/integration/docker_integration_test.py
```

### 3. API Integration Test (Requires API Running)
Subset of main test that validates API endpoints.

## Test Coverage

### Stage 1: Cross-Market Arbitrage
- ✅ Module imports
- ✅ Pairs selector execution
- ✅ Divergence detection

### Stage 2: Regime Classifier
- ✅ Module imports
- ✅ Feature extraction
- ✅ Label generation
- ✅ Model training

### Stage 3: Portfolio Allocation
- ✅ Module imports
- ✅ Feature building
- ✅ Weight calculation

### Stage 4: Volatility & Risk
- ✅ Module imports
- ✅ Volatility computation
- ✅ C-ATR calculation

### Stage 5: Strategy Evolution
- ✅ Module imports
- ✅ Genome operations

### Stage 6: API
- ✅ Health endpoint
- ✅ Regime endpoint
- ✅ Response formats

### Stage 7: Execution
- ✅ Module imports
- ✅ Order manager
- ✅ Risk gate

### Stage 9: AI Agents
- ✅ Module imports
- ✅ Orchestrator creation

### Stage 10: Production
- ✅ Database writes/reads
- ✅ Model registry
- ✅ Pipeline execution

## Success Criteria

**PASS:** All imports succeed, core functions execute, no exceptions

**FAIL:** Any import errors or runtime failures

## Troubleshooting

### Common Issues:
1. **Import errors:** Check PYTHONPATH is set correctly
2. **API tests fail:** Ensure API is running on port 8000
3. **Docker tests fail:** Run `docker-compose up -d` first
4. **Module not found:** Verify all Stage 1-10 modules exist

### Quick Fixes:
```bash
# Reset Python path
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# Restart API
pkill -f uvicorn
uvicorn meridian_v2_1_2.meridian_api.main:app --port 8000 &

# Rebuild Docker
cd deploy && docker-compose down && docker-compose build && docker-compose up -d
```

## Next Steps

After tests pass:
1. ✅ Meridian 3.0 is validated
2. ✅ Safe to deploy to production
3. ✅ Ready for live trading (after paper testing)
4. ✅ Ready for cloud deployment

## Notes

- Tests use synthetic data (safe, fast)
- No real API keys required for basic tests
- Docker tests require Docker Desktop
- API tests require running API server

