<template>
  <section v-if="momentum" class="momentum" aria-labelledby="momentum-title">
    <header class="momentum__head">
      <div>
        <p class="momentum__eyebrow">Momentum and friction</p>
        <h3 id="momentum-title" class="momentum__title">Where practice is moving</h3>
        <p class="momentum__intro">{{ momentum.window }}</p>
      </div>
      <span class="momentum__version" :title="`Momentum version ${momentum.version}`">
        v{{ momentum.version }}
      </span>
    </header>

    <div class="momentum-stats">
      <article class="momentum-stat">
        <span class="momentum-stat__label">Completed</span>
        <strong>{{ momentum.summary.completed }}</strong>
        <span class="momentum-stat__detail">{{ momentum.summary.started }} started</span>
      </article>
      <article class="momentum-stat">
        <span class="momentum-stat__label">Clean solves</span>
        <strong>{{ momentum.summary.clean_rate }}<small>%</small></strong>
        <span class="momentum-stat__detail">{{ momentum.summary.clean_solves }} of {{ momentum.summary.completed }}</span>
      </article>
      <article class="momentum-stat">
        <span class="momentum-stat__label">Active branches</span>
        <strong>{{ momentum.summary.active_branches }}<small>/6</small></strong>
        <span class="momentum-stat__detail">practice breadth</span>
      </article>
      <article class="momentum-stat">
        <span class="momentum-stat__label">Friction branches</span>
        <strong>{{ momentum.summary.friction_branches }}</strong>
        <span class="momentum-stat__detail">{{ momentum.summary.gaining_branches }} gaining</span>
      </article>
    </div>

    <div class="momentum-cards">
      <article class="momentum-card momentum-card--gain">
        <div class="momentum-card__head">
          <span class="momentum-card__mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 17 10 11l4 4 6-7" />
              <path d="M20 8v5h-5" />
            </svg>
          </span>
          <h4>Gaining</h4>
        </div>
        <ul v-if="momentum.gaining.length" class="momentum-list">
          <li v-for="row in momentum.gaining" :key="row.branch">
            <strong>{{ row.branch }}</strong>
            <span>{{ row.evidence }}</span>
          </li>
        </ul>
        <p v-else class="momentum-empty">
          No branch has enough recent evidence to show a gain yet. Two more
          completions in a branch will start the comparison.
        </p>
      </article>

      <article class="momentum-card momentum-card--friction">
        <div class="momentum-card__head">
          <span class="momentum-card__mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 3 2 21h20L12 3Z" />
              <path d="M12 9v5" />
              <path d="M12 17h.01" />
            </svg>
          </span>
          <h4>Friction</h4>
        </div>
        <ul v-if="momentum.friction.length" class="momentum-list">
          <li v-for="row in momentum.friction" :key="row.branch">
            <strong>{{ row.branch }}</strong>
            <span>{{ row.evidence }}</span>
          </li>
        </ul>
        <p v-else class="momentum-empty">
          No branch is above the friction threshold. Keep the current pace and
          add one stretch exercise.
        </p>
      </article>

      <article class="momentum-card momentum-card--next">
        <div class="momentum-card__head">
          <span class="momentum-card__mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14" />
              <path d="m13 6 6 6-6 6" />
            </svg>
          </span>
          <h4>Next move</h4>
        </div>
        <p class="momentum-next">{{ momentum.next_move }}</p>
      </article>
    </div>

    <div class="momentum-branches">
      <div class="momentum-branches__head">
        <h4>Branch read</h4>
        <span>Recent half compared with the earlier half</span>
      </div>
      <div class="momentum-branch-grid">
        <article
          v-for="branch in momentum.branches"
          :key="branch.key"
          class="momentum-branch"
          :class="`momentum-branch--${branch.status}`"
        >
          <div class="momentum-branch__top">
            <strong>{{ branch.label }}</strong>
            <span class="momentum-branch__status">{{ branch.status_label }}</span>
          </div>
          <div
            class="momentum-branch__friction"
            role="progressbar"
            :aria-valuenow="branch.friction_score"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`${branch.label} friction: ${branch.friction_score} out of 100`"
          >
            <span :style="{ width: branch.friction_score + '%' }"></span>
          </div>
          <div class="momentum-branch__numbers">
            <span><b>{{ branch.completed }}</b> done</span>
            <span><b>{{ branch.hint_rate }}%</b> hints</span>
            <span><b>{{ branch.first_attempt_rate }}%</b> first try</span>
          </div>
          <div v-if="branch.movement.delta !== null" class="momentum-branch__compare">
            <div class="momentum-compare-row">
              <span>Earlier {{ branch.movement.earlier_clean_rate }}%</span>
              <div class="momentum-compare-track">
                <span :style="{ width: branch.movement.earlier_clean_rate + '%' }"></span>
              </div>
            </div>
            <div class="momentum-compare-row">
              <span>Recent {{ branch.movement.recent_clean_rate }}%</span>
              <div class="momentum-compare-track momentum-compare-track--recent">
                <span :style="{ width: branch.movement.recent_clean_rate + '%' }"></span>
              </div>
            </div>
          </div>
          <p class="momentum-branch__movement">
            {{ branch.movement.label }}
            <span v-if="branch.movement.delta !== null" class="momentum-branch__delta">
              {{ signed(branch.movement.delta) }} pts
            </span>
          </p>
          <p class="momentum-branch__next">{{ branch.next_action }}</p>
          <router-link
            v-if="branch.next_lab"
            :to="`/exercises/${branch.next_lab.track_slug}`"
            class="momentum-branch__link"
          >
            Open next exercise: {{ branch.next_lab.name }}
          </router-link>
        </article>
      </div>
    </div>

    <div v-if="momentum.stuck_points.length" class="momentum-stuck">
      <div class="momentum-branches__head">
        <h4>Where the friction is</h4>
        <span>Use these as review prompts, not labels</span>
      </div>
      <ul class="momentum-stuck-list">
        <li v-for="point in momentum.stuck_points" :key="point.lab">
          <div>
            <strong>{{ point.lab }}</strong>
            <span class="momentum-stuck__branch">{{ point.branch }}</span>
          </div>
          <p>{{ point.reason }} — {{ point.evidence }}</p>
        </li>
      </ul>
    </div>

    <p class="momentum__disclaimer">{{ momentum.disclaimer }}</p>
  </section>
