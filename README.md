# Real-Time Digital Twin for Streaming-Based Anomaly Detection

### IOE413: Streaming & Data Analytics — Mini Project
**Academic Team:** Team 12 — Rohit Pratap Singh (2023BCS0138)  
**Baseline Research Paper:**  
A. Ranpariya and S. Sharma, *"A digital twin solution for fault detection in time-critical IIoT applications,"* *Journal of Simulation*, vol. 19, no. 4, pp. 441–454, 2025. [DOI: 10.1080/17477778.2025.2453725](https://doi.org/10.1080/17477778.2025.2453725)

---

## 📌 Quickstart: Run in 1 Click (No-CLI)

### Option A: Windows Docker Launcher (Recommended)
1. Ensure **Docker Desktop** is running.
2. Double-click `start.bat`.
3. The launcher builds the image, starts the container, waits for readiness, and opens `http://localhost:8000` in your default browser.
4. To shut down cleanly: double-click `stop.bat`.

### Option B: Local Python Host Runner
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch master application
python run.py
```
This automatically verifies/trains models, starts the 10 Hz streaming engine, boots the FastAPI server on `http://127.0.0.1:8000`, and opens the browser.

---

## 🎛️ Operations Console Highlights

Once running, navigate to `http://localhost:8000` to interact with the 5-row industrial operations console:
- **Row 1 (KPI Strip):** Live Composite Health Index (CHI), estimation delay (ms), active fault, and packet counters.
- **Row 2 (Twin & Telemetry):** Dynamic 2D rotating induction motor/pump Canvas visualizer + 4 real-time Canvas streaming charts (Vibration, Temperature, Current, CHI).
- **Row 3 (Inference & Fault Injection Deck):** Two-Stage inference breakdown with 1-click fault triggers (Bearing Defect, Stator Overheating, Rotor Imbalance, Cavitation, Sensor Drift, and Normal Reset).
- **Row 4 (Pipeline Controls):** Start, Stop, and Restart the streaming engine without crashing the web console; view recent engine logs in a slide-out drawer.
- **Row 5 (Audit Feed & Benchmark Matrix):** Live timestamped anomaly alerts + published research comparison table with clear provenance markers.

---

## 📚 Complete Project Documentation

| Document | Description |
|---|---|
| 📖 [PROJECT_MASTER_GUIDE.md](docs/PROJECT_MASTER_GUIDE.md) | **Comprehensive Master Guide:** Viva defense reference, full event lifecycle, glossary, formulas, and developer recipes. |
| 🎯 [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) | Problem statement, academic context, system scope, personas, and demo workflow. |
| 🏗️ [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Mermaid topology, event flow sequence, network ports, schemas, and service boundaries. |
| 🔍 [COMPONENTS_DEEP_DIVE.md](docs/COMPONENTS_DEEP_DIVE.md) | Module-by-module breakdown of code responsibility, interfaces, and error paths. |
| 🐳 [SETUP_DOCKER_AND_RUNBOOK.md](docs/SETUP_DOCKER_AND_RUNBOOK.md) | Docker build instructions, persistence volume rules, environment variables, and runbook. |
| 🎮 [DASHBOARD_AND_OPERATIONS.md](docs/DASHBOARD_AND_OPERATIONS.md) | Complete user guide for all UI elements, chart channels, and fault injection workflows. |
| 🔧 [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Verified root cause and resolution for all 7 runtime errors (Kafka, Spark, scikit-learn, etc.). |
| 📊 [MODELS_AND_METRICS.md](docs/MODELS_AND_METRICS.md) | 14-D feature space, Digital Twin residual formulas, CHI derivation, and ML benchmarks. |
| 🗺️ [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) | Completed milestones, technical backlog, and academic research extensions. |
| 🧪 [VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md) | Automated test execution log (22/22 tests passing) and validation checklist. |
| 📋 [IMPLEMENTATION_AUDIT.md](docs/IMPLEMENTATION_AUDIT.md) | Pre- and post-upgrade discrepancy audit table and verified resolutions. |

---

## 🧪 Automated Testing

Execute the complete automated test suite:
```powershell
python -m pytest tests/ -v
```
All 25 unit and integration tests validate the Digital Twin physics, Two-Stage ML Ensemble, Streaming Engine, and REST/WebSocket API endpoints.

---

## 🔬 Benchmark Summary vs Baseline Paper

| Model Architecture | Features Used | Accuracy | F1-Score | Edge Delay |
|---|---|:---:|:---:|:---:|
| **Proposed 2-Stage DT Ensemble** | **Raw + DT Residuals (14-D)** | **100.0%** (Synthetic) | **100.0%** | **1.5 ms** (Fast) / **4.8 ms** (Diag) |
| Published Baseline (Ranpariya & Sharma 2025) | Edge-Cloud Digital Twin | 99.71% | — | 4.80 ms |
| Baseline A: Random Forest | Raw Telemetry Only (7-D) | 100.0% | 100.0% | 7.50 ms |
| Baseline B: SVM (RBF) | Raw Telemetry Only (7-D) | 100.0% | 100.0% | 14.21 ms |
