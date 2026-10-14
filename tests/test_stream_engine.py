"""
Tests for RealTimeStreamingEngine streaming coordinator.
"""

import pytest
import asyncio
from streaming.stream_engine import RealTimeStreamingEngine

def test_stream_engine_step():
    engine = RealTimeStreamingEngine(interval_sec=0.01)
    packet = asyncio.run(engine.step())
    
    assert "packet_id" in packet
    assert packet["packet_id"] == 1
    assert "timestamp" in packet
    assert "raw_telemetry" in packet
    assert "digital_twin" in packet
    assert "prediction" in packet
    assert "window_aggregates" in packet
    assert len(engine.recent_buffer) == 1
    assert engine.last_packet == packet

def test_stream_engine_sliding_window():
    async def _run():
        engine = RealTimeStreamingEngine(interval_sec=0.01)
        for _ in range(5):
            await engine.step()
        return engine.compute_sliding_window_metrics()
    
    metrics = asyncio.run(_run())
    assert "window_size_samples" in metrics
    assert metrics["window_size_samples"] == 5
    assert "rolling_avg_vibration" in metrics
    assert "rolling_avg_temp" in metrics

def test_stream_engine_fault_injection_and_reset():
    engine = RealTimeStreamingEngine()
    engine.inject_fault(2, 0.8)
    assert engine.simulator.current_mode == 2
    assert engine.simulator.mode_intensity == 0.8
    
    engine.reset_fault()
    assert engine.simulator.current_mode == 0
    assert engine.simulator.mode_intensity == 0.0

def test_stream_engine_client_management():
    engine = RealTimeStreamingEngine()
    dummy_ws = object()
    
    engine.register_client(dummy_ws)
    assert dummy_ws in engine.subscribers
    
    engine.unregister_client(dummy_ws)
    assert dummy_ws not in engine.subscribers
