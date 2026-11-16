<template>
  <section class="consent-panel" aria-labelledby="consent-panel-title">
    <div class="consent-panel__head">
      <div>
        <h2 id="consent-panel-title" class="section-title">AI and career data</h2>
        <p class="consent-panel__lead">
          These controls govern derived intelligence: Cyber DNA, Cyber GPS,
          portfolio snapshots, and future AI coaching. Revoking a consent blocks
          the feature immediately and deletes its derived data. Your learning
          record, completions, certificates, and achievements are kept.
        </p>
      </div>
      <button
        type="button"
        class="btn btn--secondary btn--sm"
        :disabled="loading || saving"
        @click="load"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <p v-if="loading" class="consent-panel__status" role="status">
      Loading your consent state...
    </p>

    <p v-if="errorMessage" class="error-message" role="alert">
      {{ errorMessage }}
    </p>
    <p v-if="successMessage" class="success-message" role="status">
      {{ successMessage }}
    </p>

    <div v-if="!loading && consentList.length" class="consent-grid">
      <article
        v-for="row in consentList"
        :key="row.consent_type"
        class="consent-card"
        :class="`consent-card--${statusFor(row).tone}`"
      >
        <header class="consent-card__head">
          <h3>{{ row.label }}</h3>
          <span class="consent-badge" :class="`consent-badge--${statusFor(row).tone}`">
            {{ statusFor(row).label }}
          </span>
        </header>

        <p class="consent-card__description">{{ row.description }}</p>

        <p v-if="row.granted" class="consent-card__meta">
          Processing is on<template v-if="row.version"> · consent version {{ row.version }}</template>.
        </p>
        <p v-else-if="row.revocation_in_progress" class="consent-card__meta">
          Removal is running. The feature is already blocked.
        </p>
        <p v-else class="consent-card__meta">
          Processing is off. Enabling it allows new activity only; deleted data is
          not restored.
        </p>

        <details class="consent-card__details">
          <summary>What revocation removes</summary>
          <ul>
            <li v-for="item in row.removed" :key="item">{{ item }}</li>
          </ul>
        </details>
        <details class="consent-card__details">
          <summary>What is kept</summary>
          <ul>
            <li v-for="item in row.kept" :key="item">{{ item }}</li>
          </ul>
        </details>

        <p v-if="latestRevocation(row)" class="consent-card__revocation">
          <strong>{{ revocationLabel(latestRevocation(row).status) }}</strong>
          <template v-if="latestRevocation(row).requested_at">
            · requested {{ formatDate(latestRevocation(row).requested_at) }}
          </template>
          <template v-if="latestRevocation(row).verified_at">
            · verified {{ formatDate(latestRevocation(row).verified_at) }}
          </template>
          <template v-if="latestRevocation(row).audit_id">
            <br />
            <span class="consent-card__audit">
              Audit {{ latestRevocation(row).audit_id.slice(0, 8) }}
              · {{ latestRevocation(row).jobs.filter(job => job.status === 'complete').length }}
              removal step(s) complete
            </span>
          </template>
        </p>

        <div class="consent-card__actions">
          <button
            v-if="row.granted && !row.revocation_in_progress"
            type="button"
            class="btn btn--danger btn--sm"
            :disabled="!!saving"
            @click="startConfirm(row.consent_type)"
          >
            Revoke consent
          </button>
          <button
            v-else-if="!row.revocation_in_progress"
            type="button"
            class="btn btn--primary btn--sm"
            :disabled="!!saving"
            @click="enable(row)"
          >
            {{ saving === row.consent_type ? 'Enabling...' : 'Enable' }}
          </button>
          <span v-else class="consent-card__waiting">
            <span class="consent-card__spinner" aria-hidden="true"></span>
            Removal in progress — this page refreshes automatically.
          </span>
        </div>

        <div
          v-if="confirming === row.consent_type"
          class="consent-card__confirm"
          role="alert"
        >
          <p>
            Revoke <strong>{{ row.label }}</strong> and delete its derived data?
            This takes effect immediately for processing. Removal is queued now
            and verified after it runs.
          </p>
          <label class="consent-card__reason">
            <span>Reason (optional)</span>
            <input
              v-model="reason"
              type="text"
              maxlength="500"
              placeholder="Why are you revoking this?"
              :disabled="!!saving"
            />
          </label>
          <div class="consent-card__confirm-actions">
            <button
              type="button"
              class="btn btn--danger btn--sm"
              :disabled="!!saving"
              @click="revoke(row)"
            >
              {{ saving === row.consent_type ? 'Revoking...' : 'Yes, revoke and delete' }}
            </button>
            <button
              type="button"
              class="btn btn--secondary btn--sm"
              :disabled="!!saving"
              @click="cancelConfirm"
            >
              Keep my consent
            </button>
          </div>
        </div>
      </article>
    </div>

    <section v-if="!loading && remainingRows.length" class="consent-remaining">
      <h3>Educational records that remain</h3>
      <p>
        Revocation never removes these records. They stay part of your learning
        record and transcript.
      </p>
      <ul>
        <li v-for="row in remainingRows" :key="row.key">
          <strong>{{ row.value }}</strong> {{ row.label.toLowerCase() }}
        </li>
      </ul>
    </section>

    <section v-if="!loading && history.length" class="consent-history">
      <h3>Recent consent history</h3>
      <ul>
        <li v-for="(row, index) in history" :key="`${row.occurred_at}-${index}`">
          <span class="consent-history__action" :class="`consent-history__action--${row.action}`">
            {{ row.action === 'revoke' ? 'Revoked' : 'Granted' }}
          </span>
          <span>{{ labelFor(row.consent_type) }}</span>
          <span class="consent-history__meta">
            version {{ row.version }}
            <template v-if="row.occurred_at"> · {{ formatDate(row.occurred_at) }}</template>
          </span>
        </li>
      </ul>
    </section>

    <p class="consent-panel__notice">
      Read the <router-link to="/privacy">privacy notice</router-link> for how
      personal information is handled, or contact the privacy officer at
      <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>.
    </p>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import axios from '../api/axios'

