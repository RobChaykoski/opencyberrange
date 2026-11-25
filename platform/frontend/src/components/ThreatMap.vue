<template>
  <section class="threat-map" aria-labelledby="threat-map-title">
    <header class="threat-map__head">
      <div>
        <p class="threat-map__eyebrow">Snapshot explorer</p>
        <h2 id="threat-map-title">Where the snapshot is concentrated</h2>
        <p class="threat-map__lede">
          Each marker is a country with reported hostile addresses in this
          snapshot. Marker size shows the number of entries. It is not a live
          attack map, and a country is where an address is registered, not where
          a person or an attack is.
        </p>
      </div>
      <div class="threat-map__stamp">
        <span class="threat-map__stamp-dot" aria-hidden="true"></span>
        <div>
          <strong>{{ snapshotLabel }}</strong>
          <span>{{ windowHours }}h window · not live</span>
        </div>
      </div>
    </header>

    <div class="threat-map__controls" role="group" aria-label="Map filters">
      <div class="threat-map__regions" role="group" aria-label="Filter by region">
        <button
          v-for="region in regionOptions"
          :key="region.id"
          type="button"
          class="threat-map__chip"
          :class="{ 'threat-map__chip--active': regionFilter === region.id }"
          :aria-pressed="regionFilter === region.id"
          @click="setRegion(region.id)"
        >
          {{ region.label }}
        </button>
      </div>
      <label class="threat-map__threshold">
        <span>Show</span>
        <select v-model.number="threshold">
          <option v-for="option in thresholdOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>
    </div>

    <p class="threat-map__count" role="status">
      Showing {{ activeRows.length }} of {{ rows.length }} countries
      <template v-if="regionFilter !== 'all'"> in {{ regionLabel(regionFilter) }}</template>
      with at least {{ formatCount(threshold) }} reported
      {{ threshold === 1 ? 'entry' : 'entries' }}.
    </p>

    <div class="threat-map__stage">
      <div class="threat-map__canvas" :class="{ 'threat-map__canvas--dimmed': !activeRows.length }">
        <svg
          class="threat-map__svg"
          :viewBox="`0 0 ${WORLD_WIDTH} ${WORLD_HEIGHT}`"
          role="group"
          aria-labelledby="threat-map-svg-title threat-map-svg-desc"
          @mouseleave="hoveredCode = null"
        >
          <title id="threat-map-svg-title">Reported hostile addresses by country</title>
          <desc id="threat-map-svg-desc">
            A bubble map. Larger markers mean more reported entries. Use the arrow
            keys to move between countries, Enter to select one, and Escape to
            clear the selection. The hotspot list below the map lists the same
            countries in order.
          </desc>

          <rect
            class="threat-map__ocean"
            x="0"
            y="0"
            :width="WORLD_WIDTH"
            :height="WORLD_HEIGHT"
            aria-hidden="true"
          />

          <g class="threat-map__grid" aria-hidden="true">
            <line
              v-for="lon in graticuleLongitudes"
              :key="`lon-${lon}`"
              :x1="lon + 180"
              y1="0"
              :x2="lon + 180"
              :y2="WORLD_HEIGHT"
            />
            <line
              v-for="lat in graticuleLatitudes"
              :key="`lat-${lat}`"
              x1="0"
              :y1="latY(lat)"
              :x2="WORLD_WIDTH"
              :y2="latY(lat)"
            />
            <line class="threat-map__equator" x1="0" :y1="latY(0)" :x2="WORLD_WIDTH" :y2="latY(0)" />
          </g>

          <path
            class="threat-map__land"
            :d="WORLD_LAND_PATH"
            aria-hidden="true"
          />

          <g class="threat-map__markers">
            <g
              v-for="row in markers"
              :key="row.code"
              class="threat-map__marker"
              :class="{
                'threat-map__marker--selected': row.code === selectedCode,
                'threat-map__marker--muted': selectedCode && row.code !== selectedCode,
              }"
              role="button"
              :tabindex="row.code === rovingCode ? 0 : -1"
              :aria-label="markerLabel(row)"
              :aria-pressed="row.code === selectedCode"
              :ref="(element) => setMarkerRef(row.code, element)"
              @click="select(row)"
              @mouseenter="hoveredCode = row.code"
              @focus="onMarkerFocus(row)"
              @blur="hoveredCode = null"
              @keydown="onMarkerKeydown($event, row)"
            >
              <title>{{ markerLabel(row) }}</title>
              <circle
                v-if="row.code === focusedCode"
                class="threat-map__focus-ring"
                :cx="row.x"
                :cy="row.y"
                :r="row.radius + 1.4"
              />
              <circle
                class="threat-map__halo"
                :cx="row.x"
                :cy="row.y"
                :r="row.radius + 1.1"
                :opacity="row.code === selectedCode ? 0.55 : 0.2"
              />
              <circle
                v-if="row.code === selectedCode"
                class="threat-map__ping"
                :cx="row.x"
                :cy="row.y"
                :r="row.radius + 1.4"
              />
              <circle
                class="threat-map__dot"
                :cx="row.x"
                :cy="row.y"
                :r="row.radius"
                :opacity="row.opacity"
              />
              <circle
                v-if="topThreeCodes.has(row.code)"
                class="threat-map__top-ring"
                :cx="row.x"
                :cy="row.y"
                :r="row.radius + 0.7"
              />
              <circle
                class="threat-map__hit"
                :cx="row.x"
                :cy="row.y"
                :r="row.hitRadius"
              />
            </g>
          </g>

          <g class="threat-map__labels" aria-hidden="true">
            <text
              v-for="row in topThree"
              :key="`label-${row.code}`"
              :x="row.x"
              :y="labelY(row)"
              class="threat-map__label"
            >{{ row.code }}</text>
          </g>
        </svg>

        <p v-if="!activeRows.length" class="threat-map__empty" role="status">
          No countries match these filters. Lower the minimum or choose another
          region.
        </p>

        <div
          v-if="hoveredRow"
          class="threat-map__tip"
          :class="{ 'threat-map__tip--below': hoveredRow.y < 24 }"
          :style="tipStyle"
          aria-hidden="true"
        >
          <strong>{{ hoveredRow.label }}</strong>
          <span>{{ formatCount(hoveredRow.count) }} entries · {{ formatShare(hoveredRow.share) }}</span>
        </div>
      </div>

      <aside class="threat-map__detail" aria-live="polite">
        <template v-if="selectedRow">
          <p class="threat-map__eyebrow">Selected country</p>
          <h3>{{ selectedRow.label }} <span>{{ selectedRow.code }}</span></h3>
          <p class="threat-map__big">{{ formatCount(selectedRow.count) }}</p>
          <p class="threat-map__share">
            {{ formatShare(selectedRow.share) }} of reported entries ·
            rank {{ selectedRow.rank }} of {{ rows.length }}
          </p>
          <div class="threat-map__bar" aria-hidden="true">
            <span :style="{ width: barWidth(selectedRow.count) }"></span>
          </div>
          <p class="threat-map__note">
            A country is where an address is registered, not where a person or
            an attack is. Shared hosting, VPNs, and stale feed entries distort
            this view.
          </p>
          <a
            :href="openStreetMapUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="threat-map__external"
          >
            View on OpenStreetMap
          </a>
          <p class="threat-map__note threat-map__note--tight">
            Opens openstreetmap.org in a new tab. Your browser contacts that
            site; the platform does not fetch map tiles.
          </p>
          <button type="button" class="btn btn--secondary btn--sm" @click="clearSelection">
            Clear selection
          </button>
        </template>
        <template v-else>
          <p class="threat-map__eyebrow">How to explore</p>
          <h3>Read the map</h3>
          <ul class="threat-map__legend">
            <li><span class="threat-map__legend-dot threat-map__legend-dot--big"></span>More reported entries</li>
            <li><span class="threat-map__legend-dot"></span>Fewer reported entries</li>
            <li><span class="threat-map__legend-dot threat-map__legend-dot--selected"></span>Selected country</li>
            <li><span class="threat-map__legend-ring"></span>Top three hotspots</li>
          </ul>
          <p class="threat-map__note">
            Hover or focus a marker, or use the hotspot list, to see the count
            and share. Nothing here identifies a learner, a lab, or a host.
          </p>
          <dl class="threat-map__mini">
            <div>
              <dt>Entries reported</dt>
              <dd>{{ formatCount(entriesReported) }}</dd>
            </div>
            <div>
              <dt>Countries in snapshot</dt>
              <dd>{{ formatCount(rows.length) }}</dd>
            </div>
            <div>
              <dt>Top region</dt>
              <dd>{{ topRegion.label }} · {{ formatShare(topRegion.share) }}</dd>
            </div>
          </dl>
        </template>
      </aside>
    </div>

    <div class="threat-map__lower">
      <section class="threat-map__hotspots" aria-labelledby="threat-map-hotspots-title">
        <header>
          <div>
            <p class="threat-map__eyebrow">Select a row</p>
            <h3 id="threat-map-hotspots-title">Hotspots</h3>
          </div>
          <span class="threat-map__muted">{{ activeRows.length }} in view</span>
        </header>
        <ol v-if="visibleHotspots.length" class="threat-map__list">
          <li v-for="row in visibleHotspots" :key="row.code">
            <button
              type="button"
              class="threat-map__row"
              :class="{ 'threat-map__row--active': row.code === selectedCode }"
              :aria-pressed="row.code === selectedCode"
              @click="select(row)"
              @mouseenter="hoveredCode = row.code"
              @mouseleave="hoveredCode = null"
            >
              <span class="threat-map__rank">{{ row.rank }}</span>
              <span class="threat-map__name">{{ row.label }} <small>{{ row.code }}</small></span>
              <span class="threat-map__row-track" aria-hidden="true">
                <span :style="{ width: barWidth(row.count) }"></span>
              </span>
              <strong>{{ formatCount(row.count) }}</strong>
            </button>
          </li>
        </ol>
        <p v-else class="threat-map__muted">No hotspots match these filters.</p>
        <button
          v-if="activeRows.length > hotspotLimit"
          type="button"
          class="threat-map__more"
          :aria-expanded="showAllHotspots"
          @click="showAllHotspots = !showAllHotspots"
        >
          {{ showAllHotspots ? 'Show top 8' : `Show all ${activeRows.length} countries` }}
        </button>
      </section>

      <ThreatMapQuiz
        v-if="quizReady"
        :countries="rows"
        :entries-reported="entriesReported"
        :regions="regionTotals"
      />
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'

