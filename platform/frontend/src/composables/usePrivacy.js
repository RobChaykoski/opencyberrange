import { ref } from 'vue'

const STORAGE_KEY = 'privacy-mode'

function storedPrivacy() {
  const value = localStorage.getItem(STORAGE_KEY)
  if (value === 'on') return true
  if (value === 'off') return false
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
// identifiers are masked during screen sharing or shoulder-surfing. A stored
// explicit preference always wins.
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
}

/**
 * Apply the admin default once, if the user has never chosen explicitly.
 * Call after login, setup, or restoring an impersonated session.
 */
export function applyPrivacyDefaultForRole(role) {
  if (storedPrivacy() !== null) return
  if (role === 'admin') {
    privacyMode.value = true
    localStorage.setItem(STORAGE_KEY, 'on')
  }
}

export function usePrivacy() {
  return { privacyMode, maskUsername, maskEmail, togglePrivacy, applyPrivacyDefaultForRole }
}
