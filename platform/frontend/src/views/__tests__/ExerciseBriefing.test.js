import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'

const { get, route } = vi.hoisted(() => ({
  get: vi.fn(),
  route: {
    params: { trackSlug: 'network-defence' },
    query: { labId: '12', courseId: '3', wikiSlug: 'net-101' },
  },
}))

vi.mock('../../api/axios', () => ({
  default: { get: (...args) => get(...args) },
}))

vi.mock('vue-router', () => ({
  useRoute: () => route,
}))

import ExerciseBriefing from '../ExerciseBriefing.vue'
import { setWikiBaseUrl } from '../../utils/wikiUrl'

function labResponse(overrides = {}) {
  return {
    lab: {
      id: 12,
      name: 'Suspicious Login',
      scenario: 'Review the alert on <target>.',
      objectives: ['Explain the detection'],
      hints_total: 1,
      requested_hints: [{ number: 1, text: 'Start with the auth log.' }],
      workbook: 'guide.md',
      ...overrides,
    },
    track: { name: 'Network Defence', slug: 'network-defence' },
    level: { number: 2, name: 'Detection' },
    hostnames: [{ hostname: 'files.lab', description: 'File server', ip: '10.1.2.5' }],
    target_ips: [],
  }
}

const RouterLinkStub = {
  props: ['to'],
  template: '<a class="router-link-stub"><slot /></a>',
}

describe('ExerciseBriefing pop-out', () => {
  beforeEach(() => {
    setWikiBaseUrl('')
  })

  it('fetches the active lab and renders the same read-only brief', async () => {
    get.mockResolvedValueOnce({ data: labResponse() })

    const wrapper = mount(ExerciseBriefing, {
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    expect(get).toHaveBeenCalledWith('/exercises/labs/12', {
      params: { course_id: 3 },
    })
    expect(wrapper.text()).toContain('Suspicious Login')
    expect(wrapper.text()).toContain('Review the alert on <target>.')
    expect(wrapper.text()).toContain('files.lab')
    expect(wrapper.text()).toContain('auth log')
    expect(wrapper.text()).not.toContain('Pop out briefing')
    expect(wrapper.get('.exercise-brief__workbook-link').attributes('href')).toContain(
      '/wiki/course/net-101/guide.md'
    )

    // App.vue loads the wiki origin asynchronously. The workbook link must
    // follow that change instead of freezing the first relative URL.
    setWikiBaseUrl('https://wiki.example.test')
    await nextTick()
    expect(wrapper.get('.exercise-brief__workbook-link').attributes('href')).toBe(
      'https://wiki.example.test/wiki/course/net-101/guide.md'
    )
  })

  it('shows a readable message when the lab cannot be loaded', async () => {
    get.mockRejectedValueOnce(new Error('forbidden'))

    const wrapper = mount(ExerciseBriefing, {
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Briefing unavailable')
    expect(wrapper.text()).not.toContain('forbidden')
  })
})