import {
  COUNTRY_CENTROIDS,
  WORLD_HEIGHT,
  WORLD_LAND_PATH,
  WORLD_WIDTH,
} from '../data/worldMap'
import ThreatMapQuiz from './ThreatMapQuiz.vue'

const props = defineProps({
  countries: {
    type: Array,
    default: () => [],
  },
  entriesReported: {
    type: Number,
    default: 0,
  },
  generatedAt: {
    type: String,
    default: '',
  },
  windowHours: {
    type: Number,
    default: 24,
  },
})

const REGION_LABELS = {
  Americas: 'Americas',
  Europe: 'Europe',
  Africa: 'Africa',
  Asia: 'Asia',
  Oceania: 'Oceania',
  Other: 'Other',
}

const thresholdOptions = [
  { value: 1, label: 'All countries' },
  { value: 100, label: '100+ entries' },
  { value: 1000, label: '1,000+ entries' },
  { value: 10000, label: '10,000+ entries' },
]

const threshold = ref(1)
const regionFilter = ref('all')
const selectedCode = ref('')
const hoveredCode = ref('')
const focusedCode = ref('')
const showAllHotspots = ref(false)
const hotspotLimit = 8
const markerRefs = new Map()

const numberFormat = new Intl.NumberFormat()

function formatCount(value) {
  return numberFormat.format(value || 0)
}

