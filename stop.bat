@echo off
REM ===================================================================
REM  Digital Twin Operations Console — Windows Shutdown Launcher
REM  Double-click this file to stop the full stack.
REM ===================================================================

title Digital Twin — Shutdown

echo.
echo  ============================================================
echo   IOE413 Real-Time Digital Twin Anomaly Detection
echo   Stopping Docker Containers...
echo  ============================================================
echo.

docker compose down

if %errorlevel% neq 0 (
    echo.
    echo  [WARN] Docker Compose down encountered an issue or Docker is not running.
    echo.
) else (
    echo.
    echo  [OK] Digital Twin stack stopped successfully.
    echo.
)

pause
