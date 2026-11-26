import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ExerciseBrief from '../ExerciseBrief.vue'

const lab = {
  name: 'Investigating a Suspicious Login',
  scenario:
    'Review the alert and connect to <target>.\n\nThe flag format is OCR{reg_<register>_val_<value>}.',
  objectives: ['Explain the detection', 'Confirm the finding by hand'],
  hints_total: 2,
  workbook: 'guide.md',
}

const hostnames = [
  { hostname: 'files.lab', description: 'File server', ip: '10.100.6.5' },
  { hostname: 'jump.lab', description: 'Jump host', ip: null },
]

describe('ExerciseBrief', () => {
  it('renders the scenario, objectives, hosts, and unlocked hints', () => {
    const wrapper = mount(ExerciseBrief, {
      props: {
        lab,
        track: { name: 'Network Defence' },
        level: { number: 3, name: 'Investigation' },
        hostnames,
        hints: [{ number: 1, text: 'Start with the authentication log.' }],
        workbookUrl: '/wiki/course/net/guide.md',
      },
    })

    expect(wrapper.text()).toContain('Investigating a Suspicious Login')
    expect(wrapper.text()).toContain('Network Defence')
    expect(wrapper.text()).toContain('Level 3')
    expect(wrapper.text()).toContain('<target>')
    expect(wrapper.text()).not.toContain('&lt;target&gt;')
    expect(wrapper.text()).toContain('Explain the detection')
    expect(wrapper.text()).toContain('files.lab')
    expect(wrapper.text()).toContain('10.100.6.5')
    expect(wrapper.text()).toContain('Hint 1')
    expect(wrapper.text()).toContain('authentication log')
  })

  it('sanitizes scenario HTML and never renders a script or event handler', () => {
    const wrapper = mount(ExerciseBrief, {
      props: {
        lab: {
          ...lab,
          scenario: 'Safe <script>alert(1)</script><img src="x" onerror="alert(1)">',
        },
      },
    })

    expect(wrapper.find('script').exists()).toBe(false)
    expect(wrapper.find('img').exists()).toBe(true)
    expect(wrapper.find('img').attributes('onerror')).toBeUndefined()
  })

  it('does not render a flag or an unsafe workbook link', () => {
    const wrapper = mount(ExerciseBrief, {
      props: {
        lab: { ...lab, scenario: 'Review the alert.', flag: 'OCR{secret}' },
        workbookUrl: 'javascript:alert(1)',
      },
    })

    expect(wrapper.text()).not.toContain('OCR{secret}')
    expect(wrapper.find('.exercise-brief__workbook-link').exists()).toBe(false)
  })

  it('emits pop-out and workbook actions', async () => {
    const wrapper = mount(ExerciseBrief, {
      props: {
        lab,
        workbookUrl: 'https://wiki.example.test/wiki/course/net/guide.md',
      },
    })

    const popOut = wrapper
      .findAll('button')
      .find((button) => button.text() === 'Pop out briefing')
    expect(popOut).toBeTruthy()
    await popOut.trigger('click')
    expect(wrapper.emitted('pop-out')).toHaveLength(1)

    await wrapper.get('.exercise-brief__workbook-link').trigger('click')
    expect(wrapper.emitted('open-workbook')).toHaveLength(1)
  })

  it('hides the pop-out control in the pop-out page itself', () => {
    const wrapper = mount(ExerciseBrief, {
      props: { lab, popout: true },
    })

    expect(wrapper.text()).not.toContain('Pop out briefing')
  })
})
