<template>
  <div class="student-dashboard">
    <div class="dashboard-header">
      <img src="/ocr-logo-dark.png" alt="OpenCyberRange" class="dashboard-logo" />
      <div class="dashboard-header__text">
        <h1 class="page-title">Welcome, {{ username }}</h1>
        <p class="page-subtitle">Your training dashboard</p>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Next Objective -->
      <div class="card card--objective">
        <div class="card__header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="card__icon card__icon--blue">
            <circle cx="12" cy="12" r="10"/>
            <polygon points="10 8 16 12 10 16 10 8"/>
          </svg>
          <h2 class="card__title">Next Objective</h2>
        </div>
        <div v-if="data.next_objective" class="objective-info">
          <span class="objective-track">{{ data.next_objective.track_name }} - {{ data.next_objective.level_name }}</span>
          <h3 class="objective-name">{{ data.next_objective.lab_name }}</h3>
          <router-link :to="resumeLink" class="btn btn--primary">
            Resume Training
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
              <line x1="5" y1="12" x2="19" y2="12"/>
              <polyline points="12 5 19 12 12 19"/>
            </svg>
          </router-link>
        </div>
        <div v-else class="objective-complete">
          <span class="complete-bar"></span>
          <p>All labs completed!</p>
        </div>
      </div>

      <!-- Progress -->
      <div class="card card--progress">
        <div class="card__header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="card__icon card__icon--green">
            <line x1="12" y1="20" x2="12" y2="10"/>
            <line x1="18" y1="20" x2="18" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="16"/>
          </svg>
          <h2 class="card__title">My Progress</h2>
        </div>
        <div class="progress-info">
          <div class="progress-bar-wrapper">
            <div class="progress-bar">
              <div class="progress-bar__fill" :style="{ width: data.progress_percent + '%' }"></div>
            </div>
            <span class="progress-percent">{{ data.progress_percent }}%</span>
          </div>
          <span class="progress-count">{{ data.completed_labs }} / {{ data.total_labs }} labs completed</span>
        </div>
      </div>

      <!-- VPN Status -->
      <div class="card card--vpn">
        <div class="card__header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="card__icon card__icon--cyan">
            <path d="M12 2L3 7V12C3 16.97 7.02 21.45 12 22C16.98 21.45 21 16.97 21 12V7L12 2Z"/>
          </svg>
          <h2 class="card__title">VPN Status</h2>
        </div>
        <div class="vpn-info">
          <div class="vpn-row">
            <span class="vpn-dot" :class="data.vpn_status?.vpn_registered ? 'vpn-dot--on' : 'vpn-dot--off'"></span>
            <span class="vpn-text">{{ data.vpn_status?.vpn_registered ? 'Registered' : 'Not Configured' }}</span>
          </div>
          <span v-if="data.vpn_status?.client_ip" class="vpn-ip">{{ data.vpn_status.client_ip }}</span>
          <router-link to="/vpn-setup" class="btn btn--outline btn--sm">
            {{ data.vpn_status?.has_config ? 'Download Config' : 'Setup VPN' }}
          </router-link>
        </div>
      </div>

      <!-- Rank (only shown when enrolled in a course) -->
      <div v-if="data.scoreboard_rank" class="card card--rank">
        <div class="card__header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="card__icon card__icon--amber">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          <h2 class="card__title">Your Rank</h2>
        </div>
        <div class="rank-info">
          <span class="rank-number">#{{ data.scoreboard_rank }}</span>
          <span class="rank-course" v-if="data.course_name">in {{ data.course_name }}</span>
        </div>
      </div>
    </div>

    <!-- Completion matrix: courses x levels -->
    <div v-if="matrix.columns.length" class="card card--matrix">
      <div class="card__header">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="card__icon card__icon--purple">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <line x1="9" y1="3" x2="9" y2="21"/>
          <line x1="15" y1="3" x2="15" y2="21"/>
          <line x1="3" y1="9" x2="21" y2="9"/>
          <line x1="3" y1="15" x2="21" y2="15"/>
        </svg>
        <div>
          <h2 class="card__title">Exercise Completion Matrix</h2>
          <p class="matrix-subtitle">Exercises completed per course and level</p>
        </div>
      </div>

      <div class="matrix-scroll">
        <table class="matrix-table">
          <thead>
            <tr>
              <th class="matrix-corner">Course</th>
              <th v-for="col in matrix.columns" :key="col.key" class="matrix-col-head">
                <span class="matrix-track">{{ col.track_name }}</span>
                <span class="matrix-level">Level {{ col.level_number }} &middot; {{ col.level_name }}</span>
              </th>
              <th class="matrix-col-head matrix-col-head--total">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in matrix.rows" :key="row.course_id">
              <th class="matrix-row-head">
                <span class="matrix-course-code">{{ row.course_code }}</span>
                <span class="matrix-course-name">{{ row.course_name }}</span>
              </th>
              <td
                v-for="col in matrix.columns"
                :key="col.key"
                class="matrix-cell"
                :class="cellClass(row.cells[col.key])"
              >
                <template v-if="row.cells[col.key] && row.cells[col.key].total">
                  {{ row.cells[col.key].completed }}/{{ row.cells[col.key].total }}
                </template>
                <span v-else class="matrix-empty">&ndash;</span>
              </td>
              <td class="matrix-cell matrix-cell--total">{{ row.completed }}/{{ row.total }}</td>
            </tr>
          </tbody>
          <tfoot v-if="matrix.rows.length > 1">
            <tr>
              <th class="matrix-row-head">All courses</th>
              <td
                v-for="col in matrix.columns"
                :key="col.key"
                class="matrix-cell"
                :class="cellClass(matrix.totals.cells[col.key])"
              >
                <template v-if="matrix.totals.cells[col.key] && matrix.totals.cells[col.key].total">
                  {{ matrix.totals.cells[col.key].completed }}/{{ matrix.totals.cells[col.key].total }}
                </template>
                <span v-else class="matrix-empty">&ndash;</span>
              </td>
              <td class="matrix-cell matrix-cell--total">
                {{ matrix.totals.completed }}/{{ matrix.totals.total }}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div class="matrix-legend">
        <span><i class="matrix-swatch matrix-swatch--complete"></i> Complete</span>
        <span><i class="matrix-swatch matrix-swatch--partial"></i> In progress</span>
        <span><i class="matrix-swatch matrix-swatch--empty"></i> Not started</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '../api/axios'

