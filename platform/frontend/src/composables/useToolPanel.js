import { computed, ref } from 'vue'

// One shared panel state so the sidebar and the active-lab panel open the same
// bottom drawer. Only allow-listed tools can be opened; the URL is never taken
// from a route, query string, or learner input.
const TOOLS = Object.freeze({
  cyberchef: {
    key: 'cyberchef',
    title: 'CyberChef',
    url: '/tools/cyberchef/',
    description: 'Encode, decode, and inspect data without leaving the exercise.',
    attribution:
      'CyberChef is an Apache-2.0 tool by GCHQ. The pinned build is served from this platform, so it works without internet access.',
  },
})

const activeKey = ref(null)
const isOpen = ref(false)

export function useToolPanel() {
  const activeTool = computed(() => (activeKey.value ? TOOLS[activeKey.value] : null))

  const openTool = (key) => {
    if (!TOOLS[key]) return
    activeKey.value = key
    isOpen.value = true
  }

  const closeTool = () => {
    isOpen.value = false
  }

  const toggleTool = (key) => {
    if (isOpen.value && activeKey.value === key) {
      closeTool()
      return
    }
    openTool(key)
  }

  return {
    activeTool,
    isOpen,
    openTool,
    closeTool,
    toggleTool,
    tools: TOOLS,
  }
}
