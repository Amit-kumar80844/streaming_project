# Project Overview — Real-Time Digital Twin for Streaming Anomaly Detection

**Course:** IOE413 Streaming & Data Analytics  
**Academic Team:** Team 10 — Mohammed Sirajudheen (2023BCS0132), Rohit Pratap Singh (2023BCS0138), Amit Kumar (2023BCS0210), and Kartik P (2023BCD0051)  
**Baseline Publication:** A. Ranpariya and S. Sharma, *"A digital twin solution for fault detection in time-critical IIoT applications,"* *Journal of Simulation*, vol. 19, no. 4, pp. 441–454, 2025. [DOI: 10.1080/17477778.2025.2453725](https://doi.org/10.1080/17477778.2025.2453725)

---

## 1. Problem Statement

Industrial Internet of Things (IIoT) rotating machinery—such as 15 kW induction motor and centrifugal pump assemblies—generates high-frequency multivariate telemetry streams:
- Structural vibration (RMS and Peak acceleration)
- Thermal dynamics (motor winding and bearing casing temperature)
- Rotational speed (RPM)
- Electrical draw (3-phase stator current)
- Hydraulic discharge pressure
- Acoustic emissions (dB)

In time-critical manufacturing plants, mechanical and electrical faults (bearing inner/outer race flaking, rotor dynamic unbalance, stator winding thermal runaway, hydraulic cavitation) escalate rapidly. Batch analytical systems incur multi-minute processing delays, leading to catastrophic downtime. Conversely, heavy deep neural network inference directly on resource-constrained edge microcontrollers introduces inference latencies that violate real-time control constraints.

## 2. Project Goals

1. **Sub-5ms End-to-End Estimation Delay:** Replicate the two-stage inference topology from Ranpariya & Sharma (2025) to achieve sub-millisecond screening for normal operations and $<5$ ms full diagnostic latency.
2. **Physics-Informed Digital Twin Residual Modeling:** Maintain a continuous real-time mathematical model of nominal operating dynamics to extract 7-D residual signatures that augment raw sensor measurements into a 14-D feature space.
3. **High-Frequency Streaming Orchestration:** Ingest and process telemetry at 10 Hz (100 ms emissions) with windowed aggregate tracking (5-second sliding windows).
4. **Interactive Operations Console:** Provide an industrial-grade telemetry and diagnostics dashboard with live asset visualization, real-time Canvas charts, on-demand fault injection, and service lifecycle controls.
5. **No-CLI One-Click Deployment:** Provide a turnkey containerized Docker stack and Windows double-click launcher (`start.bat` / `stop.bat`) requiring zero command-line configuration for end users.

## 3. Scope and Boundaries

| In-Scope | Out-of-Scope (Optional / Reference) |
|---|---|
| In-process 10 Hz streaming engine | Physical hardware sensor wiring (telemetry is simulated) |
| Physics-based induction motor/pump digital twin | Multi-cluster Spark/Kafka deployments beyond the local default Docker stack |
| Two-stage ML ensemble (SGD + ExtraTrees) | Cloud-hosted multi-tenant SaaS authentication |
| REST and WebSocket telemetry API | Arbitrary shell command execution from the web browser |
| 5-row responsive industrial operations console | Modifying production PLC firmware |

## 4. Key Personas & Use Cases

- **Reliability Engineers:** Monitor asset Composite Health Index (CHI), inspect vibration and thermal trends, and examine alert history.
- **Academic Evaluators / Viva Assessors:** Validate reproduction of Ranpariya & Sharma (2025) benchmark metrics, trigger dynamic fault injections, and inspect latency budgets.
- **Plant Operators:** Observe live asset status and safely pause or restart the streaming ingestion pipeline via one-click service controls.

## 5. Live Demonstration Workflow

1. **Start System:** Double-click `start.bat` on Windows or execute `python run.py`.
2. **Examine Nominal State:** The motor runs at ~1480 RPM, Composite Health Index is in the Optimal tier ($\ge 85\%$), and inference delay is ~1.5 ms (Stage 1 fast path).
3. **Inject Bearing Race Fault:** Click **Bearing Defect** (Class 1) at 85% intensity. Vibration spikes, Stage 1 detects anomaly, Stage 2 diagnoses defect in 4.7 ms, and CHI drops into Degradation tier.
4. **Inject Stator Overheating:** Click **Stator Overheat** (Class 2). Temperature climbs past 90°C, health index plummets into Critical tier ($<60\%$), and motor aura turns red.
5. **Reset & Restore:** Click **Normal Operation** (Class 0). The physics simulator recovers, residuals return to baseline, and CHI climbs back to 100%.
6. **Pipeline Lifecycle Control:** Stop and restart the streaming engine directly from the Pipeline & Controls deck without crashing the server.
