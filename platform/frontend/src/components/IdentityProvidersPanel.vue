<template>
  <section class="idp-panel" aria-labelledby="idp-title">
    <header class="idp-panel__head">
      <div>
        <p class="idp-panel__eyebrow">V3 · Identity</p>
        <h3 id="idp-title">Identity providers</h3>
        <p class="idp-panel__lead">
          Configure LDAP, OpenID Connect, or SAML providers. Secrets are encrypted
          and never returned by the API. Login flows are enabled by the v3
          identity adapter, not by this settings panel alone.
        </p>
      </div>
      <button type="button" class="btn btn--primary btn--sm" @click="startCreate">
        Add provider
      </button>
    </header>

    <p v-if="loading" class="idp-state">Loading identity providers...</p>
    <p v-else-if="error" class="idp-state idp-state--error" role="alert">{{ error }}</p>

    <div v-else-if="!providers.length" class="idp-empty">
      No identity providers configured. Local username/password login remains the
      default until a v3 provider is enabled.
    </div>

    <div v-else class="idp-list">
      <article v-for="provider in providers" :key="provider.id" class="idp-card">
        <div class="idp-card__head">
          <div class="idp-card__identity">
            <span class="idp-kind" :class="`idp-kind--${provider.kind}`">{{ kindLabel(provider.kind) }}</span>
            <strong>{{ provider.name }}</strong>
            <span v-if="provider.is_default" class="idp-badge idp-badge--default">Default</span>
            <span class="idp-badge" :class="provider.enabled ? 'idp-badge--on' : 'idp-badge--off'">
              {{ provider.enabled ? 'Enabled' : 'Disabled' }}
            </span>
          </div>
          <div class="idp-card__actions">
            <button type="button" class="btn btn--outline btn--xs" @click="startEdit(provider)">Edit</button>
            <button
              v-if="!provider.is_default && provider.enabled"
              type="button"
              class="btn btn--outline btn--xs"
              @click="makeDefault(provider)"
            >
              Make default
            </button>
            <button type="button" class="btn btn--danger btn--xs" @click="removeProvider(provider)">Delete</button>
          </div>
        </div>
        <dl class="idp-card__meta">
          <div><dt>Endpoint</dt><dd>{{ summary(provider) }}</dd></div>
          <div><dt>Secret fields</dt><dd>{{ provider.secret_keys?.length ? provider.secret_keys.join(', ') : 'None stored' }}</dd></div>
        </dl>
      </article>
    </div>

    <form v-if="showForm" class="idp-form" @submit.prevent="saveProvider">
      <div class="idp-form__head">
        <h4>{{ editing ? 'Edit identity provider' : 'New identity provider' }}</h4>
        <button type="button" class="idp-form__close" aria-label="Close provider form" @click="closeForm">×</button>
      </div>

      <div class="idp-form__row">
        <label class="field">
          <span>Name</span>
          <input v-model="form.name" type="text" maxlength="120" required />
        </label>
        <label class="field">
          <span>Type</span>
          <select v-model="form.kind" :disabled="Boolean(editing)" @change="onKindChange">
            <option value="ldap">LDAP / Active Directory</option>
            <option value="oidc">OpenID Connect</option>
            <option value="saml">SAML 2.0</option>
          </select>
        </label>
        <label class="idp-check">
          <input v-model="form.enabled" type="checkbox" />
          <span>Enabled</span>
        </label>
        <label class="idp-check">
          <input v-model="form.is_default" type="checkbox" :disabled="!form.enabled" />
          <span>Default provider</span>
        </label>
      </div>

      <template v-if="form.kind === 'ldap'">
        <div class="idp-form__row">
          <label class="field idp-form__wide">
            <span>Server URL</span>
            <input v-model="form.config.server_url" type="text" placeholder="ldaps://ldap.example.edu" required />
          </label>
          <label class="field">
            <span>Start TLS</span>
            <select v-model="form.config.start_tls">
              <option :value="false">No</option>
              <option :value="true">Yes</option>
            </select>
          </label>
          <label class="field">
            <span>Verify TLS</span>
            <select v-model="form.config.tls_verify">
              <option :value="true">Yes</option>
              <option :value="false">No</option>
            </select>
          </label>
        </div>
        <div class="idp-form__row">
          <label class="field idp-form__wide">
            <span>Base DN</span>
            <input v-model="form.config.base_dn" type="text" placeholder="ou=people,dc=example,dc=edu" required />
          </label>
          <label class="field idp-form__wide">
            <span>Bind DN (optional)</span>
            <input v-model="form.config.bind_dn" type="text" placeholder="cn=svc-ocr,ou=services,dc=example,dc=edu" />
          </label>
        </div>
        <div class="idp-form__row">
          <label class="field idp-form__wide">
            <span>User search filter</span>
            <input v-model="form.config.user_search_filter" type="text" placeholder="(uid={username})" />
          </label>
          <label class="field idp-form__wide">
            <span>{{ editing && hasSecret('bind_password') ? 'New bind password (leave blank to keep)' : 'Bind password' }}</span>
            <input v-model="form.secrets.bind_password" type="password" autocomplete="new-password" />
          </label>
        </div>
      </template>

      <template v-else-if="form.kind === 'oidc'">
        <div class="idp-form__row">
          <label class="field idp-form__wide">
            <span>Issuer URL</span>
            <input v-model="form.config.issuer" type="text" placeholder="https://idp.example.edu" required />
          </label>
          <label class="field">
            <span>Client ID</span>
            <input v-model="form.config.client_id" type="text" required />
          </label>
        </div>
        <div class="idp-form__row">
          <label class="field idp-form__wide">
            <span>Scopes</span>
            <input v-model="form.config.scopes" type="text" placeholder="openid email profile" />
          </label>
          <label class="field idp-form__wide">
            <span>{{ editing && hasSecret('client_secret') ? 'New client secret (leave blank to keep)' : 'Client secret' }}</span>
            <input v-model="form.secrets.client_secret" type="password" autocomplete="new-password" />
          </label>
        </div>
      </template>

      <template v-else>
        <div class="idp-form__row">
          <label class="field idp-form__wide">
            <span>IdP entity ID</span>
            <input v-model="form.config.idp_entity_id" type="text" required />
          </label>
          <label class="field idp-form__wide">
            <span>SP entity ID</span>
            <input v-model="form.config.sp_entity_id" type="text" required />
          </label>
        </div>
        <div class="idp-form__row">
          <label class="field idp-form__wide">
            <span>SSO URL</span>
            <input v-model="form.config.sso_url" type="text" required />
          </label>
          <label class="field idp-form__wide">
            <span>ACS URL</span>
            <input v-model="form.config.acs_url" type="text" required />
          </label>
        </div>
        <div class="idp-form__row">
          <label class="field idp-form__wide">
            <span>SLO URL (optional)</span>
            <input v-model="form.config.slo_url" type="text" />
          </label>
          <label class="field idp-form__wide">
            <span>{{ editing && hasSecret('private_key') ? 'New private key (leave blank to keep)' : 'SP private key' }}</span>
            <textarea v-model="form.secrets.private_key" rows="3" autocomplete="off" />
          </label>
        </div>
      </template>

      <p v-if="formError" class="idp-state idp-state--error" role="alert">{{ formError }}</p>
      <div class="idp-form__footer">
        <button type="button" class="btn btn--secondary btn--sm" @click="closeForm">Cancel</button>
        <button type="submit" class="btn btn--primary btn--sm" :disabled="saving">
          {{ saving ? 'Saving...' : (editing ? 'Save provider' : 'Create provider') }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const providers = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')

const blankConfig = () => ({
  server_url: '',
  base_dn: '',
  bind_dn: '',
  user_search_filter: '(uid={username})',
  start_tls: false,
  tls_verify: true,
  issuer: '',
  client_id: '',
  scopes: 'openid email profile',
  idp_entity_id: '',
  sp_entity_id: '',
  sso_url: '',
  slo_url: '',
  acs_url: '',
})

const blankSecrets = () => ({ bind_password: '', client_secret: '', private_key: '' })

const form = reactive({
  name: '',
  kind: 'ldap',
  enabled: false,
  is_default: false,
  config: blankConfig(),
  secrets: blankSecrets(),
})

const kindLabel = (kind) => ({ ldap: 'LDAP', oidc: 'OIDC', saml: 'SAML' }[kind] || kind)
const hasSecret = (key) => Boolean(editing.value?.secret_keys?.includes(key))

const summary = (provider) => {
  const config = provider.config || {}
  if (provider.kind === 'ldap') return config.server_url || 'Not configured'
  if (provider.kind === 'oidc') return config.issuer || 'Not configured'
  return config.sso_url || 'Not configured'
}

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await axios.get('/identity/providers')
    providers.value = data.providers || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load identity providers.'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.name = ''
  form.kind = 'ldap'
  form.enabled = false
  form.is_default = false
  form.config = blankConfig()
  form.secrets = blankSecrets()
  formError.value = ''
}

