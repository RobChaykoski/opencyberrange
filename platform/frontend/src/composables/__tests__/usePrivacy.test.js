import { beforeEach, describe, expect, it, vi } from 'vitest'

async function freshPrivacy() {
  vi.resetModules()
  const module = await import('../usePrivacy')
  return module.usePrivacy()
}

describe('privacy helpers', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('masks usernames and emails when privacy mode is on', async () => {
    localStorage.setItem('user', JSON.stringify({ role: 'admin' }))
    localStorage.setItem('privacy-mode', 'on')
    localStorage.setItem('privacy-mode-explicit', '1')
    const { privacyMode, maskUsername, maskEmail } = await freshPrivacy()
    expect(privacyMode.value).toBe(true)
    expect(maskUsername('student')).toBe('s\u2022\u2022\u2022\u2022\u2022t')
    expect(maskEmail('learner@example.edu')).toContain('@e')
  })

  it('persists an explicit toggle choice', async () => {
    localStorage.setItem('user', JSON.stringify({ role: 'admin' }))
    const { privacyMode, togglePrivacy } = await freshPrivacy()
    const initial = privacyMode.value
    togglePrivacy()
    expect(privacyMode.value).toBe(!initial)
    expect(localStorage.getItem('privacy-mode')).toBe(
      privacyMode.value ? 'on' : 'off'
    )
    expect(localStorage.getItem('privacy-mode-explicit')).toBe('1')
  })
})
