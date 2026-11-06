<template>
  <div class="login-page">
    <nav class="login-powered" aria-label="Powered by OpenCyberRange">
      <a
        class="login-powered__brand"
        href="https://github.com/RobChaykoski/opencyberrange"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Powered by OpenCyberRange — open the OpenCyberRange project"
        title="Powered by OpenCyberRange"
      >
        <span>Powered by</span>
        <img src="/ocr-logo-dark.png" alt="OpenCyberRange" />
        <span>OpenCyberRange</span>
      </a>
      <span class="login-powered__divider" aria-hidden="true"></span>
      <a
        class="login-powered__social"
        href="https://www.linkedin.com/company/swocts"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="SWOCTS on LinkedIn"
        title="SWOCTS on LinkedIn"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.55V9h3.57v11.45Z"/>
        </svg>
      </a>
    </nav>

    <div class="login-split">
      <!-- Left: form panel -->
      <div class="login-form-panel">
        <div class="form-panel-inner">
          <div class="brand">
            <img src="/swocts-cyber-range-mark.png" alt="" class="brand-icon" />
            <div class="brand-text">
              <h1 class="brand-title">SWOCTS Cyber Range</h1>
              <p class="brand-subtitle">Welcome back</p>
            </div>
          </div>

          <p class="form-subtext">Sign in to continue your training</p>

          <div v-if="$route.query.deleted" class="success-message" role="status">
            Your account and personal data have been deleted.
          </div>

          <div v-if="errorMessage" class="error-message" role="alert">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <label for="username" class="form-label">Username</label>
              <input
                id="username"
                v-model="username"
                type="text"
                class="form-input"
                :class="{ 'form-input--error': errorMessage }"
                placeholder="Enter your username"
                required
                autocomplete="username"
              />
              <button
                type="button"
                class="forgot-username-link"
                @click="toggleUsernameHelp"
              >
                Forgot username?
              </button>
            </div>

            <div v-if="showUsernameHelp" class="forgot-username-panel">
              <p class="forgot-username-help">
                Enter the email address on your account. We will send your
                username to that address only.
              </p>
              <div class="forgot-username-row">
                <input
                  id="reminder-email"
                  v-model="reminderEmail"
                  type="email"
                  class="form-input"
                  placeholder="you@example.edu"
                  autocomplete="email"
                  @keyup.enter="requestUsername"
                />
                <button
                  type="button"
                  class="forgot-username-submit"
                  :disabled="reminderLoading || !reminderEmail.trim()"
                  @click="requestUsername"
                >
                  {{ reminderLoading ? 'Sending...' : 'Email my username' }}
                </button>
              </div>
              <p
                v-if="reminderMessage"
                class="forgot-username-message"
                :class="{ 'forgot-username-message--error': reminderError }"
                role="status"
              >
                {{ reminderMessage }}
              </p>
            </div>

            <div class="form-group">
              <label for="password" class="form-label">Password</label>
              <div class="password-wrap">
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input"
                  :class="{ 'form-input--error': errorMessage }"
                  placeholder="Enter your password"
                  required
                  autocomplete="current-password"
                />
                <button
                  type="button"
                  class="password-toggle"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  @click="showPassword = !showPassword"
                >
                  {{ showPassword ? 'Hide' : 'Show' }}
                </button>
              </div>
            </div>

            <div v-if="mfaRequired" class="form-group">
              <label for="mfa-code" class="form-label">Authenticator or recovery code</label>
              <input
                id="mfa-code"
                v-model="mfaCode"
                type="text"
                class="form-input"
                :class="{ 'form-input--error': errorMessage }"
                placeholder="6-digit or recovery code"
                autocomplete="one-time-code"
                required
              />
              <p class="mfa-help">
                Enter the code from your authenticator app, or one of your recovery codes.
              </p>
            </div>

            <button type="submit" class="login-button" :disabled="loading">
              <span v-if="loading">Signing In...</span>
              <span v-else-if="mfaRequired">Verify &amp; Sign In</span>
              <span v-else>Sign In</span>
            </button>
          </form>

          <p class="login-security">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <rect x="4" y="10" width="16" height="10" rx="2"/>
              <path d="M8 10V7a4 4 0 0 1 8 0v3"/>
            </svg>
            Secure sign-in · MFA supported
          </p>

          <div class="register-section">
            <p class="register-text">
              Don't have an account?
              <router-link to="/register" class="register-link">Register here</router-link>
            </p>
          </div>
        </div>
      </div>

      <!-- Right: platform preview -->
      <div class="login-hero-panel">
        <div class="hero-content">
          <div class="hero-head">
            <span class="hero-kicker">Platform preview</span>
            <h2 class="hero-title">Learn by doing.<br />Prove what you can do.</h2>
            <p class="hero-subtitle">
              Hands-on labs, a browser-based RangeBox, achievements, and
              verifiable certificates.
            </p>
          </div>

          <div class="preview-grid">
            <article class="preview-card preview-card--labs">
              <div class="preview-card__head">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <circle cx="12" cy="12" r="9"/>
                  <circle cx="12" cy="12" r="4"/>
                  <circle cx="12" cy="12" r="1"/>
                </svg>
                <span>Labs</span>
              </div>
              <ul class="preview-lab-list">
                <li>
                  <span class="preview-dot preview-dot--done"></span>
                  <span><strong>Windows port scan</strong><small>Recon · 120 min</small></span>
                  <span class="preview-status">Complete</span>
                </li>
                <li>
                  <span class="preview-dot preview-dot--next"></span>
                  <span><strong>SMB share enumeration</strong><small>Windows · 90 min</small></span>
                  <span class="preview-status">Next</span>
                </li>
                <li>
                  <span class="preview-dot preview-dot--locked"></span>
                  <span><strong>Memory analysis</strong><small>Forensics · 60 min</small></span>
                  <span class="preview-status">Locked</span>
                </li>
              </ul>
            </article>

            <article class="preview-card preview-card--rangebox">
              <div class="preview-card__head">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <rect x="3" y="4" width="18" height="16" rx="2"/>
                  <path d="m7 9 3 3-3 3"/>
                  <path d="M13 15h4"/>
                </svg>
                <span>RangeBox</span>
              </div>
              <div class="mini-terminal" aria-label="Sample RangeBox terminal">
                <div class="mini-terminal__bar">
                  <span></span><span></span><span></span>
                  <small>rangebox://kali</small>
                </div>
                <p><b>$</b> nmap -sV 10.100.3.0/24</p>
                <p class="mini-terminal__muted">445/tcp open microsoft-ds</p>
                <p class="mini-terminal__ok">Session ready · 01:42:18</p>
              </div>
            </article>

            <article class="preview-card preview-card--achievements">
              <div class="preview-card__head">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <circle cx="12" cy="8" r="5"/>
                  <path d="m8.5 12-1 9 4.5-2.5L16.5 21l-1-9"/>
                </svg>
                <span>Achievements</span>
              </div>
              <div class="preview-badges">
                <span class="preview-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/></svg>First Blood</span>
                <span class="preview-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12c.5.5 1 1.2 1 2h6c0-.8.5-1.5 1-2A7 7 0 0 0 12 2Z"/></svg>Self-Reliant</span>
                <span class="preview-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 2c1 4-1 5-1 8a3 3 0 0 0 6 0c0-1-.5-2-1-3 3 2 5 5 5 8a7 7 0 0 1-14 0c0-4 2-7 5-13Z"/></svg>On a Roll</span>
              </div>
            </article>

            <article class="preview-card preview-card--certificate">
              <div class="preview-certificate">
                <div class="preview-certificate__brandline">
                  <img src="/swocts-cyber-range-mark.png" alt="" class="preview-certificate__logo" />
                  <strong>SWOCTS Cyber Range</strong>
                  <span class="preview-certificate__powered">
                    <span>Powered by</span>
                    <a
                      class="preview-certificate__site"
                      href="https://github.com/RobChaykoski/opencyberrange"
                      target="_blank"
                      rel="noopener noreferrer"
                      title="OpenCyberRange project"
                    >OpenCyberRange</a>
                    <a
                      class="preview-certificate__social"
                      href="https://www.linkedin.com/company/swocts"
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label="SWOCTS on LinkedIn"
                      title="SWOCTS on LinkedIn"
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                        <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.55V9h3.57v11.45Z"/>
                      </svg>
                    </a>
                  </span>
                </div>
                <div class="preview-certificate__main">
                  <span class="preview-certificate__seal">SWOCTS</span>
                  <div class="preview-certificate__body">
                    <small class="preview-certificate__eyebrow">Certificate of Completion</small>
                    <strong class="preview-certificate__name">Avery Chen</strong>
                    <span>Network Foundations · Level 1</span>
                    <small class="preview-certificate__meta">Issued 04 Nov 2026 · SWOCTS-2026-0142</small>
                    <span class="preview-certificate__verified">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
                        <path d="m5 12 4 4L19 6"/>
                      </svg>
                      Verified
                    </span>
                  </div>
                </div>
              </div>
            </article>
          </div>

          <p class="hero-note">
            Sample preview. Your real progress stays private and is never publicly ranked.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, inject } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios' // Use plain axios for login (no token needed)
