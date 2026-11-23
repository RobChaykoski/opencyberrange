<template>
  <section class="dna-v3" aria-labelledby="dna-v3-title">
    <header class="dna-v3__head">
      <div>
        <p class="dna-v3__eyebrow">Cyber DNA v3</p>
        <h2 id="dna-v3-title" class="section-title">Career affinity</h2>
        <p class="dna-v3__lead">
          A descriptive read of the competencies your practice covers, the behaviors you
          show, and the pathways that fit. It is not a probability, a ranking, or a hiring
          prediction.
        </p>
      </div>
      <span v-if="data" class="dna-v3__version" :title="`Version ${data.version}`">
        v{{ data.version }}
      </span>
    </header>

    <p v-if="state === 'loading'" class="dna-v3__status" role="status">
      Loading your Cyber DNA...
    </p>

    <article v-else-if="state === 'consent'" class="dna-v3__notice" role="status">
      <h3>Cyber DNA is off</h3>
      <p>
        Cyber DNA turns your practice into derived career signals. It is opt-in, private
        to you, and never shared with employers. Turning it off deletes its derived data;
        your exercises, certificates, and achievements stay.
      </p>
      <router-link
        class="btn btn--primary btn--sm"
        :to="{ path: '/profile', query: { tab: 'security' } }"
      >
        Review privacy settings
      </router-link>
    </article>

    <article v-else-if="state === 'denied'" class="dna-v3__notice">
      <h3>Career affinity is scoped to learner accounts</h3>
      <p>
        Your current role does not include this learner view. An administrator can grant
        it in the role settings.
      </p>
    </article>

    <article v-else-if="state === 'disabled'" class="dna-v3__notice">
      <h3>Cyber DNA v3 is not enabled</h3>
      <p>
        An administrator can enable it in Settings &rarr; Features. The rest of your
        profile is unaffected.
      </p>
    </article>

    <div v-else-if="state === 'error'" class="dna-v3__notice" role="alert">
      <h3>Cyber DNA could not load</h3>
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary btn--sm" @click="load">
        Try again
      </button>
    </div>

    <template v-else-if="data">
      <div class="dna-v3__stats" aria-label="Evidence summary">
        <div>
          <strong>{{ evidenceItems }}</strong>
          <span>observations</span>
        </div>
        <div>
          <strong>{{ competenciesWithEvidence }}</strong>
          <span>competencies</span>
        </div>
        <div>
          <strong>{{ gate.labs.have }}</strong>
          <span>labs</span>
        </div>
        <div>
          <strong>{{ gate.domains.have }}</strong>
          <span>domains</span>
        </div>
      </div>

      <section class="dna-card" aria-labelledby="dna-gate-title">
        <div class="dna-card__head">
          <div>
            <h3 id="dna-gate-title">Affinity gate</h3>
            <p class="dna-v3__meta">
              Affinity unlocks at 30 labs, 3 domains, and 100 observations.
            </p>
          </div>
          <span
            class="dna-badge"
            :class="gate.available ? 'dna-badge--success' : 'dna-badge--warning'"
          >
            {{ gate.available ? 'Unlocked' : 'More evidence needed' }}
          </span>
        </div>

        <div class="dna-gate">
          <div v-for="item in gateItems" :key="item.key" class="dna-gate__item">
            <div class="dna-gate__label">
              <span>{{ item.label }}</span>
              <span>{{ item.have }} / {{ item.need }}</span>
            </div>
            <div
              class="dna-gate__track"
              role="progressbar"
              :aria-label="`${item.label}: ${item.have} of ${item.need}`"
              :aria-valuenow="item.percent"
              :aria-valuetext="`${item.have} of ${item.need} ${item.label.toLowerCase()}`"
              aria-valuemin="0"
              aria-valuemax="100"
            >
              <span :style="{ width: item.percent + '%' }"></span>
            </div>
          </div>
        </div>

        <p v-if="!gate.available" class="dna-v3__meta">
          The evidence below is still yours. Affinity hides itself until every threshold
          is met so the score cannot overstate a small sample.
        </p>
      </section>

      <section
        v-if="gate.available && pathways.length"
        class="dna-card"
        aria-labelledby="dna-pathways-title"
      >
        <div class="dna-card__head">
          <div>
            <h3 id="dna-pathways-title">Pathways that fit your practice</h3>
            <p class="dna-v3__meta">
              Ordered by affinity. Open a pathway to see what supports it and what to
              build next.
            </p>
          </div>
          <span class="dna-badge dna-badge--neutral">{{ pathways.length }} pathways</span>
        </div>

        <div class="dna-pathways">
          <article
            v-for="(pathway, index) in visiblePathways"
            :key="pathway.pathway_id"
            class="dna-pathway"
          >
            <header class="dna-pathway__head">
              <div>
                <p class="dna-pathway__rank">#{{ index + 1 }}</p>
                <h4>{{ pathway.title }}</h4>
                <p class="dna-v3__meta">
                  {{ labelize(pathway.family) }} &middot;
                  {{ pathway.evidence_count }} critical competencies with evidence
                </p>
              </div>
              <div class="dna-pathway__score">
                <strong>{{ pathway.affinity }}</strong>
                <span>affinity &middot; {{ pathway.confidence_band }} confidence</span>
              </div>
            </header>

            <div class="dna-pathway__components" aria-label="Score components">
              <span
                v-for="(value, key) in pathway.components"
                :key="key"
                class="dna-component"
                :class="{ 'dna-component--empty': value === null }"
              >
                {{ componentLabel(key) }}
                <strong>{{ percent(value) }}</strong>
              </span>
            </div>

            <div class="dna-pathway__columns">
              <div>
                <p class="dna-pathway__label">Strongest evidence</p>
                <ul class="dna-pathway__list">
                  <li v-for="item in pathway.strongest_competencies" :key="item">
                    {{ item }}
                  </li>
                </ul>
              </div>
              <div>
                <p class="dna-pathway__label">Build next</p>
                <ul class="dna-pathway__list">
                  <li v-for="item in pathway.gaps" :key="item">{{ item }}</li>
                </ul>
              </div>
            </div>

            <details class="dna-pathway__why">
              <summary>Why this score</summary>
              <ul>
                <li v-for="line in pathway.why" :key="line">{{ line }}</li>
              </ul>
            </details>
          </article>
        </div>

        <button
          v-if="pathways.length > 3"
          type="button"
          class="btn btn--secondary btn--sm"
          :aria-expanded="showAllPathways"
          @click="showAllPathways = !showAllPathways"
        >
          {{ showAllPathways ? 'Show top 3' : `Show all ${pathways.length}` }}
        </button>
      </section>

      <div class="dna-v3__grid">
        <section class="dna-card" aria-labelledby="dna-competencies-title">
          <div class="dna-card__head">
            <div>
              <h3 id="dna-competencies-title">Competency evidence</h3>
              <p class="dna-v3__meta">
                Top {{ visibleCompetencies.length }} of {{ competencies.length }} scored
                competencies.
              </p>
            </div>
          </div>

          <ul v-if="competencies.length" class="dna-competencies">
            <li v-for="item in visibleCompetencies" :key="item.competency_id">
              <div class="dna-competency__head">
                <span>{{ item.competency_name }}</span>
                <span class="dna-competency__score">
                  {{ item.score }} &middot; {{ bandLabel(item.band) }}
                </span>
              </div>
              <div class="dna-competency__track" aria-hidden="true">
                <span :style="{ width: item.score + '%' }"></span>
              </div>
              <p class="dna-v3__meta">
                {{ item.domain_label }} &middot; {{ item.evidence_count }} observations
                <template v-if="item.last_practised_at">
                  &middot; last practised {{ formatDate(item.last_practised_at) }}
                </template>
              </p>
            </li>
          </ul>
          <p v-else class="dna-v3__meta">
            Complete an exercise to start your competency evidence.
          </p>

          <button
            v-if="competencies.length > 8"
            type="button"
            class="btn btn--secondary btn--sm"
            :aria-expanded="showAllCompetencies"
            @click="showAllCompetencies = !showAllCompetencies"
          >
            {{ showAllCompetencies ? 'Show top 8' : `Show all ${competencies.length}` }}
          </button>
        </section>

        <section class="dna-card" aria-labelledby="dna-behavior-title">
          <div class="dna-card__head">
            <div>
              <h3 id="dna-behavior-title">Behavior signals</h3>
              <p class="dna-v3__meta">
                Last {{ behavior.window_days }} days. Low-confidence signals stay visible
                but are not treated as conclusions.
              </p>
            </div>
          </div>

          <ul class="dna-signals">
            <li v-for="signal in behaviorSignals" :key="signal.key">
              <div class="dna-signal__head">
                <span>{{ signal.label }}</span>
                <strong>{{ signal.value === null ? '—' : signal.value }}</strong>
              </div>
              <p class="dna-v3__meta">
                {{ signal.sample_size }} samples &middot;
                {{ signal.confidence ? `${signal.confidence} confidence` : 'no confidence yet' }}
              </p>
              <p v-if="signal.note" class="dna-signal__note">{{ signal.note }}</p>
            </li>
          </ul>

          <p v-if="behavior.note" class="dna-signal__note">{{ behavior.note }}</p>
        </section>

        <section class="dna-card" aria-labelledby="dna-interest-title">
          <div class="dna-card__head">
            <div>
              <h3 id="dna-interest-title">Voluntary interest</h3>
              <p class="dna-v3__meta">
                Built from exercises you chose outside a course, weighted by recency.
              </p>
            </div>
          </div>

          <template v-if="interest.available && interestItems.length">
            <ul class="dna-interest">
              <li v-for="item in interestItems" :key="item.key">
                <div class="dna-interest__head">
                  <span>{{ item.label }}</span>
                  <span>{{ item.value }}%</span>
                </div>
                <div class="dna-interest__track" aria-hidden="true">
                  <span :style="{ width: item.value + '%' }"></span>
                </div>
              </li>
            </ul>
            <p class="dna-v3__meta">{{ interest.note }}</p>
          </template>
          <p v-else class="dna-v3__meta">
            Complete a few exercises outside a course to build an interest signal.
          </p>
        </section>
      </div>

      <p class="dna-v3__disclaimer">{{ data.disclaimer }}</p>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'

