// CSV cell encoding that neutralises spreadsheet formula injection.
//
// Excel and LibreOffice execute cells beginning with =, +, -, or @ even when
// the field is quoted. Prefix only formula-like values with an apostrophe;
// plain numbers (including -5) and ordinary text are left unchanged.

const DANGEROUS_PREFIX = /^[\s]*[=+\-@\t\r\n]/
const NUMERIC = /^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$/
const LONE_MARKERS = new Set(['-', '+', '@'])

export function csvCell(value) {
  if (value === null || value === undefined) return '""'
  let text = String(value)
  const stripped = text.replace(/^[\s]+/, '')
  if (
    stripped
    && !LONE_MARKERS.has(stripped)
    && DANGEROUS_PREFIX.test(text)
    && !NUMERIC.test(stripped)
  ) {
    text = `'${text}`
  }
  return `"${text.replaceAll('"', '""')}"`
}

export function csvRow(values) {
  return values.map(csvCell).join(',')
}
