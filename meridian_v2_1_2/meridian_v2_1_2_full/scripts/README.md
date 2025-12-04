# Meridian v2.1.2 — Scripts Directory

This directory contains utility scripts for managing and monitoring your Meridian trading platform.

---

## 🚀 Dashboard Management

### Start Dashboard
```bash
./scripts/start_dashboard.sh
```
Launches the Streamlit dashboard on port 8501 with proper Python path configuration.

**Access URLs after starting:**
- Local: http://localhost:8501
- Network: http://192.168.178.96:8501

### Stop Dashboard
```bash
./scripts/stop_dashboard.sh
```
Gracefully stops the running dashboard.

---

## 🩺 System Diagnostics

### Environment Doctor (Standard)
```bash
./scripts/Meridian_Environment_Doctor.sh
```
Runs basic system health checks:
- Python version
- Package dependencies
- Project structure
- Module imports
- Test suite status
- Service status

### Environment Doctor (Pro Edition)
```bash
./scripts/MeridianEnvironmentDoctor_ProEdition.sh
```
Advanced diagnostics with:
- ✅ Color-coded output
- 📝 Detailed logging to `meridian_env_doctor_pro.log`
- 📊 Health score calculation (0-100%)
- 💾 Disk space monitoring
- 📦 Project size tracking
- ⚠️ Warning/Error categorization
- 🎯 Exit codes for automation (0=healthy, 1=degraded, 2=critical)

**Output includes:**
- Environment check (Python version, venv)
- Package dependencies (with version validation)
- Project structure integrity
- Module import tests
- Test suite status (682 tests)
- Service status (dashboard running?)
- System resources (disk space)
- Configuration files

---

## 📋 Quick Reference

| Script | Purpose | Output |
|--------|---------|--------|
| `start_dashboard.sh` | Launch dashboard | Interactive web UI |
| `stop_dashboard.sh` | Stop dashboard | Terminal |
| `Meridian_Environment_Doctor.sh` | Basic health check | Terminal |
| `MeridianEnvironmentDoctor_ProEdition.sh` | Advanced diagnostics | Terminal + Log file |

---

## 🎯 Typical Workflow

### Starting a Session:
```bash
# 1. Check system health
./scripts/MeridianEnvironmentDoctor_ProEdition.sh

# 2. Start the dashboard
./scripts/start_dashboard.sh

# 3. Open browser to http://localhost:8501
```

### Ending a Session:
```bash
# Stop the dashboard
./scripts/stop_dashboard.sh
```

---

## 🔧 Troubleshooting

### Dashboard won't start?
1. Run the Environment Doctor:
   ```bash
   ./scripts/MeridianEnvironmentDoctor_ProEdition.sh
   ```
2. Check if port 8501 is in use:
   ```bash
   lsof -i :8501
   ```
3. Review the log file:
   ```bash
   cat meridian_env_doctor_pro.log
   ```

### Import errors?
The `start_dashboard.sh` script automatically sets `PYTHONPATH`. If running Python commands manually, use:
```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
```

---

## 📝 Notes

- All scripts are designed to be run from the project root
- Scripts are executable (`chmod +x` already applied)
- Pro Edition generates a log file for troubleshooting
- Dashboard runs on `localhost` by default (secure)

---

## 🆘 Need Help?

- Check the main [README.md](../README.md)
- Review [Quick Start Guide](../guides/quickstart_full.pdf)
- Consult [Operator's Handbook](../guides/operator_handbook_full.pdf)

---

**Last Updated:** 2025-12-03
**Meridian Version:** v2.1.2


