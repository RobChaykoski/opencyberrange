<template>
  <section class="gps" aria-labelledby="gps-title">
    <header class="gps-hero">
      <div class="gps-hero__compass" aria-hidden="true">
        <span>N</span>
        <span>E</span>
        <span>S</span>
        <span>W</span>
        <i></i>
      </div>
      <div class="gps-hero__body">
        <p class="gps-eyebrow">Cybersecurity GPS</p>
        <h2 id="gps-title" class="gps-hero__title">Where am I, and where could I go?</h2>
        <p class="gps-hero__intro">
          The GPS combines your practice evidence, your recent growth, and a few
          optional questions. The questions help you name a direction; they do not
          change your grades. Skip any question and the evidence-only view still works.
        </p>
        <p class="gps-hero__privacy">
          <strong>Optional and private.</strong> Answers are used for this view only
          and are not saved, logged, or shared with your cohort.
        </p>
      </div>
      <div v-if="data" class="gps-hero__next">
        <span>Next experiment</span>
        <p>{{ data.next_step }}</p>
      </div>
    </header>

    <p v-if="loading" class="gps-state">Reading your evidence map…</p>
    <p v-else-if="error" class="gps-state gps-state--error" role="alert">{{ error }}</p>

    <template v-else-if="data">
      <section class="gps-panel" aria-labelledby="gps-where-title">
        <div class="gps-panel__head">
          <div>
            <p class="gps-eyebrow">Where you are</p>
            <h3 id="gps-where-title">Your current evidence</h3>
          </div>
          <div class="gps-panel__chips">
            <span
              class="gps-signal"
              :class="signalClass"
              :title="signalTitle"
            >
              <span class="gps-signal__dot" aria-hidden="true"></span>
              {{ signalLabel }}
            </span>
            <span class="gps-chip">{{ data.where_you_are.evidence_total }} evidence points</span>
          </div>
        </div>

        <div class="gps-where">
          <div class="gps-domains">
            <article
              v-for="domain in data.where_you_are.top_domains"
              :key="domain.key"
              class="gps-domain"
              :class="[
                `gps-domain--${domain.colour}`,
                {
                  'gps-domain--active': domain.recent_count > 0,
                  'gps-domain--idle': domain.recent_count === 0 && domain.evidence_count > 0,
                },
              ]"
              :title="
                domain.recent_count > 0
                  ? `${domain.recent_count} completion(s) here in the last 30 days`
                  : 'No practice here in the last 30 days. One exercise restores the signal.'
              "
            >
              <div class="gps-domain__head">
                <strong>
                  <i class="gps-dot" :class="`gps-dot--${domain.colour}`" aria-hidden="true"></i>
                  {{ domain.label }}
                </strong>
                <span>{{ domain.score }}%</span>
              </div>
              <p>{{ domain.evidence_count }} evidence · {{ domain.recent_count }} in the last 30 days</p>
            </article>
            <p v-if="!data.where_you_are.top_domains.length" class="gps-empty">
              No domain evidence yet. Complete one exercise to place the first point.
            </p>
          </div>

          <div class="gps-strengths">
            <p class="gps-eyebrow">Strongest competencies</p>
            <ul v-if="data.where_you_are.strongest_competencies.length">
              <li v-for="skill in data.where_you_are.strongest_competencies" :key="skill.id">
                <div>
                  <strong>{{ skill.name }}</strong>
                  <span>{{ skill.domain }} · {{ skill.level || 'No level yet' }}</span>
                </div>
                <span class="gps-score">{{ skill.score }}</span>
              </li>
            </ul>
            <p v-else class="gps-empty">Your first completed exercise starts this list.</p>
          </div>
        </div>

        <p class="gps-growth">
          <strong>{{ data.where_you_are.recent_total }} recent completion(s)</strong>
          in the last 30 days.
          <span :class="signalClass">
            {{ signalActive
              ? 'Your signal is shimmering; keep the habit going.'
              : 'Your signal is fading. One completed exercise restores it.' }}
          </span>
          {{ data.growth.note }}
        </p>

        <p v-if="fadingDomains.length" class="gps-revisit">
          <strong>Fading interest signals:</strong>
          {{ fadingDomains.map((domain) => domain.label).join(', ') }}.
          You have worked in {{ fadingDomains.length === 1 ? 'this area' : 'these areas' }}
          before, so a short exercise can show whether the interest is still there.
        </p>
      </section>

      <section class="gps-panel" aria-labelledby="gps-questions-title">
        <div class="gps-panel__head">
          <div>
            <p class="gps-eyebrow">Optional questions</p>
            <h3 id="gps-questions-title">Help the compass point</h3>
            <p class="gps-panel__intro">{{ data.answers_note }}</p>
          </div>
          <span v-if="data.answers_received" class="gps-chip gps-chip--active">Answers applied</span>
        </div>

        <form class="gps-questions" @submit.prevent="submitAnswers">
          <fieldset v-for="question in data.questions" :key="question.id" class="gps-question">
            <legend>{{ question.prompt }}</legend>
            <p v-if="question.help" class="gps-question__help">{{ question.help }}</p>
            <div class="gps-options">
              <label
                v-for="option in question.options"
                :key="option.id"
                class="gps-option"
                :class="{ 'gps-option--selected': answers[question.id] === option.id }"
              >
                <input
                  v-model="answers[question.id]"
                  type="radio"
                  :name="`gps-${question.id}`"
                  :value="option.id"
                />
                <span>{{ option.label }}</span>
              </label>
            </div>
          </fieldset>

          <div class="gps-actions">
            <button type="submit" class="btn btn--primary btn--sm" :disabled="submitting">
              {{ submitting ? 'Updating…' : 'Update my map' }}
            </button>
            <button
              type="button"
              class="btn btn--secondary btn--sm"
              :disabled="submitting || !hasAnswers"
              @click="clearAnswers"
            >
              Clear answers
            </button>
            <span class="gps-actions__note">You can change or skip these at any time.</span>
          </div>
        </form>
      </section>

      <section class="gps-panel" aria-labelledby="gps-directions-title">
        <div class="gps-panel__head">
          <div>
            <p class="gps-eyebrow">Possible directions</p>
            <h3 id="gps-directions-title">Where the evidence and interest meet</h3>
            <p class="gps-panel__intro">
              Fit combines practice evidence, optional interest, and recent growth.
              A stretch direction is a prompt to explore, not a closed door.
            </p>
          </div>
        </div>

        <div class="gps-directions">
          <article
            v-for="direction in data.directions"
            :key="direction.role_id"
            class="gps-direction"
            :class="`gps-direction--${direction.colour}`"
          >
            <div class="gps-direction__head">
              <div>
                <span class="gps-direction__family">{{ direction.family }}</span>
                <h4>{{ direction.title }}</h4>
              </div>
              <div class="gps-direction__fit">
                <strong>{{ direction.fit_score }}</strong>
                <span :class="`gps-fit gps-fit--${direction.colour}`">{{ direction.fit_label }}</span>
              </div>
            </div>

            <div class="gps-direction__bars">
              <div>
                <span>Evidence</span>
                <div class="gps-bar"><span :style="{ width: `${direction.evidence_score}%` }"></span></div>
                <small>{{ direction.evidence_score }}</small>
              </div>
              <div>
                <span>Interest</span>
                <div class="gps-bar gps-bar--interest">
                  <span :style="{ width: `${direction.interest_score ?? 0}%` }"></span>
                </div>
                <small>{{ direction.interest_score === null ? '—' : direction.interest_score }}</small>
              </div>
              <div>
                <span>Growth</span>
                <div class="gps-bar gps-bar--growth">
                  <span :style="{ width: `${direction.growth_score}%` }"></span>
                </div>
                <small>{{ direction.growth_score }}</small>
              </div>
            </div>

            <ul class="gps-why">
              <li v-for="reason in direction.why" :key="reason">{{ reason }}</li>
            </ul>

            <p class="gps-direction__next">
              <span>Try next</span>
              {{ direction.next_experiment }}
            </p>

            <p class="gps-direction__rating">
              Curriculum readiness: {{ direction.readiness_rating }}
            </p>
          </article>
        </div>

        <p v-if="data.pace" class="gps-pace">
          <strong>Pace:</strong> {{ data.pace }}
        </p>
      </section>

      <p class="gps-disclaimer">{{ data.disclaimer }}</p>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'
