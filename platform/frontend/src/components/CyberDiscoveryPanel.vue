<template>
  <section class="discovery" aria-labelledby="discovery-title">
    <div v-if="loading" class="discovery-state">Loading the Cyber Discovery experience…</div>
    <p v-else-if="error" class="discovery-state discovery-state--error" role="alert">{{ error }}</p>

    <template v-else-if="data">
      <header class="discovery-hero">
        <div class="discovery-hero__body">
          <p class="discovery-eyebrow">Cyber Discovery Experience</p>
          <h2 id="discovery-title">{{ data.plan.tagline || 'Discover Your Cyber DNA. Find Your Cyber Path.' }}</h2>
          <p class="discovery-hero__intro">
            Four short investigations, four career pathways, and a Cyber DNA snapshot.
            This is a discovery day, not a CTF. Readiness is a curriculum-coverage
            signal, not a hiring prediction.
          </p>
          <ul v-if="data.plan.promise?.length" class="discovery-promise">
            <li v-for="item in data.plan.promise" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div class="discovery-hero__progress">
          <span>Morning investigations</span>
          <strong>{{ data.progress.completed_blocks }} / {{ data.progress.total_blocks }}</strong>
          <div
            class="discovery-progress"
            role="progressbar"
            :aria-valuenow="data.progress.completed_blocks"
            aria-valuemin="0"
            :aria-valuemax="data.progress.total_blocks"
            :aria-label="`${data.progress.completed_blocks} of ${data.progress.total_blocks} investigations complete`"
          >
            <span :style="{ width: progressPercent + '%' }"></span>
          </div>
          <router-link
            v-if="data.next_action?.kind === 'exercise'"
            :to="exerciseLink(data.next_action.lab)"
            class="btn btn--primary btn--sm"
          >
            {{ data.next_action.label }}
          </router-link>
          <router-link
            v-else-if="data.next_action?.kind === 'certificate'"
            :to="data.next_action.url"
            class="btn btn--primary btn--sm"
          >
            {{ data.next_action.label }}
          </router-link>
          <span v-else class="discovery-hero__join">{{ data.next_action?.label }}</span>
        </div>
      </header>

      <section class="discovery-panel" aria-labelledby="discovery-morning-title">
        <div class="discovery-panel__head">
          <div>
            <p class="discovery-eyebrow">Morning</p>
            <h3 id="discovery-morning-title">What does it take to become a cyber person?</h3>
            <p>Each block is one short investigation. Complete one to place a point on your map.</p>
          </div>
        </div>
        <div class="discovery-blocks">
          <article
            v-for="block in data.progress.morning"
            :key="block.id"
            class="discovery-block"
            :class="block.completed ? 'discovery-block--done' : ''"
          >
            <div class="discovery-block__head">
              <span class="discovery-block__status">
                {{ block.completed ? 'Evidence collected' : 'Not started' }}
              </span>
              <span class="discovery-block__count">{{ block.completed_labs }} / {{ block.total_labs }}</span>
            </div>
            <h4>{{ block.title }}</h4>
            <p>{{ block.scenario }}</p>
            <div class="discovery-tags">
              <span v-for="competency in block.competencies" :key="competency" class="discovery-tag">
                {{ competency }}
              </span>
            </div>
            <ul v-if="block.labs.length" class="discovery-labs">
              <li v-for="lab in block.labs" :key="lab.slug">
                <span :class="lab.completed ? 'discovery-lab--done' : ''">
                  {{ lab.completed ? '✓' : '○' }} {{ lab.name }}
                </span>
                <router-link :to="exerciseLink(lab)" class="discovery-lab__open">
                  {{ lab.completed ? 'Review' : 'Open' }}
                </router-link>
              </li>
            </ul>
          </article>
        </div>
      </section>

      <div class="discovery-grid">
        <section class="discovery-panel" aria-labelledby="discovery-dna-title">
          <div class="discovery-panel__head">
            <div>
              <p class="discovery-eyebrow">Cyber DNA</p>
              <h3 id="discovery-dna-title">Your practice shape</h3>
            </div>
            <span v-if="data.dna?.class?.class_name" class="discovery-chip">
              {{ data.dna.class.class_name }}
            </span>
          </div>
          <div v-if="data.dna?.dimensions?.length" class="discovery-dna">
            <div v-for="dimension in data.dna.dimensions" :key="dimension.key" class="discovery-dna__row">
              <span>{{ dimension.label }}</span>
              <div class="discovery-dna__bar">
                <span :style="{ width: `${dimension.score}%` }"></span>
              </div>
              <strong>{{ dimension.score }}</strong>
            </div>
          </div>
          <p v-else class="discovery-empty">Complete an investigation to start your Cyber DNA.</p>
          <p class="discovery-note">
            Overall {{ data.dna?.overall ?? 0 }} / 100 · {{ data.dna?.tier || 'Unranked' }}.
            This is a descriptive practice signal, not a grade.
          </p>
        </section>

        <section class="discovery-panel" aria-labelledby="discovery-cert-title">
          <div class="discovery-panel__head">
            <div>
              <p class="discovery-eyebrow">Exclusive certificate</p>
              <h3 id="discovery-cert-title">Cyber Discovery Experience</h3>
            </div>
          </div>
          <template v-if="data.certificate.available">
            <p>
              Your event certificate is ready. It records participation in this
              DevFest experience and includes the event sponsors.
            </p>
            <p v-if="data.certificate.serial" class="discovery-serial">
              <span>Serial</span>
              <code>{{ data.certificate.serial }}</code>
            </p>
            <router-link :to="data.certificate.url" class="btn btn--primary btn--sm">
              Open certificate
            </router-link>
          </template>
          <p v-else-if="!data.certificate.joined" class="discovery-empty">
            Join the event to unlock the exclusive certificate after the event ends.
          </p>
          <p v-else-if="!data.certificate.event_ended" class="discovery-empty">
            The certificate unlocks when the event ends. Keep practising the four
            investigations in the meantime.
          </p>
          <p v-else class="discovery-empty">
            The certificate is not available yet. Check with the event organiser.
          </p>
          <p class="discovery-note">
            The certificate is event-exclusive and verifies through the platform.
            It is not a certification or a hiring credential.
          </p>
        </section>
      </div>

      <section class="discovery-panel" aria-labelledby="discovery-pathways-title">
        <div class="discovery-panel__head">
          <div>
            <p class="discovery-eyebrow">Afternoon</p>
            <h3 id="discovery-pathways-title">Where can I go next?</h3>
            <p>Try a pathway, then read your readiness and the next workbooks.</p>
          </div>
        </div>
        <div class="discovery-pathways">
          <article v-for="pathway in data.pathways" :key="pathway.id" class="discovery-pathway">
            <div class="discovery-pathway__head">
              <div>
                <h4>{{ pathway.title }}</h4>
                <p>{{ pathway.scenario }}</p>
              </div>
              <div class="discovery-pathway__score">
                <strong>{{ pathway.readiness_score }}</strong>
                <span>{{ pathway.rating?.label }}</span>
              </div>
            </div>
            <ul class="discovery-activities">
              <li v-for="activity in pathway.activities" :key="activity">{{ activity }}</li>
            </ul>
            <div v-if="pathway.labs.length" class="discovery-labs">
              <div v-for="lab in pathway.labs" :key="lab.slug" class="discovery-lab-line">
                <span :class="lab.completed ? 'discovery-lab--done' : ''">
                  {{ lab.completed ? '✓' : '○' }} {{ lab.name }}
                </span>
                <router-link :to="exerciseLink(lab)" class="discovery-lab__open">
                  {{ lab.completed ? 'Review' : 'Open' }}
                </router-link>
              </div>
            </div>
            <p v-if="pathway.next_workbooks?.length" class="discovery-next">
              <span>Next workbook</span>
              {{ pathway.next_workbooks[0].name }}
            </p>
          </article>
        </div>
      </section>

      <section v-if="data.plan.career_stories?.stories?.length" class="discovery-panel" aria-labelledby="discovery-stories-title">
        <div class="discovery-panel__head">
          <div>
            <p class="discovery-eyebrow">Career Stories</p>
            <h3 id="discovery-stories-title">Become the person, not just the flag</h3>
            <p>Each story has a role, a situation, and an artifact you can keep.</p>
          </div>
        </div>
        <div class="discovery-stories">
          <article v-for="story in data.plan.career_stories.stories" :key="story.id" class="discovery-story">
            <h4>{{ story.title }}</h4>
            <ol>
              <li v-for="beat in story.beats" :key="beat">{{ beat }}</li>
            </ol>
            <p><span>Artifact</span>{{ story.artifact }}</p>
          </article>
        </div>
      </section>

      <section v-if="canManage" class="discovery-panel" aria-labelledby="discovery-admin-title">
        <div class="discovery-panel__head">
          <div>
            <p class="discovery-eyebrow">Organizer overview</p>
            <h3 id="discovery-admin-title">Aggregate event participation</h3>
          </div>
        </div>
        <p v-if="overviewLoading" class="discovery-empty">Loading event aggregates…</p>
        <p v-else-if="overviewError" class="discovery-empty discovery-empty--error" role="alert">{{ overviewError }}</p>
        <template v-else-if="overview">
          <div v-if="overview.state !== 'available'" class="discovery-suppressed">
            <strong>{{ overview.state === 'suppressed' ? 'Cohort suppressed' : 'No evidence yet' }}</strong>
            <p>{{ overview.reason }}</p>
          </div>
          <template v-else>
            <div class="discovery-admin-stats">
              <div><strong>{{ overview.participants }}</strong><span>participants</span></div>
              <div><strong>{{ overview.certificates_available }}</strong><span>certificates available</span></div>
            </div>
            <div class="discovery-admin-grid">
              <div>
                <h4>Morning investigations</h4>
                <ul class="discovery-admin-list">
                  <li v-for="block in overview.morning" :key="block.id">
                    <span>{{ block.title }}</span>
                    <strong>{{ block.participants }} · {{ block.rate }}%</strong>
                  </li>
                </ul>
              </div>
              <div>
                <h4>Pathway starts</h4>
                <ul class="discovery-admin-list">
                  <li v-for="pathway in overview.pathways" :key="pathway.id">
                    <span>{{ pathway.title }}</span>
                    <strong>{{ pathway.participants }} · {{ pathway.rate }}%</strong>
                  </li>
                </ul>
              </div>
            </div>
            <p class="discovery-note">{{ overview.disclaimer }}</p>
          </template>
        </template>
      </section>

      <p class="discovery-disclaimer">{{ data.disclaimer }}</p>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  competitionId: { type: [Number, String], required: true },
  joined: { type: Boolean, default: false },
  canManage: { type: Boolean, default: false },
})

