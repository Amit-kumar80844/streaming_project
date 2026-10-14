/**
 * Telemetry Charts Manager — Real-Time Digital Twin Dashboard
 * Uses native Canvas API; no external charting library required.
 * IOE413 Team 12
 */

class TelemetryChartsManager {
  constructor() {
    this.MAX_POINTS = 80;
    this.charts = {};
    this._init();
  }

  _init() {
    // Vibration RMS + Peak
    this.charts.vib = this._makeChart('chartVibration', {
      datasets: [
        { label: 'RMS',  color: '#38BDF8', data: [], limit: 4.5 },
        { label: 'Peak', color: '#A78BFA', data: [] },
      ],
      yLabel: 'mm/s',
      limitLine: 4.5,
      limitColor: 'rgba(248, 113, 113, 0.75)',
    });

    // Temperature: actual vs twin
    this.charts.temp = this._makeChart('chartTemperature', {
      datasets: [
        { label: 'Actual',  color: '#FBBF24', data: [] },
        { label: 'Twin',    color: '#38BDF8', data: [], dashed: true },
      ],
      yLabel: '°C',
      limitLine: 85,
      limitColor: 'rgba(248, 113, 113, 0.75)',
    });

    // Current
    this.charts.curr = this._makeChart('chartElectrical', {
      datasets: [
        { label: 'Current (A)', color: '#2DD4BF', data: [] },
      ],
      yLabel: 'A',
      limitLine: 28.5,
      limitColor: 'rgba(251, 191, 36, 0.75)',
    });

    // CHI
    this.charts.health = this._makeChart('chartHealth', {
      datasets: [
        { label: 'CHI (%)', color: '#4ADE80', data: [], fill: true },
      ],
      yLabel: '%',
      yMin: 0, yMax: 100,
      limitLine: 60,
      limitColor: 'rgba(248, 113, 113, 0.75)',
    });

    window.addEventListener('resize', () => this._resizeAll());
  }