</template>

<script setup>
defineProps({
  momentum: { type: Object, default: null },
})

function signed(value) {
  const number = Number(value)
  if (!Number.isFinite(number) || number === 0) return '0'
  return `${number > 0 ? '+' : ''}${number}`
}
</script>

<style scoped>
.momentum {
  margin: 1.25rem 0;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
}

.momentum__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.momentum__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.momentum__title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 650;
}

.momentum__intro {
  max-width: 58rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.8125rem;
  line-height: 1.5;
}

.momentum__version {
  flex: 0 0 auto;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.6875rem;
}

.momentum-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.65rem;
  margin: 0.9rem 0;
}

.momentum-stat {
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.momentum-stat__label {
  display: block;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.momentum-stat strong {
  display: block;
  margin-top: 0.15rem;
  color: var(--text-primary);
  font-size: 1.35rem;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}

.momentum-stat strong small {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
}

.momentum-stat__detail {
  color: var(--text-muted);
  font-size: 0.72rem;
}

.momentum-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.65rem;
}

.momentum-card {
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.momentum-card--gain {
  border-color: color-mix(in srgb, var(--success) 45%, var(--border-color));
}

.momentum-card--friction {
  border-color: color-mix(in srgb, var(--warning) 55%, var(--border-color));
}

.momentum-card--next {
  border-color: color-mix(in srgb, var(--accent) 55%, var(--border-color));
}

.momentum-card__head {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.momentum-card__mark {
  display: inline-grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.momentum-card--gain .momentum-card__mark {
  color: var(--success);
}

.momentum-card--friction .momentum-card__mark {
  color: var(--warning);
}

.momentum-card--next .momentum-card__mark {
  color: var(--accent-text);
}

.momentum-card__mark svg {
  width: 14px;
  height: 14px;
}

.momentum-card h4,
.momentum-branches h4,
.momentum-stuck h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 650;
}

.momentum-list {
  margin: 0.5rem 0 0;
  padding: 0;
  list-style: none;
}

.momentum-list li {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.4rem 0;
  border-top: 1px solid var(--border-color);
}

.momentum-list li:first-child {
  border-top: 0;
}

.momentum-list strong {
  color: var(--text-primary);
  font-size: 0.78rem;
}

.momentum-list span,
.momentum-empty,
.momentum-next {
  color: var(--text-secondary);
  font-size: 0.76rem;
  line-height: 1.45;
}

.momentum-empty,
.momentum-next {
  margin: 0.5rem 0 0;
}

.momentum-next {
  color: var(--text-primary);
}

.momentum-branches {
  margin-top: 1rem;
}

.momentum-branches__head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}

.momentum-branches__head span {
  color: var(--text-muted);
  font-size: 0.7rem;
}

.momentum-branch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.65rem;
}

.momentum-branch {
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.momentum-branch--gaining {
  border-left: 3px solid var(--success);
}

.momentum-branch--friction {
  border-left: 3px solid var(--warning);
}

.momentum-branch--steady {
  border-left: 3px solid var(--accent);
}

.momentum-branch--no_evidence {
  border-left: 3px solid var(--text-muted);
}

.momentum-branch__top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
}

.momentum-branch__top strong {
  color: var(--text-primary);
  font-size: 0.8rem;
}

.momentum-branch__status {
  color: var(--text-secondary);
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.momentum-branch__friction {
  height: 6px;
  margin: 0.45rem 0;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.momentum-branch__friction span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--text-muted);
  transition: width 220ms ease;
}

.momentum-branch--gaining .momentum-branch__friction span {
  background: var(--success);
}

.momentum-branch--friction .momentum-branch__friction span {
  background: var(--warning);
}

.momentum-branch--steady .momentum-branch__friction span {
  background: var(--accent);
}

.momentum-branch__numbers {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.7rem;
  color: var(--text-muted);
  font-size: 0.7rem;
}

.momentum-branch__numbers b {
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}

.momentum-branch__compare {
  margin-top: 0.5rem;
  display: grid;
  gap: 0.3rem;
}

.momentum-compare-row {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  align-items: center;
  gap: 0.4rem;
  color: var(--text-muted);
  font-size: 0.66rem;
}

.momentum-compare-track {
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.momentum-compare-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--text-muted);
}

