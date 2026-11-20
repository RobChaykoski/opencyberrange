import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { defineComponent, h, ref, withDirectives } from 'vue'

import modalDialog from '../modalDialog'

const Host = defineComponent({
  props: { onClose: { type: Function, default: () => {} } },
  setup(props) {
    const open = ref(true)
    return () =>
      open.value
        ? withDirectives(
            h('div', { class: 'modal-overlay' }, [
              h('h3', { class: 'modal-title' }, 'Disk management'),
              h('button', { class: 'first' }, 'Close'),
              h('button', { class: 'last' }, 'Confirm'),
            ]),
            [[modalDialog, props.onClose]]
          )
        : null
  },
})

const mountHost = (onClose = () => {}) =>
  mount(Host, { props: { onClose }, attachTo: document.body })

describe('v-modal-dialog', () => {
  it('declares a labelled modal dialog', () => {
    const wrapper = mountHost()
    const overlay = wrapper.get('.modal-overlay')
    expect(overlay.attributes('role')).toBe('dialog')
    expect(overlay.attributes('aria-modal')).toBe('true')
    expect(overlay.attributes('tabindex')).toBe('-1')
    expect(overlay.attributes('aria-labelledby')).toBeTruthy()
    const title = document.getElementById(overlay.attributes('aria-labelledby'))
    expect(title.textContent).toBe('Disk management')
    wrapper.unmount()
  })

  it('closes on Escape', async () => {
    const onClose = vi.fn()
    const wrapper = mountHost(onClose)
    await wrapper.get('.modal-overlay').trigger('keydown', { key: 'Escape' })
    expect(onClose).toHaveBeenCalledTimes(1)
    wrapper.unmount()
  })

  it('moves focus inside the dialog and wraps Tab at the end', async () => {
    const wrapper = mountHost()
    await new Promise((resolve) => requestAnimationFrame(resolve))
    const first = wrapper.get('.first').element
    const last = wrapper.get('.last').element
    expect(document.activeElement).toBe(first)

    last.focus()
    await wrapper.get('.modal-overlay').trigger('keydown', { key: 'Tab' })
    expect(document.activeElement).toBe(first)
    wrapper.unmount()
  })
})
