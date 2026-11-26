<template>
  <article class="exercise-brief" :class="{ 'exercise-brief--popout': popout }">
    <header class="exercise-brief__header">
      <div class="exercise-brief__heading">
        <p class="exercise-brief__eyebrow">Briefing</p>
        <h2 class="exercise-brief__title">{{ lab.name }}</h2>
        <p v-if="meta" class="exercise-brief__meta">{{ meta }}</p>
      </div>
      <div v-if="!popout" class="exercise-brief__actions">
        <button
          type="button"
          class="btn btn--secondary btn--sm"
          @click="$emit('pop-out')"
        >
          Pop out briefing
        </button>
      </div>
    </header>

    <section class="exercise-brief__section" aria-labelledby="exercise-brief-scenario">
      <h3 id="exercise-brief-scenario" class="exercise-brief__section-title">Scenario</h3>
      <!-- security-delta: allow Vue v-html (DOMPurify.sanitize) -->
      <div v-if="scenarioHtml" class="exercise-brief__scenario" v-html="scenarioHtml"></div>
      <p v-else class="exercise-brief__empty">
        This exercise has no written scenario. Start the desktop and inspect the
        network, or follow the workbook walkthrough.
      </p>
    </section>

    <section
      v-if="objectives.length"
      class="exercise-brief__section"
      aria-labelledby="exercise-brief-objectives"
    >
      <h3 id="exercise-brief-objectives" class="exercise-brief__section-title">
        By completion you will be able to
      </h3>
      <ul class="exercise-brief__objectives">
        <li v-for="(objective, index) in objectives" :key="index">{{ objective }}</li>
      </ul>
    </section>

    <section
      v-if="hostnames.length"
      class="exercise-brief__section"
      aria-labelledby="exercise-brief-hostnames"
    >
      <h3 id="exercise-brief-hostnames" class="exercise-brief__section-title">
        Target hostnames
      </h3>
      <ul class="exercise-brief__hosts">
        <li v-for="(host, index) in hostnames" :key="`${host.hostname}-${index}`">
          <span class="exercise-brief__hostname">{{ host.hostname }}</span>
          <code v-if="host.ip" class="exercise-brief__host-ip">{{ host.ip }}</code>
          <span v-if="host.description" class="exercise-brief__host-description">
            {{ host.description }}
          </span>
        </li>
      </ul>
      <p class="exercise-brief__note">
        Lab DNS resolves these names automatically inside RangeBox.
      </p>
    </section>

    <section
      v-if="lab.workbook"
      class="exercise-brief__section"
      aria-labelledby="exercise-brief-workbook"
    >
      <h3 id="exercise-brief-workbook" class="exercise-brief__section-title">Workbook</h3>
      <template v-if="workbookHref">
        <a
          :href="workbookHref"
          class="exercise-brief__workbook-link"
          target="_blank"
          rel="noopener noreferrer"
          @click.prevent="$emit('open-workbook')"
        >
          Open workbook walkthrough
        </a>
        <p class="exercise-brief__note">Opens in a new tab.</p>
      </template>
      <p v-else class="exercise-brief__note">
        This exercise's walkthrough lives in a course workbook. Open the exercise
        from the course to read it.
      </p>
    </section>

    <section
      v-if="hintsTotal"
      class="exercise-brief__section"
      aria-labelledby="exercise-brief-hints"
    >
      <h3 id="exercise-brief-hints" class="exercise-brief__section-title">
        Hints you have unlocked
      </h3>
      <div v-for="(hint, index) in hints" :key="index" class="exercise-brief__hint">
        <p class="exercise-brief__hint-number">Hint {{ hint.number || index + 1 }}</p>
        <!-- security-delta: allow Vue v-html (DOMPurify.sanitize) -->
        <div v-html="renderLabMarkdown(hint.text)"></div>
      </div>
      <p v-if="hints.length === 0" class="exercise-brief__note">
        No hints requested yet. Request hints from the Exercise tab.
      </p>
    </section>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { renderLabMarkdown } from '../utils/markdown'
import { safeHttpUrl } from '../utils/url'