import { useGpsAnswers } from '../composables/useGpsAnswers'

const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const data = ref(null)
const { answers } = useGpsAnswers()

const hasAnswers = computed(() => Object.values(answers).some(Boolean))

const signalActive = computed(
  () => (data.value?.where_you_are?.recent_total || 0) > 0,
)
const signalClass = computed(() =>
  signalActive.value ? 'gps-signal--active' : 'gps-signal--idle',
)
const signalLabel = computed(() =>
  signalActive.value ? 'Signal active' : 'Signal fading',
)
const signalTitle = computed(() =>
  signalActive.value
    ? `${data.value?.where_you_are?.recent_total || 0} completion(s) in the last 30 days`
    : 'No completion in the last 30 days. One exercise restores the signal.',
)
const fadingDomains = computed(() =>
  (data.value?.where_you_are?.top_domains || []).filter(
    (domain) => domain.recent_count === 0 && domain.evidence_count > 0,
  ),
)

async function load(payload = {}) {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.post('/profile/gps', { answers: payload })
    data.value = response.data
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      'Could not load the GPS. The preview may not be enabled on this deployment.'
  } finally {
    loading.value = false
  }
}

async function submitAnswers() {
  submitting.value = true
  try {
    await load({ ...answers })
  } finally {
    submitting.value = false
  }
}

