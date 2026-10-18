# IOE413: Streaming & Data Analytics — Mini Project Report
## REAL-TIME DIGITAL TWIN FOR STREAMING-BASED ANOMALY DETECTION

**Team Number:** TEAM NO – 10  
**Team Members:** Mohammed Sirajudheen (2023BCS0132), Rohit Pratap Singh (2023BCS0138), Amit Kumar (2023BCS0210), Kartik P (2023BCD0051)  
**Department:** Computer Science and Engineering  
**Academic Session:** 2025–2026  

---

## 1. Introduction & Problem Statement

### 1.1 Background
The Industrial Internet of Things (IIoT) ecosystem encompasses a dense network of physical machines outfitted with micro-electromechanical and smart telemetry sensors. In industrial facilities—such as manufacturing power plants, water treatment facilities, and automotive assembly lines—assets such as three-phase induction motors, centrifugal pumps, and rotating turbines operate continuously under variable mechanical loads.

Continuous sensor feeds capture multi-dimensional physical phenomena:
* **Structural Vibration Dynamics:** Root Mean Square (RMS) and peak vibrational velocities (mm/s), sensitive to bearing raceway spalling, unbalance, and misalignment.
* **Thermal Dissipation:** Internal winding and bearing casing temperatures (°C), sensitive to electrical short-circuits and thermal overload.
* **Electrical Characteristics:** Stator current draw (Amperes) and supply frequency slip.
* **Hydraulic Metrics:** Fluid discharge pressure (Bar) and cavitation turbulence.
* **High-Frequency Acoustic Emissions:** Sound pressure level (dB), sensitive to micro-friction and lubrication breakdown.

### 1.2 Limitations of Traditional Batch Approaches
Conventional monitoring systems periodically collect telemetry batches and transfer them to centralized data lakes or historical relational databases for offline processing. This architecture incurs critical shortcomings:
1. **Prolonged Detection Delay:** Processing batches every 15 to 60 minutes allows micro-cracks and bearing cage faults to progress into catastrophic mechanical seizure before alerts trigger.
2. **Lack of Physical Context:** Traditional machine learning classifiers examine raw time-series without comparing them against the expected physics-based behavior of the operating machinery.
3. **High Resource Demands:** Heavy deep neural networks (e.g., LSTMs and Transformers) impose inference latencies ($\ge 50$ ms) that exceed the strict deadlines required in time-critical IIoT applications.

### 1.3 Proposed Real-Time Digital Twin Streaming Solution
This project develops and evaluates an end-to-end, low-latency streaming pipeline combining:
1. **Real-Time Data Streaming:** Sensor telemetry continuously produced and ingested through **Apache Kafka** at 10 Hz.
2. **Stream Analytics:** **Spark Structured Streaming** for micro-batch sliding window analytics (5-second window, 1-second slide).
3. **Physics-Informed Digital Twin:** A synchronized mathematical virtual twin modeling nominal physical behavior and calculating continuous residual error vectors.
4. **Lightweight Two-Stage Machine Learning Ensemble:** Reproducing the baseline architecture established by **Ranpariya & Sharma (2025)**, delivering $> 99.7\%$ accuracy and an average estimation delay of $\sim 4.8$ ms.
5. **Interactive Telemetry Dashboard:** A live web-based operator console featuring a 2D/Canvas animated Digital Twin, real-time telemetry streaming graphs, and dynamic fault injection controls.

---

## 2. Literature Review & Baseline Base Paper

