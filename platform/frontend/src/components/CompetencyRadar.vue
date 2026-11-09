<template>
  <section class="competency-radar" aria-labelledby="competency-radar-title">
    <div class="competency-radar__head">
      <div>
        <p class="competency-radar__eyebrow">{{ data.mode === 'cohort' ? 'Cohort competency' : 'Your competency' }}</p>
        <h3 id="competency-radar-title">Competency radar</h3>
        <p class="competency-radar__note">
          {{ data.mode === 'cohort'
            ? 'Median, interquartile band, and target across the cohort. Small cohorts are suppressed.'
            : 'Baseline, current, and target. Missing components are provisional and labelled, not silently redistributed.' }}
        </p>
      </div>
      <span class="competency-radar__model">Model {{ data.model_version }}</span>
    </div>

    <div class="competency-radar__layout">
      <figure class="competency-chart">
        <svg viewBox="0 0 400 370" role="img" :aria-label="ariaLabel">
          <g class="competency-chart__grid">
            <polygon
              v-for="ring in rings"
              :key="ring"
              :points="ringPoints(ring)"
              fill="none"
              stroke="var(--border-color)"
              stroke-width="1"
            />
            <line
              v-for="(axis, index) in axes"
              :key="`axis-${axis.key}`"
              :x1="center.x"
              :y1="center.y"
              :x2="point(index, 100).x"
              :y2="point(index, 100).y"
              stroke="var(--border-color)"
              stroke-width="1"
            />
          </g>

          <template v-if="!isCohort">
            <polygon :points="polygon(axes.map((a) => a.baseline ?? 0))" class="competency-chart__baseline" />
            <polygon :points="polygon(axes.map((a) => a.target ?? 0))" class="competency-chart__target" />
            <polygon :points="polygon(axes.map((a) => a.current ?? 0))" class="competency-chart__current" />
          </template>

          <template v-else>
            <path :d="iqrPath" class="competency-chart__iqr" />
            <polygon :points="polygon(axes.map((a) => a.cohort_median ?? 0))" class="competency-chart__current" />
            <polygon :points="polygon(axes.map((a) => a.target ?? 0))" class="competency-chart__target" />
          </template>

          <g v-for="(axis, index) in axes" :key="`dot-${axis.key}`">
            <circle
              v-if="!isCohort"
              :cx="point(index, axis.current ?? 0).x"
              :cy="point(index, axis.current ?? 0).y"
              r="3.5"
              class="competency-chart__dot"
            />
            <circle
              v-else
              :cx="point(index, axis.cohort_median ?? 0).x"
              :cy="point(index, axis.cohort_median ?? 0).y"
              r="3.5"
              class="competency-chart__dot"
            />
            <text
              :x="labelPoint(index).x"
              :y="labelPoint(index).y"
              :text-anchor="labelAnchor(index)"
              class="competency-chart__label"
            >{{ axis.label }}</text>
          </g>
        </svg>
        <figcaption>
          {{ isCohort
            ? 'Cohort median is the solid accent shape; the interquartile band shows spread; the dashed shape is the target.'
            : 'Current is the solid accent shape; baseline is the muted shape; target is dashed.' }}
        </figcaption>
      </figure>

      <div class="competency-legend" aria-label="Chart legend">
        <span v-if="!isCohort" class="competency-legend__item competency-legend__item--baseline">Baseline</span>
        <span class="competency-legend__item competency-legend__item--current">{{ isCohort ? 'Cohort median' : 'Current' }}</span>
        <span v-if="isCohort" class="competency-legend__item competency-legend__item--iqr">Interquartile band</span>
        <span class="competency-legend__item competency-legend__item--target">Target {{ data.target_profile }}</span>
        <p class="competency-legend__weights">
          50% assessment · 25% independent completion · 15% retained · 10% instructor
        </p>
      </div>
    </div>

    <div class="sr-only">
      <table>
        <caption>Competency radar values and evidence quality</caption>
      <thead>
        <tr>
          <th scope="col">Competency</th>
          <template v-if="isCohort">
            <th scope="col">Cohort median</th>
            <th scope="col">Q1</th>
            <th scope="col">Q3</th>
          </template>
          <template v-else>
            <th scope="col">Baseline</th>
            <th scope="col">Current</th>
          </template>
          <th scope="col">Target</th>
          <th scope="col">Evidence</th>
          <th scope="col">Quality</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="axis in axes" :key="`table-${axis.key}`">
          <th scope="row">{{ axis.label }}</th>
          <template v-if="isCohort">
            <td>{{ value(axis.cohort_median) }}</td>
            <td>{{ value(axis.cohort_q1) }}</td>
            <td>{{ value(axis.cohort_q3) }}</td>
          </template>
          <template v-else>
            <td>{{ value(axis.baseline) }}</td>
            <td>{{ value(axis.current) }}</td>
          </template>
          <td>{{ value(axis.target) }}</td>
          <td>{{ axis.sample_size ?? axis.learners_with_evidence ?? 0 }}</td>
          <td>{{ axis.suppressed ? 'Suppressed' : (axis.evidence_quality || '—') }}</td>
        </tr>
      </tbody>
      </table>
    </div>

    <div class="competency-drilldown">
      <h4>Evidence behind each axis</h4>
      <details v-for="axis in axes" :key="`detail-${axis.key}`" class="competency-axis">
        <summary>
          <span>{{ axis.label }}</span>
          <span class="competency-axis__value">
            {{ isCohort ? `median ${value(axis.cohort_median)}` : `current ${value(axis.current)}` }}
            <b :class="`competency-status competency-status--${statusFor(axis)}`">
              {{ axis.suppressed ? 'Suppressed' : (axis.evidence_quality || 'No evidence') }}
            </b>
          </span>
        </summary>
        <div class="competency-axis__body">
          <p v-if="axis.suppressed" class="competency-axis__muted">
            This axis is below the minimum cohort size. Counts and exhibits are hidden.
          </p>
          <template v-else>
            <div class="competency-components">
              <span v-for="(componentValue, name) in axis.components" :key="name">
                <b>{{ componentLabel(name) }}</b>
                {{ value(componentValue) }}
              </span>
            </div>
            <p class="competency-axis__meta">
              {{ axis.sample_size ?? axis.learners_with_evidence ?? 0 }} evidence item(s) ·
              {{ axis.latest_evidence_at ? `latest ${formatDate(axis.latest_evidence_at)}` : 'no timestamp' }} ·
              model {{ axis.model_version || data.model_version }}
              <template v-if="axis.mapping_versions?.length"> · mapping {{ axis.mapping_versions.join(', ') }}</template>
            </p>
            <div v-if="axis.contributing_labs?.length" class="competency-evidence">
              <strong>Labs</strong>
              <ul>
                <li v-for="lab in axis.contributing_labs.slice(0, 8)" :key="`${axis.key}-${lab.lab_id}`">
                  {{ lab.lab_name }} <small>{{ lab.track || '' }} · {{ lab.mapping_version || 'unversioned' }}</small>
                </li>
              </ul>
            </div>
            <div v-if="axis.contributing_assessments?.length" class="competency-evidence">
              <strong>Assessments</strong>
              <ul>
                <li v-for="quiz in axis.contributing_assessments.slice(0, 8)" :key="`${axis.key}-quiz-${quiz.lab_id}`">
                  {{ quiz.lab_name }} · {{ quiz.score }}%
                </li>
              </ul>
            </div>
            <p class="competency-axis__muted">
              Sources: {{ axis.sources?.observed || 0 }} observed · {{ axis.sources?.self_reported || 0 }} self-reported ·
              {{ axis.sources?.instructor || 0 }} instructor. Weight coverage: {{ axis.weight_coverage_pct }}%.
            </p>
          </template>
        </div>
      </details>
    </div>

    <div v-if="!isCohort && confidenceAxes.length" class="competency-confidence">
      <h4>Self-confidence (separate from the score)</h4>
      <div v-for="axis in confidenceAxes" :key="`confidence-${axis.key}`" class="competency-confidence__row">
        <span>{{ axis.label }}</span>
        <div class="competency-confidence__bar" aria-hidden="true">
          <span :style="{ width: `${axis.self_confidence.value}%` }"></span>
        </div>
        <b>{{ axis.self_confidence.value }}%</b>
        <small>{{ axis.self_confidence.responses }} response(s)</small>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, required: true },
})

