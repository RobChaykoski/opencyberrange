<template>
  <div v-if="open" class="reauth-backdrop" role="presentation" @click.self="close">
    <section class="reauth-dialog" role="dialog" aria-modal="true" aria-labelledby="reauth-title">
      <header>
        <h2 id="reauth-title">Re-authenticate</h2>
        <button type="button" class="reauth-close" aria-label="Close" @click="close">×</button>
      </header>
      <p>
        For your security, confirm your password before
        <strong>{{ purpose || 'this action' }}</strong>.
      </p>
      <form @submit.prevent="submit">
        <label>
          <span>Password</span>
          <input
            ref="passwordInput"
            v-model="password"
            type="password"
            maxlength="128"
            autocomplete="current-password"
            required
          />
        </label>
        <label v-if="mfaEnabled">
          <span>Authenticator or recovery code</span>
          <input v-model.trim="code" inputmode="numeric" autocomplete="one-time-code" required />
        </label>
        <p v-if="error" class="reauth-error" role="alert">{{ error }}</p>
        <div class="reauth-actions">
          <button type="button" class="btn btn--outline btn--sm" @click="close">Cancel</button>
          <button type="submit" class="btn btn--primary btn--sm" :disabled="saving">
            {{ saving ? 'Checking...' : 'Re-authenticate' }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import api from '../api/axios'

const open = ref(false)
const purpose = ref('')
const password = ref('')
const code = ref('')
const error = ref('')
const saving = ref(false)
const passwordInput = ref(null)

const mfaEnabled = ref(false)
try {
  mfaEnabled.value = Boolean(JSON.parse(localStorage.getItem('user') || '{}').mfa_enabled)
} catch {
  mfaEnabled.value = false
}

function show(event) {
  purpose.value = event?.detail?.purpose || ''
  error.value = ''
  password.value = ''
  code.value = ''
  open.value = true
  nextTick(() => passwordInput.value?.focus())
}

function close() {
  open.value = false
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await api.post('/auth/reauth', {
      password: password.value,
      totp_code: code.value || null,
    })
    close()
    window.dispatchEvent(new CustomEvent('ocr:reauth-complete'))
  } catch (e) {
    error.value = e.response?.data?.detail || 'Re-authentication failed.'
  } finally {
    saving.value = false
  }
}

function onRequired(event) {
  show(event)
}

onMounted(() => window.addEventListener('ocr:reauth-required', onRequired))
onUnmounted(() => window.removeEventListener('ocr:reauth-required', onRequired))
</script>

<style scoped>
.reauth-backdrop {
  position: fixed;
  inset: 0;
  z-index: 4000;
  background: rgba(15, 23, 42, 0.55);
  display: grid;
  place-items: center;
  padding: 1rem;
}
.reauth-dialog {
  width: min(28rem, 100%);
  background: var(--surface, #fff);
  color: var(--text, #0f172a);
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.3);
}
.reauth-dialog header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.reauth-dialog h2 {
  margin: 0;
  font-size: 1.15rem;
}
.reauth-close {
  border: 0;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}
.reauth-dialog form {
  display: grid;
  gap: 0.75rem;
  margin-top: 0.75rem;
}
.reauth-dialog label {
  display: grid;
  gap: 0.3rem;
  font-size: 0.85rem;
}
.reauth-dialog input {
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--border, #cbd5e1);
  border-radius: 0.35rem;
}
.reauth-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.reauth-error {
  color: #991b1b;
  margin: 0;
}
</style>
