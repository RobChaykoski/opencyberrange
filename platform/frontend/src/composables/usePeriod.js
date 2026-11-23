import { computed, ref } from 'vue'

export const PERIOD_PRESETS = [
  { key: '1h', label: '1h' },
  { key: '6h', label: '6h' },
  { key: '24h', label: '24h' },
  { key: '7d', label: '7 days' },
  { key: 'this-week', label: 'This week' },
  { key: 'last-week', label: 'Last week' },
  { key: '30d', label: '30 days' },
  { key: '90d', label: '90 days' },
  { key: 'custom', label: 'Custom' },
]

const DAY_MS = 86_400_000

const fmt = new Intl.DateTimeFormat(undefined, {
  month: 'short',
  day: 'numeric',
})

export function formatPeriodDay(value) {
  const date = value instanceof Date ? value : new Date(value)
  return Number.isNaN(date.getTime()) ? '' : fmt.format(date)
}

export function toLocalInput(value) {
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (number) => String(number).padStart(2, '0')
  return [
    date.getFullYear(),
    '-',
    pad(date.getMonth() + 1),
    '-',
    pad(date.getDate()),
    'T',
    pad(date.getHours()),
    ':',
    pad(date.getMinutes()),
  ].join('')
}

function startOfDay(value) {
  const date = new Date(value)
  date.setHours(0, 0, 0, 0)
  return date
}

function startOfWeek(value) {
  const date = startOfDay(value)
  const offset = (date.getDay() + 6) % 7 // Monday = 0
  date.setDate(date.getDate() - offset)
  return date
}

function rangeLabel(base, start, end, includeDates = true) {
  if (!includeDates) return base
  if (formatPeriodDay(start) === formatPeriodDay(end)) {
    return `${base} - ${formatPeriodDay(start)}`
  }
  return `${base} - ${formatPeriodDay(start)} to ${formatPeriodDay(end)}`
}

/**
 * Build a reporting window from a preset.
 *
 * The returned range is always concrete. "This week" starts Monday at local
 * midnight; "Last week" is the previous Monday through the current Monday.
 * Rolling presets end at the moment the range is built.
 */
export function buildPeriodRange(preset, customStart = '', customEnd = '', now = new Date()) {
  const current = new Date(now)
  let start
  let end = current
  let base
  let includeDates = false

  switch (preset) {
    case '1h':
      start = new Date(current.getTime() - 3_600_000)
      base = 'Last 1 hour'
      break
    case '6h':
      start = new Date(current.getTime() - 6 * 3_600_000)
      base = 'Last 6 hours'
      break
    case '24h':
      start = new Date(current.getTime() - DAY_MS)
      base = 'Last 24 hours'
      break
    case 'this-week':
      start = startOfWeek(current)
      base = 'This week'
      includeDates = true
      break
    case 'last-week':
      end = startOfWeek(current)
      start = new Date(end.getTime() - 7 * DAY_MS)
      base = 'Last week'
      includeDates = true
      break
    case '30d':
      start = new Date(current.getTime() - 30 * DAY_MS)
      base = 'Last 30 days'
      break
    case '90d':
      start = new Date(current.getTime() - 90 * DAY_MS)
      base = 'Last 90 days'
      break
    case 'today':
      start = startOfDay(current)
      base = 'Today'
      break
    case 'custom': {
      const customEndDate = customEnd ? new Date(customEnd) : null
      const customStartDate = customStart ? new Date(customStart) : null
      end = customEndDate && !Number.isNaN(customEndDate.getTime())
        ? customEndDate
        : current
      start = customStartDate && !Number.isNaN(customStartDate.getTime())
        ? customStartDate
        : new Date(end.getTime() - 7 * DAY_MS)
      base = 'Custom'
      includeDates = true
      break
    }
    default:
      start = new Date(current.getTime() - 7 * DAY_MS)
      base = 'Last 7 days'
  }

  if (!(start instanceof Date) || Number.isNaN(start.getTime())) {
    start = new Date(current.getTime() - 7 * DAY_MS)
  }
  if (!(end instanceof Date) || Number.isNaN(end.getTime())) {
    end = current
  }
  if (start >= end) {
    end = new Date(start.getTime() + 60_000)
  }

  const days = Math.max(0.01, (end - start) / DAY_MS)
  return {
    start,
    end,
    startIso: start.toISOString(),
    endIso: end.toISOString(),
    days,
    label: rangeLabel(base, start, end, includeDates),
  }
}

export function usePeriodFilter(defaultPreset = '7d') {
  const preset = ref(defaultPreset)
  const customStart = ref('')
  const customEnd = ref('')
  const tick = ref(0)

  const range = computed(() => {
    tick.value // dependency: refresh() moves rolling windows forward
    return buildPeriodRange(preset.value, customStart.value, customEnd.value)
  })
  const label = computed(() => range.value.label)
  const days = computed(() => range.value.days)
  const isShort = computed(() => range.value.days < 7)

  function setPreset(next) {
    if (next === 'custom') {
      if (!customStart.value) {
        customStart.value = toLocalInput(new Date(Date.now() - 7 * DAY_MS))
      }
      if (!customEnd.value) {
        customEnd.value = toLocalInput(new Date())
      }
    }
    preset.value = next
    tick.value += 1
  }

  function setCustomStart(value) {
    customStart.value = value
    tick.value += 1
  }

  function setCustomEnd(value) {
    customEnd.value = value
    tick.value += 1
  }

  function refresh() {
    tick.value += 1
  }

  return {
    preset,
    customStart,
    customEnd,
    range,
    label,
    days,
    isShort,
    setPreset,
    setCustomStart,
    setCustomEnd,
    refresh,
  }
}