const data = ref(null)
const loading = ref(true)
const error = ref('')
const overview = ref(null)
const overviewLoading = ref(false)
const overviewError = ref('')

const progressPercent = computed(() => {
  const total = data.value?.progress?.total_blocks || 0
  if (!total) return 0
  return Math.round((data.value.progress.completed_blocks / total) * 100)
})

function exerciseLink(lab) {
  if (lab?.track_slug && lab?.id) {
    return {
      path: `/exercises/${lab.track_slug}`,
      query: { labId: String(lab.id) },
    }
  }
  return { path: '/exercises' }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get(`/competitions/${props.competitionId}/discovery`)
    data.value = response.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load the Cyber Discovery experience.'
  } finally {
    loading.value = false
  }
}

async function loadOverview() {
  if (!props.canManage) return
  overviewLoading.value = true
  overviewError.value = ''
  try {
    const response = await axios.get(`/competitions/${props.competitionId}/discovery/overview`)
    overview.value = response.data
  } catch (e) {
    overviewError.value = e.response?.data?.detail || 'Could not load event aggregates.'
  } finally {
    overviewLoading.value = false
  }
}

onMounted(async () => {
  await load()
  await loadOverview()
})
</script>

<style scoped>
.discovery {
  display: grid;
  gap: 0.8rem;
  margin: 1rem 0;
}

