# 🏗️ Meridian 3.0 Architecture Diagrams

**Version:** 3.0.0  
**Last Updated:** December 4, 2025  
**Format:** Mermaid Diagrams  
**Status:** Production-Ready

---

## 📊 Available Diagrams

This directory contains comprehensive architecture diagrams for the Meridian 3.0 quantitative trading platform. All diagrams are written in Mermaid syntax and can be rendered in GitHub, VS Code, or any Mermaid-compatible viewer.

---

### 1. **Full Architecture Diagram**
**File:** [`Meridian_Full_Architecture.mmd`](./Meridian_Full_Architecture.mmd)

**Description:**  
Complete system overview showing all major components:
- External data sources
- Data ingestion and validation layer
- 8 core quantitative engines
- Daily pipeline orchestration
- Storage layer (SQLite, files, logs)
- FastAPI backend
- Streamlit dashboard (9 pages)
- APScheduler for automation

**Use Case:** Understanding the entire Meridian ecosystem

**View Online:** [Mermaid Live Editor](https://mermaid.live/)

---

### 2. **Data Flow Map**
**File:** [`Meridian_Data_Flow_Map.mmd`](./Meridian_Data_Flow_Map.mmd)

**Description:**  
Traces data from external sources through the complete processing pipeline:
- Market data ingestion (min year 2000 enforcement)
- Validation checks (≥1500 bars, real data only)
- Processing through 8 core engines
- Pipeline execution
- Storage in SQLite and JSON
- Exposure via API
- Display in dashboard

**Use Case:** Understanding data lineage and processing flow

---

### 3. **Docker Architecture Map**
**File:** [`Meridian_Docker_Architecture.mmd`](./Meridian_Docker_Architecture.mmd)

**Description:**  
Container architecture for Docker deployment:
- `meridian-api` (FastAPI, port 8000)
- `meridian-dashboard` (Streamlit, port 8501)
- `meridian-scheduler` (APScheduler, background jobs)
- Shared volumes (data, logs, models, cache, database)
- Inter-container communication

**Use Case:** Deploying and managing Docker infrastructure

---

### 4. **Pipeline Flow Diagram**
**File:** [`Meridian_Pipeline_Flow.mmd`](./Meridian_Pipeline_Flow.mmd)

**Description:**  
Step-by-step execution of the daily pipeline:
1. Fetch market data
2. Validate dataset
3. Run Hurst Phasing
4. Run Harmonics
5. Run Forecast Engine
6. Run Volatility & Risk
7. Run Regime Classifier
8. Run Intermarket Engine
9. Run Strategy Evolution
10. Run Portfolio Allocation
11. Save results
12. Expose to API
13. Display in dashboard

**Use Case:** Understanding daily operations and debugging pipeline issues

---

### 5. **Developer Workflow Diagram**
**File:** [`Meridian_Developer_Workflow.mmd`](./Meridian_Developer_Workflow.mmd)

**Description:**  
Recommended workflow for developers:
- Edit code
- Run integration tests
- Build Docker containers
- Start stack
- Verify health
- Run pipeline
- Review outputs
- Commit and push

Includes failure loops for test-driven development.

**Use Case:** Onboarding developers and maintaining code quality

---

### 6. **CI/CD System Diagram**
**File:** [`Meridian_CICD_Diagram.mmd`](./Meridian_CICD_Diagram.mmd)

**Description:**  
Continuous integration and deployment pipeline:
- GitHub push triggers CI
- Linting and static checks
- Python test suite
- Docker image builds
- Test reports and coverage
- Optional cloud deployment (Azure, GCP)

**Use Case:** Understanding automated testing and deployment

---

## 🔧 How to View Diagrams

### **Option 1: GitHub (Recommended)**
GitHub automatically renders `.mmd` files. Just click any diagram file above!

### **Option 2: VS Code**
Install the "Mermaid Preview" extension:
```bash
code --install-extension bierner.markdown-mermaid
```
Then open any `.mmd` file and use preview mode.

### **Option 3: Mermaid Live Editor**
1. Copy the contents of any `.mmd` file
2. Visit: https://mermaid.live/
3. Paste and view

### **Option 4: Documentation Sites**
These diagrams work natively in:
- GitHub Pages
- GitLab
- Notion
- Obsidian
- Docusaurus
- MkDocs

---

## 📸 Exporting to PNG/SVG

### **Using Mermaid CLI:**
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Export to PNG
mmdc -i Meridian_Full_Architecture.mmd -o rendered/Meridian_Full_Architecture.png

# Export to SVG
mmdc -i Meridian_Full_Architecture.mmd -o rendered/Meridian_Full_Architecture.svg

# Batch export all
for file in *.mmd; do
  mmdc -i "$file" -o "rendered/${file%.mmd}.png"
  mmdc -i "$file" -o "rendered/${file%.mmd}.svg"
done
```

### **Using Mermaid Live Editor:**
1. Open https://mermaid.live/
2. Paste diagram code
3. Click "Actions" → "Download PNG" or "Download SVG"

### **Using VS Code Extension:**
1. Open diagram in VS Code
2. Right-click preview
3. Select "Export to PNG" or "Export to SVG"

---

## 🔄 Keeping Diagrams Updated

### **When to Update:**
Update diagrams whenever:
- ✅ New modules are added
- ✅ Architecture changes (new engines, services)
- ✅ Docker configuration changes
- ✅ API endpoints are added/modified
- ✅ Dashboard pages are added
- ✅ Data flow rules change
- ✅ Pipeline steps are added/modified

### **How to Update:**
1. Edit the relevant `.mmd` file
2. Validate syntax at https://mermaid.live/
3. Re-export PNG/SVG versions
4. Commit with message: `docs(architecture): update diagrams to reflect [change]`

### **Validation Checklist:**
- [ ] Diagram renders without errors
- [ ] All module names match filesystem paths
- [ ] All service names match `docker-compose.yml`
- [ ] Data flow reflects current data policy
- [ ] No broken references

---

## 📋 Diagram Maintenance Log

| Date | Diagram | Change | Version |
|------|---------|--------|---------|
| 2025-12-04 | All | Initial creation | 3.0.0 |

---

## 🎯 Quick Reference

**Need to understand:**
- **Overall system?** → Full Architecture
- **How data flows?** → Data Flow Map
- **Docker setup?** → Docker Architecture
- **Daily operations?** → Pipeline Flow
- **Development process?** → Developer Workflow
- **CI/CD pipeline?** → CI/CD Diagram

---

## 📚 Related Documentation

- [Docker Setup Walkthrough](../DOCKER_SETUP_WALKTHROUGH.md)
- [Docker Operator Handbook](../DOCKER_OPERATOR_HANDBOOK.md)
- [First Real Data Run Guide](../FIRST_REAL_DATA_RUN.md)
- [Stage Completion Guides](../../STAGE_*_COMPLETE.md)
- [Data Policy](../DATA_POLICY.md)

---

## 🏆 Diagram Standards

All Meridian architecture diagrams follow these standards:
- ✅ Mermaid syntax validated
- ✅ Clear, descriptive labels
- ✅ Logical grouping with subgraphs
- ✅ Consistent styling
- ✅ Version controlled
- ✅ Accessible to technical and non-technical users

---

**Maintained by:** Meridian Development Team  
**Questions?** See main documentation or open an issue

**Status:** ✅ Production-Ready, Version 3.0.0

