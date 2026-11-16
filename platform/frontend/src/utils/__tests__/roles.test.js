import { beforeEach, describe, expect, it } from 'vitest'
import { getUserRole, hasRole, isAdmin, isInstructor } from '../roles'

describe('role helpers', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('falls back to student for malformed or missing user state', () => {
    expect(getUserRole()).toBe('student')
    localStorage.setItem('user', '{not-json')
    expect(getUserRole()).toBe('student')
  })

  it('enforces the student < instructor < admin hierarchy', () => {
    localStorage.setItem('user', JSON.stringify({ role: 'instructor' }))
    expect(hasRole('student')).toBe(true)
    expect(hasRole('instructor')).toBe(true)
    expect(hasRole('admin')).toBe(false)
    expect(isInstructor()).toBe(true)
    expect(isAdmin()).toBe(false)
  })
})
