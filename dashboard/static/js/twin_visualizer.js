/**
 * Digital Twin Motor/Pump Visualizer
 * Draws the asset using Canvas; animation driven by actual telemetry state.
 * IOE413 Team 12
 */

class DigitalTwinVisualizer {
  constructor(canvasId) {
    this.canvas  = document.getElementById(canvasId);
    if (!this.canvas) throw new Error(`Canvas #${canvasId} not found`);
    this.ctx     = this.canvas.getContext('2d');
    this._state  = {
      rpm: 1480,
      health: 100,
      temperature: 62,
      vibration: 1.8,
      faultCode: 0,
      isAnomaly: false,
      severity: 'NORMAL',
    };
    this._angle  = 0;
    this._rafId  = null;
    this._resize();
    window.addEventListener('resize', () => this._resize());
    this._loop();
  }

  updateTelemetry(packet) {
    const rt  = packet.raw_telemetry || {};
    const dt  = packet.digital_twin  || {};
    const pred = packet.prediction   || {};
    this._state.rpm        = rt.rpm         ?? this._state.rpm;
    this._state.health     = dt.composite_health_index ?? this._state.health;
    this._state.temperature = rt.temperature ?? this._state.temperature;
    this._state.vibration  = rt.vibration_rms ?? this._state.vibration;
    this._state.faultCode  = pred.fault_code  ?? 0;
    this._state.isAnomaly  = !!pred.is_anomaly;
    this._state.severity   = pred.severity_level || 'NORMAL';
  }

  _resize() {
    const wrap = this.canvas.parentElement;
    const dpr  = window.devicePixelRatio || 1;
    const w    = wrap ? wrap.clientWidth  : 400;
    const h    = wrap ? wrap.clientHeight : 240;
    this.canvas.width  = w * dpr;
    this.canvas.height = h * dpr;
    this.canvas.style.width  = w + 'px';
    this.canvas.style.height = h + 'px';
    this.ctx.scale(dpr, dpr);
    this._w = w;
    this._h = h;
  }

  _loop() {
    this._rafId = requestAnimationFrame(() => this._loop());
    const rpm = Math.max(100, this._state.rpm);
    // Angular velocity proportional to RPM; vibration adds jitter
    const vibJitter = this._state.isAnomaly ? (Math.random() - 0.5) * 0.04 * this._state.vibration : 0;
    this._angle += (rpm / 60 / 60) + vibJitter; // ~degrees per frame at 60fps
    this._draw();
  }