.discovery-state {
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.76rem;
}

.discovery-state--error {
  border-color: var(--danger);
  color: var(--danger);
}

.discovery-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 0.35fr);
  gap: 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    radial-gradient(circle at 100% 0%, var(--accent-bg), transparent 55%),
    var(--bg-secondary);
}

.discovery-eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.discovery-hero h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 750;
}

.discovery-hero__intro {
  max-width: 56rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.76rem;
  line-height: 1.5;
}

.discovery-promise {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.8rem;
  margin: 0.5rem 0 0;
  padding: 0;
  list-style: none;
  color: var(--text-muted);
  font-size: 0.62rem;
}

.discovery-promise li::before {
  content: '✓';
  margin-right: 0.25rem;
  color: var(--success);
}

.discovery-hero__progress {
  display: grid;
  align-content: start;
  gap: 0.3rem;
  padding: 0.65rem 0.75rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  background: var(--accent-bg);
}

.discovery-hero__progress span {
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.discovery-hero__progress strong {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-variant-numeric: tabular-nums;
}

.discovery-progress {
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.discovery-progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--success));
}

.discovery-hero__join {
  color: var(--text-secondary);
  font-size: 0.68rem;
}

.discovery-panel {
  padding: 0.8rem 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.discovery-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.discovery-panel__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 700;
}

.discovery-panel__head p {
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.66rem;
  line-height: 1.4;
}

.discovery-blocks {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.5rem;
}