function formatShare(value) {
  return `${Math.round((value || 0) * 1000) / 10}%`
}

function regionLabel(id) {
  return id === 'all' ? 'all regions' : REGION_LABELS[id] || id
}

const graticuleLongitudes = [-150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150]
const graticuleLatitudes = [-45, -15, 15, 45, 75]

function latY(lat) {
  return Math.max(0, Math.min(WORLD_HEIGHT, 84 - lat))
}

const snapshotLabel = computed(() => {
  if (!props.generatedAt) return 'Current snapshot'
  const date = new Date(props.generatedAt)
  if (Number.isNaN(date.getTime())) return 'Current snapshot'
  return date.toLocaleString([], {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
})

const rows = computed(() => {
  const source = (props.countries || [])
    .map((row) => {
      const centroid = COUNTRY_CENTROIDS[row.code]
      if (!centroid) return null
      const [lon, lat, region] = centroid
      return {
        code: row.code,
        label: row.label || row.code,
        count: Number(row.count) || 0,
        share: Number(row.share) || 0,
        region,
        lon,
        lat,
        x: Math.max(0, Math.min(WORLD_WIDTH, lon + 180)),
        y: latY(lat),
      }
    })
    .filter((row) => row && row.count > 0)

  source.sort((a, b) => b.count - a.count || a.label.localeCompare(b.label))
  const max = source.length ? source[0].count : 1
  return source.map((row, index) => {
    const ratio = Math.sqrt(row.count / max)
    return {
      ...row,
      rank: index + 1,
      radius: 2.2 + 9.8 * ratio,
      hitRadius: Math.max(2.2 + 9.8 * ratio + 5, 6),
      opacity: 0.38 + 0.58 * ratio,
    }
  })
})

const maxCount = computed(() => (rows.value.length ? rows.value[0].count : 1))

const topThree = computed(() => activeRows.value.slice(0, 3))
const topThreeCodes = computed(() => new Set(topThree.value.map((row) => row.code)))

const regionOptions = computed(() => {
  const present = new Set(rows.value.map((row) => row.region))
  const options = [{ id: 'all', label: 'All regions' }]
  for (const id of ['Americas', 'Europe', 'Africa', 'Asia', 'Oceania', 'Other']) {
    if (present.has(id)) options.push({ id, label: REGION_LABELS[id] })
  }
  return options
})

const regionTotals = computed(() => {
  const totals = new Map()
  for (const row of rows.value) {
    totals.set(row.region, (totals.get(row.region) || 0) + row.count)
  }
  const reported = props.entriesReported || rows.value.reduce((sum, row) => sum + row.count, 0)
  return [...totals.entries()]
    .map(([id, count]) => ({
      id,
      label: REGION_LABELS[id] || id,
      count,
      share: reported ? count / reported : 0,
    }))
    .sort((a, b) => b.count - a.count)
})

const topRegion = computed(() => regionTotals.value[0] || { label: 'Unknown', share: 0 })

const activeRows = computed(() => rows.value.filter((row) => {
  if (row.count < threshold.value) return false
  if (regionFilter.value !== 'all' && row.region !== regionFilter.value) return false
  return true
}))

const visibleHotspots = computed(() => (
  showAllHotspots.value ? activeRows.value : activeRows.value.slice(0, hotspotLimit)
))

const markers = computed(() => {
  if (!selectedCode.value) return activeRows.value
  const selected = activeRows.value.find((row) => row.code === selectedCode.value)
  if (!selected) return activeRows.value
  return [selected, ...activeRows.value.filter((row) => row.code !== selected.code)]
})

const selectedRow = computed(() => (
  rows.value.find((row) => row.code === selectedCode.value) || null
))
const hoveredRow = computed(() => (
  markers.value.find((row) => row.code === hoveredCode.value) || null
))

const openStreetMapUrl = computed(() => {
  if (!selectedRow.value) return ''
  const lat = selectedRow.value.lat.toFixed(2)
  const lon = selectedRow.value.lon.toFixed(2)
  return `https://www.openstreetmap.org/#map=4/${lat}/${lon}`
})

const rovingCode = computed(() => {
  if (focusedCode.value && activeRows.value.some((row) => row.code === focusedCode.value)) {
    return focusedCode.value
  }
  return activeRows.value[0]?.code || ''
})

const quizReady = computed(() => rows.value.length >= 4 && regionTotals.value.length >= 2)

const tipStyle = computed(() => {
  if (!hoveredRow.value) return {}
  const x = Math.max(9, Math.min(91, (hoveredRow.value.x / WORLD_WIDTH) * 100))
  const y = (hoveredRow.value.y / WORLD_HEIGHT) * 100
  return { left: `${x}%`, top: `${y}%` }
})

function barWidth(count) {
  const max = maxCount.value || 1
  return `${Math.max(3, Math.min(100, Math.round((count / max) * 100)))}%`
}

function labelY(row) {
  return row.y < 12 ? row.y + row.radius + 6 : row.y - row.radius - 2.5
}

function markerLabel(row) {
  return `${row.label}: ${formatCount(row.count)} reported entries, ${formatShare(row.share)} of the snapshot. ${row.region}.`
}

function setMarkerRef(code, element) {
  if (element) markerRefs.set(code, element)
  else markerRefs.delete(code)
}

function select(row) {
  selectedCode.value = selectedCode.value === row.code ? '' : row.code
}

function onMarkerFocus(row) {
  focusedCode.value = row.code
  hoveredCode.value = row.code
}

function clearSelection() {
  selectedCode.value = ''
}

function setRegion(id) {
  regionFilter.value = id
  showAllHotspots.value = false
}

function focusMarker(code) {
  focusedCode.value = code
  hoveredCode.value = code
  nextTick(() => {
    const element = markerRefs.get(code)
    if (element && typeof element.focus === 'function') element.focus()
  })
}

function onMarkerKeydown(event, row) {
  const list = activeRows.value
  const index = list.findIndex((item) => item.code === row.code)
  if (index === -1) return
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    select(row)
    return
  }
  if (event.key === 'Escape') {
    event.preventDefault()
    clearSelection()
    return
  }
  if (event.key === 'Home') {
    event.preventDefault()
    focusMarker(list[0].code)
    return
  }
  if (event.key === 'End') {
    event.preventDefault()
    focusMarker(list[list.length - 1].code)
    return
  }
  const step = event.key === 'ArrowRight' || event.key === 'ArrowDown'
    ? 1
    : event.key === 'ArrowLeft' || event.key === 'ArrowUp'
      ? -1
      : 0
  if (!step) return
  event.preventDefault()
  const next = (index + step + list.length) % list.length
  focusMarker(list[next].code)
}
</script>

<style scoped>
.threat-map {
  display: grid;
  gap: 1rem;
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
  min-width: 0;
}

.threat-map__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.threat-map__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent-text);
}

