<template>
  <section class="learning-analytics" aria-labelledby="learning-analytics-title">
    <div class="learning-analytics__head">
      <span class="learning-analytics__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 3v18h18" />
          <path d="m7 14 4-4 3 3 5-6" />
        </svg>
      </span>
      <div>
        <h2 id="learning-analytics-title">Learning analytics</h2>
        <p>Your own progress, not a ranking. Indicators are descriptive, not grades.</p>
      </div>
    </div>

    <p v-if="loading" class="learning-analytics__state">Loading your learning analytics...</p>
    <p v-else-if="error" class="learning-analytics__state learning-analytics__state--error" role="alert">
      {{ error }}
    </p>

    <template v-else-if="data">
      <div class="learning-stat-grid">
        <article class="learning-stat">
          <span class="learning-stat__label">Completion</span>
          <strong>{{ data.summary.completed_exercises }}<small>/{{ data.summary.started_exercises }}</small></strong>
          <span class="learning-stat__detail">exercises started</span>
        </article>
        <article class="learning-stat">
          <span class="learning-stat__label">Learning time</span>
          <strong>{{ data.summary.total_learning_hours ?? 0 }}<small> h</small></strong>
          <span class="learning-stat__detail">{{ data.summary.total_learning_minutes ?? 0 }} min across started exercises</span>
        </article>
        <article class="learning-stat">
          <span class="learning-stat__label">Median time</span>
          <strong>{{ data.summary.median_time_minutes ?? '—' }}<small v-if="data.summary.median_time_minutes !== null"> min</small></strong>
          <span class="learning-stat__detail">per completed exercise</span>
        </article>
        <article class="learning-stat">
          <span class="learning-stat__label">Hint-free</span>
          <strong>{{ data.summary.hint_free_rate }}<small>%</small></strong>
          <span class="learning-stat__detail">{{ data.summary.hints_per_completion }} hints per completion</span>
        </article>
        <article class="learning-stat">
          <span class="learning-stat__label">First attempt</span>
          <strong>{{ data.summary.first_attempt_rate }}<small>%</small></strong>
          <span class="learning-stat__detail">{{ data.summary.reattempt_rate }}% needed a reattempt</span>
        </article>
      </div>

      <div class="growth-head">
        <h3>Growth indicators</h3>
        <span>Compared with your earlier exercises</span>
      </div>
      <div class="growth-grid">
        <article
          v-for="item in data.growth"
          :key="item.label"
          class="growth-card"
          :class="`growth-card--${item.status}`"
        >
          <div class="growth-card__top">
            <span class="growth-card__label">{{ item.label }}</span>
            <span class="growth-card__status">{{ statusLabel(item.status) }}</span>
          </div>
          <strong v-if="item.value !== undefined" class="growth-card__value">
            {{ item.value }} <small>{{ item.unit }}</small>
          </strong>
          <strong v-else class="growth-card__value">
            {{ item.latest ?? '—' }} <small>{{ item.unit }}</small>
          </strong>
          <p>{{ item.explanation }}</p>
        </article>
      </div>

      <div class="impact-grid">
        <article class="impact-card">
          <span>Learning reported</span>
          <strong>{{ data.learning_impact.learning_reported ?? '—' }}<small v-if="data.learning_impact.learning_reported !== null">/5</small></strong>
          <p>From {{ data.summary.pulse_responses }} pulse {{ data.summary.pulse_responses === 1 ? 'response' : 'responses' }}</p>
        </article>
        <article class="impact-card">
          <span>Completion rate</span>
          <strong>{{ data.learning_impact.completion_rate }}<small>%</small></strong>
          <p>Of exercises you started</p>
        </article>
        <article class="impact-card">
          <span>Confidence gain</span>
          <strong>{{ data.learning_impact.confidence_gain !== null ? `${data.learning_impact.confidence_gain > 0 ? '+' : ''}${data.learning_impact.confidence_gain}` : '—' }}</strong>
          <p>Performance-growth proxy, not a psychological score</p>
        </article>
      </div>

      <div v-if="data.domains?.length" class="domains">
        <div class="growth-head">
          <h3>Competency growth by domain</h3>
          <span>Evidence grows with completed exercises</span>
        </div>
        <div class="domain-grid">
          <article
            v-for="domain in data.domains"
            :key="domain.key"
            class="domain-card"
            :class="`domain-card--${domain.growth_status}`"
          >
            <div class="domain-card__head">
              <strong>{{ domain.label }}</strong>
              <span>{{ domain.completed_exercises ? domainStatusLabel(domain.growth_status) : 'No evidence yet' }}</span>
            </div>
            <div class="domain-card__numbers">
              <span><b>{{ domain.completed_exercises }}</b> completed</span>
              <span><b>{{ domain.hint_free_rate }}%</b> hint-free</span>
              <span><b>{{ domain.first_attempt_rate }}%</b> first try</span>
            </div>
            <div class="domain-card__bar" aria-hidden="true">
              <span :style="{ width: Math.min(100, domain.completed_exercises * 12.5) + '%' }"></span>
            </div>
            <small>{{ evidenceLabel(domain.evidence_level) }}</small>
          </article>
        </div>
      </div>

      <CompetencyRadar
        v-if="data.competency_radar"
        :data="data.competency_radar"
      />

      <div v-if="data.ai_prompts?.length" class="ai-prompts">
        <div class="growth-head">
          <h3>AI practice prompts</h3>
          <span>Copy into your own AI assistant for coaching, not answers</span>
        </div>
        <div class="ai-prompt-grid">
          <article
            v-for="prompt in data.ai_prompts"
            :key="prompt.id"
            class="ai-prompt-card"
          >
            <div class="ai-prompt-card__head">
              <strong>{{ prompt.title }}</strong>
              <button
                type="button"
                class="ai-prompt-card__copy"
                @click="copyText(prompt.prompt, prompt.id)"
              >
                {{ copied === prompt.id ? 'Copied' : 'Copy prompt' }}
              </button>
            </div>
            <p class="ai-prompt-card__reason">{{ prompt.reason }}</p>
            <p class="ai-prompt-card__text">{{ prompt.prompt }}</p>
          </article>
        </div>
        <p class="ai-prompts__note">
          These prompts ask an AI to coach you with questions. They do not include
          your account details, flags, or another learner's data.
        </p>
      </div>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '../api/axios'