const center = { x: 200, y: 178 }
const radius = 118
const labelRadius = 146
const rings = [25, 50, 75, 100]

const axes = computed(() => props.data?.axes || [])
const isCohort = computed(() => props.data?.mode === 'cohort')
const confidenceAxes = computed(() =>
  axes.value.filter((axis) => axis.self_confidence?.value !== null && axis.self_confidence?.value !== undefined)
)

const angle = (index) => -Math.PI / 2 + (index * 2 * Math.PI) / Math.max(1, axes.value.length)
const point = (index, value, r = radius) => {
  const clamped = Math.max(0, Math.min(100, Number(value) || 0))
  const a = angle(index)
  return {
    x: Number((center.x + Math.cos(a) * r * (clamped / 100)).toFixed(2)),
    y: Number((center.y + Math.sin(a) * r * (clamped / 100)).toFixed(2)),
  }
}
const labelPoint = (index) => {
  const a = angle(index)
  return {
    x: Number((center.x + Math.cos(a) * labelRadius).toFixed(2)),
    y: Number((center.y + Math.sin(a) * labelRadius).toFixed(2)),
  }
}
const labelAnchor = (index) => {
  const x = labelPoint(index).x
  if (x < center.x - 8) return 'end'
  if (x > center.x + 8) return 'start'
  return 'middle'
}
const polygon = (values) => values.map((value, index) => {
  const p = point(index, value)
  return `${p.x},${p.y}`
}).join(' ')
const ringPoints = (ring) => polygon(axes.value.map(() => ring))
const iqrPath = computed(() => {
  const upper = axes.value.map((axis, index) => point(index, axis.cohort_q3 ?? 0))
  const lower = axes.value.map((axis, index) => point(index, axis.cohort_q1 ?? 0)).reverse()
  if (!upper.length) return ''
  return `M ${upper.map((p) => `${p.x},${p.y}`).join(' L ')} L ${lower.map((p) => `${p.x},${p.y}`).join(' L ')} Z`
})
const value = (v) => (v === null || v === undefined ? '—' : `${v}`)
const formatDate = (value) => {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString()
}
const componentLabel = (name) => ({
  assessment: 'Assessment',
  independent: 'Independent',
  retained: 'Retained',
  instructor: 'Instructor',
}[name] || name)
const statusFor = (axis) => {
  if (axis.suppressed) return 'grey'
  const score = isCohort.value ? axis.cohort_median : axis.current
  if (score === null || score === undefined) return 'grey'
  if (score >= 80) return 'green'
  if (score >= 60) return 'amber'
  return 'red'
}
const ariaLabel = computed(() => {
  const summary = axes.value.map((axis) =>
    `${axis.label}: ${isCohort.value ? `median ${value(axis.cohort_median)}` : `current ${value(axis.current)}, baseline ${value(axis.baseline)}`}`
  ).join('; ')
  return `Competency radar. ${summary}.`
})
</script>

