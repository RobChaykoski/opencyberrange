# Charting standard

The Release 5 frontend uses **Apache ECharts** for data visualization.

## Rules

1. Use `components/EChart.vue`; do not initialize ECharts directly in a view.
2. Import only the chart types and components a view needs. The shared wrapper
   registers line, bar, grid, legend, tooltip, and mark-line support. Add a new
   chart type there deliberately, not by importing the full `echarts` bundle.
3. Keep the option object in the view. Shared colours, tooltip styling, axes, and
   grid defaults live in `components/charts/echartsTheme.js`.
4. Every chart needs an `aria-label` summary and an accessible table of the same
   values, visible or `sr-only`. The chart is an aid, not the only record.
5. Charts show aggregates, not learner labels or rankings. Follow the existing
   cohort-suppression rules; do not plot a row the analytics service suppressed.
6. Instructor-only charts belong in instructor-only chunks. Lazy-load the
   containing view or panel (as `Course.vue` does with `CourseAnalytics.vue`) so
   learners do not download the ECharts bundle.
7. Disable animation when the panel auto-refreshes. A full dataset swap should
   not flash the dashboard.
8. Prefer horizontal bars for many categories, heatmaps for dense matrices, and
   line charts for time series. Keep labels truncated with a tooltip instead of
   overlapping them.

## Bundle budget

The ECharts chunk is roughly 553 kB minified / 187 kB gzip. It currently loads
only for the instructor dashboard and the course Analytics tab. If another
learner-facing view needs a chart, check the bundle impact first and consider a
lighter visual instead.

## Reporting

Charts are not reports. PDF, certificate, and transcript generation stays on the
backend `fpdf2` pipeline. ECharts is browser-only.