import { useClipboard } from '../composables/useClipboard'
import CompetencyRadar from './CompetencyRadar.vue'

const { copied, copyText } = useClipboard()
const data = ref(null)
const loading = ref(true)
const error = ref('')

const statusLabel = (status) => ({
  improving: 'Improving',
  steady: 'Steady',
  needs_attention: 'Needs attention',
  insufficient_evidence: 'More evidence needed',
}[status] || status)

const domainStatusLabel = (status) => ({
  improving: 'Improving',
  steady: 'Steady',
  needs_attention: 'Needs attention',
  insufficient_evidence: 'Building evidence',
}[status] || status)

const evidenceLabel = (level) => ({
  no_evidence: 'No evidence yet',
  early: 'Early evidence',
  growing: 'Growing evidence',
  strong: 'Strong evidence',
}[level] || level)

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/analytics/student/me')
    data.value = response.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load your learning analytics.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.learning-analytics {
  margin-top: 1rem;
  padding: 1.15rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background:
    radial-gradient(circle at 100% 0%, color-mix(in srgb, var(--accent) 9%, transparent), transparent 48%),
    var(--bg-secondary);
}

.learning-analytics__head {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.learning-analytics__icon {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--accent-bg);
  color: var(--accent);
}

.learning-analytics__icon svg {
  width: 19px;
  height: 19px;
}

.learning-analytics h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.05rem;
}