<style scoped>
.competency-radar {
  margin-top: 1.25rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.competency-radar__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.competency-radar__eyebrow {
  margin: 0 0 0.15rem;
  color: var(--accent-text);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.competency-radar h3 {
  margin: 0 0 0.25rem;
  color: var(--text-primary);
  font-size: 1.05rem;
}

.competency-radar__note,
.competency-radar__model {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.45;
}

.competency-radar__model {
  flex-shrink: 0;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.68rem;
}

.competency-radar__layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(220px, 0.85fr);
  gap: 1rem;
  align-items: center;
  margin-top: 0.75rem;
}

.competency-chart {
  margin: 0;
  min-width: 0;
}

.competency-chart svg {
  width: 100%;
  max-width: 420px;
  display: block;
  margin: 0 auto;
}

.competency-chart figcaption {
  color: var(--text-muted);
  font-size: 0.7rem;
  line-height: 1.4;
  text-align: center;
}

.competency-chart__baseline {
  fill: color-mix(in srgb, var(--text-muted) 18%, transparent);
  stroke: var(--text-muted);
  stroke-dasharray: 4 3;
  stroke-width: 1.5;
}

.competency-chart__target {
  fill: none;
  stroke: var(--text-secondary);
  stroke-dasharray: 2 4;
  stroke-width: 1.5;
}

.competency-chart__current {
  fill: color-mix(in srgb, var(--accent) 20%, transparent);
  stroke: var(--accent);
  stroke-width: 2;
}

.competency-chart__iqr {
  fill: color-mix(in srgb, var(--accent) 20%, transparent);
  stroke: none;
}

.competency-chart__dot {
  fill: var(--accent);
}

.competency-chart__label {
  fill: var(--text-primary);
  font-size: 7px;
  font-weight: 600;
}

.competency-legend {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.competency-legend__item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.competency-legend__item::before {
  content: '';
  width: 14px;
  height: 3px;
  border-radius: 99px;
  background: var(--accent);
}

.competency-legend__item--baseline::before { background: var(--text-muted); }
.competency-legend__item--target::before { background: var(--text-secondary); height: 2px; }
.competency-legend__item--iqr::before { background: color-mix(in srgb, var(--accent) 30%, transparent); height: 10px; }

.competency-legend__weights {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.7rem;
  line-height: 1.4;
}

.competency-drilldown {
  margin-top: 1rem;
}

.competency-drilldown h4,
.competency-confidence h4 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 0.86rem;
}

.competency-axis {
  border-top: 1px solid var(--border-color);
  padding: 0.5rem 0;
}

.competency-axis summary {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 600;
}

.competency-axis__value {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.competency-axis__body {
  padding-top: 0.5rem;
}

.competency-components {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.9rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.competency-components b {
  color: var(--text-primary);
}

.competency-axis__meta,
.competency-axis__muted {
  margin: 0.35rem 0;
  color: var(--text-muted);
  font-size: 0.74rem;
  line-height: 1.45;
}

.competency-evidence {
  margin-top: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.competency-evidence ul {
  margin: 0.2rem 0 0;
  padding-left: 1.1rem;
}

.competency-evidence small {
  color: var(--text-muted);
}

.competency-status {
  display: inline-block;
  padding: 0.08rem 0.4rem;
  border-radius: 999px;
  font-size: 0.64rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.competency-status--green { background: color-mix(in srgb, var(--success) 15%, transparent); color: var(--badge-green); }
.competency-status--amber { background: color-mix(in srgb, var(--warning) 16%, transparent); color: var(--badge-amber); }
.competency-status--red { background: color-mix(in srgb, var(--danger) 14%, transparent); color: var(--badge-red); }
.competency-status--grey { background: color-mix(in srgb, var(--text-muted) 14%, transparent); color: var(--text-secondary); }

.competency-confidence {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

.competency-confidence__row {
  display: grid;
  grid-template-columns: minmax(120px, 0.6fr) minmax(80px, 1fr) auto auto;
  gap: 0.5rem;
  align-items: center;
  color: var(--text-secondary);
  font-size: 0.78rem;
  margin-top: 0.35rem;
}

.competency-confidence__bar {
  height: 7px;
  border-radius: 999px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.competency-confidence__bar span {
  display: block;
  height: 100%;
  background: var(--accent);
}

.competency-confidence small {
  color: var(--text-muted);
}

@media (max-width: 760px) {
  .competency-radar__layout {
    grid-template-columns: 1fr;
  }

  .competency-confidence__row {
    grid-template-columns: 1fr auto auto;
  }

  .competency-confidence__bar {
    grid-column: 1 / -1;
  }
}
</style>
