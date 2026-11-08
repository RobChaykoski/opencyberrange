import { ref } from 'vue'
import api from '../api/axios'

const STORAGE_KEY = 'privacy-mode'
// Older builds wrote the admin default into STORAGE_KEY, so a stored "on" value
// is not proof that the admin chose it. The marker is written only when the
// sidebar or Settings toggle is used, which makes the explicit choice durable
// while letting a changed platform default reach browsers that never chose.
const EXPLICIT_KEY = 'privacy-mode-explicit'

function storedPrivacy() {
  const value = localStorage.getItem(STORAGE_KEY)
  if (value === 'off') return false
  if (value === 'on' && localStorage.getItem(EXPLICIT_KEY) === '1') return true
  return null
}

function currentUserRole() {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}').role || ''
  } catch {
    return ''
  }
}

// Admin accounts start with privacy mode on so names, emails, and student
// identifiers are masked during screen sharing or shoulder-surfing. The
// platform default is editable in Admin > Settings > Security; an explicit
// per-browser preference always wins.
const adminPrivacyDefault = ref(true)
let privacyDefaultLoaded = false
let privacyDefaultRequest = null

const privacyMode = ref(storedPrivacy() ?? currentUserRole() === 'admin')

function maskUsername(name) {
  if (!name) return ''
  if (!privacyMode.value) return name
  if (name.length <= 2) return name
  return name[0] + '\u2022'.repeat(name.length - 2) + name[name.length - 1]
}

function maskEmail(email) {
  if (!email) return ''
  if (!privacyMode.value) return email
  const [local, domain] = email.split('@')
  if (!domain) return email[0] + '\u2022\u2022\u2022'
  return local[0] + '\u2022\u2022\u2022@' + domain[0] + '\u2022\u2022\u2022.' + domain.split('.').pop()
}

function togglePrivacy() {
  privacyMode.value = !privacyMode.value
  localStorage.setItem(STORAGE_KEY, privacyMode.value ? 'on' : 'off')
  localStorage.setItem(EXPLICIT_KEY, '1')
}

async function fetchPrivacyDefault(role) {
  try {
    // The category endpoint is admin-only, which is fine: only admins use the
    // platform default. Instructors keep the existing per-browser behaviour.
    const { data } = await api.get('/settings/security')
    const row = Array.isArray(data)
      ? data.find(item => item.key === 'privacy_default_on')
      : null
    if (row) adminPrivacyDefault.value = row.value === 'true'
    privacyDefaultLoaded = true
    applyPrivacyDefaultForRole(role)
  } catch {
    // Keep the secure default and retry on the next role check.
  }
}

/**
 * Apply the admin default when the user has never chosen explicitly.
 * Call after login, setup, or restoring an impersonated session.
 */
export function applyPrivacyDefaultForRole(role) {
  if (role === 'admin' && !privacyDefaultLoaded && !privacyDefaultRequest) {
    privacyDefaultRequest = fetchPrivacyDefault(role).finally(() => {
      privacyDefaultRequest = null
    })
  }
  if (storedPrivacy() !== null) return
  privacyMode.value = role === 'admin' ? adminPrivacyDefault.value : false
}

/**
 * Update the cached default after the admin saves the setting, so a change is
 * reflected immediately in a browser that has no explicit preference.
 */
export function setAdminPrivacyDefault(value) {
  adminPrivacyDefault.value = !!value
  privacyDefaultLoaded = true
  applyPrivacyDefaultForRole(currentUserRole())
}

export function usePrivacy() {
  return {
    privacyMode,
    maskUsername,
    maskEmail,
    togglePrivacy,
    applyPrivacyDefaultForRole,
    setAdminPrivacyDefault,
  }
}
