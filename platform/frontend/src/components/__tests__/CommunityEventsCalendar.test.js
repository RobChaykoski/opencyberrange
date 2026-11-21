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

  it('shows the destination host and never renders an unsafe link', () => {
    const start = inDays(7)
    const wrapper = mount(CommunityEventsCalendar, {
      props: {
        communityEvents: [
          {
            id: 'safe-1',
            title: 'Cyber Hive YXU',
            start,
            end: start,
            location: 'London, ON',
            description: 'Monthly meetup.',
            url: 'https://www.eventbrite.ca/e/cyber-hive-tickets-1',
            source: 'Cyber Hive YXU',
          },
          {
            id: 'unsafe-1',
            title: 'Unsafe link',
            start,
            end: start,
            location: 'London, ON',
            description: 'This link must not become an anchor.',
            url: 'javascript:alert(1)',
            source: 'Community',
          },
        ],
        sources: [
          {
            key: 'cyber-hive',
            name: 'Cyber Hive YXU',
            description: 'London meetups',
            location: 'London, ON',
            url: 'https://www.eventbrite.ca/o/cyber-hive-yxu-113603781581',
          },
        ],
      },
      global: {
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })

    expect(wrapper.text()).toContain('eventbrite.ca')
    expect(wrapper.find('a[href="javascript:alert(1)"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('External link unavailable')
  })
})
