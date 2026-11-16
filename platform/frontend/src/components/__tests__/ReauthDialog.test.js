import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { post } = vi.hoisted(() => ({
  post: vi.fn().mockResolvedValue({ data: { reauth: true } }),
}))
vi.mock('../../api/axios', () => ({ default: { post } }))

import ReauthDialog from '../ReauthDialog.vue'

describe('ReauthDialog', () => {
  beforeEach(() => {
    post.mockClear()
    localStorage.clear()
  })

  it('opens on the reauth event and submits the password', async () => {
    localStorage.setItem('user', JSON.stringify({ mfa_enabled: false }))
    const wrapper = mount(ReauthDialog)
    window.dispatchEvent(
      new CustomEvent('ocr:reauth-required', { detail: { purpose: 'account export' } })
    )
    await flushPromises()
    expect(wrapper.text()).toContain('account export')

    const inputs = wrapper.findAll('input')
    expect(inputs.length).toBeGreaterThan(0)
    await inputs[0].setValue('correct horse battery staple')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(post).toHaveBeenCalledWith('/api/auth/reauth', {
      password: 'correct horse battery staple', // security-delta: allow credential-like assignment
      totp_code: null,
    })
  })
})