.momentum-compare-track--recent span {
  background: var(--accent);
}

.momentum-branch--gaining .momentum-compare-track--recent span {
  background: var(--success);
}

.momentum-branch--friction .momentum-compare-track--recent span {
  background: var(--warning);
}

.momentum-branch__movement {
  margin: 0.5rem 0 0;
  color: var(--text-primary);
  font-size: 0.75rem;
  font-weight: 600;
}

.momentum-branch__delta {
  margin-left: 0.35rem;
  color: var(--text-muted);
  font-weight: 500;
}

.momentum-branch__next {
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.45;
}

.momentum-branch__link {
  display: inline-block;
  margin-top: 0.45rem;
  color: var(--accent-text);
  font-size: 0.7rem;
  font-weight: 600;
  text-decoration: none;
}

.momentum-branch__link:hover {
  text-decoration: underline;
}

.momentum-branch__link:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 4px;
}

.momentum-stuck {
  margin-top: 1rem;
}

.momentum-stuck-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.65rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.momentum-stuck-list li {
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.momentum-stuck-list strong {
  color: var(--text-primary);
  font-size: 0.78rem;
}

.momentum-stuck__branch {
  margin-left: 0.4rem;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.momentum-stuck-list p {
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.45;
}

.momentum__disclaimer {
  margin: 0.9rem 0 0;
  padding-top: 0.7rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.7rem;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .momentum__head,
  .momentum-branches__head {
    flex-direction: column;
    align-items: flex-start;
  }

  .momentum-compare-row {
    grid-template-columns: 74px minmax(0, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .momentum-branch__friction span {
    transition: none;
  }
}
</style>