const data = ref({
  next_objective: null,
  progress_percent: 0,
  total_labs: 0,
  completed_labs: 0,
  vpn_status: null,
  scoreboard_rank: null,
  course_name: null,
})

const username = computed(() => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (!user.username) return 'Student'
    return user.username.charAt(0).toUpperCase() + user.username.slice(1).toLowerCase()
  } catch {
    return 'Student'
  }
})

// Deep-link "Resume Training" straight to the next incomplete lab. The track
// page opens the lab panel from the labId query param. Older backends that do
// not send track_slug fall back to the exercises list.
const resumeLink = computed(() => {
  const obj = data.value.next_objective
  if (obj?.track_slug && obj?.lab_id) {
    return { path: `/exercises/${obj.track_slug}`, query: { labId: String(obj.lab_id) } }
  }
  return '/exercises'
})

const fetchDashboard = async () => {
  try {
    const res = await axios.get('/dashboard/student')
    data.value = res.data
  } catch (e) {
    console.error('Failed to fetch student dashboard:', e)
  }
}

const matrix = computed(() => (
  data.value.completion_matrix || {
    columns: [],
    rows: [],
    totals: { cells: {}, completed: 0, total: 0 },
  }
))

// A cell with no assigned exercises is rendered as a dash rather than 0/0.
const cellClass = (cell) => {
  if (!cell || !cell.total) return 'matrix-cell--empty'
  if (cell.completed >= cell.total) return 'matrix-cell--complete'
  if (cell.completed > 0) return 'matrix-cell--partial'
  return 'matrix-cell--empty'
}

onMounted(() => {
  fetchDashboard()
})
</script>