.learning-analytics__head p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.learning-analytics__state {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.learning-analytics__state--error {
  color: var(--danger);
}

.learning-stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.5rem;
}

.learning-stat {
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.learning-stat__label {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.learning-stat strong {
  display: block;
  margin: 0.15rem 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-variant-numeric: tabular-nums;
}

.learning-stat strong small {
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 600;
}

.learning-stat__detail {
  color: var(--text-muted);
  font-size: 0.62rem;
}

.growth-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin: 1rem 0 0.5rem;
}

.growth-head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.78rem;
}

.growth-head span {
  color: var(--text-muted);
  font-size: 0.62rem;
}

.growth-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.5rem;
}

.growth-card {
  --growth-accent: var(--accent);
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--growth-accent);
  border-radius: 10px;
  background: var(--bg-primary);
}

.growth-card--improving { --growth-accent: var(--success); }
.growth-card--needs_attention { --growth-accent: var(--warning); }
.growth-card--insufficient_evidence { --growth-accent: var(--text-muted); }

.growth-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
}

.growth-card__label {
  color: var(--text-primary);
  font-size: 0.7rem;
  font-weight: 700;
}

.growth-card__status {
  color: var(--growth-accent);
  font-size: 0.56rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.growth-card__value {
  display: block;
  margin: 0.25rem 0 0.15rem;
  color: var(--text-primary);
  font-size: 1rem;
}

.growth-card__value small {
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 500;
}

.growth-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.64rem;
  line-height: 1.45;
}

.impact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.impact-card {
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.impact-card span {
  display: block;
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.impact-card strong {
  display: block;
  margin: 0.1rem 0;
  color: var(--text-primary);
  font-size: 1.05rem;
}

.impact-card strong small {
  color: var(--text-muted);
  font-size: 0.65rem;
}

.impact-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.domains {
  margin-top: 1rem;
  padding-top: 0.9rem;
  border-top: 1px solid var(--border-color);
}

.domain-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.domain-card {
  --domain-accent: var(--accent);
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--domain-accent);
  border-radius: 10px;
  background: var(--bg-primary);
}

.domain-card--improving { --domain-accent: var(--success); }
.domain-card--needs_attention { --domain-accent: var(--warning); }
.domain-card--insufficient_evidence { --domain-accent: var(--text-muted); }

.domain-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
}

.domain-card__head strong {
  color: var(--text-primary);
  font-size: 0.72rem;
}

.domain-card__head span {
  color: var(--domain-accent);
  font-size: 0.55rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.domain-card__numbers {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 0.35rem 0;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.domain-card__numbers b {
  color: var(--text-secondary);
}

.domain-card__bar {
  height: 3px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.domain-card__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--domain-accent);
}

.domain-card small {
  display: block;
  margin-top: 0.3rem;
  color: var(--text-muted);
  font-size: 0.58rem;
}

.ai-prompts {
  margin-top: 1rem;
  padding-top: 0.9rem;
  border-top: 1px solid var(--border-color);
}

.ai-prompt-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.55rem;
}

.ai-prompt-card {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 11px;
  background: var(--bg-primary);
}

.ai-prompt-card__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.ai-prompt-card__head strong {
  color: var(--text-primary);
  font-size: 0.72rem;
}

.ai-prompt-card__copy {
  flex-shrink: 0;
  padding: 0.1rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: transparent;
  color: var(--accent);
  font-size: 0.58rem;
  font-weight: 700;
  cursor: pointer;
}

.ai-prompt-card__copy:hover {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.ai-prompt-card__reason {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.6rem;
  font-style: italic;
}

.ai-prompt-card__text {
  display: -webkit-box;
  margin: 0.15rem 0 0;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 0.65rem;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 5;
}

.ai-prompts__note {
  margin: 0.5rem 0 0;
  color: var(--text-muted);
  font-size: 0.6rem;
}
</style>
