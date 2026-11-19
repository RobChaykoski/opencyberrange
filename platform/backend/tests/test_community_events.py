"""Community calendar ingestion tests."""

from datetime import datetime, timezone

from app.services.community_events import parse_ics


SAMPLE = """BEGIN:VCALENDAR
VERSION:2.0
X-WR-TIMEZONE:America/Toronto
BEGIN:VEVENT
DTSTART;TZID=America/Toronto:20261208T180000
DTEND;TZID=America/Toronto:20261208T200000
RRULE:FREQ=WEEKLY;COUNT=2
UID:weekly-1
SUMMARY:Weekly security meetup
LOCATION:Hall\\, London
DESCRIPTION:<p>Hello &amp; welcome</p>
URL:https://example.com/event
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:20270128
DTEND;VALUE=DATE:20270130
UID:all-day-1
SUMMARY:Two day workshop
LOCATION:London
END:VEVENT
END:VCALENDAR
"""


def test_parse_ics_expands_recurrence_and_strips_html():
    events = parse_ics(
        SAMPLE,
        now=datetime(2026, 12, 1, 12, tzinfo=timezone.utc),
    )
    weekly = [event for event in events if event["title"] == "Weekly security meetup"]
    assert len(weekly) == 2
    assert weekly[0]["start"] == "2026-12-08T18:00:00-05:00"
    assert weekly[0]["location"] == "Hall, London"
    assert weekly[0]["description"] == "Hello & welcome"
    assert weekly[0]["url"] == "https://example.com/event"
    assert weekly[1]["start"] == "2026-12-15T18:00:00-05:00"


def test_parse_ics_treats_all_day_end_as_exclusive():
    events = parse_ics(
        SAMPLE,
        now=datetime(2026, 12, 1, 12, tzinfo=timezone.utc),
    )
    all_day = next(event for event in events if event["title"] == "Two day workshop")
    assert all_day["all_day"] is True
    assert all_day["start"] == "2027-01-28T00:00:00-05:00"
    assert all_day["end"] == "2027-01-29T00:00:00-05:00"


def test_disallowed_frequency_does_not_expand():
    feed = """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART:20261208T180000Z
DTEND:20261208T190000Z
RRULE:FREQ=SECONDLY
UID:seconds-1
SUMMARY:Unsafe frequency
END:VEVENT
END:VCALENDAR
"""
    events = parse_ics(feed, now=datetime(2026, 12, 1, tzinfo=timezone.utc))
    assert len(events) == 1


def test_malformed_event_is_skipped():
    feed = """BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:Missing start
END:VEVENT
BEGIN:VEVENT
DTSTART:20261208T180000Z
DTEND:20261208T190000Z
UID:valid-1
SUMMARY:Valid event
END:VEVENT
END:VCALENDAR
"""
    events = parse_ics(feed, now=datetime(2026, 12, 1, tzinfo=timezone.utc))
    assert [event["title"] for event in events] == ["Valid event"]


def test_community_events_endpoint(client, monkeypatch):
    from app.routers import public_config

    payload = {
        "events": [
            {
                "id": "event-1",
                "title": "Test event",
                "start": "2026-12-08T18:00:00-05:00",
                "end": "2026-12-08T20:00:00-05:00",
                "location": "London",
                "description": "Test",
                "url": "https://example.com",
                "source": "SWOCTS Hub",
            }
        ],
        "source": {"key": "swocts-hub", "name": "SWOCTS Hub"},
        "available": True,
        "cached": False,
        "stale": False,
    }
    monkeypatch.setattr(public_config, "get_community_events", lambda: payload)

    response = client.get("/api/public/community-events")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["events"][0]["title"] == "Test event"
    assert response.headers["cache-control"].startswith("public")
