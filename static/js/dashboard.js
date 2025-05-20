document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('roaChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: roaData.labels,
      datasets: [{
        label: 'ROA mensual (%)',
        data: roaData.values,
        fill: false,
        tension: 0.1
      }]
    },
    options: {
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
});
