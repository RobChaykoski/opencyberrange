<template>
  <div class="reports-page">
    <header class="reports-head">
      <div>
        <p class="reports-head__eyebrow">SWOCTS Cyber Range analytics</p>
        <h1>Reports &amp; Analytics</h1>
        <p>Cross-course performance, learning, and confidence signals for teaching review.</p>
      </div>
      <div class="reports-head__actions">
        <label class="reports-reason">
          <span>Reason for export (required)</span>
          <input
            v-model="exportReason"
            type="text"
            maxlength="500"
            placeholder="e.g. end-of-term teaching review"
          />
        </label>
        <button
          type="button"
          class="btn btn--outline btn--sm"
          :disabled="!rows.length || exportReason.trim().length < 5"
          @click="exportCsv"
        >
          Export CSV
        </button>
        <button
          type="button"
          class="btn btn--outline btn--sm"
          :disabled="!rows.length || exportingPdf || exportReason.trim().length < 5"
          @click="exportPdf"
        >
          {{ exportingPdf ? 'Preparing PDF...' : 'Export PDF' }}
        </button>
      </div>
    </header>

    <p v-if="loading" class="reports-state">Loading course reports...</p>
    <p v-else-if="error" class="reports-state reports-state--error" role="alert">{{ error }}</p>

    <template v-else>
      <div class="reports-summary">
        <article class="reports-stat">
          <span>Courses</span>
          <strong>{{ totals.courses || 0 }}</strong>
        </article>
        <article class="reports-stat">
          <span>Learners</span>
          <strong>{{ totals.enrolled_learners || 0 }}</strong>
        </article>
        <article class="reports-stat">
          <span>Learning hours</span>
          <strong>{{ totals.total_learning_hours || 0 }}</strong>
        </article>
        <article class="reports-stat">
          <span>Pulse responses</span>
          <strong>{{ totals.pulse_responses || 0 }}</strong>
        </article>
        <article class="reports-stat">
          <span>Exercise feedback</span>
          <strong>{{ totals.positive_rate || 0 }}<small>% positive</small></strong>
        </article>
        <article class="reports-stat reports-stat--rag">
          <span>Signals</span>
          <div class="rag-counts">
            <b class="rag-dot rag-dot--red">{{ totals.rag_counts?.red || 0 }}</b>
            <b class="rag-dot rag-dot--amber">{{ totals.rag_counts?.amber || 0 }}</b>
            <b class="rag-dot rag-dot--green">{{ totals.rag_counts?.green || 0 }}</b>
          </div>
        </article>
      </div>

      <p
        v-if="totals.suppressed_courses || totals.no_evidence_courses"
        class="reports-cohort-note"
      >
        <strong>Small-cohort protection is active.</strong>
        {{ totals.suppressed_courses || 0 }} course{{ (totals.suppressed_courses || 0) === 1 ? '' : 's' }}
        suppressed below the {{ totals.minimum_cohort_size || 5 }}-learner minimum;
        {{ totals.no_evidence_courses || 0 }} course{{ (totals.no_evidence_courses || 0) === 1 ? '' : 's' }}
        with no evidence yet.
      </p>

      <div v-if="data.trending_topics?.length" class="trending-panel">
        <div class="trending-panel__head">
          <div>
            <h2>Trending topics</h2>
            <p>What learners asked to cover next in their pulse responses.</p>
          </div>
          <span>{{ totals.pulse_responses || 0 }} responses</span>
        </div>
        <div class="trending-topics">
          <span
            v-for="(topic, index) in data.trending_topics"
            :key="topic.key"
            class="trending-topic"
            :class="{ 'trending-topic--top': index === 0 }"
          >
            <strong>{{ topic.label }}</strong>
            <small>{{ topic.count }} {{ topic.count === 1 ? 'request' : 'requests' }}</small>
          </span>
        </div>
      </div>

      <section
        v-if="skillTree && skillTree.dimensions?.length && skillTree.assigned_total"
        class="skill-panel"
        aria-labelledby="skill-tree-title"
      >
        <div class="skill-panel__head">
          <div>
            <p class="skill-panel__eyebrow">Skill tree</p>
            <h2 id="skill-tree-title">Exercise coverage by skill branch</h2>
            <p>
              How {{ skillScopeLabel }} spreads across the six Skill DNA branches.
              The outer shape is the assigned curriculum; the inner shape is what
              learners completed.
            </p>
          </div>
          <label class="skill-panel__scope">
            <span>Scope</span>
            <select v-model="selectedCourseId">
              <option value="all">All courses</option>
              <option
                v-for="row in rows"
                :key="row.course.id"
                :value="String(row.course.id)"
              >
                {{ row.course.code }} · {{ row.course.name }}
              </option>
            </select>
          </label>
        </div>

        <div class="skill-panel__body">
          <div class="skill-chart">
            <svg
              class="skill-radar"
              viewBox="0 0 360 320"
              role="img"
              :aria-label="skillAriaLabel"
            >
              <polygon
                v-for="(ring, index) in radarRings"
                :key="`ring-${index}`"
                :points="ring"
                class="skill-radar__grid"
              />
              <line
                v-for="(axis, index) in radarAxes"
                :key="`axis-${index}`"
                :x1="radarCenter.x"
                :y1="radarCenter.y"
                :x2="axis.x"
                :y2="axis.y"
                class="skill-radar__axis"
              />
              <polygon
                :points="assignedPolygon"
                class="skill-radar__area skill-radar__area--assigned"
              />
              <polygon
                :points="completedPolygon"
                class="skill-radar__area skill-radar__area--completed"
              />
              <circle
                v-for="point in assignedPoints"
                :key="`assigned-${point.key}`"
                :cx="point.x"
                :cy="point.y"
                r="3.4"
                class="skill-radar__dot skill-radar__dot--assigned"
              />
              <circle
                v-for="point in completedPoints"
                :key="`completed-${point.key}`"
                :cx="point.x"
                :cy="point.y"
                r="3.4"
                class="skill-radar__dot skill-radar__dot--completed"
              />
              <text
                v-for="label in radarLabels"
                :key="`label-${label.key}`"
                :x="label.x"
                :y="label.y"
                :text-anchor="label.anchor"
                class="skill-radar__label"
              >
                {{ label.label }}
              </text>
            </svg>
            <div class="skill-legend">
              <span class="skill-legend__item skill-legend__item--assigned">
                Assigned <b>{{ skillTree.assigned_total }}</b>
              </span>
              <span class="skill-legend__item skill-legend__item--completed">
                Completed <b>{{ skillTree.completed_total }}</b>
                <small>{{ skillTree.completion_pct }}%</small>
              </span>
            </div>
          </div>

          <div class="skill-table-wrap" tabindex="0" role="region" aria-label="Skill branch evidence table">
            <table class="skill-table">
              <thead>
                <tr>
                  <th scope="col">Branch</th>
                  <th scope="col">Assigned</th>
                  <th scope="col">Share</th>
                  <th scope="col">Completed</th>
                  <th scope="col">Share</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="dimension in skillTree.dimensions" :key="dimension.key">
                  <th scope="row">{{ dimension.label }}</th>
                  <td>{{ dimension.assigned }}</td>
                  <td>{{ dimension.assigned_pct }}%</td>
                  <td>{{ dimension.completed }}</td>
                  <td>{{ dimension.completed_pct }}%</td>
                </tr>
              </tbody>
            </table>
            <p class="skill-panel__note">
              Shares describe the mix of exercises, not learner scores. Completed
              exercises are distinct exercises with at least one completion.
            </p>
          </div>
        </div>
      </section>

      <div v-if="!rows.length" class="reports-empty">
        No active courses yet. Create a course to start collecting analytics.
      </div>

      <div v-else class="reports-table-wrap" tabindex="0" role="region" aria-label="Course reports table">
        <table class="reports-table">
          <caption class="sr-only">
            Cross-course learning report with each course's signal, learners,
            completion, abandonment, learning, feedback, confidence, and pulse counts.
          </caption>
          <thead>
            <tr>
              <th scope="col">Course</th>
              <th scope="col">Signal</th>
              <th scope="col">Learners</th>
              <th scope="col">Completion</th>
              <th scope="col">Abandonment</th>
              <th scope="col">Learning</th>
              <th scope="col">Feedback</th>
              <th scope="col">Confidence</th>
              <th scope="col">Pulse</th>
              <th scope="col"><span class="sr-only">Open</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.course.id">
              <td>
                <router-link :to="`/courses/${row.course.id}?tab=analytics`" class="reports-course">
                  <strong>{{ row.course.code }}</strong>
                  <span>{{ row.course.name }}</span>
                </router-link>
              </td>
              <td>
                <span class="reports-rag" :class="`reports-rag--${row.summary.rag}`">
                  {{ ragLabel(row.summary.rag) }}
                </span>
                <small v-if="row.summary.rag_reasons?.length">{{ row.summary.rag_reasons[0] }}</small>
              </td>
              <td>{{ row.summary.enrolled_learners }}</td>
              <td>
                <template v-if="row.cohort_state === 'available'">
                  <strong>{{ row.summary.completion_rate }}%</strong>
                  <small>{{ row.summary.completed_learners }} completed</small>
                </template>
                <span v-else>—</span>
              </td>
              <td>
                <template v-if="row.cohort_state === 'available'">
                  {{ row.summary.abandonment_rate }}%
                </template>
                <span v-else>—</span>
              </td>
              <td>
                <template v-if="row.cohort_state === 'available'">
                  {{ row.summary.learning_reported ?? '—' }}<small v-if="row.summary.learning_reported !== null">/5</small>
                </template>
                <span v-else>—</span>
              </td>
              <td>
                <template v-if="row.cohort_state === 'available'">
                  <template v-if="row.summary.reaction_count">
                    <strong>{{ row.summary.positive_rate }}%</strong>
                    <small>{{ row.summary.likes }} like{{ row.summary.likes === 1 ? '' : 's' }} · {{ row.summary.dislikes }} dislike{{ row.summary.dislikes === 1 ? '' : 's' }}</small>
                  </template>
                  <span v-else>—</span>
                </template>
                <span v-else>—</span>
              </td>
              <td>
                <template v-if="row.cohort_state === 'available'">
                  {{ row.summary.confidence_gain !== null ? `${row.summary.confidence_gain > 0 ? '+' : ''}${row.summary.confidence_gain}` : '—' }}
                </template>
                <span v-else>—</span>
              </td>
              <td>
                <template v-if="row.cohort_state === 'available'">
                  {{ row.summary.pulse_responses }}
                </template>
                <span v-else>—</span>
              </td>
              <td>
                <router-link :to="`/courses/${row.course.id}?tab=analytics`" class="reports-open">
                  Open
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p class="reports-note">
        RAG is a teaching signal, not a learner label. Learning is self-reported;
        exercise reactions are optional and shown as totals, never by learner name;
        confidence gain is a performance-growth proxy, not a psychological score.
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'
import { csvRow } from '../utils/csv'

