<template>
  <section class="privacy-panel">
    <h2 class="section-title">Privacy and data</h2>
    <p class="privacy-panel__lead">
      You can download a copy of your personal data or permanently delete your
      account. Deletion is immediate and cannot be undone.
    </p>

    <section class="privacy-panel__email" aria-labelledby="email-pref-title">
      <div class="privacy-panel__email-head">
        <div>
          <h3 id="email-pref-title">Email preferences</h3>
          <p class="privacy-panel__email-help">
            We collect your email address to create and secure your account,
            confirm registration, and send essential service notices. We do not
            sell your email or use it for marketing.
          </p>
        </div>
      </div>

      <label class="privacy-panel__email-toggle">
        <input
          v-model="emailNotifications"
          type="checkbox"
          :disabled="emailSaving"
          @change="saveEmailPreference"
        />
        <span>Email me about my account</span>
      </label>

      <p class="privacy-panel__email-help">
        Under PIPEDA, you can withdraw consent to optional account email at any
        time. Turning this off does not close your account. Essential security
        and service messages may still be sent where required to operate your
        account. You can access, correct, export, or delete your information
        from this panel, and contact the privacy contact for questions.
      </p>
      <p v-if="emailConsentUpdatedAt" class="privacy-panel__email-meta">
        Consent preference updated {{ formatExportDate(emailConsentUpdatedAt) }}
        <template v-if="emailConsentVersion"> · version {{ emailConsentVersion }}</template>
      </p>
      <p v-if="emailMessage" :class="emailError ? 'error-message' : 'success-message'" role="status">
        {{ emailMessage }}
      </p>
    </section>

    <div class="privacy-panel__actions">
      <button
        type="button"
        class="btn btn--secondary"
        :disabled="exporting"
        @click="downloadData"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        {{ exporting ? 'Preparing download...' : 'Download my data' }}
      </button>

      <button
        v-if="!confirming"
        type="button"
        class="btn btn--danger"
        @click="confirming = true"
      >
        Delete my account
      </button>
    </div>

    <p v-if="exportError" class="error-message" role="alert">{{ exportError }}</p>
    <p v-if="exportSuccess" class="success-message" role="status">{{ exportSuccess }}</p>
    <p class="privacy-panel__last-export">
      <template v-if="exportStatusLoading">Checking your last download...</template>
      <template v-else-if="lastExportedAt">
        Most recent copy downloaded: {{ formatExportDate(lastExportedAt) }}
      </template>
      <template v-else>You have not downloaded a copy of your data yet.</template>
    </p>

    <div v-if="confirming" class="privacy-panel__confirm">
      <h3 class="privacy-panel__confirm-title">Permanently delete your account</h3>
      <p>
        This removes your profile, password, MFA settings, VPN configuration,
        progress, badges, course enrolments, quiz attempts, lab sessions and
        activity history. It cannot be reversed.
      </p>
      <p class="privacy-panel__retention">
        Security audit records are anonymised and kept for up to 90 days. Backups
        rotate on a 30-day cycle, so a copy of your data may remain in a backup
        for that period before it is overwritten.
      </p>

      <div v-if="blockedMessage" class="privacy-panel__blocked" role="alert">
        <p>{{ blockedMessage }}</p>
        <ul v-if="blockedCourses.length">
          <li v-for="course in blockedCourses" :key="course.id">
            {{ course.code }} &mdash; {{ course.name }}
          </li>
        </ul>
        <p v-if="blockedCourses.length" class="privacy-panel__blocked-hint">
          Ask a platform administrator to transfer these courses to another
          instructor, then return here to delete your account.
        </p>
      </div>

      <form class="privacy-panel__form" @submit.prevent="deleteAccount">
        <div class="form-group">
          <label for="delete-account-password">Current password</label>
          <input
            id="delete-account-password"
            v-model="password"
            type="password"
            class="form-input"
            autocomplete="current-password"
            required
          />
        </div>

        <div v-if="mfaEnabled" class="form-group">
          <label for="delete-account-code">Authenticator or recovery code</label>
          <input
            id="delete-account-code"
            v-model="code"
            type="text"
            class="form-input"
            inputmode="numeric"
            autocomplete="one-time-code"
            placeholder="6-digit code"
          />
        </div>

        <div class="form-group">
          <label for="delete-account-confirm">
            Type <strong>DELETE</strong> to confirm
          </label>
          <input
            id="delete-account-confirm"
            v-model="confirmation"
            type="text"
            class="form-input"
            autocomplete="off"
            spellcheck="false"
            required
          />
        </div>

        <p v-if="error" class="error-message" role="alert">{{ error }}</p>

        <div class="privacy-panel__form-actions">
          <button
            type="submit"
            class="btn btn--danger"
            :disabled="deleting || confirmation !== 'DELETE' || !password"
          >
            {{ deleting ? 'Deleting...' : 'Delete permanently' }}
          </button>
          <button
            type="button"
            class="btn btn--secondary"
            :disabled="deleting"
            @click="cancel"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../api/axios'
import { clearWikiAuthCookie } from '../utils/wikiAuth'

defineProps({
  mfaEnabled: { type: Boolean, default: false },
})

const router = useRouter()

const exporting = ref(false)
const exportError = ref('')
const exportSuccess = ref('')
const lastExportedAt = ref(null)
const exportStatusLoading = ref(true)
const emailNotifications = ref(true)
const emailConsentVersion = ref('')
const emailConsentUpdatedAt = ref('')
const emailSaving = ref(false)
const emailMessage = ref('')
const emailError = ref(false)

const formatExportDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

const fetchExportStatus = async () => {
  exportStatusLoading.value = true
  try {
    const { data } = await axios.get('/auth/settings')
    lastExportedAt.value = data.data_exported_at || null
    emailNotifications.value = data.email_notifications !== false
    emailConsentVersion.value = data.email_consent_version || ''
    emailConsentUpdatedAt.value = data.email_consent_updated_at || ''
  } catch {
    lastExportedAt.value = null
  } finally {
    exportStatusLoading.value = false
  }
}

onMounted(fetchExportStatus)

const saveEmailPreference = async () => {
  emailSaving.value = true
  emailMessage.value = ''
  emailError.value = false
  const previous = !emailNotifications.value
  try {
    await axios.put('/auth/settings', {
      email_notifications: emailNotifications.value,
    })
    await fetchExportStatus()
    emailMessage.value = emailNotifications.value
      ? 'Email preference saved. We will email you about your account.'
      : 'Email preference saved. Optional account email is now off.'
  } catch {
    emailNotifications.value = previous
    emailError.value = true
    emailMessage.value = 'Could not save your email preference. Please try again.'
  } finally {
    emailSaving.value = false
  }
}

const confirming = ref(false)
const password = ref('')
const code = ref('')
const confirmation = ref('')
const deleting = ref(false)
const error = ref('')
const blockedMessage = ref('')
const blockedCourses = ref([])

const cancel = () => {
  confirming.value = false
  password.value = ''
  code.value = ''
  confirmation.value = ''
  error.value = ''
  blockedMessage.value = ''
  blockedCourses.value = []
}

const downloadData = async () => {
  exporting.value = true
  exportError.value = ''
  exportSuccess.value = ''
  try {
    const { data } = await axios.get('/auth/export')
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `swocts-cyber-range-data-${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    lastExportedAt.value = data.generated_at || new Date().toISOString()
    exportSuccess.value = 'Your data export has been downloaded.'
  } catch (e) {
    exportError.value =
      e.response?.data?.detail || 'Could not prepare your data export.'
  } finally {
    exporting.value = false
  }
}

const clearLocalAccountState = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  Object.keys(localStorage)
    .filter((key) => key.startsWith('ocr_orientation_seen_v1_'))
    .forEach((key) => localStorage.removeItem(key))
  sessionStorage.removeItem('ocr_impersonating')
  clearWikiAuthCookie()
}

const deleteAccount = async () => {
  if (confirmation.value !== 'DELETE') return
  deleting.value = true
  error.value = ''
  blockedMessage.value = ''
  blockedCourses.value = []
  try {
    await axios.post('/auth/delete-account', {
      password: password.value,
      code: code.value.trim() || null,
      confirm: confirmation.value,
    })
    clearLocalAccountState()
    router.push({ path: '/login', query: { deleted: '1' } })
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail && typeof detail === 'object') {
      blockedMessage.value = detail.message || ''
      blockedCourses.value = detail.details?.courses || []
      if (!blockedMessage.value) {
        error.value = 'Could not delete your account.'
      }
    } else {
      error.value = detail || 'Could not delete your account.'
    }
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.privacy-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}

.privacy-panel .section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.privacy-panel__lead {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0 0 0.85rem;
}

.privacy-panel__email {
  margin: 0 0 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
}

.privacy-panel__email-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.privacy-panel__email h3 {
  margin: 0 0 0.35rem;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.privacy-panel__email-help {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.55;
}

.privacy-panel__email-toggle {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  margin: 0.8rem 0;
  color: var(--text-primary);
  font-size: 0.86rem;
  font-weight: 600;
  cursor: pointer;
}

.privacy-panel__email-toggle input {
  margin-top: 0.15rem;
  accent-color: var(--accent);
}

.privacy-panel__email-meta {
  margin: 0.55rem 0 0;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.privacy-panel__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.privacy-panel__actions svg {
  width: 16px;
  height: 16px;
}

.privacy-panel__confirm {
  margin-top: 1.25rem;
  padding: 1rem;
  border: 1px solid color-mix(in srgb, var(--danger) 45%, var(--border-color));
  border-radius: 10px;
  background: var(--danger-bg);
}

.privacy-panel__confirm-title {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.privacy-panel__confirm p {
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.55;
  margin: 0 0 0.6rem;
}

.privacy-panel__retention {
  padding-top: 0.5rem;
  border-top: 1px solid color-mix(in srgb, var(--danger) 30%, transparent);
}

.privacy-panel__blocked {
  margin: 0.75rem 0;
  padding: 0.75rem;
  border-radius: 8px;
  background: var(--warning-bg);
  color: var(--text-primary);
  font-size: 0.85rem;
}

.privacy-panel__blocked p {
  color: var(--text-primary);
  margin: 0 0 0.35rem;
}

.privacy-panel__blocked ul {
  margin: 0.35rem 0;
  padding-left: 1.25rem;
}

.privacy-panel__blocked-hint {
  color: var(--text-secondary) !important;
}

.privacy-panel__form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.85rem;
}

.privacy-panel__form .form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.privacy-panel__form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 0.25rem;
}

@media (max-width: 640px) {
  .privacy-panel__actions,
  .privacy-panel__form-actions {
    flex-direction: column;
  }

  .privacy-panel__actions .btn,
  .privacy-panel__form-actions .btn {
    width: 100%;
  }
}
</style>
