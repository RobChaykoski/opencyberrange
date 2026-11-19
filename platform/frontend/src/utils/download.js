/**
 * Trigger a browser download for a Blob.
 *
 * Revoking the object URL immediately after `click()` can cancel the download
 * in Firefox and Safari. Keep the URL alive briefly so the browser can start
 * the transfer, then revoke it.
 */
export function downloadBlob(blob, filename) {
  const payload = blob instanceof Blob ? blob : new Blob([blob])
  const url = URL.createObjectURL(payload)
  const link = document.createElement('a')
  link.href = url
  link.download = filename || 'download'
  link.rel = 'noopener'
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 1500)
}

/** Extract a filename from a Content-Disposition header, with a fallback. */
export function filenameFromDisposition(disposition, fallback) {
  if (!disposition) return fallback
  const match = /filename\*?=(?:UTF-8''|")?([^";]+)"?/i.exec(disposition)
  return match ? decodeURIComponent(match[1]) : fallback
}
