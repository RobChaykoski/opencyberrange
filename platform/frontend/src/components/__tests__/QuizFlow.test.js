import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import QuizNavigation from '../QuizNavigation.vue'
import QuizQuestionDots from '../QuizQuestionDots.vue'
import QuizSubmitPanel from '../QuizSubmitPanel.vue'

describe('QuizQuestionDots', () => {
  it('marks the current and answered questions and emits a jump', async () => {
    const wrapper = mount(QuizQuestionDots, {
      props: { total: 4, position: 2, answeredPositions: [1, 3] },
    })

    const dots = wrapper.findAll('.quiz-dot')
    expect(dots).toHaveLength(4)
    expect(dots[1].attributes('aria-current')).toBe('true')
    expect(dots[0].classes()).toContain('quiz-dot--answered')
    expect(dots[2].classes()).toContain('quiz-dot--answered')
    expect(dots[1].attributes('aria-label')).toContain('not answered')

    await dots[3].trigger('click')
    expect(wrapper.emitted('jump')).toEqual([[4]])
  })

  it('disables jumping while a submission is in flight', () => {
    const wrapper = mount(QuizQuestionDots, {
      props: { total: 3, position: 1, disabled: true },
    })

    expect(wrapper.findAll('.quiz-dot').every((dot) => dot.attributes('disabled') !== undefined)).toBe(true)
  })
})

describe('QuizNavigation', () => {
  it('moves between questions and reports answered progress', async () => {
    const wrapper = mount(QuizNavigation, {
      props: { position: 1, total: 5, answeredCount: 2 },
    })

    expect(wrapper.text()).toContain('Question 1 of 5')
    expect(wrapper.text()).toContain('2 of 5 answered')
    expect(wrapper.findAll('button')[0].attributes('disabled')).toBeDefined()

    await wrapper.findAll('button')[1].trigger('click')
    expect(wrapper.emitted('change')).toEqual([[2]])
  })

  it('does not move past the last question', () => {
    const wrapper = mount(QuizNavigation, {
      props: { position: 5, total: 5, answeredCount: 5 },
    })

    expect(wrapper.findAll('button')[1].attributes('disabled')).toBeDefined()
  })
})

describe('QuizSubmitPanel', () => {
  it('requires confirmation before emitting submit', async () => {
    const wrapper = mount(QuizSubmitPanel, {
      props: {
        confirming: false,
        submitLabel: 'Submit for final mark',
        confirmText: 'Submit now?',
        confirmLabel: 'Yes, submit',
      },
    })

    const trigger = wrapper.findAll('button').find((button) => button.text() === 'Submit for final mark')
    await trigger.trigger('click')
    expect(wrapper.emitted('update:confirming')).toEqual([[true]])
    expect(wrapper.emitted('submit')).toBeUndefined()

    await wrapper.setProps({ confirming: true })
    expect(wrapper.text()).toContain('Submit now?')

    const confirm = wrapper.findAll('button').find((button) => button.text() === 'Yes, submit')
    await confirm.trigger('click')
    expect(wrapper.emitted('submit')).toHaveLength(1)
  })

  it('shows the unanswered warning and can cancel confirmation', async () => {
    const wrapper = mount(QuizSubmitPanel, {
      props: {
        confirming: true,
        warning: '2 questions still unanswered.',
        cancelLabel: 'Keep working',
      },
    })

    expect(wrapper.text()).toContain('2 questions still unanswered.')
    const cancel = wrapper.findAll('button').find((button) => button.text() === 'Keep working')
    await cancel.trigger('click')
    expect(wrapper.emitted('update:confirming')).toEqual([[false]])
  })
})
