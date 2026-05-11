// Chart.js global config — runs AFTER Chart.js is loaded
// No DOMContentLoaded needed since this script is placed AFTER chart.umd.min.js in base.html

Chart.defaults.font.family = "'DM Sans', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#8B6E5A';
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = true;
Chart.defaults.animation = { duration: 550, easing: 'easeInOutQuart' };

// ── THIS IS THE KEY FIX — set interaction globally ──────────────────────────
Chart.defaults.interaction.mode      = 'index';
Chart.defaults.interaction.intersect = false;

// Tooltip
Chart.defaults.plugins.tooltip.enabled         = true;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(26,20,16,0.92)';
Chart.defaults.plugins.tooltip.titleColor      = '#F5A264';
Chart.defaults.plugins.tooltip.bodyColor       = '#ffffff';
Chart.defaults.plugins.tooltip.borderColor     = 'rgba(232,112,26,0.45)';
Chart.defaults.plugins.tooltip.borderWidth     = 1;
Chart.defaults.plugins.tooltip.padding         = 12;
Chart.defaults.plugins.tooltip.cornerRadius    = 10;
Chart.defaults.plugins.tooltip.displayColors   = true;
Chart.defaults.plugins.tooltip.boxPadding      = 4;
Chart.defaults.plugins.tooltip.titleFont       = { size: 12, weight: '600' };
Chart.defaults.plugins.tooltip.bodyFont        = { size: 12 };

// Legend
Chart.defaults.plugins.legend.labels.boxWidth      = 12;
Chart.defaults.plugins.legend.labels.boxHeight     = 12;
Chart.defaults.plugins.legend.labels.padding       = 16;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle    = 'circle';

// Shared helpers used in templates
window.GRID_COLOR = 'rgba(234,216,204,0.6)';

window.ACADEMIC_PALETTE = {
  orange:  '#E8701A',
  orangeLight: '#F5A264',
  orangeFill:  'rgba(232,112,26,0.13)',
  green:   '#2E8B57',
  red:     '#C0392B',
  blue:    '#2980B9',
  series:  ['#E8701A','#2E8B57','#2980B9','#8E44AD','#C0392B','#F39C12','#16A085','#D35400'],
};

// Shared tooltip config object — use spread in each chart: { ...TT }
window.TT = {
  enabled:         true,
  backgroundColor: 'rgba(26,20,16,0.92)',
  titleColor:      '#F5A264',
  bodyColor:       '#ffffff',
  borderColor:     'rgba(232,112,26,0.45)',
  borderWidth:     1,
  padding:         12,
  cornerRadius:    10,
  displayColors:   true,
  boxPadding:      4,
  titleFont:       { size: 12, weight: '600' },
  bodyFont:        { size: 12 },
};
