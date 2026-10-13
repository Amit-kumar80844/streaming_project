/**
 * Lightweight, Ultra-Responsive High-DPI Streaming Charts.
 * Built with HTML5 Canvas for zero-dependency offline reliability, 60fps rendering, and neon glowing traces.
 */

class RealTimeStreamChart {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    this.maxPoints = options.maxPoints || 50;
    this.series = (options.series || []).map(s => ({
      data: [],
      ...s
    }));
    this.yMin = options.yMin !== undefined ? options.yMin : 0;
    this.yMax = options.yMax !== undefined ? options.yMax : 100;
    this.threshold = options.threshold || null;
    this.unit = options.unit || '';
    
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas || !this.canvas.parentElement) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return;
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx = this.canvas.getContext('2d');
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height;
    this.render();
  }

  pushValues(valuesMap) {
    this.series.forEach(s => {
      const v = valuesMap[s.name];
      if (v !== undefined) {
        s.data.push(v);
        if (s.data.length > this.maxPoints) {
          s.data.shift();
        }
      }
    });
    this.render();
  }

  render() {
    if (!this.canvas) return;
    if (!this.width || this.width <= 0) {
      this.resize();
      return;
    }
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    
    ctx.clearRect(0, 0, w, h);
    
    // Draw subtle horizontal gridlines & labels
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.fillStyle = '#64748b';
    ctx.font = '9px "JetBrains Mono", monospace';
    ctx.lineWidth = 1;

    const gridSteps = 3;
    for (let i = 0; i <= gridSteps; i++) {
      const y = h - 18 - (i * (h - 26) / gridSteps);
      const val = this.yMin + (i * (this.yMax - this.yMin) / gridSteps);
      
      ctx.beginPath();
      ctx.moveTo(35, y);
      ctx.lineTo(w, y);
      ctx.stroke();

      ctx.fillText(`${val.toFixed(1)}${this.unit}`, 4, y + 3);
    }

    // Threshold indicator line if present
    if (this.threshold !== null && this.threshold >= this.yMin && this.threshold <= this.yMax) {
      const ty = h - 18 - ((this.threshold - this.yMin) / (this.yMax - this.yMin)) * (h - 26);
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = 'rgba(244, 63, 94, 0.7)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(35, ty);
      ctx.lineTo(w, ty);
      ctx.stroke();
      ctx.fillStyle = '#f43f5e';
      ctx.fillText('LIMIT', w - 32, ty - 3);
      ctx.restore();
    }

    // Plot each series line
    this.series.forEach(s => {
      if (s.data.length < 2) return;
      
      ctx.save();
      ctx.strokeStyle = s.color;
      ctx.lineWidth = s.lineWidth || 2;
      ctx.shadowColor = s.color;
      ctx.shadowBlur = s.glow ? 8 : 0;
      
      if (s.dashed) {
        ctx.setLineDash([4, 3]);
      } else {
        ctx.setLineDash([]);
      }

      ctx.beginPath();
      const xStep = (w - 40) / (this.maxPoints - 1);
      
      s.data.forEach((val, idx) => {
        const x = 38 + (idx + (this.maxPoints - s.data.length)) * xStep;
        const clamped = Math.max(this.yMin, Math.min(this.yMax, val));
        const y = h - 18 - ((clamped - this.yMin) / (this.yMax - this.yMin)) * (h - 26);
        
        if (idx === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
      ctx.restore();
    });
  }
}

class TelemetryChartsManager {
  constructor() {
    // 1. Vibration Dynamics (RMS & Peak)
    this.chartVib = new RealTimeStreamChart('chartVibration', {
      maxPoints: 40,
      yMin: 0,
      yMax: 12,
      unit: '',
      threshold: 4.5,
      series: [
        { name: 'vibration_rms', color: '#06b6d4', glow: true, lineWidth: 2 },
        { name: 'vibration_peak', color: '#e879f9', dashed: true, lineWidth: 1.5 }
      ]
    });

    // 2. Thermal Profile (Actual vs Twin Expected)
    this.chartTemp = new RealTimeStreamChart('chartTemperature', {
      maxPoints: 40,
      yMin: 30,
      yMax: 100,
      unit: '°C',
      threshold: 85,
      series: [
        { name: 'temp_actual', color: '#f59e0b', glow: true, lineWidth: 2 },
        { name: 'temp_twin', color: '#38bdf8', dashed: true, lineWidth: 1.5 }
      ]
    });

    // 3. Electrical & Speed Dynamics
    this.chartElectrical = new RealTimeStreamChart('chartElectrical', {
      maxPoints: 40,
      yMin: 10,
      yMax: 40,
      unit: 'A',
      threshold: 32,
      series: [
        { name: 'current_amp', color: '#eab308', glow: true, lineWidth: 2 }
      ]
    });

    // 4. Composite Health Index & Residual Tracking
    this.chartHealth = new RealTimeStreamChart('chartHealth', {
      maxPoints: 40,
      yMin: 0,
      yMax: 100,
      unit: '%',
      threshold: 60,
      series: [
        { name: 'health_index', color: '#10b981', glow: true, lineWidth: 2.5 }
      ]
    });
  }

  update(packet) {
    const raw = packet.raw_telemetry || {};
    const dt = packet.digital_twin || {};
    
    // Update Vibration
    this.chartVib.pushValues({
      vibration_rms: raw.vibration_rms,
      vibration_peak: raw.vibration_peak
    });

    // Update Temperature
    const exp = dt.expected_state || {};
    this.chartTemp.pushValues({
      temp_actual: raw.temperature,
      temp_twin: exp.temperature || raw.temperature
    });

    // Update Electrical
    this.chartElectrical.pushValues({
      current_amp: raw.current_amp
    });

    // Update Health
    this.chartHealth.pushValues({
      health_index: dt.composite_health_index
    });
  }
}

window.TelemetryChartsManager = TelemetryChartsManager;