const data = ref(null)
const loading = ref(true)
const error = ref('')
const exportingPdf = ref(false)
const exportReason = ref('')

const rows = computed(() => data.value?.courses || [])
const totals = computed(() => data.value?.totals || {})

const ragLabel = (rag) => ({
  red: 'Red',
  amber: 'Amber',
  green: 'Green',
  suppressed: 'Suppressed',
  no_evidence: 'No evidence',
  insufficient_evidence: 'No evidence',
}[rag] || 'No signal')

const RADAR_CENTER = { x: 180, y: 155 }
const RADAR_RADIUS = 112
const RADAR_LABEL_RADIUS = 126

const selectedCourseId = ref('all')
const radarCenter = RADAR_CENTER

const skillTree = computed(() => {
  if (selectedCourseId.value === 'all') return totals.value?.skill_tree || null
  const row = rows.value.find(
    (item) => String(item.course.id) === selectedCourseId.value
  )
  return row?.skill_tree || null
})

const skillScopeLabel = computed(() => {
  if (selectedCourseId.value === 'all') return 'all selected courses'
  const row = rows.value.find(
    (item) => String(item.course.id) === selectedCourseId.value
  )
  return row ? `${row.course.code} · ${row.course.name}` : 'this course'
})

const skillDimensions = computed(() => skillTree.value?.dimensions || [])