  _makeChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    const chart = { canvas, ctx, config, labels: [] };
    this._resize(chart);
    return chart;
  }

  _resize(chart) {
    if (!chart) return;
    const wrap = chart.canvas.parentElement;
    if (!wrap) return;
    const dpr = window.devicePixelRatio || 1;
    const w = wrap.clientWidth  || 300;
    const h = wrap.clientHeight || 130;
    chart.canvas.width  = w * dpr;
    chart.canvas.height = h * dpr;
    chart.canvas.style.width  = w + 'px';
    chart.canvas.style.height = h + 'px';
    chart.ctx.scale(dpr, dpr);
    chart._w = w;
    chart._h = h;
  }

  _resizeAll() {
    Object.values(this.charts).forEach(c => { if (c) this._resize(c); });
    this._redrawAll();
  }

  update(packet) {
    const rt  = packet.raw_telemetry || {};
    const dt  = packet.digital_twin  || {};
    const exp = dt.expected_state    || {};
    const chi = dt.composite_health_index;

    this._push(this.charts.vib,    [rt.vibration_rms, rt.vibration_peak]);
    this._push(this.charts.temp,   [rt.temperature, exp.temperature]);
    this._push(this.charts.curr,   [rt.current_amp]);
    this._push(this.charts.health, [chi]);

    this._redrawAll();
  }

  _push(chart, values) {
    if (!chart) return;
    chart.labels.push('');
    if (chart.labels.length > this.MAX_POINTS) chart.labels.shift();
    chart.config.datasets.forEach((ds, i) => {
      ds.data.push(values[i] ?? null);
      if (ds.data.length > this.MAX_POINTS) ds.data.shift();
    });
  }

  _redrawAll() {
    Object.values(this.charts).forEach(c => { if (c) this._drawChart(c); });
  }

  _drawChart(chart) {
    const { ctx, config } = chart;
    const w = chart._w || chart.canvas.width;
    const h = chart._h || chart.canvas.height;
    const PAD = { top: 8, right: 12, bottom: 24, left: 40 };
    const plotW = w - PAD.left - PAD.right;
    const plotH = h - PAD.top  - PAD.bottom;

    ctx.clearRect(0, 0, w, h);

    // Collect all data points to compute range
    let allVals = [];
    config.datasets.forEach(ds => {
      ds.data.forEach(v => { if (v != null) allVals.push(v); });
    });
    if (allVals.length === 0) {
      this._drawEmpty(ctx, w, h);
      return;
    }

    let yMin = config.yMin ?? (Math.min(...allVals) * 0.9);
    let yMax = config.yMax ?? (Math.max(...allVals) * 1.1 + 0.001);
    if (config.limitLine) {
      yMax = Math.max(yMax, config.limitLine * 1.05);
    }
    if (yMax - yMin < 0.5) { yMin -= 0.25; yMax += 0.25; }

    const scaleX = i => PAD.left + (i / (this.MAX_POINTS - 1)) * plotW;
    const scaleY = v => PAD.top  + plotH - ((v - yMin) / (yMax - yMin)) * plotH;

    // Grid lines (4 horizontal)
    ctx.strokeStyle = 'rgba(39, 50, 64, 0.7)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = PAD.top + (plotH / 4) * i;
      ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(PAD.left + plotW, y); ctx.stroke();
      const val = yMax - ((yMax - yMin) / 4) * i;
      ctx.fillStyle = '#748196';
      ctx.font = '10px JetBrains Mono, monospace';
      ctx.textAlign = 'right';
      ctx.fillText(val.toFixed(1), PAD.left - 4, y + 3);
    }

    // Limit line
    if (config.limitLine != null && config.limitLine >= yMin && config.limitLine <= yMax) {
      const ly = scaleY(config.limitLine);
      ctx.strokeStyle = config.limitColor || 'rgba(248, 113, 113, 0.75)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 3]);
      ctx.beginPath(); ctx.moveTo(PAD.left, ly); ctx.lineTo(PAD.left + plotW, ly); ctx.stroke();
      ctx.setLineDash([]);
    }

    // Datasets
    config.datasets.forEach((ds, di) => {
      const pts = ds.data;
      if (!pts.length) return;

      ctx.save();
      ctx.beginPath();
      ctx.rect(PAD.left, PAD.top, plotW, plotH);
      ctx.clip();

      ctx.strokeStyle = ds.color;
      ctx.lineWidth = 1.5;
      ctx.lineJoin = 'round';
      if (ds.dashed) ctx.setLineDash([4, 3]);

      // Fill (only first dataset with fill:true)
      if (ds.fill) {
        ctx.beginPath();
        let started = false;
        pts.forEach((v, i) => {
          if (v == null) return;
          const x = scaleX(i);
          const y = scaleY(v);
          if (!started) { ctx.moveTo(x, y); started = true; }
          else ctx.lineTo(x, y);
        });
        // Close fill path to bottom
        const lastI = pts.reduce((a, v, i) => v != null ? i : a, -1);
        const firstI = pts.findIndex(v => v != null);
        if (lastI >= 0) {
          ctx.lineTo(scaleX(lastI), PAD.top + plotH);
          ctx.lineTo(scaleX(firstI), PAD.top + plotH);
          ctx.closePath();
          const grad = ctx.createLinearGradient(0, PAD.top, 0, PAD.top + plotH);
          grad.addColorStop(0, ds.color + '25');
          grad.addColorStop(1, ds.color + '00');
          ctx.fillStyle = grad;
          ctx.fill();
        }
      }

      // Line
      ctx.beginPath();
      let started = false;
      pts.forEach((v, i) => {
        if (v == null) { started = false; return; }
        const x = scaleX(i);
        const y = scaleY(v);
        if (!started) { ctx.moveTo(x, y); started = true; }
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();
    });

    // Axis label
    ctx.fillStyle = '#748196';
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.textAlign = 'left';
    ctx.save();
    ctx.translate(10, PAD.top + plotH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText(config.yLabel || '', 0, 0);
    ctx.restore();

    // Legend
    let lx = PAD.left;
    config.datasets.forEach(ds => {
      ctx.fillStyle = ds.color;
      ctx.fillRect(lx, h - 14, 14, 3);
      ctx.fillStyle = '#A7B3C4';
      ctx.font = '10px Inter, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(ds.label, lx + 18, h - 9);
      lx += ctx.measureText(ds.label).width + 36;
    });
  }

  _drawEmpty(ctx, w, h) {
    ctx.fillStyle = '#748196';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Awaiting stream…', w / 2, h / 2 + 4);
  }
}