const startCreate = () => {
  editing.value = null
  resetForm()
  showForm.value = true
}

const startEdit = (provider) => {
  editing.value = provider
  form.name = provider.name
  form.kind = provider.kind
  form.enabled = provider.enabled
  form.is_default = provider.is_default
  form.config = { ...blankConfig(), ...(provider.config || {}) }
  form.secrets = blankSecrets()
  formError.value = ''
  showForm.value = true
}

const closeForm = () => {
  if (saving.value) return
  showForm.value = false
  editing.value = null
  formError.value = ''
}

const onKindChange = () => {
  form.config = blankConfig()
  form.secrets = blankSecrets()
}

const payload = () => {
  const secrets = Object.fromEntries(
    Object.entries(form.secrets).filter(([, value]) => String(value || '').trim() !== '')
  )
  return {
    name: form.name.trim(),
    kind: form.kind,
    enabled: form.enabled,
    is_default: form.is_default,
    config: { ...form.config },
    ...(Object.keys(secrets).length ? { secrets } : {}),
  }
}

const saveProvider = async () => {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await axios.patch(`/identity/providers/${editing.value.id}`, payload())
    } else {
      await axios.post('/identity/providers', payload())
    }
    showForm.value = false
    editing.value = null
    await load()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Could not save the identity provider.'
  } finally {
    saving.value = false
  }
}

