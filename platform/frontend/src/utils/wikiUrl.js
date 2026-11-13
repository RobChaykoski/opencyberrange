import { safeHttpUrl } from './url'

// Optional separate origin for the workbook/manual wiki. When set at build
// time (for example https://wiki.example.edu), the iframe is cross-origin to
// the SPA and its scripts cannot read the SPA's localStorage. When empty, the
// wiki stays same-origin for single-host development deployments.
export const WIKI_BASE_URL = String(
  import.meta.env.VITE_WIKI_BASE_URL || ''
).replace(/\/+$/, '')

export function wikiUrl(path) {
  if (!path) return ''
  const raw = String(path).trim()
  if (!raw) return ''
  if (/^https?:\/\//i.test(raw)) return safeHttpUrl(raw)
  const normalized = raw.startsWith('/') ? raw : `/${raw}`
  return safeHttpUrl(WIKI_BASE_URL ? `${WIKI_BASE_URL}${normalized}` : normalized)
}