  _draw() {
    const { ctx } = this;
    const w = this._w, h = this._h;
    const cx = w * 0.42, cy = h * 0.5;
    const R  = Math.min(w, h) * 0.28;

    ctx.clearRect(0, 0, w, h);

    // --- Health colour ---
    const health = this._state.health;
    const healthColor = health >= 85 ? '#4ADE80' : health >= 60 ? '#FBBF24' : '#F87171';

    // --- Stator housing (outer ring - dark metallic graphite) ---
    ctx.save();
    const statorGrad = ctx.createRadialGradient(cx, cy, R * 0.7, cx, cy, R * 1.05);
    statorGrad.addColorStop(0, '#1E293B');
    statorGrad.addColorStop(1, '#0F172A');
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.fillStyle = statorGrad;
    ctx.fill();
    ctx.strokeStyle = healthColor + '66';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();

    // --- Stator windings (industrial copper & steel tones) ---
    ctx.save();
    const windingColors = ['#C27838', '#94A3B8', '#D97706', '#64748B', '#B45309', '#748196'];
    for (let i = 0; i < 6; i++) {
      const angle = (i / 6) * Math.PI * 2;
      const x1 = cx + Math.cos(angle) * R * 0.62;
      const y1 = cy + Math.sin(angle) * R * 0.62;
      const x2 = cx + Math.cos(angle) * R * 0.88;
      const y2 = cy + Math.sin(angle) * R * 0.88;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = windingColors[i] + '90';
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Winding coil arc
      ctx.beginPath();
      ctx.arc(x2, y2, R * 0.08, angle - 0.7, angle + 0.7);
      ctx.strokeStyle = windingColors[i] + '60';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
    ctx.restore();

    // --- Rotor (rotates with real RPM) ---
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this._angle * Math.PI / 180);

    const rotorGrad = ctx.createRadialGradient(0, 0, R * 0.05, 0, 0, R * 0.52);
    rotorGrad.addColorStop(0, '#263342');
    rotorGrad.addColorStop(1, '#141B24');
    ctx.beginPath();
    ctx.arc(0, 0, R * 0.52, 0, Math.PI * 2);
    ctx.fillStyle = rotorGrad;
    ctx.fill();
    ctx.strokeStyle = '#273240';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Rotor bars
    const barColor = this._state.faultCode === 3 ? '#FBBF24' : (this._state.isAnomaly ? '#F87171' : '#38BDF8');
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * R * 0.18, Math.sin(a) * R * 0.18);
      ctx.lineTo(Math.cos(a) * R * 0.46, Math.sin(a) * R * 0.46);
      ctx.strokeStyle = barColor + (this._state.isAnomaly ? 'CC' : '70');
      ctx.lineWidth = this._state.faultCode === 3 ? 3 : 1.5; // thicker if rotor imbalance
      ctx.stroke();
    }

    // Shaft center
    const shaftGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, R * 0.12);
    shaftGrad.addColorStop(0, '#475569');
    shaftGrad.addColorStop(1, '#1E293B');
    ctx.beginPath();
    ctx.arc(0, 0, R * 0.12, 0, Math.PI * 2);
    ctx.fillStyle = shaftGrad;
    ctx.fill();
    ctx.strokeStyle = '#64748B';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.restore();

    // --- Health glow overlay (restrained, only during anomaly) ---
    if (this._state.isAnomaly) {
      const t = Date.now() / 600;
      const glow = Math.abs(Math.sin(t)) * 0.25 + 0.05;
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, R * 1.02, 0, Math.PI * 2);
      ctx.strokeStyle = healthColor;
      ctx.lineWidth = 2.5;
      ctx.globalAlpha = glow;
      ctx.stroke();
      ctx.restore();
    }

    // --- Pump volute (right side) ---
    const pumpX = cx + R * 1.35, pumpY = cy;
    const pumpR = R * 0.38;
    ctx.save();
    const pumpGrad = ctx.createRadialGradient(pumpX, pumpY, pumpR * 0.3, pumpX, pumpY, pumpR);
    pumpGrad.addColorStop(0, '#1E293B');
    pumpGrad.addColorStop(1, '#0F172A');
    ctx.beginPath();
    ctx.ellipse(pumpX, pumpY, pumpR, pumpR * 0.9, 0, 0, Math.PI * 2);
    ctx.fillStyle = pumpGrad;
    ctx.fill();
    const pumpBorderColor = this._state.faultCode === 4 ? '#F87171' : (this._state.isAnomaly ? '#FB923C' : '#2DD4BF');
    ctx.strokeStyle = pumpBorderColor + '70';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Pump impeller
    ctx.save();
    ctx.translate(pumpX, pumpY);
    ctx.rotate(-(this._angle * 0.85) * Math.PI / 180);
    const impellerColor = this._state.faultCode === 4 ? '#F87171' : '#2DD4BF';
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.bezierCurveTo(
        Math.cos(a) * pumpR * 0.25, Math.sin(a) * pumpR * 0.25,
        Math.cos(a + 0.6) * pumpR * 0.55, Math.sin(a + 0.6) * pumpR * 0.55,
        Math.cos(a + 0.9) * pumpR * 0.5, Math.sin(a + 0.9) * pumpR * 0.5
      );
      ctx.strokeStyle = impellerColor + '99';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
    ctx.restore();

    // Coupling shaft
    ctx.beginPath();
    ctx.moveTo(cx + R, pumpY - 4);
    ctx.lineTo(pumpX - pumpR, pumpY - 4);
    ctx.lineTo(pumpX - pumpR, pumpY + 4);
    ctx.lineTo(cx + R, pumpY + 4);
    ctx.closePath();
    ctx.fillStyle = '#1E293B';
    ctx.fill();
    ctx.strokeStyle = '#273240';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();

    // --- Temperature indicator (thermal shading if high temp) ---
    if (this._state.temperature > 75) {
      const heat = Math.min(1, (this._state.temperature - 75) / 20);
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, R * 1.01, 0, Math.PI * 2);
      ctx.fillStyle = this._state.temperature > 85 ? `rgba(248,113,113,${heat * 0.15})` : `rgba(251,191,36,${heat * 0.12})`;
      ctx.fill();
      ctx.restore();
    }

    // --- Discharge pipe arrow ---
    const pipeX = pumpX + pumpR;
    const pipeColor = this._state.faultCode === 4 ? '#F87171' : '#2DD4BF';
    ctx.save();
    ctx.strokeStyle = pipeColor + 'AA';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(pipeX, pumpY);
    ctx.lineTo(pipeX + 32, pumpY);
    ctx.stroke();
    // Arrow head
    ctx.fillStyle = pipeColor;
    ctx.beginPath();
    ctx.moveTo(pipeX + 38, pumpY);
    ctx.lineTo(pipeX + 28, pumpY - 6);
    ctx.lineTo(pipeX + 28, pumpY + 6);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // --- RPM text ---
    ctx.save();
    ctx.font = `bold ${Math.max(11, R * 0.22)}px JetBrains Mono, monospace`;
    ctx.textAlign = 'center';
    ctx.fillStyle = '#F1F5F9';
    ctx.fillText(`${Math.round(this._state.rpm)}`, cx, cy + R * 0.06);
    ctx.font = `${Math.max(9, R * 0.16)}px Inter, sans-serif`;
    ctx.fillStyle = '#748196';
    ctx.fillText('RPM', cx, cy + R * 0.22);
    ctx.restore();

    // --- Simulated label watermark ---
    ctx.save();
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillStyle = 'rgba(116, 129, 150, 0.4)';
    ctx.fillText('DIGITAL TWIN SIMULATION', w - 10, h - 10);
    ctx.restore();
  }
}
