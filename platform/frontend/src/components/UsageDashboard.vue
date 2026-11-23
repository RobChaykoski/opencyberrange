<template>
  <div class="usage-page">
    <header class="usage-head">
      <div>
        <p class="usage-head__eyebrow">
          {{ admin ? 'Admin usage detail' : 'Public usage tracker' }}
        </p>
        <h1>{{ admin ? 'Cyber Range usage' : 'Usage, in the open' }}</h1>
        <p class="usage-head__lead">
          Registrations, conference QR scans, and lab completions from the
          SWOCTS Cyber Range. Aggregate data only; small groups are suppressed.
        </p>
      </div>
      <div class="usage-head__meta">
        <span v-if="data">Data to {{ formatDate(data.generated_at) }}</span>
        <router-link v-if="admin" to="/usage" class="btn btn--secondary btn--sm">
          Open public page
        </router-link>
      </div>
    </header>

    <div class="usage-toolbar">
      <div class="usage-window" role="group" aria-label="Reporting window">
        <button
          v-for="option in windowOptions"
          :key="option"
          type="button"
          class="btn btn--sm"
          :class="days === option ? 'btn--primary' : 'btn--secondary'"
          :aria-pressed="days === option"
          @click="days = option"
        >
          {{ option }} days
        </button>
      </div>
      <div class="usage-toolbar__links">
        <a
          v-if="!admin"
          :href="`/api/usage/public?days=${days}`"
          target="_blank"
          rel="noopener"
          class="usage-link"
        >
          JSON API
        </a>
        <a
          v-if="!admin"
          :href="`/api/usage/public.csv?days=${days}`"
          class="usage-link"
        >
          Daily CSV
        </a>
        <button
          v-if="admin"
          type="button"
          class="btn btn--secondary btn--sm"
          :disabled="exporting"
          @click="downloadLabsCsv"
        >
          {{ exporting ? 'Preparing CSV...' : 'Download labs CSV' }}
        </button>
      </div>
    </div>

    <p v-if="loading" class="usage-state" role="status">Loading usage...</p>
    <div v-else-if="error" class="usage-state" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary btn--sm" @click="load">
        Try again
      </button>
    </div>

    <template v-else-if="data">
      <section class="usage-hero" aria-labelledby="usage-hero-title">
        <div class="usage-hero__main">
          <p class="usage-hero__eyebrow">Last {{ data.window_days }} days</p>
          <h2 id="usage-hero-title" class="usage-hero__value">
            {{ formatNumber(totals.completions.value) }}
          </h2>
          <p class="usage-hero__caption">lab completions, tracked in the open</p>
          <p class="usage-hero__delta" :class="deltaClass(totals.completions.delta_pct)">
            {{ formatDelta(totals.completions.delta_pct) }} vs the previous
            {{ data.window_days }} days
          </p>
        </div>
        <div class="usage-hero__stats">
          <article
            v-for="card in heroCards"
            :key="card.key"
            class="usage-stat"
          >
            <p class="usage-stat__label">{{ card.label }}</p>
            <p class="usage-stat__value">{{ formatNumber(card.value) }}</p>
            <p class="usage-stat__delta" :class="deltaClass(card.delta)">
              {{ formatDelta(card.delta) }}
            </p>
          </article>
        </div>
      </section>

      <section class="usage-card" aria-labelledby="usage-daily-title">
        <div class="usage-card__head">
          <div>
            <h2 id="usage-daily-title">Daily activity</h2>
            <p class="usage-card__meta">
              Registrations, QR scans, and lab completions per day.
            </p>
          </div>
        </div>
        <EChart
          :option="dailyOption"
          height="300px"
          aria-label="Daily registrations, QR scans, and lab completions"
        />
        <details class="usage-chart-table">
          <summary>View daily data as a table</summary>
          <div class="usage-table-wrap">
            <table class="usage-table">
              <caption class="sr-only">Daily usage</caption>
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Registrations</th>
                  <th scope="col">QR scans</th>
                  <th scope="col">Completions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in data.daily" :key="row.date">
                  <th scope="row">{{ row.date }}</th>
                  <td>{{ row.registrations }}</td>
                  <td>{{ row.qr_scans }}</td>
                  <td>{{ row.completions }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>
      </section>

      <div class="usage-columns">
        <section class="usage-card" aria-labelledby="usage-week-title">
          <div class="usage-card__head">
            <div>
              <h2 id="usage-week-title">This week</h2>
              <p class="usage-card__meta">Last 7 days against the 7 before.</p>
            </div>
          </div>
          <div class="usage-week">
            <article v-for="item in weekCards" :key="item.key" class="usage-week__item">
              <p class="usage-stat__label">{{ item.label }}</p>
              <p class="usage-week__value">{{ formatNumber(item.current) }}</p>
              <p class="usage-stat__delta" :class="deltaClass(item.delta_pct)">
                {{ formatDelta(item.delta_pct) }}
              </p>
            </article>
          </div>
        </section>

        <section class="usage-card" aria-labelledby="usage-movers-title">
          <div class="usage-card__head">
            <div>
              <h2 id="usage-movers-title">Top movers</h2>
              <p class="usage-card__meta">Largest week-over-week change.</p>
            </div>
          </div>
          <div class="usage-movers">
            <div>
              <p class="usage-movers__label">Sources</p>
              <ul v-if="data.movers.sources.length" class="usage-movers__list">
                <li v-for="item in data.movers.sources" :key="item.key">
                  <span>{{ item.label }}</span>
                  <strong :class="deltaClass(item.delta_pct)">
                    {{ formatDelta(item.delta_pct) }}
                  </strong>
                </li>
              </ul>
              <p v-else class="usage-card__meta">No source activity yet.</p>
            </div>
            <div>
              <p class="usage-movers__label">Labs</p>
              <ul v-if="data.movers.labs.length" class="usage-movers__list">
                <li v-for="item in data.movers.labs" :key="item.name">
                  <span>{{ item.name }}</span>
                  <strong :class="deltaClass(item.delta_pct)">
                    {{ formatDelta(item.delta_pct) }}
                  </strong>
                </li>
              </ul>
              <p v-else class="usage-card__meta">No lab movement yet.</p>
            </div>
          </div>
        </section>
      </div>

      <section class="usage-card" aria-labelledby="usage-sources-title">
        <div class="usage-card__head">
          <div>
            <h2 id="usage-sources-title">Registration sources</h2>
            <p class="usage-card__meta">
              Where accounts came from, with QR scans and completions from each
              source.
            </p>
          </div>
        </div>
        <div class="usage-table-wrap">
          <table class="usage-table">
            <caption class="sr-only">Registration sources</caption>
            <thead>
              <tr>
                <th scope="col">Source</th>
                <th scope="col">Registrations</th>
                <th scope="col">Share</th>
                <th scope="col">QR scans</th>
                <th scope="col">Completions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.sources" :key="row.key">
                <th scope="row">{{ row.label }}</th>
                <td>
                  <template v-if="row.registrations_suppressed">
                    &lt;{{ data.minimum_cohort_size }}
                  </template>
                  <template v-else>{{ formatNumber(row.registrations) }}</template>
                </td>
                <td>
                  <template v-if="row.share === null">&mdash;</template>
                  <template v-else>{{ Math.round(row.share * 100) }}%</template>
                </td>
                <td>{{ formatNumber(row.scans) }}</td>
                <td>{{ formatNumber(row.completions) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section
        v-if="data.campaigns.length"
        class="usage-card"
        aria-labelledby="usage-campaigns-title"
      >
        <div class="usage-card__head">
          <div>
            <h2 id="usage-campaigns-title">Campaigns</h2>
            <p class="usage-card__meta">
              Conference and placement QR codes, with scan-to-registration
              conversion.
            </p>
          </div>
        </div>
        <div class="usage-table-wrap">
          <table class="usage-table">
            <caption class="sr-only">QR campaigns</caption>
            <thead>
              <tr>
                <th scope="col">Campaign</th>
                <th scope="col">Scans</th>
                <th scope="col">Registrations</th>
                <th scope="col">Conversion</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.campaigns" :key="row.campaign">
                <th scope="row">{{ row.campaign }}</th>
                <td>{{ formatNumber(row.scans) }}</td>
                <td>
                  <template v-if="row.registrations_suppressed">
                    &lt;{{ data.minimum_cohort_size }}
                  </template>
                  <template v-else>{{ formatNumber(row.registrations) }}</template>
                </td>
                <td>
                  {{ row.conversion === null ? '—' : `${Math.round(row.conversion * 100)}%` }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="usage-card" aria-labelledby="usage-labs-title">
        <div class="usage-card__head">
          <div>
            <h2 id="usage-labs-title">Lab completions</h2>
            <p class="usage-card__meta">
              {{ formatNumber(data.labs.total) }} labs with activity. Median time,
              attempts, and completion rates are calculated from the selected
              window.
            </p>
          </div>
        </div>

        <div class="usage-lab-toolbar">
          <label class="usage-field">
            <span>Search</span>
            <input
              v-model.trim="labSearch"
              type="search"
              class="form-input"
              placeholder="Lab name, slug, or category"
            />
          </label>
          <label class="usage-field">
            <span>Sort</span>
            <select v-model="labSort" class="form-input">
              <option value="completions">Completions</option>
              <option value="learners">Learners</option>
              <option value="median_minutes">Median time</option>
              <option value="first_attempt_rate">First-attempt success</option>
              <option value="completion_rate">Completion rate</option>
              <option value="name">Name</option>
            </select>
          </label>
        </div>

        <div class="usage-table-wrap">
          <table class="usage-table">
            <caption class="sr-only">Lab completion telemetry</caption>
            <thead>
              <tr>
                <th scope="col">Lab</th>
                <th scope="col">Category</th>
                <th scope="col">Completions</th>
                <th scope="col">Learners</th>
                <th scope="col">Median time</th>
                <th scope="col">First attempt</th>
                <th scope="col">Completion rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pagedLabs" :key="row.slug">
                <th scope="row">
                  <span class="usage-lab-name">{{ row.name }}</span>
                  <span class="usage-lab-slug">{{ row.slug }}</span>
                </th>
                <td>{{ labelize(row.category) }}</td>
                <td>{{ formatNumber(row.completions) }}</td>
                <td>
                  <template v-if="row.learners_suppressed">
                    &lt;{{ data.minimum_cohort_size }}
                  </template>
                  <template v-else>{{ formatNumber(row.learners) }}</template>
                </td>
                <td>{{ row.median_minutes === null ? '—' : `${row.median_minutes} min` }}</td>
                <td>{{ row.first_attempt_rate === null ? '—' : `${Math.round(row.first_attempt_rate * 100)}%` }}</td>
                <td>{{ row.completion_rate === null ? '—' : `${Math.round(row.completion_rate * 100)}%` }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="!pagedLabs.length" class="usage-card__meta">
          No labs match this search.
        </p>

        <div v-if="labPageCount > 1" class="usage-pager">
          <button
            type="button"
            class="btn btn--secondary btn--sm"
            :disabled="labPage === 1"
            @click="labPage -= 1"
          >
            Previous
          </button>
          <span>Page {{ labPage }} of {{ labPageCount }}</span>
          <button
            type="button"
            class="btn btn--secondary btn--sm"
            :disabled="labPage === labPageCount"
            @click="labPage += 1"
          >
            Next
          </button>
        </div>
      </section>

      <div class="usage-columns">
        <section class="usage-card" aria-labelledby="usage-recent-title">
          <div class="usage-card__head">
            <div>
              <h2 id="usage-recent-title">Latest activity</h2>
              <p class="usage-card__meta">Aggregate events, without learner identity.</p>
            </div>
          </div>
          <ul v-if="data.recent.length" class="usage-recent">
            <li v-for="(item, index) in data.recent" :key="`${item.at}-${index}`">
              <span class="usage-recent__kind" :class="`usage-recent__kind--${item.kind}`">
                {{ item.kind }}
              </span>
              <span class="usage-recent__label">{{ item.label }}</span>
              <time :datetime="item.at">{{ formatWhen(item.at) }}</time>
            </li>
          </ul>
          <p v-else class="usage-card__meta">No activity yet.</p>
        </section>

        <section v-if="admin" class="usage-card" aria-labelledby="usage-qr-title">
          <div class="usage-card__head">
            <div>
              <h2 id="usage-qr-title">Conference QR</h2>
              <p class="usage-card__meta">
                Tracked registration link for a source and campaign.
              </p>
            </div>
          </div>
          <div class="usage-qr">
            <label class="usage-field">
              <span>Source</span>
              <select v-model="qrSource" class="form-input">
                <option v-for="source in sourceOptions" :key="source" :value="source">
                  {{ sourceLabel(source) }}
                </option>
              </select>
            </label>
            <label class="usage-field">
              <span>Campaign</span>
              <input
                v-model.trim="qrCampaign"
                type="text"
                class="form-input"
                maxlength="100"
                placeholder="e.g. gdg-november-2026"
              />
            </label>
            <button type="button" class="btn btn--primary btn--sm" @click="loadQr">
              Update QR
            </button>
            <div v-if="qrUrl" class="usage-qr__preview">
              <img :src="qrUrl" alt="Registration QR code" width="180" height="180" />
              <a :href="qrUrl" download="registration-qr.png" class="usage-link">
                Download PNG
              </a>
            </div>
            <p v-else class="usage-card__meta">Choose a source and update the code.</p>
          </div>
        </section>
      </div>

      <p class="usage-footnote">
        Aggregate usage only. Learner names, emails, IP addresses, and individual
        progress are never included. Counts below the configured cohort threshold
        are shown as &lt;{{ data.minimum_cohort_size }}.
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import axios from '../api/axios'
import EChart from './EChart.vue'
import {
  ECHART_COLORS,
  categoryAxis,
  chartGrid,
  legendStyle,
  tooltipStyle,
  valueAxis,
} from './charts/echartsTheme'

const props = defineProps({
  admin: { type: Boolean, default: false },
})

const windowOptions = [7, 30, 90]
const days = ref(30)
const loading = ref(true)
const error = ref('')
const data = ref(null)
const exporting = ref(false)
const labSearch = ref('')
const labSort = ref('completions')
const labPage = ref(1)
const labPageSize = 10
const qrSource = ref('gdg')
const qrCampaign = ref('')
const qrUrl = ref('')
const sourceOptions = ['gdg', 'linkedin', 'swocts', 'direct']
const sourceLabels = {
  gdg: 'GDG',
  linkedin: 'LinkedIn',
  swocts: 'SWOCTS',
  direct: 'Direct',
}

const totals = computed(() => data.value?.totals || {
  registrations: { value: 0, previous: 0, delta_pct: 0 },
  qr_scans: { value: 0, previous: 0, delta_pct: 0 },
  completions: { value: 0, previous: 0, delta_pct: 0 },
  active_learners: { value: 0, previous: 0, delta_pct: 0 },
})

const heroCards = computed(() => [
  { key: 'registrations', label: 'Registrations', ...totals.value.registrations, delta: totals.value.registrations.delta_pct },
  { key: 'qr_scans', label: 'QR scans', ...totals.value.qr_scans, delta: totals.value.qr_scans.delta_pct },
  { key: 'active_learners', label: 'Active learners', ...totals.value.active_learners, delta: totals.value.active_learners.delta_pct },
])

const weekCards = computed(() => [
  { key: 'registrations', label: 'Registrations', ...(data.value?.week?.registrations || {}) },
  { key: 'qr_scans', label: 'QR scans', ...(data.value?.week?.qr_scans || {}) },
  { key: 'completions', label: 'Lab completions', ...(data.value?.week?.completions || {}) },
  { key: 'active_learners', label: 'Active learners', ...(data.value?.week?.active_learners || {}) },
])

const dailyOption = computed(() => {
  const rows = data.value?.daily || []
  return {
    animation: false,
    color: [ECHART_COLORS.accent, ECHART_COLORS.success, ECHART_COLORS.warning],
    tooltip: { trigger: 'axis', ...tooltipStyle },
    legend: { ...legendStyle, data: ['Registrations', 'QR scans', 'Completions'] },
    grid: { ...chartGrid, top: 48 },
    xAxis: {
      ...categoryAxis,
      boundaryGap: true,
      data: rows.map((row) => row.date.slice(5)),
      axisLabel: { ...categoryAxis.axisLabel, interval: rows.length > 14 ? 4 : 0 },
    },
    yAxis: valueAxis,
    series: [
      {
        name: 'Registrations',
        type: 'bar',
        barMaxWidth: 8,
        data: rows.map((row) => row.registrations),
        itemStyle: { color: ECHART_COLORS.accent },
      },
      {
        name: 'QR scans',
        type: 'bar',
        barMaxWidth: 8,
        data: rows.map((row) => row.qr_scans),
        itemStyle: { color: ECHART_COLORS.success },
      },
      {
        name: 'Completions',
        type: 'bar',
        barMaxWidth: 8,
        data: rows.map((row) => row.completions),
        itemStyle: { color: ECHART_COLORS.warning },
      },
    ],
  }
})

const filteredLabs = computed(() => {
  const search = labSearch.value.toLowerCase()
  const rows = (data.value?.labs?.items || []).filter((row) => {
    if (!search) return true
    return [row.name, row.slug, row.category]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(search))
  })
  const sorted = [...rows].sort((a, b) => {
    if (labSort.value === 'name') return String(a.name).localeCompare(String(b.name))
    const left = a[labSort.value]
    const right = b[labSort.value]
    if (left === null || left === undefined) return 1
    if (right === null || right === undefined) return -1
    return Number(right) - Number(left)
  })
  return sorted
})
const labPageCount = computed(() =>
  Math.max(1, Math.ceil(filteredLabs.value.length / labPageSize))
)
const pagedLabs = computed(() => {
  const start = (labPage.value - 1) * labPageSize
  return filteredLabs.value.slice(start, start + labPageSize)
})

watch([labSearch, labSort], () => {
  labPage.value = 1
})
watch(labPageCount, (count) => {
  if (labPage.value > count) labPage.value = count
})
watch(days, load)

function formatNumber(value) {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString()
}

function formatDelta(value) {
  if (!value) return '0%'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value}%`
}

function deltaClass(value) {
  if (value > 0) return 'usage-delta--up'
  if (value < 0) return 'usage-delta--down'
  return 'usage-delta--flat'
}

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatWhen(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function labelize(value) {
  return String(value || '')
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function sourceLabel(value) {
  return sourceLabels[value] || labelize(value)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const path = props.admin ? '/usage/admin' : '/usage/public'
    const { data: payload } = await axios.get(path, { params: { days: days.value } })
    data.value = payload
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load usage data.'
  } finally {
    loading.value = false
  }
}

async function downloadLabsCsv() {
  exporting.value = true
  try {
    const response = await axios.get('/usage/admin.csv', {
      params: { days: days.value },
      responseType: 'blob',
    })
    const url = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = `opencyberrange-usage-labs-${days.value}d.csv`
    link.click()
    URL.revokeObjectURL(url)
  } catch {
    error.value = 'Could not export the lab telemetry.'
  } finally {
    exporting.value = false
  }
}

async function loadQr() {
  if (!props.admin) return
  try {
    const response = await axios.get('/usage/admin/qr', {
      params: {
        source: qrSource.value,
        campaign: qrCampaign.value || undefined,
      },
      responseType: 'blob',
    })
    if (qrUrl.value) URL.revokeObjectURL(qrUrl.value)
    qrUrl.value = URL.createObjectURL(response.data)
  } catch {
    qrUrl.value = ''
  }
}

onMounted(async () => {
  await load()
  if (props.admin) await loadQr()
})

onBeforeUnmount(() => {
  if (qrUrl.value) URL.revokeObjectURL(qrUrl.value)
})
</script>

<style scoped>
.usage-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
  display: grid;
  gap: 1.25rem;
}

.usage-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
}

.usage-head__eyebrow {
  margin: 0 0 0.35rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.usage-head h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.usage-head__lead {
  max-width: 68ch;
  margin: 0.5rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.usage-head__meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.usage-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.usage-window {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.usage-toolbar__links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

.usage-link {
  color: var(--accent-text);
  font-size: 0.82rem;
  text-decoration: none;
}

.usage-link:hover {
  text-decoration: underline;
}

.usage-state {
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.usage-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr);
  gap: 1rem;
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}

.usage-hero__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.usage-hero__value {
  margin: 0.25rem 0 0;
  color: var(--text-primary);
  font-size: 2.8rem;
  line-height: 1.05;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.usage-hero__caption {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
}

.usage-hero__delta {
  margin: 0.6rem 0 0;
  font-size: 0.8rem;
}

.usage-hero__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.6rem;
}

.usage-stat,
.usage-week__item {
  padding: 0.8rem 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.usage-stat__label {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.usage-stat__value,
.usage-week__value {
  margin: 0.25rem 0 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
}

.usage-stat__delta {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
}

.usage-delta--up {
  color: var(--success);
}

.usage-delta--down {
  color: var(--danger);
}

.usage-delta--flat {
  color: var(--text-muted);
}

.usage-card {
  padding: 1.1rem 1.15rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.usage-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.85rem;
}

.usage-card__head h2 {
  margin: 0;
  font-size: 1.05rem;
}

.usage-card__meta {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

.usage-chart-table {
  margin-top: 0.75rem;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.usage-chart-table summary {
  cursor: pointer;
  color: var(--accent-text);
}

.usage-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
  align-items: start;
}

.usage-week {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.6rem;
}

.usage-movers {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.usage-movers__label {
  margin: 0 0 0.35rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.usage-movers__list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.35rem;
}

.usage-movers__list li {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.usage-table-wrap {
  max-width: 100%;
  overflow-x: auto;
}

.usage-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.usage-table th,
.usage-table td {
  padding: 0.55rem 0.6rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  vertical-align: top;
}

.usage-table thead th {
  color: var(--text-muted);
  font-size: 0.7rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
}

.usage-table tbody th {
  color: var(--text-primary);
  font-weight: 600;
}

.usage-table tbody td {
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}

.usage-lab-name {
  display: block;
}

.usage-lab-slug {
  display: block;
  margin-top: 0.15rem;
  color: var(--text-muted);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.7rem;
  font-weight: 400;
}

.usage-lab-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.usage-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 160px;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.usage-field .form-input {
  min-width: 0;
}

.usage-pager {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.75rem;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.usage-recent {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.5rem;
}

.usage-recent li {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: baseline;
  gap: 0.65rem;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.usage-recent__kind {
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.usage-recent__kind--completion {
  background: var(--success-bg);
  color: var(--success);
}

.usage-recent__kind--registration {
  background: var(--accent-bg);
  color: var(--accent-text);
}

.usage-recent__kind--scan {
  background: var(--warning-bg);
  color: var(--warning);
}

.usage-recent time {
  color: var(--text-muted);
  font-size: 0.72rem;
  white-space: nowrap;
}

.usage-qr {
  display: grid;
  gap: 0.75rem;
}

.usage-qr__preview {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.usage-qr__preview img {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: #fff;
}

.usage-footnote {
  margin: 0;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.75rem;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .usage-hero {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .usage-head,
  .usage-card__head {
    flex-direction: column;
  }

  .usage-head__meta {
    align-items: flex-start;
  }

  .usage-head h1 {
    font-size: 1.6rem;
  }

  .usage-hero__value {
    font-size: 2.2rem;
  }

  .usage-recent li {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .usage-recent time {
    grid-column: 2;
  }
}
</style>
