<template>
  <section class="readiness-panel">
    <div class="readiness-panel__head">
      <div>
        <p class="readiness-panel__eyebrow">Pilot instructor support</p>
        <h2 class="readiness-panel__title">Readiness and lab health</h2>
        <p class="readiness-panel__lead">
          A support prompt, not a grade. Every score is provisional until the
          rubric is calibrated. Platform-wide failures are excluded from learner
          risk and shown in lab health instead.
        </p>
      </div>
      <div class="readiness-panel__controls">
        <label class="readiness-panel__course">
          <span>Course</span>
          <select
            :value="courseId ?? ''"
            class="form-input form-input--sm"
            @change="selectCourse($event.target.value)"
          >
            <option value="">Select a course</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.code }} — {{ course.name }}
            </option>
          </select>
        </label>
        <button
          v-if="courseId"
          type="button"
          class="btn btn--secondary btn--sm"
          :disabled="loading"
          @click="fetchReadiness"
        >
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="!courseId" class="readiness-panel__empty">
      Select a course to see the support queue and lab health.
    </div>

    <div v-else-if="loading && !data" class="readiness-panel__empty" role="status">
      Loading readiness evidence...
    </div>

    <div v-else-if="error" class="readiness-panel__empty readiness-panel__empty--error" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary btn--sm" @click="fetchReadiness">
        Try again
      </button>
    </div>

    <template v-else-if="data">
      <div class="readiness-panel__tabs" role="tablist" aria-label="Readiness views">
        <button
          id="readiness-tab-queue"
          type="button"
          role="tab"
          class="readiness-panel__tab"
          :class="{ 'readiness-panel__tab--active': activeView === 'queue' }"
          :aria-selected="activeView === 'queue'"
          aria-controls="readiness-panel-queue"
          @click="activeView = 'queue'"
        >
          Support queue
          <span>{{ data.cohort.students }}</span>
        </button>
        <button
          id="readiness-tab-labs"
          type="button"
          role="tab"
          class="readiness-panel__tab"
          :class="{ 'readiness-panel__tab--active': activeView === 'labs' }"
          :aria-selected="activeView === 'labs'"
          aria-controls="readiness-panel-labs"
          @click="activeView = 'labs'"
        >
          Lab health
          <span>{{ data.lab_health.counts.degraded || 0 }} degraded</span>
        </button>
      </div>

      <div
        v-if="activeView === 'queue'"
        id="readiness-panel-queue"
        role="tabpanel"
        aria-labelledby="readiness-tab-queue"
        class="readiness-panel__view"
      >
        <div class="readiness-panel__bands">
          <span
            v-for="band in bandSummary"
            :key="band.key"
            class="readiness-band"
            :class="`readiness-band--${band.key}`"
          >
            <strong>{{ band.count }}</strong>
            {{ band.label }}
          </span>
        </div>

        <p class="readiness-panel__meta">
          {{ data.cohort.students }} learners · {{ data.cohort.assigned_exercises }} assigned exercises ·
          median {{ data.cohort.median_completed }} completed ·
          formula {{ data.formula_version }}
        </p>

        <div v-if="!data.students.length" class="readiness-panel__empty">
          No learners with enough evidence yet.
        </div>

        <div v-else class="readiness-list">
          <article
            v-for="student in visibleStudents"
            :key="student.user_id"
            class="readiness-card"
            :class="`readiness-card--${student.band}`"
          >
            <button
              type="button"
              class="readiness-card__summary"
              :aria-expanded="expandedStudent === student.user_id"
              @click="toggleStudent(student)"
            >
              <span class="readiness-card__identity">
                <strong>{{ student.display_name }}</strong>
                <small>{{ student.username }}</small>
              </span>
              <span class="readiness-card__score">
                <strong>{{ student.cwrs }}</strong>
                <small>{{ student.band_label }}</small>
              </span>
              <span class="readiness-card__confidence">{{ student.confidence }}</span>
              <span class="readiness-card__flags">
                <span v-for="flag in student.flags.slice(0, 2)" :key="flag" class="readiness-flag">
                  {{ flagLabel(flag) }}
                </span>
              </span>
              <span class="readiness-card__caret" aria-hidden="true">
                {{ expandedStudent === student.user_id ? '−' : '+' }}
              </span>
            </button>

            <div v-if="expandedStudent === student.user_id" class="readiness-card__detail">
              <div class="readiness-card__components">
                <div v-for="(value, key) in student.components" :key="key" class="readiness-component">
                  <div class="readiness-component__head">
                    <span>{{ componentLabel(key) }}</span>
                    <strong>{{ value == null ? 'Not measured' : value }}</strong>
                  </div>
                  <div
                    class="readiness-component__bar"
                    role="progressbar"
                    :aria-valuenow="value ?? 0"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    :aria-label="`${componentLabel(key)} risk`"
                  >
                    <span
                      :style="{ width: `${value ?? 0}%` }"
                      :class="{ 'is-missing': value == null }"
                    ></span>
                  </div>
                </div>
              </div>

              <div class="readiness-card__facts">
                <span><strong>{{ student.completed_exercises }}</strong> of {{ student.assigned_exercises }} completed</span>
                <span><strong>{{ student.days_since_activity ?? '—' }}</strong> days since activity</span>
                <span v-if="student.provisional" class="readiness-panel__provisional">Provisional evidence</span>
              </div>

              <div class="readiness-card__capabilities">
                <div class="readiness-card__capabilities-head">
                  <h3>Capability detail</h3>
                  <button
                    type="button"
                    class="btn btn--secondary btn--sm"
                    :disabled="capabilitiesLoading === student.user_id"
                    @click="loadCapabilities(student.user_id)"
                  >
                    {{ capabilitiesLoading === student.user_id ? 'Loading...' : 'Load capabilities' }}
                  </button>
                </div>
                <div v-if="capabilitiesError" class="readiness-panel__empty readiness-panel__empty--error" role="alert">
                  {{ capabilitiesError }}
                </div>
                <div v-else-if="capabilitiesFor === student.user_id && capabilities" class="capability-list">
                  <div v-for="axis in capabilities.axes" :key="axis.key" class="capability-row">
                    <span>{{ axis.label }}</span>
                    <div
                      class="capability-row__bar"
                      role="progressbar"
                      :aria-valuenow="axis.score ?? 0"
                      aria-valuemin="0"
                      aria-valuemax="100"
                      :aria-label="`${axis.label} capability`"
                    >
                      <span :style="{ width: `${axis.score ?? 0}%` }"></span>
                    </div>
                    <strong>{{ axis.score == null ? 'No evidence' : axis.score }}</strong>
                  </div>
                  <p class="readiness-panel__meta">{{ capabilities.disclaimer }}</p>
                </div>
              </div>
            </div>
          </article>

          <button
            v-if="data.students.length > defaultVisible"
            type="button"
            class="btn btn--secondary btn--sm readiness-panel__more"
            @click="showAllStudents = !showAllStudents"
          >
            {{ showAllStudents ? 'Show top 5' : `Show all ${data.students.length} learners` }}
          </button>
        </div>
      </div>

      <div
        v-else
        id="readiness-panel-labs"
        role="tabpanel"
        aria-labelledby="readiness-tab-labs"
        class="readiness-panel__view"
      >
        <div class="readiness-panel__bands">
          <span class="readiness-band readiness-band--critical_intervention">
            <strong>{{ data.lab_health.counts.degraded || 0 }}</strong> degraded
          </span>
          <span class="readiness-band readiness-band--high_risk">
            <strong>{{ data.lab_health.counts.warning || 0 }}</strong> warning
          </span>
          <span class="readiness-band readiness-band--monitor">
            <strong>{{ data.lab_health.counts.no_data || 0 }}</strong> no data
          </span>
          <span class="readiness-band readiness-band--healthy">
            <strong>{{ data.lab_health.counts.healthy || 0 }}</strong> healthy
          </span>
        </div>

        <p class="readiness-panel__meta">
          Low success is not automatically a defect. Review hints, abandonment,
          time, and the workbook before changing a lab.
        </p>

        <div v-if="!visibleLabs.length" class="readiness-panel__empty">
          No lab health issues in this view.
        </div>

        <div v-else class="table-wrapper">
          <table class="data-table readiness-table">
            <caption class="sr-only">Lab health for the selected course</caption>
            <thead>
              <tr>
                <th scope="col">Lab</th>
                <th scope="col">Status</th>
                <th scope="col">Started</th>
                <th scope="col">Success</th>
                <th scope="col">Abandon</th>
                <th scope="col">Hints</th>
                <th scope="col">Median time</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lab in visibleLabs" :key="lab.lab_id">
                <td>
                  <strong>{{ lab.name }}</strong>
                  <small>{{ lab.track || 'Uncategorized' }} · {{ lab.level || 'No level' }}</small>
                </td>
                <td>
                  <span class="lab-status" :class="`lab-status--${lab.status}`">
                    {{ labStatusLabel(lab.status) }}
                  </span>
                </td>
                <td>{{ lab.started }}</td>
                <td>{{ lab.success_rate == null ? '—' : `${lab.success_rate}%` }}</td>
                <td>{{ lab.abandonment_rate == null ? '—' : `${lab.abandonment_rate}%` }}</td>
                <td>{{ lab.median_hints ?? '—' }}</td>
                <td>{{ lab.median_minutes == null ? '—' : `${lab.median_minutes}m` }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <button
          v-if="hasHealthyLabs"
          type="button"
          class="btn btn--secondary btn--sm readiness-panel__more"
          @click="showHealthy = !showHealthy"
        >
          {{ showHealthy ? 'Hide healthy labs' : 'Show healthy labs' }}
        </button>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  courseId: { type: Number, default: null },
  courses: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:courseId'])

const data = ref(null)
const loading = ref(false)
const error = ref('')
const activeView = ref('queue')
const showAllStudents = ref(false)
const showHealthy = ref(false)
const expandedStudent = ref(null)
const capabilities = ref(null)
const capabilitiesFor = ref(null)
const capabilitiesLoading = ref(null)
const capabilitiesError = ref('')
const defaultVisible = 5

const bandSummary = computed(() => {
  const counts = data.value?.cohort?.band_counts || {}
  return [
    { key: 'critical_intervention', label: 'Critical', count: counts.critical_intervention || 0 },
    { key: 'high_risk', label: 'High', count: counts.high_risk || 0 },
    { key: 'elevated', label: 'Elevated', count: counts.elevated || 0 },
    { key: 'monitor', label: 'Monitor', count: counts.monitor || 0 },
    { key: 'healthy', label: 'Healthy', count: counts.healthy || 0 },
  ]
})

const visibleStudents = computed(() => {
  if (!data.value) return []
  return showAllStudents.value
    ? data.value.students
    : data.value.students.slice(0, defaultVisible)
})

const visibleLabs = computed(() => {
  if (!data.value) return []
  const labs = data.value.lab_health.labs || []
  return showHealthy.value ? labs : labs.filter((lab) => lab.status !== 'healthy')
})

const hasHealthyLabs = computed(() => (data.value?.lab_health.labs || []).some((lab) => lab.status === 'healthy'))

const componentLabel = (key) => ({
  performance: 'Performance',
  engagement: 'Engagement',
  progression: 'Progression',
  competency: 'Competency',
  behavioural: 'Learning behaviour',
  infrastructure: 'Learner-specific infrastructure',
}[key] || key)

const flagLabel = (flag) => ({
  performance: 'Performance',
  engagement: 'Engagement',
  progression: 'Falling behind',
  competency: 'Capability gap',
  abandonment: 'Abandonment',
  inactive: 'Inactive',
  no_completions: 'No completions',
}[flag] || flag)

const labStatusLabel = (status) => ({
  degraded: 'Degraded',
  warning: 'Warning',
  no_data: 'No data',
  healthy: 'Healthy',
}[status] || status)

function selectCourse(value) {
  emit('update:courseId', value ? Number(value) : null)
}

async function fetchReadiness() {
  if (!props.courseId) {
    data.value = null
    return
  }
  loading.value = true
  error.value = ''
  try {
    const { data: payload } = await axios.get(`/analytics/courses/${props.courseId}/readiness`)
    data.value = payload
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load readiness evidence.'
  } finally {
    loading.value = false
  }
}

async function toggleStudent(student) {
  if (expandedStudent.value === student.user_id) {
    expandedStudent.value = null
    return
  }
  expandedStudent.value = student.user_id
  capabilities.value = null
  capabilitiesFor.value = null
  capabilitiesError.value = ''
  await loadCapabilities(student.user_id)
}

async function loadCapabilities(userId) {
  capabilitiesLoading.value = userId
  capabilitiesError.value = ''
  try {
    const { data: payload } = await axios.get(
      `/analytics/courses/${props.courseId}/students/${userId}/capabilities`,
    )
    capabilities.value = payload
    capabilitiesFor.value = userId
  } catch (e) {
    capabilitiesError.value = e.response?.data?.detail || 'Could not load capability detail.'
  } finally {
    capabilitiesLoading.value = null
  }
}

watch(
  () => props.courseId,
  () => {
    showAllStudents.value = false
    showHealthy.value = false
    expandedStudent.value = null
    capabilities.value = null
    capabilitiesFor.value = null
    fetchReadiness()
  },
  { immediate: true },
)
</script>

<style scoped>
.readiness-panel {
  margin-top: 1.5rem;
  padding: 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.readiness-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.readiness-panel__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent-text);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.readiness-panel__title {
  margin: 0 0 0.3rem;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.readiness-panel__lead,
.readiness-panel__meta {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.6;
}

.readiness-panel__controls {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.readiness-panel__course {
  display: grid;
  gap: 0.2rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 600;
}

.readiness-panel__tabs {
  display: flex;
  gap: 0.35rem;
  margin: 1rem 0 0.75rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.readiness-panel__tab {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.7rem;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.readiness-panel__tab:hover,
.readiness-panel__tab--active {
  border-color: var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
}

.readiness-panel__tab span {
  color: var(--text-muted);
  font-size: 0.68rem;
}

.readiness-panel__view {
  display: grid;
  gap: 0.8rem;
}

.readiness-panel__bands {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.readiness-band {
  display: inline-flex;
  align-items: baseline;
  gap: 0.3rem;
  padding: 0.3rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 0.7rem;
}

.readiness-band strong {
  color: var(--text-primary);
  font-size: 0.85rem;
}

.readiness-band--critical_intervention {
  border-color: var(--danger);
  background: var(--danger-bg);
  color: var(--danger);
}

.readiness-band--high_risk {
  border-color: var(--warning);
  background: var(--warning-bg);
  color: var(--warning);
}

.readiness-band--elevated,
.readiness-band--monitor {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.readiness-band--healthy {
  border-color: var(--success);
  background: var(--success-bg);
  color: var(--success);
}

.readiness-list {
  display: grid;
  gap: 0.55rem;
}

.readiness-card {
  border: 1px solid var(--border-color);
  border-radius: 9px;
  background: var(--bg-primary);
  overflow: hidden;
}

.readiness-card--critical_intervention {
  border-left: 3px solid var(--danger);
}

.readiness-card--high_risk {
  border-left: 3px solid var(--warning);
}

.readiness-card--elevated,
.readiness-card--monitor {
  border-left: 3px solid var(--accent);
}

.readiness-card--healthy {
  border-left: 3px solid var(--success);
}

.readiness-card__summary {
  display: grid;
  grid-template-columns: minmax(10rem, 1.4fr) auto auto minmax(8rem, 1fr) auto;
  align-items: center;
  gap: 0.7rem;
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 0;
  background: transparent;
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
}

.readiness-card__summary:hover {
  background: var(--hover-bg);
}

.readiness-card__identity,
.readiness-card__score {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.readiness-card__identity small,
.readiness-card__score small {
  color: var(--text-muted);
  font-size: 0.68rem;
}

.readiness-card__score {
  text-align: right;
}

.readiness-card__score strong {
  font-size: 1.15rem;
}

.readiness-card__confidence {
  color: var(--text-muted);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.readiness-card__flags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.readiness-flag {
  padding: 0.1rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 0.64rem;
}

.readiness-card__caret {
  color: var(--text-muted);
  font-size: 1rem;
}

.readiness-card__detail {
  display: grid;
  gap: 0.75rem;
  padding: 0 0.75rem 0.8rem;
}

.readiness-card__components {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
  gap: 0.5rem 0.8rem;
}

.readiness-component {
  display: grid;
  gap: 0.25rem;
}

.readiness-component__head {
  display: flex;
  justify-content: space-between;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.readiness-component__head strong {
  color: var(--text-primary);
}

.readiness-component__bar,
.capability-row__bar {
  height: 5px;
  border-radius: 999px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.readiness-component__bar span,
.capability-row__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--purple));
}

.readiness-component__bar span.is-missing {
  width: 0 !important;
}

.readiness-card__facts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.9rem;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.readiness-panel__provisional {
  color: var(--warning);
}

.readiness-card__capabilities {
  padding-top: 0.6rem;
  border-top: 1px solid var(--border-color);
}

.readiness-card__capabilities-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.readiness-card__capabilities-head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.82rem;
}

.capability-list {
  display: grid;
  gap: 0.35rem;
  margin-top: 0.5rem;
}

.capability-row {
  display: grid;
  grid-template-columns: minmax(8rem, 1fr) minmax(6rem, 1.5fr) 3rem;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.capability-row strong {
  color: var(--text-primary);
  text-align: right;
}

.readiness-table td small {
  display: block;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.lab-status {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
}

.lab-status--degraded {
  background: var(--danger-bg);
  color: var(--danger);
}

.lab-status--warning {
  background: var(--warning-bg);
  color: var(--warning);
}

.lab-status--no_data {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.lab-status--healthy {
  background: var(--success-bg);
  color: var(--success);
}

.readiness-panel__empty {
  padding: 1rem;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.readiness-panel__empty--error {
  border-color: var(--danger);
  color: var(--danger);
}

.readiness-panel__more {
  justify-self: start;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 720px) {
  .readiness-card__summary {
    grid-template-columns: 1fr auto auto;
  }

  .readiness-card__confidence,
  .readiness-card__flags {
    display: none;
  }
}
</style>