import { setWikiAuthCookie } from '../utils/wikiAuth'

const router = useRouter()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const mfaRequired = ref(false)
const mfaCode = ref('')
const errorMessage = ref('')
const loading = ref(false)

// "Forgot username" flow: email the username to the address on the account.
const showUsernameHelp = ref(false)
const reminderEmail = ref('')
const reminderMessage = ref('')
const reminderError = ref(false)
const reminderLoading = ref(false)

const toggleUsernameHelp = () => {
  showUsernameHelp.value = !showUsernameHelp.value
  reminderMessage.value = ''
  reminderError.value = false
}

const requestUsername = async () => {
  if (reminderLoading.value) return
  reminderMessage.value = ''
  reminderError.value = false
  reminderLoading.value = true
  try {
    const { data } = await axios.post('/api/auth/forgot-username', {
      email: reminderEmail.value.trim(),
    })
    reminderMessage.value = data?.message
      || 'If that email is registered, we have sent the username to it.'
  } catch (error) {
    if (error.response?.status === 429) {
      reminderError.value = true
      reminderMessage.value = 'Too many requests. Wait a minute and try again.'
    } else if (error.response?.status === 422) {
      reminderError.value = true
      reminderMessage.value = 'Enter a valid email address.'
    } else {
      reminderError.value = true
      reminderMessage.value = 'We could not process that request. Try again later.'
    }
  } finally {
    reminderLoading.value = false
  }
}