<style scoped>
.student-dashboard {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.dashboard-logo {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
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
  color: var(--text-muted);
  font-size: 0.9375rem;
  margin: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Cards */
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}

.card__header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.card__icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.card__icon--blue { color: var(--accent); }
.card__icon--green { color: var(--success); }
.card__icon--cyan { color: #06b6d4; }
.card__icon--amber { color: var(--warning); }

.card__title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

/* Objective */
.objective-track {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: block;
  margin-bottom: 0.25rem;
}

.objective-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
}

.objective-complete {
  text-align: center;
  padding: 1rem 0;
}

.complete-bar {
  display: inline-block;
  width: 40px;
  height: 4px;
  border-radius: 2px;
  background: var(--success);
  margin-bottom: 0.5rem;
}

.objective-complete p {
  color: var(--text-secondary);
  margin: 0;
}

/* Progress */
.progress-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar {
  flex: 1;
  height: 10px;
  background: var(--bg-tertiary);
  border-radius: 999px;
  overflow: hidden;
}

.progress-bar__fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #22c55e);
  border-radius: 999px;
  transition: width 0.6s ease;
}

.progress-percent {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 3rem;
  text-align: right;
}

.progress-count {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

/* VPN */
.vpn-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.vpn-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.vpn-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.vpn-dot--on {
  background: var(--success);
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
}

.vpn-dot--off {
  background: var(--nav-label);
}

.vpn-text {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text-primary);
}

.vpn-ip {
  font-family: monospace;
  font-size: 0.875rem;
  color: var(--accent);
}

/* Rank */
.rank-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.rank-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--warning);
  line-height: 1.2;
}

.rank-course {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.btn--primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.btn--primary:hover {
  background: linear-gradient(135deg, #2563eb, #1e40af);
}

.btn--outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn--outline:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.btn--sm {
  padding: 0.375rem 0.875rem;
  font-size: 0.75rem;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* Completion matrix */
.card--matrix {
  margin-top: 1.5rem;
}

.card__icon--purple { color: #a78bfa; }

.matrix-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.matrix-scroll {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
  min-width: 560px;
}

.matrix-table th,
.matrix-table td {
  padding: 0.55rem 0.65rem;
  border-bottom: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
  text-align: center;
  white-space: nowrap;
}

.matrix-table thead th {
  background: var(--bg-tertiary);
  vertical-align: bottom;
}

.matrix-table tbody tr:last-child th,
.matrix-table tbody tr:last-child td {
  border-bottom: 0;
}

.matrix-table th:last-child,
.matrix-table td:last-child {
  border-right: 0;
}

.matrix-corner,
.matrix-row-head {
  text-align: left;
  position: sticky;
  left: 0;
  background: var(--bg-secondary);
  z-index: 1;
}

.matrix-table thead .matrix-corner {
  background: var(--bg-tertiary);
}

.matrix-row-head {
  min-width: 150px;
  max-width: 190px;
  white-space: normal;
}

.matrix-course-code {
  display: block;
  font-weight: 700;
  color: var(--text-primary);
}

.matrix-course-name {
  display: block;
  font-size: 0.68rem;
  font-weight: 400;
  color: var(--text-muted);
}

.matrix-col-head {
  min-width: 92px;
}

.matrix-track {
  display: block;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
}

.matrix-level {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.matrix-col-head--total {
  min-width: 64px;
}

.matrix-cell {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  color: var(--text-secondary);
}

.matrix-cell--complete {
  background: rgba(34, 197, 94, 0.16);
  color: var(--success);
}

.matrix-cell--partial {
  background: rgba(245, 158, 11, 0.16);
  color: var(--warning);
}

.matrix-cell--empty {
  color: var(--text-muted);
}

.matrix-cell--total {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.matrix-empty {
  opacity: 0.5;
}

.matrix-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 0.75rem;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.matrix-legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.matrix-swatch {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  display: inline-block;
}

.matrix-swatch--complete { background: rgba(34, 197, 94, 0.5); }
.matrix-swatch--partial { background: rgba(245, 158, 11, 0.5); }
.matrix-swatch--empty { background: var(--bg-tertiary); }

/* Responsive */
@media (max-width: 768px) {
  .student-dashboard {
    padding: 1rem;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
