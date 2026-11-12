import { computed, ref, watch } from 'vue'

const STORAGE_KEY = 'theme'
const DARK = 'dark'
const LIGHT = 'light'
const CONTRAST = 'contrast'
const THEMES = [DARK, LIGHT, CONTRAST]
const LABELS = {
  [DARK]: 'dark',
  [LIGHT]: 'light',
  [CONTRAST]: 'high contrast',
}

// Shared state across all components that call useTheme()
const theme = ref(getInitialTheme())
const isDark = ref(theme.value === DARK)

function getInitialTheme() {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (THEMES.includes(stored)) return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? DARK : LIGHT
}

function applyTheme(value) {
  document.documentElement.setAttribute('data-theme', value)
  localStorage.setItem(STORAGE_KEY, value)
}

// Apply on module load
applyTheme(theme.value)

// Listen for system preference changes (only when no stored preference)
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (!localStorage.getItem(STORAGE_KEY)) {
    theme.value = e.matches ? DARK : LIGHT
  }
})

watch(theme, (val) => {
  isDark.value = val === DARK
  applyTheme(val)
})

const nextTheme = computed(() => THEMES[(THEMES.indexOf(theme.value) + 1) % THEMES.length])
const nextThemeLabel = computed(() => LABELS[nextTheme.value])

export function useTheme() {
  // Cycles dark -> light -> high contrast -> dark. The control keeps the same
  // button shape, so the only change for existing users is one extra stop.
  const toggleTheme = () => {
    theme.value = nextTheme.value
  }

  const setTheme = (value) => {
    if (THEMES.includes(value)) theme.value = value
  }

  return { theme, isDark, toggleTheme, setTheme, nextTheme, nextThemeLabel, themes: THEMES }
}
