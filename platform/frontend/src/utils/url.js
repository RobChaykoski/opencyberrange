// Only allow http(s) URLs (and same-origin relative paths) to reach href/src
// bindings. Content-authored links and admin-supplied website fields otherwise
// allow javascript:, data:, or vbscript: URLs to execute in the app origin.
export function safeHttpUrl(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  try {
    const parsed = new URL(raw, window.location.origin)
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return ''
    return raw
  } catch {
    return ''
  }
}
