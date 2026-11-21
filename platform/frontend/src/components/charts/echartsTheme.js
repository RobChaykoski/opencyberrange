/**
 * Shared colours and small option fragments for the ECharts views.
 *
 * These mirror the platform's slate/blue palette. Keep chart-specific series
 * colours in the view; keep axes, tooltips, and legends here so every new
 * chart looks like it belongs to the same product.
 */
export const ECHART_COLORS = {
  accent: '#3b82f6',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  grid: '#334155',
  text: '#94a3b8',
  muted: '#64748b',
  tooltipBg: '#1e293b',
  tooltipBorder: '#334155',
  tooltipTitle: '#f1f5f9',
  tooltipBody: '#cbd5e1',
}

export const tooltipStyle = {
  backgroundColor: ECHART_COLORS.tooltipBg,
  borderColor: ECHART_COLORS.tooltipBorder,
  borderWidth: 1,
  textStyle: { color: ECHART_COLORS.tooltipBody },
  titleStyle: { color: ECHART_COLORS.tooltipTitle },
}

export const legendStyle = {
  top: 0,
  textStyle: { color: ECHART_COLORS.text },
  itemWidth: 10,
  itemHeight: 10,
  icon: 'circle',
}

export const categoryAxis = {
  type: 'category',
  boundaryGap: false,
  axisLine: { lineStyle: { color: ECHART_COLORS.grid } },
  axisTick: { show: false },
  axisLabel: { color: ECHART_COLORS.muted },
  splitLine: { show: false },
}

export const valueAxis = {
  type: 'value',
  minInterval: 1,
  axisLine: { show: false },
  axisTick: { show: false },
  axisLabel: { color: ECHART_COLORS.muted },
  splitLine: { lineStyle: { color: ECHART_COLORS.grid } },
}

export const chartGrid = {
  top: 40,
  right: 16,
  bottom: 24,
  left: 40,
  containLabel: true,
}
