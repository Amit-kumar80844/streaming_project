/**
 * Digital Twin Canvas Visualizer for Industrial Motor-Pump Asset (TWIN-MTR-01).
 * High-performance 2D/isometric interactive canvas rendering with dynamic physics feedback:
 * - Rotor rotation speed dynamically driven by live telemetry RPM.
 * - Stator thermal gradient rendering based on core temperature.
 * - Bearing housing vibration displacement and harmonic pulse rings.
 * - Fluid pressure turbulence visualization in pump volute.
 */

// Safe polyfill for CanvasRenderingContext2D.roundRect if not present
if (typeof CanvasRenderingContext2D !== 'undefined' && !CanvasRenderingContext2D.prototype.roundRect) {
  CanvasRenderingContext2D.prototype.roundRect = function(x, y, w, h, r = 0) {
    const radius = typeof r === 'number' ? r : 4;
    this.rect(x, y, w, h);
    return this;
  };
}

class DigitalTwinVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    // Physics & state variables
    this.rotationAngle = 0;
    this.rpm = 1480;
    this.temperature = 58;
    this.vibRms = 1.6;
    this.vibPeak = 2.4;
    this.pressure = 4.2;
    this.healthIndex = 100;
    this.isAnomaly = false;
    this.faultCode = 0;
    
    // Resize handling
    this.resize();
    window.addEventListener('resize', () => this.resize());
    
    // Start animation loop
    this.lastFrameTime = performance.now();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height;
  }

  updateTelemetry(packet) {
    const raw = packet.raw_telemetry || {};
    const dt = packet.digital_twin || {};
    const pred = packet.prediction || {};
    
    this.rpm = raw.rpm || 1480;
    this.temperature = raw.temperature || 58;
    this.vibRms = raw.vibration_rms || 1.6;
    this.vibPeak = raw.vibration_peak || 2.4;
    this.pressure = raw.pressure_bar || 4.2;
    this.healthIndex = dt.composite_health_index || 100;
    this.isAnomaly = pred.is_anomaly || false;
    this.faultCode = pred.fault_code || 0;
  }

  animate(currentTime) {
    const dt = (currentTime - this.lastFrameTime) / 1000.0;
    this.lastFrameTime = currentTime;
    
    // Increment rotation based on live RPM (scaled for visual aesthetics)
    const angularSpeed = (this.rpm / 60.0) * 2 * Math.PI * 0.15;
    this.rotationAngle += angularSpeed * dt;
    
    this.render();
    requestAnimationFrame(this.animate);
  }

  render() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    ctx.clearRect(0, 0, w, h);

    // Subtle background grid
    this.drawGrid(ctx, w, h);

    const centerX = w * 0.46;
    const centerY = h * 0.52;
    
    // Overall Asset Health Glow
    this.drawAssetGlow(ctx, centerX, centerY);

    // Vibration jitter offset if vibration is high
    let jitterX = 0;
    let jitterY = 0;
    if (this.vibRms > 3.0) {
      const jitterMagnitude = Math.min(10, (this.vibRms - 2.5) * 1.5);
      jitterX = (Math.random() - 0.5) * jitterMagnitude;
      jitterY = (Math.random() - 0.5) * jitterMagnitude;
    }

    ctx.save();
    ctx.translate(centerX + jitterX, centerY + jitterY);

    // 1. Foundation Base Mount
    this.drawBasePlate(ctx);

    // 2. Motor Stator Casing with Thermal Heat Map
    this.drawMotorStator(ctx);

    // 3. Central Rotating Rotor Shaft & Coupling
    this.drawRotatingShaft(ctx);

    // 4. Drive & Non-Drive End Bearing Housings with Vibration Waves
    this.drawBearings(ctx);

    // 5. Centrifugal Pump Volute & Impeller
    this.drawPumpVolute(ctx);

    // 6. Sensor Probe Overlays & Telemetry Labels
    this.drawSensorProbes(ctx);

    ctx.restore();
  }

  drawGrid(ctx, w, h) {
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.04)';
    ctx.lineWidth = 1;
    const step = 24;
    for (let x = 0; x < w; x += step) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += step) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }
  }

  drawAssetGlow(ctx, cx, cy) {
    let glowColor = 'rgba(16, 185, 129, 0.12)';
    if (this.healthIndex < 60 || this.isAnomaly) {
      glowColor = 'rgba(244, 63, 94, 0.22)';
    } else if (this.healthIndex < 85) {
      glowColor = 'rgba(245, 158, 11, 0.18)';
    }

    const radGrad = ctx.createRadialGradient(cx, cy, 30, cx, cy, 220);
    radGrad.addColorStop(0, glowColor);
    radGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = radGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, 220, 0, Math.PI * 2);
    ctx.fill();
  }

  drawBasePlate(ctx) {
    // Heavy steel cast bedplate
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 2;
    
    ctx.beginPath();
    ctx.roundRect(-220, 75, 420, 26, 6);
    ctx.fill();
    ctx.stroke();

    // Fastener bolts
    ctx.fillStyle = '#64748b';
    [-190, -110, 20, 110, 170].forEach(bx => {
      ctx.beginPath();
      ctx.arc(bx, 88, 4, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  drawMotorStator(ctx) {
    // Dynamic color gradient based on temperature (50C = Cyan/Blue, 90C+ = Hot Red)
    const tNorm = Math.max(0, Math.min(1, (this.temperature - 50) / 45));
    let r = Math.round(14 + tNorm * 220);
    let g = Math.round(116 - tNorm * 80);
    let b = Math.round(144 - tNorm * 110);
    
    // Stator Body Cylinder
    const statorGrad = ctx.createLinearGradient(-190, -60, -190, 70);
    statorGrad.addColorStop(0, `rgb(${r+15}, ${g+15}, ${b+15})`);
    statorGrad.addColorStop(0.5, `rgb(${r}, ${g}, ${b})`);
    statorGrad.addColorStop(1, `rgb(${Math.max(0, r-30)}, ${Math.max(0, g-30)}, ${Math.max(0, b-30)})`);

    ctx.fillStyle = statorGrad;
    ctx.strokeStyle = this.isAnomaly && this.faultCode === 2 ? '#f43f5e' : '#38bdf8';
    ctx.lineWidth = 2;
    
    ctx.beginPath();
    ctx.roundRect(-190, -55, 175, 125, 8);
    ctx.fill();
    ctx.stroke();

    // Stator cooling ribs
    ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
    for (let rx = -180; rx < -25; rx += 16) {
      ctx.fillRect(rx, -55, 6, 125);
    }

    // Terminal Box on top
    ctx.fillStyle = '#334155';
    ctx.strokeStyle = '#475569';
    ctx.beginPath();
    ctx.roundRect(-135, -78, 65, 24, 4);
    ctx.fill();
    ctx.stroke();

    // Terminal wire glow
    ctx.fillStyle = '#38bdf8';
    ctx.fillRect(-110, -74, 15, 6);
  }

  drawRotatingShaft(ctx) {
    // Main drive shaft
    ctx.fillStyle = '#94a3b8';
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1;
    ctx.fillRect(-210, 0, 310, 16);

    // Dynamic rotation stripes on shaft to show RPM spinning
    ctx.save();
    ctx.clip(new Path2D(`M-210,0 h310 v16 h-310 Z`));
    const stripeOffset = (this.rotationAngle * 25) % 24;
    ctx.fillStyle = '#475569';
    for (let sx = -220 + stripeOffset; sx < 110; sx += 24) {
      ctx.fillRect(sx, 0, 10, 16);
    }
    ctx.restore();

    // Flexible Coupling between motor and pump
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#64748b';
    ctx.beginPath();
    ctx.roundRect(-10, -8, 24, 32, 4);
    ctx.fill();
    ctx.stroke();
  }

  drawBearings(ctx) {
    // Bearing locations: Non-Drive End (-195) and Drive End (-20)
    const bearingX = [-195, -25];
    
    bearingX.forEach((bx, idx) => {
      // Bearing housing
      ctx.fillStyle = '#334155';
      ctx.strokeStyle = (this.faultCode === 1 && this.isAnomaly) ? '#f43f5e' : '#64748b';
      ctx.lineWidth = (this.faultCode === 1 && this.isAnomaly) ? 3 : 1.5;
      
      ctx.beginPath();
      ctx.roundRect(bx, -18, 16, 52, 4);
      ctx.fill();
      ctx.stroke();

      // Bearing Defect Vibration Wave Rings
      if (this.faultCode === 1 || this.vibPeak > 4.5) {
        const pulse = (performance.now() * 0.006) % 1;
        ctx.strokeStyle = `rgba(244, 63, 94, ${1 - pulse})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(bx + 8, 8, 16 + pulse * 28, 0, Math.PI * 2);
        ctx.stroke();
      }
    });
  }

  drawPumpVolute(ctx) {
    // Centrifugal Pump Spiral Volute Housing
    const pumpGrad = ctx.createRadialGradient(75, 8, 10, 75, 8, 65);
    pumpGrad.addColorStop(0, '#0f172a');
    pumpGrad.addColorStop(1, '#1e293b');

    ctx.fillStyle = pumpGrad;
    ctx.strokeStyle = (this.faultCode === 4 && this.isAnomaly) ? '#f43f5e' : '#38bdf8';
    ctx.lineWidth = 2.5;

    // Pump spiral casing
    ctx.beginPath();
    ctx.arc(75, 8, 55, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Pump Discharge Flange (vertical outlet)
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(60, -85, 30, 40);
    ctx.strokeRect(55, -92, 40, 10);

    // Fluid flow waves in discharge pipe
    const flowOffset = (performance.now() * 0.05) % 15;
    ctx.strokeStyle = (this.faultCode === 4) ? '#f59e0b' : '#06b6d4';
    ctx.lineWidth = 2;
    for (let fy = -80 + flowOffset; fy < -50; fy += 12) {
      ctx.beginPath();
      ctx.moveTo(68, fy);
      ctx.lineTo(82, fy);
      ctx.stroke();
    }

    // Rotating Impeller Blades inside pump
    ctx.save();
    ctx.translate(75, 8);
    ctx.rotate(this.rotationAngle);
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 3;
    for (let i = 0; i < 4; i++) {
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.quadraticCurveTo(15, 12, 38, 0);
      ctx.stroke();
      ctx.rotate(Math.PI / 2);
    }
    // Impeller central eye hub
    ctx.fillStyle = '#64748b';
    ctx.beginPath();
    ctx.arc(0, 0, 9, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  drawSensorProbes(ctx) {
    // 1. Stator Temp Sensor
    ctx.fillStyle = '#06b6d4';
    ctx.beginPath();
    ctx.arc(-100, -56, 4, 0, Math.PI * 2);
    ctx.fill();
    
    // 2. Drive Bearing Accelerometer
    ctx.fillStyle = '#a855f7';
    ctx.beginPath();
    ctx.arc(-17, -20, 4, 0, Math.PI * 2);
    ctx.fill();

    // 3. Discharge Pressure Transducer
    ctx.fillStyle = '#10b981';
    ctx.beginPath();
    ctx.arc(75, -92, 4, 0, Math.PI * 2);
    ctx.fill();
  }
}

window.DigitalTwinVisualizer = DigitalTwinVisualizer;
