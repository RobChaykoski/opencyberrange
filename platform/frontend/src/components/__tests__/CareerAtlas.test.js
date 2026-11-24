import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import CareerAtlas from '../CareerAtlas.vue'

describe('CareerAtlas score display', () => {
  it('shows an unmeasured state instead of zero when there is no DNA evidence', () => {
    const wrapper = mount(CareerAtlas, {
      props: {
        dna: { class: { class_name: 'Recruit' }, overall: null, tier: 'Unranked' },
        atlas: { summary: { unlocked: 0 }, families: [], regions: [] },
      },
    })
    expect(wrapper.text()).toContain('No practice evidence yet')
    expect(wrapper.text()).not.toContain('0/99')
  })

  it('shows the score when evidence exists', () => {
    const wrapper = mount(CareerAtlas, {
      props: {
        dna: { class: { class_name: 'Recruit' }, overall: 42, tier: 'Practitioner' },
        atlas: { summary: { unlocked: 0 }, families: [], regions: [] },
      },
    })
    expect(wrapper.text()).toContain('42/99')
    expect(wrapper.text()).not.toContain('No practice evidence yet')
  })
})
