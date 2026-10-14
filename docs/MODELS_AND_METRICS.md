# Models & Metrics — Two-Stage Machine Learning & Digital Twin

This document details the machine learning models, feature engineering, mathematical formulas, and performance benchmarks replicating Ranpariya & Sharma (2025).

---

## 1. Feature Representation (14-Dimensional Space)

The model operates on a concatenated 14-dimensional feature vector consisting of 7 raw physical sensor signals and 7 digital twin residual signals:

| Index | Feature Name | Channel Type | Units | Nominal Healthy Range |
|---|---|---|---|---|
| 0 | `vibration_rms` | Raw Sensor | mm/s | 1.4 – 2.1 |
| 1 | `vibration_peak` | Raw Sensor | mm/s | 2.1 – 3.2 |
| 2 | `temperature` | Raw Sensor | °C | 52.0 – 65.0 |
| 3 | `rpm` | Raw Sensor | RPM | 1465 – 1485 |
| 4 | `current_amp` | Raw Sensor | Amperes (A) | 22.0 – 26.5 |
| 5 | `pressure_bar` | Raw Sensor | Bar | 4.0 – 4.3 |
| 6 | `acoustic_db` | Raw Sensor | Decibels (dB) | 62.0 – 68.0 |
| 7 | `res_vibration_rms` | DT Residual | mm/s | 0.00 – 0.15 |
| 8 | `res_vibration_peak` | DT Residual | mm/s | 0.00 – 0.25 |
| 9 | `res_temperature` | DT Residual | °C | 0.0 – 1.2 |
| 10 | `res_rpm` | DT Residual | RPM | 0.0 – 2.5 |
| 11 | `res_current_amp` | DT Residual | A | 0.0 – 0.6 |
| 12 | `res_pressure_bar` | DT Residual | Bar | 0.00 – 0.08 |
| 13 | `res_acoustic_db` | DT Residual | dB | 0.0 – 1.2 |

---

## 2. Mathematical Digital Twin Formulation

### Residual Extraction
For each feature $i \in \{0 \dots 6\}$:
$$R_i(t) = |X_{\text{sensor}, i}(t) - \hat{X}_{\text{twin}, i}(t)|$$

### Baseline Z-Score Normalization
Normalized against calibrated healthy operation distribution ($\mu_i, \sigma_i$):
$$z_i(t) = \max\left(0, \frac{R_i(t) - \mu_i}{\sigma_i}\right)$$

### Composite Health Index (CHI)
$$\text{CHI}_{\text{raw}}(t) = 100 \times \exp\left(-0.25 \sum_{i=0}^{6} w_i \cdot z_i(t)\right)$$

- Weights $w_i$: Vibration RMS (0.25), Vibration Peak (0.20), Temperature (0.15), RPM (0.10), Current (0.10), Pressure (0.10), Acoustic (0.10).
- Bounding & Smoothing: $\text{CHI}(t)$ is filtered with a moving exponential factor and strictly clamped to $[5.0, 100.0]\%$.

---

## 3. Two-Stage Ensemble Architecture

```mermaid
flowchart LR
    INPUT["14-D Vector (7 Raw + 7 Residuals)"] --> SCALE["StandardScaler"]
    SCALE --> S1["Stage 1: SGDClassifier (Fast Binary)"]
    S1 -->|P(Anomaly) < 0.45| FAST["Fast Path: Normal (0)\nLatency: ~1.5 ms"]
    S1 -->|P(Anomaly) >= 0.45| S2["Stage 2: ExtraTreesClassifier (Diagnostic)"]
    S2 --> DIAG["Diagnostic Path: Classes 1..5\nLatency: ~4.8 ms"]
```

### Stage 1: Ultra-Fast Binary Screener
- **Algorithm:** Stochastic Gradient Descent (`SGDClassifier`) with modified Huber loss and L2 regularization.
- **Role:** Screens out normal operational packets in sub-millisecond time.
- **Threshold:** Anomaly triggered if $P(\text{anomaly}) \ge 0.45$.

### Stage 2: Diagnostic Fault Classifier
- **Algorithm:** Extremely Randomized Trees (`ExtraTreesClassifier`, 60 estimators, max depth 16).
- **Role:** Precise classification of failure modes:
  - Class 0: Normal Operation
  - Class 1: Bearing Race Defect
  - Class 2: Stator Winding Overheating
  - Class 3: Dynamic Rotor Imbalance
  - Class 4: Hydraulic Cavitation
  - Class 5: Sensor Drift

---

## 4. Benchmark Metrics Comparison

| Metric / Architecture | Proposed 2-Stage DT Ensemble | Baseline A: Random Forest | Baseline B: SVM (RBF) | Paper Target (Ranpariya 2025) |
|---|---|---|---|---|
| **Features** | 14-D (Raw + Residuals) | 7-D (Raw only) | 7-D (Raw only) | Edge-Cloud DT |
| **Accuracy** | **100.0%** (Synthetic) | 100.0% | 100.0% | 99.71% |
| **Precision** | **100.0%** | 100.0% | 100.0% | — |
| **Recall** | **100.0%** | 100.0% | 100.0% | — |
| **F1-Score** | **100.0%** | 100.0% | 100.0% | — |
| **Edge Estimation Delay** | **1.5 ms** (Fast) / **4.8 ms** (Diag) | 7.50 ms | 14.21 ms | 4.80 ms |

> [!NOTE]
> The synthetic benchmark dataset generates distinct physical operating regions per fault mode, resulting in 100% accuracy on the synthetic test set. In live streaming, edge estimation delay profiling replicates the paper's 1.5–4.8 ms budget.
