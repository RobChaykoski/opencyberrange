import { ref } from 'vue'
import axios from '../api/axios'

// Stored in the account's notification_prefs JSON so the choice follows the
// learner across devices. The local cache only prevents a one-frame flash
// before /auth/settings resolves.
const STORAGE_KEY = 'ocr.celebration.effect'
const DEFAULT_EFFECT = 'fireworks'

export const CELEBRATION_OPTIONS = [
  {
    value: 'fireworks',
    label: 'Fireworks',
    description: 'Bursts of colour behind the flag-captured card.',
  },
  {
    value: 'matrix',
    label: 'Matrix code rain',
    description: 'Green falling code in a retro terminal style.',
  },
  {
    value: 'confetti',
    label: 'Confetti',
    description: 'The classic falling confetti celebration.',
  },
  {
    value: 'off',
    label: 'Off',
    description: 'Keep the success summary, without the animated effect.',
  },
]

const VALID_EFFECTS = new Set(CELEBRATION_OPTIONS.map((option) => option.value))

function normalizeEffect(value) {
  return VALID_EFFECTS.has(value) ? value : DEFAULT_EFFECT
}

function readCachedEffect() {
  try {
    return normalizeEffect(localStorage.getItem(STORAGE_KEY))
  } catch {
    return DEFAULT_EFFECT
  }
}

function writeCachedEffect(value) {
  try {
    localStorage.setItem(STORAGE_KEY, value)
  } catch {
    // Private mode: the in-memory choice still applies for this session.
  }
}

const effect = ref(readCachedEffect())
const loaded = ref(false)
const saving = ref(false)
let loadingPromise = null

export function useCelebration() {
  async function load(force = false) {
    if (loaded.value && !force) return effect.value
    if (loadingPromise) return loadingPromise
    loadingPromise = axios
      .get('/auth/settings')
      .then(({ data }) => {
        const stored = data?.notification_prefs?.flag_celebration
        effect.value = stored ? normalizeEffect(stored) : DEFAULT_EFFECT
        loaded.value = true
        writeCachedEffect(effect.value)
        return effect.value
      })
      .catch(() => effect.value)
      .finally(() => {
        loadingPromise = null
      })
    return loadingPromise
  }

  async function setEffect(value) {
    const next = normalizeEffect(value)
    saving.value = true
    try {
      const { data } = await axios.get('/auth/settings')
      const prefs = {
        ...(data?.notification_prefs || {}),
        flag_celebration: next,
      }
      await axios.put('/auth/settings', { notification_prefs: prefs })
      effect.value = next
      loaded.value = true
      writeCachedEffect(next)
      return next
    } finally {
      saving.value = false
    }
  }

  return {
    effect,
    loaded,
    saving,
    options: CELEBRATION_OPTIONS,
    load,
    setEffect,
  }
}
