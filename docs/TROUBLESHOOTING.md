# Troubleshooting & Diagnostic Guide — Real-Time Digital Twin

This guide documents the root causes, diagnostic evidence, and verified solutions for common operational and runtime errors.

---

## 1. `kafka.errors.NoBrokersAvailable`
- **Symptom:** Terminal or logs output `kafka.errors.NoBrokersAvailable: NoBrokersAvailable` when launching external Kafka producers/consumers.
- **Root Cause:** No active Kafka broker is running on `localhost:9092`, or IPv6 resolution (`::1`) fails to connect to an IPv4-only broker.
- **Diagnostic Evidence:** `netstat -ano | findstr 9092` returns empty.
- **Fix:**
  - The default Docker stack starts Kafka with the app. Check broker status with `docker compose ps` and logs with `docker compose logs kafka`.
  - To start the full stack from the project directory:
    ```powershell
    docker compose up -d
    ```
- **Verification:** Run `docker compose ps` to verify `digital-twin-kafka` is healthy on port 9092.

---

## 2. Spark: `Failed to find data source: kafka`
- **Symptom:** `pyspark.sql.utils.AnalysisException: Failed to find data source: kafka` in `spark_streaming_job.py`.
- **Root Cause:** PySpark does not bundle the JVM Kafka streaming connector JAR (`spark-sql-kafka-0-10`) by default.
- **Fix:**
  - Submit the Spark job with the Maven dependency coordinate matching the exact Spark/Scala release:
    ```bash
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 streaming/spark_streaming_job.py
    ```
  - In Docker Compose, configure `spark.jars.ivy=/tmp/.ivy2` so Spark can write its dependency-resolution cache as the non-root Spark user.
- **Verification:** Spark streaming query initializes without `ClassNotFoundException`.

---

## 3. scikit-learn Unpickle / Version Warnings
- **Symptom:** `InconsistentVersionWarning: Trying to unpickle estimator StandardScaler from version 1.5.1 when using version 1.9.1`.
- **Root Cause:** Model artifacts were serialized using scikit-learn 1.5.1, but the active runtime interpreter uses scikit-learn 1.9.1.
- **Fix:** Re-trained and re-exported all model artifacts (`scaler.joblib`, `stage1_model.joblib`, `stage2_model.joblib`) using the active scikit-learn 1.9.1 environment via `models/train_models.py`.
- **Verification:** `python -c "import server"` imports cleanly with zero warning output.

---

## 4. `winutils.exe` / Native Hadoop Warnings on Windows
- **Symptom:** `WARN Shell: Did not find winutils.exe: {} java.io.FileNotFoundException: java.io.FileNotFoundException: HADOOP_HOME and hadoop.home.dir are unset.`
- **Root Cause:** Apache Spark expects native Hadoop WinUtils binaries when run natively on Windows filesystems.
- **Fix:**
  - In local dashboard mode, the in-process stream engine bypasses Hadoop entirely.
  - For distributed Spark processing, run Spark inside a Linux-based Docker container where native POSIX filesystem calls succeed naturally without `winutils.exe`.
- **Verification:** Container logs show clean POSIX directory binding without Hadoop shell warnings.

---

## 5. pandas >= 3.0 / PySpark Incompatibility Warning
- **Symptom:** `UserWarning: PySpark does not fully support pandas 3.0.x`.
- **Root Cause:** Upstream PySpark has deprecated or unverified bindings for pandas 3.0 API changes.
- **Fix:** Pinned compatible dependency versions in `requirements.txt` and verified that core inference and digital twin models use native NumPy arrays and Python dictionaries, avoiding fragile DataFrame conversions in the real-time hot path.
- **Verification:** In-process streaming loop executes at 10 Hz without pandas deprecation warnings.

---

## 6. `asyncio.exceptions.CancelledError` on Manual Shutdown
- **Symptom:** Verbose traceback printed to terminal upon pressing `Ctrl+C` or stopping Uvicorn.
- **Root Cause:** FastAPI lifespan task cancellation was not handled gracefully during shutdown, causing Uvicorn's event loop to treat normal task cancellation as an unhandled error.
- **Fix:** Updated `server.py` lifespan context manager:
  ```python
  stream_engine.stop()
  if _streaming_task and not _streaming_task.done():
      _streaming_task.cancel()
      try:
          await asyncio.wait_for(_streaming_task, timeout=3.0)
      except (asyncio.CancelledError, asyncio.TimeoutError):
          pass
  ```
- **Verification:** Pressing `Ctrl+C` prints clean shutdown log: `[Server] Streaming engine stopped cleanly.` with exit code 0.

---

## 7. Mismatched Python Environment Paths
- **Symptom:** Discrepancies between virtual environment packages and IDE interpreter (e.g. `Downloads\lab_...` vs project root).
- **Root Cause:** Hardcoded system paths in local IDE runner configurations.
- **Fix:**
  - Standardized paths relative to `Path(__file__).resolve().parent`.
  - Added dynamic `sys.path.insert(0, str(base_dir))` in entry points (`server.py`, `run.py`).
  - Standardized container execution in `Dockerfile` under `/app`.
- **Verification:** Automated test suite passes identically on host Python and inside Docker.