const loading = ref(true)
const saving = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const consents = ref({})
const revocations = ref([])
const history = ref([])
const remaining = ref({})
const confirming = ref('')
const reason = ref('')
let pollTimer = null

const consentList = computed(() => Object.values(consents.value))

const remainingRows = computed(() => {
  const labels = {
    completed_exercises: 'Completed exercises',
    achievements: 'Achievements',
    course_enrollments: 'Course enrolments',
  }
  return Object.entries(remaining.value || {})
    .filter(([, value]) => Number(value) > 0)
    .map(([key, value]) => ({
      key,
      label: labels[key] || key.replaceAll('_', ' '),
      value,
    }))
})

const needsPolling = computed(() => {
  if (consentList.value.some((row) => row.revocation_in_progress)) return true
  return revocations.value.some((row) =>
    ['pending', 'running', 'verifying'].includes(row.status)
  )
})

const applyDashboard = (data) => {
  consents.value = data.consents || {}
  revocations.value = data.revocations || []
  history.value = data.history || []
  remaining.value = data.remaining_records || {}
}

const load = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await axios.get('/consent/')
    applyDashboard(data)
  } catch (e) {
    errorMessage.value =
      e.response?.data?.detail || 'Could not load your consent settings.'
  } finally {
    loading.value = false
  }
}

const statusFor = (row) => {
  if (row.revocation_in_progress) return { label: 'Removing data', tone: 'pending' }
  if (row.granted) return { label: 'Active', tone: 'active' }
  if (row.revoked_at) return { label: 'Revoked', tone: 'revoked' }
  return { label: 'Not enabled', tone: 'off' }
}

const latestRevocation = (row) =>
  revocations.value.find((item) => item.consent_type === row.consent_type)

const revocationLabel = (status) => {
  const labels = {
    pending: 'Removal queued',
    running: 'Removal running',
    verifying: 'Verifying removal',
    complete: 'Removal complete',
    failed: 'Removal needs attention',
    cancelled: 'Revocation cancelled',
  }
  return labels[status] || 'Removal status unknown'
}

const labelFor = (consentType) =>
  consents.value[consentType]?.label || consentType.replaceAll('_', ' ')

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

const startConfirm = (consentType) => {
  confirming.value = consentType
  reason.value = ''
  successMessage.value = ''
}

const cancelConfirm = () => {
  confirming.value = ''
  reason.value = ''
}

const revoke = async (row) => {
  saving.value = row.consent_type
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const { data } = await axios.post(`/consent/${row.consent_type}/revoke`, {
      reason: reason.value.trim() || null,
    })
    successMessage.value =
      data.message ||
      'Consent revoked. The feature is blocked while derived data is removed.'
    confirming.value = ''
    reason.value = ''
    await load()
  } catch (e) {
    errorMessage.value =
      e.response?.data?.detail || 'Could not revoke this consent.'
  } finally {
    saving.value = ''
  }
}

const enable = async (row) => {
  saving.value = row.consent_type
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const { data } = await axios.post(`/consent/${row.consent_type}/grant`)
    successMessage.value =
      data.message ||
      'Consent enabled. New activity may be processed again.'
    await load()
  } catch (e) {
    errorMessage.value =
      e.response?.data?.detail || 'Could not enable this consent.'
  } finally {
    saving.value = ''
  }
}

const syncPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  if (needsPolling.value) {
    pollTimer = setInterval(() => {
      if (!loading.value && !saving.value) load()
    }, 5000)
  }
}

watch(needsPolling, syncPolling, { immediate: true })

onMounted(load)
onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.consent-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.consent-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.consent-panel .section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.consent-panel__lead {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0 0 1rem;
}

.consent-panel__status {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.consent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
  gap: 1rem;
}

.consent-card {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
}

.consent-card--active {
  border-color: color-mix(in srgb, var(--success, #10b981) 30%, var(--border-color));
}

.consent-card--pending {
  border-color: color-mix(in srgb, var(--warning, #f59e0b) 40%, var(--border-color));
}

.consent-card--revoked {
  border-color: color-mix(in srgb, var(--danger, #ef4444) 30%, var(--border-color));
}

.consent-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.consent-card__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
}

.consent-badge {
  flex: 0 0 auto;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary, var(--bg-secondary));
  color: var(--text-secondary);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.consent-badge--active {
  color: var(--success-text, #0a6b3a);
  background: var(--success-bg, rgba(16, 185, 129, 0.12));
  border-color: color-mix(in srgb, var(--success, #10b981) 45%, var(--border-color));
}

.consent-badge--pending {
  color: var(--warning-text, #7a4b00);
  background: var(--warning-bg, rgba(245, 158, 11, 0.12));
  border-color: color-mix(in srgb, var(--warning, #f59e0b) 45%, var(--border-color));
}

.consent-badge--revoked {
  color: var(--danger-text, #8b1e1e);
  background: var(--danger-bg, rgba(239, 68, 68, 0.12));
  border-color: color-mix(in srgb, var(--danger, #ef4444) 45%, var(--border-color));
}

.consent-card__description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.55;
}

.consent-card__meta {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.78rem;
  line-height: 1.5;
}

.consent-card__details {
  border-top: 1px solid var(--border-color);
  padding-top: 0.45rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.consent-card__details summary {
  cursor: pointer;
  color: var(--text-primary);
  font-weight: 600;
}

.consent-card__details ul {
  margin: 0.35rem 0 0;
  padding-left: 1.1rem;
  line-height: 1.5;
}

.consent-card__revocation {
  margin: 0;
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  background: var(--bg-tertiary, var(--bg-secondary));
  color: var(--text-secondary);
  font-size: 0.76rem;
  line-height: 1.5;
}

.consent-card__audit {
  color: var(--text-muted);
  font-family: ui-monospace, 'JetBrains Mono', monospace;
  font-size: 0.7rem;
}

.consent-card__actions {
  margin-top: auto;
  padding-top: 0.35rem;
}

.consent-card__waiting {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.consent-card__spinner {
  width: 0.8rem;
  height: 0.8rem;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: consent-spin 0.9s linear infinite;
}

@keyframes consent-spin {
  to { transform: rotate(360deg); }
}

.consent-card__confirm {
  margin-top: 0.5rem;
  padding: 0.75rem;
  border: 1px solid color-mix(in srgb, var(--danger, #ef4444) 40%, var(--border-color));
  border-radius: 10px;
  background: var(--danger-bg, rgba(239, 68, 68, 0.1));
}

.consent-card__confirm p {
  margin: 0 0 0.55rem;
  color: var(--text-primary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.consent-card__reason {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.6rem;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.consent-card__reason input {
  width: 100%;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font: inherit;
}

.consent-card__confirm-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.consent-remaining,
.consent-history {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.consent-remaining h3,
.consent-history h3 {
  margin: 0 0 0.35rem;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.consent-remaining p {
  margin: 0 0 0.5rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.consent-remaining ul,
.consent-history ul {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.6;
}

.consent-history li {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: baseline;
}

.consent-history__action {
  font-weight: 700;
  color: var(--text-primary);
}

.consent-history__action--revoke {
  color: var(--danger, #ef4444);
}

.consent-history__action--grant {
  color: var(--success, #10b981);
}

.consent-history__meta {
  color: var(--text-muted);
  font-size: 0.72rem;
}

.consent-panel__notice {
  margin: 1.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.75rem;
  line-height: 1.5;
}

.consent-panel__notice a {
  color: var(--accent);
}

@media (max-width: 640px) {
  .consent-panel__head,
  .consent-card__confirm-actions {
    flex-direction: column;
  }

  .consent-panel__head .btn,
  .consent-card__confirm-actions .btn,
  .consent-card__actions .btn {
    width: 100%;
  }
}
</style>
