<template>
  <div class="course-analytics">
    <p v-if="loading" class="empty-tab">Loading learning analytics...</p>
    <p v-else-if="error" class="empty-tab course-analytics__error" role="alert">{{ error }}</p>

    <template v-else-if="overview">
      <div class="analytics-summary">
        <article class="analytics-stat analytics-stat--accent">
          <span>Completion</span>
          <strong>{{ overview.summary.completion_rate }}<small>%</small></strong>
          <small>{{ overview.summary.completed_learners }} of {{ overview.summary.enrolled_learners }} learners</small>
        </article>
        <article class="analytics-stat">
          <span>Started</span>
          <strong>{{ overview.summary.started_learners }}<small>/{{ overview.summary.enrolled_learners }}</small></strong>
          <small>{{ overview.summary.started_rate }}% of assigned seats</small>
        </article>
        <article class="analytics-stat">
          <span>Median time</span>
          <strong>{{ overview.summary.median_time_minutes ?? '—' }}<small v-if="overview.summary.median_time_minutes !== null"> min</small></strong>
          <small>{{ overview.summary.time_over_estimate_rate }}% over estimate</small>
        </article>
        <article class="analytics-stat">
          <span>Hint-free</span>
          <strong>{{ overview.summary.hint_free_rate }}<small>%</small></strong>
          <small>{{ overview.summary.hints_per_completion }} hints per completion</small>
        </article>
        <article class="analytics-stat">
          <span>First attempt</span>
          <strong>{{ overview.summary.first_attempt_rate }}<small>%</small></strong>
          <small>{{ overview.summary.reattempt_rate }}% needed a reattempt</small>
        </article>
        <article class="analytics-stat">
          <span>Abandonment</span>
          <strong>{{ overview.summary.abandonment_rate }}<small>%</small></strong>
          <small>started but not completed</small>
        </article>
      </div>

      <div class="impact-strip">
        <article class="impact-card" :class="`impact-card--${overview.summary.rag}`">
          <span class="impact-card__label">Overall signal</span>
          <strong>{{ ragLabel(overview.summary.rag) }}</strong>
          <p>{{ (overview.summary.rag_reasons || []).join(' · ') || 'Mixed evidence' }}</p>
        </article>
        <article class="impact-card">
          <span class="impact-card__label">Learning reported</span>
          <strong>{{ overview.summary.learning_reported ?? '—' }}<small v-if="overview.summary.learning_reported !== null">/5</small></strong>
          <p>{{ overview.summary.pulse_responses }} pulse {{ overview.summary.pulse_responses === 1 ? 'response' : 'responses' }}</p>
        </article>
        <article class="impact-card">
          <span class="impact-card__label">Confidence gain</span>
          <strong>{{ overview.summary.confidence_gain !== null ? `${overview.summary.confidence_gain > 0 ? '+' : ''}${overview.summary.confidence_gain}` : '—' }}</strong>
          <p>Performance-growth proxy, not a psychological score</p>
        </article>
      </div>

      <div class="analytics-section-head">
        <div>
          <h3>Exercise signals</h3>
          <p>Completion, time, hints, and attempts for each assigned exercise.</p>
        </div>
        <span class="analytics-muted">Descriptive only &middot; not a grade</span>
      </div>

      <div class="analytics-table-wrap">
        <table class="analytics-table">
          <thead>
            <tr>
              <th scope="col">Exercise</th>
              <th scope="col">Started</th>
              <th scope="col">Completed</th>
              <th scope="col">Abandoned</th>
              <th scope="col">Learning</th>
              <th scope="col">Attempts</th>
              <th scope="col">Signal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="exercise in exercises" :key="exercise.lab_id">
              <td>
                <span class="analytics-exercise">{{ exercise.lab_name }}</span>
                <small>{{ exercise.track_name }}<template v-if="exercise.level_name"> · {{ exercise.level_name }}</template></small>
              </td>
              <td>{{ exercise.started_learners }}</td>
              <td>
                <span class="analytics-rate">{{ exercise.completion_rate }}%</span>
                <small>{{ exercise.completed_learners }} learners</small>
              </td>
              <td>
                <span class="analytics-rate">{{ exercise.abandonment_rate }}%</span>
                <small>abandoned</small>
              </td>
              <td>
                {{ exercise.learning_reported ?? '—' }}<small v-if="exercise.learning_reported !== null">/5 · {{ exercise.pulse_responses }} pulse</small>
              </td>
              <td>{{ exercise.median_attempts ?? '—' }}<small>{{ exercise.first_attempt_rate }}% first try</small></td>
              <td>
                <span class="analytics-rag" :class="`analytics-rag--${exercise.rag}`">
                  {{ ragLabel(exercise.rag) }}
                </span>
                <small v-if="exercise.rag_reasons?.length">{{ exercise.rag_reasons.join(' · ') }}</small>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="teachingSignals.length" class="teaching-signals">
        <article v-for="signal in teachingSignals" :key="signal.title" class="teaching-signal">
          <span class="teaching-signal__icon" aria-hidden="true">{{ signal.icon }}</span>
          <div>
            <h4>{{ signal.title }}</h4>
            <p>{{ signal.body }}</p>
          </div>
        </article>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  courseId: { type: [Number, String], required: true },
})

