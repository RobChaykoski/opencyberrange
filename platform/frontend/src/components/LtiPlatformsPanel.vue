<template>
  <section class="lti-panel" aria-labelledby="lti-title">
    <header class="lti-panel__head">
      <div>
        <p class="lti-panel__eyebrow">LTI 1.3</p>
        <h3 id="lti-title">LTI platforms</h3>
        <p class="lti-panel__lead">
          Register the LMS deployments that may launch this platform. The learner
          link is created through the normal SSO ticket exchange; local password
          login and the break-glass administrator remain available.
        </p>
      </div>
      <button type="button" class="btn btn--primary btn--sm" @click="startCreate">
        Add platform
      </button>
    </header>

    <div class="lti-endpoints">
      <div>
        <span>Login URL</span>
        <code>{{ loginUrl }}</code>
      </div>
      <div>
        <span>Launch / redirect URI</span>
        <code>{{ launchUrl }}</code>
      </div>
    </div>

    <p v-if="loading" class="lti-state">Loading LTI platforms...</p>
    <p v-else-if="error" class="lti-state lti-state--error" role="alert">{{ error }}</p>

    <div v-else-if="!platforms.length" class="lti-empty">
      No LTI platform is registered. Add the LMS issuer, client ID, and deployment
      ID to enable launches.
    </div>

    <div v-else class="lti-list">
      <article v-for="platform in platforms" :key="platform.id" class="lti-card">
        <div class="lti-card__head">
          <div class="lti-card__identity">
            <strong>{{ platform.name }}</strong>
            <span class="lti-badge" :class="platform.enabled ? 'lti-badge--on' : 'lti-badge--off'">
              {{ platform.enabled ? 'Enabled' : 'Disabled' }}
            </span>
            <span class="lti-badge" :class="platform.has_private_key ? 'lti-badge--on' : 'lti-badge--muted'">
              {{ platform.has_private_key ? 'Client key stored' : 'No client key' }}
            </span>
          </div>
          <div class="lti-card__actions">
            <button
              type="button"
              class="btn btn--outline btn--xs"
              :disabled="testingId === platform.id"
              @click="testPlatform(platform)"
            >
              {{ testingId === platform.id ? 'Testing...' : 'Test keys' }}
            </button>
            <button type="button" class="btn btn--outline btn--xs" @click="startEdit(platform)">
              Edit
            </button>
            <button type="button" class="btn btn--danger btn--xs" @click="removePlatform(platform)">
              Delete
            </button>
          </div>
        </div>
        <dl class="lti-card__meta">
          <div><dt>Issuer</dt><dd class="lti-mono">{{ platform.issuer }}</dd></div>
          <div><dt>Client ID</dt><dd class="lti-mono">{{ platform.client_id }}</dd></div>
          <div><dt>Deployment</dt><dd class="lti-mono">{{ platform.deployment_id }}</dd></div>
          <div><dt>JWKS</dt><dd class="lti-mono">{{ platform.jwks_url }}</dd></div>
        </dl>
        <p v-if="testResults[platform.id]" class="lti-test" :class="{ 'lti-test--error': !testResults[platform.id].ok }" role="status">
          {{ testResults[platform.id].message }}
        </p>
      </article>
    </div>

    <form v-if="showForm" class="lti-form" @submit.prevent="savePlatform">
      <div class="lti-form__head">
        <h4>{{ editing ? 'Edit LTI platform' : 'New LTI platform' }}</h4>
        <button type="button" class="lti-form__close" aria-label="Close platform form" @click="closeForm">×</button>
      </div>
      <div class="lti-form__grid">
        <label class="field">
          <span>Name</span>
          <input v-model="form.name" type="text" maxlength="120" required />
        </label>
        <label class="field">
          <span>Issuer</span>
          <input v-model="form.issuer" type="url" placeholder="https://lms.example.edu" required />
        </label>
        <label class="field">
          <span>Client ID</span>
          <input v-model="form.client_id" type="text" maxlength="255" required />
        </label>
        <label class="field">
          <span>Deployment ID</span>
          <input v-model="form.deployment_id" type="text" maxlength="255" required />
        </label>
        <label class="field lti-form__wide">
          <span>OIDC login URL</span>
          <input v-model="form.auth_login_url" type="url" placeholder="https://lms.example.edu/lti/login" required />
        </label>
        <label class="field lti-form__wide">
          <span>Token URL</span>
          <input v-model="form.token_url" type="url" placeholder="https://lms.example.edu/lti/token" required />
        </label>
        <label class="field lti-form__wide">
          <span>JWKS URL</span>
          <input v-model="form.jwks_url" type="url" placeholder="https://lms.example.edu/lti/jwks" required />
        </label>
        <label class="field lti-form__wide">
          <span>Client private key {{ editing?.has_private_key ? '(stored; leave blank to keep)' : '(optional for launch)' }}</span>
          <textarea v-model="form.private_key" rows="4" placeholder="Paste the PEM private key from the LMS tool registration"></textarea>
        </label>
        <label class="lti-check">
          <input v-model="form.enabled" type="checkbox" />
          <span>Enabled</span>
        </label>
      </div>
      <p v-if="formError" class="lti-state lti-state--error" role="alert">{{ formError }}</p>
      <div class="lti-form__actions">
        <button type="button" class="btn btn--outline" :disabled="saving" @click="closeForm">Cancel</button>
        <button type="submit" class="btn btn--primary" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save platform' }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const platforms = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')
