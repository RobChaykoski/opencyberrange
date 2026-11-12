<template>
  <section class="portfolio" aria-labelledby="portfolio-title">
    <header class="portfolio-hero">
      <div class="portfolio-hero__seal" aria-hidden="true">
        <span>{{ classInitial }}</span>
      </div>
      <div class="portfolio-hero__body">
        <p class="portfolio-hero__eyebrow">Professional portfolio</p>
        <h2 id="portfolio-title" class="portfolio-hero__title">
          {{ data?.identity?.display_name || 'Your evidence record' }}
        </h2>
        <p class="portfolio-hero__subtitle">
          {{ data?.cyber_dna?.class?.class_name || 'Recruit' }} ·
          {{ data?.cyber_dna?.overall ?? 0 }}/99 · {{ data?.cyber_dna?.tier || 'Unranked' }}
          <span v-if="data?.generated_at"> · generated {{ formatDate(data.generated_at) }}</span>
        </p>
        <p class="portfolio-hero__headline">{{ data?.headline }}</p>
        <div v-if="data?.portfolio_id" class="portfolio-hero__verify">
          <span>Portfolio ID</span>
          <code>{{ data.portfolio_id }}</code>
          <button type="button" class="portfolio-hero__copy" @click="copyId">
            {{ copied ? 'Copied' : 'Copy' }}
          </button>
        </div>
      </div>
      <div class="portfolio-hero__actions">
        <button
          type="button"
          class="btn btn--primary btn--sm"
          :disabled="downloading"
          @click="download('html')"
        >
          {{ downloading === 'html' ? 'Preparing...' : 'Print / save PDF' }}
        </button>
        <button
          type="button"
          class="btn btn--secondary btn--sm"
          :disabled="downloading"
          @click="download('md')"
        >
          {{ downloading === 'md' ? 'Preparing...' : 'Download Markdown' }}
        </button>
      </div>
    </header>

    <p v-if="loading" class="portfolio-state">Loading your portfolio...</p>
    <p v-else-if="error" class="portfolio-state portfolio-state--error" role="alert">{{ error }}</p>

    <template v-else-if="data">
      <p v-if="downloadMessage" :class="downloadError ? 'error-message' : 'success-message'">
        {{ downloadMessage }}
      </p>

      <div class="portfolio-stats">
        <article v-for="stat in stats" :key="stat.label" class="portfolio-stat">
          <span>{{ stat.label }}</span>
          <strong>{{ stat.value }}</strong>
          <small>{{ stat.detail }}</small>
        </article>
      </div>

      <section class="portfolio-section" aria-labelledby="portfolio-dna-title">
        <div class="portfolio-section__head">
          <div>
            <p class="portfolio-eyebrow">Cyber DNA</p>
            <h3 id="portfolio-dna-title">The practice shape behind the record</h3>
            <p class="portfolio-section__intro">
              Six descriptive traits built from completed work. They are not a grade,
              a ranking, or a prediction.
            </p>
          </div>
          <span class="portfolio-chip">v{{ data.cyber_dna.formula_version }}</span>
        </div>

        <div class="portfolio-dna">
          <div class="portfolio-dna__chart">
            <svg viewBox="0 0 340 300" role="img" :aria-label="dnaAria">
              <polygon
                v-for="(ring, index) in treeRings"
                :key="`ring-${index}`"
                :points="ring"
                class="portfolio-dna__ring"
              />
              <line
                v-for="(axis, index) in treeAxes"
                :key="`axis-${index}`"
                :x1="treeCenter.x"
                :y1="treeCenter.y"
                :x2="axis.x"
                :y2="axis.y"
                class="portfolio-dna__axis"
              />
              <polygon :points="treePolygon" class="portfolio-dna__area" />
              <circle
                v-for="point in treePoints"
                :key="`node-${point.key}`"
                :cx="point.x"
                :cy="point.y"
                r="8"
                class="portfolio-dna__node"
                :class="{ 'portfolio-dna__node--top': point.key === topBranchKey }"
              />
              <circle
                v-for="point in treePoints"
                :key="`dot-${point.key}`"
                :cx="point.x"
                :cy="point.y"
                r="3.5"
                class="portfolio-dna__dot"
              />
              <circle :cx="treeCenter.x" :cy="treeCenter.y" r="18" class="portfolio-dna__core" />
              <text
                :x="treeCenter.x"
                :y="treeCenter.y + 4"
                text-anchor="middle"
                class="portfolio-dna__core-label"
              >{{ classInitial }}</text>
              <text
                v-for="label in treeLabels"
                :key="`label-${label.key}`"
                :x="label.x"
                :y="label.y"
                :text-anchor="label.anchor"
                class="portfolio-dna__label"
              >{{ label.label }}</text>
            </svg>
          </div>
          <div class="portfolio-dna__traits">
            <article
              v-for="dim in data.cyber_dna.dimensions"
              :key="dim.key"
              class="portfolio-trait"
            >
              <div class="portfolio-trait__head">
                <strong>{{ dim.label }}</strong>
                <span>{{ dim.score }}</span>
              </div>
              <div
                class="portfolio-trait__bar"
                role="progressbar"
                :aria-valuenow="dim.score"
                aria-valuemin="0"
                aria-valuemax="99"
                :aria-label="`${dim.label}: ${dim.score} out of 99`"
              >
                <span :style="{ width: dim.score + '%' }"></span>
              </div>
              <p>{{ dim.evidence }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="portfolio-section" aria-labelledby="portfolio-skills-title">
        <div class="portfolio-section__head">
          <div>
            <p class="portfolio-eyebrow">Skills catalogue</p>
            <h3 id="portfolio-skills-title">Competency evidence by domain</h3>
            <p class="portfolio-section__intro">
              Eight competency domains, each with its evidence level and the career
              families it supports.
            </p>
          </div>
        </div>
        <div class="portfolio-skills">
          <article v-for="skill in data.skills" :key="skill.key" class="portfolio-skill">
            <div class="portfolio-skill__head">
              <strong>{{ skill.label }}</strong>
              <span>{{ skill.evidence_label }}</span>
            </div>
            <div
              class="portfolio-skill__bar"
              role="progressbar"
              :aria-valuenow="skill.score || 0"
              aria-valuemin="0"
              aria-valuemax="100"
              :aria-label="`${skill.label}: ${skill.score ?? 'no score'} out of 100`"
            >
              <span :style="{ width: (skill.score || 0) + '%' }"></span>
            </div>
            <p>{{ skill.description }}</p>
            <div class="portfolio-skill__meta">
              <span>{{ skill.score !== null ? `${skill.score}/100` : 'No score yet' }}</span>
              <span>{{ skill.evidence_count }} evidence</span>
            </div>
            <p v-if="skill.career_families.length" class="portfolio-skill__families">
              {{ skill.career_families.join(' · ') }}
            </p>
          </article>
        </div>
      </section>

      <section
        v-if="data.career_pathway?.recommended_family"
        class="portfolio-section"
        aria-labelledby="portfolio-career-title"
      >
        <div class="portfolio-section__head">
          <div>
            <p class="portfolio-eyebrow">Career direction</p>
            <h3 id="portfolio-career-title">{{ data.career_pathway.recommended_family.label }}</h3>
            <p class="portfolio-section__intro">
              {{ data.career_pathway.recommended_family.summary }}
            </p>
          </div>
          <span class="portfolio-chip">
            {{ data.career_pathway.recommended_family.branch_label }} ·
            {{ data.career_pathway.recommended_family.unlock_state.replace('_', ' ') }}
          </span>
        </div>
        <div class="portfolio-career">
          <div class="portfolio-career__roles">
            <p class="portfolio-career__label">Role ladder</p>
            <ul>
              <li
                v-for="role in data.career_pathway.recommended_family.roles"
                :key="role.title"
              >
                <span class="portfolio-role__level">{{ role.level }}</span>
                <strong>{{ role.title }}</strong>
                <p>{{ role.summary }}</p>
              </li>
            </ul>
          </div>
          <aside class="portfolio-career__next">
            <p class="portfolio-career__label">Next practice step</p>
            <p>{{ data.career_pathway.recommended_family.next_step }}</p>
            <p class="portfolio-career__note">{{ data.career_pathway.salary_note }}</p>
          </aside>
        </div>
      </section>

      <section class="portfolio-section" aria-labelledby="portfolio-capstones-title">
        <div class="portfolio-section__head">
          <div>
            <p class="portfolio-eyebrow">Capstones</p>
            <h3 id="portfolio-capstones-title">Role-shaped work</h3>
            <p class="portfolio-section__intro">
              Completed assessment and capstone exercises. These are the strongest
              portfolio artifacts because they combine scope, evidence, and reporting.
            </p>
          </div>
        </div>
        <div v-if="data.capstones.length" class="portfolio-table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Capstone</th>
                <th scope="col">Track</th>
                <th scope="col">Difficulty</th>
                <th scope="col">Completed</th>
                <th scope="col">Clean</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.capstones" :key="row.name + row.completed_at">
                <th scope="row">{{ row.name }}</th>
                <td>{{ row.track }}</td>
                <td>{{ row.difficulty }}</td>
                <td>{{ formatDate(row.completed_at) }}</td>
                <td>{{ row.clean_solve ? 'Yes' : 'No' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="portfolio-empty">
          No capstone evidence yet. Complete an assessment or capstone exercise to
          add one.
        </p>
      </section>

      <section class="portfolio-section" aria-labelledby="portfolio-samples-title">
        <div class="portfolio-section__head">
          <div>
            <p class="portfolio-eyebrow">Work samples</p>
            <h3 id="portfolio-samples-title">Evidence you can talk through</h3>
            <p class="portfolio-section__intro">
              Recent and clean completions selected as conversation anchors. Use the
              workbook and your notes to explain the decisions behind each one.
            </p>
          </div>
        </div>
        <ul class="portfolio-samples">
          <li v-for="row in data.work_samples" :key="row.name + row.completed_at">
            <div>
              <strong>{{ row.name }}</strong>
              <span>{{ row.track }} · {{ row.difficulty }}</span>
            </div>
            <span class="portfolio-sample__meta">
              {{ formatDate(row.completed_at) }} · {{ row.clean_solve ? 'clean solve' : 'completed' }}
            </span>
          </li>
        </ul>
      </section>

      <section class="portfolio-section" aria-labelledby="portfolio-certificates-title">
        <div class="portfolio-section__head">
          <div>
            <p class="portfolio-eyebrow">Recognition</p>
            <h3 id="portfolio-certificates-title">Certificates and achievements</h3>
          </div>
        </div>
        <div class="portfolio-recognition">
          <div>
            <p class="portfolio-career__label">Certificates</p>
            <ul v-if="data.certificates.length" class="portfolio-certificates">
              <li v-for="cert in data.certificates" :key="cert.certificate_id">
                <strong>{{ cert.track_name }} · Level {{ cert.level_number }}</strong>
                <span>{{ cert.level_name }} · {{ cert.certificate_id }}</span>
              </li>
            </ul>
            <p v-else class="portfolio-empty">No certificates yet.</p>
          </div>
          <div>
            <p class="portfolio-career__label">Achievements</p>
            <div v-if="data.achievements.length" class="portfolio-badges">
              <span v-for="badge in data.achievements.slice(0, 12)" :key="badge.type || badge.label">
                {{ badge.label }}
              </span>
            </div>
            <p v-else class="portfolio-empty">No achievements yet.</p>
          </div>
        </div>
      </section>

      <section class="portfolio-verification" aria-labelledby="portfolio-verification-title">
        <div>
          <p class="portfolio-eyebrow">Verification</p>
          <h3 id="portfolio-verification-title">Portfolio fingerprint</h3>
          <p>{{ data.verification.note }}</p>
        </div>
        <code class="portfolio-verification__hash">{{ data.verification.sha256 }}</code>
        <p class="portfolio-verification__privacy">{{ data.privacy_note }}</p>
      </section>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'
import { useClipboard } from '../composables/useClipboard'

const loading = ref(true)
const error = ref('')
const data = ref(null)
const downloading = ref('')
const downloadMessage = ref('')
const downloadError = ref(false)
const { copied, copyText } = useClipboard()

const classInitial = computed(() => (data.value?.cyber_dna?.class?.class_name || 'R').charAt(0))

const stats = computed(() => {
  const learning = data.value?.learning || {}
  return [
    { label: 'Exercises', value: learning.completed_exercises ?? 0, detail: `${learning.started_exercises ?? 0} started` },
    { label: 'Learning time', value: `${learning.learning_hours ?? 0} h`, detail: `${learning.learning_minutes ?? 0} min` },
    { label: 'Workbooks', value: learning.workbooks_completed ?? 0, detail: 'completed chapters' },
    { label: 'Capstones', value: learning.capstones_completed ?? 0, detail: 'assessment work' },
    { label: 'Certificates', value: learning.certificates ?? 0, detail: 'level awards' },
    { label: 'Clean solves', value: learning.clean_solves ?? 0, detail: `${learning.hint_free_rate ?? 0}% hint-free` },
  ]
})

const treeCenter = { x: 170, y: 140 }
const TREE_RADIUS = 100
const TREE_LABEL_RADIUS = 128

const treeDimensions = computed(() => data.value?.cyber_dna?.dimensions || [])
const treePointAtRadius = (index, radius) => {
  const count = treeDimensions.value.length || 6
  const angle = -Math.PI / 2 + index * ((2 * Math.PI) / count)
  return {
    x: treeCenter.x + Math.cos(angle) * radius,
    y: treeCenter.y + Math.sin(angle) * radius,
  }
}
const treePoint = (index, score) =>
  treePointAtRadius(index, TREE_RADIUS * (Math.max(0, Math.min(100, score)) / 100))
const treeRing = (percent) =>
  treeDimensions.value
    .map((_, index) => treePointAtRadius(index, TREE_RADIUS * (percent / 100)))
    .map((point) => `${point.x},${point.y}`)
    .join(' ')
const treeRings = computed(() => [25, 50, 75, 100].map(treeRing))
const treeAxes = computed(() =>
  treeDimensions.value.map((_, index) => treePointAtRadius(index, TREE_RADIUS))
)
const treePolygon = computed(() =>
  treeDimensions.value
    .map((dimension, index) => treePoint(index, dimension.score))
    .map((point) => `${point.x},${point.y}`)
    .join(' ')
)
const treePoints = computed(() =>
  treeDimensions.value.map((dimension, index) => ({
    key: dimension.key,
    ...treePoint(index, dimension.score),
  }))
)
const treeLabels = computed(() =>
  treeDimensions.value.map((dimension, index) => {
    const point = treePointAtRadius(index, TREE_LABEL_RADIUS)
    return {
      key: dimension.key,
      label: dimension.label,
      x: point.x,
      y: point.y,
      anchor:
        point.x < treeCenter.x - 5
          ? 'end'
          : point.x > treeCenter.x + 5
            ? 'start'
            : 'middle',
    }
  })
)
const topBranchKey = computed(() => {
  const dimensions = treeDimensions.value
  if (!dimensions.length) return null
  return [...dimensions].sort((a, b) => b.score - a.score)[0].key
})
const dnaAria = computed(() => {
  const branches = treeDimensions.value
    .map((dimension) => `${dimension.label}: ${dimension.score} out of 99`)
    .join('. ')
  return `Cyber DNA skill tree. ${branches}.`
})

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value).slice(0, 10)
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function copyId() {
  if (data.value?.portfolio_id) copyText(data.value.portfolio_id)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data: payload } = await axios.get('/profile/portfolio')
    data.value = payload
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      'Could not load the professional portfolio. The preview may not be enabled on this deployment.'
  } finally {
    loading.value = false
  }
}

