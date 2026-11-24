<template>
  <div class="impact">
    <header class="impact__head">
      <p class="impact__eyebrow">Contribution, not completion</p>
      <h1>Your impact</h1>
      <p>
        What you built, protected, taught, and served. Recognition is separate
        from your evidence and never changes your score by itself.
      </p>
    </header>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="message" class="impact__message" role="status">{{ message }}</p>
    <p v-if="loading" class="impact__muted">Loading your impact...</p>

    <template v-else-if="impact">
      <section v-if="celebration" class="impact__celebration" role="status">
        <div>
          <p class="impact__eyebrow">Achievement earned</p>
          <h2>{{ celebration.title }}</h2>
          <p>{{ celebration.earned_message }}</p>
        </div>
        <button type="button" class="btn btn--outline btn--sm" @click="dismissCelebration">
          Nice
        </button>
      </section>

      <section class="impact__story">
        <div class="impact__score">
          <span>Legacy score</span>
          <strong>{{ impact.legacy_score }}</strong>
          <p>{{ impact.legacy_class }}</p>
        </div>
        <div class="impact__score">
          <span>Meaning index</span>
          <strong>{{ impact.meaning_index.total }}</strong>
          <p>People and communities affected</p>
        </div>
        <div class="impact__score">
          <span>Stewardship</span>
          <strong>{{ impact.stewardship.points }}/150</strong>
          <p>{{ impact.stewardship.band }}</p>
        </div>
        <div class="impact__score">
          <span>Pending</span>
          <strong>{{ impact.pending_impact }}</strong>
          <p>Awaiting verification</p>
        </div>
      </section>

      <section class="impact__dimensions">
        <article v-for="(value, key) in impact.dimensions" :key="key">
          <span>{{ dimensionLabel(key) }}</span>
          <strong>{{ value }}</strong>
        </article>
      </section>

      <section class="impact__meaning">
        <h2>Who this reached</h2>
        <ul>
          <li><span>Organizations protected</span><strong>{{ impact.meaning_index.organizations_protected }}</strong></li>
          <li><span>Learners mentored</span><strong>{{ impact.meaning_index.learners_mentored }}</strong></li>
          <li><span>People taught</span><strong>{{ impact.meaning_index.people_taught }}</strong></li>
          <li><span>Open-source users</span><strong>{{ impact.meaning_index.open_source_users }}</strong></li>
          <li><span>Communities supported</span><strong>{{ impact.meaning_index.communities_supported }}</strong></li>
          <li><span>Years contributing</span><strong>{{ impact.meaning_index.years_contributing }}</strong></li>
        </ul>
      </section>

      <section class="impact__section">
        <h2>Your contributions</h2>
        <p class="impact__muted">
          Self-reported work stays pending until another person verifies it.
          Points are shown only after verification.
        </p>
        <p v-if="!impact.contributions.length" class="impact__muted">
          No contributions yet. Start with something small that another person
          can check.
        </p>
        <ul class="impact__list">
          <li v-for="item in impact.contributions" :key="item.id">
            <div>
              <span class="impact__tag">{{ dimensionLabel(item.dimension) }} · {{ item.kind }}</span>
              <h3>{{ item.title }}</h3>
              <p v-if="item.summary" class="impact__muted">{{ item.summary }}</p>
              <p class="impact__muted">
                {{ statusLabel(item.status) }} · reached {{ item.reach_count }}
                <template v-if="item.status !== 'verified' && item.preview_points">
                  · provisional {{ item.preview_points }} points
                </template>
              </p>
              <p v-if="item.review_notes" class="impact__note">{{ item.review_notes }}</p>
            </div>
            <strong class="impact__points">
              {{ item.status === 'verified' ? item.points : '—' }}
            </strong>
          </li>
        </ul>
      </section>

      <section class="impact__section">
        <h2>Record a contribution</h2>
        <form class="impact__form" @submit.prevent="submitContribution">
          <label>
            <span>What did you do?</span>
            <select v-model="form.dimension" class="form-input">
              <option v-for="dimension in dimensions" :key="dimension" :value="dimension">
                {{ dimensionLabel(dimension) }}
              </option>
            </select>
          </label>
          <label>
            <span>Type</span>
            <select v-model="form.kind" class="form-input">
              <option v-for="kind in kindsFor(form.dimension)" :key="kind" :value="kind">
                {{ kindLabel(kind) }}
              </option>
            </select>
          </label>
          <label>
            <span>Title</span>
            <input v-model="form.title" class="form-input" maxlength="200" required />
          </label>
          <label>
            <span>People reached</span>
            <input v-model.number="form.reach_count" type="number" min="0" class="form-input" />
          </label>
          <label>
            <span>Originality</span>
            <select v-model="form.originality" class="form-input">
              <option v-for="item in catalogue.originalities" :key="item" :value="item">{{ item }}</option>
            </select>
          </label>
          <label class="impact__wide">
            <span>What did it change?</span>
            <textarea v-model="form.summary" class="form-input" rows="3" maxlength="4000" />
          </label>
          <div class="impact__wide">
            <button type="submit" class="btn btn--primary" :disabled="submitting">
              {{ submitting ? 'Submitting...' : 'Submit for verification' }}
            </button>
          </div>
        </form>
      </section>

      <section class="impact__section">
        <h2>Historical markers</h2>
        <p class="impact__muted">
          Recognition is not a trophy. It is a marker of what this generation
          built, protected, taught, and maintained.
        </p>
        <p v-if="board && board.whisper" class="impact__whisper">{{ board.whisper }}</p>
        <h3>Earned</h3>
        <p v-if="!board || !board.earned.length" class="impact__muted">
          Nothing earned yet. Recognition follows verified contribution, not
          activity.
        </p>
        <ul class="impact__awards">
          <li v-for="award in board?.earned || []" :key="award.key" class="impact__award impact__award--earned">
            <span class="impact__tag">{{ award.tradition }} ? {{ award.marker || award.category }}</span>
            <h3>{{ award.title }}</h3>
            <p>{{ award.earned_message }}</p>
          </li>
        </ul>
        <h3>Clues</h3>
        <p class="impact__muted">
          Some achievements show only a clue. There are
          {{ board?.sealed ?? 0 }} still sealed.
        </p>
        <ul class="impact__awards">
          <li
            v-for="(item, index) in board?.visible || []"
            :key="`${item.title}-${index}`"
            class="impact__award"
          >
            <span class="impact__tag">{{ item.tradition }} ? {{ item.category }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.clue }}</p>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const impact = ref(null)
