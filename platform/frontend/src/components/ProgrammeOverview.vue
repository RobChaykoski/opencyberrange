<template>
  <section v-if="compact" class="programme programme--compact" aria-labelledby="programme-title">
    <div v-if="loading" class="programme-state">Loading teaching snapshot...</div>
    <div v-else-if="error" class="programme-state programme-state--error" role="alert">{{ error }}</div>
    <div v-else-if="!rows.length" class="programme-state">No active courses are available for this view.</div>
    <template v-else>
      <div class="programme-compact-row">
        <div>
          <p class="programme-eyebrow">{{ isTeaching ? 'Teaching snapshot' : 'Programme progress' }}</p>
          <h2 id="programme-title">Course health</h2>
          <p class="programme-context">{{ summary.courses }} courses · {{ summary.learners }} learners</p>
        </div>
        <div class="programme-compact-metrics">
          <span><strong>{{ percent(summary.completion) }}</strong> completion</span>
          <span><strong>{{ percent(summary.responseRate) }}</strong> response</span>
          <span><strong>{{ percent(summary.coachingCoverage) }}</strong> coaching</span>
          <span><strong>{{ feeling.emoji }} {{ feeling.label }}</strong> feeling</span>
        </div>
        <router-link to="/courses" class="programme-compact-link">Open programme view</router-link>
      </div>
      <p class="programme-compact-action"><strong>Next:</strong> {{ topAction }}</p>
    </template>
  </section>

  <section v-else class="programme" aria-labelledby="programme-title">
    <header class="programme-head">
      <div>
        <h2 id="programme-title">Semester view</h2>
        <p class="programme-lead">
          Overall progress, course health, and where the programme needs attention.
        </p>
        <p class="programme-context">
          {{ summary.courses }} courses · {{ summary.learners }} learners ·
          {{ summary.possiblePairs }} learner-exercise pairs
        </p>
      </div>
      <span v-if="!loading && rows.length" class="programme-chip" :class="`programme-chip--${overallTone}`">
        {{ overallLabel }}
      </span>
    </header>

    <div v-if="loading" class="programme-state">Loading programme metrics...</div>
    <div v-else-if="error" class="programme-state programme-state--error" role="alert">
      {{ error }}
    </div>
    <div v-else-if="!rows.length" class="programme-state">
      No active courses are available for this view.
    </div>

    <template v-else>
      <div class="programme-strip" aria-label="Programme summary">
        <article>
          <span>Completion</span>
          <strong>{{ percent(summary.completion) }}</strong>
          <small>{{ summary.completedPairs }} of {{ summary.possiblePairs }} pairs</small>
        </article>
        <article>
          <span>Feedback response</span>
          <strong>{{ percent(summary.responseRate) }}</strong>
          <small>{{ summary.respondents }} of {{ summary.learners }} learners</small>
        </article>
        <article>
          <span>Coaching coverage</span>
          <strong>{{ percent(summary.coachingCoverage) }}</strong>
          <small>{{ summary.coached }} students coached</small>
        </article>
        <article class="programme-strip__voice">
          <span>Student voice</span>
          <strong>{{ feeling.emoji }} {{ feeling.label }}</strong>
          <small>{{ feeling.detail }}</small>
        </article>
      </div>

      <section class="programme-card">
        <header class="programme-card__head">
          <div>
            <h3>Course portfolio</h3>
            <p>Sorted by risk. Open a course from its name. Small cohorts are shown as counts.</p>
          </div>
          <span class="programme-card__note">Generated {{ generatedLabel }}</span>
        </header>

        <div class="programme-table-wrap">
          <table class="programme-table">
            <caption>Course health and progress for the selected semester</caption>
            <thead>
              <tr>
                <th scope="col">Course</th>
                <th scope="col">Health</th>
                <th scope="col">Progress</th>
                <th scope="col">Feedback</th>
                <th scope="col">Checks</th>
                <th scope="col">Next action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.id">
                <th scope="row">
                  <router-link :to="`/courses/${row.id}`" class="programme-course">
                    {{ row.code }}
                  </router-link>
                  <small>{{ row.name }}</small>
                </th>
                <td>
                  <span class="programme-status" :class="`programme-status--${row.tone}`">
                    {{ row.status }}
                  </span>
                  <small v-if="row.reasons.length">{{ row.reasons[0] }}</small>
                </td>
                <td>
                  <strong>{{ percent(row.completion) }}</strong>
                  <small v-if="row.projection" :title="`${row.projection.method}, ${row.projection.confidence}; band ${row.projection.low}–${row.projection.high}%`">
                    Projected {{ row.projection.value }}% · {{ row.projection.low }}–{{ row.projection.high }}
                  </small>
                  <small v-else>{{ row.projectionNote }}</small>
                </td>
                <td>
                  <strong>{{ percent(row.responseRate) }} response</strong>
                  <small>{{ percent(row.coachingCoverage) }} coached</small>
                </td>
                <td>
                  <strong>{{ row.knowledgeAttempts }}</strong>
                  <small>{{ row.knowledgeAttempts ? `${percent(row.knowledgeAccuracy)} accuracy` : 'No checks yet' }}</small>
                </td>
                <td>
                  <span class="programme-next">{{ row.nextAction }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="programme-mobile-list">
          <article v-for="row in rows" :key="`mobile-${row.id}`" class="programme-mobile-card">
            <header>
              <router-link :to="`/courses/${row.id}`" class="programme-course">{{ row.code }}</router-link>
              <span class="programme-status" :class="`programme-status--${row.tone}`">{{ row.status }}</span>
            </header>
            <small class="programme-mobile-card__name">{{ row.name }}</small>
            <div class="programme-mobile-card__grid">
              <div>
                <span>Progress</span>
                <strong>{{ percent(row.completion) }}</strong>
                <small v-if="row.projection">Projected {{ row.projection.value }}% · {{ row.projection.low }}–{{ row.projection.high }}</small>
                <small v-else>{{ row.projectionNote }}</small>
              </div>
              <div>
                <span>Feedback</span>
                <strong>{{ percent(row.responseRate) }}</strong>
                <small>{{ percent(row.coachingCoverage) }} coached</small>
              </div>
              <div>
                <span>Checks</span>
                <strong>{{ row.knowledgeAttempts }}</strong>
                <small>{{ row.knowledgeAttempts ? `${percent(row.knowledgeAccuracy)} accuracy` : 'No checks yet' }}</small>
              </div>
            </div>
            <p class="programme-next">{{ row.nextAction }}</p>
          </article>
        </div>
      </section>

      <details class="programme-quality">
        <summary>How to read this view</summary>
        <ul>
          <li v-for="note in qualityNotes" :key="note">{{ note }}</li>
        </ul>
      </details>
    </template>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  courses: { type: Array, default: () => [] },
  mode: { type: String, default: 'executive' },
  compact: { type: Boolean, default: false },
})

