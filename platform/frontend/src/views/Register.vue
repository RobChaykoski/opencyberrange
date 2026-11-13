<template>
  <div class="register-page">
    <a class="skip-link" href="#register-form">Skip to registration form</a>
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
    <div class="register-split">
      <!-- Left: Form Panel -->
      <main class="register-form-panel" id="register-form" tabindex="-1">
        <div class="form-panel-inner">
          <!-- Brand -->
          <div class="brand">
            <img src="/swocts-cyber-range-mark.png" alt="" class="brand-icon" />
            <div class="brand-text">
              <h1 class="brand-title">SWOCTS Cyber Range</h1>
              <p class="brand-subtitle">Create Account</p>
            </div>
          </div>

          <p class="form-subtext">Build hands-on skills you can prove</p>

          <div v-if="competition" class="competition-callout">
            <p class="competition-callout__kicker">Event registration</p>
            <p>
              You are creating an account for <strong>{{ competition.name }}</strong>.
              The event runs {{ formatCompetitionDates(competition) }}.
            </p>
            <label v-if="competition.status !== 'ended'" class="competition-callout__join">
              <input v-model="joinCompetition" type="checkbox" />
              <span>Add me to the event participant list</span>
            </label>
            <p v-else class="help-text">
              This event has finished. You can still create an account and explore the platform.
            </p>
            <p v-if="competition.status !== 'ended'" class="help-text">
              Your Celebration Wall name preference appears on the event leaderboard:
              real name, username, or "Anonymous participant".
            </p>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" ref="errorBanner" tabindex="-1" class="error-message" role="alert" aria-live="assertive" aria-atomic="true">
            {{ errorMessage }}
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" ref="successBanner" tabindex="-1" class="success-message" role="status" aria-live="polite">
            {{ successMessage }}
          </div>

          <form @submit.prevent="handleRegister" class="register-form" :aria-busy="loading" novalidate>
            <div class="form-group">
              <label for="username" class="form-label">Username</label>
              <input
                id="username"
                ref="usernameInput"
                v-model="form.username"
                name="username"
                type="text"
                class="form-input"
                :class="{ 'form-input--error': errors.username }"
                placeholder="Enter your username"
                required
                minlength="3"
                maxlength="50"
                autocomplete="username"
                autocapitalize="none"
                autocorrect="off"
                spellcheck="false"
                aria-describedby="username-help"
                :aria-invalid="errors.username ? 'true' : 'false'"
                @blur="validateUsername"
              />
              <p v-if="errors.username" id="username-help" class="error-text">{{ errors.username }}</p>
              <p v-else id="username-help" class="help-text">
                Must start with a letter and contain only letters, numbers, underscores, and hyphens (3-50 characters)
              </p>
            </div>

            <div class="form-group">
              <label for="email" class="form-label">Email</label>
              <input
                id="email"
                ref="emailInput"
                v-model="form.email"
                name="email"
                type="email"
                class="form-input"
                :class="{ 'form-input--error': errors.email }"
                placeholder="Enter your email"
                required
                maxlength="100"
                autocomplete="email"
                inputmode="email"
                autocapitalize="none"
                autocorrect="off"
                spellcheck="false"
                aria-describedby="email-help"
                :aria-invalid="errors.email ? 'true' : 'false'"
                @blur="validateEmail"
              />
              <p v-if="errors.email" id="email-help" class="error-text">{{ errors.email }}</p>
              <p v-else id="email-help" class="help-text">
                We use your email for sign-in and essential security notices. It is not marketing.
              </p>
            </div>

            <div class="form-group">
              <label class="form-check" for="sendRegistrationEmail">
                <input
                  id="sendRegistrationEmail"
                  v-model="form.sendRegistrationEmail"
                  type="checkbox"
                />
                <span>Email me a registration confirmation</span>
              </label>
              <p class="help-text">
                Optional. We use your email only to confirm this account and, where enabled,
                to deliver essential security notices. It is not marketing. If you leave this
                unchecked, no registration email is sent. You can review your data and account
                controls later under Profile → Privacy and data.
              </p>
              <p class="help-text">
                By creating an account you acknowledge the
                <router-link to="/privacy">Privacy notice</router-link>. Privacy questions
                can be sent to
                <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>.
              </p>
            </div>

            <div class="form-group">
              <label for="firstName" class="form-label">First name <span class="label-optional">(optional)</span></label>
              <input
                id="firstName"
                v-model="form.firstName"
                name="given-name"
                type="text"
                class="form-input"
                maxlength="80"
                placeholder="Enter your first name"
                autocomplete="given-name"
              />
            </div>

            <div class="form-group">
              <label for="lastName" class="form-label">Last name <span class="label-optional">(optional)</span></label>
              <input
                id="lastName"
                v-model="form.lastName"
                name="family-name"
                type="text"
                class="form-input"
                maxlength="80"
                placeholder="Enter your last name"
                autocomplete="family-name"
              />
              <p class="help-text">Your name appears on completion certificates. You can change it later in your profile.</p>
            </div>

            <div class="form-group">
              <label for="password" class="form-label">Password</label>
              <div class="input-wrapper">
                <input
                  id="password"
                  ref="passwordInput"
                  v-model="form.password"
                  name="new-password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input"
                  :class="{ 'form-input--error': errors.password }"
                  placeholder="Enter your password"
                  required
                  minlength="8"
                  maxlength="128"
                  autocomplete="new-password"
                  spellcheck="false"
                  :aria-describedby="passwordCapsLock
                    ? 'password-help password-checklist password-strength password-caps-warning'
                    : 'password-help password-checklist password-strength'"
                  :aria-invalid="errors.password ? 'true' : 'false'"
                  @blur="validatePassword(); passwordCapsLock = false"
                  @keydown="checkPasswordCapsLock"
                  @keyup="checkPasswordCapsLock"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="password-toggle"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  :aria-pressed="showPassword ? 'true' : 'false'"
                >
                  <svg v-if="showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <p v-if="errors.password" id="password-help" class="error-text">{{ errors.password }}</p>
              <p v-else id="password-help" class="help-text">
                At least 8 characters, with uppercase, lowercase, and a number. Avoid common words, names, and simple patterns.
              </p>
              <p v-if="passwordCapsLock" id="password-caps-warning" class="caps-warning" role="status">
                Caps Lock is on.
              </p>
              <ul
                v-if="form.password"
                id="password-checklist"
                class="password-checklist"
                aria-live="polite"
              >
                <li :class="{ 'password-checklist__item--met': passwordChecks.length }">
                  <span aria-hidden="true">{{ passwordChecks.length ? '✓' : '○' }}</span>
                  At least 8 characters
                </li>
                <li :class="{ 'password-checklist__item--met': passwordChecks.upper }">
                  <span aria-hidden="true">{{ passwordChecks.upper ? '✓' : '○' }}</span>
                  An uppercase letter
                </li>
                <li :class="{ 'password-checklist__item--met': passwordChecks.lower }">
                  <span aria-hidden="true">{{ passwordChecks.lower ? '✓' : '○' }}</span>
                  A lowercase letter
                </li>
                <li :class="{ 'password-checklist__item--met': passwordChecks.number }">
                  <span aria-hidden="true">{{ passwordChecks.number ? '✓' : '○' }}</span>
                  A number
                </li>
                <li :class="{ 'password-checklist__item--met': passwordChecks.policy }">
                  <span aria-hidden="true">{{ passwordChecks.policy ? '✓' : '○' }}</span>
                  Not a common word, name, or simple pattern
                </li>
              </ul>
              <div v-if="form.password" class="password-strength" aria-live="polite">
                <div class="password-strength__bar" aria-hidden="true">
                  <span
                    class="password-strength__fill"
                    :class="`password-strength__fill--${passwordStrength.level}`"
                    :style="{ width: `${passwordStrength.percent}%` }"
                  ></span>
                </div>
                <p id="password-strength" class="password-strength__label">
                  Password strength: <strong>{{ passwordStrength.label }}</strong>
                </p>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">Confirm Password</label>
              <div class="input-wrapper">
                <input
                  id="confirmPassword"
                  ref="confirmPasswordInput"
                  v-model="form.confirmPassword"
                  name="confirm-password"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="form-input"
                  :class="{ 'form-input--error': errors.confirmPassword }"
                  placeholder="Confirm your password"
                  required
                  minlength="8"
                  maxlength="128"
                  autocomplete="new-password"
                  spellcheck="false"
                  :aria-describedby="confirmCapsLock
                    ? 'confirm-password-help confirm-caps-warning'
                    : 'confirm-password-help'"
                  :aria-invalid="errors.confirmPassword ? 'true' : 'false'"
                  @blur="validateConfirmPassword(); confirmCapsLock = false"
                  @keydown="checkConfirmCapsLock"
                  @keyup="checkConfirmCapsLock"
                />
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="password-toggle"
                  :aria-label="showConfirmPassword ? 'Hide password confirmation' : 'Show password confirmation'"
                  :aria-pressed="showConfirmPassword ? 'true' : 'false'"
                >
                  <svg v-if="showConfirmPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <p v-if="errors.confirmPassword" id="confirm-password-help" class="error-text">{{ errors.confirmPassword }}</p>
              <p v-else id="confirm-password-help" class="help-text">Re-enter the same password to avoid typos.</p>
              <p v-if="confirmCapsLock" id="confirm-caps-warning" class="caps-warning" role="status">
                Caps Lock is on.
              </p>
            </div>

            <div v-if="inviteRequired" class="form-group">
              <label for="inviteCode" class="form-label">Invite Code</label>
              <input
                id="inviteCode"
                v-model="form.inviteCode"
                type="text"
                class="form-input"
                :class="{ 'form-input--error': errors.inviteCode }"
                placeholder="Enter the code you were given"
                autocomplete="one-time-code"
                autocapitalize="characters"
                autocorrect="off"
                spellcheck="false"
                minlength="4"
                maxlength="64"
                aria-describedby="invite-help"
                :aria-invalid="errors.inviteCode ? 'true' : 'false'"
                @blur="validateInviteCode"
              />
              <p v-if="errors.inviteCode" id="invite-help" class="error-text">{{ errors.inviteCode }}</p>
              <p v-else class="help-text" id="invite-help">
                Registration on this site is limited to people who were given a code. Your instructor issues it.
              </p>
            </div>

            <div class="form-group">
              <label class="form-check" for="isMinor">
                <input
                  id="isMinor"
                  v-model="form.isMinor"
                  name="is_minor"
                  type="checkbox"
                  aria-describedby="minor-help"
                />
                <span>I am under 18</span>
              </label>
              <p id="minor-help" class="help-text">
                If selected, your individual activity is excluded from instructor
                reports and course analytics. Your own progress remains visible to
                you. You can change this later in Profile → Security &amp; privacy.
              </p>
            </div>

            <div class="form-group">
              <label class="form-check" for="privacyAcknowledged">
                <input
                  id="privacyAcknowledged"
                  v-model="form.privacyAcknowledged"
                  name="privacy_acknowledged"
                  type="checkbox"
                  :aria-invalid="errors.privacyAcknowledged ? 'true' : 'false'"
                  aria-describedby="privacy-help"
                  @change="validatePrivacyAcknowledged"
                />
                <span>
                  I acknowledge the Privacy notice. If I am under 18, I have permission
                  from a parent or guardian to use this account.
                </span>
              </label>
              <p id="privacy-help" class="help-text">
                Read the <router-link to="/privacy">Privacy notice</router-link>.
                Privacy questions: <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>.
              </p>
              <p v-if="errors.privacyAcknowledged" class="error-text">
                {{ errors.privacyAcknowledged }}
              </p>
            </div>

            <button
              type="submit"
              class="register-button"
              :disabled="loading"
              :aria-disabled="loading ? 'true' : 'false'"
            >
              <span v-if="!loading">Create Account</span>
              <span v-else>Creating Account...</span>
            </button>
          </form>

          <div class="login-section">
            <p class="login-text">
              Already have an account?
              <router-link to="/login" class="login-link">Sign in here</router-link>
            </p>
            <p class="login-text login-text--about">
              First time here?
              <router-link to="/about" class="login-link">About this site</router-link>
            </p>
          </div>
        </div>
      </main>

      <!-- Right: onboarding preview -->
      <aside class="register-hero-panel" aria-label="What happens after you register">
        <div class="hero-content">
          <div class="hero-head">
            <span class="hero-kicker">Get started</span>
            <h2 class="hero-title">Your first lab is closer than you think.</h2>
            <p class="hero-subtitle">
              Create an account, join your course or event, and start practising
              in the browser. Progress is saved so you can pick up where you left off.
            </p>
          </div>

          <ol class="start-steps" aria-label="Getting started steps">
            <li class="start-step">
              <span class="start-step__num" aria-hidden="true">1</span>
              <span class="start-step__body">
                <strong>Create your account</strong>
                <small>Choose a username and a strong, unique password.</small>
              </span>
            </li>
            <li class="start-step">
              <span class="start-step__num" aria-hidden="true">2</span>
              <span class="start-step__body">
                <strong>Join your course or event</strong>
                <small>Use the invite code or event link from your instructor.</small>
              </span>
            </li>
            <li class="start-step">
              <span class="start-step__num" aria-hidden="true">3</span>
              <span class="start-step__body">
                <strong>Launch your first exercise</strong>
                <small>Open a guided lab and work at your own pace.</small>
              </span>
            </li>
          </ol>

          <div class="preview-grid">
            <article class="preview-card preview-card--certificate">
              <div class="preview-certificate">
                <div class="preview-certificate__top">
                  <span class="preview-certificate__seal">SWOCTS</span>
                  <span class="preview-certificate__label">Certificate of Completion</span>
                </div>
                <strong class="preview-certificate__name">Avery Chen</strong>
                <span class="preview-certificate__track">Network Foundations · Level 1</span>
                <span class="preview-certificate__meta">Verified · SWOCTS-2026-0142</span>
              </div>
            </article>

            <article class="preview-card preview-card--privacy">
              <div class="preview-card__head">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <rect x="4" y="10" width="16" height="10" rx="2"/>
                  <path d="M8 10V7a4 4 0 0 1 8 0v3"/>
                </svg>
                <span>Private by default</span>
              </div>
              <p>
                Your individual progress stays private. Under-18 accounts are
                excluded from instructor reports and course analytics.
              </p>
            </article>
          </div>

          <p class="hero-note">
            You can stop and resume at any time. Event leaderboards use the
            display name you choose.
          </p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios' // Use plain axios for registration (no token needed)
