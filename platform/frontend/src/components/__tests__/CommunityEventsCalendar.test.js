import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import CommunityEventsCalendar from '../CommunityEventsCalendar.vue'

const inDays = (days) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  date.setHours(10, 0, 0, 0)
  return date.toISOString()
}

describe('CommunityEventsCalendar', () => {
  it('renders live community events and the feed status', () => {
    const start = inDays(7)
    const wrapper = mount(CommunityEventsCalendar, {
      props: {
        communityEvents: [
          {
            id: 'live-1',
            title: 'CyberRunners London',
            start,
            end: start,
            location: 'Harris Park, London',
            description: 'Weekly run and security chat.',
            url: 'https://www.swocts.com/calendar',
            source: 'SWOCTS Hub',
            free: true,
          },
        ],
        sources: [],
        status: 'Live from the SWOCTS Hub calendar.',
      },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })

    expect(wrapper.text()).toContain('CyberRunners London')
    expect(wrapper.text()).toContain('Live from the SWOCTS Hub calendar.')
    expect(wrapper.text()).toContain('SWOCTS Hub')
  })
})
