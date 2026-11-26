import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import HaStatusCard from '../HaStatusCard.vue'

function status(overrides = {}) {
  return {
    available: true,
    checked_at: '2026-11-26T17:02:49Z',
    age_seconds: 12,
    stale: false,
    role: 'standby',
    preferred: 'prod',
    replication: { state: 'streaming', lag_bytes: 0, last_replay: '0/1' },
    redis: { master: 'up', sentinels: '2/2' },
    witness: { last_contact: '2026-11-26T17:02:40Z', prod: 'up', dev: 'up' },
    last_failover: null,
    verdict: 'ok',
    detail: 'HA status is current.',
    ...overrides,
  }
}

describe('HaStatusCard', () => {
  it('is hidden when HA is not configured', () => {
    const wrapper = mount(HaStatusCard, {
      props: { status: status({ available: false }) },
    })

    expect(wrapper.find('.ha-card').exists()).toBe(false)
  })

  it('renders the healthy standby view', () => {
    const wrapper = mount(HaStatusCard, { props: { status: status() } })

    expect(wrapper.text()).toContain('High availability')
    expect(wrapper.text()).toContain('HA checks are current')
    expect(wrapper.text()).toContain('Standby')
    expect(wrapper.text()).toContain('Production')
    expect(wrapper.text()).toContain('Streaming · lag 0 B')
    expect(wrapper.text()).toContain('master up · 2/2 sentinels')
    expect(wrapper.text()).toContain('Both up')
    expect(wrapper.text()).toContain('Observed 2026-11-26T17:02:49Z')
    expect(wrapper.find('.ha-card--ok').exists()).toBe(true)
  })

  it('shows a stale snapshot as unknown', () => {
    const wrapper = mount(HaStatusCard, {
      props: {
        status: status({
          verdict: 'unknown',
          stale: true,
          age_seconds: 600,
          detail: 'HA status is stale; the last snapshot is too old to trust.',
        }),
      },
    })

    expect(wrapper.text()).toContain('HA status is unknown')
    expect(wrapper.text()).toContain('600 s ago')
    expect(wrapper.find('.ha-card--unknown').exists()).toBe(true)
  })

  it('shows a replication error as action needed', () => {
    const wrapper = mount(HaStatusCard, {
      props: {
        status: status({
          verdict: 'error',
          replication: { state: 'stopped', lag_bytes: 0, last_replay: null },
          detail: 'The standby is not receiving WAL; failover would lose data.',
        }),
      },
    })

    expect(wrapper.text()).toContain('Action needed')
    expect(wrapper.text()).toContain('stopped')
    expect(wrapper.find('.ha-card--error').exists()).toBe(true)
  })

  it('formats replication lag and warning state', () => {
    const wrapper = mount(HaStatusCard, {
      props: {
        status: status({
          verdict: 'warning',
          replication: {
            state: 'streaming',
            lag_bytes: 65 * 1024 * 1024,
            last_replay: '0/1',
          },
        }),
      },
    })

    expect(wrapper.text()).toContain('lag 65 MB')
    expect(wrapper.text()).toContain('Some HA checks need attention')
    expect(wrapper.find('.ha-card--warning').exists()).toBe(true)
  })

  it('shows an unverified failover and emits refresh', async () => {
    const wrapper = mount(HaStatusCard, {
      props: {
        status: status({
          verdict: 'warning',
          last_failover: {
            at: '2026-11-26T17:00:00Z',
            from: 'prod',
            to: 'dev',
            verified: false,
          },
        }),
      },
    })

    expect(wrapper.text()).toContain('prod → dev · not verified')

    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('refresh')).toHaveLength(1)
  })

  it('has no promotion or failover action', () => {
    const wrapper = mount(HaStatusCard, { props: { status: status() } })
    const buttonLabels = wrapper.findAll('button').map((button) => button.text())

    expect(buttonLabels).toEqual(['Refresh'])
    expect(wrapper.text().toLowerCase()).not.toContain('promote')
  })
})
