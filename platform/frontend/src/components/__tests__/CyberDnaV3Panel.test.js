import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../api/axios', () => ({ default: { get } }))

import CyberDnaV3Panel from '../CyberDnaV3Panel.vue'

function payload(overrides = {}) {
  const base = {
    version: '2026.1',
    schema_version: '2026.1',
    generated_at: '2026-11-22T00:00:00Z',
    evidence_summary: { competencies_with_evidence: 91, evidence_items: 381 },
    competencies: [
      {
        competency_id: 'TH-003',
        competency_name: 'Investigative Queries',
        domain_id: 'TH',
        domain_label: 'Threat Hunting',
        category_id: 'TH-HUNT',
        category_label: 'Hunting',
        score: 47,
        band: 'practitioner',
        evidence_count: 12,
        last_practised_at: '2026-10-29T06:49:50Z',
        formula_version: 'evidence-2026.1',
      },
    ],
    behavior: {
      version: 'behavior-2026.1',
      window_days: 30,
      signals: {
        independence: { value: 77.3, sample_size: 3, confidence: 'low' },
        investigation: {
          value: 22.2,
          sample_size: 3,
          confidence: 'low',
          kind: 'proxy',
          note: 'Exploration breadth, not telemetry.',
        },
      },
      weights: { note: 'Investigation is an exploration proxy, not telemetry.' },
    },
    interest: {
      version: 'interest-2026.1',
      available: true,
      voluntary_completions: 39,
      vector: { 'network-analysis': 100, forensics: 28.2 },
      basis: 'voluntary activity categories, recency weighted',
      note: 'Optional answers are not stored in v3.',
    },
    affinity: {
      version: 'affinity-2026.1',
      available: true,
      gate: {
        available: true,
        labs: { have: 39, need: 30 },
        domains: { have: 13, need: 3 },
        observations: { have: 381, need: 100 },
      },
      pathways: [
        {
          pathway_id: 'soc-analyst',
          title: 'SOC Analyst',
          family: 'defensive',
          affinity: 16.3,
          confidence_band: 'high',
          evidence_count: 20,
          components: { coverage: 0, depth: 0.138, behavior: 0.443, interest: 0.462 },
          strongest_competencies: ['Packet Capture Analysis', 'Triage Techniques'],
          gaps: ['Subnetting'],
          why: ['20 of 29 critical competencies have evidence.'],
          formula_version: 'affinity-2026.1',
          weights: { coverage: 0.5 },
        },
      ],
      disclaimer: 'Affinity is descriptive, not a probability.',
    },
    proficiency_scale: [
      { id: 'practitioner', label: 'Practitioner', description: 'Applied in a familiar exercise.' },
    ],
    disclaimer: 'Affinity is descriptive, not a probability.',
  }
  return { ...base, ...overrides }
}

function mountPanel(global = {}) {
  return mount(CyberDnaV3Panel, {
    global: {
      stubs: { RouterLink: { template: '<a><slot /></a>' } },
      ...global,
    },
  })
}

describe('CyberDnaV3Panel', () => {
  beforeEach(() => {
    get.mockReset()
  })

  it('renders the affinity gate, pathways, and evidence', async () => {
    get.mockResolvedValue({ data: payload() })
    const wrapper = mountPanel()
    await flushPromises()

    expect(get).toHaveBeenCalledWith('/dna/v3/dna')
    expect(wrapper.text()).toContain('Career affinity')
    expect(wrapper.text()).toContain('Unlocked')
    expect(wrapper.text()).toContain('SOC Analyst')
    expect(wrapper.text()).toContain('20 critical competencies with evidence')
    expect(wrapper.text()).toContain('Investigative Queries')
    expect(wrapper.text()).toContain('Voluntary interest')
    expect(wrapper.text()).toContain('Network Analysis')
    expect(wrapper.text()).toContain('381')
    const gateBar = wrapper.find('[role="progressbar"]')
    expect(gateBar.attributes('aria-valuenow')).toBe('100')
    expect(gateBar.attributes('aria-valuetext')).toBe('39 of 30 labs')
  })

  it('shows gate progress without pathways below the threshold', async () => {
    const below = payload()
    below.affinity = {
      ...below.affinity,
      available: false,
      pathways: [],
      gate: {
        available: false,
        labs: { have: 12, need: 30 },
        domains: { have: 10, need: 3 },
        observations: { have: 122, need: 100 },
      },
    }
    get.mockResolvedValue({ data: below })
    const wrapper = mountPanel()
    await flushPromises()

    expect(wrapper.text()).toContain('More evidence needed')
    expect(wrapper.text()).not.toContain('SOC Analyst')
    expect(wrapper.text()).toContain('12 / 30')
    expect(wrapper.text()).toContain('Affinity hides itself')
  })

  it('shows the consent prompt when consent is revoked', async () => {
    get.mockRejectedValue({
      response: {
        status: 403,
        data: { error: 'ConsentRequired', detail: 'Cyber DNA consent is not granted.' },
      },
    })
    const wrapper = mountPanel()
    await flushPromises()

    expect(wrapper.text()).toContain('Cyber DNA is off')
    expect(wrapper.text()).toContain('Review privacy settings')
    expect(wrapper.find('a').exists()).toBe(true)
  })

  it('explains a role-scoped denial', async () => {
    get.mockRejectedValue({
      response: { status: 403, data: { detail: 'Role does not grant this permission' } },
    })
    const wrapper = mountPanel()
    await flushPromises()

    expect(wrapper.text()).toContain('scoped to learner accounts')
  })

  it('explains when the feature is disabled', async () => {
    get.mockRejectedValue({
      response: {
        status: 404,
        data: { detail: 'Cyber DNA v3 is not enabled on this deployment.' },
      },
    })
    const wrapper = mountPanel()
    await flushPromises()

    expect(wrapper.text()).toContain('Cyber DNA v3 is not enabled')
  })
})