import { passwordPolicyError } from '../utils/passwordPolicy'

const router = useRouter()
const route = useRoute()
const competition = ref(null)
const competitionId = ref(null)
const joinCompetition = ref(true)

const formatCompetitionDates = (event) => {
  if (!event?.start_at || !event?.end_at) return ''
  const start = new Date(event.start_at)
  const end = new Date(event.end_at)
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return ''
  return `${start.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })} – ${end.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}`
}

onMounted(async () => {
  const requested = Number(route.query.event || route.query.competition)
  if (!Number.isInteger(requested) || requested <= 0) return
  competitionId.value = requested
  try {
    const { data } = await axios.get(`/api/competitions/public/${requested}`)
    competition.value = data.competition
    joinCompetition.value = data.competition.status !== 'ended'
  } catch {
    competition.value = null
    competitionId.value = null
  }
})

const form = reactive({
  username: '',
  email: '',
  firstName: '',
  lastName: '',
  password: '',
  confirmPassword: '',
  inviteCode: '',
  sendRegistrationEmail: false,
  privacyAcknowledged: false,
  isMinor: false
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  inviteCode: '',
  privacyAcknowledged: ''
})

// Invite codes are off by default and a class can turn them on. Rather than
// asking every visitor for a code that is usually not needed, the field stays
// hidden until the server tells us one is required, which it does by rejecting
// the first submit. Costs one extra submit in the locked case, and keeps the
// form honest in the common one. Nothing here is a security control; the
// server decides.
const inviteRequired = ref(false)

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)
const errorBanner = ref(null)
const successBanner = ref(null)
const usernameInput = ref(null)
const emailInput = ref(null)
const passwordInput = ref(null)
const confirmPasswordInput = ref(null)
const passwordCapsLock = ref(false)
const confirmCapsLock = ref(false)

