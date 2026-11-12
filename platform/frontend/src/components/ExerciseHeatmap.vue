<template>
  <section class="heatmap" aria-labelledby="exercise-heatmap-title">
    <div class="heatmap__head">
      <div>
        <p class="heatmap__eyebrow">Exercise heatmap</p>
        <h3 id="exercise-heatmap-title">Completion and success at a glance</h3>
        <p class="heatmap__intro">
          Each cell shows the value and the sample size. Colour is a review prompt,
          not a grade or a learner label.
        </p>
      </div>
      <div class="heatmap__legend" aria-label="Heatmap legend">
        <span><i class="heatmap-dot heatmap-dot--green" aria-hidden="true"></i>Strong</span>
        <span><i class="heatmap-dot heatmap-dot--amber" aria-hidden="true"></i>Watch</span>
        <span><i class="heatmap-dot heatmap-dot--red" aria-hidden="true"></i>Needs attention</span>
        <span><i class="heatmap-dot heatmap-dot--grey" aria-hidden="true"></i>Suppressed</span>
      </div>
    </div>

    <div class="heatmap__wrap" role="region" aria-label="Exercise completion and success heatmap" tabindex="0">
      <table class="heatmap__table">
        <caption>Completion and success by assigned exercise. Suppressed rows hide percentages until the cohort reaches the minimum size.</caption>
        <thead>
          <tr>
            <th scope="col">Exercise</th>
            <th scope="col">Completion</th>
            <th scope="col">First attempt</th>
            <th scope="col">Hint-free</th>
            <th scope="col">Abandonment</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.lab_id">
            <th scope="row" class="heatmap__exercise">
              <span>{{ row.lab_name }}</span>
              <small>{{ row.chapter_label || row.track_name }}<template v-if="row.level_name"> · {{ row.level_name }}</template></small>
            </th>
            <template v-if="row.cohort_state === 'available'">
              <td
                v-for="cell in cellsFor(row)"
                :key="cell.key"
                class="heatmap__cell"
                :class="`heatmap__cell--${cell.level}`"
              >
                <span class="heatmap__value">{{ cell.value }}</span>
                <span class="heatmap__status">{{ cell.label }}</span>
                <small>n={{ row.sample_size }}</small>
              </td>
            </template>
            <td v-else :colspan="4" class="heatmap__cell heatmap__cell--grey">
              <span class="heatmap__status">{{ cohortStateLabel(row.cohort_state) }}</span>
              <small>metrics hidden until the cohort reaches {{ row.suppression?.minimum_cohort_size || 5 }} learners</small>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="5" class="heatmap__empty">No assigned exercises yet.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="heatmap__note">
      Completion is completed learners divided by enrolled learners. First attempt
      is the share of completions with one attempt. Hint-free is the share of
      completions with no hints. Abandonment is started learners without a
      completion. Read the value and n before changing a course.
    </p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  exercises: { type: Array, default: () => [] },
})

const rows = computed(() =>
  [...props.exercises].sort((a, b) => {
    const aAvailable = a.cohort_state === 'available'
    const bAvailable = b.cohort_state === 'available'
    if (aAvailable !== bAvailable) return aAvailable ? -1 : 1
    return (a.completion_rate ?? 0) - (b.completion_rate ?? 0)
  })
)

function levelFor(value, { lowerIsBetter = false } = {}) {
  if (value === null || value === undefined) return 'grey'
  if (lowerIsBetter) {
    if (value <= 10) return 'green'
    if (value <= 30) return 'amber'
    return 'red'
  }
  if (value >= 80) return 'green'
  if (value >= 50) return 'amber'
  return 'red'
}

function labelFor(level) {
  return {
    green: 'Strong',
    amber: 'Watch',
    red: 'Needs attention',
    grey: 'No evidence',
  }[level] || 'No evidence'
}

function cellsFor(row) {
  const hintFree = row.hint_use_rate === null || row.hint_use_rate === undefined
    ? null
    : Math.max(0, 100 - row.hint_use_rate)
  const metrics = [
    { key: 'completion', value: row.completion_rate, lowerIsBetter: false, suffix: '%' },
    { key: 'first-attempt', value: row.first_attempt_rate, lowerIsBetter: false, suffix: '%' },
    { key: 'hint-free', value: hintFree, lowerIsBetter: false, suffix: '%' },
    { key: 'abandonment', value: row.abandonment_rate, lowerIsBetter: true, suffix: '%' },
  ]
  return metrics.map((metric) => {
    const level = levelFor(metric.value, { lowerIsBetter: metric.lowerIsBetter })
    return {
      key: metric.key,
      level,
      label: labelFor(level),
      value: metric.value === null || metric.value === undefined
        ? '—'
        : `${metric.value}${metric.suffix}`,
    }
  })
}

function cohortStateLabel(state) {
  return {
    suppressed: 'Suppressed',
    no_evidence: 'No evidence yet',
  }[state] || 'No evidence yet'
}
</script>

<style scoped>
.heatmap {
  margin: 1.25rem 0;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.heatmap__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.heatmap__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.heatmap__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 700;
}

.heatmap__intro {
  max-width: 52rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.5;
}

.heatmap__legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.75rem;
  flex: 0 0 auto;
  color: var(--text-muted);
  font-size: 0.66rem;
}

.heatmap__legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.heatmap-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}

.heatmap-dot--green { background: var(--success); }
.heatmap-dot--amber { background: var(--warning); }
.heatmap-dot--red { background: var(--danger); }
.heatmap-dot--grey { background: var(--text-muted); }

.heatmap__wrap {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.heatmap__table {
  width: 100%;
  min-width: 720px;
  border-collapse: separate;
  border-spacing: 3px;
  font-size: 0.72rem;
}

.heatmap__table caption {
  padding: 0.45rem 0.55rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  text-align: left;
}

.heatmap__table thead th {
  padding: 0.45rem 0.5rem;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-align: left;
  text-transform: uppercase;
}

.heatmap__exercise {
  min-width: 220px;
  padding: 0.45rem 0.5rem;
  color: var(--text-primary);
  font-weight: 600;
  text-align: left;
  vertical-align: top;
}

.heatmap__exercise small {
  display: block;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 400;
}

.heatmap__cell {
  padding: 0.45rem 0.5rem;
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  vertical-align: top;
}

.heatmap__cell--green {
  background: color-mix(in srgb, var(--success) 16%, var(--bg-primary));
  border-left: 3px solid var(--success);
}

.heatmap__cell--amber {
  background: color-mix(in srgb, var(--warning) 16%, var(--bg-primary));
  border-left: 3px solid var(--warning);
}

.heatmap__cell--red {
  background: color-mix(in srgb, var(--danger) 16%, var(--bg-primary));
  border-left: 3px solid var(--danger);
}

.heatmap__cell--grey {
  background: var(--bg-primary);
  border-left: 3px solid var(--text-muted);
}

.heatmap__value {
  display: block;
  color: var(--text-primary);
  font-size: 0.8rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.heatmap__status {
  display: block;
  color: var(--text-secondary);
  font-size: 0.62rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.heatmap__cell small {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.heatmap__empty {
  padding: 1rem;
  color: var(--text-muted);
  text-align: center;
}

.heatmap__note {
  margin: 0.65rem 0 0;
  color: var(--text-muted);
  font-size: 0.66rem;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .heatmap__head {
    flex-direction: column;
  }

  .heatmap__legend {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .heatmap__cell {
    transition: none;
  }
}
</style>
