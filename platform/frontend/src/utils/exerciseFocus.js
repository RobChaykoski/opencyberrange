// Exercise catalogue focus helpers.
//
// The catalogue is intentionally progressive: a new learner sees the tracks
// that match their career target, while anyone can open the full catalogue.
// These helpers stay pure so the view and the tests share the same rules.

export const EXERCISE_VIEW_KEY = 'ocr.exercise-view'
export const FOCUS_THRESHOLD = 3

export function focusTracks(tracks, slugs) {
  if (!Array.isArray(tracks) || !Array.isArray(slugs) || slugs.length === 0) {
    return []
  }
  const wanted = new Set(slugs)
  return tracks.filter((track) => wanted.has(track.slug))
}

export function scopeProgress(tracks) {
  const rows = Array.isArray(tracks) ? tracks : []
  const completed = rows.reduce((sum, track) => sum + Number(track.completed_labs || 0), 0)
  const total = rows.reduce((sum, track) => sum + Number(track.total_labs || 0), 0)
  return {
    completed,
    total,
    percent: total > 0 ? Math.round((completed / total) * 100) : 0,
  }
}

export function focusedComplete(tracks) {
  const rows = Array.isArray(tracks) ? tracks : []
  return rows.length > 0 && rows.every((track) => track.is_complete)
}

export function defaultExerciseView(completedLabs, focusedCount, storedView = '') {
  if (storedView === 'focused' || storedView === 'all') return storedView
  return focusedCount > 0 && Number(completedLabs || 0) < FOCUS_THRESHOLD
    ? 'focused'
    : 'all'
}

export function readStoredExerciseView() {
  try {
    const value = localStorage.getItem(EXERCISE_VIEW_KEY)
    return value === 'focused' || value === 'all' ? value : ''
  } catch {
    return ''
  }
}

export function storeExerciseView(view) {
  if (view !== 'focused' && view !== 'all') return
  try {
    localStorage.setItem(EXERCISE_VIEW_KEY, view)
  } catch {
    // Private modes may block storage; the in-memory choice still applies.
  }
}