const passwordChecks = computed(() => ({
  length: form.password.length >= 8,
  upper: /\p{Lu}/u.test(form.password),
  lower: /\p{Ll}/u.test(form.password),
  number: /\p{Nd}/u.test(form.password),
  policy: form.password
    ? !passwordPolicyError(form.password, {
      username: form.username,
      email: form.email,
      firstName: form.firstName,
      lastName: form.lastName,
    })
    : false,
}))

const passwordStrength = computed(() => {
  const checks = passwordChecks.value
  // A common word with a digit/symbol appended is weak regardless of length.
  if (form.password && !checks.policy) {
    return { level: 'weak', label: 'Weak', percent: 25 }
  }
  let score = 0
  if (checks.length) score += 1
  if (checks.upper) score += 1
  if (checks.lower) score += 1
  if (checks.number) score += 1
  if (form.password.length >= 12) score += 1
  if (/[^\p{L}\p{Nd}]/u.test(form.password)) score += 1
  if (score <= 2) return { level: 'weak', label: 'Weak', percent: 25 }
  if (score <= 4) return { level: 'fair', label: 'Fair', percent: 50 }
  if (score <= 5) return { level: 'good', label: 'Good', percent: 75 }
  return { level: 'strong', label: 'Strong', percent: 100 }
})

