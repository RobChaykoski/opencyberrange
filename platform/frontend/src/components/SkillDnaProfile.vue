<template>
  <section v-if="dna" class="dna-section" aria-labelledby="dna-title">
    <div class="dna-section__head">
      <div>
        <p class="dna-section__eyebrow">Learner character sheet</p>
        <h2 id="dna-title" class="section-title">Cyber DNA</h2>
        <p class="dna-section__intro">
          Five traits built from your range activity. They describe what you have practised,
          not what you are capable of. Pick a title from your achievements and grow the rest.
        </p>
      </div>
      <span class="dna-formula" :title="`Formula version ${dna.formula_version}`">
        v{{ dna.formula_version }}
      </span>
    </div>

    <div class="dna-layout">
      <aside class="dna-class-card" :class="`dna-class-card--${dna.class.key}`">
        <div class="dna-class-card__top">
          <span class="dna-class-card__sigil" aria-hidden="true">
            {{ classInitial }}
          </span>
          <div>
            <p class="dna-class-card__eyebrow">Current class</p>
            <h3 class="dna-class-card__name">{{ dna.class.class_name }}</h3>
            <p class="dna-class-card__trait">{{ dna.class.label }} · {{ dna.tier }}</p>
          </div>
        </div>

        <div class="dna-class-card__score">
          <span class="dna-class-card__score-value">{{ dna.overall }}</span>
          <span class="dna-class-card__score-label">overall</span>
        </div>
        <div
          class="dna-class-card__bar"
          role="progressbar"
          :aria-valuenow="dna.overall"
          aria-valuemin="0"
          aria-valuemax="100"
          :aria-label="`Overall Cyber DNA score: ${dna.overall} out of 100`"
        >
          <span :style="{ width: dna.overall + '%' }"></span>
        </div>

        <div class="dna-class-card__title">
          <span class="dna-class-card__title-label">Equipped title</span>
          <span class="title-chip" :class="`title-chip--${dna.titles.equipped.rarity}`">
            {{ dna.titles.equipped.label }}
          </span>
        </div>
        <p class="dna-class-card__title-note">
          {{ dna.titles.unlocked_count }} title{{ dna.titles.unlocked_count === 1 ? '' : 's' }} unlocked
          · {{ dna.titles.rare_count }} rare or better
        </p>
      </aside>

      <div class="dna-traits">
        <article
          v-for="dim in dna.dimensions"
          :key="dim.key"
          class="dna-trait"
          :class="`dna-trait--${dim.key}`"
        >
          <div class="dna-trait__head">
            <div>
              <span class="dna-trait__label">{{ dim.label }}</span>
              <span class="dna-trait__class">{{ dim.class_name }} · {{ dim.tier }}</span>
            </div>
            <span class="dna-trait__score">{{ dim.score }}</span>
          </div>
          <div
            class="dna-trait__bar"
            role="progressbar"
            :aria-valuenow="dim.score"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`${dim.label}: ${dim.score} out of 100`"
          >
            <span :style="{ width: dim.score + '%' }"></span>
          </div>
          <p class="dna-trait__evidence">{{ dim.evidence }}</p>
          <p class="dna-trait__next">{{ dim.next_step }}</p>
        </article>
      </div>
    </div>

    <div class="dna-alignment">
      <div class="dna-alignment__head">
        <div>
          <p class="dna-section__eyebrow">Career alignment</p>
          <h3 class="dna-alignment__title">{{ dna.class.certification_focus }}</h3>
          <p class="dna-alignment__summary">{{ certificationPath.summary }}</p>
        </div>
        <a
          class="dna-alignment__link"
          :href="CERTIFICATION_ROADMAP_URL"
          target="_blank"
          rel="noopener noreferrer"
        >
          Certification roadmap
        </a>
      </div>

      <div class="dna-cert-grid">
        <div class="dna-cert">
          <span>Start here</span>
          <p>{{ certificationPath.entry.join(' · ') }}</p>
        </div>
        <div class="dna-cert">
          <span>Build on it</span>
          <p>{{ certificationPath.core.join(' · ') }}</p>
        </div>
        <div class="dna-cert">
          <span>Go further</span>
          <p>{{ certificationPath.advanced.join(' · ') }}</p>
        </div>
      </div>
      <p class="dna-alignment__roles">
        <strong>Roles:</strong> {{ certificationPath.roles.join(' · ') }}
      </p>
    </div>

    <details class="dna-titles">
      <summary class="dna-titles__summary">
        <span>Title collection</span>
        <span class="dna-titles__count">{{ dna.titles.unlocked_count }} unlocked</span>
      </summary>
      <p class="dna-titles__intro">
        Titles are cosmetic. Equip one unlocked title; your class title returns when you clear it.
      </p>
      <div class="dna-title-grid">
        <article
          v-for="title in sortedTitles"
          :key="title.key"
          class="dna-title"
          :class="{ 'dna-title--locked': !title.unlocked, 'dna-title--equipped': title.equipped }"
        >
          <div class="dna-title__head">
            <span class="title-chip" :class="`title-chip--${title.rarity}`">
              {{ titleLabel(title) }}
            </span>
            <span v-if="title.rarity !== 'class'" class="dna-title__rarity">{{ title.rarity }}</span>
          </div>
          <p class="dna-title__description">{{ titleDescription(title) }}</p>
          <div class="dna-title__foot">
            <span v-if="title.unlocked" class="dna-title__state">
              {{ title.equipped ? 'Equipped' : 'Unlocked' }}
            </span>
            <span v-else class="dna-title__state dna-title__state--locked">Locked</span>
            <button
              v-if="title.unlocked && !title.equipped"
              type="button"
              class="btn btn--secondary btn--sm"
              :disabled="busy"
              @click="emit('equip-title', title.key)"
            >
              Equip
            </button>
            <button
              v-else-if="title.equipped && title.key !== 'class'"
              type="button"
              class="btn btn--secondary btn--sm"
              :disabled="busy"
              @click="emit('equip-title', null)"
            >
              Clear
            </button>
          </div>
        </article>
      </div>
    </details>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import {
  CERTIFICATION_PATHS,
  CERTIFICATION_ROADMAP_URL,
  DEFAULT_CERTIFICATION_PATH,
} from '../data/certificationPaths'

