<template>
  <section class="badge-admin">
    <header class="badge-admin__head">
      <div>
        <h3>Open Badges issuer</h3>
        <p class="section-desc">
          Hosted Open Badges 3.0 credentials for level certificates. The Ed25519
          signing key is generated on first use and stored encrypted. Rotating the
          key keeps previous public keys in the JWKS so older credentials still verify.
        </p>
      </div>
      <button class="btn btn--secondary btn--sm" :disabled="loading" @click="load">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </header>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="message" class="success-message">{{ message }}</p>

    <div v-if="settings" class="badge-admin__facts">
      <div><span>Current key</span><code>{{ settings.current_kid }}</code></div>
      <div><span>Signing keys</span><strong>{{ settings.signing_keys }}</strong></div>
      <div><span>Credentials</span><strong>{{ settings.credential_count }}</strong></div>
    </div>

    <form class="badge-admin__form" @submit.prevent="saveSettings">
      <label>
        <span>Issuer name</span>
        <input v-model="form.issuer_name" class="form-input form-input--sm" required>
      </label>
      <label>
        <span>Issuer URL</span>
        <input v-model="form.issuer_url" class="form-input form-input--sm" placeholder="https://range.example.edu">
      </label>
      <button class="btn btn--primary btn--sm" :disabled="saving">Save</button>
      <button type="button" class="btn btn--danger btn--sm" :disabled="rotating" @click="rotateKey">
        {{ rotating ? 'Rotating...' : 'Rotate signing key' }}
      </button>
    </form>

    <h4 class="badge-admin__title">Recent credentials</h4>
    <div v-if="!credentials.length" class="empty-state">No credentials issued yet.</div>
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Learner</th>
            <th>Achievement</th>
            <th>Issued</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in credentials" :key="row.jti">
            <td><PrivacyText :value="row.username" fallback="Deleted learner" /></td>
            <td>{{ row.achievement_name }}</td>
            <td class="cell-muted">{{ row.issued_at ? row.issued_at.slice(0, 10) : '—' }}</td>
            <td><span :class="['badge-admin__status', `badge-admin__status--${row.status}`]">{{ row.status }}</span></td>
            <td class="cell-actions">
              <a class="btn btn--outline btn--xs" :href="`/badges/${row.jti}`" target="_blank" rel="noopener">View</a>
              <button
                v-if="row.status === 'active'"
                class="btn btn--danger btn--xs"
                :disabled="revokingId === row.id"
                @click="revoke(row)"
              >
                {{ revokingId === row.id ? 'Revoking...' : 'Revoke' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'
import PrivacyText from './PrivacyText.vue'

const settings = ref(null)
const credentials = ref([])
const loading = ref(false)
const saving = ref(false)
const rotating = ref(false)
const revokingId = ref(null)
const error = ref('')
const message = ref('')
const form = reactive({ issuer_name: '', issuer_url: '' })

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const [{ data: config }, { data: list }] = await Promise.all([
      axios.get('/admin/badges/settings'),
      axios.get('/admin/badges?limit=50'),
    ])
    settings.value = config
    form.issuer_name = config.issuer_name || ''
    form.issuer_url = config.issuer_url || ''
    credentials.value = list.credentials || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load badge settings.'
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await axios.put('/admin/badges/settings', {
      issuer_name: form.issuer_name,
      issuer_url: form.issuer_url,
    })
    message.value = 'Issuer settings saved.'
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not save issuer settings.'
  } finally {
    saving.value = false
  }
}

const rotateKey = async () => {
  if (!window.confirm('Rotate the signing key? Existing credentials stay valid through the published old key.')) return
  rotating.value = true
  error.value = ''
  message.value = ''
  try {
    await axios.post('/admin/badges/rotate-key')
    message.value = 'Signing key rotated.'
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not rotate the key.'
  } finally {
    rotating.value = false
  }
}

const revoke = async (row) => {
  const reason = window.prompt('Reason for revoking this credential (recorded in the audit log):', '')
  if (reason === null) return
  if (reason.trim().length < 3) {
    error.value = 'A revocation reason of at least three characters is required.'
    return
  }
  revokingId.value = row.id
  error.value = ''
  message.value = ''
  try {
    await axios.post(`/admin/badges/${row.id}/revoke`, { reason: reason.trim() })
    message.value = 'Credential revoked.'
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not revoke the credential.'
  } finally {
    revokingId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.badge-admin { display: flex; flex-direction: column; gap: 1rem; }
.badge-admin__head { display: flex; justify-content: space-between; gap: 1rem; align-items: flex-start; }
.badge-admin__head h3 { margin: 0 0 0.3rem; }
.badge-admin__facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; }
.badge-admin__facts div { border: 1px solid var(--border-color); border-radius: 8px; padding: 0.6rem; background: var(--bg-secondary); display: flex; flex-direction: column; gap: 0.2rem; }
.badge-admin__facts span { color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; }
.badge-admin__facts code { font-size: 0.75rem; overflow-wrap: anywhere; }
.badge-admin__form { display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: flex-end; }
.badge-admin__form label { display: flex; flex-direction: column; gap: 0.2rem; color: var(--text-muted); font-size: 0.72rem; }
.badge-admin__form .form-input { width: 260px; }
.badge-admin__title { margin: 0.5rem 0 0; font-size: 0.95rem; }
.badge-admin__status { text-transform: capitalize; font-size: 0.75rem; }
.badge-admin__status--active { color: var(--success); }
.badge-admin__status--revoked { color: var(--danger); }
</style>