const radarAnchor = (x) => {
  if (x < RADAR_CENTER.x - 6) return 'end'
  if (x > RADAR_CENTER.x + 6) return 'start'
  return 'middle'
}

const radarPoint = (index, value, radius = RADAR_RADIUS) => {
  const count = skillDimensions.value.length || 5
  const angle = -Math.PI / 2 + (2 * Math.PI * index) / count
  const clamped = Math.max(0, Math.min(100, Number(value) || 0))
  const distance = radius * (clamped / 100)
  return {
    x: Number((RADAR_CENTER.x + Math.cos(angle) * distance).toFixed(2)),
    y: Number((RADAR_CENTER.y + Math.sin(angle) * distance).toFixed(2)),
  }
}

const radarPolygon = (values) => {
  const count = skillDimensions.value.length || 5
  return Array.from({ length: count }, (_, index) => {
    const point = radarPoint(index, values[index] ?? 0)
    return `${point.x},${point.y}`
  }).join(' ')
}

const radarRings = computed(() =>
  [25, 50, 75, 100].map((level) =>
    radarPolygon(Array(skillDimensions.value.length || 5).fill(level))
  )
)

const radarAxes = computed(() =>
  Array.from(
    { length: skillDimensions.value.length || 5 },
    (_, index) => radarPoint(index, 100)
  )
)

