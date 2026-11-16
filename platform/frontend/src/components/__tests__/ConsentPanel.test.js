import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { get, post } = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))
vi.mock('../../api/axios', () => ({ default: { get, post } }))

import ConsentPanel from '../ConsentPanel.vue'

describe('ConsentPanel', () => {
  beforeEach(() => {
    get.mockReset()
    get.mockResolvedValue({
      data: {
        consents: {
          cyber_dna: {
            consent_type: 'cyber_dna',
            label: 'Cyber DNA',
            description: 'Derived competency evidence.',
            granted: true,
            version: 2,
          },
        },
        revocations: [],
        history: [],
        remaining_records: {},
      },
    })
  })

  it('renders the learner consent state from the API', async () => {
    const wrapper = mount(ConsentPanel)
    await flushPromises()
    expect(get).toHaveBeenCalledWith('/consent/')
    expect(wrapper.text()).toContain('Cyber DNA')
    expect(wrapper.text()).toContain('Processing is on')
  })
})
