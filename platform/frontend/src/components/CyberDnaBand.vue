<template>
  <section class="dna-band" aria-labelledby="dna-band-title">
    <div class="dna-band__head">
      <div class="dna-band__intro">
        <p class="dna-band__eyebrow">
          Cyber DNA
          <span v-if="growth" class="dna-band__confidence">{{ growth.confidence.label }}</span>
        </p>
        <h2 id="dna-band-title" class="dna-band__title">{{ headline }}</h2>
        <p class="dna-band__lede">{{ lede }}</p>
      </div>
      <router-link to="/profile?tab=skill-tree" class="btn btn--outline btn--sm">
        Open report
      </router-link>
    </div>

    <div v-if="!onboarding" class="dna-band__discover">
      <div>
        <strong>Discover your Cyber DNA</strong>
        <p>Pick what you enjoy, get three starter exercises, and unlock your report.</p>
      </div>
      <router-link to="/discover" class="btn btn--primary btn--sm">Start discovery</router-link>
    </div>

    <div v-else-if="starterLabs.length && starterDone < starterLabs.length" class="starter">
      <div class="starter__head">
        <strong>Your starter path</strong>
        <span class="starter__count">{{ starterDone }} of {{ starterLabs.length }} complete</span>
      </div>
      <ul class="starter__list">
        <li v-for="lab in starterLabs" :key="lab.slug" class="starter__row">
          <span class="starter__check" :class="{ 'starter__check--done': completed.has(lab.slug) }" aria-hidden="true">
            <svg v-if="completed.has(lab.slug)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </span>
          <span class="starter__label">{{ lab.title }}</span>
          <router-link :to="`/exercises/${lab.track}`" class="starter__action">
            {{ completed.has(lab.slug) ? 'Review' : 'Open' }}
          </router-link>
        </li>
      </ul>
      <p class="starter__note">
        Completing all {{ starterLabs.length }} unlocks the Career GPS confidence view.
      </p>
    </div>

    <template v-if="growth">
      <div v-if="growth.confidence.percent_ready" class="signals">
        <div v-for="signal in growth.signals" :key="signal.key" class="signal">
          <p class="signal__label">{{ signal.label }}</p>
          <p class="signal__value">{{ signal.value }}</p>
          <p class="signal__detail">
            <span class="signal__arrow" :class="'signal__arrow--' + signal.direction" aria-hidden="true">
              {{ signal.direction === 'up' ? '↑' : signal.direction === 'down' ? '↓' : '→' }}
            </span>
            {{ signal.detail }}
          </p>
        </div>
      </div>

      <div v-else class="dna-band__locked">
        <strong>Trends unlock after three exercises.</strong>
        <p>One completion is an accident; three is a pattern. Until then you see counts, not percentages.</p>
      </div>

      <div v-if="growth.confidence.percent_ready && growth.trend.length" class="trend" aria-label="Completions over 30, 60, and 90 days">
        <div v-for="point in growth.trend" :key="point.days" class="trend__item">
          <span class="trend__bar" :style="{ height: barHeight(point.completions) }"></span>
          <span class="trend__value">{{ point.completions }}</span>
          <span class="trend__label">{{ point.days }}d</span>
        </div>
      </div>

      <div v-if="opportunity" class="opportunity">
        <div>
          <p class="opportunity__eyebrow">Next opportunity</p>
          <p class="opportunity__title">{{ opportunity.label }}</p>
          <p class="opportunity__detail">{{ opportunity.detail }}</p>
        </div>
        <router-link :to="opportunity.route" class="btn btn--ghost btn--sm">
          {{ opportunity.action }}
        </router-link>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  profile: { type: Object, default: null },
  settings: { type: Object, default: null },
})

const onboarding = computed(() => props.settings?.notification_prefs?.dna_onboarding_v1 || null)
const starterLabs = computed(() => onboarding.value?.labs || [])
const growth = computed(() => props.profile?.growth_velocity || null)
const skillDna = computed(() => props.profile?.skill_dna || null)

const completed = computed(() => {
  const slugs = new Set()
  for (const row of props.profile?.completions || []) {
    if (row.lab_slug) slugs.add(row.lab_slug)
  }
  return slugs
})

const starterDone = computed(
  () => starterLabs.value.filter((lab) => completed.value.has(lab.slug)).length
)

const classLabel = computed(() => skillDna.value?.class?.class_name || skillDna.value?.class?.label || '')
const topBranch = computed(() => {
  const rows = [...(skillDna.value?.dimensions || [])]
  rows.sort((a, b) => (b.score || 0) - (a.score || 0))
  return rows[0] || null
})

