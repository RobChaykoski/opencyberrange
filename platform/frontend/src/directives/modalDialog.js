/**
 * v-modal-dialog — add dialog behaviour to an existing overlay element.
 *
 * The admin overlays are hand-written markup with their own scoped styles, so a
 * component rewrite would be a large diff for little gain. This directive adds
 * what the markup is missing:
 *
 *   - role="dialog" and aria-modal="true"
 *   - aria-labelledby wired to the first .modal-title, h2, or h3 inside
 *   - Escape closes (when a close handler is passed)
 *   - focus moves into the dialog on open and returns on close
 *   - Tab and Shift+Tab stay inside the dialog
 *
 * Usage:
 *   <div v-if="open" class="modal-overlay" @click.self="close" v-modal-dialog="close">
 */

const FOCUSABLE = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled]):not([type="hidden"])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

let sequence = 0

function focusableIn(element) {
  return Array.from(element.querySelectorAll(FOCUSABLE)).filter((node) => {
    const style = window.getComputedStyle(node)
    return style.display !== 'none' && style.visibility !== 'hidden'
  })
}

export default {
  mounted(element, binding) {
    const close = typeof binding.value === 'function' ? binding.value : null

    element.setAttribute('role', 'dialog')
    element.setAttribute('aria-modal', 'true')
    if (!element.hasAttribute('tabindex')) element.setAttribute('tabindex', '-1')

    if (!element.hasAttribute('aria-label') && !element.hasAttribute('aria-labelledby')) {
      const title = element.querySelector('.modal-title, h2, h3')
      if (title) {
        if (!title.id) title.id = `ocr-dialog-title-${++sequence}`
        element.setAttribute('aria-labelledby', title.id)
      }
    }

    element.__ocrReturnFocus =
      document.activeElement instanceof HTMLElement ? document.activeElement : null

    requestAnimationFrame(() => {
      const [first] = focusableIn(element)
      ;(first || element).focus({ preventScroll: true })
    })

    const onKeydown = (event) => {
      if (event.key === 'Escape' && close) {
        event.preventDefault()
        event.stopPropagation()
        close()
        return
      }
      if (event.key !== 'Tab') return

      const items = focusableIn(element)
      if (!items.length) {
        event.preventDefault()
        element.focus()
        return
      }
      const first = items[0]
      const last = items[items.length - 1]
      if (
        event.shiftKey &&
        (document.activeElement === first || document.activeElement === element)
      ) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }

    element.addEventListener('keydown', onKeydown)
    element.__ocrKeydown = onKeydown
  },

  unmounted(element) {
    if (element.__ocrKeydown) {
      element.removeEventListener('keydown', element.__ocrKeydown)
    }
    const previous = element.__ocrReturnFocus
    if (previous && document.contains(previous)) {
      previous.focus({ preventScroll: true })
    }
  },
}
