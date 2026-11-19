import { describe, expect, it } from 'vitest'

import { mergeCommunityEvents } from '../communityEvents'

describe('mergeCommunityEvents', () => {
  it('keeps fetched events and deduplicates by title and day', () => {
    const primary = [
      {
        id: 'live-1',
        title: 'CyberRunners London',
        start: '2026-11-21T10:00:00-05:00',
      },
    ]
    const fallback = [
      {
        id: 'saved-1',
        title: 'cyberrunners london',
        start: '2026-11-21T10:00:00-05:00',
      },
      {
        id: 'saved-2',
        title: 'Cyber Hive YXU',
        start: '2026-12-08T18:00:00-05:00',
      },
    ]

    const merged = mergeCommunityEvents(primary, fallback)
    expect(merged).toHaveLength(2)
    expect(merged[0].id).toBe('live-1')
    expect(merged[1].id).toBe('saved-2')
  })
})
