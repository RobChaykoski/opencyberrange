import { beforeEach, describe, expect, it } from 'vitest'

import {
  EXERCISE_VIEW_KEY,
  defaultExerciseView,
  focusTracks,
  focusedComplete,
  readStoredExerciseView,
  scopeProgress,
  storeExerciseView,
} from '../exerciseFocus'

const tracks = [
  { slug: 'netfor', completed_labs: 2, total_labs: 5, is_complete: false },
  { slug: 'linpt', completed_labs: 5, total_labs: 5, is_complete: true },
  { slug: 'webpt', completed_labs: 0, total_labs: 8, is_complete: false },
]

describe('exercise focus helpers', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('keeps only tracks in the selected career pathway, in catalogue order', () => {
    expect(focusTracks(tracks, ['webpt', 'netfor']).map((track) => track.slug)).toEqual([
      'netfor',
      'webpt',
    ])
  })

  it('falls back to an empty focus when the pathway has no tracks', () => {
    expect(focusTracks(tracks, [])).toEqual([])
    expect(focusTracks(tracks, ['missing'])).toEqual([])
  })

  it('computes progress for the visible scope', () => {
    expect(scopeProgress(tracks.slice(0, 2))).toEqual({
      completed: 7,
      total: 10,
      percent: 70,
    })
  })

  it('detects a completed focus without calling an empty focus complete', () => {
    expect(focusedComplete([tracks[1]])).toBe(true)
    expect(focusedComplete([tracks[0], tracks[1]])).toBe(false)
    expect(focusedComplete([])).toBe(false)
  })

  it('starts new learners focused and returning learners on all tracks', () => {
    expect(defaultExerciseView(0, 5)).toBe('focused')
    expect(defaultExerciseView(2, 5)).toBe('focused')
    expect(defaultExerciseView(3, 5)).toBe('all')
    expect(defaultExerciseView(0, 0)).toBe('all')
  })

  it('respects an explicit stored preference', () => {
    expect(defaultExerciseView(0, 5, 'all')).toBe('all')
    expect(defaultExerciseView(10, 5, 'focused')).toBe('focused')
  })

  it('persists only a valid view choice', () => {
    storeExerciseView('focused')
    expect(localStorage.getItem(EXERCISE_VIEW_KEY)).toBe('focused')
    expect(readStoredExerciseView()).toBe('focused')
    storeExerciseView('nonsense')
    expect(readStoredExerciseView()).toBe('focused')
  })
})