const state = ref('loading')
const error = ref('')
const data = ref(null)
const showAllPathways = ref(false)
const showAllCompetencies = ref(false)

const gate = computed(() => data.value?.affinity?.gate || {
  available: false,
  labs: { have: 0, need: 30 },
  domains: { have: 0, need: 3 },
  observations: { have: 0, need: 100 },
})
const pathways = computed(() => data.value?.affinity?.pathways || [])
const visiblePathways = computed(() =>
  showAllPathways.value ? pathways.value : pathways.value.slice(0, 3)
)
const competencies = computed(() =>
  [...(data.value?.competencies || [])].sort((a, b) => (b.score || 0) - (a.score || 0))
)
const visibleCompetencies = computed(() =>
  showAllCompetencies.value ? competencies.value : competencies.value.slice(0, 8)
)
const behavior = computed(() => data.value?.behavior || { signals: {}, window_days: 30 })
const interest = computed(() => data.value?.interest || { available: false, vector: {} })
const evidenceItems = computed(() => data.value?.evidence_summary?.evidence_items || 0)
const competenciesWithEvidence = computed(
  () => data.value?.evidence_summary?.competencies_with_evidence || 0
)

const gateItems = computed(() =>
  [
    { key: 'labs', label: 'Labs', ...gate.value.labs },
    { key: 'domains', label: 'Domains', ...gate.value.domains },
    { key: 'observations', label: 'Observations', ...gate.value.observations },
  ].map((item) => ({
    ...item,
    percent: Math.min(100, Math.round((item.have / Math.max(item.need, 1)) * 100)),
  }))
)

