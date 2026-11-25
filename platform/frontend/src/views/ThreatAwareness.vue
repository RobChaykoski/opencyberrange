<template>
  <div class="threat">
    <header class="threat__head">
      <p class="threat__eyebrow">Awareness, not telemetry</p>
      <h1>Threat map</h1>
      <p class="threat__lede">
        Explore where reported hostile addresses are concentrated in the current
        snapshot. The map is aggregated by country and feed. It is not a live
        attack map: no individual address, attack path, victim name, or post
        link is shown.
      </p>
    </header>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="threat__muted">Loading the current snapshot...</p>

    <template v-else-if="data">
      <section v-if="data.sample" class="threat__sample" role="status">
        <strong>Sample snapshot.</strong>
        The deployment has not refreshed the feed yet. An operator can run
        <code>scripts/fetch-threat-feed.py</code> on a host with feed and GeoIP
        access; the panel then shows dated aggregated counts.
      </section>

      <section class="threat__stats">
        <article>
          <span>Reported entries</span>
          <strong>{{ formatCount(data.totals.entries_reported) }}</strong>
          <p>Across {{ data.totals.categories }} feeds</p>
        </article>
        <article>
          <span>Countries seen</span>
          <strong>{{ data.totals.countries }}</strong>
          <p>{{ data.totals.buckets_suppressed }} small buckets suppressed</p>
        </article>
        <article>
          <span>Feed coverage</span>
          <strong>{{ formatShare(data.totals.coverage) }}</strong>
          <p>Of {{ formatCount(data.totals.entries_observed) }} observed entries</p>
        </article>
        <article>
          <span>Snapshot</span>
          <strong class="threat__date">{{ formatTime(data.generated_at) }}</strong>
          <p>{{ data.window_hours }}h window</p>
        </article>
      </section>

      <ThreatMap
        v-if="data.countries.length"
        :countries="data.countries"
        :entries-reported="data.totals.entries_reported"
        :generated-at="data.generated_at"
        :window-hours="data.window_hours"
      />

      <p
        v-if="!data.categories.length && !data.countries.length"
        class="threat__muted"
        role="status"
      >
        This snapshot has no aggregated rows yet. Refresh the feed on the
        operations host, then reload this page.
      </p>

      <div v-else class="threat__grid">
        <section v-if="data.categories.length" class="threat__card">
          <h2>What is being reported</h2>
          <p class="threat__muted">
            An entry can appear in more than one feed, so counts overlap. Feeds
            describe the kind of list an address appeared on, not a confirmed
            attack.
          </p>
          <ul class="threat__bars">
            <li v-for="row in data.categories" :key="row.id">
              <div class="threat__bar-head">
                <span>{{ row.label }}</span>
                <strong>{{ formatCount(row.count) }}</strong>
              </div>
              <div
                class="threat__track"
                role="progressbar"
                aria-valuemin="0"
                :aria-valuenow="row.count"
                :aria-valuemax="maxCategory"
                :aria-label="`${row.label}: ${formatCount(row.count)} entries`"
              >
                <span :style="{ width: barWidth(row.count, maxCategory) }"></span>
              </div>
              <span class="threat__share">{{ formatShare(row.share) }}</span>
            </li>
          </ul>
        </section>
      </div>

      <p v-if="ransomError" class="form-error" role="alert">{{ ransomError }}</p>

      <section v-if="ransom" class="threat__card">
        <h2>Ransomware activity</h2>
        <p class="threat__muted">
          Aggregated from public reporting. Group names and counts only; no
          victim, link, or cryptocurrency detail is shown.
        </p>
        <p v-if="ransom.sample" class="threat__inline-note">
          Sample snapshot. An operator can run
          <code>scripts/fetch-ransomware-feed.py</code> to refresh it.
        </p>

        <div class="threat__mini-stats">
          <div>
            <span>Posts · last {{ ransom.window_days }} days</span>
            <strong>{{ formatCount(ransom.totals.window_posts) }}</strong>
          </div>
          <div>
            <span>Posts · last 24 hours</span>
            <strong>{{ formatCount(ransom.totals.posts_24h) }}</strong>
          </div>
          <div>
            <span>Groups tracked</span>
            <strong>{{ formatCount(ransom.totals.groups) }}</strong>
          </div>
          <div>
            <span>Posts · all time</span>
            <strong>{{ formatCount(ransom.totals.posts_total) }}</strong>
          </div>
        </div>

        <ul class="threat__bars">
          <li v-for="row in visibleRansomGroups" :key="row.name">
            <div class="threat__bar-head">
              <span>{{ row.name }}</span>
              <strong>{{ formatCount(row.count) }}</strong>
            </div>
            <div
              class="threat__track"
              role="progressbar"
              aria-valuemin="0"
              :aria-valuenow="row.count"
              :aria-valuemax="maxRansomGroup"
              :aria-label="`${row.name}: ${formatCount(row.count)} posts`"
            >
              <span :style="{ width: barWidth(row.count, maxRansomGroup) }"></span>
            </div>
            <span class="threat__share">{{ formatShare(row.share) }}</span>
          </li>
        </ul>
        <button
          v-if="ransom.groups.length > 8"
          type="button"
          class="threat__more"
          :aria-expanded="showAllRansomGroups"
          @click="showAllRansomGroups = !showAllRansomGroups"
        >
          {{ showAllRansomGroups ? 'Show top 8 groups' : `Show all ${ransom.groups.length} groups` }}
        </button>

        <p class="threat__attribution">
          {{ ransom.source.attribution }}
          <a :href="ransom.source.url" target="_blank" rel="noopener noreferrer">
            {{ ransom.source.licence }}
          </a>
        </p>
      </section>

      <section class="threat__card threat__method">
        <h2>How to read this</h2>
        <ul>
          <li v-for="note in data.notes" :key="note">{{ note }}</li>
          <li>
            The map marker is the country where an address is registered. It is
            not proof that a person, group, or government in that country is
            responsible. Shared hosting, VPNs, Tor exits, and stale feed entries
            all distort the picture.
          </li>
          <li>
            Country attribution: {{ data.method.geoip === 'local-database'
              ? 'local GeoIP database'
              : 'not configured, so entries are counted as unknown' }}.
          </li>
          <li>
            Minimum bucket size: {{ data.method.minimum_bucket_size }}. Smaller
            buckets are not published, so the map never narrows down to a
            handful of hosts.
          </li>
        </ul>
        <p class="threat__attribution">
          {{ data.source.attribution }}
          <a v-if="data.source.url" :href="data.source.url" target="_blank" rel="noopener noreferrer">
            Source
          </a>
        </p>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '../api/axios'
