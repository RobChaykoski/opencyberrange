<template>
  <div class="threat">
    <header class="threat__head">
      <p class="threat__eyebrow">Awareness, not telemetry</p>
      <h1>Global threat awareness</h1>
      <p class="threat__lede">
        Where hostile addresses are concentrated, aggregated by country and feed.
        This is a periodic snapshot, not a live attack map. No individual address
        or attack path is shown.
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
          <span>Entries reported</span>
          <strong>{{ formatCount(data.totals.entries_reported) }}</strong>
          <p>Across {{ data.totals.categories }} feeds</p>
        </article>
        <article>
          <span>Countries</span>
          <strong>{{ data.totals.countries }}</strong>
          <p>{{ data.totals.buckets_suppressed }} small buckets suppressed</p>
        </article>
        <article>
          <span>Coverage</span>
          <strong>{{ formatShare(data.totals.coverage) }}</strong>
          <p>Of {{ formatCount(data.totals.entries_observed) }} observed entries</p>
        </article>
        <article>
          <span>Snapshot</span>
          <strong class="threat__date">{{ formatTime(data.generated_at) }}</strong>
          <p>{{ data.window_hours }}h window</p>
        </article>
      </section>

      <div class="threat__grid">
        <section class="threat__card">
          <h2>By feed</h2>
          <p class="threat__muted">
            An entry can appear in more than one feed, so counts overlap.
          </p>
          <ul class="threat__bars">
            <li v-for="row in data.categories" :key="row.id">
              <div class="threat__bar-head">
                <span>{{ row.label }}</span>
                <strong>{{ formatCount(row.count) }}</strong>
              </div>
              <div class="threat__track" aria-hidden="true">
                <span :style="{ width: barWidth(row.share) }"></span>
              </div>
              <span class="threat__share">{{ formatShare(row.share) }}</span>
            </li>
          </ul>
        </section>

        <section class="threat__card">
          <h2>By country</h2>
          <p class="threat__muted">
            Aggregated counts only. A country with a small count is suppressed.
          </p>
          <ul class="threat__bars">
            <li v-for="row in data.countries" :key="row.code">
              <div class="threat__bar-head">
                <span>{{ row.label }} <small>{{ row.code }}</small></span>
                <strong>{{ formatCount(row.count) }}</strong>
              </div>
              <div class="threat__track" aria-hidden="true">
                <span :style="{ width: barWidth(row.share) }"></span>
              </div>
              <span class="threat__share">{{ formatShare(row.share) }}</span>
            </li>
          </ul>
        </section>
      </div>

      <section class="threat__card threat__method">
        <h2>How to read this</h2>
        <ul>
          <li v-for="note in data.notes" :key="note">{{ note }}</li>
          <li>
            Country attribution: {{ data.method.geoip === 'local-database'
              ? 'local GeoIP database'
              : 'not configured, so entries are counted as unknown' }}.
          </li>
          <li>
            Minimum bucket size: {{ data.method.minimum_bucket_size }}. Smaller
            buckets are not published.
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
import { onMounted, ref } from 'vue'

import api from '../api/axios'

const data = ref(null)
const error = ref('')
const loading = ref(true)

const numberFormat = new Intl.NumberFormat()

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

function barWidth(share) {
  return `${Math.min(100, Math.max(0, (share || 0) * 100))}%`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/threat-awareness')
    data.value = response.data
  } catch (err) {
    error.value =
      err.response?.data?.detail || 'Could not load the threat-awareness snapshot.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.threat {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1.25rem;
}

.threat__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.threat__head h1 {
  margin: 0 0 0.5rem;
}

.threat__lede {
  margin: 0;
  max-width: 70ch;
  color: var(--muted);
}

.threat__muted {
  color: var(--muted);
}

.threat__sample {
  padding: 0.9rem 1rem;
  border: 1px solid var(--warning);
  border-radius: 10px;
  background: color-mix(in srgb, var(--warning) 12%, transparent);
  line-height: 1.5;
}

.threat__sample code {
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  background: var(--panel);
}

.threat__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
}

.threat__stats article {
  padding: 0.9rem 1rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--panel);
}

.threat__stats span {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}

.threat__stats strong {
  display: block;
  margin: 0.25rem 0;
  font-size: 1.6rem;
}

.threat__stats p {
  margin: 0;
  font-size: 0.82rem;
  color: var(--muted);
}

.threat__date {
  font-size: 1rem !important;
}

.threat__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.threat__card {
  padding: 1rem 1.1rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--panel);
}

.threat__card h2 {
  margin: 0 0 0.35rem;
  font-size: 1.05rem;
}

.threat__bars {
  list-style: none;
  margin: 0.75rem 0 0;
  padding: 0;
  display: grid;
  gap: 0.65rem;
}

.threat__bar-head {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.88rem;
}

.threat__bar-head small {
  color: var(--muted);
  font-size: 0.72rem;
}

.threat__track {
  height: 6px;
  margin: 0.25rem 0;
  border-radius: 999px;
  background: var(--accent-soft);
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
  color: var(--muted);
}

.threat__method ul {
  margin: 0.5rem 0;
  padding-left: 1.1rem;
  display: grid;
  gap: 0.35rem;
  color: var(--muted);
}

.threat__attribution {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
  color: var(--muted);
}

.threat__attribution a {
  margin-left: 0.3rem;
  color: var(--accent);
}
</style>
