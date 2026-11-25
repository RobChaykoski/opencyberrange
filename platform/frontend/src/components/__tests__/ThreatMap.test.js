import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ThreatMap from '../ThreatMap.vue'

const countries = [
  { code: 'US', label: 'United States', count: 100, share: 0.5 },
  { code: 'DE', label: 'Germany', count: 60, share: 0.3 },
  { code: 'JP', label: 'Japan', count: 30, share: 0.15 },
  { code: 'FR', label: 'France', count: 10, share: 0.05 },
]

function mountMap(overrides = {}) {
  return mount(ThreatMap, {
    props: {
      countries,
      entriesReported: 200,
      generatedAt: '2026-11-24T22:12:13Z',
      windowHours: 24,
      ...overrides,
    },
  })
}

describe('ThreatMap', () => {
  it('renders one marker per country and keeps the snapshot boundary visible', () => {
    const wrapper = mountMap()
    expect(wrapper.findAll('.threat-map__dot')).toHaveLength(4)
    expect(wrapper.text()).toContain('not live')
    expect(wrapper.text()).toContain('a country is where an address is registered')
    expect(wrapper.text()).toContain('No answer, score, or identity is sent')
  })

  it('selects a country from the hotspot list and shows the aggregate detail', async () => {
    const wrapper = mountMap()
    const germany = wrapper.findAll('.threat-map__row')
      .find((row) => row.text().includes('Germany'))
    await germany.trigger('click')
    expect(wrapper.find('.threat-map__detail').text()).toContain('Germany')
    expect(wrapper.find('.threat-map__detail').text()).toContain('60')
    expect(wrapper.find('.threat-map__detail').text()).toContain('rank 2 of 4')
    const osm = wrapper.find('.threat-map__external')
    expect(osm.exists()).toBe(true)
    expect(osm.attributes('href')).toContain('openstreetmap.org')
    expect(osm.attributes('href')).toContain('51.10')
  })

  it('filters by region without changing the underlying snapshot', async () => {
    const wrapper = mountMap()
    const europe = wrapper.findAll('.threat-map__chip')
      .find((chip) => chip.text() === 'Europe')
    await europe.trigger('click')
    expect(wrapper.text()).toMatch(/Showing 2 of 4 countries\s+in Europe/)
    expect(wrapper.findAll('.threat-map__dot')).toHaveLength(2)
  })

  it('explains an empty filter instead of showing a blank map', async () => {
    const wrapper = mountMap()
    const select = wrapper.find('.threat-map__threshold select')
    await select.setValue(1000)
    expect(wrapper.find('.threat-map__empty').exists()).toBe(true)
    expect(wrapper.text()).toContain('No countries match these filters')
  })
})
