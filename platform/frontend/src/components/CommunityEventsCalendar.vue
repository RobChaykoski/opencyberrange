<template>
  <section class="community-events" aria-labelledby="community-events-title">
    <header class="community-events__head">
      <div>
        <p class="community-events__eyebrow">Around the area</p>
        <h2 id="community-events-title">Cybersecurity events calendar</h2>
        <p class="community-events__intro">
          Our events and community events happening around Southwestern Ontario.
          Community events are hosted outside the range and are not part of your
          Cyber DNA, course credit, or platform scoring.
        </p>
      </div>
      <div class="calendar-nav" aria-label="Calendar month controls">
        <button type="button" class="btn btn--outline btn--sm" aria-label="Previous month" @click="changeMonth(-1)">
          &lsaquo;
        </button>
        <button type="button" class="btn btn--outline btn--sm" @click="goToday">Today</button>
        <button type="button" class="btn btn--outline btn--sm" aria-label="Next month" @click="changeMonth(1)">
          &rsaquo;
        </button>
      </div>
    </header>

    <div class="community-events__layout">
      <div class="calendar">
        <div class="calendar__month">{{ monthLabel }}</div>
        <div class="calendar__weekdays" aria-hidden="true">
          <span v-for="day in weekdays" :key="day">{{ day }}</span>
        </div>
        <div class="calendar__grid" role="grid" :aria-label="`${monthLabel} events`">
          <div
            v-for="cell in calendarDays"
            :key="cell.key"
            class="calendar-day"
            :class="{
              'calendar-day--muted': !cell.currentMonth,
              'calendar-day--today': cell.isToday,
              'calendar-day--has-events': cell.events.length,
            }"
            role="gridcell"
            :aria-label="cell.label"
          >
            <span class="calendar-day__number">{{ cell.date.getDate() }}</span>
            <span v-if="cell.events.length" class="calendar-day__events">
              <span
                v-for="event in cell.events.slice(0, 3)"
                :key="event.id"
                class="calendar-day__dot"
                :class="`calendar-day__dot--${event.kind}`"
                :title="event.title"
              ></span>
              <span v-if="cell.events.length > 3" class="calendar-day__more">+{{ cell.events.length - 3 }}</span>
            </span>
          </div>
        </div>
        <div class="calendar__legend">
          <span><i class="calendar-day__dot calendar-day__dot--internal"></i> Our events</span>
          <span><i class="calendar-day__dot calendar-day__dot--community"></i> Community events</span>
        </div>
      </div>

      <div class="community-events__list">
        <h3>Upcoming</h3>
        <p v-if="!upcomingEvents.length" class="community-events__empty">
          No upcoming events in the calendar. Check the community sources below
          for the latest dates.
        </p>
        <article v-for="event in upcomingEvents" :key="event.id" class="community-event">
          <div class="community-event__date">
            <strong>{{ event.start.getDate() }}</strong>
            <span>{{ event.start.toLocaleDateString(undefined, { month: 'short' }) }}</span>
          </div>
          <div class="community-event__body">
            <div class="community-event__head">
              <h4>{{ event.title }}</h4>
              <span class="community-event__badge" :class="`community-event__badge--${event.kind}`">
                {{ event.kind === 'internal' ? 'Our event' : event.source || 'Community' }}
              </span>
            </div>
            <p class="community-event__meta">{{ formatEventDate(event) }} &middot; {{ event.location }}</p>
            <p class="community-event__description">{{ event.description }}</p>
            <router-link v-if="event.kind === 'internal'" :to="event.to" class="community-event__link">
              Open event &rarr;
            </router-link>
            <a
              v-else
              :href="safeHttpUrl(event.url)"
              target="_blank"
              rel="noopener noreferrer"
              class="community-event__link"
            >
              Event details &rarr;
            </a>
          </div>
        </article>

        <div class="community-events__sources">
          <h3>Community sources</h3>
          <article v-for="source in sources" :key="source.key" class="community-source">
            <div>
              <strong>{{ source.name }}</strong>
              <p>{{ source.description }}</p>
              <p class="community-source__meta">{{ source.location }}</p>
            </div>
            <div class="community-source__actions">
              <a :href="safeHttpUrl(source.url)" target="_blank" rel="noopener noreferrer" class="btn btn--primary btn--sm">
                Events
              </a>
              <a
                v-if="source.calendarUrl"
                :href="safeHttpUrl(source.calendarUrl)"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn--outline btn--sm"
              >
                Calendar
              </a>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { safeHttpUrl } from '../utils/url'

const props = defineProps({
  internalEvents: { type: Array, default: () => [] },
  communityEvents: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] },
})

const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const today = new Date()
const toDate = (value) => (value ? new Date(value) : null)
const startOfDay = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate())
const startOfMonth = (date) => new Date(date.getFullYear(), date.getMonth(), 1)
const sameDay = (a, b) => startOfDay(a).getTime() === startOfDay(b).getTime()

const normalizedEvents = computed(() => {
  const internal = props.internalEvents
    .filter((event) => event.start_at)
    .map((event) => ({
      id: `internal-${event.id}`,
      title: event.name,
      start: toDate(event.start_at),
      end: toDate(event.end_at),
      kind: 'internal',
      location: 'This range',
      description: event.description || 'Platform event.',
      to: `/events/${event.id}`,
    }))
  const community = props.communityEvents
    .filter((event) => event.start)
    .map((event) => ({
      ...event,
      start: toDate(event.start),
      end: toDate(event.end),
      kind: 'community',
    }))
  return [...internal, ...community].sort((a, b) => a.start - b.start)
})

