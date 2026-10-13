"""
Physics-Informed IIoT Telemetry Generator for Industrial Asset Digital Twin.
Simulates high-fidelity multi-sensor data streams with real-time fault injection.
"""

import time
import math
import random
import numpy as np
import pandas as pd
from typing import Dict, Any, Generator

class IIoTSensorStreamSimulator:
    """
    Simulates real-time sensor telemetry from an industrial induction motor-pump unit.
    Includes physics-informed multi-variable coupling and fault signatures.
    """
    def __init__(self, asset_id: str = "TWIN-MTR-01"):
        self.asset_id = asset_id
        self.current_mode = 0  # 0: Normal
        self.mode_intensity = 0.0  # 0.0 to 1.0 severity
        self.step_count = 0
        self.start_time = time.time()
        
        # State variables for continuous physics tracking
        self.temp_internal = 58.0
        self.ambient_temp = 25.0
        self.current_rpm = 1480.0
        self.accumulated_wear = 0.0
        self.load_factor = 0.75  # 75% nominal load
        
    def set_fault_mode(self, fault_code: int, intensity: float = 1.0):
        """Inject specific fault mode dynamically into the stream."""
        self.current_mode = fault_code
        self.mode_intensity = max(0.1, min(1.0, intensity))
        
    def reset_to_normal(self):
        """Restore normal operational state."""
        self.current_mode = 0
        self.mode_intensity = 0.0

    def generate_sample(self, timestamp: float = None) -> Dict[str, Any]:
        """
        Generates a single physics-consistent telemetry record.
        """
        if timestamp is None:
            timestamp = time.time()
            
        self.step_count += 1
        t = self.step_count * 0.1  # virtual time in seconds (10 Hz)
        
        # Base operational fluctuations (grid frequency 50Hz, motor pole harmonics)
        grid_jitter = math.sin(2 * math.pi * 50 * t * 0.01) * 0.02
        load_variation = math.sin(t * 0.05) * 0.08 + (random.gauss(0, 0.01))
        active_load = max(0.5, min(1.0, self.load_factor + load_variation))
        
        # Baseline physical values
        base_rpm = 1480.0 - (active_load * 15.0) + (random.gauss(0, 1.2))
        base_current = 20.0 + (active_load * 8.5) + (random.gauss(0, 0.25))
        
        # Thermal dynamics: First-order differential response to current load
        target_temp = self.ambient_temp + 35.0 * (base_current / 28.5) ** 1.8
        self.temp_internal += (target_temp - self.temp_internal) * 0.02 + random.gauss(0, 0.08)
        
        # Mechanical baseline vibration (ISO 10816 Class II industrial machine)
        base_vib_rms = 1.6 + 0.5 * active_load + random.gauss(0, 0.08)
        base_vib_peak = base_vib_rms * (1.414 + random.uniform(0.1, 0.3))
        
        # Hydraulic baseline pressure
        base_pressure = 4.2 - 0.2 * (active_load - 0.75) + random.gauss(0, 0.04)
        
        # Acoustic baseline (dB)
        base_acoustic = 64.0 + 5.0 * active_load + random.gauss(0, 0.5)

        # ==========================================
        # FAULT INJECTION SIGNATURES
        # ==========================================
        label = self.current_mode
        fault_name = "Normal"
        
        vib_rms = base_vib_rms
        vib_peak = base_vib_peak
        temp = self.temp_internal
        rpm = base_rpm
        current = base_current
        pressure = base_pressure
        acoustic = base_acoustic
        
        sev = self.mode_intensity
        
        if label == 1:
            # Bearing Inner/Outer Race Fault: High-frequency impacts, sharp spike in peak vib & acoustic dB
            fault_name = "Bearing Fault"
            impact_pulses = abs(math.sin(2 * math.pi * 123.4 * t)) ** 5 * (6.0 * sev)
            vib_rms += 2.8 * sev + random.gauss(0, 0.3)
            vib_peak += 6.5 * sev + impact_pulses + random.gauss(0, 0.5)
            acoustic += 18.0 * sev + random.gauss(0, 1.2)
            temp += 4.0 * sev
            
        elif label == 2:
            # Stator Winding Overheating: Thermal runaway, phase current surge
            fault_name = "Winding Overheating"
            temp += 28.0 * sev + random.gauss(0, 0.4)
            current += 9.5 * sev + random.gauss(0, 0.6)
            vib_rms += 0.8 * sev
            acoustic += 3.5 * sev
            
        elif label == 3:
            # Dynamic Rotor Imbalance: Severe 1X rotational frequency vibration, speed oscillation
            fault_name = "Rotor Imbalance"
            rpm_mod = math.sin(2 * math.pi * (rpm / 60.0) * t) * (35.0 * sev)
            rpm += rpm_mod
            vib_rms += 5.2 * sev + random.gauss(0, 0.4)
            vib_peak += 7.0 * sev + random.gauss(0, 0.5)
            current += 3.0 * sev
            acoustic += 8.0 * sev
            
        elif label == 4:
            # Hydraulic Cavitation / Pressure Drop: Violent turbulence, acoustic spike, pressure drop
            fault_name = "Cavitation / Pressure Loss"
            pressure = max(0.5, pressure - 2.4 * sev + random.gauss(0, 0.2))
            acoustic += 22.0 * sev + random.gauss(0, 1.5)
            vib_rms += 3.4 * sev + random.gauss(0, 0.3)
            vib_peak += 4.5 * sev
            rpm += 15.0 * sev
            
        elif label == 5:
            # Sensor Drift / Failure: Calibration offset / stuck reading
            fault_name = "Sensor Drift"
            temp += 22.0 * sev  # false reading drift
            vib_rms = max(0.1, vib_rms * 0.2)  # sensor attenuation
            pressure += 2.0 * sev

        record = {
            "timestamp": round(timestamp, 4),
            "step": self.step_count,
            "asset_id": self.asset_id,
            "vibration_rms": round(float(vib_rms), 4),
            "vibration_peak": round(float(vib_peak), 4),
            "temperature": round(float(temp), 2),
            "rpm": round(float(rpm), 1),
            "current_amp": round(float(current), 2),
            "pressure_bar": round(float(pressure), 3),
            "acoustic_db": round(float(acoustic), 2),
            "fault_label": int(label),
            "fault_name": fault_name,
            "is_anomaly": int(label > 0)
        }
        return record

    def stream_records(self, interval_sec: float = 0.1) -> Generator[Dict[str, Any], None, None]:
        """Continuous generator yielding real-time records at requested cadence."""
        while True:
            t0 = time.time()
            yield self.generate_sample(t0)
            elapsed = time.time() - t0
            sleep_time = max(0.0, interval_sec - elapsed)
            time.sleep(sleep_time)


