import { ref } from 'vue'

const STORAGE_KEY = 'ocr.career-goal'

function readStoredGoal() {
  try {
    return localStorage.getItem(STORAGE_KEY) || 'soc-analyst'
  } catch (e) {
    return 'soc-analyst'
  }
}

// Shared across the profile so the role selector, readiness panel, and GPS
// all describe the same goal. This is a preference, not evidence.
const selectedRole = ref(readStoredGoal())

export function useCareerGoal() {
  function setGoal(roleId) {
    if (!roleId) return
    selectedRole.value = roleId
    try {
      localStorage.setItem(STORAGE_KEY, roleId)
    } catch (e) {
      // Storage can be unavailable in private modes; the in-memory value is enough.
    }
  }

  return { selectedRole, setGoal }
}
