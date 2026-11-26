import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ breaks: true, gfm: true })

// The one sanctioned markdown-to-HTML path: parse with marked, sanitize with
// DOMPurify. Every v-html of user or content-authored markdown goes through
// here so the sanitization step can never be forgotten at a call site.
export function renderMarkdown(text) {
  return DOMPurify.sanitize(marked.parse(String(text || '')))
}

// Hints/scenarios use angle-bracket placeholders -- flag formats like
// OCR{...reg_<register>_val_<value>} and command templates like `nmap <target>`.
// Two markdown hazards corrupt them: (1) <register>/<target> are parsed as HTML
// tags and stripped, and (2) underscores flanking a placeholder are parsed as
// emphasis (>_val_< -> italic "val"), dropping the underscores the exact-match
// flag needs. Escape the placeholder brackets, then convert the flanking
// underscores to a numeric entity so markdown leaves them literal. The URL-safe
// char class skips autolinks (<http://...> has :// ), and the transform is
// idempotent (entities are not re-matched).
export function escapeLabPlaceholders(text) {
  return String(text || '')
    .replace(/<([A-Za-z0-9_ -]+)>/g, '&lt;$1&gt;')
    .replace(/&gt;_/g, '&gt;&#95;')
    .replace(/_&lt;/g, '&#95;&lt;')
}

// Exercise prose is hard-wrapped in the source. Unwrap single newlines so
// paragraphs flow, while preserving intentional paragraph breaks (double
// newlines). Hints and short labels should use renderLabMarkdown without the
// unwrap option so a deliberate line break stays a line break.
export function renderLabMarkdown(text, { unwrap = false } = {}) {
  if (!text) return ''
  const source = String(text)
  const prepared = unwrap
    ? source
        .split(/\n\s*\n/)
        .map((para) => para.replace(/\n/g, ' '))
        .join('\n\n')
    : source
  return DOMPurify.sanitize(marked.parse(escapeLabPlaceholders(prepared)))
}