const checkPasswordCapsLock = (event) => {
  passwordCapsLock.value = Boolean(event?.getModifierState?.('CapsLock'))
}

const checkConfirmCapsLock = (event) => {
  confirmCapsLock.value = Boolean(event?.getModifierState?.('CapsLock'))
}


const validateUsername = () => {
  errors.username = ''
  if (!form.username) {
    errors.username = 'Username is required'
    return
  }

  if (form.username.length < 3 || form.username.length > 50) {
    errors.username = 'Username must be between 3 and 50 characters'
    return
  }
  if (/\s/.test(form.username)) {
    errors.username = 'Username cannot contain spaces'
    return
  }
  if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(form.username)) {
    errors.username = 'Username must start with a letter and contain only letters, numbers, underscores, and hyphens'
  }
}

const validateEmail = () => {
  errors.email = ''
  if (!form.email) {
    errors.email = 'Email is required'
    return
  }

  const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/
  if (!emailRegex.test(form.email)) {
    errors.email = 'Invalid email format'
  }
}

const setPasswordError = (message) => {
  errors.password = message
}

const validatePassword = () => {
  errors.password = ''
  if (!form.password) {
    setPasswordError('Password is required')
    return
  }

  if (!passwordChecks.value.length) {
    setPasswordError('Password must be at least 8 characters')
    return
  }
  if (!passwordChecks.value.upper) {
    setPasswordError('Password must contain at least one uppercase letter')
    return
  }
  if (!passwordChecks.value.lower) {
    setPasswordError('Password must contain at least one lowercase letter')
    return
  }
  if (!passwordChecks.value.number) {
    setPasswordError('Password must contain at least one number')
    return
  }

  const policyError = passwordPolicyError(form.password, {
    username: form.username,
    email: form.email,
    firstName: form.firstName,
    lastName: form.lastName,
  })
  if (policyError) {
    errors.password = policyError
  }
}