const isTeaching = computed(() => props.mode === 'teaching')
const rows = ref([])
const loading = ref(true)
const error = ref('')
const generatedAt = ref(null)
const WEEK_MS = 7 * 24 * 60 * 60 * 1000

const safeData = (result) => (result.status === 'fulfilled' ? result.value.data : null)
const num = (value) => (typeof value === 'number' && Number.isFinite(value) ? value : null)
const percent = (value) => (value === null || value === undefined ? '—' : `${Math.round(value)}%`)

const courseStatus = (course) => {
  if (!course) return 'unknown'
  const now = Date.now()
  const start = course.start_date ? new Date(course.start_date).getTime() : null
  const end = course.end_date ? new Date(course.end_date).getTime() : null
  if (course.is_active === false) return 'inactive'
  if (end && now > end) return 'ended'
  if (start && now < start) return 'upcoming'
  return 'active'
}

const projectionFor = (course, completion) => {
  if (completion === null) return { projection: null, note: 'No completion data yet' }
  const status = courseStatus(course)
  if (status === 'ended') return { projection: null, note: 'Ended; final value shown' }
  if (status === 'upcoming') return { projection: null, note: 'Course has not started' }
  const start = course.start_date ? new Date(course.start_date).getTime() : null
  const end = course.end_date ? new Date(course.end_date).getTime() : null
  if (!start || !end || end <= start) return { projection: null, note: 'Add course dates to project' }
  const weeksElapsed = (Date.now() - start) / WEEK_MS
  const weeksTotal = (end - start) / WEEK_MS
  if (weeksElapsed < 1 || weeksTotal < 2) {
    return { projection: null, note: 'Baseline only; needs one full week' }
  }
  const value = Math.min(100, Math.round((completion / weeksElapsed) * weeksTotal))
  return {
    projection: {
      value,
      low: Math.max(0, value - 8),
      high: Math.min(100, value + 8),
      method: 'Run-rate projection',
      confidence: weeksElapsed >= 3 ? 'early projection' : 'very early projection',
    },
    note: '',
  }
}

