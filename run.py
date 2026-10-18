"""
One-Command Master Runner for IOE413 Mini Project.
Real-Time Digital Twin for Streaming-Based Anomaly Detection
Team 10 | Mohammed Sirajudheen (2023BCS0132), Rohit Pratap Singh (2023BCS0138), Amit Kumar (2023BCS0210), Kartik P (2023BCD0051)
"""

import sys
import os
import webbrowser
import threading
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def main():
    print("=" * 75)
    print("IOE413 - STREAMING & DATA ANALYTICS MINI PROJECT")
    print("Title: Real-Time Digital Twin for Streaming-Based Anomaly Detection")
    print("Team No: 10 | Mohammed Sirajudheen (2023BCS0132), Rohit Pratap Singh (2023BCS0138), Amit Kumar (2023BCS0210), Kartik P (2023BCD0051)")
    print("Base Paper: Ranpariya & Sharma (2025), Journal of Simulation")
    print("=" * 75)

    # 1. Check if model weights are present; if not, train them
    model_file = BASE_DIR / "models" / "saved" / "stage2_model.joblib"
    if not model_file.exists():
        print("\n[Step 1/2] Pretrained models not found. Running training & benchmark pipeline...")
        from models.train_models import run_training_pipeline
        run_training_pipeline()
    else:
        print("\n[Step 1/2] Pretrained models found in models/saved/.")

    # 2. Launch FastAPI Server & Live Streaming Dashboard
    print("\n[Step 2/2] Starting Real-Time Streaming Engine & Live Dashboard...")
    from config.settings import HOST, PORT
    url = f"http://{HOST}:{PORT}"
    print(f"-> Live Dashboard URL: {url}")
    print("-> Press CTRL+C to terminate the streaming server.\n")

    # Automatically open browser after 1.2 seconds
    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()

    # Start uvicorn server
    import uvicorn
    uvicorn.run("server:app", host=HOST, port=PORT, log_level="warning")

if __name__ == "__main__":
    main()