const assignedValues = computed(() =>
  skillDimensions.value.map((dimension) => Number(dimension.assigned_pct) || 0)
)
const completedValues = computed(() =>
  skillDimensions.value.map((dimension) => Number(dimension.completed_pct) || 0)
)
const assignedPolygon = computed(() => radarPolygon(assignedValues.value))
const completedPolygon = computed(() => radarPolygon(completedValues.value))
const assignedPoints = computed(() =>
  skillDimensions.value.map((dimension, index) => ({
    key: dimension.key,
    ...radarPoint(index, assignedValues.value[index]),
  }))
)
const completedPoints = computed(() =>
  skillDimensions.value.map((dimension, index) => ({
    key: dimension.key,
    ...radarPoint(index, completedValues.value[index]),
  }))
)
const radarLabels = computed(() =>
  skillDimensions.value.map((dimension, index) => {
    const point = radarPoint(index, 100, RADAR_LABEL_RADIUS)
    return {
      key: dimension.key,
      label: dimension.label,
      x: point.x,
      y: point.y,
      anchor: radarAnchor(point.x),
    }
  })
)
const skillAriaLabel = computed(() =>
  `Skill tree coverage for ${skillScopeLabel.value}. ` +
  skillDimensions.value
    .map(
      (dimension) =>
        `${dimension.label}: ${dimension.assigned_pct}% assigned, ${dimension.completed_pct}% completed`
    )
    .join('. ')
)

const skillMix = (tree, field) =>
  (tree?.dimensions || [])
    .map((dimension) => `${dimension.label} ${dimension[field]}%`)
    .join('; ')


const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/analytics/reports/overview')
    data.value = response.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load reports.'
  } finally {
    loading.value = false
  }
}

const exportCsv = async () => {
  const reason = exportReason.value.trim()
  error.value = ''
  if (reason.length < 5) {
    error.value = 'Enter a reason of at least 5 characters before exporting.'
    return
  }
  try {
    await axios.post('/analytics/reports/export-audit', { format: 'csv', reason })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not record the export reason.'
    return
  }

  const header = ['Course code', 'Course', 'RAG', 'Cohort state', 'Learners', 'Learning hours', 'Completion %', 'Abandonment %', 'Learning reported', 'Likes', 'Dislikes', 'Positive feedback %', 'Confidence gain', 'Pulse responses', 'Skill tree assigned %', 'Skill tree completed %']
  const lines = rows.value.map((row) => {
    const available = row.cohort_state === 'available'
    const metric = (value, fallback = '') => available ? (value ?? fallback) : ''
    return [
      row.course.code,
      row.course.name,
      ragLabel(row.summary.rag),
      row.cohort_state,
      row.summary.enrolled_learners,
      metric(row.summary.total_learning_hours, 0),
      metric(row.summary.completion_rate),
      metric(row.summary.abandonment_rate),
      metric(row.summary.learning_reported),
      metric(row.summary.likes, 0),
      metric(row.summary.dislikes, 0),
      metric(row.summary.positive_rate, 0),
      metric(row.summary.confidence_gain),
      metric(row.summary.pulse_responses),
      available ? skillMix(row.skill_tree, 'assigned_pct') : '',
      available ? skillMix(row.skill_tree, 'completed_pct') : '',
    ]
  })
  const csv = [header, ...lines]
    .map((line) => csvRow(line))
    .join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `learning-reports-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
  exportReason.value = ''
}

const exportPdf = async () => {
  const reason = exportReason.value.trim()
  error.value = ''
  if (reason.length < 5) {
    error.value = 'Enter a reason of at least 5 characters before exporting.'
    return
  }
  exportingPdf.value = true
  try {
    const response = await axios.get('/analytics/reports/export.pdf', {
      params: { reason },
      responseType: 'blob',
    })
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `learning-reports-${new Date().toISOString().slice(0, 10)}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    exportReason.value = ''
  } catch {
    error.value = 'Could not prepare the PDF report. Please try again.'
  } finally {
    exportingPdf.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.reports-page {
  max-width: 1240px;
  margin: 0 auto;
  padding: 2rem;
}

.reports-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.reports-head__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.5rem;
}