const feelingFor = (feedback) => {
  const checkin = feedback?.course_checkin
  const values = [checkin?.clarity, checkin?.engagement, checkin?.confidence]
    .filter((value) => typeof value === 'number')
  const n = Number(checkin?.responses || 0)
  if (!values.length || !n) {
    return { emoji: '○', label: 'No check-in', detail: 'No check-in data yet', n: 0 }
  }
  const score = values.reduce((sum, value) => sum + value, 0) / values.length
  const suffix = n < 5 ? ' · early' : ''
  const noun = n === 1 ? 'check-in' : 'check-ins'
  if (score >= 4) return { emoji: '🙂', label: 'Positive', detail: `${score.toFixed(1)}/5 · ${n} ${noun}${suffix}`, score, n }
  if (score >= 3) return { emoji: '😐', label: 'Mixed', detail: `${score.toFixed(1)}/5 · ${n} ${noun}${suffix}`, score, n }
  return { emoji: '🙁', label: 'Low', detail: `${score.toFixed(1)}/5 · ${n} ${noun}${suffix}`, score, n }
}

const nextActionFor = (row) => {
  if (row.responseRate !== null && row.responseRate < 50) return 'Ask for a course check-in'
  if (row.coachingCoverage !== null && row.coachingCoverage < 50) return 'Add coaching notes'
  if (!row.knowledgeAttempts) return 'Add a knowledge check'
  if (row.completion !== null && row.completion < 50) return 'Check the next exercise and scope'
  if (row.status === 'Needs attention') return 'Review the next exercise and pacing'
  return 'Keep the feedback loop going'
}

const buildRow = (item) => {
  const course = item.course
  const overview = item.overview?.summary || {}
  const feedback = item.feedback || {}
  const rag = overview.rag || 'unknown'
  const tone = rag === 'green' ? 'healthy' : rag === 'amber' ? 'watch' : rag === 'red' ? 'attention' : 'muted'
  const status = rag === 'green' ? 'Healthy' : rag === 'amber' ? 'Watch' : rag === 'red' ? 'Needs attention' : 'No data'
  const enrolled = num(overview.enrolled_learners) ?? Number(course.student_count || 0)
  const assigned = num(overview.assigned_exercises) ?? Number(course.lab_count || 0)
  const completion = num(overview.completion_rate)
  const startedRate = num(overview.started_rate)
  const responseRate = num(feedback?.aggregate?.response_rate)
  const coached = Number(feedback?.instructor_coaching?.students_coached || 0)
  const coachingCoverage = enrolled ? (coached / enrolled) * 100 : null
  const knowledgeAttempts = Number(feedback?.quizzes?.attempts || 0)
  const knowledgeAccuracy = num(feedback?.quizzes?.accuracy)
  const { projection, note } = projectionFor(course, completion)
  const row = {
    id: course.id,
    code: course.code || 'Course',
    name: course.name || '',
    enrolled,
    assigned,
    completion,
    startedRate,
    responseRate,
    respondents: responseRate !== null ? Math.round((responseRate / 100) * enrolled) : 0,
    coached,
    coachingCoverage,
    knowledgeAttempts,
    knowledgeAccuracy,
    feedback,
    projection,
    projectionNote: note,
    rag,
    tone,
    status,
    reasons: overview.rag_reasons || [],
    completedLearners: Number(overview.completed_learners || 0),
  }
  row.nextAction = nextActionFor(row)
  return row
}

