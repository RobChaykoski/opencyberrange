<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-head">
        <h1 class="auth-title">Choose a new password</h1>
        <p class="auth-subtitle" v-if="token">
          Your reset link is valid for a short time. Choose a strong password you
          have not used on this account before.
        </p>
        <p class="auth-subtitle" v-else>
          This page needs a reset link. Request a new link to continue.
        </p>
      </div>

      <div v-if="!token" class="error-message" role="alert">
        The reset link is missing or incomplete.
      </div>

      <div v-if="done" class="success-message" role="status">
        <p>{{ message }}</p>
        <router-link to="/login" class="btn btn--primary auth-submit">Go to sign in</router-link>
      </div>

      <form v-else-if="token" class="auth-form" @submit.prevent="submit" novalidate>
        <div class="form-group">
          <label for="new-password" class="form-label">New password</label>
          <div class="password-wrap">
            <input
              id="new-password"
              v-model="newPassword"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="Enter a new password"
              autocomplete="new-password"
              minlength="8"
              maxlength="128"
              required
              :disabled="loading"
            />
            <button
              type="button"
              class="password-toggle"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              :aria-pressed="showPassword ? 'true' : 'false'"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <p class="field-help">
            At least 8 characters with uppercase, lowercase, and a number. Avoid
            common words, names, and simple patterns.
          </p>
        </div>

        <div class="form-group">
          <label for="confirm-password" class="form-label">Confirm new password</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            :type="showPassword ? 'text' : 'password'"
            class="form-input"
            placeholder="Enter the same password again"
            autocomplete="new-password"
            minlength="8"
            maxlength="128"
            required
            :disabled="loading"
          />
        </div>

        <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>

        <button type="submit" class="btn btn--primary auth-submit" :disabled="loading">
          {{ loading ? 'Saving...' : 'Set new password' }}
        </button>
      </form>

      <p class="auth-links">
        <router-link to="/login">Back to sign in</router-link>
        <span aria-hidden="true">·</span>
        <router-link to="/forgot-password">Request a new link</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'
import { passwordPolicyError } from '../utils/passwordPolicy'

const route = useRoute()
const router = useRouter()

const token = computed(() => {
  const value = route.query.token
  return typeof value === 'string' ? value.trim() : ''
})

const newPassword = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const loading = ref(false)
const done = ref(false)
const message = ref('')
const errorMessage = ref('')

function validate() {
  if (newPassword.value.length < 8) {
    return 'Password must be at least 8 characters'
  }
  if (!/[A-Z]/.test(newPassword.value)) {
    return 'Password must contain at least one uppercase letter'
  }
  if (!/[a-z]/.test(newPassword.value)) {
    return 'Password must contain at least one lowercase letter'
  }
  if (!/[0-9]/.test(newPassword.value)) {
    return 'Password must contain at least one number'
  }
  if (newPassword.value !== confirmPassword.value) {
    return 'Passwords do not match'
  }
  return passwordPolicyError(newPassword.value) || ''
}

async function submit() {
  if (loading.value) return
  errorMessage.value = ''
  const validationError = validate()
  if (validationError) {
    errorMessage.value = validationError
    return
  }

  loading.value = true
  try {
    const { data } = await axios.post('/auth/reset-password', {
      token: token.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value,
    })
    message.value = data?.message || 'Password reset. Sign in with your new password.'
    done.value = true

    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    if (window.__updateAuthState) {
      window.__updateAuthState()
    }
    window.setTimeout(() => router.push('/login'), 2500)
  } catch (error) {
    const detail = error.response?.data?.detail
    if (Array.isArray(detail)) {
      errorMessage.value = detail.map((item) => item.msg || JSON.stringify(item)).join('. ')
    } else {
      errorMessage.value = detail || 'Could not reset the password. Request a new link.'
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

.password-wrap {
  position: relative;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 0.5rem;
  transform: translateY(-50%);
  border: 0;
  background: transparent;
  color: var(--accent-text);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.field-help {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.45;
}

.auth-submit {
  width: 100%;
  justify-content: center;
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