.threat-map__head h2 {
  margin: 0 0 0.35rem;
  font-size: 1.3rem;
  color: var(--text-primary);
}

.threat-map__lede {
  margin: 0;
  max-width: 78ch;
  color: var(--text-secondary);
  line-height: 1.55;
  font-size: 0.9rem;
}

.threat-map__stamp {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  white-space: nowrap;
}

.threat-map__stamp-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--warning);
  box-shadow: 0 0 0 4px var(--warning-bg);
}

.threat-map__stamp strong {
  display: block;
  font-size: 0.82rem;
  color: var(--text-primary);
}

.threat-map__stamp span {
  display: block;
  font-size: 0.7rem;
  color: var(--text-muted);
}

.threat-map__controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.threat-map__regions {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.threat-map__chip {
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 999px;
  padding: 0.3rem 0.7rem;
  font: inherit;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.threat-map__chip:hover,
.threat-map__chip:focus-visible {
  border-color: var(--accent);
  color: var(--text-primary);
}

.threat-map__chip--active {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--accent-text);
}

.threat-map__threshold {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.threat-map__threshold select {
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  border-radius: 6px;
  padding: 0.3rem 0.45rem;
  font: inherit;
  font-size: 0.78rem;
}

.threat-map__count {
  margin: 0;
  font-size: 0.78rem;
  color: var(--text-muted);
}

.threat-map__stage {
  display: grid;
  grid-template-columns: minmax(0, 1.9fr) minmax(220px, 1fr);
  gap: 1rem;
  align-items: start;
}

.threat-map__canvas {
  position: relative;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    radial-gradient(ellipse at 28% 18%, rgba(37, 99, 235, 0.16), transparent 55%),
    var(--bg-primary);
  overflow: hidden;
}

.threat-map__canvas--dimmed {
  opacity: 0.65;
}

.threat-map__svg {
  display: block;
  width: 100%;
  height: auto;
  min-height: 150px;
}

.threat-map__ocean {
  fill: transparent;
}

.threat-map__grid line {
  stroke: var(--border-color);
  stroke-width: 0.35;
  stroke-dasharray: 1 2;
  opacity: 0.55;
  vector-effect: non-scaling-stroke;
}

.threat-map__grid .threat-map__equator {
  stroke: var(--accent);
  opacity: 0.25;
  stroke-dasharray: none;
}

.threat-map__land {
  fill: var(--bg-tertiary);
  fill-opacity: 0.72;
  stroke: var(--border-color);
  stroke-width: 0.35;
  stroke-opacity: 0.8;
  vector-effect: non-scaling-stroke;
}

.threat-map__marker {
  cursor: pointer;
  outline: none;
}

.threat-map__marker--muted {
  opacity: 0.42;
}

.threat-map__hit {
  fill: transparent;
}

.threat-map__dot {
  fill: var(--accent-text);
  stroke: var(--bg-primary);
  stroke-width: 0.35;
  vector-effect: non-scaling-stroke;
}

.threat-map__marker--selected .threat-map__dot {
  fill: var(--warning);
  stroke: var(--text-primary);
  stroke-width: 0.5;
}

.threat-map__halo {
  fill: var(--accent);
  opacity: 0.2;
}

.threat-map__marker--selected .threat-map__halo {
  fill: var(--warning);
  opacity: 0.35;
}

.threat-map__top-ring {
  fill: none;
  stroke: var(--accent-text);
  stroke-width: 0.4;
  stroke-dasharray: 1 1;
  opacity: 0.9;
  vector-effect: non-scaling-stroke;
}

.threat-map__ping {
  fill: none;
  stroke: var(--warning);
  stroke-width: 0.5;
  transform-box: fill-box;
  transform-origin: center;
  animation: threat-map-ping 1.8s ease-out infinite;
  vector-effect: non-scaling-stroke;
  pointer-events: none;
}

@keyframes threat-map-ping {
  0% {
    transform: scale(1);
    opacity: 0.75;
  }
  100% {
    transform: scale(2.6);
    opacity: 0;
  }
}

.threat-map__focus-ring {
  fill: none;
  stroke: var(--text-primary);
  stroke-width: 0.6;
  vector-effect: non-scaling-stroke;
}

.threat-map__label {
  fill: var(--text-primary);
  font-size: 4.4px;
  font-weight: 700;
  text-anchor: middle;
  letter-spacing: 0.08em;
  paint-order: stroke;
  stroke: var(--bg-primary);
  stroke-width: 1.2px;
  stroke-linejoin: round;
}

.threat-map__tip {
  position: absolute;
  transform: translate(-50%, calc(-100% - 8px));
  pointer-events: none;
  padding: 0.4rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.28);
  white-space: nowrap;
  z-index: 2;
}

.threat-map__tip--below {
  transform: translate(-50%, 10px);
}

.threat-map__tip strong {
  display: block;
  font-size: 0.78rem;
  color: var(--text-primary);
}

.threat-map__tip span {
  display: block;
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.threat-map__empty {
  position: absolute;
  inset: 0;
  margin: 0;
  display: grid;
  place-items: center;
  padding: 1rem;
  text-align: center;
  color: var(--text-secondary);
  background: color-mix(in srgb, var(--bg-primary) 72%, transparent);
}

.threat-map__detail {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
  min-width: 0;
}

.threat-map__detail h3 {
  margin: 0;
  font-size: 1.15rem;
  color: var(--text-primary);
}

.threat-map__detail h3 span {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.08em;
}

.threat-map__big {
  margin: 0.5rem 0 0.15rem;
  font-size: 1.9rem;
  font-weight: 800;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.threat-map__share {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.threat-map__bar {
  height: 6px;
  margin: 0.7rem 0;
  border-radius: 999px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.threat-map__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}

.threat-map__note {
  margin: 0.7rem 0;
  font-size: 0.78rem;
  line-height: 1.55;
  color: var(--text-muted);
}

.threat-map__note--tight {
  margin: 0.35rem 0 0.7rem;
  font-size: 0.72rem;
}

.threat-map__external {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--accent-text);
  font-size: 0.8rem;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.threat-map__external:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.threat-map__legend {
  list-style: none;
  margin: 0.75rem 0;
  padding: 0;
  display: grid;
  gap: 0.45rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.threat-map__legend li {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.threat-map__legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-text);
  flex-shrink: 0;
}

.threat-map__legend-dot--big {
  width: 14px;
  height: 14px;
}

.threat-map__legend-dot--selected {
  background: var(--warning);
}

.threat-map__legend-ring {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px dashed var(--accent-text);
  flex-shrink: 0;
}

.threat-map__mini {
  display: grid;
  gap: 0.45rem;
  margin: 0.9rem 0 0;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border-color);
}

.threat-map__mini div {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.78rem;
}

.threat-map__mini dt {
  color: var(--text-muted);
}

.threat-map__mini dd {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
  text-align: right;
}

.threat-map__lower {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(240px, 1fr);
  gap: 1rem;
  align-items: start;
}

.threat-map__hotspots {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
  min-width: 0;
}

.threat-map__hotspots header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.threat-map__hotspots h3 {
  margin: 0;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.threat-map__muted {
  color: var(--text-muted);
  font-size: 0.78rem;
}

.threat-map__list {
  list-style: none;
  margin: 0.7rem 0 0;
  padding: 0;
  display: grid;
  gap: 0.25rem;
}

.threat-map__row {
  display: grid;
  grid-template-columns: 2rem minmax(0, 1.4fr) minmax(60px, 1fr) auto;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.38rem 0.45rem;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: var(--text-primary);
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.threat-map__row:hover,
.threat-map__row:focus-visible {
  background: var(--bg-secondary);
  border-color: var(--border-color);
}

.threat-map__row--active {
  background: var(--accent-bg);
  border-color: var(--accent);
}

.threat-map__rank {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.threat-map__name {
  font-size: 0.8rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.threat-map__name small {
  color: var(--text-muted);
  font-size: 0.68rem;
  letter-spacing: 0.06em;
}

.threat-map__row-track {
  height: 5px;
  border-radius: 999px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.threat-map__row-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}

.threat-map__row strong {
  font-size: 0.78rem;
  font-variant-numeric: tabular-nums;
}

.threat-map__more {
  margin-top: 0.6rem;
  border: 0;
  background: none;
  color: var(--accent-text);
  font: inherit;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem 0;
}

.threat-map__more:hover {
  text-decoration: underline;
}

@media (max-width: 900px) {
  .threat-map__stage,
  .threat-map__lower {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 640px) {
  .threat-map {
    padding: 0.9rem;
  }
  .threat-map__head {
    gap: 0.6rem;
  }
  .threat-map__stamp {
    white-space: normal;
  }
  .threat-map__svg {
    min-height: 120px;
  }
  .threat-map__label {
    display: none;
  }
  .threat-map__row {
    grid-template-columns: 1.6rem minmax(0, 1fr) auto;
  }
  .threat-map__row-track {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .threat-map * {
    transition: none !important;
    animation: none !important;
  }
}
</style>