const validateConfirmPassword = () => {
  errors.confirmPassword = ''
  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password'
    return
  }

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
  }
}

// The server accepts invite_code as optional and enforces whether one is
// actually required (the require_invite_code setting), so a blank value is
// valid here. A non-blank value still has to satisfy the server's length
// bounds, and catching that client-side beats a 422 with no useful text.
const validateInviteCode = () => {
  errors.inviteCode = ''
  const code = form.inviteCode.trim()
  if (!code) return
  if (code.length < 4 || code.length > 64) {
    errors.inviteCode = 'Invite code must be between 4 and 64 characters'
  }
}

const validatePrivacyAcknowledged = () => {
  errors.privacyAcknowledged = form.privacyAcknowledged
    ? ''
    : 'Please acknowledge the Privacy notice before creating an account.'
}

const focusFirstInvalidField = async () => {
  await nextTick()
  if (errors.username) usernameInput.value?.focus()
  else if (errors.email) emailInput.value?.focus()
  else if (errors.password) passwordInput.value?.focus()
  else if (errors.confirmPassword) confirmPasswordInput.value?.focus()
  else errorBanner.value?.focus()
}

const handleRegister = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  // Validate all fields
  validateUsername()
  validateEmail()
  validatePassword()
  validateConfirmPassword()
  validateInviteCode()
  validatePrivacyAcknowledged()

  if (errors.username || errors.email || errors.password || errors.confirmPassword || errors.inviteCode || errors.privacyAcknowledged) {
    errorMessage.value = 'Please fix the highlighted fields before creating your account.'
    await focusFirstInvalidField()
    return
  }

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    await focusFirstInvalidField()
    return
  }

  loading.value = true

  try {
    const payload = {
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password,
      send_registration_email: form.sendRegistrationEmail,
      is_minor: form.isMinor
    }
    if (form.firstName.trim()) payload.first_name = form.firstName.trim()
    if (form.lastName.trim()) payload.last_name = form.lastName.trim()
    const inviteCode = form.inviteCode.trim()
    if (inviteCode) {
      payload.invite_code = inviteCode
    }
    if (competitionId.value && joinCompetition.value) {
      payload.competition_id = competitionId.value
    }

    const response = await axios.post('/api/auth/register', payload)

    const approved = response.data?.is_approved === true
    successMessage.value = approved
      ? 'Account created. You can sign in now.'
      : 'Account created successfully! Your account is pending administrator approval. You will be able to log in once approved.'

    // Clear form
    form.username = ''
    form.email = ''
    form.firstName = ''
    form.lastName = ''
    form.password = ''
    form.confirmPassword = ''
    form.inviteCode = ''
    form.privacyAcknowledged = false
    form.isMinor = false
    form.sendRegistrationEmail = false

    await nextTick()
    successBanner.value?.focus()

    // Redirect to login after 5 seconds
    setTimeout(() => {
      router.push('/login')
    }, 5000)
  } catch (error) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string' && /invite code is required/i.test(detail)) {
      inviteRequired.value = true
      errorMessage.value = 'Registration here needs an invite code. Enter the code you were given and submit again.'
    } else if (error.response?.status === 429) {
      errorMessage.value = 'Too many registration attempts. Wait a minute and try again.'
    } else if (Array.isArray(detail)) {
      errorMessage.value = detail.map(err => err.msg || JSON.stringify(err)).join('. ')
    } else if (detail) {
      errorMessage.value = detail
    } else {
      errorMessage.value = 'Registration failed. Please check your information and try again.'
    }
    await nextTick()
    errorBanner.value?.focus()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.skip-link {
  position: absolute;
  left: 1rem;
  top: -100px;
  z-index: 10;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  background: var(--accent);
  color: #08111f;
  font-weight: 700;
  text-decoration: none;
}

