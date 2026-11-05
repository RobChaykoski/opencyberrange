<template>
  <div class="sso-callback-page">
    <div class="sso-callback-card">
      <div v-if="loading" class="sso-callback-state" role="status" aria-live="polite">
        <span class="sso-spinner" aria-hidden="true"></span>
        <h1>Completing sign-in</h1>
        <p>Connecting your institution account to OpenCyberRange.</p>
      </div>

      <div v-else class="sso-callback-state sso-callback-state--error" role="alert">
        <span class="sso-callback-mark" aria-hidden="true">!</span>
        <h1>Sign-in could not complete</h1>
        <p>{{ errorMessage }}</p>
        <router-link to="/login" class="btn btn--primary">Back to sign in</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { setWikiAuthCookie } from '../utils/wikiAuth'

const route = useRoute()
const router = useRouter()
const updateAuthState = inject('updateAuthState', null)
const loading = ref(true)
const errorMessage = ref('')

const friendlyError = (code) => {
  if (code === 'pending_approval') {
    return 'Your account is awaiting administrator approval. Ask your instructor or administrator to approve it, then try again.'
  }
  if (code === 'access_denied') {
    return 'The identity provider did not grant access. Try again or use your local account.'
  }
  if (code === 'invalid_request') {
    return 'The sign-in response was incomplete. Start the sign-in again.'
  }
  return 'Single sign-on could not complete. Try again, or use your local account.'
}

const finishSignIn = async (data) => {
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('user', JSON.stringify(data.user || {}))
  setWikiAuthCookie()
  if (updateAuthState) {
    updateAuthState()
  } else if (window.__updateAuthState) {
    window.__updateAuthState()
  }
  const target = typeof data.return_to === 'string' && data.return_to.startsWith('/')
    && !data.return_to.startsWith('//')
    ? data.return_to
    : '/dashboard'
  await router.replace(target)
}

onMounted(async () => {
  const code = route.query.error
  if (code) {
    errorMessage.value = friendlyError(String(code))
    loading.value = false
    return
  }
  const ticket = route.query.ticket
  if (!ticket) {
    errorMessage.value = friendlyError('invalid_request')
    loading.value = false
    return
  }
  try {
    const { data } = await axios.post('/api/auth/sso/exchange', { ticket: String(ticket) })
    await finishSignIn(data)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail
      || 'Single sign-on could not complete. Try again, or use your local account.'
    loading.value = false
  }
})
</script>

<style scoped>
.sso-callback-page {
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 1.5rem;
  background: var(--bg-primary);
}

.sso-callback-card {
  width: min(100%, 28rem);
  padding: 2rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  text-align: center;
}

.sso-callback-state h1 {
  margin: 0.9rem 0 0.4rem;
  color: var(--text-primary);
  font-size: 1.35rem;
}

.sso-callback-state p {
  margin: 0 0 1.25rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.55;
}

.sso-callback-mark {
  display: inline-grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 999px;
  background: var(--danger-bg);
  color: var(--danger);
  font-size: 1.4rem;
  font-weight: 700;
}

.sso-spinner {
  display: inline-block;
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 999px;
  animation: sso-spin 0.8s linear infinite;
}

.btn--primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 0.9rem;
  border-radius: 6px;
  background: var(--accent);
  color: #fff;
  font-size: 0.8125rem;
  font-weight: 600;
  text-decoration: none;
}

.btn--primary:hover {
  filter: brightness(1.08);
}

@keyframes sso-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .sso-spinner { animation: none; }
}
</style>