.reports-reason {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.7rem;
  color: var(--text-muted);
  min-width: 220px;
}

.reports-reason input {
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.8rem;
}

.reports-head__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent-text);
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.reports-head h1 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
}

.reports-head p:last-child {
  max-width: 64ch;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.reports-state,
.reports-empty {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.82rem;
}

.reports-state--error {
  color: var(--danger);
}

.reports-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.6rem;
  margin-bottom: 1rem;
}

.reports-stat {
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.reports-stat > span {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.reports-stat strong {
  display: block;
  margin-top: 0.2rem;
  color: var(--text-primary);
  font-size: 1.35rem;
}

.rag-counts {
  display: flex;
  gap: 0.35rem;
  margin-top: 0.25rem;
}

.rag-dot {
  display: inline-grid;
  place-items: center;
  min-width: 28px;
  height: 26px;
  border-radius: 8px;
  font-size: 0.75rem;
}

.rag-dot--red { background: color-mix(in srgb, var(--danger) 14%, transparent); color: var(--danger); }
.rag-dot--amber { background: color-mix(in srgb, var(--warning) 16%, transparent); color: var(--warning); }
.rag-dot--green { background: color-mix(in srgb, var(--success) 14%, transparent); color: var(--success); }

.reports-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.trending-panel {
  margin-bottom: 1rem;
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.trending-panel__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.6rem;
}

.trending-panel h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.trending-panel p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.trending-panel__head > span {
  color: var(--text-muted);
  font-size: 0.64rem;
}

.trending-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.trending-topic {
  display: inline-flex;
  align-items: baseline;
  gap: 0.35rem;
  padding: 0.25rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
}

.trending-topic strong {
  color: var(--text-secondary);
  font-size: 0.68rem;
}

.trending-topic small {
  color: var(--text-muted);
  font-size: 0.58rem;
}

.trending-topic--top {
  border-color: color-mix(in srgb, var(--accent) 45%, var(--border-color));
  background: var(--accent-bg);
}

.trending-topic--top strong {
  color: var(--accent);
}

.skill-panel {
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  min-width: 0;
  max-width: 100%;
}

.skill-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.skill-panel__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent);
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.skill-panel h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.skill-panel__head p {
  max-width: 68ch;
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.68rem;
  line-height: 1.5;
}

.skill-panel__scope {
  display: flex;
  flex-direction: column;
  gap: 0.28rem;
  flex: 0 0 auto;
  min-width: 14rem;
}

.skill-panel__scope span {
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.skill-panel__scope select {
  width: 100%;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.72rem;
}

.skill-panel__body {
  display: grid;
  grid-template-columns: minmax(260px, 340px) minmax(0, 1fr);
  gap: 1.25rem;
  align-items: center;
  margin-top: 0.8rem;
  min-width: 0;
}

.skill-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}

.skill-radar {
  width: 100%;
  max-width: 340px;
  height: auto;
  overflow: visible;
}

.skill-radar__grid,
.skill-radar__axis {
  fill: none;
  stroke: var(--border-color);
  stroke-width: 1;
}

.skill-radar__area {
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}

.skill-radar__area--assigned {
  fill: color-mix(in srgb, var(--accent) 16%, transparent);
  stroke: var(--accent);
}

.skill-radar__area--completed {
  fill: color-mix(in srgb, var(--success) 15%, transparent);
  stroke: var(--success);
  stroke-dasharray: 4 3;
}

.skill-radar__dot--assigned { fill: var(--accent); }
.skill-radar__dot--completed { fill: var(--success); }

.skill-radar__label {
  fill: var(--text-secondary);
  font-size: 11px;
  font-weight: 700;
}

.skill-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-top: 0.35rem;
  color: var(--text-secondary);
  font-size: 0.68rem;
}

