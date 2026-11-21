// Only allow http(s) URLs (and same-origin relative paths) to reach href/src
// bindings. Content-authored links and admin-supplied website fields otherwise
// allow javascript:, data:, or vbscript: URLs to execute in the app origin.
export function safeHttpUrl(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  // Control characters and backslashes are parsed differently by browsers and
  // URL libraries. Reject them instead of guessing which interpretation wins.
  const hasControl = [...raw].some((char) => {
    const code = char.charCodeAt(0)
    return code < 32 || code === 127
  })
  if (hasControl || raw.includes('\\')) return ''
  try {
    const parsed = new URL(raw, window.location.origin)
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return ''
    // Credentials in a link are a phishing signal and never needed here.
    if (parsed.username || parsed.password) return ''
    // Return the normalized URL so the href is exactly what was validated.
    return parsed.href
  } catch {
    return ''
  }
}