const handleLogin = async () => {
  errorMessage.value = ''
  loading.value = true

  try {
    // Use URLSearchParams for OAuth2 password flow (application/x-www-form-urlencoded)
    const params = new URLSearchParams()
    params.append('username', username.value)
    params.append('password', password.value)
    if (mfaRequired.value && mfaCode.value.trim()) {
      params.append('totp_code', mfaCode.value.trim())
    }

    const response = await axios.post('/api/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    localStorage.setItem('token', response.data.access_token)
    localStorage.setItem('user', JSON.stringify(response.data.user))

    // Sync the wiki_auth cookie now, in THIS tab. App.vue only refreshes it on
    // mount (token was null then) and on cross-tab storage events (which do not
    // fire in the tab that logged in), so without this a fresh login cannot open
    // the gated course wikis until a full page reload.
    setWikiAuthCookie()

    const updateAuthState = inject('updateAuthState', null)
    if (updateAuthState) {
      updateAuthState()
    } else if (window.__updateAuthState) {
      window.__updateAuthState()
    }

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    router.push('/dashboard')
  } catch (error) {
    const mfaHeader = error.response?.headers?.['x-mfa-required']
    if (mfaHeader === 'true' || error.response?.data?.detail === 'MFA code required') {
      mfaRequired.value = true
      errorMessage.value = mfaCode.value.trim()
        ? 'That authenticator code was not accepted. Try the current code or a recovery code.'
        : 'Enter the code from your authenticator app to finish signing in.'
    } else {
      mfaRequired.value = false
      mfaCode.value = ''
      if (error.response?.data?.detail) {
        errorMessage.value = error.response.data.detail
      } else {
        errorMessage.value = 'Login failed. Please check your credentials and try again.'
      }
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  background: var(--bg-primary);
}

.login-powered {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.28rem 0.4rem 0.28rem 0.6rem;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.62);
  box-shadow: 0 6px 20px rgba(2, 6, 23, 0.28);
  backdrop-filter: blur(10px);
}

.login-powered__brand {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 999px;
  color: #cbd5e1;
  font-size: 0.62rem;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.15s ease;
}

.login-powered__brand:hover {
  color: #f8fafc;
}

.login-powered__brand img {
  height: 14px;
  width: auto;
  padding: 1px 3px;
  border-radius: 3px;
  background: #ffffff;
}

.login-powered__divider {
  width: 1px;
  height: 14px;
  background: rgba(148, 163, 184, 0.28);
}

.login-powered__social {
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  color: #cbd5e1;
  transition: background 0.15s ease, color 0.15s ease;
}

.login-powered__social:hover {
  background: rgba(56, 189, 248, 0.16);
  color: #e0f2fe;
}

.login-powered__social svg {
  width: 13px;
  height: 13px;
}

.login-powered a:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}

.login-split {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  min-height: 100vh;
}

/* Left: form */
.login-form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  background: var(--bg-primary);
}