const behaviorSignals = computed(() =>
  Object.entries(behavior.value.signals || {}).map(([key, signal]) => ({
    key,
    label: signalLabel(key),
    value: signal.value,
    sample_size: signal.sample_size,
    confidence: signal.confidence,
    note: signal.note,
  }))
)

const interestItems = computed(() =>
  Object.entries(interest.value.vector || {})
    .map(([key, value]) => ({ key, label: labelize(key), value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6)
)

const bandMap = computed(() =>
  Object.fromEntries(
    (data.value?.proficiency_scale || []).map((item) => [item.id, item.label])
  )
)

function percent(value) {
  return value === null || value === undefined ? '—' : `${Math.round(value * 100)}%`
}

function labelize(value) {
  return String(value || '')
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function signalLabel(key) {
  return {
    persistence: 'Persistence',
    independence: 'Independence',
    speed: 'Speed',
    consistency: 'Consistency',
    investigation: 'Investigation breadth',
  }[key] || labelize(key)
}

function componentLabel(key) {
  return {
    coverage: 'Coverage',
    depth: 'Depth',
    behavior: 'Behavior',
    interest: 'Interest',
  }[key] || labelize(key)
}

function bandLabel(band) {
  return bandMap.value[band] || labelize(band)
}

function formatDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

async function load() {
  state.value = 'loading'
  error.value = ''
  try {
    const { data: payload } = await axios.get('/dna/v3/dna')
    data.value = payload
    state.value = 'ready'
  } catch (e) {
    const status = e.response?.status
    const body = e.response?.data || {}
    if (status === 403 && body.error === 'ConsentRequired') {
      state.value = 'consent'
      return
    }
    if (status === 403 && String(body.detail || '').toLowerCase().includes('role')) {
      state.value = 'denied'
      return
    }
    if (status === 404) {
      state.value = 'disabled'
      return
    }
    state.value = 'error'
    error.value = body.detail || 'Could not load Cyber DNA. Try again in a moment.'
  }
}

onMounted(load)
</script>

<style scoped>
.dna-v3 {
  display: grid;
  gap: 1.25rem;
}

.dna-v3__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.dna-v3__eyebrow {
  margin: 0 0 0.35rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.dna-v3__lead {
  max-width: 68ch;
  margin: 0.5rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.dna-v3__version {
  flex: none;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.7rem;
}

.dna-v3__status,
.dna-v3__notice {
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.dna-v3__notice h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
}

.dna-v3__notice p {
  max-width: 68ch;
  margin: 0 0 0.9rem;
  color: var(--text-secondary);
}

.dna-v3__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
}

.dna-v3__stats > div {
  padding: 0.85rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.dna-v3__stats strong {
  display: block;
  color: var(--text-primary);
  font-size: 1.35rem;
  line-height: 1.2;
}

.dna-v3__stats span {
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.dna-card {
  padding: 1.1rem 1.15rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.dna-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.9rem;
}

.dna-card__head h3 {
  margin: 0;
  font-size: 1rem;
}

.dna-v3__meta {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

.dna-badge {
  flex: none;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
}

.dna-badge--success {
  background: var(--success-bg);
  color: var(--success);
}

.dna-badge--warning {
  background: var(--warning-bg);
  color: var(--warning);
}

.dna-badge--neutral {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.dna-gate {
  display: grid;
  gap: 0.85rem;
}

.dna-gate__label {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.dna-gate__track,
.dna-competency__track,
.dna-interest__track {
  height: 0.45rem;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.dna-gate__track span,
.dna-competency__track span,
.dna-interest__track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
  transition: width 240ms ease;
}

.dna-pathways {
  display: grid;
  gap: 0.9rem;
}

.dna-pathway {
  padding: 0.95rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.dna-pathway__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.dna-pathway__rank {
  margin: 0 0 0.15rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.dna-pathway__head h4 {
  margin: 0;
  font-size: 1rem;
}

.dna-pathway__score {
  flex: none;
  text-align: right;
}

.dna-pathway__score strong {
  display: block;
  color: var(--accent-text);
  font-size: 1.5rem;
  line-height: 1;
}

.dna-pathway__score span {
  color: var(--text-muted);
  font-size: 0.7rem;
}

.dna-pathway__components {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin: 0.75rem 0;
}

.dna-component {
  padding: 0.18rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.dna-component strong {
  color: var(--text-primary);
}

.dna-component--empty {
  opacity: 0.65;
}

.dna-pathway__columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.dna-pathway__label {
  margin: 0 0 0.3rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dna-pathway__list {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.5;
}

.dna-pathway__why {
  margin-top: 0.65rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.dna-pathway__why summary {
  cursor: pointer;
  color: var(--accent-text);
}

.dna-pathway__why ul {
  margin: 0.4rem 0 0;
  padding-left: 1.1rem;
  line-height: 1.5;
}

.dna-v3__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  align-items: start;
}

.dna-competencies,
.dna-signals,
.dna-interest {
  display: grid;
  gap: 0.8rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.dna-competency__head,
.dna-signal__head,
.dna-interest__head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.3rem;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.dna-competency__score {
  flex: none;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.dna-signal__head strong {
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.dna-signal__note {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.75rem;
  line-height: 1.45;
}

.dna-v3__disclaimer {
  margin: 0;
  padding-top: 0.25rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.75rem;
  line-height: 1.5;
}

.dna-card .btn {
  margin-top: 0.9rem;
}

@media (max-width: 640px) {
  .dna-v3__head,
  .dna-card__head,
  .dna-pathway__head {
    flex-direction: column;
  }

  .dna-pathway__score {
    text-align: left;
  }
}

@media (prefers-reduced-motion: reduce) {
  .dna-gate__track span,
  .dna-competency__track span,
  .dna-interest__track span {
    transition: none;
  }
}
</style>
