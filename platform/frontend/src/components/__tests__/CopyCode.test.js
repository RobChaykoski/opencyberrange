import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import CopyCode from '../CopyCode.vue'

describe('CopyCode', () => {
  it('is a labelled button, not clickable-looking text', () => {
    const wrapper = mount(CopyCode, {
      props: { value: 'ABC-123', label: 'invite code' },
    })
    const button = wrapper.get('button')
    expect(button.attributes('type')).toBe('button')
    expect(button.attributes('aria-label')).toBe('Copy invite code')
    expect(button.text()).toContain('ABC-123')
  })

  it('writes to the clipboard and confirms inline', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    vi.stubGlobal('navigator', { clipboard: { writeText } })

    const wrapper = mount(CopyCode, {
      props: { value: 'ABC-123', label: 'invite code' },
    })
    await wrapper.get('button').trigger('click')
    await Promise.resolve()

    expect(writeText).toHaveBeenCalledWith('ABC-123')
    expect(wrapper.get('button').attributes('aria-label')).toBe('invite code copied')
    expect(wrapper.text()).toContain('Copied')
    vi.unstubAllGlobals()
  })
})
