import { afterEach, describe, expect, it, vi } from 'vitest'
import { downloadBlob, filenameFromDisposition } from '../download'

describe('downloadBlob', () => {
  const originalCreate = URL.createObjectURL
  const originalRevoke = URL.revokeObjectURL

  afterEach(() => {
    URL.createObjectURL = originalCreate
    URL.revokeObjectURL = originalRevoke
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('revokes the object URL after the download has started', () => {
    vi.useFakeTimers()
    const create = vi.fn(() => 'blob:test')
    const revoke = vi.fn()
    URL.createObjectURL = create
    URL.revokeObjectURL = revoke

    const click = vi.fn()
    const original = document.createElement.bind(document)
    vi.spyOn(document, 'createElement').mockImplementation((tag) => {
      const element = original(tag)
      if (tag === 'a') element.click = click
      return element
    })

    downloadBlob(new Blob(['x']), 'report.csv')

    expect(create).toHaveBeenCalledTimes(1)
    expect(click).toHaveBeenCalledTimes(1)
    expect(revoke).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1500)
    expect(revoke).toHaveBeenCalledWith('blob:test')
  })
})

describe('filenameFromDisposition', () => {
  it('reads quoted and unquoted filenames', () => {
    expect(filenameFromDisposition('attachment; filename="report.pdf"', 'x')).toBe('report.pdf')
    expect(filenameFromDisposition('attachment; filename=report.csv', 'x')).toBe('report.csv')
  })

  it('falls back when the header is missing', () => {
    expect(filenameFromDisposition('', 'fallback.json')).toBe('fallback.json')
  })
})
