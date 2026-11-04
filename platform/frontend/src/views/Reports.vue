<template>
  <div class="reports-page">
    <header class="reports-head">
      <div>
        <p class="reports-head__eyebrow">V2 analytics</p>
        <h1>Learning reports</h1>
        <p>Cross-course performance, learning, and confidence signals for teaching review.</p>
      </div>
      <div class="reports-head__actions">
        <button
          type="button"
          class="btn btn--outline btn--sm"
          :disabled="!rows.length"
          @click="exportCsv"
        >
          Export CSV
        </button>
        <button
          type="button"
          class="btn btn--outline btn--sm"
          :disabled="!rows.length || exportingPdf"
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

      <div v-if="!rows.length" class="reports-empty">
        No active courses yet. Create a course to start collecting analytics.
      </div>

      <div v-else class="reports-table-wrap">
        <table class="reports-table">
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
                <strong>{{ row.summary.completion_rate }}%</strong>
                <small>{{ row.summary.completed_learners }} completed</small>
              </td>
              <td>{{ row.summary.abandonment_rate }}%</td>
              <td>
                {{ row.summary.learning_reported ?? '—' }}<small v-if="row.summary.learning_reported !== null">/5</small>
              </td>
              <td>
                <template v-if="row.summary.reaction_count">
                  <strong>{{ row.summary.positive_rate }}%</strong>
                  <small>{{ row.summary.likes }} like{{ row.summary.likes === 1 ? '' : 's' }} · {{ row.summary.dislikes }} dislike{{ row.summary.dislikes === 1 ? '' : 's' }}</small>
                </template>
                <span v-else>—</span>
              </td>
              <td>
                {{ row.summary.confidence_gain !== null ? `${row.summary.confidence_gain > 0 ? '+' : ''}${row.summary.confidence_gain}` : '—' }}
              </td>
              <td>{{ row.summary.pulse_responses }}</td>
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

const data = ref(null)
const loading = ref(true)
const error = ref('')
const exportingPdf = ref(false)

const rows = computed(() => data.value?.courses || [])
const totals = computed(() => data.value?.totals || {})

const ragLabel = (rag) => ({ red: 'Red', amber: 'Amber', green: 'Green' }[rag] || 'No signal')

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

const exportCsv = () => {
  const header = ['Course code', 'Course', 'RAG', 'Learners', 'Learning hours', 'Completion %', 'Abandonment %', 'Learning reported', 'Likes', 'Dislikes', 'Positive feedback %', 'Confidence gain', 'Pulse responses']
  const lines = rows.value.map((row) => [
    row.course.code,
    row.course.name,
    ragLabel(row.summary.rag),
    row.summary.enrolled_learners,
    row.summary.total_learning_hours ?? 0,
    row.summary.completion_rate,
    row.summary.abandonment_rate,
    row.summary.learning_reported ?? '',
    row.summary.likes ?? 0,
    row.summary.dislikes ?? 0,
    row.summary.positive_rate ?? 0,
    row.summary.confidence_gain ?? '',
    row.summary.pulse_responses,
  ])
  const csv = [header, ...lines]
    .map((line) => line.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(','))
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
}

const exportPdf = async () => {
  exportingPdf.value = true
  error.value = ''
  try {
    const response = await axios.get('/analytics/reports/export.pdf', {
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
  gap: 0.5rem;
}

.reports-head__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent);
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.reports-head h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.7rem, 4vw, 2.3rem);
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
  color: var(--text-muted);
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
  color: var(--accent);
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

.reports-rag--red { background: color-mix(in srgb, var(--danger) 14%, transparent); color: var(--danger); }
.reports-rag--amber { background: color-mix(in srgb, var(--warning) 16%, transparent); color: var(--warning); }
.reports-rag--green { background: color-mix(in srgb, var(--success) 14%, transparent); color: var(--success); }

.reports-open {
  color: var(--accent);
  font-size: 0.65rem;
  font-weight: 700;
  text-decoration: none;
}

.reports-open:hover {
  text-decoration: underline;
}

.reports-note {
  margin: 0.8rem 0 0;
  color: var(--text-muted);
  font-size: 0.64rem;
}

@media (max-width: 720px) {
  .reports-page { padding: 1rem; }
  .reports-head { flex-direction: column; }
}
</style>