const board = ref(null)
const catalogue = ref({ dimensions: {}, validation_levels: [], originalities: [] })
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const message = ref('')
const celebration = ref(null)

const form = reactive({
  dimension: 'build',
  kind: 'lab',
  title: '',
  reach_count: 0,
  originality: 'original',
  summary: '',
})

const dimensions = ['build', 'protect', 'teach', 'serve']

function dimensionLabel(value) {
  return { build: 'Build', protect: 'Protect', teach: 'Teach', serve: 'Serve' }[value] || value
}

function kindLabel(value) {
  return String(value || '').replaceAll('_', ' ')
}

function statusLabel(value) {
  return String(value || '').replaceAll('_', ' ')
}

function kindsFor(dimension) {
  return Object.keys(catalogue.value.dimensions?.[dimension] || {})
}

async function loadImpact() {
  loading.value = true
  error.value = ''
  try {
    const [impactResponse, catalogueResponse, boardResponse] = await Promise.all([
      axios.get('/impact/me'),
      axios.get('/impact/catalogue'),
      axios.get('/recognition/me'),
    ])
    impact.value = impactResponse.data
    catalogue.value = catalogueResponse.data
    board.value = boardResponse.data
    if (!kindsFor(form.dimension).includes(form.kind)) {
      form.kind = kindsFor(form.dimension)[0] || ''
    }
    const evaluation = await axios.post('/recognition/evaluate')
    const newly = evaluation.data.newly_earned || []
    const unseen = (board.value.earned || []).filter((item) => item.unseen)
    celebration.value = newly[0] || unseen[0] || null
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load your impact.'
  } finally {
    loading.value = false
  }
}

