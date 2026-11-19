import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../api/axios', () => ({ default: { get } }))

import InstructorReadinessPanel from '../InstructorReadinessPanel.vue'

const readiness = {
  formula_version: 'cwrs-pilot-2026.1',
  provisional: true,
  note: 'Pilot readiness view.',
  cohort: {
    students: 1,
    assigned_exercises: 3,
    median_completed: 1,
    band_counts: {
      critical_intervention: 0,
      high_risk: 1,
      elevated: 0,
      monitor: 0,
      healthy: 0,
    },
  },
  students: [
    {
      user_id: 4,
      username: 'avery',
      display_name: 'Avery One',
      cwrs: 76,
      band: 'high_risk',
      band_label: 'High risk',
      confidence: 'high',
      components: {
        performance: 80,
        engagement: 90,
        progression: 70,
        competency: 60,
        behavioural: 40,
        infrastructure: 0,
      },
      flags: ['engagement', 'inactive'],
      started_exercises: 3,
      completed_exercises: 1,
      assigned_exercises: 3,
      last_activity: '2026-11-18T08:00:00Z',
      days_since_activity: 12,
      provisional: true,
    },
  ],
  lab_health: {
    counts: { degraded: 1, warning: 0, no_data: 0, healthy: 1 },
    labs: [
      {
        lab_id: 2,
        name: 'OAuth Attack',
        slug: 'oauth-attack',
        track: 'Cloud',
        level: 'Level 1',
        difficulty: 'intermediate',
        started: 10,
        completed: 4,
        success_rate: 40,
        abandonment_rate: 60,
        median_hints: 3,
        median_minutes: 70,
        sample_size: 10,
        status: 'degraded',
      },
      {
        lab_id: 3,
        name: 'Sentinel Intro',
        slug: 'sentinel-intro',
        track: 'Detection',
        level: 'Level 1',
        difficulty: 'beginner',
        started: 10,
        completed: 10,
        success_rate: 100,
        abandonment_rate: 0,
        median_hints: 0,
        median_minutes: 30,
        sample_size: 10,
        status: 'healthy',
      },
    ],
  },
  generated_at: '2026-11-19T00:00:00Z',
}

describe('InstructorReadinessPanel', () => {
  beforeEach(() => {
    get.mockReset()
    get.mockImplementation((url) => {
      if (url.endsWith('/readiness')) return Promise.resolve({ data: readiness })
      if (url.includes('/capabilities')) {
        return Promise.resolve({
          data: {
            axes: [
              { key: 'network_systems', label: 'Network systems', score: 72, evidence_count: 5 },
            ],
            disclaimer: 'A low score with no evidence is unmeasured.',
          },
        })
      }
      return Promise.reject(new Error(`unexpected ${url}`))
    })
  })

  it('shows the support queue and expands capability detail', async () => {
    const wrapper = mount(InstructorReadinessPanel, {
      props: {
        courseId: 7,
        courses: [{ id: 7, code: 'CYB101', name: 'Cyber Foundations' }],
      },
    })
    await flushPromises()

    expect(get).toHaveBeenCalledWith('/analytics/courses/7/readiness')
    expect(wrapper.text()).toContain('Readiness and lab health')
    expect(wrapper.text()).toContain('Avery One')
    expect(wrapper.text()).toContain('High risk')

    await wrapper.get('.readiness-card__summary').trigger('click')
    await flushPromises()

    expect(get).toHaveBeenCalledWith('/analytics/courses/7/students/4/capabilities')
    expect(wrapper.text()).toContain('Capability detail')
    expect(wrapper.text()).toContain('Network systems')
  })

  it('shows only unhealthy labs by default', async () => {
    const wrapper = mount(InstructorReadinessPanel, {
      props: {
        courseId: 7,
        courses: [{ id: 7, code: 'CYB101', name: 'Cyber Foundations' }],
      },
    })
    await flushPromises()

    const buttons = wrapper.findAll('.readiness-panel__tab')
    await buttons[1].trigger('click')

    expect(wrapper.text()).toContain('OAuth Attack')
    expect(wrapper.text()).not.toContain('Sentinel Intro')
    expect(wrapper.text()).toContain('Show healthy labs')
  })
})
