import { ref } from 'vue'
import { safeHttpUrl } from './url'

// The wiki origin is a server setting read at runtime. The build-time value is
// only a fallback for older deployments and for the first paint before
// /api/config/public returns.
const BUILD_BASE = String(import.meta.env.VITE_WIKI_BASE_URL || '').replace(/\/+$/, '')
export const wikiBaseUrl = ref(BUILD_BASE)

export function setWikiBaseUrl(value) {
  wikiBaseUrl.value = String(value || '').trim().replace(/\/+$/, '')
}

export function wikiUrl(path) {
  if (!path) return ''
  const raw = String(path).trim()
  if (!raw) return ''
  if (/^https?:\/\//i.test(raw)) return safeHttpUrl(raw)
  const normalized = raw.startsWith('/') ? raw : `/${raw}`
  const base = wikiBaseUrl.value
  return safeHttpUrl(base ? `${base}${normalized}` : normalized)
}