async function clearAnswers() {
  Object.keys(answers).forEach((key) => {
    delete answers[key]
  })
  submitting.value = true
  try {
    await load({})
  } finally {
    submitting.value = false
  }
}

onMounted(() => load())
</script>

<style scoped>
.gps {
  display: grid;
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.gps-hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) minmax(220px, 0.6fr);
  gap: 1rem;
  align-items: center;
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    radial-gradient(circle at 100% 0%, var(--accent-bg), transparent 55%),
    var(--bg-secondary);
}

.gps-hero__compass {
  position: relative;
  display: grid;
  place-items: center;
  width: 84px;
  height: 84px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  color: var(--text-muted);
  font-size: 0.56rem;
  font-weight: 700;
}

.gps-hero__compass span {
  position: absolute;
}

.gps-hero__compass span:nth-child(1) { top: 4px; }
.gps-hero__compass span:nth-child(2) { right: 6px; }
.gps-hero__compass span:nth-child(3) { bottom: 4px; }
.gps-hero__compass span:nth-child(4) { left: 6px; }

.gps-hero__compass i {
  width: 34px;
  height: 34px;
  border: 2px solid var(--accent);
  border-radius: 50% 50% 50% 4px;
  transform: rotate(45deg);
  background: var(--accent-bg);
}

.gps-eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.gps-hero__title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 750;
}

