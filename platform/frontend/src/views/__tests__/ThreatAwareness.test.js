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

const ransomware = {
  schema_version: 1,
  mode: 'sample',
  sample: true,
  generated_at: '2026-11-24T00:00:00Z',
  window_days: 7,
  source: {
    name: 'RansomLook',
    url: 'https://www.ransomlook.io/',
    licence: 'CC BY 4.0',
    attribution: 'Aggregated counts derived from RansomLook.',
  },
  method: {
    aggregation: 'group',
    victim_details: false,
    links: false,
    crypto_addresses: false,
  },
  totals: {
    posts_24h: 40,
    posts_month: 300,
    posts_90d: 900,
    posts_year: 3000,
    posts_total: 10000,
    groups: 654,
    groups_online: 727,
    markets: 161,
    window_posts: 200,
  },
  groups: [
    { name: 'alpha', count: 120, share: 0.6 },
    { name: 'beta', count: 50, share: 0.25 },
  ],
  notes: ['Aggregated per group.'],
}

const ok = (payload) => Promise.resolve({ data: payload })
const fail = (detail) =>
  Promise.reject({ response: { data: { detail } } })

function mockBoth() {
  get.mockImplementation((url) => {
    if (url === '/threat-awareness') return ok(snapshot)
    if (url === '/ransomware-activity') return ok(ransomware)
    return fail('unexpected endpoint')
  })
}

describe('ThreatAwareness', () => {
  beforeEach(() => {
    get.mockReset()
  })

  it('labels sample snapshots and renders both aggregated sections', async () => {
    mockBoth()
    const wrapper = mount(ThreatAwareness)
    await flushPromises()

    expect(get).toHaveBeenCalledWith('/threat-awareness')
    expect(get).toHaveBeenCalledWith('/ransomware-activity')
    expect(wrapper.text()).toContain('Sample snapshot')
    expect(wrapper.text()).toContain('High risk')
    expect(wrapper.text()).toContain('United States')
    expect(wrapper.text()).toContain('Ransomware activity')
    expect(wrapper.text()).toContain('alpha')
    expect(wrapper.text()).toContain('CC BY 4.0')
    expect(wrapper.text()).toContain('90%')
    expect(wrapper.text()).not.toMatch(/\b\d{1,3}(?:\.\d{1,3}){3}\b/)
    expect(wrapper.text()).not.toMatch(/post_title|magnet:/i)
  })

  it('keeps the threat section when ransomware data fails', async () => {
    get.mockImplementation((url) => {
      if (url === '/threat-awareness') return ok(snapshot)
      return fail('ransomware snapshot is not installed')
    })
    const wrapper = mount(ThreatAwareness)
    await flushPromises()

    expect(wrapper.text()).toContain('United States')
    expect(wrapper.text()).toContain('ransomware snapshot is not installed')
  })

  it('shows the threat API error message', async () => {
    get.mockImplementation(() => fail('snapshot is not installed'))
    const wrapper = mount(ThreatAwareness)
    await flushPromises()

    expect(wrapper.text()).toContain('snapshot is not installed')
  })
})