const load = async () => {
  const list = (props.courses || []).filter((course) => course && course.id)
  if (!list.length) {
    rows.value = []
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    const results = await Promise.allSettled(list.map(async (course) => {
      const [overview, feedback] = await Promise.allSettled([
        axios.get(`/analytics/courses/${course.id}/overview`),
        axios.get(`/courses/${course.id}/feedback/summary`),
      ])
      return { course, overview: safeData(overview), feedback: safeData(feedback) }
    }))
    const built = results
      .filter((result) => result.status === 'fulfilled')
      .map((result) => buildRow(result.value))
      .sort((a, b) => {
        const rank = { attention: 0, watch: 1, muted: 2, healthy: 3 }
        return (rank[a.tone] ?? 4) - (rank[b.tone] ?? 4) || a.code.localeCompare(b.code)
      })
    rows.value = built
    generatedAt.value = new Date()
    if (!built.length) error.value = 'Programme metrics are not available for these courses.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load programme metrics.'
  } finally {
    loading.value = false
  }
}

const summary = computed(() => {
  const active = rows.value
  const learners = active.reduce((sum, row) => sum + row.enrolled, 0)
  const possiblePairs = active.reduce((sum, row) => sum + row.enrolled * row.assigned, 0)
  const completedPairs = active.reduce((sum, row) => {
    if (row.completion === null) return sum
    return sum + (row.completion / 100) * row.enrolled * row.assigned
  }, 0)
  const completion = possiblePairs ? (completedPairs / possiblePairs) * 100 : null
  const respondents = active.reduce((sum, row) => sum + row.respondents, 0)
  const responseRate = learners ? (respondents / learners) * 100 : null
  const coached = active.reduce((sum, row) => sum + row.coached, 0)
  const coachingCoverage = learners ? (coached / learners) * 100 : null
  const knowledgeAttempts = active.reduce((sum, row) => sum + row.knowledgeAttempts, 0)
  const accuracyRows = active.filter((row) => row.knowledgeAccuracy !== null)
  const knowledgeAccuracy = accuracyRows.length
    ? accuracyRows.reduce((sum, row) => sum + row.knowledgeAccuracy, 0) / accuracyRows.length
    : null
  return {
    courses: active.length,
    learners,
    possiblePairs: Math.round(possiblePairs),
    completedPairs: Math.round(completedPairs),
    completion: completion === null ? null : Math.round(completion),
    respondents,
    responseRate,
    coached,
    coachingCoverage,
    knowledgeAttempts,
    knowledgeAccuracy,
  }
})

const feeling = computed(() => {
  const parts = rows.value.map((row) => feelingFor(row.feedback)).filter((item) => item.n)
  if (!parts.length) return feelingFor(null)
  const n = parts.reduce((sum, item) => sum + item.n, 0)
  const score = parts.reduce((sum, item) => sum + item.score * item.n, 0) / n
  const suffix = n < 5 ? ' · early' : ''
  const noun = n === 1 ? 'check-in' : 'check-ins'
  if (score >= 4) return { emoji: '🙂', label: 'Positive', detail: `${score.toFixed(1)}/5 · ${n} ${noun}${suffix}` }
  if (score >= 3) return { emoji: '😐', label: 'Mixed', detail: `${score.toFixed(1)}/5 · ${n} ${noun}${suffix}` }
  return { emoji: '🙁', label: 'Low', detail: `${score.toFixed(1)}/5 · ${n} ${noun}${suffix}` }
})