const nextEvent = computed(() =>
  normalizedEvents.value.find((event) => event.start >= startOfDay(today)),
)
const viewMonth = ref(startOfMonth(nextEvent.value?.start || today))

const monthLabel = computed(() =>
  viewMonth.value.toLocaleDateString(undefined, { month: 'long', year: 'numeric' }),
)

const eventCoversDay = (event, date) => {
  const day = startOfDay(date).getTime()
  const start = startOfDay(event.start).getTime()
  const end = event.end ? startOfDay(event.end).getTime() : start
  return day >= start && day <= end
}

const calendarDays = computed(() => {
  const year = viewMonth.value.getFullYear()
  const month = viewMonth.value.getMonth()
  const first = new Date(year, month, 1)
  const leading = first.getDay()
  const cells = []
  for (let index = 0; index < 42; index += 1) {
    const date = new Date(year, month, index - leading + 1)
    const events = normalizedEvents.value.filter((event) => eventCoversDay(event, date))
    const label = `${date.toLocaleDateString(undefined, {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })}${events.length ? `: ${events.map((event) => event.title).join(', ')}` : ''}`
    cells.push({
      key: `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`,
      date,
      currentMonth: date.getMonth() === month,
      isToday: sameDay(date, today),
      events,
      label,
    })
  }
  return cells
})

const upcomingEvents = computed(() =>
  normalizedEvents.value
    .filter((event) => event.start >= startOfDay(today))
    .slice(0, 8),
)

const changeMonth = (delta) => {
  viewMonth.value = new Date(viewMonth.value.getFullYear(), viewMonth.value.getMonth() + delta, 1)
}

const goToday = () => {
  viewMonth.value = startOfMonth(today)
}

const formatEventDate = (event) =>
  event.start.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
</script>

<style scoped>
.community-events {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.community-events__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.community-events__eyebrow {
  margin: 0 0 0.25rem;
  color: var(--accent);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.community-events__head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.15rem;
}

.community-events__intro {
  max-width: 58rem;
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.calendar-nav {
  display: flex;
  gap: 0.35rem;
  flex: 0 0 auto;
}

.community-events__layout {
  display: grid;
  grid-template-columns: minmax(280px, 0.95fr) minmax(0, 1.05fr);
  gap: 1rem;
}

.calendar {
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
}

.calendar__month {
  margin-bottom: 0.6rem;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 700;
}

.calendar__weekdays,
.calendar__grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.25rem;
}

.calendar__weekdays span {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 700;
  text-align: center;
  text-transform: uppercase;
}

.calendar-day {
  min-height: 2.4rem;
  padding: 0.25rem;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.calendar-day--muted {
  color: var(--text-muted);
  opacity: 0.45;
}

.calendar-day--today {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--accent-text);
}

.calendar-day--has-events {
  background: var(--bg-secondary);
}

.calendar-day__number {
  display: block;
  font-weight: 700;
  text-align: center;
}

.calendar-day__events {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.15rem;
  margin-top: 0.15rem;
  flex-wrap: wrap;
}

.calendar-day__dot {
  width: 0.35rem;
  height: 0.35rem;
  border-radius: 50%;
  background: var(--text-muted);
}

.calendar-day__dot--internal {
  background: var(--accent);
}

.calendar-day__dot--community {
  background: var(--success);
}

.calendar-day__more {
  color: var(--text-muted);
  font-size: 0.55rem;
}

.calendar__legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.7rem;
  color: var(--text-muted);
  font-size: 0.66rem;
}

.calendar__legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.calendar__legend i {
  display: inline-block;
}

.community-events__list h3 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.community-events__empty {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

.community-event {
  display: flex;
  gap: 0.7rem;
  padding: 0.7rem 0;
  border-bottom: 1px solid var(--border-color);
}

.community-event:last-of-type {
  border-bottom: none;
}

.community-event__date {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 2.8rem;
  padding: 0.3rem 0.2rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.community-event__date strong {
  font-size: 1rem;
  line-height: 1;
}

.community-event__date span {
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
}

.community-event__body {
  min-width: 0;
}

.community-event__head {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  justify-content: space-between;
}

.community-event__head h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.86rem;
  line-height: 1.3;
}

.community-event__badge {
  flex: 0 0 auto;
  padding: 0.1rem 0.35rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.56rem;
  font-weight: 700;
  text-transform: uppercase;
  white-space: nowrap;
}

.community-event__badge--internal {
  border-color: var(--accent);
  color: var(--accent);
}

.community-event__badge--community {
  border-color: var(--success);
  color: var(--success);
}

.community-event__meta,
.community-event__description {
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.4;
}

.community-event__description {
  color: var(--text-secondary);
}

.community-event__link {
  display: inline-block;
  margin-top: 0.3rem;
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  text-decoration: none;
}

.community-event__link:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.community-events__sources {
  margin-top: 1rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border-color);
}

.community-source {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.7rem;
  padding: 0.55rem 0;
  border-bottom: 1px solid var(--border-color);
}

.community-source:last-of-type {
  border-bottom: none;
}

.community-source strong {
  color: var(--text-primary);
  font-size: 0.82rem;
}

.community-source p {
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.4;
}

.community-source__meta {
  color: var(--text-muted) !important;
}

.community-source__actions {
  display: flex;
  gap: 0.35rem;
  flex: 0 0 auto;
}

@media (max-width: 900px) {
  .community-events__layout {
    grid-template-columns: 1fr;
  }

  .community-events__head {
    flex-direction: column;
  }
}

@media (max-width: 520px) {
  .community-source {
    flex-direction: column;
  }

  .calendar-day {
    min-height: 2.1rem;
  }
}
</style>
