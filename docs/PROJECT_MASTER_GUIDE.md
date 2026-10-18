# Project Master Guide — Real-Time Digital Twin for Streaming Anomaly Detection

**Course:** IOE413 Streaming & Data Analytics  
**Academic Team:** Team 10 — Mohammed Sirajudheen (2023BCS0132), Rohit Pratap Singh (2023BCS0138), Amit Kumar (2023BCS0210), and Kartik P (2023BCD0051)  
**Baseline Publication:** A. Ranpariya and S. Sharma, *"A digital twin solution for fault detection in time-critical IIoT applications,"* *Journal of Simulation*, vol. 19, no. 4, pp. 441–454, 2025. [DOI: 10.1080/17477778.2025.2453725](https://doi.org/10.1080/17477778.2025.2453725)

---

## 1. Executive Summary & Purpose

This master guide serves as the definitive reference manual for the IOE413 Real-Time Digital Twin Streaming Project. It is structured to provide:
1. Immediate operational instructions for plant operators and assessors (no CLI needed).
2. End-to-end architectural traceability for every telemetry packet.
3. Theoretical, mathematical, and viva defense explanations for the Digital Twin and Two-Stage Machine Learning Ensemble.
4. Step-by-step developer guides for extending sensors, fault scenarios, and API endpoints.

---

## 2. Comprehensive System Glossary

- **IIoT (Industrial Internet of Things):** High-frequency sensorized instrumentation of manufacturing assets streaming physical measurements (vibration, heat, speed, pressure) for predictive maintenance.
- **Digital Twin:** A real-time virtual mathematical representation of a physical asset that executes synchronized physical equations to predict nominal baseline behavior under varying operating loads.
- **Residual ($R_i$):** The absolute algebraic difference between the physical sensor reading and the Digital Twin's expected mathematical state: $R_i(t) = |X_{\text{sensor}, i}(t) - \hat{X}_{\text{twin}, i}(t)|$.
- **CHI (Composite Health Index):** A normalized metric ($[5.0, 100.0]\%$) derived from residual Z-scores, indicating the overall structural and electrical degradation of the asset.
- **Kafka Topic / Partition:** A distributed append-only log partitioned across brokers for fault-tolerant, high-throughput message streaming.
- **Structured Streaming:** A stream processing engine built on Apache Spark that executes incremental queries over continuous streams with event-time semantics.
- **Event-Time Window & Watermark:** Windowed aggregations based on the generation timestamp embedded inside the telemetry payload, bounded by a watermark delay to handle late-arriving records.
- **WebSocket:** A full-duplex, persistent TCP communication protocol allowing the FastAPI backend to push 10 Hz telemetry packets directly to browser Canvas visualizers with minimal protocol overhead.
- **Two-Stage ML Inference:** An asymmetrical pipeline combining an ultra-fast linear screener (Stage 1, $<1.5$ ms) with a high-capacity diagnostic ensemble (Stage 2, $\sim 3.2$ ms) to balance edge speed with diagnostic depth.
- **Model Artifact:** Serialized binary weights, hyperparameters, and scaler distributions (`.joblib`) saved to disk to decouple training from runtime inference.
- **Health Check & Readiness:** Active probes (`/api/health`) verifying that internal loops and memory buffers are operating before accepting traffic.
- **Lifecycle Controller:** Safe application-level process manager that permits stopping, starting, and restarting streaming pipelines without taking down the HTTP/WebSocket host.

---

## 3. Reference Tables

### Important Files & Roles

| File Path | Component | Responsibility |
|---|---|---|
| `server.py` | API / Web Gateway | FastAPI application, REST endpoints, WebSocket telemetry hub, graceful shutdown. |
| `run.py` | Host Launcher | Single-command launcher for native Python host execution. |
| `start.bat` / `stop.bat` | Windows Launchers | One-click startup and shutdown scripts using Docker Compose. |
| `Dockerfile` / `compose.yaml` | Containerization | Debian-slim Python 3.11 container with healthchecks and loopback security. |
| `config/settings.py` | Configuration | Network ports, intervals, asset metadata, and fault dictionaries. |
| `data/generator.py` | Telemetry Generator | Physics-informed 10 Hz generator with dynamic fault modulation. |
| `models/digital_twin.py` | Digital Twin | Virtual physics model, residual computation, and CHI evaluation. |
| `models/two_stage_ensemble.py` | ML Engine | Stage 1 SGD screener and Stage 2 ExtraTrees diagnostic classifier. |
| `models/train_models.py` | Training Pipeline | Retrains models on 18,000 synthetic samples and outputs benchmarks. |
| `streaming/stream_engine.py` | Streaming Core | Asynchronous orchestration loop, sliding windows, and client broadcaster. |
| `dashboard/templates/index.html`| UI Console | 5-row responsive industrial operations console layout. |
| `dashboard/static/js/app.js` | UI Logic | Telemetry receiver, exponential WebSocket reconnect, REST actions. |
| `dashboard/static/js/charts.js` | Charting | 60 fps HTML5 Canvas multi-channel rolling charts. |
| `dashboard/static/js/twin_visualizer.js` | Twin Canvas | 2D dynamic motor/pump visualizer with rotating shaft and heat aura. |

### Network Ports & Configuration

| Name | Env Variable | Default | Purpose |
|---|---|---|---|
| Dashboard Host | `HOST` | `127.0.0.1` (`0.0.0.0` in Docker) | Local loopback binding |
| Dashboard Port | `PORT` | `8000` | HTTP / WebSocket console port |
| Heartbeat | `WS_HEARTBEAT_INTERVAL` | `1.0` | Keepalive interval in seconds |
| Kafka Broker | `KAFKA_BOOTSTRAP_SERVERS` | `kafka:29092` in Compose; `localhost:9092` from host | Default Docker stack broker |

### Fault Classes

| Code | Fault Name | Severity Tier | Key Physical Symptoms |
|---|---|---|---|
| 0 | Normal Operation | NORMAL | Vibration $< 2.1$ mm/s, Temp $55–62$°C, Current $24$ A, CHI $\ge 85\%$ |
| 1 | Bearing Inner/Outer Race Fault | CRITICAL | High vibration peaks ($>6.5$ mm/s), acoustic hiss ($>80$ dB) |
| 2 | Stator Winding Overheating | CRITICAL | Rapid thermal runaway ($>90$°C), current surge ($>35$ A) |
| 3 | Dynamic Rotor Imbalance | WARNING | 1X rotational vibration harmonics, periodic chassis vibration |
| 4 | Hydraulic Cavitation | CRITICAL | Discharge pressure drop ($<2.0$ bar), acoustic turbulence |
| 5 | Sensor Drift / Calibration Error | WARNING | Linear bias in thermal/acoustic sensors; physical asset remains safe |

---

## 4. Full Life of a Telemetry Event

```
[1. Simulation] ---> [2. Digital Twin] ---> [3. Residuals & CHI] ---> [4. 14-D Vector]
       |                     |                       |                       |
       v                     v                       v                       v
generate_sample()    process_telemetry()     R = |X - X_hat|         [Raw_7 || Res_7]
t = 100 ms cadence   Virtual Motor Physics   Z = max(0, (R-mu)/std)  14 float32 inputs
                                             CHI = 100*exp(-0.25*sum)
                                                                             |
[8. Dashboard] <--- [7. WebSocket] <--- [6. Windowing] <--- [5. Two-Stage Ensemble]
       |                     |                       |                       |
Canvas Visualizer    /ws/stream Push         5-second sliding        Stage 1: P(Anom) < 0.45?
Dynamic RPM & Glow   JSON Serialized         Rolling averages        YES -> Normal (~1.5 ms)
Multi-Channel Charts Bounded Retries         Peak acceleration       NO  -> Stage 2 ExtraTrees
Audit Alert Feed                                                            Diagnosis (~4.8 ms)
```

1. **Step 1 (Generation):** `IIoTSensorStreamSimulator` computes raw physical values at 10 Hz incorporating grid jitter, active mechanical load (75% nominal), and active fault coefficients.
2. **Step 2 (Digital Twin Processing):** `IndustrialDigitalTwin` accepts the raw packet and calculates nominal expected values based on slip curves and thermal diffusion models.
3. **Step 3 (Residual & Health Evaluation):** 7 residual channels are extracted. Standardized Z-scores are computed against healthy calibration baselines. The Composite Health Index is computed and exponentially smoothed.
4. **Step 4 (Feature Assembly):** A 14-D vector is constructed in strict order: `[vibration_rms, vibration_peak, temperature, rpm, current_amp, pressure_bar, acoustic_db, res_vibration_rms, res_vibration_peak, res_temperature, res_rpm, res_current_amp, res_pressure_bar, res_acoustic_db]`.
5. **Step 5 (Inference Pipeline):**
   - The vector is normalized via `StandardScaler`.
   - **Stage 1 (SGDClassifier):** If anomaly score $< 0.45$, packet is diagnosed as `Normal Operation` (Fast Path, $\sim 1.5$ ms total delay).
   - **Stage 2 (ExtraTreesClassifier):** If anomaly score $\ge 0.45$, Stage 2 evaluates the full fault ensemble to identify the specific failure class (Diagnostic Path, $\sim 4.8$ ms total delay).
6. **Step 6 (Sliding Window Analytics):** Rolling 50-sample (5-second) averages and peak metrics are computed.
7. **Step 7 (WebSocket Broadcast):** Packet is broadcast over `/ws/stream` to all registered browser clients.
8. **Step 8 (Client Rendering):** The operations console updates the rotating motor canvas, plots the new data points on Canvas charts, updates the KPI cards, and logs an alert if a critical fault is active.

---

## 5. Service States & Operational Lifecycle

The system clearly differentiates between operational stages:
- **Alive:** The FastAPI HTTP server is up and listening on port 8000.
- **Ready:** Models and scalers are loaded into memory and ready for inference.
- **Processing:** The 10 Hz asynchronous streaming loop is actively ticking and computing inferences.
- **Broadcasting:** Active WebSocket clients are receiving JSON telemetry updates.

### Safe Lifecycle Control
- Stopping the stream engine via `POST /api/services/stream-engine/stop` halts the telemetry generation and inference loops.
- **The web server and dashboard remain fully functional.** Operators can view logs, examine offline benchmarks, and restart the pipeline with a single click without browser disconnect errors.

---

## 6. Mathematical Formulas & Viva Reference

### Why Digital Twin Residuals are Superior to Raw Sensor Data
Raw sensor readings vary significantly under normal load changes (e.g. higher current when pumping denser fluid). A traditional classifier trained only on raw features may misclassify load changes as faults. The Digital Twin calculates expected current for the higher load; thus, the **residual remains near zero**. A fault is flagged only when the physical system diverges from expected physics.

### Health Index Formula
$$\text{CHI}_{\text{raw}} = 100 \times \exp\left(-0.25 \sum_{i=1}^{7} w_i \cdot z_i(t)\right)$$
Where:
$$z_i(t) = \max\left(0, \frac{R_i(t) - \mu_i}{\sigma_i}\right)$$
- If all residuals are at baseline ($z_i = 0$), $\exp(0) = 1 \implies \text{CHI} = 100.0\%$.
- As anomalies grow ($z_i \to \infty$), $\exp(-\text{large}) \to 0 \implies \text{CHI}$ drops exponentially.
- Clamped strictly between $5.0\%$ and $100.0\%$ to avoid numerical underflow or impossible percentages.

---

## 7. Developer Extension Recipes

### Recipe A: Adding a New Sensor Channel (e.g., Bearing Flux)
1. Add baseline parameters to `config/settings.py` under `ASSET_METADATA`.
2. Update `data/generator.py` in `generate_sample()` to simulate the new channel.
3. Update `models/digital_twin.py`: add expected physics in `compute_virtual_state()` and residual baseline in `self.residual_baselines`.
4. Update `FEATURE_NAMES` in `models/two_stage_ensemble.py`.
5. Run `python -m models.train_models` to re-train the models with the new $(7+1) \times 2 = 16\text{-D}$ feature vector.
6. Run `rtk python -m pytest tests/ -v` to verify test suite pass.

### Recipe B: Adding a New Fault Scenario
1. Add fault description to `FAULT_CLASSES` in `config/settings.py`.
2. Add physical fault signature in `data/generator.py` under `set_fault_mode()`.
3. Add fault button in `dashboard/templates/index.html`.
4. Retrain models via `python -m models.train_models`.
