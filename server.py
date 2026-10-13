"""
FastAPI Server and Real-Time WebSocket Telemetry Gateway.
IOE413 Streaming & Data Analytics | Mini Project Team 12 (Mohammed Sirajudheen)
"""

import asyncio
import json
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from config.settings import STATIC_DIR, TEMPLATES_DIR, DATA_DIR, HOST, PORT
from streaming.stream_engine import RealTimeStreamingEngine

# Initialize the global Streaming Engine
stream_engine = RealTimeStreamingEngine(interval_sec=0.1)

class FaultInjectionRequest(BaseModel):
    fault_code: int
    intensity: float = 1.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start streaming background task
    streaming_task = asyncio.create_task(stream_engine.run_loop())
    print(f"[Server] Real-Time Streaming Engine started on http://{HOST}:{PORT}")
    yield
    # Shutdown
    stream_engine.stop()
    streaming_task.cancel()
    print("[Server] Streaming engine stopped.")

app = FastAPI(
    title="IOE413 Real-Time Digital Twin Anomaly Detection",
    description="Digital Twin and Two-Stage ML Ensemble for Streaming Anomaly Detection (Ranpariya & Sharma 2025)",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serves the main interactive dashboard."""
    index_file = TEMPLATES_DIR / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    """Real-time bi-directional telemetry stream."""
    await websocket.accept()
    # Send recent historical packets immediately so charts populate instantly
    for p in list(stream_engine.recent_buffer)[-30:]:
        try:
            await websocket.send_json(p)
        except Exception:
            break
            
    stream_engine.register_client(websocket)
    try:
        while True:
            await asyncio.sleep(0.5)
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        stream_engine.unregister_client(websocket)

@app.post("/api/fault/inject")
async def inject_fault_endpoint(req: FaultInjectionRequest):
    """Injects a specific fault scenario into the live stream."""
    stream_engine.inject_fault(req.fault_code, req.intensity)
    return {
        "status": "success",
        "fault_code": req.fault_code,
        "intensity": req.intensity,
        "message": f"Injected fault {req.fault_code} at {req.intensity * 100}% intensity"
    }

@app.post("/api/fault/reset")
async def reset_fault_endpoint():
    """Resets the simulator to normal operation."""
    stream_engine.reset_fault()
    return {"status": "success", "message": "Restored normal operating conditions"}

@app.get("/api/benchmark")
async def get_benchmark_results():
    """Returns comparative model benchmark metrics."""
    benchmark_file = DATA_DIR / "model_benchmark_results.json"
    if benchmark_file.exists():
        with open(benchmark_file, "r") as f:
            return json.load(f)
    return {"status": "pending", "message": "Run train_models.py or evaluation/benchmark.py to generate benchmarks"}

@app.get("/api/status")
async def get_system_status():
    """Returns current live snapshot."""
    return {
        "asset_id": stream_engine.digital_twin.asset_id,
        "packet_counter": stream_engine.packet_counter,
        "health_index": stream_engine.digital_twin.health_index,
        "active_subscribers": len(stream_engine.subscribers),
        "latest_packet": stream_engine.last_packet
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=HOST, port=PORT, reload=False)
