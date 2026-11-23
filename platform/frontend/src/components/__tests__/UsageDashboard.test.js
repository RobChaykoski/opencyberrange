import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../api/axios', () => ({ default: { get } }))

import UsageDashboard from '../UsageDashboard.vue'

function payload(overrides = {}) {
  return {
    generated_at: '2026-11-23T00:00:00Z',
    window_days: 30,
    since: '2026-10-25T00:00:00Z',
    public: true,
    minimum_cohort_size: 5,
    totals: {
      registrations: { value: 42, previous: 30, delta_pct: 40 },
      qr_scans: { value: 80, previous: 100, delta_pct: -20 },
      completions: { value: 120, previous: 100, delta_pct: 20 },
      active_learners: { value: 25, previous: 20, delta_pct: 25 },
    },
    week: {
      since: '2026-11-16T00:00:00Z',
      registrations: { current: 10, previous: 8, delta_pct: 25 },
      qr_scans: { current: 20, previous: 25, delta_pct: -20 },
      completions: { current: 30, previous: 30, delta_pct: 0 },
      active_learners: { current: 12, previous: 10, delta_pct: 20 },
    },
    daily: [
      { date: '2026-11-21', registrations: 2, qr_scans: 3, completions: 5 },
      { date: '2026-11-22', registrations: 1, qr_scans: 4, completions: 6 },
    ],
    sources: [
      {
        key: 'gdg',
        label: 'GDG',
        registrations: null,
        registrations_suppressed: true,
        scans: 10,
        completions: 5,
        share: null,
      },
      {
        key: 'direct',
        label: 'Direct',
        registrations: 20,
        registrations_suppressed: false,
        scans: 0,
        completions: 12,
        share: 0.476,
      },
    ],
    campaigns: [
      {
        campaign: 'gdg-november-2026',
        scans: 10,
        registrations: null,
        registrations_suppressed: true,
        conversion: null,
      },
    ],
    labs: {
      total: 1,
      returned: 1,
      items: [
        {
          slug: 'network-0-1-ping-basics',
          name: 'Ping Basics',
          category: 'network',
          difficulty: 'beginner',
          completions: 9,
          learners: null,
          learners_suppressed: true,
          attempts_avg: 1.2,
          hints_avg: 0.2,
          median_minutes: 18,
          first_attempt_rate: 0.8,
          completion_rate: 0.75,
          last_completed_at: '2026-11-22T10:00:00Z',
        },
      ],
    },
    movers: {
      sources: [{ key: 'gdg', label: 'GDG', current: 5, previous: 2, delta_pct: 150 }],
      labs: [{ name: 'Ping Basics', current: 5, previous: 2, delta_pct: 150 }],
    },
    recent: [
      { kind: 'registration', label: 'New GDG registration', at: '2026-11-22T10:00:00Z' },
      { kind: 'completion', label: 'Completed Ping Basics', at: '2026-11-22T11:00:00Z' },
    ],
    ...overrides,
  }
}

function mountDashboard(props = {}) {
  return mount(UsageDashboard, {
    props,
    global: {
      stubs: {
        RouterLink: { template: '<a><slot /></a>' },
        EChart: { template: '<div class="echart-stub" />' },
      },
    },
  })
}

describe('UsageDashboard', () => {
  beforeEach(() => {
    get.mockReset()
    Object.defineProperty(URL, 'createObjectURL', {
      value: vi.fn(() => 'blob:qr'),
      configurable: true,
    })
    Object.defineProperty(URL, 'revokeObjectURL', {
      value: vi.fn(),
      configurable: true,
    })
  })

  it('renders the public tracker with aggregate-only counts', async () => {
    get.mockResolvedValue({ data: payload() })
    const wrapper = mountDashboard()
    await flushPromises()

    expect(get).toHaveBeenCalledWith('/usage/public', { params: { days: 30 } })
    expect(wrapper.text()).toContain('Usage, in the open')
    expect(wrapper.text()).toContain('120')
    expect(wrapper.text()).toContain('GDG')
    expect(wrapper.text()).toContain('Ping Basics')
    expect(wrapper.text()).toContain('<5')
    expect(wrapper.text()).toContain('Latest activity')
    expect(wrapper.text()).not.toContain('Conference QR')
    expect(wrapper.find('.echart-stub').exists()).toBe(true)
  })

  it('renders admin detail and the QR generator', async () => {
    get.mockImplementation((path) => {
      if (path === '/usage/admin/qr') {
        return Promise.resolve({ data: new Blob(['png']) })
      }
      return Promise.resolve({ data: payload({ public: false }) })
    })
    const wrapper = mountDashboard({ admin: true })
    await flushPromises()

    expect(get).toHaveBeenCalledWith('/usage/admin', { params: { days: 30 } })
    expect(wrapper.text()).toContain('Admin usage detail')
    expect(wrapper.text()).toContain('Conference QR')
    expect(wrapper.find('img[alt="Registration QR code"]').exists()).toBe(true)
  })
})