.gps-hero__intro {
  max-width: 58rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.gps-hero__privacy {
  margin: 0.45rem 0 0;
  color: var(--text-muted);
  font-size: 0.7rem;
  line-height: 1.45;
}

.gps-hero__privacy strong {
  color: var(--text-secondary);
}

.gps-hero__next {
  padding: 0.65rem 0.75rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  background: var(--accent-bg);
}

.gps-hero__next span {
  color: var(--accent-text);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.gps-hero__next p {
  margin: 0.2rem 0 0;
  color: var(--text-primary);
  font-size: 0.78rem;
  line-height: 1.45;
}

.gps-state {
  margin: 0;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.gps-state--error {
  border-color: var(--danger);
  color: var(--danger);
}

.gps-panel {
  padding: 0.9rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.gps-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.7rem;
}

.gps-panel__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 700;
}

.gps-panel__intro {
  max-width: 54rem;
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.45;
}

.gps-chip {
  flex: 0 0 auto;
  padding: 0.16rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.62rem;
  white-space: nowrap;
}

.gps-chip--active {
  border-color: var(--success);
  background: var(--success-bg);
  color: var(--success);
  font-weight: 700;
}

.gps-panel__chips {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.3rem;
}

.gps-signal {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.16rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  white-space: nowrap;
}

.gps-signal__dot {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: var(--text-muted);
}

.gps-signal--active {
  border-color: var(--success);
  color: var(--success);
}

.gps-signal--active .gps-signal__dot {
  background: var(--success);
  animation: gps-signal-pulse 1.8s ease-in-out infinite;
}

.gps-signal--idle {
  border-color: var(--warning);
  color: var(--warning);
}

.gps-signal--idle .gps-signal__dot {
  background: var(--warning);
  animation: gps-signal-fade 3.2s ease-in-out infinite;
}

.gps-growth .gps-signal--active { color: var(--success); font-weight: 600; }
.gps-growth .gps-signal--idle { color: var(--warning); font-weight: 600; }

.gps-revisit {
  margin: 0.35rem 0 0;
  padding: 0.45rem 0.55rem;
  border-left: 3px solid var(--warning);
  border-radius: 0 6px 6px 0;
  background: var(--warning-bg, var(--bg-primary));
  color: var(--text-secondary);
  font-size: 0.68rem;
  line-height: 1.45;
}

.gps-revisit strong { color: var(--warning); }

@keyframes gps-signal-pulse {
  0%, 100% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--success) 45%, transparent); }
  50% { box-shadow: 0 0 0 5px transparent; }
}

@keyframes gps-signal-fade {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 0.9; }
}

@media (prefers-reduced-motion: reduce) {
  .gps-signal__dot,
  .gps-domain--active .gps-dot,
  .gps-domain--idle .gps-dot {
    animation: none !important;
  }
}

.gps-where {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  gap: 0.75rem;
}

.gps-domains {
  display: grid;
  gap: 0.45rem;
}

.gps-domain {
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.gps-domain--green { border-left: 3px solid var(--success); }
.gps-domain--amber { border-left: 3px solid var(--warning); }
.gps-domain--red { border-left: 3px solid var(--danger); }
.gps-domain--grey { border-left: 3px solid var(--text-muted); }

.gps-domain__head {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  color: var(--text-primary);
  font-size: 0.74rem;
}

.gps-domain__head span {
  color: var(--text-muted);
  font-size: 0.68rem;
  font-variant-numeric: tabular-nums;
}

.gps-domain p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.62rem;
}

.gps-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  margin-right: 0.35rem;
  border-radius: 50%;
  background: var(--text-muted);
}

.gps-dot--green { background: var(--success); }
.gps-dot--amber { background: var(--warning); }
.gps-dot--red { background: var(--danger); }
.gps-dot--grey { background: var(--text-muted); }

.gps-domain--active .gps-dot {
  animation: gps-signal-pulse 1.8s ease-in-out infinite;
}

.gps-domain--idle .gps-dot {
  animation: gps-signal-fade 3.2s ease-in-out infinite;
}

.gps-domain--idle {
  border-style: dashed;
}

