"""
Tests for TwoStageFaultDetectionEnsemble (Stage 1 Binary + Stage 2 Multi-class).
"""

import pytest
from models.two_stage_ensemble import TwoStageFaultDetectionEnsemble

def test_ensemble_initialization_and_weights():
    ensemble = TwoStageFaultDetectionEnsemble()
    assert ensemble.is_trained is True
    assert ensemble.stage1_model is not None
    assert ensemble.stage2_model is not None
    assert ensemble.scaler is not None

def test_ensemble_nominal_prediction():
    ensemble = TwoStageFaultDetectionEnsemble()
    telemetry = {
        "vibration_rms": 1.85,
        "vibration_peak": 2.8,
        "temperature": 58.0,
        "rpm": 1480.0,
        "current_amp": 24.0,
        "pressure_bar": 4.2,
        "acoustic_db": 67.5,
    }
    residuals = {
        "vibration_rms": 0.05,
        "vibration_peak": 0.1,
        "temperature": 0.3,
        "rpm": 1.0,
        "current_amp": 0.2,
        "pressure_bar": 0.04,
        "acoustic_db": 0.5,
    }
    pred = ensemble.predict_stream_packet(telemetry, residuals)
    assert pred["is_anomaly"] is False
    assert pred["fault_code"] == 0
    assert pred["stage2"]["invoked"] is False
    assert pred["severity_level"] == "NORMAL"
    assert pred["estimation_delay_ms"] > 0

def test_ensemble_fault_prediction():
    ensemble = TwoStageFaultDetectionEnsemble()
    # Stator winding overheating fault pattern (high temp, high current)
    telemetry = {
        "vibration_rms": 2.5,
        "vibration_peak": 3.8,
        "temperature": 96.0,
        "rpm": 1460.0,
        "current_amp": 36.5,
        "pressure_bar": 4.0,
        "acoustic_db": 72.0,
    }
    residuals = {
        "vibration_rms": 0.6,
        "vibration_peak": 0.9,
        "temperature": 34.0,
        "rpm": 15.0,
        "current_amp": 12.0,
        "pressure_bar": 0.2,
        "acoustic_db": 4.5,
    }
    pred = ensemble.predict_stream_packet(telemetry, residuals)
    assert pred["is_anomaly"] is True
    assert pred["fault_code"] > 0
    assert pred["stage2"]["invoked"] is True
    assert pred["severity_level"] in ["CRITICAL", "WARNING"]
    assert "fault_name" in pred

def test_ensemble_schema():
    ensemble = TwoStageFaultDetectionEnsemble()
    telemetry = {
        "vibration_rms": 1.9,
        "vibration_peak": 2.9,
        "temperature": 60.0,
        "rpm": 1475.0,
        "current_amp": 24.5,
        "pressure_bar": 4.15,
        "acoustic_db": 68.0,
    }
    pred = ensemble.predict_stream_packet(telemetry, {})
    expected_keys = [
        "is_anomaly", "fault_code", "fault_name", "confidence_percent",
        "stage1", "stage2", "estimation_delay_ms", "severity_level"
    ]
    for key in expected_keys:
        assert key in pred
