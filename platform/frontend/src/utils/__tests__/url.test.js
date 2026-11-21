import { describe, expect, it } from 'vitest'

import { safeHttpUrl } from '../url'

describe('safeHttpUrl', () => {
  it('accepts normal http(s) links and normalizes them', () => {
    expect(safeHttpUrl('https://www.eventbrite.ca/e/cyber-hive-tickets-1')).toBe(
      'https://www.eventbrite.ca/e/cyber-hive-tickets-1'
    )
    expect(safeHttpUrl('/events/1')).toBe(`${window.location.origin}/events/1`)
  })

  it('rejects executable and malformed values', () => {
    expect(safeHttpUrl('javascript:alert(1)')).toBe('')
    expect(safeHttpUrl('data:text/html,<script>alert(1)</script>')).toBe('')
    expect(safeHttpUrl('vbscript:msgbox(1)')).toBe('')
    expect(safeHttpUrl('')).toBe('')
  })

  it('rejects credentials and parser-confusing characters', () => {
    expect(safeHttpUrl('https://user:pass@example.com/event')).toBe('')
    expect(safeHttpUrl('https://example.com\\@evil.example/event')).toBe('')
    expect(safeHttpUrl('https://example.com/\nnext')).toBe('')
  })
})
