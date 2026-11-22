<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-head">
        <h1 class="auth-title">Reset your password</h1>
        <p class="auth-subtitle">
          Enter the email address on your account. If it matches an eligible
          local account, we will send a one-time link that expires in 30 minutes.
        </p>
      </div>

      <div v-if="sent" class="success-message" role="status">
        <p>{{ message }}</p>
        <p class="auth-note">Check your spam folder if it does not arrive within a few minutes.</p>
      </div>

      <form v-else class="auth-form" @submit.prevent="submit" novalidate>
        <div class="form-group">
          <label for="reset-email" class="form-label">Email address</label>
          <input
            id="reset-email"
            v-model="email"
            type="email"
            class="form-input"
            placeholder="you@example.edu"
            autocomplete="email"
            inputmode="email"
            autocapitalize="none"
            autocorrect="off"
            spellcheck="false"
            maxlength="254"
            required
            :disabled="loading"
          />
        </div>

        <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>

        <button type="submit" class="btn btn--primary auth-submit" :disabled="loading || !email.trim()">
          {{ loading ? 'Sending...' : 'Email me a reset link' }}
        </button>
      </form>

      <p class="auth-links">
        <router-link to="/login">Back to sign in</router-link>
        <span aria-hidden="true">·</span>
        <router-link to="/forgot-password" v-if="sent">Send another link</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from '../api/axios'

const email = ref('')
const loading = ref(false)
const sent = ref(false)
const message = ref('')
const errorMessage = ref('')

async function submit() {
  if (loading.value) return
  errorMessage.value = ''
  loading.value = true
  try {
    const { data } = await axios.post('/auth/forgot-password', {
      email: email.value.trim(),
    })
    message.value = data?.message || 'If that email is registered, we have sent a reset link to it.'
    sent.value = true
  } catch (error) {
    const detail = error.response?.data?.detail
    if (Array.isArray(detail)) {
      errorMessage.value = detail.map((item) => item.msg || JSON.stringify(item)).join('. ')
    } else {
      errorMessage.value = detail || 'Could not send the reset link. Try again in a moment.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 1.5rem;
  background: var(--bg-primary);
}

.auth-card {
  width: min(440px, 100%);
  padding: 2rem 1.75rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
  box-shadow: 0 20px 45px rgba(2, 6, 23, 0.18);
}

.auth-head {
  margin-bottom: 1.4rem;
}

.auth-title {
  margin: 0 0 0.4rem;
  color: var(--text-primary);
  font-size: 1.35rem;
  line-height: 1.25;
}

.auth-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.5;
}

.auth-form {
  display: grid;
  gap: 1rem;
}

.auth-submit {
  width: 100%;
  justify-content: center;
}

.auth-note {
  margin: 0.6rem 0 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.auth-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.82rem;
}

.auth-links a {
  color: var(--accent-text);
  font-weight: 600;
  text-decoration: none;
}

.auth-links a:hover {
  text-decoration: underline;
}
</style>
