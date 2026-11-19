export const COMMUNITY_EVENT_SOURCES = [
  {
    key: 'swocts-hub',
    name: 'SWOCTS Hub',
    description:
      'Community meetups, workshops, and the monthly CyberHive calendar for Southwestern Ontario.',
    url: 'https://www.swocts.com/events',
    calendarUrl: 'https://www.swocts.com/calendar',
    location: 'Southwestern Ontario',
  },
  {
    key: 'cyber-hive-yxu',
    name: 'Cyber Hive YXU',
    description:
      'London, Ontario cybersecurity meetups with power talks, hands-on workshops, student presentations, and networking.',
    url: 'https://www.eventbrite.ca/o/cyber-hive-yxu-113603781581',
    location: 'London, ON',
  },
]

export const COMMUNITY_EVENTS = [
  {
    id: 'cyber-hive-yxu-2026-12',
    title: 'Cyber Hive YXU December 2026 Meetup',
    start: '2026-12-08T18:00:00-05:00',
    location: 'North London Optimist Community Centre, London, ON',
    url: 'https://www.eventbrite.ca/e/cyber-hive-yxu-december-2026-meetup-tickets-1997088089235',
    source: 'Cyber Hive YXU',
    free: true,
    description:
      'Monthly cybersecurity meetup with power talks, hands-on workshops, student presentations, and free pizza.',
  },
]

export const mergeCommunityEvents = (primary, fallback) => {
  const seen = new Set()
  return [...(primary || []), ...(fallback || [])].filter((event) => {
    const key = `${String(event.title || '').trim().toLowerCase()}|${String(event.start || '').slice(0, 10)}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}
