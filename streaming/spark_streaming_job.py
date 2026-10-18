"""
Spark Structured Streaming Job for Real-Time IIoT Telemetry Anomaly Detection.
IOE413 Streaming & Data Analytics | Mini Project Team 10 — Mohammed Sirajudheen (2023BCS0132), Rohit Pratap Singh (2023BCS0138), Amit Kumar (2023BCS0210), Kartik P (2023BCD0051)

Ingests continuous sensor telemetry from Apache Kafka,
applies watermarking and sliding window aggregations,
and runs real-time condition monitoring.
"""

import os

def create_spark_streaming_pipeline():
    """Builds and starts the PySpark Structured Streaming pipeline."""
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import from_json, col, to_timestamp, window, avg, max as spark_max, count, when
        from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
    except ImportError:
        print("[Spark Job] PySpark is not installed or available in this environment.")
        return

    print("=" * 70)
    print("STARTING SPARK STRUCTURED STREAMING ENGINE")
    print("Source: Kafka (topic: iiot-sensor-stream) | Window: 5s, Slide: 1s")
    print("=" * 70)

    # 1. Initialize Spark Session with Kafka connector packages
    spark = SparkSession.builder \
        .appName("IIoT-DigitalTwin-StreamingAnomalyDetection") \
        .master(os.getenv("SPARK_MASTER", "local[*]")) \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # 2. Define Schema for incoming IIoT sensor telemetry JSON
    schema = StructType([
        StructField("timestamp", DoubleType(), True),
        StructField("step", IntegerType(), True),
        StructField("asset_id", StringType(), True),
        StructField("vibration_rms", DoubleType(), True),
        StructField("vibration_peak", DoubleType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("rpm", DoubleType(), True),
        StructField("current_amp", DoubleType(), True),
        StructField("pressure_bar", DoubleType(), True),
        StructField("acoustic_db", DoubleType(), True),
        StructField("fault_label", IntegerType(), True),
        StructField("fault_name", StringType(), True),
        StructField("is_anomaly", IntegerType(), True)
    ])

    # 3. Read Stream from Kafka topic
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
    
    try:
        raw_stream = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_servers) \
            .option("subscribe", "iiot-sensor-stream") \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()

        # 4. Deserialize JSON and extract fields
        parsed_stream = raw_stream \
            .selectExpr("CAST(value AS STRING) as json_payload") \
            .select(from_json(col("json_payload"), schema).alias("data")) \
            .select("data.*") \
            .withColumn("event_time", to_timestamp(col("timestamp").cast("timestamp")))

        # 5. Apply Watermarking and Sliding Window Aggregations
        windowed_analytics = parsed_stream \
            .withWatermark("event_time", "10 seconds") \
            .groupBy(
                window(col("event_time"), "5 seconds", "1 second"),
                col("asset_id")
            ) \
            .agg(
                avg("vibration_rms").alias("avg_vibration_rms"),
                spark_max("vibration_peak").alias("peak_vibration"),
                avg("temperature").alias("avg_temperature"),
                avg("current_amp").alias("avg_current"),
                avg("pressure_bar").alias("avg_pressure"),
                avg("acoustic_db").alias("avg_acoustic"),
                count("*").alias("window_packet_count")
            ) \
            .withColumn(
                "streaming_health_flag",
                when(col("avg_vibration_rms") > 4.5, "HIGH_VIBRATION_ANOMALY")
                .when(col("avg_temperature") > 85.0, "THERMAL_OVERHEAT_ANOMALY")
                .when(col("avg_pressure") < 2.5, "HYDRAULIC_PRESSURE_DROP")
                .otherwise("NORMAL_OPERATION")
            )

        # 6. Stream Sink to Console for Real-Time Streaming Monitoring
        query = windowed_analytics.writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", "false") \
            .start()

        print("[Spark Job] Stream query initialized and waiting for data...")
        query.awaitTermination()

    except Exception as e:
        print(f"[Spark Job Error] Could not connect to Kafka stream: {e}")
        raise

if __name__ == "__main__":
    create_spark_streaming_pipeline()
