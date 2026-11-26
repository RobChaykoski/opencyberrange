<template>
  <div class="instructor-dashboard">
    <MobileEfficiencyNotice
      title="Instructor workspace"
      message="Cohort tables, charts, and reports are easier to read on a wider screen. Use a desktop for grading and report exports."
      storage-key="ocr.notice.instructor-dashboard"
    />
    <div class="dashboard-header">
      <img src="/swocts-cyber-range-mark.png" alt="SWOCTS Cyber Range" class="dashboard-logo" />
      <div class="dashboard-header__text">
        <h1 class="page-title">Teaching &amp; operations</h1>
        <p class="page-subtitle">Course health, coaching, and real-time platform activity</p>
      </div>
    </div>

    <ProgrammeOverview
      mode="teaching"
      :compact="true"
      :courses="filterCourses"
      class="teaching-snapshot"
    />

    <InstructorReadinessPanel
      v-model:course-id="selectedCourse"
      :courses="filterCourses"
    />

    <!-- System Health (admin only) -->
    <div v-if="showHealthCard" class="health-bar" :class="dashboardHealthClass ? `health-bar--${dashboardHealthClass}` : ''" @click="goToSystemHealth">
      <template v-if="dashboardHealthLoaded">
        <span class="health-dot" :class="`health-dot--${dashboardHealthStatus === 'ok' ? 'green' : dashboardHealthStatus === 'warning' ? 'amber' : 'red'}`"></span>
        <span class="health-bar__label">System</span>
      </template>
      <span v-else class="health-bar__label">Checking...</span>
    </div>

    <!-- Reporting window and scope. This governs Learning, The Pulse, and the
         activity feed. The live snapshot below is deliberately separate. -->
    <div class="filter-bar">
      <PeriodFilter
        :preset="activePreset"
        :custom-start="customStart"
        :custom-end="customEnd"
        @update:preset="changePreset"
        @update:custom-start="changeCustomStart"
        @update:custom-end="changeCustomEnd"
      />
      <div class="filter-bar__dropdowns">
        <select
          v-model="selectedCourse"
          class="filter-select"
          aria-label="Filter by course"
          @change="onCourseChange"
        >
          <option :value="null">All Courses</option>
          <option v-for="c in filterCourses" :key="c.id" :value="c.id">
            {{ c.code }}
          </option>
        </select>
        <select
          v-model="selectedUser"
          class="filter-select"
          aria-label="Filter by student"
          @change="onUserChange"
        >
          <option :value="null">All Students</option>
          <option v-for="s in filterStudents" :key="s.id" :value="s.id">
            {{ s.username }}
          </option>
        </select>
      </div>
      <div class="filter-bar__export">
        <input
          v-model="exportReason"
          class="filter-select filter-select--compact"
          type="text"
          maxlength="500"
          placeholder="Reason (required)"
          aria-label="Reason for export"
        />
        <select v-model="exportFormat" class="filter-select filter-select--compact" title="Report format">
          <option value="pdf">PDF</option>
          <option value="csv">CSV</option>
        </select>
        <button
          class="export-btn"
          :disabled="exportLoading || exportReason.trim().length < 5"
          @click="downloadReport"
          :title="`Download filtered view as ${exportFormat.toUpperCase()}`"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          {{ exportLoading ? 'Generating...' : 'Download Report' }}
        </button>
      </div>
    </div>

    <!-- Learning metrics for the selected period -->
    <div class="learning-metrics">
      <div class="learning-metrics__head">
        <h2 class="panel__title">Learning</h2>
        <span class="panel__subtitle">
          {{ periodLabel }}<template v-if="scopeLabel"> · {{ scopeLabel }}</template>
          · {{ learning?.students_in_scope ?? 0 }} students in scope
        </span>
        <span v-if="learningLoading" class="period-loading">Updating…</span>
      </div>
      <p v-if="learningError" class="period-error" role="alert">
        {{ learningError }}
        <button type="button" class="btn btn--outline btn--sm" @click="fetchLearning">Retry</button>
      </p>
      <p v-if="periodIsShort" class="period-note">
        Short window. These counts are operational; use 7 days or more for a learning view.
      </p>
      <div class="stats-grid learning-grid">
        <div class="rich-card">
          <div class="rich-card__header">
            <svg class="rich-card__icon rich-card__icon--active" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <span class="rich-card__label">Active students</span>
          </div>
          <div class="rich-card__body">
            <span class="rich-card__value">{{ learning?.students_active ?? 0 }}</span>
          </div>
          <div class="rich-card__footer">
            <span class="rich-card__detail rich-card__detail--muted">
              of {{ learning?.students_in_scope ?? 0 }} students in scope
            </span>
          </div>
        </div>

        <div class="rich-card">
          <div class="rich-card__header">
            <svg class="rich-card__icon rich-card__icon--flags" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
              <line x1="4" y1="22" x2="4" y2="15"/>
            </svg>
            <span class="rich-card__label">Exercise completions</span>
          </div>
          <div class="rich-card__body">
            <span class="rich-card__value">{{ learning?.labs_completed ?? 0 }}</span>
          </div>
          <div class="rich-card__footer">
            <span class="rich-card__detail rich-card__detail--muted">passing completions in this period</span>
          </div>
        </div>

        <div class="rich-card">
          <div class="rich-card__header">
            <svg class="rich-card__icon rich-card__icon--time" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3v18h18"/>
              <path d="m7 14 4-4 4 4 5-6"/>
            </svg>
            <span class="rich-card__label">Practice score</span>
          </div>
          <div class="rich-card__body">
            <span class="rich-card__value">{{ learning?.average_score != null ? learning.average_score + '%' : '-' }}</span>
          </div>
          <div class="rich-card__footer">
            <span class="rich-card__detail rich-card__detail--muted">0–100, retries and hints adjusted; not a grade</span>
          </div>
        </div>

        <div class="rich-card" :class="{ 'rich-card--attention': (learning?.check_in_students ?? 0) > 0 }">
          <div class="rich-card__header">
            <svg class="rich-card__icon rich-card__icon--warning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span class="rich-card__label">Check-in signals</span>
          </div>
          <div class="rich-card__body">
            <span class="rich-card__value">{{ learning?.check_in_students ?? 0 }}</span>
          </div>
          <div class="rich-card__footer">
            <span v-if="learning?.check_in_students" class="rich-card__detail">review Teaching focus; this is a support signal, not a learner label</span>
            <span v-else class="rich-card__detail rich-card__detail--muted">no support signals in this period</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Live snapshot: today and right now, independent of the period -->
    <div class="learning-metrics learning-metrics--live">
      <div class="learning-metrics__head">
        <h2 class="panel__title">Live snapshot</h2>
        <span class="panel__subtitle">Today and right now; not affected by the period</span>
      </div>
      <div class="stats-grid">
      <!-- Flags Today -->
      <div class="rich-card">
        <div class="rich-card__header">
          <svg class="rich-card__icon rich-card__icon--flags" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
            <line x1="4" y1="22" x2="4" y2="15"/>
          </svg>
          <span class="rich-card__label">Flags Today</span>
        </div>
        <div class="rich-card__body">
          <span class="rich-card__value">{{ stats.flags_today }}</span>
          <div class="rich-card__sparkline" v-if="stats.flags_sparkline?.length">
            <svg
              :viewBox="`0 0 ${stats.flags_sparkline.length * 12} 32`"
              preserveAspectRatio="none"
              role="img"
              :aria-label="`Flag submissions trend: ${stats.flags_sparkline.join(', ')}`"
            >
              <polyline
                :points="sparklinePoints(stats.flags_sparkline)"
                fill="none" stroke="#22c55e" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"
              />
            </svg>
          </div>
        </div>
        <div class="rich-card__footer">
          <span v-if="stats.flag_students_today" class="rich-card__detail">
            {{ stats.flag_students_today }} student{{ stats.flag_students_today !== 1 ? 's' : '' }}
          </span>
        </div>
      </div>

      <!-- Active Exercises -->
      <div class="rich-card">
        <div class="rich-card__header">
          <svg class="rich-card__icon rich-card__icon--active" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          <span class="rich-card__label">Active Now</span>
        </div>
        <div class="rich-card__body">
          <span class="rich-card__value">{{ stats.active_count || 0 }}</span>
        </div>
        <div class="rich-card__footer">
          <span v-if="!stats.active_count" class="rich-card__detail rich-card__detail--muted">No active sessions</span>
        </div>
      </div>

      <!-- Avg Completion -->
      <div class="rich-card">
        <div class="rich-card__header">
          <svg class="rich-card__icon rich-card__icon--time" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span class="rich-card__label">Avg Completion</span>
        </div>
        <div class="rich-card__body">
          <span class="rich-card__value" :class="avgTimeColor">
            {{ stats.avg_completion_min != null ? stats.avg_completion_min + 'm' : '-' }}
          </span>
        </div>
        <div class="rich-card__footer">
          <span v-if="stats.avg_completion_typical != null" class="rich-card__detail">
            typical: {{ stats.avg_completion_typical }}m
          </span>
          <span v-else class="rich-card__detail rich-card__detail--muted">no data yet</span>
        </div>
      </div>
    </div>

    </div>

    <!-- Teaching focus: a short list of actions, not another dashboard of counts -->
    <div class="panel teaching-focus">
      <div class="panel__header">
        <h2 class="panel__title">Teaching focus</h2>
        <span class="panel__subtitle">The next actions that move a cohort forward</span>
      </div>
      <div class="focus-grid">
        <article class="focus-card">
          <span class="focus-card__count">{{ stats.near_certificate_count || 0 }}</span>
          <h3 class="focus-card__title">One lab from a certificate</h3>
          <ul v-if="stats.near_certificate?.length" class="focus-list">
            <li v-for="item in stats.near_certificate" :key="`${item.user_id}-${item.track_name}-${item.level_name}`">
              <strong>{{ item.username }}</strong>
              <span>{{ item.track_name }} · {{ item.level_name }} · {{ item.completed }}/{{ item.total }}</span>
            </li>
          </ul>
          <p v-else class="focus-card__empty">No learner is one lab away right now.</p>
        </article>

        <article class="focus-card">
          <span class="focus-card__count">{{ stats.inactive_students_count || 0 }}</span>
          <h3 class="focus-card__title">Inactive 7+ days</h3>
          <ul v-if="stats.inactive_students?.length" class="focus-list">
            <li v-for="item in stats.inactive_students" :key="item.user_id">
              <strong>{{ item.username }}</strong>
              <span>
                {{ formatAgo(item.last_login_at) }}
                <template v-if="item.course_codes?.length"> · {{ item.course_codes.join(', ') }}</template>
              </span>
            </li>
          </ul>
          <p v-else class="focus-card__empty">Everyone has been active in the last 7 days.</p>
        </article>

        <article class="focus-card">
          <span class="focus-card__count">{{ (stats.recent_completions_count || 0) + (stats.recent_certificates_count || 0) }}</span>
          <h3 class="focus-card__title">Recent wins</h3>
          <ul v-if="recentWins.length" class="focus-list">
            <li v-for="win in recentWins" :key="win.key">
              <strong>{{ win.username }}</strong>
              <span>{{ win.kind }} · {{ win.label }} · {{ formatAgo(win.when) }}</span>
            </li>
          </ul>
          <p v-else class="focus-card__empty">No completions or milestones yet this week.</p>
        </article>
      </div>
    </div>

    <!-- The Pulse Chart -->
    <div class="panel">
      <div class="panel__header">
        <h2 class="panel__title">The Pulse</h2>
        <span class="panel__subtitle">
          {{ periodLabel }}<template v-if="scopeLabel"> · {{ scopeLabel }}</template>
        </span>
      </div>
      <p class="pulse-note">
        Aggregate activity for the courses you teach. This chart does not rank learners
        or expose an individual growth score.
      </p>
      <div class="chart-container">
        <EChart
          v-if="pulseData.labels.length"
          :option="pulseOption"
          height="280px"
          :aria-label="pulseAriaLabel"
        />
        <div v-else class="chart-empty">No activity data yet</div>
      </div>
      <p v-if="pulseForecast.length" class="pulse-note pulse-note--forecast">
        {{ pulseForecastNote }}
      </p>
      <table v-if="pulseRaw.length" class="sr-only">
        <caption>The Pulse: exercise sessions and flags submitted by historical time bucket. The projection is excluded from this table.</caption>
        <thead>
          <tr><th scope="col">Time</th><th scope="col">Exercise sessions</th><th scope="col">Flags submitted</th></tr>
        </thead>
        <tbody>
          <tr v-for="(point, index) in pulseRaw" :key="point.hour + index">
            <th scope="row">{{ pulseLabel(point) }}</th>
            <td>{{ point.concurrent_labs ?? 0 }}</td>
            <td>{{ point.flags_submitted ?? 0 }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Live Operations Feed -->
    <div class="panel">
      <div class="panel__header">
        <h2 class="panel__title">Live Operations Feed</h2>
        <span class="panel__subtitle feed-count">
          {{ periodLabel }}<template v-if="scopeLabel"> · {{ scopeLabel }}</template>
          · {{ studentFeed.length }} shown
        </span>
        <span v-if="feedLastUpdated" class="feed-freshness">
          Updated {{ formatTime(feedLastUpdated.toISOString()) }}
        </span>
        <button
          @click="fetchFeed('refresh')"
          class="refresh-btn"
          title="Refresh now. Auto-refreshes every 30 seconds."
          aria-label="Refresh activity feed"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'spin': feedLoading }">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
        </button>
      </div>
      <p class="feed-note">Newest first. This is an activity log, not a ranking.</p>
      <p v-if="feedError" class="period-error" role="alert">
        {{ feedError }}
        <button type="button" class="btn btn--outline btn--sm" @click="fetchFeed('refresh')">Retry</button>
      </p>
      <div class="feed-table-wrapper" role="region" aria-label="Recent learner activity table" tabindex="0">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">User</th>
              <th scope="col">Event</th>
              <th scope="col">Target</th>
              <th scope="col">Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="feedLoading && studentFeed.length === 0">
              <td colspan="4" class="empty-row">Loading activity...</td>
            </tr>
            <tr v-else-if="feedError">
              <td colspan="4" class="empty-row">Could not load activity for this period.</td>
            </tr>
            <tr v-else-if="studentFeed.length === 0">
              <td colspan="4" class="empty-row">No activity in this period. Try a wider range.</td>
            </tr>
            <tr v-for="event in studentFeed" :key="event.id">
              <td class="user-cell"><PrivacyText v-if="event.actor_username" :value="event.actor_username" /><span v-else>System</span></td>
              <td>
                <span class="event-badge" :class="'event-badge--' + event.event_type">
                  {{ event.event_label }}
                </span>
              </td>
              <td class="target-cell">{{ event.target_label || '-' }}</td>
              <td class="time-cell" :title="event.created_at ? new Date(event.created_at).toLocaleString() : ''">{{ formatTime(event.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="feedHasMore" class="feed-load-more">
        <button @click="loadMoreFeed" class="load-more-btn" :disabled="feedLoadingMore">
          {{ feedLoadingMore ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>

    <!-- Diagnostic Log (admin only) -->
    <div v-if="diagnosticFeed.length && showHealthCard" class="panel panel--diagnostic">
      <div class="panel__header">
        <h2 class="panel__title" @click="showDiagnosticLog = !showDiagnosticLog" style="cursor: pointer;">
          Diagnostic Log
          <span class="diagnostic-chevron" :class="{ 'diagnostic-chevron--open': showDiagnosticLog }">&#9662;</span>
        </h2>
        <span class="panel__subtitle feed-count">{{ diagnosticFeed.length }} events</span>
      </div>
      <div v-if="showDiagnosticLog" class="feed-table-wrapper" role="region" aria-label="Diagnostic event table" tabindex="0">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">User</th>
              <th scope="col">Event</th>
              <th scope="col">Target</th>
              <th scope="col">Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in diagnosticFeed" :key="event.id" class="activity-row--diagnostic">
              <td class="user-cell">{{ event.actor_username || 'System / removed user' }}</td>
              <td>
                <span class="event-badge event-badge--diagnostic">{{ event.event_label }}</span>
              </td>
              <td class="target-cell">{{ event.target_label || '-' }}</td>
              <td class="time-cell">{{ formatTime(event.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import MobileEfficiencyNotice from '../components/MobileEfficiencyNotice.vue'
import { useRouter } from 'vue-router'
import axios from '../api/axios'
import EChart from '../components/EChart.vue'
import PeriodFilter from '../components/PeriodFilter.vue'
import ProgrammeOverview from '../components/ProgrammeOverview.vue'
import InstructorReadinessPanel from '../components/InstructorReadinessPanel.vue'
import PrivacyText from '../components/PrivacyText.vue'
import { usePoll } from '../composables/usePoll'
import { usePeriodFilter } from '../composables/usePeriod'
import { isAdmin } from '../utils/roles'
import { downloadBlob, filenameFromDisposition } from '../utils/download'
import {
  ECHART_COLORS,
  categoryAxis,
  chartGrid,
  legendStyle,
  tooltipStyle,
  valueAxis,
} from '../components/charts/echartsTheme'

const router = useRouter()
const showHealthCard = isAdmin()

const stats = ref({
  flags_today: 0, flags_yesterday: null, flag_students_today: 0, flags_sparkline: [],
  active_count: 0, active_users: [],
  avg_completion_min: null, avg_completion_typical: null,
  students_active: 0, labs_completed: 0, average_score: null,
  struggling_students: 0, metrics_window_days: 7,
  near_certificate: [], near_certificate_count: 0,
  inactive_students: [], inactive_students_count: 0,
  recent_completions: [], recent_completions_count: 0,
  recent_certificates: [], recent_certificates_count: 0,
})

const recentWins = computed(() => {
  const certificates = (stats.value.recent_certificates || []).map((item) => ({
    key: `cert-${item.user_id}-${item.track_name}-${item.level_name}`,
    username: item.username,
    label: `${item.track_name} · ${item.level_name}`,
    kind: 'Certificate milestone',
    when: item.awarded_at,
  }))
  const completions = (stats.value.recent_completions || []).map((item) => ({
    key: `completion-${item.user_id}-${item.lab_name}-${item.completed_at}`,
    username: item.username,
    label: item.lab_name,
    kind: 'Exercise completed',
    when: item.completed_at,
  }))
  return [...certificates, ...completions]
    .sort((a, b) => String(b.when || '').localeCompare(String(a.when || '')))
    .slice(0, 5)
})

const formatAgo = (value) => {
  if (!value) return 'never signed in'
  const then = new Date(value)
  if (Number.isNaN(then.getTime())) return 'unknown'
  const days = Math.max(0, Math.floor((Date.now() - then.getTime()) / 86400000))
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  return `${days} days ago`
}

const avgTimeColor = computed(() => {
  const today = stats.value.avg_completion_min
  const typical = stats.value.avg_completion_typical
  if (today == null || typical == null) return ''
  if (today <= typical * 0.85) return 'avg--fast'
  if (today >= typical * 1.15) return 'avg--slow'
  return ''
})

const initials = (username) => {
  if (!username) return '?'
  // Handle snake_case names like jordan_patel → JP
  const parts = username.split(/[_\s-]+/)
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  return username.slice(0, 2).toUpperCase()
}

const sparklinePoints = (data) => {
  if (!data || !data.length) return ''
  const max = Math.max(...data, 1)
  return data.map((v, i) => `${i * 12 + 6},${30 - (v / max) * 26}`).join(' ')
}
const feed = ref([])
const feedLoading = ref(false)
const feedOffset = ref(0)
const feedHasMore = ref(true)
const feedLoadingMore = ref(false)
const feedError = ref('')
const feedLastUpdated = ref(null)
const feedPageSize = 50
const showDiagnosticLog = ref(false)

const studentFeed = computed(() => feed.value.filter(e => !isDiagnosticEvent(e)))
const diagnosticFeed = computed(() => feed.value.filter(e => isDiagnosticEvent(e)))
const pulseRaw = ref([])

// System health state
const dashboardHealthStatus = ref('')
const dashboardHealthLoaded = ref(false)

// Reporting window and scope
const {
  preset: activePreset,
  customStart,
  customEnd,
  range: filterRange,
  label: periodLabel,
  isShort: periodIsShort,
  setPreset,
  setCustomStart,
  setCustomEnd,
  refresh: refreshPeriod,
} = usePeriodFilter('7d')

const pulseGranularity = ref('hour')
const pulseForecast = ref([])
const pulseForecastNote = ref('')

const learning = ref(null)
const learningLoading = ref(false)
const learningError = ref('')
let learningRequestId = 0

// Course / user filter state
const selectedCourse = ref(null)
const selectedUser = ref(null)
const filterCourses = ref([])
const filterStudents = ref([])

const exportFormat = ref('pdf')
const exportReason = ref('')
const exportLoading = ref(false)

const scopeLabel = computed(() => {
  const parts = []
  if (selectedCourse.value) {
    const course = filterCourses.value.find((item) => item.id === selectedCourse.value)
    if (course) parts.push(course.code)
  }
  if (selectedUser.value) {
    const student = filterStudents.value.find((item) => item.id === selectedUser.value)
    if (student) parts.push(student.username)
  }
  return parts.join(' / ')
})

const pulseLabel = (point) => {
  const date = new Date(point.hour)
  if (pulseGranularity.value === 'day') {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const pulseData = computed(() => {
  const history = pulseRaw.value
  const forecast = pulseForecast.value
  const labels = [...history.map(pulseLabel), ...forecast.map(pulseLabel)]
  const sessions = history.map((point) => point.concurrent_labs)
  const flags = history.map((point) => point.flags_submitted)
  const padHistory = Array(forecast.length).fill(null)
  const padForecast = Array(history.length).fill(null)

  return {
    labels,
    historyLength: history.length,
    datasets: [
      {
        label: 'Exercise Sessions',
        data: [...sessions, ...padHistory],
        borderColor: ECHART_COLORS.accent,
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
      },
      {
        label: 'Flags Submitted',
        data: [...flags, ...padHistory],
        borderColor: ECHART_COLORS.success,
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
      },
      {
        label: 'Sessions forecast',
        data: [...padForecast, ...forecast.map((point) => point.concurrent_labs)],
        borderColor: ECHART_COLORS.accent,
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        lineStyle: { type: 'dashed', width: 2, opacity: 0.65 },
      },
      {
        label: 'Flags forecast',
        data: [...padForecast, ...forecast.map((point) => point.flags_submitted)],
        borderColor: ECHART_COLORS.success,
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        lineStyle: { type: 'dashed', width: 2, opacity: 0.65 },
      },
    ],
  }
})

const pulseOption = computed(() => {
  const labels = pulseData.value.labels
  const datasets = pulseData.value.datasets
  const boundary = pulseData.value.historyLength

  return {
    // The dashboard refreshes every 30s. Animating a full dataset swap makes
    // the panel flash, so updates are intentionally instant.
    animation: false,
    color: [ECHART_COLORS.accent, ECHART_COLORS.success],
    tooltip: { ...tooltipStyle, trigger: 'axis' },
    legend: {
      ...legendStyle,
      data: ['Exercise Sessions', 'Flags Submitted', 'Sessions forecast', 'Flags forecast'],
    },
    grid: chartGrid,
    xAxis: {
      ...categoryAxis,
      data: labels,
      axisLabel: { ...categoryAxis.axisLabel, hideOverlap: true },
    },
    yAxis: valueAxis,
    series: datasets.map((dataset, index) => ({
      name: dataset.label,
      type: 'line',
      smooth: true,
      showSymbol: false,
      symbolSize: 6,
      data: dataset.data,
      lineStyle: dataset.lineStyle || { width: 2 },
      areaStyle: dataset.fill ? { opacity: 0.12 } : undefined,
      markLine: index === 0 && boundary && labels[boundary - 1]
        ? {
            symbol: 'none',
            label: { formatter: 'forecast', color: '#94a3b8' },
            lineStyle: { color: '#94a3b8', type: 'dashed' },
            data: [{ xAxis: labels[boundary - 1] }],
          }
        : undefined,
    })),
  }
})

const pulseAriaLabel = computed(() => {
  const history = pulseRaw.value
  if (!history.length) return 'The Pulse: no activity data yet.'
  const sessions = history.reduce((sum, point) => sum + (Number(point.concurrent_labs) || 0), 0)
  const flags = history.reduce((sum, point) => sum + (Number(point.flags_submitted) || 0), 0)
  const forecast = pulseForecast.value
  const projection = forecast.length
    ? ` The dashed projection covers ${forecast.length} future buckets.`
    : ''
  return `The Pulse over ${history.length} time buckets: ${sessions} exercise sessions and ${flags} flags submitted.${projection}`
})

const dashboardHealthClass = computed(() =>
  dashboardHealthStatus.value === 'ok' ? 'healthy' : dashboardHealthStatus.value
)

const goToSystemHealth = () => {
  router.push({ path: '/admin', query: { tab: 'system' } })
}

const fetchDashboardHealth = async () => {
  try {
    const { data } = await axios.get('/admin/system/status')
    dashboardHealthStatus.value = data.overall || 'error'
  } catch {
    dashboardHealthStatus.value = 'error'
  } finally {
    dashboardHealthLoaded.value = true
  }
}

const tzOffset = -(new Date().getTimezoneOffset())  // minutes east of UTC (e.g. -300 for CDT)

const fetchStats = async () => {
  try {
    const res = await axios.get('/dashboard/instructor/stats', { params: { tz_offset: tzOffset } })
    stats.value = res.data
  } catch (e) {
    console.error('Failed to fetch stats:', e)
  }
}

const _scopeParams = () => {
  const p = {}
  if (selectedCourse.value) p.course_id = selectedCourse.value
  if (selectedUser.value) p.user_id = selectedUser.value
  return p
}

const fetchLearning = async () => {
  const requestId = ++learningRequestId
  learningLoading.value = true
  learningError.value = ''
  try {
    const range = filterRange.value
    const res = await axios.get('/dashboard/instructor/learning', {
      params: {
        ..._scopeParams(),
        start: range.startIso,
        end: range.endIso,
      },
    })
    if (requestId === learningRequestId) {
      learning.value = res.data
    }
  } catch (e) {
    if (requestId === learningRequestId) {
      learningError.value =
        e.response?.data?.detail || 'Could not load learning metrics for this period.'
    }
  } finally {
    if (requestId === learningRequestId) {
      learningLoading.value = false
    }
  }
}

const fetchPulse = async () => {
  try {
    const params = { ..._scopeParams() }
    const range = filterRange.value
    params.start = range.startIso
    params.end = range.endIso
    const res = await axios.get('/dashboard/instructor/pulse', { params })
    pulseRaw.value = res.data.data || []
    pulseGranularity.value = res.data.granularity || 'hour'
    pulseForecast.value = res.data.forecast || []
    pulseForecastNote.value = res.data.forecast_note || ''
  } catch (e) {
    console.error('Failed to fetch pulse:', e)
  }
}

// Cheap change-detection so a background refresh that returns identical data
// does not reassign feed.value (which would re-render the whole table = flicker).
// The feed is chronological-desc, so new activity changes the count or top id.
const _feedSignature = (events) => {
  if (!events || !events.length) return '0'
  return `${events.length}:${events[0].id}:${events[events.length - 1].id}`
}

const fetchFeed = async (mode = 'reset', { silent = false } = {}) => {
  // mode: 'reset' = fresh load (first page), 'append' = load next page, 'refresh' = reload all loaded pages
  // silent = background auto-refresh: no spinner, and skip the update when unchanged.
  if (mode === 'append') {
    feedLoadingMore.value = true
  } else if (!silent) {
    feedLoading.value = true
  }
  if (mode === 'reset') {
    feedOffset.value = 0
    feedHasMore.value = true
  }
  feedError.value = ''
  try {
    const range = filterRange.value
    const scope = _scopeParams()

    if (mode === 'refresh' && feedOffset.value > feedPageSize) {
      // Re-fetch everything up to current offset to preserve expanded state
      const params = {
        limit: feedOffset.value,
        offset: 0,
        ...scope,
        start: range.startIso,
        end: range.endIso,
      }
      const res = await axios.get('/dashboard/instructor/feed', { params })
      const events = res.data.events || []
      if (_feedSignature(events) !== _feedSignature(feed.value)) {
        feed.value = events
      }
      feedHasMore.value = events.length >= feedOffset.value
    } else {
      const offset = mode === 'append' ? feedOffset.value : 0
      const params = {
        limit: feedPageSize,
        offset,
        ...scope,
        start: range.startIso,
        end: range.endIso,
      }
      const res = await axios.get('/dashboard/instructor/feed', { params })
      const events = res.data.events || []
      if (mode === 'append') {
        feed.value = [...feed.value, ...events]
      } else if (_feedSignature(events) !== _feedSignature(feed.value)) {
        feed.value = events
      }
      feedHasMore.value = events.length >= feedPageSize
      feedOffset.value = (mode === 'append' ? feedOffset.value : 0) + events.length
    }
    feedLastUpdated.value = new Date()
  } catch (e) {
    feedError.value =
      e.response?.data?.detail || 'Could not load activity for this period.'
  } finally {
    feedLoading.value = false
    feedLoadingMore.value = false
  }
}

const loadMoreFeed = () => {
  fetchFeed('append')
}

const fetchFilterOptions = async (courseId) => {
  try {
    const params = {}
    if (courseId) params.course_id = courseId
    const res = await axios.get('/dashboard/instructor/filter-options', { params })
    filterCourses.value = res.data.courses || []
    filterStudents.value = res.data.students || []
  } catch (e) {
    console.error('Failed to fetch filter options:', e)
  }
}

const refreshReporting = () => {
  fetchLearning()
  fetchPulse()
  fetchFeed()
}

const onCourseChange = () => {
  selectedUser.value = null
  fetchFilterOptions(selectedCourse.value)
  refreshReporting()
}

const onUserChange = () => {
  refreshReporting()
}

const changePreset = (next) => {
  setPreset(next)
  refreshPeriod()
  refreshReporting()
}

const changeCustomStart = (value) => {
  setCustomStart(value)
  refreshReporting()
}

const changeCustomEnd = (value) => {
  setCustomEnd(value)
  refreshReporting()
}

const isDiagnosticEvent = (event) => {
  if (event.actor_role === 'admin') return true
  if (event.detail) {
    try {
      const obj = typeof event.detail === 'string' ? JSON.parse(event.detail) : event.detail
      if (obj.source === 'diagnostic') return true
    } catch {}
  }
  return false
}

const downloadReport = async () => {
  if (exportLoading.value) return
  const reason = exportReason.value.trim()
  if (reason.length < 5) return
  exportLoading.value = true
  try {
    const range = filterRange.value
    const params = {
      format: exportFormat.value,
      range_label: periodLabel.value,
      reason,
      ..._scopeParams(),
      start: range.startIso,
      end: range.endIso,
    }

    const res = await axios.get('/dashboard/instructor/report', {
      params,
      responseType: 'blob',
    })

    const mime = exportFormat.value === 'pdf' ? 'application/pdf' : 'text/csv'
    const blob = new Blob([res.data], { type: mime })
    const filename = filenameFromDisposition(
      res.headers?.['content-disposition'],
      `ops_report.${exportFormat.value}`
    )
    downloadBlob(blob, filename)
    exportReason.value = ''
  } catch (e) {
    console.error('Failed to download report:', e)
    alert('Failed to generate report. Please try again.')
  } finally {
    exportLoading.value = false
  }
}

const formatTime = (isoStr) => {
  if (!isoStr) return '-'
  const d = new Date(isoStr)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h ago`
  return d.toLocaleDateString()
}

// Refresh the dashboard every 30 seconds; paused while the tab is hidden,
// with an immediate refresh when it becomes visible again.
usePoll(() => {
  if (showHealthCard) fetchDashboardHealth()
  refreshPeriod()
  fetchStats()
  fetchLearning()
  fetchPulse()
  fetchFeed('refresh', { silent: true })
}, 30000)

onMounted(() => {
  if (showHealthCard) fetchDashboardHealth()
  fetchFilterOptions()
  fetchStats()
  fetchLearning()
  fetchPulse()
  fetchFeed()
})
</script>

<style scoped>
.instructor-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
  padding: 1.25rem 1.4rem;
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--accent);
  border-radius: 14px;
  background:
    linear-gradient(135deg, var(--accent-bg), transparent 62%),
    var(--bg-secondary);
}

.teaching-snapshot {
  margin-bottom: 1.5rem;
}

.dashboard-logo {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  object-fit: contain;
  background: var(--bg-primary);
  border-radius: 14px;
  padding: 5px;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 0.9375rem;
  margin: 0;
}

/* Health Bar (compact, admin only) */
.health-bar {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.health-bar:hover { border-color: var(--accent); }
.health-bar--healthy { border-color: rgba(22, 101, 52, 0.4); }
.health-bar--warning { border-color: #854d0e; }
.health-bar--error { border-color: #991b1b; }

.health-bar__label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
  margin-right: 0.5rem;
}

/* Stats Grid - 3 wide cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* Learning metrics */
.learning-metrics {
  margin-bottom: 1.25rem;
}

.learning-metrics__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.learning-grid {
  grid-template-columns: repeat(4, 1fr);
  margin-bottom: 0;
}

.learning-metrics--live {
  margin-top: 1.5rem;
}

.period-loading {
  color: var(--text-muted);
  font-size: 0.7rem;
  font-style: italic;
}

.period-error {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin: 0 0 0.75rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid color-mix(in srgb, var(--danger) 40%, var(--border-color));
  border-radius: 8px;
  background: var(--danger-bg);
  color: var(--text-primary);
  font-size: 0.78rem;
}

.period-note {
  margin: 0 0 0.75rem;
  padding: 0.45rem 0.6rem;
  border-left: 2px solid var(--warning);
  background: var(--warning-bg);
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.45;
}

.rich-card--attention {
  border-color: color-mix(in srgb, var(--warning) 45%, var(--border-color));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--warning) 20%, transparent);
}

.rich-card__icon--warning {
  color: var(--warning);
}

/* Rich Cards */
.rich-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  min-height: 140px;
}

.rich-card__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rich-card__icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.rich-card__icon--flags { color: #4ade80; }
.rich-card__icon--active { color: #60a5fa; }
.rich-card__icon--time { color: #a78bfa; }

.rich-card__label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.rich-card__body {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.rich-card__value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.rich-card__value.avg--fast { color: #4ade80; }
.rich-card__value.avg--slow { color: #fbbf24; }

.rich-card__sparkline {
  flex: 1;
  height: 32px;
  opacity: 0.7;
}

.rich-card__sparkline svg {
  width: 100%;
  height: 100%;
}

.rich-card__footer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 1.25rem;
}

.rich-card__trend {
  font-size: 0.75rem;
  font-weight: 600;
}

.trend--up { color: #4ade80; }
.trend--down { color: #f87171; }
.trend--flat { color: var(--text-muted); }

.rich-card__detail {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.rich-card__detail--muted {
  color: var(--text-muted);
  font-style: italic;
}

/* Active user avatars */
.active-avatars {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.active-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.active-avatar--more {
  background: rgba(100, 116, 139, 0.15);
  color: #94a3b8;
}

/* Health dots */
.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.health-dot--green {
  background: #4ade80;
  box-shadow: 0 0 4px rgba(74, 222, 128, 0.4);
}

.health-dot--amber {
  background: #fbbf24;
  box-shadow: 0 0 4px rgba(251, 191, 36, 0.4);
  animation: pulse-amber 2s ease-in-out infinite;
}

.health-dot--red {
  background: #f87171;
  box-shadow: 0 0 6px rgba(248, 113, 113, 0.5);
  animation: pulse-red 1.5s ease-in-out infinite;
}

@keyframes pulse-amber {
  0%, 100% { box-shadow: 0 0 4px rgba(251, 191, 36, 0.4); }
  50% { box-shadow: 0 0 8px rgba(251, 191, 36, 0.7); }
}

@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 6px rgba(248, 113, 113, 0.5); }
  50% { box-shadow: 0 0 12px rgba(248, 113, 113, 0.8); }
}

.stat-card__content {
  display: flex;
  flex-direction: column;
}

.stat-card__value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-card__label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Panels */
.panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.panel--disabled {
  opacity: 0.5;
  position: relative;
}

.panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.panel__title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.panel__subtitle {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.pulse-note {
  margin: 0.35rem 0 0.6rem;
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.45;
}

.pulse-note--forecast {
  padding-left: 0.55rem;
  border-left: 2px solid var(--accent);
  color: var(--text-secondary);
}

.panel__description {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0.5rem 0 0 0;
}

/* Teaching focus: three actionable cohorts, not a wall of metrics */
.teaching-focus {
  border-left: 3px solid var(--accent);
}

.focus-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.85rem;
}

.focus-card {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  min-width: 0;
  padding: 0.9rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-tertiary, rgba(148, 163, 184, 0.06));
}

.focus-card__count {
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1;
  color: var(--accent);
  font-variant-numeric: tabular-nums;
}

.focus-card__title {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
}

.focus-list {
  list-style: none;
  margin: 0.25rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.focus-list li {
  display: flex;
  flex-direction: column;
  min-width: 0;
  font-size: 0.76rem;
  line-height: 1.35;
}

.focus-list strong {
  color: var(--text-primary);
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.focus-list span {
  color: var(--text-muted);
}

.focus-card__empty {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.76rem;
}

.badge--coming-soon {
  display: inline-block;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.5rem;
}

.refresh-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.375rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
  display: block;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

/* Chart */
.chart-container {
  height: 280px;
  position: relative;
}

.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--nav-label);
  font-size: 0.9375rem;
}

/* Feed Table */.feed-table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 0.625rem 1rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--hover-bg);
}

.empty-row {
  text-align: center;
  color: var(--nav-label);
  padding: 2rem 1rem !important;
}

.feed-count {
  margin-left: auto;
  margin-right: 0.5rem;
}

.feed-freshness {
  color: var(--text-muted);
  font-size: 0.68rem;
  white-space: nowrap;
}

.feed-note {
  margin: 0 0 0.5rem;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.feed-load-more {
  display: flex;
  justify-content: center;
  padding: 0.75rem 0 0.25rem;
}

.load-more-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.4rem 1.5rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.load-more-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: wait;
}

.user-cell {
  font-weight: 500;
  color: var(--text-primary);
}

.target-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time-cell {
  color: var(--text-muted);
  white-space: nowrap;
}

/* Event Badges */
.event-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.event-badge--lab_started { background: rgba(59, 130, 246, 0.15); color: var(--badge-blue); }
.event-badge--lab_stopped { background: rgba(100, 116, 139, 0.2); color: var(--badge-slate); }
.event-badge--lab_completed { background: rgba(34, 197, 94, 0.15); color: var(--badge-green); }
.event-badge--flag_correct { background: rgba(34, 197, 94, 0.15); color: var(--badge-green); }
.event-badge--flag_incorrect { background: rgba(239, 68, 68, 0.15); color: var(--badge-red); }
.event-badge--hint_used { background: rgba(245, 158, 11, 0.15); color: var(--badge-amber); }
.event-badge--user_registered { background: rgba(168, 85, 247, 0.15); color: var(--badge-purple); }
.event-badge--user_approved { background: rgba(168, 85, 247, 0.15); color: var(--badge-purple); }
.event-badge--vpn_downloaded { background: rgba(6, 182, 212, 0.15); color: var(--badge-cyan); }
.event-badge--course_enrolled { background: rgba(236, 72, 153, 0.15); color: var(--badge-pink); }
.event-badge--achievement_awarded { background: rgba(245, 158, 11, 0.15); color: var(--badge-amber); }
.event-badge--diagnostic { background: rgba(245, 158, 11, 0.15); color: var(--badge-amber); }

.diagnostic-tag {
  display: inline-block;
  margin-left: 0.375rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: rgba(245, 158, 11, 0.1);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.activity-row--diagnostic { background: rgba(245, 158, 11, 0.03); }
.activity-row--diagnostic td { opacity: 0.75; }
.activity-row--diagnostic td:nth-child(2) { opacity: 1; }

.panel--diagnostic { border-color: rgba(245, 158, 11, 0.2); }
.panel--diagnostic .panel__title { font-size: 0.95rem; }
.diagnostic-chevron {
  display: inline-block;
  font-size: 0.7rem;
  margin-left: 0.35rem;
  transition: transform 0.2s ease;
}
.diagnostic-chevron--open { transform: rotate(180deg); }

/* Filter Bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-bar__presets {
  display: flex;
  gap: 0.375rem;
}

.filter-pill {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.3125rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.filter-pill:hover {
  border-color: var(--nav-label);
  color: var(--text-secondary);
}

.filter-pill--active {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
}

.filter-pill--active:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.filter-bar__dropdowns {
  display: flex;
  gap: 0.5rem;
  margin-left: 0.25rem;
}

.filter-select {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.3125rem 0.625rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-family: inherit;
  outline: none;
  cursor: pointer;
  transition: border-color 0.15s ease;
  max-width: 160px;
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23888'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  padding-right: 1.5rem;
}

.filter-select:hover {
  border-color: var(--nav-label);
}

.filter-select:focus {
  border-color: var(--accent);
}

.filter-select option {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.filter-bar__custom {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-datetime {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.3125rem 0.625rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s ease;
}

.filter-datetime:focus {
  border-color: var(--accent);
}

.filter-datetime::-webkit-calendar-picker-indicator {
  filter: invert(0.85) brightness(1.2);
  cursor: pointer;
}

.filter-separator {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.filter-bar__export {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
}

.filter-select--compact {
  max-width: 90px;
}

.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: var(--accent);
  border: 1px solid var(--accent);
  color: #ffffff;
  padding: 0.3125rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
  white-space: nowrap;
}

.export-btn:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 1200px) {
  .learning-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .stats-grid,
  .learning-grid {
    grid-template-columns: 1fr;
  }

  .rich-card { min-height: auto; }
}

@media (max-width: 768px) {
  .instructor-dashboard {
    padding: 1rem;
  }

  .dashboard-header {
    align-items: flex-start;
    padding: 1rem;
  }

  .dashboard-logo {
    width: 56px;
    height: 56px;
  }
}
</style>
