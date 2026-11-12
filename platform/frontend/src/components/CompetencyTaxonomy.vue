<template>
  <section class="taxonomy" aria-labelledby="taxonomy-title">
    <header class="taxonomy__head">
      <div>
        <p class="taxonomy__eyebrow">Competency taxonomy</p>
        <h2 id="taxonomy-title" class="taxonomy__title">Evidence by domain, category, and competency</h2>
        <p class="taxonomy__intro">
          Every competency is scored across knowledge, execution, troubleshooting,
          documentation, and communication. A score is provisional when one or more
          evidence dimensions are missing.
        </p>
      </div>
      <span v-if="data" class="taxonomy__version">v{{ data.version }}</span>
    </header>

    <p v-if="loading" class="taxonomy__state">Loading the competency profile…</p>
    <p v-else-if="error" class="taxonomy__state taxonomy__state--error" role="alert">{{ error }}</p>

    <template v-else-if="data">
      <div class="taxonomy-stats">
        <div><strong>{{ data.summary.domains }}</strong><span>domains</span></div>
        <div><strong>{{ data.summary.competencies }}</strong><span>competencies</span></div>
        <div><strong>{{ data.summary.competencies_with_evidence }}</strong><span>with evidence</span></div>
        <div><strong>{{ data.summary.average_score ?? '—' }}</strong><span>average score</span></div>
      </div>

      <div class="taxonomy-domains">
        <details
          v-for="domain in data.domains"
          :key="domain.id"
          class="taxonomy-domain"
          :open="domain.evidence_count > 0"
        >
          <summary class="taxonomy-domain__summary">
            <span class="taxonomy-domain__id">{{ domain.id }}</span>
            <span class="taxonomy-domain__label">{{ domain.label }}</span>
            <span class="taxonomy-domain__count">{{ domain.evidence_count }} evidence</span>
          </summary>
          <p class="taxonomy-domain__intro">{{ domain.description }}</p>
          <div
            v-for="category in domain.categories"
            :key="category.id"
            class="taxonomy-category"
          >
            <h4>{{ category.label }}</h4>
            <div class="taxonomy-competencies">
              <article
                v-for="competency in category.competencies"
                :key="competency.id"
                class="taxonomy-competency"
                :class="{
                  'taxonomy-competency--awarded': competency.assessment?.awarded,
                  'taxonomy-competency--empty': !competency.evidence_count,
                }"
              >
                <div class="taxonomy-competency__head">
                  <div>
                    <span class="taxonomy-competency__id">{{ competency.id }}</span>
                    <strong>{{ competency.name }}</strong>
                  </div>
                  <span
                    class="taxonomy-chip"
                    :class="`taxonomy-chip--${competency.assessment?.level?.id || 'no_evidence'}`"
                  >
                    {{ competency.assessment?.level?.badge || competency.evidence_label }}
                  </span>
                </div>
                <div class="taxonomy-competency__meta">
                  <span>{{ competency.evidence_count }} evidence</span>
                  <span v-if="competency.assessment?.score !== null">
                    Score {{ competency.assessment.score }}/100
                  </span>
                  <span v-if="competency.assessment?.provisional">Provisional</span>
                  <span v-if="competency.assessment?.awarded" class="taxonomy-awarded">Validated</span>
                </div>
                <div
                  v-if="competency.assessment?.dimensions"
                  class="taxonomy-dimensions"
                >
                  <div
                    v-for="dimension in competency.assessment.dimensions"
                    :key="dimension.key"
                    class="taxonomy-dimension"
                  >
                    <span>{{ dimension.label }}</span>
                    <div class="taxonomy-dimension__bar">
                      <span :style="{ width: (dimension.score || 0) + '%' }"></span>
                    </div>
                    <small>{{ dimension.score !== null ? dimension.score : '—' }}</small>
                  </div>
                </div>
                <p v-else class="taxonomy-empty">No assessment evidence yet.</p>
              </article>
            </div>
          </div>
        </details>
      </div>

      <p class="taxonomy__note">{{ data.disclaimer }}</p>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '../api/axios'

const loading = ref(true)
const error = ref('')
const data = ref(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/profile/competencies')
    data.value = response.data
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      'Could not load the competency taxonomy. The preview may not be enabled on this deployment.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.taxonomy {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.taxonomy__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.taxonomy__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.taxonomy__title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 700;
}

.taxonomy__intro {
  max-width: 58rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.5;
}

.taxonomy__version {
  flex: 0 0 auto;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.64rem;
}

.taxonomy__state {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.taxonomy__state--error {
  color: var(--danger);
}

.taxonomy-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.55rem;
  margin-bottom: 0.75rem;
}

.taxonomy-stats div {
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.taxonomy-stats strong {
  display: block;
  color: var(--text-primary);
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.taxonomy-stats span {
  color: var(--text-muted);
  font-size: 0.62rem;
}

.taxonomy-domains {
  display: grid;
  gap: 0.55rem;
}

.taxonomy-domain {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.taxonomy-domain__summary {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.6rem 0.7rem;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 0.8rem;
  font-weight: 650;
}

.taxonomy-domain__id {
  color: var(--accent-text);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.62rem;
}

.taxonomy-domain__count {
  margin-left: auto;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 400;
}

.taxonomy-domain__intro {
  margin: 0;
  padding: 0 0.7rem 0.5rem;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.taxonomy-category {
  padding: 0 0.7rem 0.7rem;
}

.taxonomy-category h4 {
  margin: 0.35rem 0 0.45rem;
  color: var(--text-secondary);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.taxonomy-competencies {
  display: grid;
  gap: 0.45rem;
}

.taxonomy-competency {
  padding: 0.55rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.taxonomy-competency--awarded {
  border-left: 3px solid var(--success);
}

.taxonomy-competency--empty {
  opacity: 0.78;
}

.taxonomy-competency__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.taxonomy-competency__id {
  display: block;
  color: var(--text-muted);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.58rem;
}

.taxonomy-competency__head strong {
  display: block;
  color: var(--text-primary);
  font-size: 0.74rem;
}

.taxonomy-chip {
  flex: 0 0 auto;
  padding: 0.12rem 0.4rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.56rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.taxonomy-chip--independent,
.taxonomy-chip--applied,
.taxonomy-chip--professional {
  background: var(--success-bg);
  color: var(--success);
}

.taxonomy-chip--guided {
  background: var(--warning-bg);
  color: var(--warning);
}

.taxonomy-chip--awareness {
  background: var(--accent-bg);
  color: var(--accent-text);
}

.taxonomy-competency__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem 0.6rem;
  margin-top: 0.25rem;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.taxonomy-awarded {
  color: var(--success);
  font-weight: 700;
}

.taxonomy-dimensions {
  display: grid;
  gap: 0.2rem;
  margin-top: 0.4rem;
}

.taxonomy-dimension {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr) 28px;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.58rem;
}

.taxonomy-dimension__bar {
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.taxonomy-dimension__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}

.taxonomy-dimension small {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.taxonomy-empty {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
  font-size: 0.64rem;
}

.taxonomy__note {
  margin: 0.75rem 0 0;
  color: var(--text-muted);
  font-size: 0.66rem;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .taxonomy__head {
    flex-direction: column;
  }

  .taxonomy-dimension {
    grid-template-columns: 78px minmax(0, 1fr) 24px;
  }
}
</style>