.skill-legend__item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.skill-legend__item::before {
  content: '';
  width: 9px;
  height: 9px;
  border-radius: 2px;
}

.skill-legend__item--assigned::before { background: var(--accent); }
.skill-legend__item--completed::before { background: var(--success); }
.skill-legend b { color: var(--text-primary); }
.skill-legend small { color: var(--text-muted); }

.skill-table-wrap { min-width: 0; max-width: 100%; overflow-x: auto; }

.skill-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.72rem;
}

.skill-table th,
.skill-table td {
  padding: 0.45rem 0.55rem;
  border-bottom: 1px solid var(--border-color);
  text-align: right;
}

.skill-table thead th {
  color: var(--text-muted);
  font-size: 0.56rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.skill-table th:first-child,
.skill-table thead th:first-child {
  text-align: left;
}

.skill-table tbody th {
  color: var(--text-primary);
  font-weight: 700;
  text-align: left;
}

.skill-table tbody tr:last-child th,
.skill-table tbody tr:last-child td {
  border-bottom: 0;
}

.skill-panel__note {
  margin: 0.55rem 0 0;
  color: var(--text-muted);
  font-size: 0.62rem;
  line-height: 1.45;
}

.reports-table {
  width: 100%;
  min-width: 980px;
  border-collapse: collapse;
  font-size: 0.74rem;
}

.reports-table th,
.reports-table td {
  padding: 0.65rem 0.7rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  vertical-align: top;
}

.reports-table th {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.58rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.reports-table tbody tr:last-child td {
  border-bottom: 0;
}

.reports-course {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  text-decoration: none;
}

.reports-course strong {
  color: var(--accent-text);
  font-size: 0.7rem;
}

.reports-course span {
  color: var(--text-primary);
  font-weight: 600;
}

.reports-table td small {
  display: block;
  margin-top: 0.12rem;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.reports-rag {
  display: inline-block;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  font-size: 0.58rem;
  font-weight: 800;
  text-transform: uppercase;
}

.reports-rag--red { background: color-mix(in srgb, var(--danger) 14%, transparent); color: var(--badge-red); }
.reports-rag--amber { background: color-mix(in srgb, var(--warning) 16%, transparent); color: var(--badge-amber); }
.reports-rag--green { background: color-mix(in srgb, var(--success) 14%, transparent); color: var(--badge-green); }

.reports-open {
  color: var(--accent-text);
  font-size: 0.65rem;
  font-weight: 700;
  text-decoration: none;
}

.reports-open:hover {
  text-decoration: underline;
}

.reports-cohort-note {
  margin: 0.9rem 0 0;
  padding: 0.65rem 0.8rem;
  border: 1px solid color-mix(in srgb, var(--warning) 30%, transparent);
  border-radius: 8px;
  background: color-mix(in srgb, var(--warning) 8%, transparent);
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.5;
}

.reports-rag--suppressed,
.reports-rag--no_evidence,
.reports-rag--insufficient_evidence {
  background: color-mix(in srgb, var(--text-muted) 12%, transparent);
  color: var(--text-muted);
}

.reports-note {
  margin: 0.8rem 0 0;
  color: var(--text-muted);
  font-size: 0.64rem;
}

@media (max-width: 900px) {
  .skill-panel__body {
    grid-template-columns: 1fr;
  }

  .skill-chart {
    justify-self: center;
    width: 100%;
  }
}

@media (max-width: 720px) {
  .reports-page { padding: 1rem; }
  .reports-head { flex-direction: column; }
  .skill-panel__head { flex-direction: column; }
  .skill-panel__scope { width: 100%; }
}
</style>
