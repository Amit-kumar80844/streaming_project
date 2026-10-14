"""
Kafka Consumer for IIoT Sensor Stream.
Consumes continuous sensor data from Kafka and pipes into Digital Twin & ML Pipeline.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Callable, Optional

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from config.settings import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_TELEMETRY
from models.digital_twin import IndustrialDigitalTwin
from models.two_stage_ensemble import TwoStageFaultDetectionEnsemble

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KafkaConsumer")

class IIoTKafkaConsumer:
    """Consumes real-time stream from Kafka topic and runs Digital Twin processing."""
    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS, topic: str = KAFKA_TOPIC_TELEMETRY):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.digital_twin = IndustrialDigitalTwin()
        self.ensemble = TwoStageFaultDetectionEnsemble()
        self.is_running = False

    def start_consuming(self, message_callback: Optional[Callable] = None):
        """Starts real-time consumption loop."""
        try:
            from kafka import KafkaConsumer
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="iiot-digital-twin-cg",
                consumer_timeout_ms=5000
            )
            logger.info(f"Subscribed to topic '{self.topic}' at {self.bootstrap_servers}")
            self.is_running = True
            
            for msg in consumer:
                if not self.is_running:
                    break
                telemetry = msg.value
                
                # 1. Digital Twin state synchronization & residual calculation
                twin_state = self.digital_twin.process_telemetry(telemetry)
                
                # 2. Two-Stage ML Ensemble Fault Prediction
                prediction = self.ensemble.predict_stream_packet(telemetry, twin_state["residuals"])
                
                processed_packet = {
                    "raw_telemetry": telemetry,
                    "digital_twin": twin_state,
                    "prediction": prediction
                }
                
                if message_callback:
                    message_callback(processed_packet)
                else:
                    logger.info(f"[Consumer] Anomaly: {prediction['is_anomaly']} | Fault: {prediction['fault_name']} | Delay: {prediction['estimation_delay_ms']}ms | CHI: {twin_state['composite_health_index']}%")
                    
        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")

    def stop(self):
        self.is_running = False

if __name__ == "__main__":
    consumer = IIoTKafkaConsumer()
    consumer.start_consuming()