const props = defineProps({
  dna: { type: Object, default: null },
  busy: { type: Boolean, default: false },
})

const emit = defineEmits(['equip-title'])

const classInitial = computed(() => (props.dna?.class?.class_name || 'R').charAt(0))

const certificationPath = computed(() => {
  const key = props.dna?.class?.certification_key
  return CERTIFICATION_PATHS[key] || DEFAULT_CERTIFICATION_PATH
})

const sortedTitles = computed(() => {
  const titles = props.dna?.titles?.titles || []
  const rarityRank = { legendary: 0, epic: 1, rare: 2, uncommon: 3, common: 4 }
  return [...titles].sort((a, b) => {
    if (a.unlocked !== b.unlocked) return a.unlocked ? -1 : 1
    return (rarityRank[a.rarity] ?? 5) - (rarityRank[b.rarity] ?? 5) ||
      a.label.localeCompare(b.label)
  })
})

const titleLabel = (title) => title.hidden && !title.unlocked ? 'Secret title' : title.label
const titleDescription = (title) => {
  if (title.hidden && !title.unlocked) {
    return 'Complete a hidden challenge to reveal this title.'
  }
  return title.description
}
</script>

<style scoped>
.dna-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.dna-section__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.dna-section__eyebrow {
  margin: 0 0 0.25rem;
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dna-section__intro {
  max-width: 58rem;
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.55;
}

.dna-formula {
  flex: 0 0 auto;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.6875rem;
  letter-spacing: 0.04em;
}

.dna-layout {
  display: grid;
  grid-template-columns: minmax(15rem, 18rem) minmax(0, 1fr);
  gap: 1rem;
}

.dna-class-card {
  --class-color: var(--accent);
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  padding: 1.1rem;
  border: 1px solid var(--border-color);
  border-top: 3px solid var(--class-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.dna-class-card--builder { --class-color: var(--success); }
.dna-class-card--defender { --class-color: var(--warning); }
.dna-class-card--investigator { --class-color: var(--purple); }
.dna-class-card--leader { --class-color: var(--danger); }
.dna-class-card--recruit { --class-color: var(--text-muted); }

.dna-class-card__top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dna-class-card__sigil {
  display: grid;
  place-items: center;
  width: 3.25rem;
  height: 3.25rem;
  border: 1px solid var(--class-color);
  border-radius: 10px;
  background: color-mix(in srgb, var(--class-color) 16%, transparent);
  color: var(--class-color);
  font-size: 1.5rem;
  font-weight: 700;
}

.dna-class-card__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dna-class-card__name {
  margin: 0.1rem 0 0;
  color: var(--text-primary);
  font-size: 1.2rem;
}

.dna-class-card__trait {
  margin: 0.15rem 0 0;
  color: var(--text-secondary);
  font-size: 0.8125rem;
}

.dna-class-card__score {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  margin-top: 0.25rem;
}

.dna-class-card__score-value {
  color: var(--text-primary);
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.dna-class-card__score-label {
  color: var(--text-muted);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.dna-class-card__bar,
.dna-trait__bar {
  height: 0.45rem;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.dna-class-card__bar span,
.dna-trait__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--class-color);
}

.dna-class-card__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
}

.dna-class-card__title-label {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.dna-class-card__title-note {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.75rem;
}

.dna-traits {
  display: grid;
  gap: 0.65rem;
}

.dna-trait {
  --trait-color: var(--accent);
  padding: 0.8rem 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.dna-trait--builder { --trait-color: var(--success); }
.dna-trait--defender { --trait-color: var(--warning); }
.dna-trait--investigator { --trait-color: var(--purple); }
.dna-trait--leader { --trait-color: var(--danger); }

.dna-trait__head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.4rem;
}

.dna-trait__label {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 600;
}

.dna-trait__class {
  margin-left: 0.45rem;
  color: var(--text-muted);
  font-size: 0.75rem;
}

.dna-trait__score {
  color: var(--trait-color);
  font-size: 1.05rem;
  font-weight: 700;
}

.dna-trait__bar span {
  background: var(--trait-color);
}

.dna-trait__evidence,
.dna-trait__next {
  margin: 0.4rem 0 0;
  font-size: 0.75rem;
  line-height: 1.4;
}

.dna-trait__evidence { color: var(--text-secondary); }
.dna-trait__next { color: var(--text-muted); }

.dna-alignment {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.dna-alignment__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.dna-alignment__title {
  margin: 0.1rem 0 0;
  color: var(--text-primary);
  font-size: 1rem;
}

.dna-alignment__summary {
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.8125rem;
}

.dna-alignment__link {
  flex: 0 0 auto;
  color: var(--accent);
  font-size: 0.8125rem;
  text-decoration: none;
}

.dna-alignment__link:hover { text-decoration: underline; }

.dna-cert-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: 0.85rem;
}

.dna-cert {
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.dna-cert span {
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.dna-cert p {
  margin: 0.3rem 0 0;
  color: var(--text-primary);
  font-size: 0.75rem;
  line-height: 1.45;
}

.dna-alignment__roles {
  margin: 0.75rem 0 0;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.dna-titles {
  margin-top: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.dna-titles__summary {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1rem;
  color: var(--text-primary);
  font-weight: 600;
  cursor: pointer;
}

.dna-titles__count {
  color: var(--text-muted);
  font-size: 0.8125rem;
  font-weight: 500;
}

.dna-titles__intro {
  margin: 0 1rem 0.75rem;
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.dna-title-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr));
  gap: 0.65rem;
  padding: 0 1rem 1rem;
}

.dna-title {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.dna-title--locked { opacity: 0.62; }
.dna-title--equipped { border-color: var(--accent); }

.dna-title__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.4rem;
}

.dna-title__rarity {
  color: var(--text-muted);
  font-size: 0.625rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.dna-title__description {
  flex: 1;
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.75rem;
  line-height: 1.4;
}

.dna-title__foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.15rem;
}

.dna-title__state {
  color: var(--success);
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.dna-title__state--locked { color: var(--text-muted); }

.title-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.3;
}

.title-chip--common { background: rgba(148, 163, 184, 0.15); color: var(--text-secondary); }
.title-chip--uncommon { background: var(--success-bg); color: var(--success); }
.title-chip--rare { background: var(--accent-bg); color: var(--accent); }
.title-chip--epic { background: rgba(139, 92, 246, 0.15); color: var(--purple); }
.title-chip--legendary { background: var(--warning-bg); color: var(--warning); }
.title-chip--class { background: var(--bg-tertiary); color: var(--text-primary); }

@media (max-width: 900px) {
  .dna-layout { grid-template-columns: 1fr; }
  .dna-cert-grid { grid-template-columns: 1fr; }
  .dna-section__head { flex-direction: column; }
  .dna-alignment__head { flex-direction: column; }
}

@media (max-width: 600px) {
  .dna-section { padding: 1rem; }
  .dna-trait__class { display: block; margin: 0.15rem 0 0; }
}
</style>