const overallTone = computed(() => {
  if (rows.value.some((row) => row.tone === 'attention')) return 'attention'
  if (rows.value.some((row) => row.tone === 'watch')) return 'watch'
  return 'healthy'
})
const overallLabel = computed(() => ({ attention: 'Needs attention', watch: 'Watch', healthy: 'Healthy' }[overallTone.value] || 'Watch'))

const topAction = computed(() => {
  const first = rows.value[0]
  return first ? `${first.code}: ${first.nextAction}` : 'Keep the feedback loop going.'
})

const qualityNotes = computed(() => {
  const notes = []
  const sessionGap = rows.value.some((row) => (
    row.completion !== null
    && row.completion > 20
    && row.startedRate !== null
    && row.startedRate < 5
  ))
  if (sessionGap) notes.push('Some courses have completions without reliable session-start records. Completion, hint, attempt, and time signals are the primary evidence.')
  if (rows.value.some((row) => row.enrolled > 0 && row.enrolled < 5)) notes.push('At least one course has fewer than five learners. Percentages are an early signal, not a trend.')
  if (rows.value.some((row) => !row.projection)) notes.push('A projection needs course dates and at least one full week of data. “Baseline” means no forecast is shown.')
  notes.push('Projections are run-rate planning aids, not promises, and are not used for individual learner decisions.')
  notes.push('Student voice is self-reported from the course check-in; it is not inferred from activity.')
  return notes
})

const generatedLabel = computed(() => (
  generatedAt.value
    ? generatedAt.value.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    : 'now'
))

watch(() => props.courses, load, { immediate: true, deep: true })
</script>