.form-panel-inner {
  width: 100%;
  max-width: 400px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin-bottom: 1.75rem;
}

.brand-icon {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  object-fit: contain;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.brand-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
}

.form-subtext {
  color: var(--text-secondary);
  font-size: 0.9375rem;
  margin-bottom: 1.75rem;
}

.success-message,
.error-message {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
}

.success-message {
  background: var(--success-bg);
  border: 1px solid color-mix(in srgb, var(--success) 40%, transparent);
  color: var(--text-primary);
}

.error-message {
  background: var(--danger-bg);
  border: 1px solid color-mix(in srgb, var(--danger) 40%, transparent);
  color: var(--danger);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.form-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.forgot-username-link {
  align-self: flex-start;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.forgot-username-link:hover {
  text-decoration: underline;
}

.forgot-username-panel {
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.forgot-username-help {
  margin: 0 0 0.6rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.45;
}

.forgot-username-row {
  display: flex;
  gap: 0.5rem;
}

.forgot-username-row .form-input {
  min-width: 0;
}

.forgot-username-submit {
  flex-shrink: 0;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--accent);
  border-radius: 6px;
  background: transparent;
  color: var(--accent);
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
}

.forgot-username-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.forgot-username-message {
  margin: 0.5rem 0 0;
  color: var(--success);
  font-size: 0.76rem;
}

.forgot-username-message--error {
  color: var(--danger);
}

.form-input {
  width: 100%;
  padding: 0.8rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9375rem;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 18%, transparent);
}

.form-input::placeholder {
  color: var(--text-muted);
}

.form-input--error {
  border-color: var(--danger);
}

.form-input--error:focus {
  border-color: var(--danger);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--danger) 18%, transparent);
}

.password-wrap {
  position: relative;
}

.password-wrap .form-input {
  padding-right: 4.5rem;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 0.5rem;
  transform: translateY(-50%);
  padding: 0.35rem 0.5rem;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
}

