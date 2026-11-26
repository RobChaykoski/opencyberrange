<template>
  <section
    v-if="visible"
    class="ha-card"
    :class="`ha-card--${status.verdict}`"
    aria-labelledby="ha-card-title"
  >
    <div class="ha-card__head">
      <div>
        <h3 id="ha-card-title" class="section-title">High availability</h3>
        <p class="ha-card__summary">{{ summary }}</p>
      </div>
      <button
        type="button"
        class="btn btn--secondary btn--sm"
        :disabled="loading"
        @click="$emit('refresh')"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <dl class="ha-card__grid">
      <div class="ha-card__row">
        <dt>This node</dt>
        <dd>{{ roleLabel }}</dd>
      </div>
      <div class="ha-card__row">
        <dt>Preferred</dt>
        <dd>{{ preferredLabel }}</dd>
      </div>
      <div class="ha-card__row">
        <dt>Replication</dt>
        <dd>{{ replicationLabel }}</dd>
      </div>
      <div class="ha-card__row">
        <dt>Redis</dt>
        <dd>{{ redisLabel }}</dd>
      </div>
      <div class="ha-card__row">
        <dt>Witness</dt>
        <dd>{{ witnessLabel }}</dd>
      </div>
      <div class="ha-card__row">
        <dt>Last failover</dt>
        <dd>{{ failoverLabel }}</dd>
      </div>
    </dl>

    <p class="ha-card__observed">{{ observedLabel }}</p>
    <p v-if="status.detail" class="ha-card__detail">{{ status.detail }}</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

defineEmits(['refresh'])

const visible = computed(() => Boolean(props.status?.available))

const roleLabel = computed(() => {
  const role = props.status?.role
  if (role === 'primary') return 'Primary'
  if (role === 'standby') return 'Standby'
  return 'Unknown'
})

const preferredLabel = computed(() => {
  const preferred = props.status?.preferred
  if (preferred === 'prod') return 'Production'
  if (preferred === 'dev') return 'Development'
  return 'Not recorded'
})

const replicationLabel = computed(() => {
  const replication = props.status?.replication
  if (!replication || !replication.state) return 'Not reported'
  const state = replication.state === 'streaming' ? 'Streaming' : replication.state
  if (Number.isInteger(replication.lag_bytes)) {
    return `${state} · lag ${formatBytes(replication.lag_bytes)}`
  }
  return state
})

const redisLabel = computed(() => {
  const redis = props.status?.redis
  if (!redis || (!redis.master && !redis.sentinels)) return 'Not reported'
  const parts = []
  if (redis.master) parts.push(`master ${redis.master}`)
  if (redis.sentinels) parts.push(`${redis.sentinels} sentinels`)
  return parts.join(' · ')
})

const witnessLabel = computed(() => {
  const witness = props.status?.witness
  if (!witness || (!witness.prod && !witness.dev)) return 'Not reported'
  if (witness.prod === 'up' && witness.dev === 'up') return 'Both up'
  return `prod ${witness.prod || 'unknown'} · dev ${witness.dev || 'unknown'}`
})

const failoverLabel = computed(() => {
  const failover = props.status?.last_failover
  if (!failover) return 'None'
  const route = [failover.from, failover.to].filter(Boolean).join(' → ')
  const verified =
    failover.verified === true
      ? 'verified'
      : failover.verified === false
        ? 'not verified'
        : 'verification unknown'
  return route ? `${route} · ${verified}` : verified
})

const observedLabel = computed(() => {
  const checkedAt = props.status?.checked_at
  const age = props.status?.age_seconds
  if (!checkedAt) return 'Observed: no snapshot timestamp'
  const ageText = Number.isInteger(age) ? ` · ${age} s ago` : ''
  return `Observed ${checkedAt}${ageText}`
})

const summary = computed(() => {
  const verdict = props.status?.verdict
  if (verdict === 'ok') return 'HA checks are current.'
  if (verdict === 'warning') return 'Some HA checks need attention.'
  if (verdict === 'error') return 'Action needed; failover would lose data.'
  return 'HA status is unknown; the last snapshot is stale or unreadable.'
})

function formatBytes(value) {
  if (!Number.isFinite(value) || value < 0) return 'unknown'
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`
  if (value < 1024 * 1024 * 1024) {
    return `${Math.round(value / (1024 * 1024))} MB`
  }
  return `${(value / (1024 * 1024 * 1024)).toFixed(1)} GB`
}
</script>

<style scoped>
.ha-card {
  margin-bottom: 1.25rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--border-color, #334155);
  border-left: 4px solid var(--text-secondary, #94a3b8);
  border-radius: 0.5rem;
  background: var(--bg-secondary, #1e293b);
}

.ha-card--ok {
  border-left-color: var(--success);
}

.ha-card--warning {
  border-left-color: var(--warning);
}

.ha-card--error {
  border-left-color: var(--danger);
}

.ha-card--unknown {
  border-left-color: var(--text-secondary, #94a3b8);
}

.ha-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.ha-card__summary {
  margin: 0.25rem 0 0;
  color: var(--text-secondary, #94a3b8);
  font-size: 0.875rem;
}

.ha-card__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.65rem 1.25rem;
  margin: 0;
}

.ha-card__row {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.ha-card__row dt {
  color: var(--text-secondary, #94a3b8);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.ha-card__row dd {
  margin: 0;
  color: var(--text-primary, #e2e8f0);
  font-size: 0.875rem;
}

.ha-card__observed,
.ha-card__detail {
  margin: 0.75rem 0 0;
  color: var(--text-secondary, #94a3b8);
  font-size: 0.8125rem;
}

.ha-card--error .ha-card__detail {
  color: var(--danger);
}

.ha-card--warning .ha-card__detail {
  color: var(--warning);
}
</style>
