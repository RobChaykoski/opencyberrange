<template>
  <section v-if="atlas" class="atlas" aria-labelledby="atlas-title">
    <header class="atlas__head">
      <div>
        <p class="atlas__eyebrow">Cyber GPS</p>
        <h2 id="atlas-title" class="atlas__title">Practice evidence, mapped to real work</h2>
        <p class="atlas__intro">
          Six practice branches, eleven career families, and the roles inside them.
          Nodes unlock from the work you have already completed. They are a
          conversation aid, not a job label or a prediction.
        </p>
      </div>
      <div class="atlas__controls">
        <span class="atlas__version" :title="`Career Atlas version ${atlas.version}`">
          v{{ atlas.version }}
        </span>
        <div class="atlas-region" role="group" aria-label="Salary region">
          <button
            v-for="item in atlas.regions"
            :key="item.key"
            type="button"
            class="atlas-region__button"
            :class="{ 'atlas-region__button--active': region === item.key }"
            :aria-pressed="region === item.key"
            @click="region = item.key"
          >
            {{ item.label }}
            <span>{{ item.currency }}</span>
          </button>
        </div>
      </div>
    </header>

    <div class="atlas-legend" aria-label="Unlock legend">
      <span class="atlas-legend__item">
        <span class="atlas-legend__dot atlas-legend__dot--unlocked" aria-hidden="true"></span>
        Unlocked
      </span>
      <span class="atlas-legend__item">
        <span class="atlas-legend__dot atlas-legend__dot--next" aria-hidden="true"></span>
        One step away
      </span>
      <span class="atlas-legend__item">
        <span class="atlas-legend__dot atlas-legend__dot--locked" aria-hidden="true"></span>
        Locked
      </span>
      <span class="atlas-legend__count">
        {{ atlas.summary.unlocked }} of {{ atlas.summary.families }} families unlocked
      </span>
      <InfoTip
        text="A family unlocks from practice evidence: completed labs in its branch and the strength of your Cyber DNA affinity. Locked is not a negative label; it is the next part of the map to explore."
      />
    </div>

    <div v-if="isFirstRun" class="atlas-empty" role="note">
      <div>
        <strong>Start the map with one completed lab.</strong>
        The families below are a preview. Your first completion unlocks a branch,
        adds evidence, and moves the recommendation.
      </div>
      <router-link to="/exercises" class="btn btn--secondary btn--sm">
        Find an exercise
      </router-link>
    </div>

    <div v-if="nextUnlock" class="atlas-next-unlock">
      <span class="atlas-next-unlock__eyebrow">Next unlock</span>
      <strong>{{ nextUnlock.label }}</strong>
      <span class="atlas-next-unlock__hint">{{ nextUnlock.unlock_hint }}</span>
      <button type="button" class="btn btn--secondary btn--sm" @click="selectFamily(nextUnlock)">
        Open path
      </button>
    </div>

    <div class="atlas-tree" aria-label="Career skill tree">
      <div class="atlas-core">
        <span class="atlas-core__sigil" aria-hidden="true">{{ classInitial }}</span>
        <div>
          <strong>{{ dna?.class?.class_name || 'Recruit' }}</strong>
          <span>{{ dna?.overall ?? 0 }}/99 · {{ dna?.tier || 'Unranked' }}</span>
        </div>
      </div>

      <div class="atlas-lanes">
        <article
          v-for="branch in atlas.branches"
          :key="branch.key"
          class="atlas-lane"
          :class="`atlas-lane--${branch.key}`"
        >
          <header class="atlas-lane__head">
            <div class="atlas-lane__identity">
              <span
                class="atlas-lane__ring"
                :class="{ 'atlas-lane__ring--strong': branch.score >= 50 }"
                :style="{ '--branch-score': `${branch.score}%` }"
                aria-hidden="true"
              ></span>
              <div>
                <span class="atlas-lane__label">{{ branch.label }}</span>
                <span class="atlas-lane__tier">{{ branch.tier }}</span>
              </div>
            </div>
            <span class="atlas-lane__score" :title="`${branch.label} branch score`">
              {{ branch.score }}
            </span>
          </header>
          <div class="atlas-lane__rail">
            <span class="atlas-lane__line" aria-hidden="true"></span>
            <button
              v-for="family in branch.families"
              :key="family.key"
              type="button"
              class="atlas-node"
              :class="[
                `atlas-node--${family.unlock_state}`,
                {
                  'atlas-node--selected': family.key === selectedFamilyKey,
                  'atlas-node--recommended': family.recommended,
                },
              ]"
              :aria-pressed="family.key === selectedFamilyKey"
              :aria-label="nodeAria(family)"
              @click="selectFamily(family)"
            >
              <span class="atlas-node__dot" aria-hidden="true"></span>
              <span class="atlas-node__ring" aria-hidden="true">
                <svg viewBox="0 0 44 44">
                  <circle class="atlas-node__ring-bg" cx="22" cy="22" r="18" />
                  <circle
                    class="atlas-node__ring-fill"
                    cx="22"
                    cy="22"
                    r="18"
                    :stroke-dasharray="`${family.match_score * 1.131} 113.1`"
                  />
                </svg>
                <span class="atlas-node__glyph">
                  <svg v-if="family.unlock_state === 'locked'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="5" y="11" width="14" height="9" rx="2" />
                    <path d="M8 11V8a4 4 0 0 1 8 0v3" />
                  </svg>
                  <svg v-else-if="family.unlock_state === 'next'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z" />
                    <path d="M19 17v4" />
                    <path d="M17 19h4" />
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m5 12 4 4L19 6" />
                  </svg>
                </span>
              </span>
              <span class="atlas-node__label">
                {{ family.label }}
                <span v-if="family.recommended" class="atlas-node__badge">Recommended</span>
              </span>
              <span class="atlas-node__meta">
                {{ family.match_score }}% · {{ family.roles.length }} roles
                <template v-if="family.evidence_count"> · {{ family.evidence_count }} labs</template>
              </span>
            </button>
          </div>
        </article>
      </div>
    </div>

    <div v-if="selectedFamily" class="atlas-detail">
      <header class="atlas-detail__head">
        <div>
          <p class="atlas-detail__eyebrow">
            {{ selectedFamily.branch_label }} branch ·
            {{ unlockLabel(selectedFamily.unlock_state) }}
          </p>
          <h3>{{ selectedFamily.label }}</h3>
          <p>{{ selectedFamily.summary }}</p>
          <p class="atlas-detail__evidence">
            {{ selectedFamily.branch_label }} branch · {{ selectedFamily.evidence_count }} labs in
            this branch · {{ selectedFamily.dimension_average }} average branch score
          </p>
          <p class="atlas-detail__basis">
            <span
              class="atlas-basis"
              :class="`atlas-basis--${evidenceBand(selectedFamily).key}`"
            >
              {{ evidenceBand(selectedFamily).label }}
            </span>
            {{ evidenceBand(selectedFamily).note }}
          </p>
        </div>
        <div class="atlas-detail__score">
          <span
            class="atlas-detail__ring"
            :style="{ '--match-score': `${selectedFamily.match_score}%` }"
            aria-hidden="true"
          ></span>
          <div>
            <span>Practice match</span>
            <strong>{{ selectedFamily.match_score }}<small>/100</small></strong>
          </div>
        </div>
      </header>

      <div class="atlas-unlock">
        <div
          class="atlas-unlock__bar"
          role="progressbar"
          :aria-valuenow="selectedFamily.match_score"
          aria-valuemin="0"
          aria-valuemax="100"
          :aria-label="`${selectedFamily.label} practice match: ${selectedFamily.match_score} out of 100`"
        >
          <span :style="{ width: selectedFamily.match_score + '%' }"></span>
        </div>
        <p>{{ selectedFamily.unlock_hint }}</p>
      </div>

      <div class="atlas-role-grid">
        <button
          v-for="(role, index) in selectedFamily.roles"
          :key="role.title"
          type="button"
          class="atlas-role"
          :class="{ 'atlas-role--selected': index === selectedRoleIndex }"
          :aria-pressed="index === selectedRoleIndex"
          @click="selectedRoleIndex = index"
        >
          <span class="atlas-role__level">{{ role.level }}</span>
          <strong>{{ role.title }}</strong>
          <span class="atlas-role__median">
            {{ formatMoney(role.salary[region].median, role.salary[region].currency) }}
            <small>median</small>
          </span>
          <span class="atlas-role__range">
            {{ formatMoney(role.salary[region].low, role.salary[region].currency) }} –
            {{ formatMoney(role.salary[region].high, role.salary[region].currency) }}
          </span>
        </button>
      </div>

      <div v-if="selectedRole" class="atlas-salary">
        <div class="atlas-salary__head">
          <div>
            <p class="atlas-salary__eyebrow">
              Salary lens · {{ regionMeta.label }} ({{ regionMeta.currency }})
            </p>
            <h4>{{ selectedRole.title }}</h4>
            <p>{{ selectedRole.summary }}</p>
          </div>
          <span class="atlas-salary__occupation">{{ salary.occupation }}</span>
        </div>

        <div
          class="atlas-salary__scale"
          role="img"
          :aria-label="`${selectedRole.title} salary range in ${regionMeta.label}: low ${formatMoney(salary.low, salary.currency)}, median ${formatMoney(salary.median, salary.currency)}, high ${formatMoney(salary.high, salary.currency)}`"
        >
          <div class="atlas-salary__track">
            <span class="atlas-salary__fill"></span>
            <span class="atlas-salary__marker atlas-salary__marker--low"></span>
            <span class="atlas-salary__marker atlas-salary__marker--median" :style="{ left: medianPosition + '%' }"></span>
            <span class="atlas-salary__marker atlas-salary__marker--high"></span>
          </div>
          <div class="atlas-salary__labels">
            <span>
              <small>Low 10th</small>
              <strong>{{ formatMoney(salary.low, salary.currency) }}</strong>
            </span>
            <span>
              <small>Median</small>
              <strong>{{ formatMoney(salary.median, salary.currency) }}</strong>
            </span>
            <span>
              <small>High 90th</small>
              <strong>{{ formatMoney(salary.high, salary.currency) }}</strong>
            </span>
          </div>
        </div>

        <div class="atlas-salary__meta">
          <span>{{ salary.source_label }}</span>
          <span>As of {{ salary.as_of }}</span>
          <span>{{ salary.basis }}</span>
        </div>
        <p class="atlas-salary__note">{{ atlas.salary_note }}</p>
      </div>

      <div class="atlas-detail__next">
        <strong>Next practice step</strong>
        <p>{{ selectedFamily.next_step }}</p>
      </div>
    </div>

    <div class="atlas-footer">
      <p class="atlas-footer__disclaimer">{{ atlas.disclaimer }}</p>

      <details class="atlas-table">
        <summary>Salary table (all roles, both regions)</summary>
        <div class="atlas-table__wrap">
          <table>
            <caption>National planning ranges from public labour-market data. Not an offer.</caption>
            <thead>
              <tr>
                <th scope="col">Family</th>
                <th scope="col">Role</th>
                <th scope="col">Level</th>
                <th scope="col">CA low</th>
                <th scope="col">CA median</th>
                <th scope="col">CA high</th>
                <th scope="col">US low</th>
                <th scope="col">US median</th>
                <th scope="col">US high</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableRows" :key="`${row.family}-${row.title}`">
                <th scope="row">{{ row.family }}</th>
                <td>{{ row.title }}</td>
                <td>{{ row.level }}</td>
                <td class="atlas-table__salary">{{ formatMoney(row.salary.ca.low, 'CAD') }}</td>
                <td class="atlas-table__salary">{{ formatMoney(row.salary.ca.median, 'CAD') }}</td>
                <td class="atlas-table__salary">{{ formatMoney(row.salary.ca.high, 'CAD') }}</td>
                <td class="atlas-table__salary">{{ formatMoney(row.salary.us.low, 'USD') }}</td>
                <td class="atlas-table__salary">{{ formatMoney(row.salary.us.median, 'USD') }}</td>
                <td class="atlas-table__salary">{{ formatMoney(row.salary.us.high, 'USD') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>

      <div class="atlas-sources">
        <strong>Salary sources</strong>
        <ul>
          <li v-for="source in atlas.sources" :key="source.key">
            <a :href="source.url" target="_blank" rel="noopener noreferrer">{{ source.label }}</a>
            <span>{{ source.detail }} {{ source.basis }}</span>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import InfoTip from './InfoTip.vue'

const props = defineProps({
  atlas: { type: Object, default: null },
  dna: { type: Object, default: null },
})

const region = ref(props.atlas?.regions?.[0]?.key || 'ca')
const selectedFamilyKey = ref(
  props.atlas?.recommended_family_key ||
    props.atlas?.families?.find((family) => family.unlock_state !== 'locked')?.key ||
    props.atlas?.families?.[0]?.key ||
    null
)
const selectedRoleIndex = ref(0)

const classInitial = computed(() => (props.dna?.class?.class_name || 'R').charAt(0))

const selectedFamily = computed(() => {
  const families = props.atlas?.families || []
  return families.find((family) => family.key === selectedFamilyKey.value) || families[0] || null
})

const isFirstRun = computed(
  () =>
    Number(props.dna?.overall || 0) === 0 &&
    Number(props.atlas?.summary?.unlocked || 0) === 0,
)

const nextUnlock = computed(() => {
  const families = props.atlas?.families || []
  return (
    families
      .filter((family) => family.unlock_state === 'next')
      .sort((a, b) => b.match_score - a.match_score)[0] || null
  )
})

const selectedRole = computed(() => {
  const roles = selectedFamily.value?.roles || []
  return roles[selectedRoleIndex.value] || roles[0] || null
})

const regionMeta = computed(() => {
  const regions = props.atlas?.regions || []
  return regions.find((item) => item.key === region.value) || regions[0] || { label: 'Canada', currency: 'CAD' }
})

const salary = computed(() => selectedRole.value?.salary?.[region.value] || null)

const tableRows = computed(() => {
  const rows = []
  for (const family of props.atlas?.families || []) {
    for (const role of family.roles || []) {
      rows.push({
        family: family.label,
        title: role.title,
        level: role.level,
        salary: role.salary,
      })
    }
  }
  return rows
})

const medianPosition = computed(() => {
  if (!salary.value) return 50
  const { low, median, high } = salary.value
  if (high <= low) return 50
  return Math.max(0, Math.min(100, ((median - low) / (high - low)) * 100))
})

watch(selectedFamily, () => {
  selectedRoleIndex.value = 0
})

function unlockLabel(state) {
  return String(state || '').replace('_', ' ')
}

function selectFamily(family) {
  selectedFamilyKey.value = family.key
}

function nodeAria(family) {
  const band = evidenceBand(family)
  return `${family.label}. ${unlockLabel(family.unlock_state)}. Practice match ${family.match_score} out of 100. Evidence: ${band.label}. ${family.roles.length} roles.`
}

function evidenceBand(family) {
  const count = Number(family?.evidence_count || 0)
  if (count >= 5) {
    return {
      key: 'strong',
      label: 'Established',
      note: `${count} completed labs in this branch.`,
    }
  }
  if (count > 0) {
    return {
      key: 'growing',
      label: 'Growing',
      note: `${count} completed ${count === 1 ? 'lab' : 'labs'} in this branch. A few more will stabilise the match.`,
    }
  }
  return {
    key: 'none',
    label: 'No evidence yet',
    note: 'A starting suggestion from your branch profile, not an assessment.',
  }
}

function formatMoney(value, currency = null) {
  if (value === null || value === undefined) return '—'
  const code = currency || salary.value?.currency || regionMeta.value.currency || 'CAD'
  try {
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: code,
      maximumFractionDigits: 0,
    }).format(value)
  } catch {
    return `${code} ${Number(value).toLocaleString()}`
  }
}
</script>

