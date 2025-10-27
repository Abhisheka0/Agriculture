// Chart.js global defaults and helpers
(function(){
  if (typeof window.Chart === 'undefined') return;
  Chart.defaults.font.family = 'Inter, Poppins, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial';
  Chart.defaults.color = '#334155';
  Chart.defaults.responsive = true;
  Chart.defaults.maintainAspectRatio = false;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.elements.line.tension = 0.35;
  Chart.defaults.elements.point.radius = 0;
  Chart.defaults.animation.duration = 500;

  // Expose a small helper to create a 3-series line chart
  window.createAgriLineChart = function(ctx, labels, temp, hum, soil){
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'Temperature (°C)', data: temp, borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,.15)', fill: true },
          { label: 'Humidity (%)', data: hum, borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,.12)', fill: true },
          { label: 'Soil Moisture (%)', data: soil, borderColor: '#16a34a', backgroundColor: 'rgba(22,163,74,.12)', fill: true }
        ]
      },
      options: {
        interaction: { intersect: false, mode: 'index' },
        plugins: {
          tooltip: { enabled: true, backgroundColor: 'rgba(15,23,42,.9)', padding: 10, bodySpacing: 6, titleSpacing: 6 },
          legend: { position: 'top' }
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(226,232,240,.6)' } }
        }
      }
    });
  };
})();