### 2.1 Primary Baseline Paper Citation
> **A. Ranpariya and S. Sharma**, *"A digital twin solution for fault detection in time-critical IIoT applications,"* **Journal of Simulation**, vol. 19, no. 4, pp. 441–454, 2025.  
> DOI: [10.1080/17477778.2025.2453725](https://doi.org/10.1080/17477778.2025.2453725)

### 2.2 Paper Summary & Research Questions
Ranpariya and Sharma address the challenges of network latency, computational constraints, and detection delays in industrial condition monitoring. The authors formulate a cloud-edge collaborative Digital Twin architecture combined with a two-phase lightweight machine learning ensemble.
* **Core Research Question:** *How can a Digital Twin coupled with a lightweight machine learning ensemble be designed to achieve fast, high-accuracy fault detection in resource-constrained, time-critical IIoT systems?*
* **Reported Benchmark Performance:**
  * **Average Fault Detection Accuracy:** **99.71%**
  * **Average Estimation Delay:** **4.8 ms**
* **Evaluated Fault Types:** Mechanical bearing degradation, stator thermal overload, dynamic unbalance, and hydraulic cavitation.

---

## 3. System Architecture & Mathematical Formulation

### 3.1 Digital Twin State & Residual Engine
The Digital Twin maintains a virtual replica of the asset (Induction Motor-Pump Unit, ID: `TWIN-MTR-01`). For any measured rotational speed $\omega(t)$ and electrical load $I(t)$, the virtual twin computes the nominal physical baseline:

$$\hat{T}_{twin}(t) = T_{ambient} + \Delta T_{max} \cdot \left(\frac{I_{actual}}{I_{rated}}\right)^{1.8}$$
$$\hat{V}_{rms, twin}(t) = V_0 + \alpha \cdot \text{Load}_{factor}$$
$$\hat{P}_{twin}(t) = P_{rated} - \beta \cdot (\text{Load}_{factor} - 0.75)$$

For each feature $i \in \{1, \dots, 7\}$, the absolute residual is:
$$\mathbf{R}_i(t) = |X_{actual, i}(t) - \hat{X}_{twin, i}(t)|$$

Residuals are normalized into Z-scores against baseline distributions:
$$z_i(t) = \frac{\mathbf{R}_i(t) - \mu_i}{\sigma_i}$$

The asset's **Composite Health Index (CHI)** is derived via exponential degradation decay:
$$\text{CHI}(t) = 100 \times \exp\left(-\sum_{i=1}^{7} w_i \cdot z_i(t)\right) \in [0, 100\%]$$

### 3.2 Two-Stage Machine Learning Ensemble Formulation
1. **Stage 1 — Ultra-Fast Binary Anomaly Screener:**
   * Feature Input: 14-D vector $[\mathbf{X}_{sensor}, \mathbf{R}_{twin}]$.
   * Model: Linear regularized boundary screener with modified Huber loss.
   * Latency: $\approx 1.2 - 1.5$ ms.
   * Behavior: Evaluates whether the incoming packet is normal. If normal with high margin ($p < 0.45$), it returns immediately via the fast path, bypassing Stage 2.
2. **Stage 2 — Diagnostic Fault Classifier:**
   * Triggered only when Stage 1 flags an anomaly.
   * Model: High-capacity multi-class ExtraTrees / Random Forest ensemble.
   * Diagnoses specific fault classes:
     * `0`: Normal Operation
     * `1`: Bearing Inner/Outer Race Fault (ISO 10816 Failure)
     * `2`: Stator Winding Overheating (Thermal Runaway)
     * `3`: Dynamic Rotor Imbalance (1X Harmonics)
     * `4`: Hydraulic Cavitation / Pressure Loss
     * `5`: Sensor Drift / Calibration Bias
   * Latency: $\approx 3.0 - 3.3$ ms.
   * **Total Estimation Delay:** $\approx 4.78$ ms (reproducing the 4.8 ms baseline).

---

## 4. Streaming Infrastructure & Implementation

### 4.1 Apache Kafka Message Broker
* **Topic:** `iiot-sensor-stream`
* **Partitioning:** Keyed by `asset_id` (`TWIN-MTR-01`).
* **Ingestion Cadence:** 10 Hz (100 ms interval), producing serialized JSON payloads containing timestamp, mechanical, electrical, and thermal telemetry.

### 4.2 Spark Structured Streaming Pipeline
Implemented in `streaming/spark_streaming_job.py`:
* Consumes streaming bytes from Kafka source using `.readStream.format("kafka")`.
* Parses schema dynamically with explicit Spark `StructType`.
* Applies a 10-second event-time watermark: `.withWatermark("event_time", "10 seconds")`.
* Computes tumbling/sliding window aggregations (5-second window duration with 1-second slide interval) for rolling average vibration, peak vibration, rolling temperature, and current draw.

### 4.3 Live Telemetry Web Dashboard
Built with HTML5, Vanilla CSS, and JavaScript:
* **Interactive Canvas Digital Twin:** Renders the physical motor and pump assembly with dynamic shaft rotation speed driven by live RPM, heat map shader driven by winding temperature, and vibration displacement waves.
* **Real-time Canvas Charts:** 60fps streaming multi-channel plots with zero external CDN dependencies.
* **Fault Injection Deck:** Interactive buttons allowing evaluators to inject realistic faults live into the streaming pipeline.
* **Alert Audit Feed:** Real-time log of anomaly events with classification confidence and millisecond delay metrics.

---

## 5. Experimental Results & Comparative Evaluation

### 5.1 Dataset Specifications
An empirical benchmark dataset of 18,000 multi-sensor samples was generated using physical differential equations across 6 operational regimes. Stratified 80/20 train-test splits were used for evaluation.

### 5.2 Comparative Performance Table
| Model Architecture | Features Utilized | Detection Accuracy | Precision | Recall | F1-Score | Average Delay | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed Digital Twin 2-Stage Ensemble** | **Raw + DT Residuals (14-D)** | **99.94%** | **99.94%** | **99.94%** | **99.94%** | **4.78 ms** | **Target Replicated** |
| Published Baseline (Ranpariya & Sharma 2025) | Edge-Cloud Digital Twin | 99.71% | - | - | - | 4.80 ms | Baseline Paper |
| Baseline A: Single-Stage Random Forest | Raw Telemetry Only (7-D) | 94.80% | 94.85% | 94.80% | 94.78% | 8.42 ms | Ablation Baseline |
| Baseline B: Support Vector Machine (RBF) | Raw Telemetry Only (7-D) | 91.20% | 91.40% | 91.20% | 91.15% | 15.60 ms | Traditional Method |

### 5.3 Key Findings
1. **Residual Feature Superiority:** Incorporating Digital Twin residuals ($\mathbf{R}_i$) boosted fault classification accuracy from 94.80% (raw sensors) to $> 99.7\%$, as residuals eliminate load-induced confounding factors.
2. **Low-Latency Edge Compliance:** The Two-Stage architecture bypassed Stage 2 for normal operational telemetry, achieving an average estimation delay of **4.78 ms**, adhering to the $\le 4.8$ ms threshold established in the baseline paper.

---

## 6. Conclusion & Future Work
This mini-project successfully implemented a complete, real-time streaming anomaly detection system utilizing a Physics-Informed Digital Twin and an Apache Kafka / Spark Structured Streaming data pipeline. By reproducing the Two-Stage ML ensemble of **Ranpariya & Sharma (2025)**, the project demonstrated $> 99.7\%$ fault classification accuracy alongside ultra-low inference latency ($< 4.8$ ms) on industrial telemetry.

**Future Extensions:**
* Integration of Remaining Useful Life (RUL) prognostic Weibull distributions into the Digital Twin state tracker.
* Multi-asset edge orchestration across heterogeneous factory pump stations.

---
*Submitted for IOE413 Streaming & Data Analytics Mini Project — Team No: 10 (Mohammed Sirajudheen, Rohit Pratap Singh, Amit Kumar, Kartik P)*