const makeDefault = async (provider) => {
  error.value = ''
  try {
    await axios.post(`/identity/providers/${provider.id}/default`)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not make that provider the default.'
  }
}

const removeProvider = async (provider) => {
  if (!window.confirm(`Delete identity provider “${provider.name}”? This cannot be undone.`)) return
  error.value = ''
  try {
    await axios.delete(`/identity/providers/${provider.id}`)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not delete the identity provider.'
  }
}

onMounted(load)
</script>

<style scoped>
.idp-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.idp-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}
.idp-panel__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent);
  font-size: 0.64rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.idp-panel__head h3 {
  margin: 0 0 0.3rem;
  color: var(--text-primary);
  font-size: 1.05rem;
}
.idp-panel__lead {
  max-width: 70ch;
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.55;
}
.idp-state,
.idp-empty {
  margin: 0;
  padding: 0.9rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.8rem;
}
.idp-state--error {
  border-color: color-mix(in srgb, var(--danger) 45%, var(--border-color));
  color: var(--danger);
}
.idp-list {
  display: grid;
  gap: 0.7rem;
}
.idp-card {
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
}
.idp-card__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}
.idp-card__identity {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.45rem;
  min-width: 0;
}
.idp-card__identity strong {
  color: var(--text-primary);
  font-size: 0.88rem;
  overflow-wrap: anywhere;
}
.idp-kind,
.idp-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.12rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.idp-kind--ldap { color: #60a5fa; border-color: rgba(96, 165, 250, 0.4); }
.idp-kind--oidc { color: #34d399; border-color: rgba(52, 211, 153, 0.4); }
.idp-kind--saml { color: #fbbf24; border-color: rgba(251, 191, 36, 0.4); }
.idp-badge--on { color: var(--success); border-color: color-mix(in srgb, var(--success) 40%, var(--border-color)); }
.idp-badge--off { color: var(--text-muted); }
.idp-badge--default { color: var(--accent); border-color: color-mix(in srgb, var(--accent) 40%, var(--border-color)); }
.idp-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  flex-shrink: 0;
}
.idp-card__meta {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: 0.5rem 1rem;
  margin: 0.7rem 0 0;
  font-size: 0.7rem;
}
.idp-card__meta div { min-width: 0; }
.idp-card__meta dt {
  color: var(--text-muted);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.58rem;
}
.idp-card__meta dd {
  margin: 0.1rem 0 0;
  color: var(--text-secondary);
  overflow-wrap: anywhere;
}
.idp-form {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
}
.idp-form__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}
.idp-form__head h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.92rem;
}
.idp-form__close {
  border: 0;
  background: transparent;
  color: var(--text-secondary);
  font-size: 1.2rem;
  cursor: pointer;
}
.idp-form__row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  margin-bottom: 0.7rem;
}
.idp-form__row .field { flex: 1 1 12rem; min-width: 0; }
.idp-form__row .idp-form__wide { flex: 2 1 20rem; }
.idp-check {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  align-self: flex-end;
  padding-bottom: 0.45rem;
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
}
.idp-form__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  margin-top: 0.8rem;
}
@media (max-width: 700px) {
  .idp-panel__head,
  .idp-card__head {
    flex-direction: column;
  }
  .idp-card__actions { width: 100%; }
  .idp-card__meta { grid-template-columns: 1fr; }
}
</style>
