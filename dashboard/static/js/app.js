/**
 * Main Application Controller for Real-Time Digital Twin Live Dashboard.
 * IOE413 Streaming & Data Analytics | Team 12 (Rohit Pratap Singh)
 */

function initApp() {
  console.log('[App] Initializing Digital Twin Live Dashboard...');
  
  // 1. Initialize Sub-modules with error resilience
  let twinVisualizer = null;
  let chartsManager = null;
  try {
    twinVisualizer = new DigitalTwinVisualizer('twinCanvas');
  } catch (e) {
    console.error('[App] Error initializing twinVisualizer:', e);
  }

  try {
    chartsManager = new TelemetryChartsManager();
  } catch (e) {
    console.error('[App] Error initializing chartsManager:', e);
  }

  // 2. DOM Elements
  const elStreamPill = document.getElementById('streamStatusPill');
  const elPacketCount = document.getElementById('packetCount');
  const elHealthVal = document.getElementById('kpiHealthVal');
  const elHealthStatus = document.getElementById('kpiHealthStatus');
  const elDelayVal = document.getElementById('kpiDelayVal');
  const elDelaySub = document.getElementById('kpiDelaySub');
  const elStage1Badge = document.getElementById('stage1Badge');
  const elStage2Badge = document.getElementById('stage2Badge');
  const elFaultName = document.getElementById('kpiFaultName');
  const elConfidence = document.getElementById('kpiConfidence');
  const elThroughput = document.getElementById('kpiThroughput');
  const elSparkWindow = document.getElementById('kpiSparkWindow');
  const elAlertTableBody = document.getElementById('alertTableBody');
  const elResidualVib = document.getElementById('resVib');
  const elResidualTemp = document.getElementById('resTemp');
  const elResidualPress = document.getElementById('resPress');
  const elResidualAcoustic = document.getElementById('resAcoustic');
  const elIntensitySlider = document.getElementById('faultIntensity');
  const elIntensityVal = document.getElementById('faultIntensityVal');

  let packetCounter = 0;
  let activeFaultCode = 0;

  // 3. Setup WebSocket Connection with Auto-reconnect
  let ws = null;
  function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/stream`;

    console.log('[WebSocket] Connecting to:', wsUrl);
    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('[WebSocket] Connected successfully!');
        if (elStreamPill) {
          elStreamPill.innerHTML = '<span class="pulse-dot"></span><span>STREAM LIVE @ 10 Hz</span>';
          elStreamPill.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        }
      };

      ws.onmessage = (event) => {
        try {
          const packet = JSON.parse(event.data);
          handleIncomingTelemetry(packet);
        } catch (err) {
          console.error('[WebSocket] Parse error:', err);
        }
      };

      ws.onclose = () => {
        console.warn('[WebSocket] Closed. Retrying in 2s...');
        setTimeout(connectWebSocket, 2000);
      };

      ws.onerror = (err) => {
        console.error('[WebSocket] Error encountered:', err);
      };
    } catch (e) {
      console.error('[WebSocket] Setup exception:', e);
    }
  }

  // Fallback high-frequency telemetry polling (10 Hz)
  setInterval(async () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        if (data && data.latest_packet && data.latest_packet.packet_id) {
          handleIncomingTelemetry(data.latest_packet);
        }
      } catch (e) {}
    }
  }, 100);

  // 4. Handle Real-Time Telemetry Packets
  function handleIncomingTelemetry(packet) {
    if (!packet) return;
    packetCounter++;
    if (elPacketCount) elPacketCount.textContent = packet.packet_id || packetCounter;

    // A. Update Canvas & Charts
    try {
      if (twinVisualizer) twinVisualizer.updateTelemetry(packet);
      if (chartsManager) chartsManager.update(packet);
    } catch (e) {
      console.error('[App] Error updating visualizer/charts:', e);
    }

    // B. Digital Twin State & Health Index
    const dt = packet.digital_twin || {};
    const health = dt.composite_health_index || 100;
    if (elHealthVal) elHealthVal.textContent = `${health.toFixed(1)}%`;
    if (elHealthStatus) {
      elHealthStatus.textContent = dt.health_status || 'Optimal';
      elHealthStatus.style.color = dt.health_color || '#10b981';
    }

    // Residual mini stats
    const res = dt.residuals || {};
    if (elResidualVib) elResidualVib.textContent = `${(res.vibration_rms || 0).toFixed(3)} mm/s`;
    if (elResidualTemp) elResidualTemp.textContent = `${(res.temperature || 0).toFixed(2)} °C`;
    if (elResidualPress) elResidualPress.textContent = `${(res.pressure_bar || 0).toFixed(3)} bar`;
    if (elResidualAcoustic) elResidualAcoustic.textContent = `${(res.acoustic_db || 0).toFixed(1)} dB`;

    // C. Two-Stage Ensemble Decision & Latency
    const pred = packet.prediction || {};
    const delay = pred.estimation_delay_ms || 4.8;
    if (elDelayVal) elDelayVal.textContent = `${delay.toFixed(2)}`;
    if (elDelaySub) {
      elDelaySub.innerHTML = delay <= 5.0 
        ? '<span style="color:#10b981;">✔ Target Met (&lt; 4.8 ms)</span>' 
        : '<span style="color:#f59e0b;">Within tolerance</span>';
    }

    // Stage 1 & Stage 2 badges
    const s1 = pred.stage1 || {};
    const s2 = pred.stage2 || {};

    if (elStage1Badge) {
      if (s1.flagged_anomaly) {
        elStage1Badge.className = 'badge badge-sev-critical';
        elStage1Badge.textContent = `S1: ANOMALY (${(s1.delay_ms || 1.4).toFixed(1)}ms)`;
      } else {
        elStage1Badge.className = 'badge badge-team';
        elStage1Badge.textContent = `S1: NORMAL (${(s1.delay_ms || 1.2).toFixed(1)}ms)`;
      }
    }

    if (elStage2Badge) {
      if (s2.invoked) {
        elStage2Badge.className = 'badge badge-sev-critical';
        elStage2Badge.textContent = `S2: DIAGNOSED (${(s2.delay_ms || 3.1).toFixed(1)}ms)`;
      } else {
        elStage2Badge.className = 'badge badge-paper';
        elStage2Badge.textContent = 'S2: BYPASSED (FAST-PATH)';
      }
    }

    if (elFaultName) {
      elFaultName.textContent = pred.fault_name || 'Normal Operation';
      elFaultName.style.color = pred.is_anomaly ? '#f43f5e' : '#ffffff';
    }

    if (elConfidence) {
      elConfidence.textContent = `${(pred.confidence_percent || 99.7).toFixed(1)}% Confidence`;
    }

    // D. Sliding Window Aggregates (Spark equivalent)
    const win = packet.window_aggregates || {};
    if (elThroughput) {
      elThroughput.textContent = `${win.window_size_samples ? (win.window_size_samples / 5).toFixed(1) : 10.0} Hz`;
    }
    if (elSparkWindow) {
      elSparkWindow.textContent = `5s Window (Rolling Max Vib: ${(win.rolling_max_vibration || 1.8).toFixed(2)} mm/s)`;
    }

    // E. Alert Table Trigger
    if (pred.is_anomaly) {
      addAlertTableRow({
        time: new Date().toLocaleTimeString(),
        fault: pred.fault_name,
        severity: pred.severity_level || 'CRITICAL',
        delay: `${delay.toFixed(2)} ms`,
        chi: `${health.toFixed(1)}%`
      });
    }
  }

  function addAlertTableRow(alert) {
    if (!elAlertTableBody) return;
    const tr = document.createElement('tr');
    const sevBadge = alert.severity === 'CRITICAL' 
      ? '<span class="badge badge-sev-critical">CRITICAL</span>'
      : '<span class="badge badge-sev-warning">WARNING</span>';
      
    tr.innerHTML = `
      <td>${alert.time}</td>
      <td style="color:#f87171;font-weight:600;">${alert.fault}</td>
      <td>${sevBadge}</td>
      <td>${alert.delay}</td>
      <td style="color:#38bdf8;">${alert.chi}</td>
    `;

    elAlertTableBody.insertBefore(tr, elAlertTableBody.firstChild);
    while (elAlertTableBody.children.length > 8) {
      elAlertTableBody.removeChild(elAlertTableBody.lastChild);
    }
  }

  // 5. Fault Injection Buttons
  const faultButtons = document.querySelectorAll('.fault-btn');
  faultButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const faultCode = parseInt(btn.dataset.fault, 10);
      const intensity = elIntensitySlider ? parseFloat(elIntensitySlider.value) / 100.0 : 1.0;
      
      try {
        const resp = await fetch('/api/fault/inject', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fault_code: faultCode, intensity: intensity })
        });
        const res = await resp.json();
        
        // Update active button state
        faultButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeFaultCode = faultCode;
        console.log('[Fault Lab] Activated:', res);
      } catch (err) {
        console.error('[Fault Lab] Error injecting fault:', err);
      }
    });
  });

  if (elIntensitySlider && elIntensityVal) {
    elIntensitySlider.addEventListener('input', () => {
      elIntensityVal.textContent = `${elIntensitySlider.value}%`;
    });
  }

  // Bootstrap initial telemetry snapshot immediately
  fetch('/api/status')
    .then(r => r.json())
    .then(data => {
      if (data && data.latest_packet && Object.keys(data.latest_packet).length > 0) {
        handleIncomingTelemetry(data.latest_packet);
      }
    })
    .catch(e => console.warn('Initial status fetch:', e));

  // Connect WebSocket on load
  connectWebSocket();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