const loading = ref(true)
const error = ref('')
const overview = ref(null)
const exercises = ref([])

const ragLabel = (rag) => ({
  red: 'Red',
  amber: 'Amber',
  green: 'Green',
}[rag] || 'No signal')

const teachingSignals = computed(() => {
  const signals = []
  const rows = exercises.value
  if (rows.some((row) => row.flags.includes('high_hint_pressure'))) {
    signals.push({
      icon: '💡',
      title: 'Add a worked example',
      body: 'One or more exercises show high hint pressure. A short demonstration or hint rewrite may reduce guesswork.',
    })
  }
  if (rows.some((row) => row.flags.includes('high_attempt_burden'))) {
    signals.push({
      icon: '🧭',
      title: 'Check the starting point',
      body: 'Some exercises need many flag attempts. Review the brief, prerequisites, or flag format before changing difficulty.',
    })
  }
  if (rows.some((row) => row.flags.includes('low_completion'))) {
    signals.push({
      icon: '⏱️',
      title: 'Review time and scope',
      body: 'A started exercise has low completion. Consider splitting the task, extending time, or adding a checkpoint.',
    })
  }
  return signals
})

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const [overviewRes, exercisesRes] = await Promise.all([
      axios.get(`/analytics/courses/${props.courseId}/overview`),
      axios.get(`/analytics/courses/${props.courseId}/exercises`),
    ])
    overview.value = overviewRes.data
    exercises.value = exercisesRes.data.exercises || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load course analytics.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.course-analytics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.course-analytics__error {
  color: var(--danger);
}

.analytics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
  gap: 0.6rem;
}

.analytics-stat {
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.analytics-stat--accent {
  border-color: color-mix(in srgb, var(--accent) 40%, var(--border-color));
  background:
    radial-gradient(circle at 100% 0%, color-mix(in srgb, var(--accent) 12%, transparent), transparent 60%),
    var(--bg-secondary);
}

.analytics-stat > span {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.analytics-stat strong {
  display: block;
  margin: 0.2rem 0 0.1rem;
  color: var(--text-primary);
  font-size: 1.3rem;
  font-variant-numeric: tabular-nums;
}

.analytics-stat strong small {
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 600;
}

.analytics-stat > small {
  color: var(--text-muted);
  font-size: 0.62rem;
}

.impact-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.55rem;
}

.impact-card {
  --impact-accent: var(--accent);
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--impact-accent);
  border-radius: 11px;
  background: var(--bg-primary);
}

.impact-card--red { --impact-accent: var(--danger); }
.impact-card--amber { --impact-accent: var(--warning); }
.impact-card--green { --impact-accent: var(--success); }

.impact-card__label {
  display: block;
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.impact-card strong {
  display: block;
  margin: 0.15rem 0;
  color: var(--impact-accent);
  font-size: 1.1rem;
}

.impact-card strong small {
  color: var(--text-muted);
  font-size: 0.68rem;
}

.impact-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.62rem;
  line-height: 1.4;
}

.analytics-section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 0.3rem;
}

.analytics-section-head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.92rem;
}

.analytics-section-head p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.7rem;
}

.analytics-muted {
  color: var(--text-muted);
  font-size: 0.64rem;
}

.analytics-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.analytics-table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
  font-size: 0.72rem;
}

.analytics-table th,
.analytics-table td {
  padding: 0.6rem 0.7rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  vertical-align: top;
}

.analytics-table th {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 0.58rem;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.analytics-table tbody tr:last-child td {
  border-bottom: 0;
}

.analytics-exercise {
  display: block;
  color: var(--text-primary);
  font-weight: 600;
}

.analytics-table td small {
  display: block;
  margin-top: 0.1rem;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.analytics-rate {
  color: var(--text-primary);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.analytics-flag {
  display: inline-block;
  margin: 0 0.2rem 0.2rem 0;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  font-size: 0.56rem;
  font-weight: 700;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.analytics-rag {
  display: inline-block;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.analytics-rag--red {
  background: color-mix(in srgb, var(--danger) 15%, transparent);
  color: var(--danger);
}

.analytics-rag--amber {
  background: color-mix(in srgb, var(--warning) 16%, transparent);
  color: var(--warning);
}

.analytics-rag--green {
  background: color-mix(in srgb, var(--success) 15%, transparent);
  color: var(--success);
}

.analytics-flag--high_hint_pressure {
  background: color-mix(in srgb, var(--warning) 15%, transparent);
  color: var(--warning);
}

.analytics-flag--high_attempt_burden {
  background: color-mix(in srgb, var(--danger) 12%, transparent);
  color: var(--danger);
}

.analytics-flag--low_completion {
  background: color-mix(in srgb, var(--accent) 13%, transparent);
  color: var(--accent);
}

.teaching-signals {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.6rem;
}

.teaching-signal {
  display: flex;
  gap: 0.65rem;
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.teaching-signal__icon {
  font-size: 1.2rem;
  line-height: 1;
}

.teaching-signal h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.76rem;
}

.teaching-signal p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.66rem;
  line-height: 1.45;
}

@media (max-width: 720px) {
  .analytics-section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