<style scoped>
.programme { display: grid; gap: 1rem; }
.programme-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.programme-eyebrow { margin: 0 0 0.2rem; color: var(--accent); font-size: 0.66rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
.programme-head h2, .programme--compact h2 { margin: 0; color: var(--text-primary); font-size: clamp(1.2rem, 2.5vw, 1.55rem); }
.programme-lead { margin: 0.3rem 0 0; max-width: 72ch; color: var(--text-secondary); font-size: 0.84rem; line-height: 1.55; }
.programme-context { margin: 0.35rem 0 0; color: var(--text-muted); font-size: 0.72rem; }
.programme-chip { flex-shrink: 0; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.programme-chip--healthy { background: var(--success-bg); color: var(--success); }
.programme-chip--watch { background: var(--warning-bg); color: var(--warning); }
.programme-chip--attention { background: var(--danger-bg); color: var(--danger); }
.programme-state { padding: 1rem; border: 1px solid var(--border-color); border-radius: 10px; color: var(--text-secondary); font-size: 0.85rem; }
.programme-state--error { border-color: var(--danger); color: var(--danger); }
.programme-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.65rem; }
.programme-strip article { display: grid; gap: 0.15rem; padding: 0.7rem 0.8rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-secondary); min-width: 0; }
.programme-strip span { color: var(--text-muted); font-size: 0.64rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.programme-strip strong { color: var(--text-primary); font-size: 1.15rem; line-height: 1.15; }
.programme-strip small { color: var(--text-muted); font-size: 0.66rem; line-height: 1.35; }
.programme-strip__voice { border-color: var(--info, #38bdf8) !important; }
.programme-card { display: grid; gap: 0.7rem; padding: 1rem; border: 1px solid var(--border-color); border-radius: 12px; background: var(--bg-secondary); min-width: 0; }
.programme-card__head { display: flex; justify-content: space-between; gap: 0.75rem; align-items: flex-start; }
.programme-card__head h3 { margin: 0; color: var(--text-primary); font-size: 0.95rem; }
.programme-card__head p { margin: 0.2rem 0 0; color: var(--text-muted); font-size: 0.74rem; line-height: 1.45; }
.programme-card__note { color: var(--text-muted); font-size: 0.7rem; white-space: nowrap; }
.programme-table-wrap { overflow-x: auto; }
.programme-table { width: 100%; border-collapse: collapse; min-width: 720px; }
.programme-table caption { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
.programme-table th, .programme-table td { padding: 0.55rem 0.45rem; border-bottom: 1px solid var(--border-color); text-align: left; vertical-align: top; font-size: 0.76rem; color: var(--text-secondary); }
.programme-table thead th { color: var(--text-muted); font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }
.programme-table tbody th { font-weight: 600; color: var(--text-primary); }
.programme-table strong { display: block; color: var(--text-primary); font-size: 0.86rem; }
.programme-table small { display: block; margin-top: 0.15rem; color: var(--text-muted); font-size: 0.66rem; line-height: 1.35; }
.programme-course { display: block; color: var(--text-primary); font-size: 0.78rem; font-weight: 700; text-decoration: none; }
.programme-course:hover { color: var(--accent); text-decoration: underline; }
.programme-status { display: inline-block; padding: 0.1rem 0.4rem; border-radius: 999px; font-size: 0.62rem; font-weight: 700; text-transform: uppercase; white-space: nowrap; }
.programme-status--healthy { background: var(--success-bg); color: var(--success); }
.programme-status--watch { background: var(--warning-bg); color: var(--warning); }
.programme-status--attention { background: var(--danger-bg); color: var(--danger); }
.programme-status--muted { background: var(--bg-primary); color: var(--text-muted); }
.programme-next { display: block; max-width: 15rem; color: var(--text-secondary); font-size: 0.72rem; line-height: 1.4; }
.programme-mobile-list { display: none; }
.programme-mobile-card { display: grid; gap: 0.35rem; padding: 0.7rem 0.8rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); }
.programme-mobile-card header { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.programme-mobile-card__name { color: var(--text-muted); font-size: 0.7rem; }
.programme-mobile-card__grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.45rem; }
.programme-mobile-card__grid div { display: grid; gap: 0.1rem; }
.programme-mobile-card__grid span { color: var(--text-muted); font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.programme-mobile-card__grid strong { color: var(--text-primary); font-size: 0.86rem; }
.programme-mobile-card__grid small { color: var(--text-muted); font-size: 0.64rem; line-height: 1.3; }
.programme-quality { border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-secondary); color: var(--text-muted); font-size: 0.72rem; }
.programme-quality summary { padding: 0.6rem 0.9rem; cursor: pointer; color: var(--text-primary); font-size: 0.74rem; font-weight: 600; }
.programme-quality ul { margin: 0; padding: 0 1.2rem 0.7rem 2rem; display: grid; gap: 0.2rem; }
.programme--compact { gap: 0.35rem; padding: 0.75rem 0.9rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-secondary); }
.programme-compact-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.programme--compact h2 { font-size: 1rem; }
.programme-compact-metrics { display: flex; flex-wrap: wrap; gap: 0.35rem 1rem; color: var(--text-muted); font-size: 0.72rem; }
.programme-compact-metrics strong { color: var(--text-primary); }
.programme-compact-link { color: var(--accent); font-size: 0.74rem; font-weight: 600; text-decoration: none; }
.programme-compact-link:hover { text-decoration: underline; }
.programme-compact-action { margin: 0; color: var(--text-secondary); font-size: 0.72rem; }
.programme-compact-action strong { color: var(--text-primary); }
@media (max-width: 820px) {
  .programme-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .programme-head { flex-direction: column; }
  .programme-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .programme-table-wrap { display: none; }
  .programme-mobile-list { display: grid; gap: 0.5rem; }
  .programme-compact-row { align-items: flex-start; }
  .programme-compact-metrics { gap: 0.2rem 0.8rem; }
}
@media (max-width: 360px) {
  .programme-strip { grid-template-columns: 1fr; }
}
</style>