async function submitContribution() {
  submitting.value = true
  error.value = ''
  message.value = ''
  try {
    await axios.post('/impact/contributions', {
      dimension: form.dimension,
      kind: form.kind,
      title: form.title,
      reach_count: form.reach_count,
      originality: form.originality,
      summary: form.summary || null,
    })
    message.value = 'Submitted for verification. It stays provisional until reviewed.'
    form.title = ''
    form.summary = ''
    form.reach_count = 0
    await loadImpact()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not submit the contribution.'
  } finally {
    submitting.value = false
  }
}

async function dismissCelebration() {
  celebration.value = null
  try {
    await axios.post('/recognition/seen')
  } catch {
    // The award is already saved; clearing the banner is not worth an error.
  }
}

onMounted(loadImpact)
</script>

<style scoped>
.impact {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1.25rem;
}

.impact__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.impact__head h1 {
  margin: 0 0 0.5rem;
}

.impact__head p {
  margin: 0;
  color: var(--text-muted, #64748b);
}

.impact__muted {
  color: var(--text-muted, #64748b);
  font-size: 0.88rem;
}

.impact__message {
  color: #166534;
  background: #dcfce7;
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}

.impact__celebration {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
  border: 1px solid var(--accent, #2563eb);
  border-radius: 0.9rem;
  background: linear-gradient(135deg, #eff6ff, #ffffff);
  padding: 1rem;
}

.impact__celebration h2 {
  margin: 0.2rem 0;
}

.impact__celebration p {
  margin: 0;
}

.impact__story,
.impact__dimensions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
}

.impact__score,
.impact__dimensions article {
  border: 1px solid var(--border, #dbe3ee);
  border-radius: 0.8rem;
  background: var(--surface, #fff);
  padding: 0.9rem;
}

.impact__score span,
.impact__dimensions span {
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted, #64748b);
}

.impact__score strong {
  font-size: 1.6rem;
}

.impact__score p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-muted, #64748b);
}

.impact__dimensions article {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.impact__dimensions strong {
  font-size: 1.2rem;
}

.impact__meaning ul,
.impact__list,
.impact__awards {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.6rem;
}

.impact__meaning li {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid var(--border, #dbe3ee);
  padding: 0.35rem 0;
}

.impact__list li,
.impact__award {
  border: 1px solid var(--border, #dbe3ee);
  border-radius: 0.8rem;
  background: var(--surface, #fff);
  padding: 0.9rem;
}

.impact__list li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.impact__list h3,
.impact__award h3 {
  margin: 0.2rem 0 0.3rem;
  font-size: 1rem;
}

.impact__tag {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
}

.impact__points {
  font-size: 1.3rem;
}

.impact__note {
  margin: 0.3rem 0 0;
  font-size: 0.85rem;
  color: #92400e;
  background: #fef3c7;
  border-radius: 0.4rem;
  padding: 0.35rem 0.5rem;
}

.impact__form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 0.75rem;
}

.impact__form label {
  display: grid;
  gap: 0.25rem;
}

.impact__wide {
  grid-column: 1 / -1;
}

.impact__awards {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.impact__award--earned {
  border-color: var(--accent, #2563eb);
}

.impact__whisper {
  font-style: italic;
  border-left: 3px solid var(--accent, #2563eb);
  padding-left: 0.75rem;
  color: var(--text-muted, #64748b);
}

@media (max-width: 640px) {
  .impact__list li {
    flex-direction: column;
  }
}
</style>