.skip-link:focus {
  top: 1rem;
  outline: 3px solid #f8fafc;
  outline-offset: 2px;
}

.register-page {
  position: relative;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* Powered by / social */
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

.register-split {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
  min-height: 100vh;
}

/* Left: form */
.register-form-panel {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 4.5rem 2rem 3rem;
  background: var(--bg-primary);
}

.register-form-panel:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: -3px;
}

.form-panel-inner {
  width: 100%;
  max-width: 440px;
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
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
}

.form-subtext {
  color: var(--text-secondary);
  font-size: 0.9375rem;
  margin-bottom: 1.5rem;
}

.competition-callout {
  margin-bottom: 1.25rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--accent);
  border-radius: 10px;
  background: var(--accent-bg);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.competition-callout__kicker {
  margin: 0 0 0.2rem;
  color: var(--accent-text);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.competition-callout p {
  margin: 0.2rem 0;
}

.competition-callout__join {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
  margin: 0.55rem 0 0.3rem;
  color: var(--text-primary);
  font-weight: 600;
  cursor: pointer;
}

.competition-callout__join input {
  margin-top: 0.15rem;
  accent-color: var(--accent);
}

/* Messages */
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
  color: var(--text-primary);
}

.error-message:focus-visible {
  outline: 3px solid var(--danger);
  outline-offset: 2px;
}

