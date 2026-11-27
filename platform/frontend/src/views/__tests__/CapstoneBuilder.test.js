import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { get, post, put } = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
}))
vi.mock('../../api/axios', () => ({ default: { get, post, put } }))

import CapstoneBuilder from '../CapstoneBuilder.vue'

const profiles = [
  {
    id: 'soc-analyst',
    title: 'SOC Analyst',
    summary: 'Triage alerts and escalate with a clear record.',
    critical_competency_count: 29,
    tracks: ['network'],
    capstone: { title: 'Ransomware Investigation', description: 'Investigate an incident end to end.' },
    career_ready_threshold: null,
  },
  {
    id: 'ai-security-analyst',
    title: 'AI Security Analyst',
    summary: 'Assess AI systems.',
    critical_competency_count: 16,
    tracks: ['ai'],
    capstone: { title: 'Secure AI Application Assessment', description: 'Review an AI feature.' },
    career_ready_threshold: null,
  },
]

const proposal = {
  profile: profiles[0],
  request: { duration_hours: 12, max_labs: 9 },
  objectives: [
    {
      number: 1,
      statement: 'Given the evidence, reconstruct the timeline.',
      competencies: [{ id: 'FOR-005', name: 'Timeline Analysis' }],
      evidence_types: ['artifact'],
    },
  ],
  labs: [
    {
      order: 1,
      slug: 'network-0-2-dns-basics',
      title: 'DNS Records',
      track: 'Network',
      difficulty: 'beginner',
      hours: 0.4,
      reviewed: true,
      competencies: ['NET-011'],
      prerequisites: [],
    },
  ],
  assessments: [
    {
      type: 'formative',
      title: 'Evidence table',
      weight: 0.3,
      rubric: 'analyst-answer',
      evidence_type: 'analyst_answer',
      description: 'Source, time, hash, and relevance.',
    },
  ],
  deliverables: [
    { number: 1, title: 'Incident timeline', evidence_type: 'artifact', reviewer: 'Instructor', description: 'Reviewed artifact.' },
  ],
  evidence_map: [{ competency_id: 'FOR-005', name: 'Timeline Analysis', labs: ['network-0-2-dns-basics'], evidence_types: ['artifact'] }],
  validation: {
    coverage_percent: 48.3,
    target_coverage_percent: 90,
    coverage_pass: false,
    workload_hours: 11.2,
    target_hours: 12,
    variance_percent: -6.7,
    workload_pass: true,
    workload_note: 'Selected lab time is within the workload tolerance.',
    recommended_duration_hours: 14,
    waived_competencies: [],
    waiver_reason: null,
    waiver_valid: true,
    assessment_weights_total: 1,
    weights_pass: true,
    prerequisites_satisfied: true,
    assume_entry_level: true,
    prerequisite_gaps: [],
    prerequisite_assumed: true,
    publishable: false,
    gaps: [{ competency_id: 'SOC-002', name: 'Case Management', alternatives: ['soc-1-1-case-triage'] }],
  },
  notes: ['This is a proposal. An instructor edits and approves it.'],
}

function mockLoads() {
  get.mockImplementation((url) => {
    if (url === '/capstones/profiles') return Promise.resolve({ data: { profiles } })
    if (url === '/capstones/plans') return Promise.resolve({ data: { plans: [] } })
    return Promise.resolve({ data: {} })
  })
}

describe('CapstoneBuilder', () => {
  beforeEach(() => {
    get.mockReset()
    post.mockReset()
    put.mockReset()
    mockLoads()
  })

  it('loads profiles and explains the empty state', async () => {
    const wrapper = mount(CapstoneBuilder)
    await flushPromises()

    expect(wrapper.find('h1').text()).toBe('Capstone Builder')
    expect(wrapper.findAll('select option')).toHaveLength(3)
    expect(wrapper.text()).toContain('Choose a profile and generate a proposal')
  })

  it('generates a proposal and shows the validation gate', async () => {
    post.mockResolvedValueOnce({ data: proposal })
    const wrapper = mount(CapstoneBuilder)
    await flushPromises()

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(post).toHaveBeenCalledWith('/capstones/plan', expect.objectContaining({ profile_id: 'soc-analyst' }))
    expect(wrapper.text()).toContain('Needs review')
    expect(wrapper.text()).toContain('48.3%')
    expect(wrapper.text()).toContain('Uncovered critical competencies')
    expect(wrapper.text()).toContain('SOC-002')
  })

  it('keeps approval unavailable until a plan is saved and publishable', async () => {
    post.mockResolvedValueOnce({ data: proposal })
    const wrapper = mount(CapstoneBuilder)
    await flushPromises()

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const approve = wrapper.findAll('button').find((button) => button.text() === 'Approve plan')
    expect(approve).toBeUndefined()
  })
})