.gps-strengths {
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.gps-strengths ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.gps-strengths li {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.35rem 0;
  border-top: 1px solid var(--border-color);
}

.gps-strengths li:first-child {
  border-top: 0;
}

.gps-strengths strong {
  display: block;
  color: var(--text-primary);
  font-size: 0.72rem;
}

.gps-strengths div span {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.gps-score {
  flex: 0 0 auto;
  color: var(--accent-text);
  font-size: 0.72rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.gps-growth {
  margin: 0.6rem 0 0;
  padding-top: 0.55rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.66rem;
  line-height: 1.45;
}

.gps-growth strong {
  color: var(--text-secondary);
}

.gps-questions {
  display: grid;
  gap: 0.7rem;
}

.gps-question {
  margin: 0;
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.gps-question legend {
  padding: 0 0.25rem;
  color: var(--text-primary);
  font-size: 0.76rem;
  font-weight: 650;
}

.gps-question__help {
  margin: 0 0 0.45rem;
  color: var(--text-muted);
  font-size: 0.64rem;
}

.gps-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.gps-option {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.28rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.68rem;
  cursor: pointer;
}

.gps-option input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.gps-option:hover {
  border-color: var(--accent);
}

.gps-option--selected {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--accent-text);
  font-weight: 650;
}

.gps-option:focus-within {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.gps-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.gps-actions__note {
  color: var(--text-muted);
  font-size: 0.64rem;
}

.gps-directions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.6rem;
}

.gps-direction {
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.gps-direction--green { border-top: 3px solid var(--success); }
.gps-direction--amber { border-top: 3px solid var(--warning); }
.gps-direction--red { border-top: 3px solid var(--danger); }
.gps-direction--grey { border-top: 3px solid var(--text-muted); }

.gps-direction__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.gps-direction__family {
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.gps-direction h4 {
  margin: 0.1rem 0 0;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 700;
}

.gps-direction__fit {
  display: grid;
  justify-items: end;
  gap: 0.1rem;
}

.gps-direction__fit strong {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-variant-numeric: tabular-nums;
}

.gps-fit {
  padding: 0.1rem 0.35rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 0.54rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.gps-fit--green { background: var(--success-bg); color: var(--success); }
.gps-fit--amber { background: var(--warning-bg); color: var(--warning); }
.gps-fit--red { background: var(--danger-bg); color: var(--danger); }
.gps-fit--grey { background: var(--bg-tertiary); color: var(--text-muted); }

.gps-direction__bars {
  display: grid;
  gap: 0.25rem;
  margin: 0.5rem 0;
}

.gps-direction__bars > div {
  display: grid;
  grid-template-columns: 58px minmax(0, 1fr) 30px;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.58rem;
}

.gps-direction__bars small {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.gps-bar {
  height: 5px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.gps-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}

.gps-bar--interest span { background: var(--warning); }
.gps-bar--growth span { background: var(--success); }

.gps-why {
  margin: 0.4rem 0 0;
  padding-left: 1rem;
  color: var(--text-secondary);
  font-size: 0.66rem;
  line-height: 1.45;
}

.gps-why li {
  margin: 0.15rem 0;
}

.gps-direction__next {
  margin: 0.45rem 0 0;
  padding: 0.4rem 0.5rem;
  border-left: 2px solid var(--accent);
  border-radius: 0 6px 6px 0;
  background: var(--accent-bg);
  color: var(--text-primary);
  font-size: 0.66rem;
  line-height: 1.4;
}

.gps-direction__next span {
  display: block;
  color: var(--accent-text);
  font-size: 0.56rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.gps-direction__rating {
  margin: 0.4rem 0 0;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.gps-pace {
  margin: 0.7rem 0 0;
  padding: 0.5rem 0.6rem;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.45;
}

.gps-pace strong {
  color: var(--text-primary);
}

.gps-empty {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.gps-disclaimer {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.66rem;
  line-height: 1.45;
}

@media (max-width: 900px) {
  .gps-hero,
  .gps-where {
    grid-template-columns: minmax(0, 1fr);
  }

  .gps-hero__compass {
    display: none;
  }
}

@media (max-width: 640px) {
  .gps-panel__head {
    flex-direction: column;
  }

  .gps-direction__bars > div {
    grid-template-columns: 52px minmax(0, 1fr) 26px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .gps-hero__compass i {
    transition: none;
  }
}
</style>