def generate_benchmark_dataset(num_samples: int = 15000, save_path: str = None) -> pd.DataFrame:
    """
    Generates a balanced multi-state dataset representing normal and 5 fault modes
    with varying severities for model training and scientific evaluation.
    """
    simulator = IIoTSensorStreamSimulator()
    records = []
    
    # Fault distribution: 50% normal, 10% for each of the 5 fault types
    modes = [0] * int(num_samples * 0.5)
    fault_modes = [1, 2, 3, 4, 5]
    samples_per_fault = int((num_samples * 0.5) / len(fault_modes))
    for f in fault_modes:
        modes.extend([f] * samples_per_fault)
        
    random.seed(42)
    np.random.seed(42)
    random.shuffle(modes)
    
    current_time = time.time() - (num_samples * 0.1)
    
    for i, mode in enumerate(modes):
        simulator.current_mode = mode
        simulator.mode_intensity = random.uniform(0.4, 1.0) if mode > 0 else 0.0
        rec = simulator.generate_sample(timestamp=current_time + (i * 0.1))
        records.append(rec)
        
    df = pd.DataFrame(records)
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"[Dataset Generator] Successfully saved {len(df)} samples to {save_path}")
    return df


if __name__ == "__main__":
    from pathlib import Path
    out_file = Path(__file__).resolve().parent / "dataset_benchmark.csv"
    generate_benchmark_dataset(num_samples=18000, save_path=str(out_file))
