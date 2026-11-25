import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ThreatMapQuiz from '../ThreatMapQuiz.vue'

const countries = [
  { code: 'US', label: 'United States', count: 100, share: 0.5, region: 'Americas' },
  { code: 'DE', label: 'Germany', count: 60, share: 0.3, region: 'Europe' },
  { code: 'JP', label: 'Japan', count: 30, share: 0.15, region: 'Asia' },
  { code: 'FR', label: 'France', count: 10, share: 0.05, region: 'Europe' },
]
const regions = [
  { id: 'Americas', label: 'Americas', count: 100, share: 0.5 },
  { id: 'Europe', label: 'Europe', count: 70, share: 0.35 },
  { id: 'Asia', label: 'Asia', count: 30, share: 0.15 },
]

function mountQuiz() {
  return mount(ThreatMapQuiz, {
    props: { countries, entriesReported: 200, regions },
  })
}

describe('ThreatMapQuiz', () => {
  it('asks a comparison question, reveals the answer, and moves on', async () => {
    const wrapper = mountQuiz()
    expect(wrapper.text()).toContain('Question 1 of 3')
    expect(wrapper.text()).toContain('Which of these countries has the most reported hostile addresses?')

    const correct = wrapper.findAll('.map-quiz__option')
      .find((option) => option.text().includes('United States (US)'))
    expect(correct).toBeTruthy()
    await correct.trigger('click')
    expect(wrapper.text()).toContain('Correct.')
    expect(wrapper.text()).toContain('100 entries')

    const next = wrapper.findAll('button').find((button) => button.text() === 'Next question')
    await next.trigger('click')
    expect(wrapper.text()).toContain('Question 2 of 3')
    expect(wrapper.text()).toContain('About what share of reported entries comes from United States?')
  })

  it('finishes the round and offers a replay without recording anything', async () => {
    const wrapper = mountQuiz()

    for (let index = 0; index < 3; index += 1) {
      const option = wrapper.findAll('.map-quiz__option')[0]
      if (option) await option.trigger('click')
      const next = wrapper.findAll('button')
        .find((button) => ['Next question', 'See result'].includes(button.text()))
      if (next) await next.trigger('click')
    }

    expect(wrapper.text()).toContain('Complete')
    expect(wrapper.text()).toContain('No answer, score, or identity is sent')
    const replay = wrapper.findAll('button').find((button) => button.text() === 'Play again')
    expect(replay).toBeTruthy()
  })
})
