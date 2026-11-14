<template>
  <div class="badge-page">
    <div class="badge-shell">
      <p v-if="loading" class="badge-state">Loading credential...</p>
      <p v-else-if="error" class="badge-state badge-state--error" role="alert">{{ error }}</p>

      <template v-else-if="data">
        <header class="badge-head">
          <div>
            <p class="badge-eyebrow">Open Badge 3.0 · JWT-VC</p>
            <h1>{{ vc?.name || achievement?.name || 'Credential' }}</h1>
            <p class="badge-issuer">{{ vc?.issuer?.name || vc?.issuer?.id || 'Issuer' }}</p>
          </div>
          <span :class="['badge-status', `badge-status--${data.status}`]">{{ data.status }}</span>
        </header>

        <div v-if="data.status === 'revoked'" class="badge-revoked" role="alert">
          This credential has been revoked and should not be treated as valid.
        </div>

        <dl class="badge-facts">
          <div><dt>Issued</dt><dd>{{ formatDate(vc?.validFrom) }}</dd></div>
          <div><dt>Recipient</dt><dd>{{ recipient }}</dd></div>
          <div><dt>Achievement</dt><dd>{{ achievement?.name || '—' }}</dd></div>
          <div><dt>Credential ID</dt><dd class="badge-mono">{{ data.jti }}</dd></div>
        </dl>

        <p v-if="achievement?.description" class="badge-description">{{ achievement.description }}</p>

        <div class="badge-actions">
          <a class="btn btn--secondary" :href="jwksUrl" target="_blank" rel="noopener noreferrer">
            Issuer keys (JWKS)
          </a>
          <button class="btn btn--secondary" @click="copyCredential">
            {{ copied ? 'Credential copied' : 'Copy JWT' }}
          </button>
          <button class="btn btn--outline" @click="downloadCredential">Download JWT</button>
        </div>

        <details class="badge-raw">
          <summary>Raw credential</summary>
          <pre>{{ prettyCredential }}</pre>
        </details>

        <p class="badge-note">
          Verify by checking the JWT signature against the issuer JWKS and the
          status endpoint. A revoked credential must fail verification.
        </p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from '../api/axios'

const route = useRoute()
const data = ref(null)
const loading = ref(true)
const error = ref('')
const copied = ref(false)

const vc = computed(() => {
  try {
    const token = data.value?.credential
    if (!token) return null
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return decoded.vc
  } catch {
    return null
  }
})
const achievement = computed(() => vc.value?.credentialSubject?.achievement || null)
const recipient = computed(
  () => vc.value?.credentialSubject?.name || 'Pseudonymous subject'
)
const jwksUrl = computed(
  () => `${window.location.origin}/api/badges/issuer/jwks`
)
const prettyCredential = computed(() => {
  try {
    const token = data.value?.credential || ''
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return JSON.stringify(decoded, null, 2)
  } catch {
    return data.value?.credential || ''
  }
})

const formatDate = (value) => {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString()
}

const copyCredential = async () => {
  if (!data.value?.credential) return
  try {
    await navigator.clipboard.writeText(data.value.credential)
  } catch {
    const input = document.createElement('textarea')
    input.value = data.value.credential
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    input.remove()
  }
  copied.value = true
  setTimeout(() => { copied.value = false }, 2500)
}

const downloadCredential = () => {
  if (!data.value?.credential) return
  const blob = new Blob([data.value.credential], { type: 'application/jwt' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${data.value.jti}.jwt`
  link.click()
  URL.revokeObjectURL(link.href)
}

onMounted(async () => {
  try {
    const { data: payload } = await axios.get(`/badges/credentials/${route.params.jti}`)
    data.value = payload
  } catch (e) {
    error.value = e.response?.data?.detail || 'This credential could not be found.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.badge-page {
  min-height: 100vh;
  padding: 3rem 1rem;
  background: var(--bg-primary);
}
.badge-shell {
  max-width: 820px;
  margin: 0 auto;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}
.badge-state { color: var(--text-muted); }
.badge-state--error { color: var(--danger); }
.badge-head { display: flex; justify-content: space-between; gap: 1rem; align-items: flex-start; }
.badge-eyebrow { margin: 0 0 0.3rem; color: var(--accent); font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; }
.badge-head h1 { margin: 0; font-size: 1.5rem; }
.badge-issuer { margin: 0.3rem 0 0; color: var(--text-muted); }
.badge-status {
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  font-size: 0.75rem;
  text-transform: capitalize;
}
.badge-status--active { color: var(--success); border-color: var(--success); }
.badge-status--revoked { color: var(--danger); border-color: var(--danger); }
.badge-revoked {
  margin: 1rem 0;
  padding: 0.7rem;
  border: 1px solid var(--danger);
  border-radius: 8px;
  color: var(--danger);
}
.badge-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.8rem; margin: 1.25rem 0; }
.badge-facts dt { color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; }
.badge-facts dd { margin: 0.15rem 0 0; }
.badge-mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.8rem; }
.badge-description { color: var(--text-secondary); }
.badge-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1.25rem 0; }
.badge-raw { margin-top: 1rem; }
.badge-raw summary { cursor: pointer; color: var(--text-muted); }
.badge-raw pre { margin: 0.5rem 0 0; padding: 0.75rem; background: var(--bg-primary); border-radius: 8px; overflow: auto; font-size: 0.75rem; }
.badge-note { margin-top: 1rem; color: var(--text-muted); font-size: 0.78rem; }
</style>