const testingId = ref(null)
const testResults = reactive({})

const loginUrl = computed(() => `${window.location.origin}/api/lti/login`)
const launchUrl = computed(() => `${window.location.origin}/api/lti/launch`)

const blank = () => ({
  name: '',
  issuer: '',
  client_id: '',
  deployment_id: '',
  auth_login_url: '',
  token_url: '',
  jwks_url: '',
  private_key: '',
  enabled: true,
})
const form = reactive(blank())

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await axios.get('/lti/admin/platforms')
    platforms.value = data.platforms || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load LTI platforms.'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.assign(form, blank())
  formError.value = ''
}

const startCreate = () => {
  editing.value = null
  resetForm()
  showForm.value = true
}

const startEdit = (platform) => {
  editing.value = platform
  Object.assign(form, {
    name: platform.name,
    issuer: platform.issuer,
    client_id: platform.client_id,
    deployment_id: platform.deployment_id,
    auth_login_url: platform.auth_login_url,
    token_url: platform.token_url,
    jwks_url: platform.jwks_url,
    private_key: '',
    enabled: platform.enabled,
  })
  formError.value = ''
  showForm.value = true
}

const closeForm = () => {
  if (saving.value) return
  showForm.value = false
  editing.value = null
  formError.value = ''
}

const payload = () => {
  const body = {
    name: form.name.trim(),
    issuer: form.issuer.trim(),
    client_id: form.client_id.trim(),
    deployment_id: form.deployment_id.trim(),
    auth_login_url: form.auth_login_url.trim(),
    token_url: form.token_url.trim(),
    jwks_url: form.jwks_url.trim(),
    enabled: form.enabled,
  }
  if (form.private_key.trim()) body.private_key = form.private_key.trim()
  return body
}

const savePlatform = async () => {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await axios.patch(`/lti/admin/platforms/${editing.value.id}`, payload())
    } else {
      await axios.post('/lti/admin/platforms', payload())
    }
    showForm.value = false
    editing.value = null
    await load()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Could not save the LTI platform.'
  } finally {
    saving.value = false
  }
}

const testPlatform = async (platform) => {
  if (testingId.value) return
  testingId.value = platform.id
  testResults[platform.id] = null
  try {
    const { data } = await axios.post(`/lti/admin/platforms/${platform.id}/test`)
    testResults[platform.id] = { ok: true, message: data.message || 'JWKS test passed.' }
  } catch (e) {
    testResults[platform.id] = {
      ok: false,
      message: e.response?.data?.detail || 'Could not fetch the JWKS.',
    }
  } finally {
    testingId.value = null
  }
}

