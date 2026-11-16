<template>
  <section class="security-center" aria-labelledby="security-center-title">
    <header class="panel-header">
      <div>
        <h2 id="security-center-title" class="panel-title">Security center</h2>
        <p class="security-center__sub">
          Append-only security, audit, and privacy events; emergency access; and
          non-human service identities.
        </p>
      </div>
      <button type="button" class="btn btn--outline btn--sm" :disabled="loading" @click="refreshAll">
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </header>

    <div class="sub-tabs" role="tablist" aria-label="Security workspace">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        role="tab"
        :aria-selected="activeView === tab.key"
        :class="['sub-tab', { active: activeView === tab.key }]"
        @click="activeView = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <p v-if="error" class="security-state security-state--error" role="alert">{{ error }}</p>

    <template v-if="activeView === 'events'">
      <div class="security-summary" v-if="summary">
        <div class="security-summary__card">
          <span>Total</span><strong>{{ summary.total }}</strong>
        </div>
        <div class="security-summary__card">
          <span>Critical</span><strong>{{ summary.by_severity?.critical || 0 }}</strong>
        </div>
        <div class="security-summary__card">
          <span>Warnings</span><strong>{{ summary.by_severity?.warning || 0 }}</strong>
        </div>
        <div class="security-summary__card">
          <span>Denied</span><strong>{{ summary.by_outcome?.denied || 0 }}</strong>
        </div>
      </div>

      <div class="security-filters">
        <label>
          <span>Category</span>
          <select v-model="filters.category" @change="loadEvents">
            <option value="">All</option>
            <option value="security">Security</option>
            <option value="audit">Audit</option>
            <option value="privacy">Privacy</option>
          </select>
        </label>
        <label>
          <span>Severity</span>
          <select v-model="filters.severity" @change="loadEvents">
            <option value="">All</option>
            <option value="info">Info</option>
            <option value="notice">Notice</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
        </label>
        <label class="security-filters__search">
          <span>Search</span>
          <input v-model.trim="filters.search" type="search" placeholder="event, actor, path, target" @keyup.enter="loadEvents" />
        </label>
        <button type="button" class="btn btn--primary btn--sm" @click="loadEvents">Apply</button>
      </div>

      <div class="table-container" v-if="events.length">
        <table class="data-table">
          <caption class="visually-hidden">Security events, newest first</caption>
          <thead>
            <tr>
              <th>Time</th>
              <th>Severity</th>
              <th>Event</th>
              <th>Actor</th>
              <th>Target / path</th>
              <th>Outcome</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in events" :key="row.id">
              <td class="security-mono">{{ formatTime(row.occurred_at) }}</td>
              <td><span :class="['security-badge', `security-badge--${row.severity}`]">{{ row.severity }}</span></td>
              <td>
                <strong>{{ row.event_type }}</strong>
                <div v-if="row.action && row.action !== row.event_type" class="security-meta">{{ row.action }}</div>
              </td>
              <td>
                {{ row.actor_username || row.actor_id || 'system' }}
                <div v-if="row.actor_role" class="security-meta">{{ row.actor_role }}</div>
              </td>
              <td>
                {{ row.target_label || row.target_id || row.path || '-' }}
                <div v-if="row.path" class="security-meta security-mono">{{ row.path }}</div>
              </td>
              <td>{{ row.outcome }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="security-state">No events match the current filters.</p>
    </template>

    <template v-else-if="activeView === 'break-glass'">
      <form class="security-form" @submit.prevent="requestBreakGlass">
        <h3>Request emergency access</h3>
        <p class="security-meta">
          MFA is required. The grant is time-bound, scoped when a learner id is
          supplied, and every use is a critical event.
        </p>
        <label>
          <span>Permission</span>
          <select v-model="grantForm.permission" required>
            <option v-for="item in eligiblePermissions" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>
        <label>
          <span>Reason (minimum 10 characters)</span>
          <textarea v-model.trim="grantForm.reason" rows="3" required minlength="10" />
        </label>
        <div class="security-form__row">
          <label>
            <span>Reference</span>
            <input v-model.trim="grantForm.reference" placeholder="INC-42" />
          </label>
          <label>
            <span>Minutes</span>
            <input v-model.number="grantForm.minutes" type="number" min="1" max="1440" />
          </label>
          <label>
            <span>Learner id (optional)</span>
            <input v-model.number="grantForm.user_id" type="number" min="1" />
          </label>
        </div>
        <button type="submit" class="btn btn--danger btn--sm" :disabled="saving">
          {{ saving ? 'Requesting...' : 'Request break-glass' }}
        </button>
      </form>

      <div class="table-container" v-if="grants.length">
        <table class="data-table">
          <caption class="visually-hidden">Break-glass grants</caption>
          <thead>
            <tr><th>User</th><th>Permission</th><th>Status</th><th>Expires</th><th>Uses</th><th>Review</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in grants" :key="row.id">
              <td>{{ row.username || row.user_id }}</td>
              <td>{{ row.permission }}<div v-if="row.reference" class="security-meta">{{ row.reference }}</div></td>
              <td><span :class="['security-badge', `security-badge--${row.status}`]">{{ row.status }}</span></td>
              <td class="security-mono">{{ formatTime(row.expires_at) }}</td>
              <td>{{ row.use_count }}</td>
              <td>{{ row.review_status }}</td>
              <td class="security-actions">
                <button v-if="row.status === 'pending'" type="button" class="btn btn--outline btn--sm" @click="approveGrant(row)">Approve</button>
                <button v-if="row.status === 'active' || row.status === 'pending'" type="button" class="btn btn--outline btn--sm" @click="revokeGrant(row)">Revoke</button>
                <button v-if="row.review_status !== 'reviewed'" type="button" class="btn btn--outline btn--sm" @click="reviewGrant(row)">Review</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="security-state">No break-glass grants.</p>
    </template>

    <template v-else-if="activeView === 'services'">
      <form class="security-form" @submit.prevent="createService">
        <h3>Create a service identity</h3>
        <p class="security-meta">
          The raw token is shown once. A service identity has no password login and
          only the scopes you select.
        </p>
        <div class="security-form__row">
          <label>
            <span>Name</span>
            <input v-model.trim="serviceForm.name" required minlength="3" />
          </label>
          <label>
            <span>Days</span>
            <input v-model.number="serviceForm.days" type="number" min="1" max="365" />
          </label>
        </div>
        <label>
          <span>Scopes</span>
          <select v-model="serviceForm.scopes" multiple size="6" class="security-scopes">
            <option v-for="item in serviceScopes" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>
        <button type="submit" class="btn btn--primary btn--sm" :disabled="saving">
          {{ saving ? 'Creating...' : 'Create service identity' }}
        </button>
        <p v-if="newServiceToken" class="security-token">
          <strong>Copy this token now:</strong>
          <code>{{ newServiceToken }}</code>
        </p>
      </form>

      <div class="table-container" v-if="services.length">
        <table class="data-table">
          <caption class="visually-hidden">Service identities</caption>
          <thead><tr><th>Name</th><th>User</th><th>Scopes</th><th>Expires</th><th>Last used</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="row in services" :key="row.id">
              <td>{{ row.name }}</td>
              <td class="security-mono">{{ row.username }}</td>
              <td>{{ (row.scopes || []).join(', ') }}</td>
              <td class="security-mono">{{ formatTime(row.expires_at) }}</td>
              <td class="security-mono">{{ formatTime(row.last_used_at) }}</td>
              <td><button v-if="row.active" type="button" class="btn btn--outline btn--sm" @click="revokeService(row)">Revoke</button></td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="security-state">No service identities.</p>
    </template>

    <template v-else>
      <div class="table-container" v-if="roles.length">
        <table class="data-table">
          <caption class="visually-hidden">RBAC roles</caption>
          <thead><tr><th>Role</th><th>Label</th><th>Permissions</th></tr></thead>
          <tbody>
            <tr v-for="row in roles" :key="row.key">
              <td class="security-mono">{{ row.key }}</td>
              <td>{{ row.label }}</td>
              <td>{{ row.permissions.length }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="security-state">Role catalog unavailable.</p>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'
import { showToast } from './Toast.vue'

const tabs = [
  { key: 'events', label: 'Events' },
  { key: 'break-glass', label: 'Break-glass' },
  { key: 'services', label: 'Service identities' },
  { key: 'roles', label: 'Roles' },
]
const activeView = ref('events')
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const events = ref([])
const summary = ref(null)
const grants = ref([])
const services = ref([])
const roles = ref([])
const newServiceToken = ref('')
const filters = reactive({ category: '', severity: '', search: '' })
const grantForm = reactive({ permission: 'dna.view.private', reason: '', reference: '', minutes: 60, user_id: null })
const serviceForm = reactive({ name: '', days: 90, scopes: [] })
const eligiblePermissions = [
  'dna.view.private',
  'gps.view.private',
  'coach.transcript.view',
  'export.restricted',
  'audit.view',
]
const serviceScopes = computed(() => {
  const row = roles.value.find((item) => item.key === 'admin')
  return (row?.permissions || []).filter((item) => !item.includes('.private') && !item.endsWith('.restricted')).sort()
})

function formatTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function loadEvents() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.category) params.category = filters.category
    if (filters.severity) params.severity = filters.severity
    if (filters.search) params.search = filters.search
    const [eventResponse, summaryResponse] = await Promise.all([
      axios.get('/api/admin/security/events', { params: { ...params, limit: 100 } }),
      axios.get('/api/admin/security/events/summary', { params: { days: 30 } }),
    ])
    events.value = eventResponse.data.events || []
    summary.value = summaryResponse.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load security events.'
  } finally {
    loading.value = false
  }
}