import ThreatMap from '../components/ThreatMap.vue'

const data = ref(null)
const ransom = ref(null)
const error = ref('')
const ransomError = ref('')
const loading = ref(true)
const showAllRansomGroups = ref(false)

const numberFormat = new Intl.NumberFormat()

const maxCategory = computed(() =>
  Math.max(1, ...(data.value?.categories || []).map((row) => row.count)),
)
const maxRansomGroup = computed(() =>
  Math.max(1, ...(ransom.value?.groups || []).map((row) => row.count)),
)
const visibleRansomGroups = computed(() => {
  const groups = ransom.value?.groups || []
  return showAllRansomGroups.value ? groups : groups.slice(0, 8)
})

function formatCount(value) {
  return numberFormat.format(value || 0)
}

function formatShare(value) {
  return `${Math.round((value || 0) * 1000) / 10}%`
}

function formatTime(value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Unknown' : date.toLocaleString()
}

function barWidth(count, max) {
  return `${Math.min(100, Math.max(0, ((count || 0) / max) * 100))}%`
}

async function load() {
  loading.value = true
  error.value = ''
  ransomError.value = ''
  const [threatResult, ransomResult] = await Promise.allSettled([
    api.get('/threat-awareness'),
    api.get('/ransomware-activity'),
  ])
  if (threatResult.status === 'fulfilled') {
    data.value = threatResult.value.data
  } else {
    error.value =
      threatResult.reason?.response?.data?.detail ||
      'Could not load the threat-awareness snapshot.'
  }
  if (ransomResult.status === 'fulfilled') {
    ransom.value = ransomResult.value.data
  } else {
    ransomError.value =
      ransomResult.reason?.response?.data?.detail ||
      'Could not load the ransomware-activity snapshot.'
  }
  loading.value = false
}