.password-toggle:hover,
.password-toggle:focus-visible {
  color: var(--text-primary);
  background: var(--bg-tertiary);
  outline: none;
}

.mfa-help {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.78rem;
  line-height: 1.45;
}

.login-button {
  width: 100%;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, var(--accent), var(--purple));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
  margin-top: 0.25rem;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px color-mix(in srgb, var(--accent) 30%, transparent);
  filter: brightness(1.05);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-security {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  margin: 1rem 0 0;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.login-security svg {
  width: 14px;
  height: 14px;
}

.register-section {
  margin-top: 1.5rem;
  text-align: center;
}

.register-text {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.register-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  margin-left: 0.25rem;
}

.register-link:hover {
  text-decoration: underline;
}

/* Right: platform preview */
.login-hero-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2.5rem;
  background:
    radial-gradient(circle at 15% 10%, color-mix(in srgb, var(--accent) 28%, transparent), transparent 42%),
    radial-gradient(circle at 90% 80%, color-mix(in srgb, var(--purple) 24%, transparent), transparent 46%),
    #0b1220;
  color: #e2e8f0;
  position: relative;
  overflow: hidden;
}

.login-hero-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
  background-size: 26px 26px;
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  max-width: 560px;
}

.hero-head {
  max-width: 46ch;
}