.success-message:focus-visible {
  outline: 3px solid var(--success);
  outline-offset: 2px;
}

.caps-warning {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--warning);
}

/* Form */
.register-form {
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

.label-optional {
  font-weight: 400;
  color: var(--text-muted);
}

.form-check {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
}

.form-check input {
  margin-top: 0.15rem;
  min-width: 1.25rem;
  min-height: 1.25rem;
  accent-color: var(--accent);
}

.input-wrapper {
  position: relative;
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

.input-wrapper .form-input {
  padding-right: 4.75rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 18%, transparent);
}

.form-input::placeholder {
  color: var(--text-secondary);
}

.form-input--error {
  border-color: var(--danger);
}

.form-input--error:focus {
  border-color: var(--danger);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--danger) 18%, transparent);
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 0.25rem;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.75rem;
  min-height: 2.75rem;
  padding: 0.35rem;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
}

.password-toggle:hover,
.password-toggle:focus-visible {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.password-toggle svg {
  width: 20px;
  height: 20px;
}

.help-text {
  margin: 0;
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.45;
}

.error-text {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--danger);
  font-weight: 600;
  line-height: 1.45;
}

.password-checklist {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.3rem 0.75rem;
  margin: 0.15rem 0 0;
  padding: 0;
  list-style: none;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.password-checklist li {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.password-checklist__item--met {
  color: var(--success);
}

.password-strength {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-top: 0.2rem;
}

.password-strength__bar {
  height: 0.4rem;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.password-strength__fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  transition: width 0.2s ease;
}

.password-strength__fill--weak { background: var(--danger); }
.password-strength__fill--fair { background: var(--warning); }
.password-strength__fill--good { background: var(--accent-text); }
.password-strength__fill--strong { background: var(--success); }

.password-strength__label {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.register-button {
  width: 100%;
  min-height: 2.875rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, var(--accent), var(--purple));
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
  margin-top: 0.25rem;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px color-mix(in srgb, var(--accent) 30%, transparent);
  filter: brightness(1.05);
}

.register-button:active:not(:disabled) {
  transform: translateY(0);
}

.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Sign in links */
.login-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.login-text {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.9rem;
  line-height: 1.5;
}

.login-text--about {
  margin-top: 0.55rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.login-link {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 2px;
  font-weight: 700;
  margin-left: 0.25rem;
}

.login-link:hover {
  text-decoration-thickness: 2px;
}

/* Right: onboarding preview */
.register-hero-panel {
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

.register-hero-panel::before {
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
  gap: 1.1rem;
  width: 100%;
  max-width: 520px;
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

.start-steps {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.start-step {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.045);
}

.start-step__num {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 1.55rem;
  height: 1.55rem;
  border-radius: 50%;
  border: 1px solid rgba(147, 197, 253, 0.45);
  background: rgba(59, 130, 246, 0.18);
  color: #dbeafe;
  font-size: 0.72rem;
  font-weight: 800;
}

.start-step__body {
  min-width: 0;
}

.start-step__body strong {
  display: block;
  color: #f1f5f9;
  font-size: 0.8rem;
  font-weight: 600;
}

.start-step__body small {
  display: block;
  margin-top: 0.1rem;
  color: #94a3b8;
  font-size: 0.7rem;
  line-height: 1.45;
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
}

.preview-card__head {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.45rem;
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

.preview-card--certificate {
  display: flex;
  align-items: center;
}

.preview-certificate {
  width: 100%;
  min-width: 0;
  padding: 0.7rem;
  border: 1px solid rgba(251, 191, 36, 0.32);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(251, 191, 36, 0.1), transparent 52%),
    rgba(15, 23, 42, 0.55);
}

.preview-certificate__top {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.45rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(251, 191, 36, 0.18);
}

.preview-certificate__seal {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: 50%;
  border: 1px solid rgba(251, 191, 36, 0.65);
  background:
    radial-gradient(circle at 35% 30%, rgba(255, 255, 255, 0.22), transparent 45%),
    rgba(251, 191, 36, 0.14);
  color: #fbbf24;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 0.36rem;
  font-weight: 900;
  letter-spacing: 0.02em;
  line-height: 1;
  overflow: hidden;
}

.preview-certificate__label {
  flex: 1 1 120px;
  min-width: 0;
  color: #fbbf24;
  font-size: 0.5rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  line-height: 1.25;
  text-transform: uppercase;
}

.preview-certificate__name {
  display: block;
  margin: 0.4rem 0 0.15rem;
  color: #f8fafc;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.preview-certificate__track {
  display: block;
  color: #dbeafe;
  font-size: 0.66rem;
  line-height: 1.4;
}

.preview-certificate__meta {
  display: block;
  margin-top: 0.18rem;
  color: #94a3b8;
  font-size: 0.56rem;
}

.preview-card--privacy {
  display: flex;
  flex-direction: column;
}

.preview-card--privacy p {
  margin: 0;
  color: #cbd5e1;
  font-size: 0.68rem;
  line-height: 1.5;
}

.hero-note {
  margin: 0;
  color: #94a3b8;
  font-size: 0.68rem;
  line-height: 1.5;
}

/* Focus */
.form-input:focus-visible,
.register-button:focus-visible,
.password-toggle:focus-visible,
.login-link:focus-visible,
.form-check input:focus-visible,
.register-form a:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Responsive */
@media (max-width: 960px) {
  .register-split {
    grid-template-columns: 1fr;
  }

  .register-form-panel {
    padding: 3.5rem 1.5rem 2.5rem;
  }

  .form-panel-inner {
    max-width: 560px;
  }

  .register-hero-panel {
    padding: 2.5rem 1.5rem;
  }

  .hero-content {
    max-width: 640px;
  }
}

@media (max-width: 640px) {
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

  .register-form-panel {
    padding: 3rem 1rem 2rem;
  }

  .register-hero-panel {
    padding: 2rem 1rem;
  }

  .hero-title {
    font-size: 1.45rem;
  }

  .preview-grid {
    grid-template-columns: 1fr;
  }

  .brand-icon {
    width: 60px;
    height: 60px;
  }

  .password-checklist {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .form-input,
  .register-button,
  .password-toggle,
  .login-link,
  .login-powered__brand,
  .login-powered__social,
  .password-strength__fill {
    transition: none;
  }

  .register-button:hover:not(:disabled) {
    transform: none;
  }
}
</style>
