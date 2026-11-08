import { onMounted, onUnmounted, ref } from 'vue'

/**
 * Track whether the viewport is in the mobile shell range.
 *
 * The query result is read during setup so the app does not briefly render the
 * desktop sidebar on a phone before the first resize event.
 */
export function useMobileView(breakpoint = 768) {
  const query = typeof window !== 'undefined'
    ? window.matchMedia(`(max-width: ${breakpoint}px)`)
    : null
  const isMobile = ref(query ? query.matches : false)

  const update = (event) => {
    isMobile.value = event.matches
  }

  onMounted(() => {
    if (query) query.addEventListener('change', update)
  })

  onUnmounted(() => {
    if (query) query.removeEventListener('change', update)
  })

  return { isMobile }
}
