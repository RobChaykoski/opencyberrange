import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const get = vi.fn()

vi.mock('../../api/axios', () => ({
  default: { get: (...args) => get(...args) },
}))

import ThreatAwareness from '../ThreatAwareness.vue'

const snapshot = {
  schema_version: 1,
  mode: 'sample',
  sample: true,
  generated_at: '2026-11-24T00:00:00Z',
  window_hours: 24,
  source: {
    name: 'FireHOL threat intelligence feeds',
    url: 'https://iplists.firehol.org/',
    attribution: 'Aggregated counts derived from the FireHOL iplists project.',
  },
  method: {
    aggregation: 'country',
    minimum_bucket_size: 25,
    individual_addresses: false,
    geoip: 'local-database',
    attack_paths: 'not included',
  },
  totals: {
    entries_observed: 200,
    entries_reported: 180,
    coverage: 0.9,
    categories: 2,
    countries: 2,
    category_entries: 180,
    country_entries: 180,
    buckets_suppressed: 2,
  },
  categories: [
    { id: 'level1', label: 'High risk', count: 100, share: 0.5556 },
    { id: 'level2', label: 'Moderate risk', count: 80, share: 0.4444 },
  ],
  countries: [
    { code: 'US', label: 'United States', count: 120, share: 0.6667 },
    { code: 'DE', label: 'Germany', count: 60, share: 0.3333 },
  ],
  notes: ['Aggregated per country.'],
}

describe('ThreatAwareness', () => {
  beforeEach(() => {
    get.mockReset()
  })

  it('labels a sample snapshot and renders aggregated rows', async () => {
    get.mockResolvedValue({ data: snapshot })
    const wrapper = mount(ThreatAwareness)
    await flushPromises()

    expect(get).toHaveBeenCalledWith('/threat-awareness')
    expect(wrapper.text()).toContain('Sample snapshot')
    expect(wrapper.text()).toContain('High risk')
    expect(wrapper.text()).toContain('United States')
    expect(wrapper.text()).toContain('US')
    expect(wrapper.text()).toContain('90%')
    expect(wrapper.text()).not.toMatch(/\b\d{1,3}(?:\.\d{1,3}){3}\b/)
  })

  it('shows the API error message', async () => {
    get.mockRejectedValue({
      response: { data: { detail: 'snapshot is not installed' } },
    })
    const wrapper = mount(ThreatAwareness)
    await flushPromises()

    expect(wrapper.text()).toContain('snapshot is not installed')
  })
})