const removePlatform = async (platform) => {
  if (!window.confirm(`Delete LTI platform "${platform.name}"? The LMS will no longer be able to launch.`)) return
  error.value = ''
  try {
    await axios.delete(`/lti/admin/platforms/${platform.id}`)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not delete the LTI platform.'
  }
}

onMounted(load)
</script>

<style scoped>
.lti-panel { display: flex; flex-direction: column; gap: 1rem; }
.lti-panel__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.lti-panel__eyebrow { margin: 0 0 0.2rem; color: var(--accent); font-size: 0.64rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }
.lti-panel h3 { margin: 0; font-size: 1.05rem; }
.lti-panel__lead { margin: 0.35rem 0 0; max-width: 70ch; color: var(--text-secondary); font-size: 0.78rem; line-height: 1.5; }
.lti-endpoints { display: grid; gap: 0.5rem; padding: 0.75rem 0.85rem; border: 1px solid var(--border-color); border-radius: 0.5rem; background: var(--bg-secondary); }
.lti-endpoints span { display: block; color: var(--text-muted); font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.06em; }
.lti-endpoints code { display: block; margin-top: 0.2rem; color: var(--text-primary); font-size: 0.72rem; word-break: break-all; }
.lti-state { color: var(--text-secondary); font-size: 0.8rem; }
.lti-state--error { color: var(--danger); }
.lti-empty { padding: 1rem; border: 1px dashed var(--border-color); border-radius: 0.5rem; color: var(--text-secondary); font-size: 0.8rem; }
.lti-list { display: flex; flex-direction: column; gap: 0.75rem; }
.lti-card { border: 1px solid var(--border-color); border-radius: 0.55rem; background: var(--bg-secondary); padding: 0.85rem; }
.lti-card__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.75rem; }
.lti-card__identity { display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; }
.lti-card__actions { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.lti-badge { padding: 0.16rem 0.4rem; border-radius: 999px; font-size: 0.58rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.lti-badge--on { background: color-mix(in srgb, var(--success) 18%, transparent); color: var(--success); }
.lti-badge--off { background: color-mix(in srgb, var(--danger) 16%, transparent); color: var(--danger); }
.lti-badge--muted { background: var(--bg-primary); color: var(--text-muted); }
.lti-card__meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: 0.5rem 0.85rem; margin: 0.75rem 0 0; }
.lti-card__meta dt { color: var(--text-muted); font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.05em; }
.lti-card__meta dd { margin: 0.1rem 0 0; color: var(--text-secondary); font-size: 0.72rem; }
.lti-mono { font-family: var(--font-mono, monospace); word-break: break-all; }
.lti-test { margin: 0.65rem 0 0; color: var(--success); font-size: 0.72rem; }
.lti-test--error { color: var(--danger); }
.lti-form { border: 1px solid var(--accent); border-radius: 0.6rem; padding: 1rem; background: var(--bg-secondary); }
.lti-form__head { display: flex; justify-content: space-between; align-items: center; }
.lti-form__head h4 { margin: 0; font-size: 0.95rem; }
.lti-form__close { border: 0; background: transparent; color: var(--text-muted); font-size: 1.2rem; cursor: pointer; }
.lti-form__grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; margin-top: 0.85rem; }
.lti-form__wide { grid-column: 1 / -1; }
.lti-form .field { display: flex; flex-direction: column; gap: 0.25rem; }
.lti-form .field span { color: var(--text-secondary); font-size: 0.68rem; font-weight: 600; }
.lti-form input, .lti-form textarea { border: 1px solid var(--border-color); border-radius: 0.35rem; background: var(--bg-primary); color: var(--text-primary); padding: 0.45rem 0.55rem; font-size: 0.78rem; }
.lti-form textarea { font-family: var(--font-mono, monospace); resize: vertical; }
.lti-check { display: flex; align-items: center; gap: 0.4rem; color: var(--text-secondary); font-size: 0.75rem; }
.lti-form__actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.9rem; }
@media (max-width: 720px) {
  .lti-panel__head, .lti-card__head { flex-direction: column; }
  .lti-form__grid { grid-template-columns: 1fr; }
}
</style>