onMounted(load)
</script>

<style scoped>
.threat {
  max-width: 1080px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  gap: 1.5rem;
  min-width: 0;
}

.threat__head {
  display: grid;
  gap: 0.35rem;
}

.threat__eyebrow {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent-text);
}

.threat__head h1 {
  margin: 0;
}

.threat__lede {
  margin: 0;
  max-width: 70ch;
  color: var(--text-secondary);
  line-height: 1.6;
}

.threat__muted {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.threat__sample {
  padding: 1rem 1.1rem;
  border: 1px solid var(--warning);
  border-radius: 10px;
  background: var(--warning-bg);
  color: var(--text-primary);
  line-height: 1.6;
}

.threat__sample code {
  padding: 0.1rem 0.35rem;
  border-radius: 6px;
  background: var(--bg-primary);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.85em;
  overflow-wrap: anywhere;
}

.threat__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
}

.threat__stats article {
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  min-width: 0;
}

.threat__stats span {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}

.threat__stats strong {
  display: block;
  margin: 0.35rem 0;
  font-size: 1.6rem;
  color: var(--text-primary);
}

.threat__stats p {
  margin: 0;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.threat__date {
  font-size: 1rem !important;
}

.threat__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 1rem;
}

.threat__card {
  padding: 1.1rem 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  min-width: 0;
}

.threat__card h2 {
  margin: 0 0 0.35rem;
  font-size: 1.15rem;
  color: var(--text-primary);
}

.threat__bars {
  list-style: none;
  margin: 0.85rem 0 0;
  padding: 0;
  display: grid;
  gap: 0.7rem;
}

.threat__bar-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  font-size: 0.88rem;
  color: var(--text-primary);
}

.threat__bar-head small {
  color: var(--text-muted);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.72rem;
}

.threat__track {
  height: 6px;
  margin: 0.3rem 0;
  border-radius: 999px;
  background: var(--accent-bg);
  overflow: hidden;
}

.threat__track span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: var(--accent);
}

.threat__share {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.threat__more {
  margin-top: 0.6rem;
  padding: 0.25rem 0;
  border: 0;
  background: none;
  color: var(--accent-text);
  font: inherit;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}

.threat__more:hover {
  text-decoration: underline;
}

.threat__inline-note {
  margin: 0.5rem 0 0;
  padding: 0.5rem 0.7rem;
  border-left: 3px solid var(--warning);
  background: var(--warning-bg);
  color: var(--text-primary);
  font-size: 0.85rem;
  line-height: 1.5;
}

.threat__inline-note code {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  overflow-wrap: anywhere;
}

.threat__mini-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 0.6rem;
  margin-top: 0.85rem;
}

.threat__mini-stats div {
  padding: 0.65rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.threat__mini-stats span {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}

.threat__mini-stats strong {
  display: block;
  margin-top: 0.2rem;
  font-size: 1.15rem;
  color: var(--text-primary);
}

.threat__method ul {
  margin: 0.6rem 0;
  padding-left: 1.1rem;
  display: grid;
  gap: 0.4rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.threat__attribution {
  margin: 0.6rem 0 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  overflow-wrap: anywhere;
}

.threat__attribution a {
  margin-left: 0.3rem;
  color: var(--accent-text);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.threat__attribution a:focus-visible,
.threat__sample a:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

@media (max-width: 640px) {
  .threat {
    padding: 1rem;
    gap: 1.25rem;
  }

  .threat__stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .threat__stats strong {
    font-size: 1.35rem;
  }

  .threat__date {
    font-size: 0.82rem !important;
    line-height: 1.35;
  }

  .threat__mini-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (prefers-reduced-motion: reduce) {
  .threat * {
    transition: none !important;
    animation: none !important;
  }
}
</style>