const headline = computed(() => {
  if (!skillDna.value || !growth.value) return 'Your Cyber DNA is forming'
  if (growth.value.confidence.level === 'starting') {
    return 'Your Cyber DNA is forming'
  }
  return classLabel.value ? `You are building as ${classLabel.value}` : 'Your Cyber DNA'
})

const lede = computed(() => {
  if (!growth.value) return 'Solve a few exercises to start the profile.'
  if (growth.value.confidence.level === 'starting') {
    return 'Your first three completions will reveal a pattern. Until then, this is a starting point, not a label.'
  }
  if (!topBranch.value) return 'Your report is built from your own completed work.'
  return `${topBranch.value.label} is your strongest branch so far, with ${topBranch.value.evidence_count} pieces of evidence.`
})

const opportunity = computed(() => growth.value?.opportunities?.[0] || null)

const barHeight = (value) => {
  const values = growth.value?.trend?.map((point) => point.completions) || []
  const max = Math.max(1, ...values)
  return `${Math.max(8, Math.round((value / max) * 100))}%`
}
</script>

<style scoped>
.dna-band {
  margin: 1.25rem 0;
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  background:
    linear-gradient(135deg, rgba(37, 99, 235, 0.08), transparent 55%),
    var(--bg-secondary);
}
.dna-band__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}
.dna-band__eyebrow {
  margin: 0 0 0.35rem;
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--accent);
}
.dna-band__confidence {
  margin-left: 0.5rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  letter-spacing: 0.04em;
  font-weight: 600;
}
.dna-band__title {
  margin: 0 0 0.35rem;
  font-size: 1.25rem;
}
.dna-band__lede {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  max-width: 70ch;
}
.dna-band__discover {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 0.85rem 1rem;
  border-radius: 0.5rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}
.dna-band__discover p {
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}
.starter {
  margin-top: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
}
.starter__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.88rem;
}
.starter__count {
  color: var(--text-muted);
}
.starter__list {
  list-style: none;
  margin: 0.6rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.starter__row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.88rem;
}
.starter__check {
  width: 1.15rem;
  height: 1.15rem;
  flex: 0 0 1.15rem;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  display: grid;
  place-items: center;
  color: var(--success);
}
.starter__check--done {
  border-color: var(--success);
  background: rgba(34, 197, 94, 0.12);
}
.starter__check svg {
  width: 0.75rem;
  height: 0.75rem;
}
.starter__label {
  flex: 1;
  min-width: 0;
}
.starter__action {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
}
.starter__note {
  margin: 0.6rem 0 0;
  color: var(--text-muted);
  font-size: 0.78rem;
}
.signals {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.6rem;
  margin-top: 1rem;
}
.signal {
  padding: 0.7rem 0.8rem;
  border-radius: 0.5rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}
.signal__label {
  margin: 0;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}
.signal__value {
  margin: 0.25rem 0;
  font-weight: 700;
  font-size: 0.95rem;
}
.signal__detail {
  margin: 0;
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.35;
}
.signal__arrow--up { color: var(--success); }
.signal__arrow--down { color: var(--warning); }
.signal__arrow--flat { color: var(--text-muted); }

.dna-band__locked {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  border-left: 3px solid var(--warning);
  background: var(--bg-primary);
  border-radius: 0 0.4rem 0.4rem 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
}
.dna-band__locked p {
  margin: 0.25rem 0 0;
}

.trend {
  display: flex;
  align-items: flex-end;
  gap: 1.5rem;
  height: 5.5rem;
  margin-top: 1rem;
  padding: 0 0.5rem;
  border-bottom: 1px solid var(--border-color);
}
.trend__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  gap: 0.2rem;
  flex: 1;
}
.trend__bar {
  width: 100%;
  max-width: 4rem;
  background: linear-gradient(180deg, var(--accent), rgba(37, 99, 235, 0.35));
  border-radius: 0.25rem 0.25rem 0 0;
  min-height: 6px;
}
.trend__value {
  font-size: 0.78rem;
  font-weight: 700;
  order: -1;
}
.trend__label {
  font-size: 0.72rem;
  color: var(--text-muted);
}
.opportunity {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 0.85rem 1rem;
  border-radius: 0.5rem;
  background: var(--accent-bg);
  border: 1px solid var(--border-color);
}
.opportunity__eyebrow {
  margin: 0;
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
}
.opportunity__title {
  margin: 0.15rem 0;
  font-weight: 700;
}
.opportunity__detail {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.83rem;
}
@media (max-width: 640px) {
  .dna-band__head,
  .dna-band__discover,
  .opportunity {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
