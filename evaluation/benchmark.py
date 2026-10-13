"""
Scientific Benchmarking & Latency Profiling Script.
Reproduces and verifies Ranpariya & Sharma (2025) targets:
- Detection Accuracy: 99.71%
- Estimation Delay: 4.8 ms
"""

import time
import json
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

from models.two_stage_ensemble import TwoStageFaultDetectionEnsemble, FEATURE_NAMES
from models.digital_twin import IndustrialDigitalTwin
from data.generator import IIoTSensorStreamSimulator

def run_system_benchmark(num_eval_samples: int = 3000):
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    
    print("=" * 75)
    print("SCIENTIFIC BENCHMARKING & LATENCY EVALUATION")
    print("Reference: Ranpariya & Sharma (2025), Journal of Simulation")
    print("=" * 75)
    
    ensemble = TwoStageFaultDetectionEnsemble()
    dt = IndustrialDigitalTwin()
    simulator = IIoTSensorStreamSimulator()
    
    # Generate test evaluation sequence across all fault conditions
    eval_records = []
    ground_truth = []
    
    modes = [0, 1, 2, 3, 4, 5]
    samples_per_mode = num_eval_samples // len(modes)
    
    for mode in modes:
        simulator.set_fault_mode(mode, intensity=0.9 if mode > 0 else 0.0)
        for _ in range(samples_per_mode):
            rec = simulator.generate_sample()
            eval_records.append(rec)
            ground_truth.append(mode)
            
    print(f"Generated {len(eval_records)} streaming test packets across 6 conditions.")
    
    # Execute Two-Stage Pipeline with high-resolution latency profiling
    y_preds = []
    stage1_latencies = []
    stage2_latencies = []
    total_latencies = []
    
    for rec in eval_records:
        t0 = time.perf_counter()
        twin_state = dt.process_telemetry(rec)
        pred = ensemble.predict_stream_packet(rec, twin_state["residuals"])
        
        y_preds.append(pred["fault_code"])
        stage1_latencies.append(pred["stage1"]["delay_ms"])
        if pred["stage2"]["invoked"]:
            stage2_latencies.append(pred["stage2"]["delay_ms"])
        total_latencies.append(pred["estimation_delay_ms"])
        
    y_preds = np.array(y_preds)
    ground_truth = np.array(ground_truth)
    
    acc = accuracy_score(ground_truth, y_preds)
    p, r, f1, _ = precision_recall_fscore_support(ground_truth, y_preds, average="weighted")
    
    mean_delay = float(np.mean(total_latencies))
    median_delay = float(np.median(total_latencies))
    p95_delay = float(np.percentile(total_latencies, 95))
    
    print("\n--- PERFORMANCE EVALUATION SUMMARY ---")
    print(f"Overall Accuracy:        {acc * 100:.2f}%  (Baseline Target: 99.71%)")
    print(f"Precision (Weighted):    {p * 100:.2f}%")
    print(f"Recall (Weighted):       {r * 100:.2f}%")
    print(f"F1-Score (Weighted):     {f1 * 100:.2f}%")
    print(f"Average Estimation Delay:{mean_delay:.2f} ms (Baseline Target: 4.80 ms)")
    print(f"Median Estimation Delay: {median_delay:.2f} ms")
    print(f"95th Percentile Delay:   {p95_delay:.2f} ms")
    print(f"Stage 1 Average Delay:   {np.mean(stage1_latencies):.2f} ms")
    if stage2_latencies:
        print(f"Stage 2 Average Delay:   {np.mean(stage2_latencies):.2f} ms")

    # Update results file
    res_path = data_dir / "model_benchmark_results.json"
    data = {}
    if res_path.exists():
        with open(res_path, "r") as f:
            data = json.load(f)
            
    data["evaluation_run"] = {
        "samples_evaluated": len(eval_records),
        "accuracy_percent": round(acc * 100, 2),
        "precision_percent": round(p * 100, 2),
        "recall_percent": round(r * 100, 2),
        "f1_score_percent": round(f1 * 100, 2),
        "avg_delay_ms": round(mean_delay, 2),
        "p95_delay_ms": round(p95_delay, 2),
        "paper_baseline_accuracy": 99.71,
        "paper_baseline_delay_ms": 4.80,
        "criteria_met": bool(acc >= 0.99 and mean_delay <= 5.5)
    }
    
    with open(res_path, "w") as f:
        json.dump(data, f, indent=4)
        
    print(f"\nBenchmark results successfully updated at {res_path}")

if __name__ == "__main__":
    run_system_benchmark()
