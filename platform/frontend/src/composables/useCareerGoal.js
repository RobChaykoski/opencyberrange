import { ref } from 'vue'

const STORAGE_KEY = 'ocr.career-goal'

// New learners start on the foundations pathway. It is deliberately narrower
// than SOC Analyst and maps to the beginner-first exercise catalogue.
export const DEFAULT_CAREER_GOAL = 'cybersecurity-foundations'

function readStoredGoal() {
  try {
    return localStorage.getItem(STORAGE_KEY) || DEFAULT_CAREER_GOAL
  } catch {
    return DEFAULT_CAREER_GOAL
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
    } catch {
      // Storage can be unavailable in private modes; the in-memory value is enough.
    }
  }

  return { selectedRole, setGoal }
}