async function loadGrants() {
  const response = await axios.get('/api/admin/security/break-glass')
  grants.value = response.data.grants || []
}

async function loadServices() {
  const response = await axios.get('/api/admin/security/service-identities')
  services.value = response.data.credentials || []
}

async function loadRoles() {
  const response = await axios.get('/api/admin/security/rbac/roles')
  roles.value = response.data.roles || []
}

async function refreshAll() {
  try {
    await Promise.all([loadEvents(), loadGrants(), loadServices(), loadRoles()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not refresh the security center.'
  }
}

async function requestBreakGlass() {
  saving.value = true
  try {
    const payload = {
      permission: grantForm.permission,
      reason: grantForm.reason,
      minutes: grantForm.minutes || 60,
      reference: grantForm.reference || null,
      user_id: grantForm.user_id || null,
    }
    await axios.post('/api/admin/security/break-glass', payload)
    grantForm.reason = ''
    grantForm.reference = ''
    grantForm.user_id = null
    await loadGrants()
    showToast('Break-glass request recorded.', 'success')
  } catch (e) {
    showToast(e.response?.data?.detail || 'Break-glass request failed.', 'error')
  } finally {
    saving.value = false
  }
}

async function approveGrant(row) {
  try {
    await axios.post(`/api/admin/security/break-glass/${row.id}/approve`)
    await loadGrants()
  } catch (e) {
    showToast(e.response?.data?.detail || 'Approval failed.', 'error')
  }
}

async function revokeGrant(row) {
  try {
    await axios.post(`/api/admin/security/break-glass/${row.id}/revoke`, { reason: 'Revoked from security center' })
    await loadGrants()
  } catch (e) {
    showToast(e.response?.data?.detail || 'Revocation failed.', 'error')
  }
}

async function reviewGrant(row) {
  const note = window.prompt('Review note (required)')
  if (!note?.trim()) return
  try {
    await axios.post(`/api/admin/security/break-glass/${row.id}/review`, { note })
    await loadGrants()
  } catch (e) {
    showToast(e.response?.data?.detail || 'Review failed.', 'error')
  }
}

async function createService() {
  saving.value = true
  newServiceToken.value = ''
  try {
    const response = await axios.post('/api/admin/security/service-identities', {
      name: serviceForm.name,
      days: serviceForm.days || 90,
      scopes: serviceForm.scopes,
    })
    newServiceToken.value = response.data.token
    serviceForm.name = ''
    serviceForm.scopes = []
    await loadServices()
    showToast('Service identity created. Copy the token now.', 'success')
  } catch (e) {
    showToast(e.response?.data?.detail || 'Service identity creation failed.', 'error')
  } finally {
    saving.value = false
  }
}

async function revokeService(row) {
  if (!window.confirm(`Revoke service identity "${row.name}"?`)) return
  try {
    await axios.delete(`/api/admin/security/service-identities/${row.id}`)
    await loadServices()
  } catch (e) {
    showToast(e.response?.data?.detail || 'Revocation failed.', 'error')
  }
}

onMounted(refreshAll)
</script>

<style scoped>
.security-center { display: grid; gap: 1rem; }
.security-center__sub { color: var(--text-muted, #64748b); margin: 0.25rem 0 0; }
.security-summary { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.75rem; }
.security-summary__card { border: 1px solid var(--border, #e2e8f0); border-radius: 0.5rem; padding: 0.75rem; display: grid; gap: 0.25rem; }
.security-summary__card span { color: var(--text-muted, #64748b); font-size: 0.8rem; }
.security-summary__card strong { font-size: 1.4rem; }
.security-filters { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: end; }
.security-filters label { display: grid; gap: 0.25rem; font-size: 0.8rem; }
.security-filters__search { flex: 1 1 16rem; }
.security-filters input, .security-filters select, .security-form input, .security-form textarea, .security-form select { padding: 0.45rem 0.55rem; border: 1px solid var(--border, #cbd5e1); border-radius: 0.35rem; }
.security-form { display: grid; gap: 0.75rem; border: 1px solid var(--border, #e2e8f0); border-radius: 0.5rem; padding: 1rem; }
.security-form h3 { margin: 0; }
.security-form label { display: grid; gap: 0.25rem; font-size: 0.85rem; }
.security-form__row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.75rem; }
.security-scopes { width: 100%; }
.security-meta { color: var(--text-muted, #64748b); font-size: 0.8rem; }
.security-mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.8rem; }
.security-badge { display: inline-block; padding: 0.1rem 0.45rem; border-radius: 999px; font-size: 0.75rem; background: #e2e8f0; color: #334155; }
.security-badge--critical, .security-badge--revoked { background: #fee2e2; color: #991b1b; }
.security-badge--warning, .security-badge--pending { background: #fef3c7; color: #92400e; }
.security-badge--notice, .security-badge--active { background: #dbeafe; color: #1e40af; }
.security-state { color: var(--text-muted, #64748b); }
.security-state--error { color: #991b1b; }
.security-actions { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.security-token { background: #f8fafc; border: 1px dashed #94a3b8; padding: 0.75rem; border-radius: 0.5rem; }
.security-token code { display: block; margin-top: 0.35rem; word-break: break-all; }
@media (max-width: 760px) {
  .security-summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .security-form__row { grid-template-columns: 1fr; }
}
</style>