const props = defineProps({
  lab: { type: Object, required: true },
  track: { type: Object, default: null },
  level: { type: Object, default: null },
  hostnames: { type: Array, default: () => [] },
  hints: { type: Array, default: () => [] },
  workbookUrl: { type: String, default: '' },
  popout: { type: Boolean, default: false },
})

defineEmits(['pop-out', 'open-workbook'])

const scenarioHtml = computed(() =>
  renderLabMarkdown(props.lab?.scenario, { unwrap: true })
)

const objectives = computed(() =>
  Array.isArray(props.lab?.objectives) ? props.lab.objectives : []
)

const hostnames = computed(() =>
  Array.isArray(props.hostnames) ? props.hostnames : []
)

const hints = computed(() => (Array.isArray(props.hints) ? props.hints : []))

const hintsTotal = computed(() =>
  Number(props.lab?.hints_total || props.lab?.hints_available || 0)
)

const workbookHref = computed(() => safeHttpUrl(props.workbookUrl))

const meta = computed(() => {
  const parts = []
  if (props.track?.name) parts.push(props.track.name)
  if (props.level?.number) parts.push(`Level ${props.level.number}`)
  if (props.level?.name) parts.push(props.level.name)
  if (props.lab?.difficulty) parts.push(props.lab.difficulty)
  return parts.join(' · ')
})
</script>

<style scoped>
.exercise-brief {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  gap: 1.15rem;
  min-height: 0;
  padding: 1rem;
  overflow-y: auto;
  color: var(--text-primary);
}

.exercise-brief--popout {
  padding: 0;
  overflow: visible;
}

.exercise-brief__header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.75rem 1rem;
}

.exercise-brief__heading {
  flex: 1 1 16rem;
  min-width: 0;
}

.exercise-brief__eyebrow {
  margin: 0 0 0.15rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.exercise-brief__title {
  margin: 0;
  font-size: 1.25rem;
  line-height: 1.3;
}

.exercise-brief__meta {
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.exercise-brief__actions {
  margin-left: auto;
}

.exercise-brief__section {
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.exercise-brief__section-title {
  margin: 0 0 0.55rem;
  font-size: 0.95rem;
}

.exercise-brief__scenario {
  line-height: 1.6;
}

.exercise-brief__scenario :deep(p) {
  margin: 0 0 0.7rem;
}

.exercise-brief__scenario :deep(p:last-child) {
  margin-bottom: 0;
}

.exercise-brief__scenario :deep(pre) {
  overflow-x: auto;
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
}

.exercise-brief__scenario :deep(code) {
  overflow-wrap: anywhere;
}

.exercise-brief__objectives,
.exercise-brief__hosts {
  margin: 0;
  padding-left: 1.2rem;
}

.exercise-brief__objectives li,
.exercise-brief__hosts li {
  margin-bottom: 0.45rem;
}

.exercise-brief__hostname {
  display: block;
  font-weight: 600;
}

.exercise-brief__host-ip {
  display: inline-block;
  margin-top: 0.1rem;
  padding: 0.05rem 0.3rem;
  border-radius: 4px;
  background: var(--bg-secondary);
  font-size: 0.8rem;
}

.exercise-brief__host-description {
  display: block;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.exercise-brief__workbook-link {
  font-weight: 600;
  color: var(--text-primary);
  text-decoration: underline;
  text-underline-offset: 0.15em;
}

.exercise-brief__hint {
  margin-bottom: 0.8rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
}

.exercise-brief__hint-number {
  margin: 0 0 0.25rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.exercise-brief__hint :deep(p) {
  margin: 0 0 0.5rem;
}

.exercise-brief__hint :deep(p:last-child) {
  margin-bottom: 0;
}

.exercise-brief__note,
.exercise-brief__empty {
  margin: 0.45rem 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

@media (max-width: 480px) {
  .exercise-brief {
    padding: 0.75rem;
  }

  .exercise-brief__actions,
  .exercise-brief__actions .btn {
    width: 100%;
    margin-left: 0;
  }
}

@media print {
  .exercise-brief {
    padding: 0;
    color: #111;
  }

  .exercise-brief__actions {
    display: none;
  }

  .exercise-brief__section {
    break-inside: avoid;
  }
}
</style>