async function download(format) {
  if (!['md', 'html'].includes(format) || downloading.value) return
  downloading.value = format
  downloadMessage.value = ''
  downloadError.value = false
  try {
    const response = await axios.get(`/profile/portfolio.${format}`, {
      responseType: 'blob',
    })
    const type = format === 'html' ? 'text/html;charset=utf-8' : 'text/markdown;charset=utf-8'
    const blob = new Blob([response.data], { type })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `professional-portfolio-${data.value?.identity?.username || 'learner'}.${format}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    downloadMessage.value = 'Portfolio downloaded.'
  } catch (e) {
    downloadError.value = true
    downloadMessage.value =
      e.response?.data?.detail || 'Could not prepare the portfolio. Please try again.'
  } finally {
    downloading.value = ''
  }
}

onMounted(load)
</script>

<style scoped>
.portfolio {
  display: grid;
  gap: 1rem;
}

.portfolio-hero {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background:
    radial-gradient(circle at 0% 0%, var(--accent-bg), transparent 55%),
    var(--bg-secondary);
}

.portfolio-hero__seal {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 64px;
  height: 64px;
  border: 2px solid var(--accent);
  border-radius: 50%;
  background: var(--bg-primary);
  color: var(--accent-text);
  font-size: 1.4rem;
  font-weight: 800;
  box-shadow: inset 0 0 0 5px var(--accent-bg);
}

.portfolio-hero__body {
  min-width: 0;
  flex: 1 1 auto;
}

.portfolio-hero__eyebrow,
.portfolio-eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.portfolio-hero__title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.4rem;
  font-weight: 750;
}

.portfolio-hero__subtitle {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.portfolio-hero__headline {
  max-width: 60rem;
  margin: 0.45rem 0 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.portfolio-hero__verify {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.55rem;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.portfolio-hero__verify code {
  color: var(--text-secondary);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.66rem;
  overflow-wrap: anywhere;
}

.portfolio-hero__copy {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font: inherit;
  font-size: 0.62rem;
  padding: 0.1rem 0.35rem;
  cursor: pointer;
}

.portfolio-hero__copy:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.portfolio-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  flex: 0 0 auto;
}

.portfolio-state {
  margin: 0;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.portfolio-state--error {
  border-color: var(--danger);
  color: var(--danger);
}

.portfolio-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.65rem;
}

.portfolio-stat {
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.portfolio-stat span {
  display: block;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.portfolio-stat strong {
  display: block;
  margin-top: 0.1rem;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-variant-numeric: tabular-nums;
}

.portfolio-stat small {
  color: var(--text-muted);
  font-size: 0.66rem;
}

.portfolio-section {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.portfolio-section__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.portfolio-section__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 700;
}

.portfolio-section__intro {
  max-width: 58rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.5;
}

.portfolio-chip {
  flex: 0 0 auto;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.64rem;
  white-space: nowrap;
}

.portfolio-dna {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 0.9fr);
  gap: 1rem;
  align-items: center;
}

.portfolio-dna__chart {
  min-width: 0;
}

.portfolio-dna__chart svg {
  display: block;
  width: 100%;
  max-width: 420px;
  height: auto;
  margin: 0 auto;
  overflow: visible;
}

.portfolio-dna__ring {
  fill: none;
  stroke: var(--border-color);
  stroke-width: 1;
  opacity: 0.7;
}

.portfolio-dna__axis {
  stroke: var(--border-color);
  stroke-width: 1;
  opacity: 0.65;
}

.portfolio-dna__area {
  fill: var(--accent-bg);
  stroke: var(--accent);
  stroke-width: 2;
}

.portfolio-dna__node {
  fill: var(--bg-primary);
  stroke: var(--border-color);
  stroke-width: 2;
}

.portfolio-dna__node--top {
  stroke: var(--accent);
  stroke-width: 3;
}

.portfolio-dna__dot {
  fill: var(--accent);
  stroke: var(--bg-primary);
  stroke-width: 2;
}

.portfolio-dna__core {
  fill: var(--bg-tertiary);
  stroke: var(--accent);
  stroke-width: 2;
}

.portfolio-dna__core-label {
  fill: var(--accent-text);
  font-size: 12px;
  font-weight: 700;
}

.portfolio-dna__label {
  fill: var(--text-secondary);
  font-size: 8.5px;
  font-weight: 600;
}

.portfolio-dna__traits {
  display: grid;
  gap: 0.5rem;
}

.portfolio-trait {
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.portfolio-trait__head {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  color: var(--text-primary);
  font-size: 0.75rem;
}

.portfolio-trait__head span {
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.portfolio-trait__bar,
.portfolio-skill__bar {
  height: 6px;
  margin: 0.35rem 0;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.portfolio-trait__bar span,
.portfolio-skill__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--success));
}

.portfolio-trait p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.66rem;
  line-height: 1.4;
}

.portfolio-skills {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.65rem;
}

.portfolio-skill {
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.portfolio-skill__head {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  color: var(--text-primary);
  font-size: 0.78rem;
}

.portfolio-skill__head span {
  color: var(--accent-text);
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
}

.portfolio-skill p {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.45;
}

.portfolio-skill__meta {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.35rem;
  color: var(--text-muted);
  font-size: 0.64rem;
}

.portfolio-skill__families {
  color: var(--text-muted) !important;
  font-size: 0.62rem !important;
  text-transform: capitalize;
}

.portfolio-career {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(220px, 0.8fr);
  gap: 0.75rem;
}

.portfolio-career__roles,
.portfolio-career__next {
  padding: 0.75rem 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.portfolio-career__label {
  margin: 0 0 0.35rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.portfolio-career__roles ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.portfolio-career__roles li {
  padding: 0.4rem 0;
  border-top: 1px solid var(--border-color);
}

.portfolio-career__roles li:first-child {
  border-top: 0;
}

.portfolio-role__level {
  display: inline-block;
  margin-right: 0.35rem;
  padding: 0.05rem 0.35rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.56rem;
  font-weight: 700;
  text-transform: uppercase;
}

.portfolio-career__roles strong {
  color: var(--text-primary);
  font-size: 0.76rem;
}

.portfolio-career__roles p,
.portfolio-career__next p {
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.45;
}

.portfolio-career__next {
  border-left: 3px solid var(--accent);
}

.portfolio-career__note {
  color: var(--text-muted) !important;
  font-size: 0.64rem !important;
}

.portfolio-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.portfolio-table-wrap table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.72rem;
}

.portfolio-table-wrap th,
.portfolio-table-wrap td {
  padding: 0.45rem 0.55rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  vertical-align: top;
}

.portfolio-table-wrap thead th {
  color: var(--text-muted);
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.portfolio-table-wrap tbody th {
  color: var(--text-primary);
  font-weight: 600;
}

.portfolio-empty {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.74rem;
}

.portfolio-samples,
.portfolio-certificates {
  margin: 0;
  padding: 0;
  list-style: none;
}

.portfolio-samples li {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-top: 1px solid var(--border-color);
}

.portfolio-samples li:first-child {
  border-top: 0;
}

.portfolio-samples strong {
  color: var(--text-primary);
  font-size: 0.76rem;
}

.portfolio-samples div span {
  display: block;
  color: var(--text-muted);
  font-size: 0.66rem;
}

.portfolio-sample__meta {
  flex: 0 0 auto;
  color: var(--text-muted);
  font-size: 0.64rem;
}

.portfolio-recognition {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.75rem;
}

.portfolio-certificates li {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.4rem 0;
  border-top: 1px solid var(--border-color);
}

.portfolio-certificates li:first-child {
  border-top: 0;
}

.portfolio-certificates strong {
  color: var(--text-primary);
  font-size: 0.74rem;
}

.portfolio-certificates span {
  color: var(--text-muted);
  font-size: 0.64rem;
  overflow-wrap: anywhere;
}

.portfolio-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.portfolio-badges span {
  padding: 0.2rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.64rem;
}

.portfolio-verification {
  padding: 0.9rem 1rem;
  border: 1px dashed var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.portfolio-verification h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.portfolio-verification p {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.45;
}

.portfolio-verification__hash {
  display: block;
  margin: 0.5rem 0;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.62rem;
  overflow-wrap: anywhere;
}

.portfolio-verification__privacy {
  color: var(--text-muted) !important;
}

@media (max-width: 900px) {
  .portfolio-hero,
  .portfolio-dna,
  .portfolio-career {
    grid-template-columns: minmax(0, 1fr);
  }

  .portfolio-hero {
    flex-direction: column;
  }

  .portfolio-hero__actions {
    width: 100%;
  }

  .portfolio-hero__actions .btn {
    flex: 1 1 auto;
  }
}

@media (max-width: 640px) {
  .portfolio-section__head,
  .portfolio-samples li {
    flex-direction: column;
    align-items: flex-start;
  }

  .portfolio-samples li {
    gap: 0.2rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .portfolio-trait__bar span,
  .portfolio-skill__bar span {
    transition: none;
  }
}
</style>
