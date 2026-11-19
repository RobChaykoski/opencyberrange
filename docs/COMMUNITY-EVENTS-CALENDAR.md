# Community events calendar

The platform shows the public SWOCTS Hub calendar beside its own competitions.
The source is the public Google Calendar that also powers
`https://www.swocts.com/calendar`.

## Source

| Item | Value |
|---|---|
| Calendar | `dcf7ff998803e31e8f5c679f57807d35ef54e763391071aa3a0fe28b48082035@group.calendar.google.com` |
| Feed | Public Google Calendar iCalendar (`basic.ics`) |
| Backend endpoint | `GET /api/public/community-events` |
| Frontend | Events page, embedded community calendar |

No API key is used. The calendar ID can be overridden with
`OCR_SWOCTS_CALENDAR_ID` when the source changes.

## Behaviour

- The backend fetches the feed server-side, so the browser never calls a
  third-party origin.
- The parsed event list is cached in process for 15 minutes.
- Recurring events are expanded for a bounded window: 45 days in the past and
  730 days in the future.
- All-day events use an inclusive end date, matching the calendar UI.
- Descriptions are converted to plain text and truncated.
- If the feed is unavailable, the endpoint returns the last cached copy when it
  has one. If there is no cached copy, the frontend keeps its saved community
  events and shows a short status message.
- Fetched events are merged with the saved community list and deduplicated by
  title and start date.

## Privacy and trust

The feed is public, read-only, and contains no learner data. The endpoint is
unauthenticated because the source is public. Event links are restricted to
`http` and `https` before rendering.

## Tests

- `platform/backend/tests/test_community_events.py` covers recurrence,
  all-day end dates, HTML stripping, and the endpoint.
- `platform/frontend/src/components/__tests__/CommunityEventsCalendar.test.js`
  covers rendering fetched events and the feed status.
- `platform/frontend/src/data/__tests__/communityEvents.test.js` covers the
  merge and deduplication rule.
