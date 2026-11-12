<template>
  <section class="demand" aria-labelledby="demand-title">
    <div class="demand__head">
      <div>
        <p class="demand__eyebrow">Curriculum demand</p>
        <h2 id="demand-title">Where to build more exercises</h2>
        <p class="demand__intro">
          Aggregate telemetry turned into planning prompts: what learners asked
          for, where exercises create friction, and which competencies have thin
          evidence. Every prompt keeps its sample size.
        </p>
      </div>
      <span v-if="data?.state === 'available'" class="demand__scope">
        {{ data.courses_reporting }} of {{ data.courses_total }} courses reporting
      </span>
    </div>

    <p v-if="loading" class="demand-state">Reading curriculum telemetry…</p>
    <p v-else-if="error" class="demand-state demand-state--error" role="alert">{{ error }}</p>

    <template v-else-if="data">
      <div v-if="data.state !== 'available'" class="demand-suppressed" role="status">
        <strong>
          {{ data.state === 'suppressed' ? 'Cohort suppressed' : 'No evidence yet' }}
        </strong>
        <p>{{ data.reason }}</p>
      </div>

      <template v-else>
        <div class="demand-summary">
          <article class="demand-stat demand-stat--red">
            <span>High priority</span>
            <strong>{{ data.summary.high }}</strong>
            <small>build or rework next</small>
          </article>
          <article class="demand-stat demand-stat--amber">
            <span>Watch</span>
            <strong>{{ data.summary.medium }}</strong>
            <small>check before the next run</small>
          </article>
          <article class="demand-stat">
            <span>Topic requests</span>
            <strong>{{ data.summary.topic_demand }}</strong>
            <small>learner-requested areas</small>
          </article>
          <article class="demand-stat">
            <span>Friction points</span>
            <strong>{{ data.summary.exercise_friction }}</strong>
            <small>exercises to scaffold</small>
          </article>
          <article class="demand-stat">
            <span>Competency gaps</span>
            <strong>{{ data.summary.competency_gap }}</strong>
            <small>domains with thin coverage</small>
          </article>
        </div>

        <div v-if="data.topics.length" class="demand-topics" aria-label="Requested topics">
          <span class="demand-topics__label">Learners asked for</span>
          <span v-for="topic in data.topics" :key="topic.key" class="demand-topic">
            {{ topic.label }} <b>{{ topic.count }}</b>
          </span>
        </div>

        <div v-if="data.recommendations.length" class="demand-list">
          <article
            v-for="item in data.recommendations"
            :key="item.id"
            class="demand-card"
            :class="`demand-card--${item.colour}`"
          >
            <div class="demand-card__head">
              <div>
                <span class="demand-card__kind">{{ kindLabel(item.kind) }}</span>
                <h3>{{ item.title }}</h3>
              </div>
              <span class="demand-priority" :class="`demand-priority--${item.priority}`">
                {{ item.priority }}
              </span>
            </div>
            <p class="demand-card__rationale">{{ item.rationale }}</p>
            <p class="demand-card__evidence">
              <span>Evidence</span>{{ item.evidence }}
              <template v-if="item.course"> · {{ item.course.code }}</template>
            </p>
            <p class="demand-card__action">
              <span>Suggested action</span>{{ item.action }}
            </p>
          </article>
        </div>
        <p v-else class="demand-empty">
          No build prompts right now. Keep collecting pulse responses and completions.
        </p>

        <p class="demand-note">{{ data.disclaimer }}</p>
      </template>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '../api/axios'

const data = ref(null)
const loading = ref(true)
const error = ref('')

function kindLabel(kind) {
  return {
    topic_demand: 'Topic demand',
    exercise_friction: 'Exercise friction',
    competency_gap: 'Competency gap',
  }[kind] || 'Signal'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/analytics/reports/curriculum-demand')
    data.value = response.data
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      'Could not load curriculum demand. Instructor access is required.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.demand {
  margin: 1rem 0;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.demand__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.demand__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.demand__head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.05rem;
  font-weight: 750;
}

.demand__intro {
  max-width: 58rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.5;
}

.demand__scope {
  flex: 0 0 auto;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.62rem;
  white-space: nowrap;
}

.demand-state {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.demand-state--error {
  color: var(--danger);
}

.demand-suppressed {
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--warning);
  border-radius: 8px;
  background: var(--warning-bg);
}

.demand-suppressed strong {
  color: var(--text-primary);
  font-size: 0.8rem;
}

.demand-suppressed p {
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.demand-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.demand-stat {
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.demand-stat--red { border-left: 3px solid var(--danger); }
.demand-stat--amber { border-left: 3px solid var(--warning); }

.demand-stat span {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.demand-stat strong {
  display: block;
  color: var(--text-primary);
  font-size: 1.15rem;
  font-variant-numeric: tabular-nums;
}

.demand-stat small {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.demand-topics {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.demand-topics__label {
  margin-right: 0.2rem;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.demand-topic {
  padding: 0.16rem 0.45rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.64rem;
}

.demand-topic b {
  color: var(--accent-text);
  font-variant-numeric: tabular-nums;
}

.demand-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.6rem;
}

.demand-card {
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.demand-card--red { border-left: 3px solid var(--danger); }
.demand-card--amber { border-left: 3px solid var(--warning); }
.demand-card--green { border-left: 3px solid var(--success); }

.demand-card__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.demand-card__kind {
  color: var(--text-muted);
  font-size: 0.56rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.demand-card h3 {
  margin: 0.1rem 0 0;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 700;
}

.demand-priority {
  flex: 0 0 auto;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 0.54rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.demand-priority--high { background: var(--danger-bg); color: var(--danger); }
.demand-priority--medium { background: var(--warning-bg); color: var(--warning); }
.demand-priority--low { background: var(--bg-tertiary); color: var(--text-muted); }

.demand-card__rationale {
  margin: 0.4rem 0 0;
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.45;
}

.demand-card__evidence,
.demand-card__action {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.64rem;
  line-height: 1.45;
}

.demand-card__evidence span,
.demand-card__action span {
  display: block;
  color: var(--text-muted);
  font-size: 0.56rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.demand-card__action {
  padding: 0.4rem 0.5rem;
  border-left: 2px solid var(--accent);
  border-radius: 0 6px 6px 0;
  background: var(--accent-bg);
  color: var(--text-secondary);
}

.demand-card__action span {
  color: var(--accent-text);
}

.demand-empty {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.demand-note {
  margin: 0.75rem 0 0;
  color: var(--text-muted);
  font-size: 0.64rem;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .demand__head {
    flex-direction: column;
  }
}
</style>
