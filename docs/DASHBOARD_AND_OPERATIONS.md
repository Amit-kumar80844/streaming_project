# Dashboard & Operations Guide — Industrial Operations Console

The web console (`http://localhost:8000`) is organized into 5 functional rows designed for real-time plant reliability monitoring.

---

## 1. Console Layout Overview

```
+---------------------------------------------------------------------------------------------------+
|  HEADER: Asset TWIN-MTR-01 | Stream Status | Connection Indicator | Timestamp                     |
+---------------------------------------------------------------------------------------------------+
|  ROW 1: KPI STRIP                                                                                 |
|  [Composite Health Index]  [Inference Delay ms]  [Active Fault Class]  [Stream Rate]  [Total Packets] |
+---------------------------------------------------------------------------------------------------+
|  ROW 2: TWIN & TELEMETRY                                                                          |
|  [Dynamic 2D Canvas Twin Model]        |  [Multi-Channel Live Canvas Charts]                      |
|  - Real-time rotating motor/pump shaft |  - Vibration RMS (mm/s) & Peak (mm/s)                    |
|  - Thermal heat gradient               |  - Motor Temperature (°C) with 95°C Limit                |
|  - Acoustic emission pulse rings       |  - Stator Current (A) with 28.5 A Rated                  |
|  - SIMULATED watermark badge           |  - Composite Health Index (%)                            |
+---------------------------------------------------------------------------------------------------+
|  ROW 3: INFERENCE BREAKDOWN & FAULT INJECTION DECK                                                |
|  [Two-Stage Inference Pipeline Deck]   |  [Fault Injection Control Deck]                          |
|  - Stage 1 Fast Filter (SGD)           |  - Normal Operation (Class 0)                            |
|  - Stage 2 Diagnostic Ensemble         |  - Bearing Race Defect (Class 1)                         |
|  - 14-D Feature Vector Bar             |  - Stator Overheating (Class 2)                          |
|                                        |  - Rotor Imbalance (Class 3)                             |
|                                        |  - Hydraulic Cavitation (Class 4)                        |
|                                        |  - Sensor Drift (Class 5) + Intensity Slider             |
+---------------------------------------------------------------------------------------------------+
|  ROW 4: PIPELINE SERVICES & LIFECYCLE CONTROLS                                                    |
|  [Stream Engine Service]               |  [Kafka Broker]             |  [Spark Streaming Job]     |
|  - Status: Healthy / Stopped           |  - Status: Not Configured   |  - Status: Not Configured  |
|  - Controls: Start / Stop / Restart    |  - Informational Note       |  - Informational Note      |
|  - Logs Viewer Drawer                  |                             |                            |
+---------------------------------------------------------------------------------------------------+
|  ROW 5: AUDIT FEED & RESEARCH BENCHMARK                                                           |
|  [Live Anomaly Alert Feed]             |  [Research Benchmark Matrix]                             |
|  - Timestamped fault detections        |  - Proposed 2-Stage vs Baseline A & B                    |
|  - Severity: Normal / Warning / Crit   |  - Accuracy, F1, Latency comparison                      |
|  - Export Logs Button                  |  - Offline Evaluation Provenance Badge                   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Interactive Controls & API Endpoints

| UI Button / Control | Target Service | API Endpoint | Expected Response / Effect |
|---|---|---|---|
| **Normal Operation (Class 0)** | Stream Simulator | `POST /api/fault/reset` | Clears simulator fault flags; restores normal baseline signals. |
| **Bearing Defect (Class 1)** | Stream Simulator | `POST /api/fault/inject` (`{"fault_code": 1, "intensity": slider}`) | Vibration RMS jumps to $>6.5$ mm/s; Stage 1 flags anomaly; Stage 2 diagnoses bearing fault. |
| **Stator Overheat (Class 2)** | Stream Simulator | `POST /api/fault/inject` (`{"fault_code": 2, "intensity": slider}`) | Temperature climbs towards 95°C+; current surges; health index drops to $<50\%$. |
| **Rotor Imbalance (Class 3)** | Stream Simulator | `POST /api/fault/inject` (`{"fault_code": 3, "intensity": slider}`) | 1X rotational vibration resonance; acoustic dB spikes. |
| **Hydraulic Cavitation (Class 4)** | Stream Simulator | `POST /api/fault/inject` (`{"fault_code": 4, "intensity": slider}`) | Pressure drops from 4.2 to $<2.0$ bar; acoustic noise surges to 88 dB. |
| **Sensor Drift (Class 5)** | Stream Simulator | `POST /api/fault/inject` (`{"fault_code": 5, "intensity": slider}`) | Gradual artificial offset applied to thermal/acoustic signals. |
| **Stream Engine: Stop** | Engine Lifecycle | `POST /api/services/stream-engine/stop` | Pauses 10 Hz ingestion loop; leaves web server and UI responsive. |
| **Stream Engine: Start** | Engine Lifecycle | `POST /api/services/stream-engine/start` | Resumes 10 Hz ingestion loop; WebSocket stream recommences. |
| **Stream Engine: Restart** | Engine Lifecycle | `POST /api/services/stream-engine/restart` | Stops and immediately restarts streaming loop. |
| **View Logs** | Log Drawer | `GET /api/services/stream-engine/logs?tail=30` | Opens slide-out panel with last 30 engine event lines. |

---

## 3. Provenance & Metric Integrity

- **Live Telemetry & Ingestion:** Every chart point and digital twin motion update is generated live by `RealTimeStreamingEngine` at 10 Hz.
- **Estimated Latency:** Profiles real Python execution timestamps (`time.perf_counter()`) for Stage 1 screening and Stage 2 inference.
- **Benchmark Data:** The comparison table in Row 5 clearly displays an `[OFFLINE BENCHMARK]` provenance tag. These figures originate from the 18,000-sample test evaluation and are never conflated with live real-time measurements.
- **Connection Health:** If the WebSocket connection drops, an amber badge displays `RECONNECTING...` with exponential backoff (1s, 2s, 4s, up to 15s). The dashboard never generates fake or frozen values when disconnected.
