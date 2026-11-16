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
  otscan: {
    key: 'otscan',
    title: 'OT scan assistant',
    url: '/tools/ot-scan/',
    description: 'Build a slow, scoped nmap command for Modbus, S7, EtherNet/IP, or DNP3.',
    attribution:
      'Runs entirely in this panel. The platform does not send a scan; it only writes the command after you confirm authorisation.',
  },
  attacknavigator: {
    key: 'attacknavigator',
    title: 'MITRE ATT&CK Navigator',
    url: 'https://mitre-attack.github.io/attack-navigator/',
    description:
      'Explore ATT&CK techniques and build a coverage layer for a lab or detection review.',
    attribution:
      'MITRE ATT&CK Navigator is an Apache-2.0 project by The MITRE Corporation. It runs at mitre-attack.github.io and needs internet access.',
    // Navigator keeps its layers in its own browser storage. The iframe stays
    // cross-origin, so allow-same-origin preserves Navigator's origin and
    // storage without granting access to the platform origin.
    sandbox: 'allow-scripts allow-same-origin allow-forms allow-downloads allow-modals',
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