.hero-kicker {
  display: inline-block;
  margin-bottom: 0.5rem;
  color: #93c5fd;
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.hero-title {
  margin: 0 0 0.6rem;
  color: #f8fafc;
  font-size: clamp(1.45rem, 2.2vw, 2rem);
  line-height: 1.15;
  letter-spacing: -0.025em;
}

.hero-subtitle {
  margin: 0;
  color: #cbd5e1;
  font-size: 0.86rem;
  line-height: 1.55;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

.preview-card {
  min-width: 0;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.055);
  backdrop-filter: blur(6px);
}

.preview-card__head {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.55rem;
  color: #dbeafe;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.preview-card__head svg {
  width: 16px;
  height: 16px;
  color: #93c5fd;
}

.preview-lab-list {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.preview-lab-list li {
  display: grid;
  grid-template-columns: 8px minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
}

.preview-lab-list strong {
  display: block;
  color: #f1f5f9;
  font-size: 0.7rem;
  font-weight: 600;
  overflow-wrap: anywhere;
}

.preview-lab-list small {
  display: block;
  color: #94a3b8;
  font-size: 0.6rem;
}

.preview-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.preview-dot--done { background: #22c55e; }
.preview-dot--next { background: #f59e0b; }
.preview-dot--locked { background: #64748b; }

.preview-status {
  color: #94a3b8;
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
}

.mini-terminal {
  padding: 0.55rem 0.6rem;
  border-radius: 8px;
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.63rem;
  line-height: 1.55;
}

.mini-terminal__bar {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 0.35rem;
}

.mini-terminal__bar span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #475569;
}

.mini-terminal__bar span:first-child { background: #f38ba8; }
.mini-terminal__bar span:nth-child(2) { background: #f9e2af; }
.mini-terminal__bar span:nth-child(3) { background: #a6e3a1; }

.mini-terminal__bar small {
  margin-left: 0.3rem;
  color: #64748b;
  font-size: 0.58rem;
}

.mini-terminal p {
  margin: 0;
  color: #cbd5e1;
  overflow-wrap: anywhere;
}

.mini-terminal b { color: #86efac; }
.mini-terminal__muted { color: #94a3b8 !important; }
.mini-terminal__ok { color: #86efac !important; }

.preview-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.preview-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.28rem 0.45rem;
  border: 1px solid rgba(147, 197, 253, 0.3);
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.12);
  color: #dbeafe;
  font-size: 0.62rem;
  font-weight: 700;
}

.preview-badge svg {
  width: 13px;
  height: 13px;
  color: #93c5fd;
}

.preview-card--certificate {
  display: flex;
  align-items: center;
}

.preview-certificate {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
  width: 100%;
  padding: 0.6rem;
  border: 1px solid rgba(251, 191, 36, 0.32);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(251, 191, 36, 0.1), transparent 52%),
    rgba(15, 23, 42, 0.55);
}

.preview-certificate__brandline {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.3rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid rgba(251, 191, 36, 0.18);
  color: #f8fafc;
  font-size: 0.56rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.preview-certificate__logo {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.preview-certificate__powered {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  margin-left: auto;
  color: #94a3b8;
  font-size: 0.48rem;
  font-weight: 600;
  letter-spacing: 0;
  text-transform: none;
}

.preview-certificate__site {
  color: #cbd5e1;
  text-decoration: none;
  transition: color 0.15s ease;
}

.preview-certificate__site:hover {
  color: #f8fafc;
  text-decoration: underline;
}

.preview-certificate__social {
  display: grid;
  place-items: center;
  width: 15px;
  height: 15px;
  border-radius: 3px;
  background: rgba(56, 189, 248, 0.16);
  color: #93c5fd;
  transition: background 0.15s ease, color 0.15s ease;
}

.preview-certificate__social:hover {
  background: rgba(56, 189, 248, 0.28);
  color: #e0f2fe;
}

.preview-certificate__social svg {
  width: 9px;
  height: 9px;
}

.preview-certificate a:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
  border-radius: 3px;
}

.preview-certificate__main {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
}

.preview-certificate__seal {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  border-radius: 50%;
  border: 1px solid rgba(251, 191, 36, 0.65);
  background:
    radial-gradient(circle at 35% 30%, rgba(255, 255, 255, 0.22), transparent 45%),
    rgba(251, 191, 36, 0.14);
  color: #fbbf24;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.04em;
  box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.07);
}

.preview-certificate__body {
  min-width: 0;
}

.preview-certificate__eyebrow {
  display: block;
  color: #fbbf24;
  font-size: 0.52rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.preview-certificate__name {
  display: block;
  margin: 0.1rem 0 0.12rem;
  color: #f8fafc;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  overflow-wrap: anywhere;
}

.preview-certificate__body > span:not(.preview-certificate__verified) {
  display: block;
  color: #dbeafe;
  font-size: 0.62rem;
  line-height: 1.4;
}

.preview-certificate__meta {
  display: block;
  margin-top: 0.15rem;
  color: #94a3b8;
  font-size: 0.54rem;
}

.preview-certificate__verified {
  display: inline-flex;
  align-items: center;
  gap: 0.22rem;
  margin-top: 0.3rem;
  color: #86efac;
  font-size: 0.54rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.preview-certificate__verified svg {
  width: 11px;
  height: 11px;
}

.hero-note {
  margin: 0;
  color: #94a3b8;
  font-size: 0.68rem;
  line-height: 1.5;
}

@media (max-width: 960px) {
  .login-split {
    grid-template-columns: 1fr;
  }

  .login-hero-panel {
    padding: 2rem 1.5rem;
  }

  .hero-content {
    max-width: 640px;
  }
}

@media (max-width: 560px) {
  .login-powered {
    top: 0.6rem;
    right: 0.6rem;
    padding: 0.24rem 0.32rem 0.24rem 0.5rem;
  }

  .login-powered__brand {
    font-size: 0.58rem;
  }

  .login-powered img {
    height: 12px;
  }

  .login-form-panel {
    padding: 2rem 1rem;
  }

  .login-hero-panel {
    padding: 1.75rem 1rem;
  }

  .preview-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    font-size: 1.45rem;
  }

  .brand-icon {
    width: 60px;
    height: 60px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .form-input,
  .login-button,
  .password-toggle,
  .login-powered__brand,
  .login-powered__social,
  .preview-certificate__site,
  .preview-certificate__social {
    transition: none;
  }
}
</style>
