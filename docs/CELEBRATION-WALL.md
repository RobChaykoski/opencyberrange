# Celebration Wall

The Celebration Wall is the cross-course recognition surface for public
achievements. It is voluntary, anonymous, and deliberately not a leaderboard.

## What it shows

- recent public achievements from listed learners;
- a badge gallery with award and celebration counts;
- badges people are celebrating, aggregated by badge type;
- the current user's own corner, including celebrations received;
- privacy controls for listing and name mode.

Administrator accounts are not listed. A learner who turns off **Show me on the
wall** keeps a private corner but does not appear in the shared feed.

## Celebration action

- One signed-in user can celebrate one public achievement once.
- The action is a toggle. Selecting it again removes the celebration.
- The wall returns only the count. The celebrator's identity is stored in
  `achievement_celebrations` for duplicate prevention and is never exposed.
- A learner cannot celebrate their own win.
- A hidden or unlisted achievement cannot be celebrated.
- Celebrations do not touch analytics, completion, Cyber DNA, course health,
  certificates, or grading. They are not a learning metric.

## Data model

```text
achievement_celebrations
  id
  achievement_id  -> achievements.id (CASCADE)
  user_id         -> users.id (CASCADE)
  created_at
  UNIQUE (achievement_id, user_id)
```

The unique index enforces one celebration per person per achievement. The
`user_id` is not serialized by the wall API.

## API

```text
GET  /api/dashboard/celebrations
POST /api/dashboard/celebrations/{achievement_id}/celebrate
```

The `POST` response is:

```json
{"celebrated": true, "count": 3}
```

The wall response adds `celebration_count` and `celebrated_by_me` to each
recent win, `celebrations` and `celebrants` to each badge, and
`celebrations_received` and `celebrations_given` to the current user's corner.

## Privacy and safety

- Voluntary: the user can leave the wall at any time.
- Anonymous: the count is public; the celebrator is not.
- Name modes: real name, username, or **Anonymous participant**.
- No comments, chat, or messaging. The wall is not a support channel.
- No celebration on an unlisted or admin-owned achievement.
- No effect on progress, completion, course health, Cyber DNA, or reports.
- Follow the platform's consent and erasure rules. Deleting a user or an
  achievement cascades the celebration rows.

## Design

- The wall is a recognition page, not an operational dashboard.
- Use the existing tokens and a restrained hero. Do not add confetti or a second
  palette.
- Status and counts use text labels, not colour or emoji alone.
- The personal corner leads with the learner's own wins and celebrations.
- The "badges people are celebrating" panel is aggregated by badge, not by
  person.
- Mobile stacks the feed and the side panels; the celebration button remains at
  least 28px high and has an accessible name.

## Acceptance criteria

- A signed-in user can celebrate and un-celebrate a public win.
- The count updates for the actor and on reload.
- A self-celebration is rejected.
- A hidden or unlisted win cannot be celebrated.
- The wall never returns the celebrator's identity.
- Celebrations are absent from every analytics, course-health, and Cyber DNA
  query.
- The wall works in both themes, at 390 px and 1440 px, with no page overflow.