.discovery-block {
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.discovery-block--done {
  border-left: 3px solid var(--success);
}

.discovery-block__head {
  display: flex;
  justify-content: space-between;
  gap: 0.4rem;
  color: var(--text-muted);
  font-size: 0.58rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.discovery-block__status {
  font-weight: 700;
}

.discovery-block h4 {
  margin: 0.2rem 0 0;
  color: var(--text-primary);
  font-size: 0.78rem;
  font-weight: 700;
}

.discovery-block p {
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.66rem;
  line-height: 1.4;
}

.discovery-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.35rem;
}

.discovery-tag {
  padding: 0.08rem 0.3rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.54rem;
}

.discovery-labs {
  margin: 0.4rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.25rem;
}

.discovery-labs li,
.discovery-lab-line {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.64rem;
}

.discovery-lab--done {
  color: var(--success);
}

.discovery-lab__open {
  flex: 0 0 auto;
  color: var(--accent-text);
  font-size: 0.6rem;
  text-decoration: none;
}

.discovery-lab__open:hover {
  text-decoration: underline;
}

.discovery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.7rem;
}

.discovery-chip {
  flex: 0 0 auto;
  padding: 0.12rem 0.4rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent-text);
  font-size: 0.58rem;
  font-weight: 700;
}

.discovery-dna {
  display: grid;
  gap: 0.25rem;
}

.discovery-dna__row {
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr) 28px;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.discovery-dna__bar {
  height: 5px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.discovery-dna__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}

.discovery-dna__row strong {
  text-align: right;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.discovery-serial {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.62rem;
}

.discovery-serial code {
  color: var(--accent-text);
  font-family: "JetBrains Mono", ui-monospace, monospace;
}

.discovery-pathways {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.5rem;
}

.discovery-pathway {
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.discovery-pathway__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.discovery-pathway h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.78rem;
  font-weight: 700;
}

.discovery-pathway p {
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.64rem;
  line-height: 1.4;
}

.discovery-pathway__score {
  display: grid;
  justify-items: end;
  gap: 0.1rem;
  flex: 0 0 auto;
}

.discovery-pathway__score strong {
  color: var(--text-primary);
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.discovery-pathway__score span {
  color: var(--text-muted);
  font-size: 0.54rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.discovery-activities {
  margin: 0.35rem 0 0;
  padding-left: 1rem;
  color: var(--text-muted);
  font-size: 0.62rem;
  line-height: 1.4;
}

.discovery-next {
  margin: 0.4rem 0 0;
  padding: 0.35rem 0.45rem;
  border-left: 2px solid var(--accent);
  border-radius: 0 6px 6px 0;
  background: var(--accent-bg);
  color: var(--text-secondary);
  font-size: 0.62rem;
}

.discovery-next span {
  display: block;
  color: var(--accent-text);
  font-size: 0.54rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.discovery-stories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.5rem;
}

.discovery-story {
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.discovery-story h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.74rem;
  font-weight: 700;
}

.discovery-story ol {
  margin: 0.3rem 0 0;
  padding-left: 1rem;
  color: var(--text-secondary);
  font-size: 0.62rem;
  line-height: 1.4;
}

.discovery-story p {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.discovery-story p span {
  display: block;
  color: var(--text-muted);
  font-size: 0.54rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.discovery-admin-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 0.4rem;
  margin-bottom: 0.5rem;
}

.discovery-admin-stats div {
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.discovery-admin-stats strong {
  display: block;
  color: var(--text-primary);
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.discovery-admin-stats span {
  color: var(--text-muted);
  font-size: 0.58rem;
}

.discovery-admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.6rem;
}

.discovery-admin-grid h4 {
  margin: 0 0 0.3rem;
  color: var(--text-primary);
  font-size: 0.7rem;
}

.discovery-admin-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.2rem;
}

.discovery-admin-list li {
  display: flex;
  justify-content: space-between;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.62rem;
}

.discovery-admin-list strong {
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.discovery-suppressed {
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--warning);
  border-radius: 8px;
  background: var(--warning-bg);
}

.discovery-suppressed strong {
  color: var(--text-primary);
  font-size: 0.72rem;
}

.discovery-suppressed p {
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.66rem;
}

.discovery-empty {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.68rem;
  line-height: 1.4;
}

.discovery-empty--error {
  color: var(--danger);
}

.discovery-note {
  margin: 0.5rem 0 0;
  color: var(--text-muted);
  font-size: 0.6rem;
  line-height: 1.4;
}

.discovery-disclaimer {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.62rem;
  line-height: 1.45;
}

@media (max-width: 900px) {
  .discovery-hero {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 640px) {
  .discovery-panel__head {
    flex-direction: column;
  }

  .discovery-dna__row {
    grid-template-columns: 72px minmax(0, 1fr) 24px;
  }
}
</style>