<style scoped>
.atlas {
  margin-top: 1.5rem;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.atlas__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.25rem;
}

.atlas__eyebrow {
  margin: 0 0 0.25rem;
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.atlas__title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 700;
}

.atlas__intro {
  max-width: 58rem;
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.55;
}

.atlas__controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  flex: 0 0 auto;
}

.atlas__version {
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.6875rem;
  letter-spacing: 0.04em;
}

.atlas-region {
  display: inline-flex;
  padding: 0.2rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
}

.atlas-region__button {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.65rem;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  font: inherit;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 140ms ease, color 140ms ease;
}

.atlas-region__button span {
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 500;
}

.atlas-region__button:hover {
  color: var(--accent-text);
}

.atlas-region__button--active {
  background: var(--accent-bg);
  color: var(--accent-text);
}

.atlas-region__button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.atlas-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
  margin: 1rem 0;
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.atlas-legend__item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.atlas-legend__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}

.atlas-legend__dot--unlocked {
  background: var(--success);
}

.atlas-legend__dot--next {
  background: var(--warning);
}

.atlas-legend__dot--locked {
  background: var(--text-muted);
}

.atlas-legend__count {
  margin-left: auto;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.atlas-empty {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.65rem 1rem;
  margin-bottom: 1rem;
  padding: 0.8rem 0.9rem;
  border: 1px dashed var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.atlas-empty strong {
  color: var(--text-primary);
}

.atlas-next-unlock {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  margin-bottom: 1rem;
  padding: 0.65rem 0.8rem;
  border: 1px solid color-mix(in srgb, var(--accent) 45%, var(--border-color));
  border-radius: 10px;
  background: var(--accent-bg);
}

.atlas-next-unlock__eyebrow {
  color: var(--accent-text);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.atlas-next-unlock strong {
  color: var(--text-primary);
  font-size: 0.82rem;
}

.atlas-next-unlock__hint {
  flex: 1 1 260px;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.atlas-next-unlock .btn {
  margin-left: auto;
}

.atlas-tree {
  position: relative;
  overflow: hidden;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    radial-gradient(circle at 50% 0%, var(--accent-bg), transparent 58%),
    var(--bg-primary);
}

.atlas-tree::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(var(--border-color) 1px, transparent 1px);
  background-size: 20px 20px;
  opacity: 0.28;
  pointer-events: none;
}

.atlas-core {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  width: fit-content;
  margin: 0 auto 1rem;
  padding: 0.55rem 0.8rem;
  border: 1px solid var(--accent);
  border-radius: 999px;
  background: var(--bg-secondary);
  box-shadow: 0 10px 30px -18px var(--accent);
}

.atlas-core__sigil {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--accent-bg);
  color: var(--accent-text);
  font-size: 0.9rem;
  font-weight: 700;
}

.atlas-core strong {
  display: block;
  color: var(--text-primary);
  font-size: 0.85rem;
}

.atlas-core span:not(.atlas-core__sigil) {
  display: block;
  color: var(--text-muted);
  font-size: 0.7rem;
}

.atlas-lanes {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.atlas-lane {
  min-width: 0;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: color-mix(in srgb, var(--bg-secondary) 88%, transparent);
}

.atlas-lane__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.atlas-lane__identity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.atlas-lane__ring {
  position: relative;
  flex: 0 0 auto;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: conic-gradient(var(--accent) var(--branch-score), var(--bg-tertiary) 0);
  display: grid;
  place-items: center;
}

.atlas-lane__ring::after {
  content: '';
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--bg-secondary);
}

.atlas-lane__ring--strong {
  background: conic-gradient(var(--success) var(--branch-score), var(--bg-tertiary) 0);
}

.atlas-lane__label {
  display: block;
  color: var(--text-primary);
  font-size: 0.78rem;
  font-weight: 650;
  line-height: 1.2;
}

.atlas-lane__tier {
  display: block;
  color: var(--text-muted);
  font-size: 0.62rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.atlas-lane__score {
  color: var(--text-muted);
  font-size: 0.7rem;
  font-variant-numeric: tabular-nums;
}

.atlas-lane__rail {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding-top: 0.6rem;
}

.atlas-lane__line {
  position: absolute;
  top: 0.6rem;
  bottom: 0.6rem;
  left: 21px;
  width: 1px;
  background: var(--border-color);
}

.atlas-node {
  position: relative;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  grid-template-rows: auto auto;
  column-gap: 0.6rem;
  align-items: center;
  width: 100%;
  padding: 0.35rem 0.4rem;
  border: 1px solid transparent;
  border-radius: 9px;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: background 140ms ease, border-color 140ms ease, transform 140ms ease;
}

.atlas-node__dot {
  position: absolute;
  left: 18px;
  top: 50%;
  width: 8px;
  height: 8px;
  border: 2px solid var(--bg-secondary);
  border-radius: 50%;
  background: var(--text-muted);
  transform: translate(-50%, -50%);
  z-index: 2;
}

.atlas-node--unlocked .atlas-node__dot {
  background: var(--success);
}

.atlas-node--next .atlas-node__dot {
  background: var(--warning);
}

.atlas-node--locked .atlas-node__dot {
  background: var(--text-muted);
}

.atlas-node:hover {
  background: var(--bg-tertiary);
}

.atlas-node:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.atlas-node--selected {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.atlas-node__ring {
  position: relative;
  display: grid;
  place-items: center;
  grid-row: 1 / span 2;
  width: 44px;
  height: 44px;
}

.atlas-node__ring svg {
  position: absolute;
  inset: 0;
  width: 44px;
  height: 44px;
  transform: rotate(-90deg);
}

.atlas-node__ring-bg {
  fill: var(--bg-primary);
  stroke: var(--border-color);
  stroke-width: 3;
}

.atlas-node__ring-fill {
  fill: none;
  stroke: var(--text-muted);
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dasharray 260ms ease;
}

.atlas-node--unlocked .atlas-node__ring-fill {
  stroke: var(--success);
}

.atlas-node--next .atlas-node__ring-fill {
  stroke: var(--warning);
}

.atlas-node--locked .atlas-node__ring-fill {
  stroke: var(--text-muted);
  opacity: 0.5;
}

.atlas-node__glyph {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.atlas-node--unlocked .atlas-node__glyph {
  color: var(--success);
}

.atlas-node--next .atlas-node__glyph {
  color: var(--warning);
}

.atlas-node--locked .atlas-node__glyph {
  color: var(--text-muted);
}

.atlas-node__glyph svg {
  position: static;
  width: 14px;
  height: 14px;
  transform: none;
}

.atlas-node__label {
  align-self: end;
  color: var(--text-primary);
  font-size: 0.76rem;
  font-weight: 600;
  line-height: 1.25;
}

.atlas-node--locked .atlas-node__label {
  color: var(--text-secondary);
}

.atlas-node__badge {
  display: inline-block;
  margin-left: 0.35rem;
  padding: 0.05rem 0.35rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent-text);
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  vertical-align: middle;
}

.atlas-node__meta {
  align-self: start;
  color: var(--text-muted);
  font-size: 0.66rem;
  font-variant-numeric: tabular-nums;
}

.atlas-node--recommended::after {
  content: '';
  position: absolute;
  inset: -1px;
  border: 1px solid var(--accent);
  border-radius: 9px;
  opacity: 0.5;
  animation: atlas-pulse 2.4s ease-in-out infinite;
  pointer-events: none;
}

@keyframes atlas-pulse {
  0%, 100% { opacity: 0.18; }
  50% { opacity: 0.6; }
}

.atlas-detail {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
}

.atlas-detail__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.atlas-detail__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.atlas-detail__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.05rem;
  font-weight: 700;
}

.atlas-detail__head p:not(.atlas-detail__eyebrow) {
  max-width: 60rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.5;
}

.atlas-detail__head .atlas-detail__evidence {
  margin-top: 0.4rem;
  color: var(--text-muted);
  font-size: 0.68rem;
  letter-spacing: 0.02em;
}

.atlas-detail__basis {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.45rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.45;
}

.atlas-basis {
  display: inline-flex;
  align-items: center;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.atlas-basis--strong {
  border-color: var(--success);
  color: var(--success);
}

.atlas-basis--growing {
  border-color: var(--accent);
  color: var(--accent-text);
}

.atlas-basis--none {
  border-color: var(--border-color);
  color: var(--text-muted);
}

.atlas-detail__score {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex: 0 0 auto;
  min-width: 150px;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  text-align: right;
}

.atlas-detail__ring {
  flex: 0 0 auto;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: conic-gradient(var(--success) var(--match-score), var(--bg-tertiary) 0);
  display: grid;
  place-items: center;
}

.atlas-detail__ring::after {
  content: '';
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--bg-secondary);
}

.atlas-detail__score div {
  min-width: 0;
}

.atlas-detail__score span:not(.atlas-detail__ring) {
  display: block;
  color: var(--text-muted);
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.atlas-detail__score strong {
  color: var(--text-primary);
  font-size: 1.4rem;
  font-variant-numeric: tabular-nums;
}

.atlas-detail__score small {
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 500;
}

.atlas-unlock {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.75rem 0;
}

.atlas-unlock__bar {
  flex: 1 1 auto;
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.atlas-unlock__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--success));
  transition: width 260ms ease;
}

.atlas-unlock p {
  flex: 0 0 auto;
  margin: 0;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.atlas-role-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.6rem;
  margin: 0.75rem 0;
}

.atlas-role {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 140ms ease, transform 140ms ease;
}

.atlas-role:hover {
  border-color: var(--accent);
  transform: translateY(-1px);
}

.atlas-role:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.atlas-role--selected {
  border-color: var(--accent);
  box-shadow: inset 0 0 0 1px var(--accent);
}

.atlas-role__level {
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.atlas-role strong {
  color: var(--text-primary);
  font-size: 0.8rem;
  line-height: 1.3;
}

.atlas-role__median {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.atlas-role__median small {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 500;
}

.atlas-role__range {
  color: var(--text-muted);
  font-size: 0.68rem;
  font-variant-numeric: tabular-nums;
}

.atlas-salary {
  margin-top: 0.75rem;
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.atlas-salary__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.atlas-salary__eyebrow {
  margin: 0 0 0.15rem;
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.atlas-salary__head h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.92rem;
  font-weight: 700;
}

.atlas-salary__head p:not(.atlas-salary__eyebrow) {
  max-width: 54rem;
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.76rem;
  line-height: 1.45;
}

.atlas-salary__occupation {
  flex: 0 0 auto;
  max-width: 220px;
  color: var(--text-muted);
  font-size: 0.68rem;
  text-align: right;
}

.atlas-salary__scale {
  margin-top: 0.85rem;
}

.atlas-salary__track {
  position: relative;
  height: 12px;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.atlas-salary__fill {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent-bg), var(--accent));
  opacity: 0.35;
}

.atlas-salary__marker {
  position: absolute;
  top: 50%;
  width: 3px;
  height: 20px;
  border-radius: 999px;
  background: var(--text-primary);
  transform: translate(-50%, -50%);
}

.atlas-salary__marker--low {
  left: 0;
  background: var(--text-muted);
}

.atlas-salary__marker--median {
  background: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-bg);
}

.atlas-salary__marker--high {
  left: 100%;
  background: var(--text-muted);
}

.atlas-salary__labels {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 0.5rem;
}

.atlas-salary__labels span {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.atlas-salary__labels span:nth-child(2) {
  text-align: center;
}

.atlas-salary__labels span:last-child {
  text-align: right;
}

.atlas-salary__labels small {
  color: var(--text-muted);
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.atlas-salary__labels strong {
  color: var(--text-primary);
  font-size: 0.82rem;
  font-variant-numeric: tabular-nums;
}

.atlas-salary__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem 0.9rem;
  margin-top: 0.7rem;
  padding-top: 0.6rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.66rem;
}

.atlas-salary__note {
  margin: 0.5rem 0 0;
  color: var(--text-muted);
  font-size: 0.68rem;
  line-height: 1.45;
}

.atlas-detail__next {
  margin-top: 0.75rem;
  padding: 0.7rem 0.8rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  background: var(--accent-bg);
}

.atlas-detail__next strong {
  color: var(--accent-text);
  font-size: 0.72rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.atlas-detail__next p {
  margin: 0.2rem 0 0;
  color: var(--text-primary);
  font-size: 0.8rem;
  line-height: 1.45;
}

.atlas-footer {
  margin-top: 1rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--border-color);
}

.atlas-footer__disclaimer {
  margin: 0 0 0.75rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  line-height: 1.5;
}

.atlas-table {
  margin-bottom: 0.75rem;
}

.atlas-table summary {
  color: var(--text-secondary);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
}

.atlas-table__wrap {
  margin-top: 0.5rem;
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.atlas-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.7rem;
}

.atlas-table caption {
  padding: 0.45rem 0.6rem;
  color: var(--text-muted);
  font-size: 0.65rem;
  text-align: left;
}

.atlas-table th,
.atlas-table td {
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  vertical-align: top;
}

.atlas-table thead th {
  color: var(--text-muted);
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.atlas-table tbody th {
  color: var(--text-primary);
  font-weight: 600;
}

.atlas-table__salary {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.atlas-sources strong {
  color: var(--text-primary);
  font-size: 0.76rem;
}

.atlas-sources ul {
  margin: 0.4rem 0 0;
  padding-left: 1.1rem;
}

.atlas-sources li {
  margin: 0.3rem 0;
  color: var(--text-muted);
  font-size: 0.68rem;
  line-height: 1.45;
}

.atlas-sources a {
  color: var(--accent-text);
  font-weight: 600;
}

.atlas-sources span {
  display: block;
}

@media (max-width: 900px) {
  .atlas__head,
  .atlas-detail__head,
  .atlas-salary__head {
    flex-direction: column;
  }

  .atlas__controls {
    align-items: flex-start;
  }

  .atlas-lanes {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .atlas-salary__occupation {
    max-width: none;
    text-align: left;
  }
}

@media (max-width: 640px) {
  .atlas {
    padding: 1rem;
  }

  .atlas-lanes {
    grid-template-columns: minmax(0, 1fr);
  }

  .atlas-legend__count {
    margin-left: 0;
    width: 100%;
  }

  .atlas-next-unlock {
    flex-direction: column;
    align-items: flex-start;
  }

  .atlas-next-unlock .btn {
    margin-left: 0;
  }

  .atlas-unlock {
    flex-direction: column;
    align-items: stretch;
  }

  .atlas-salary__labels {
    flex-direction: column;
    gap: 0.35rem;
  }

  .atlas-salary__labels span,
  .atlas-salary__labels span:nth-child(2),
  .atlas-salary__labels span:last-child {
    flex-direction: row;
    justify-content: space-between;
    text-align: left;
  }
}

@media (prefers-reduced-motion: reduce) {
  .atlas-node--recommended::after {
    animation: none;
    opacity: 0.35;
  }

  .atlas-node,
  .atlas-role,
  .atlas-node__ring-fill,
  .atlas-unlock__bar span,
  .atlas-region__button {
    transition: none;
  }
}
</style>
