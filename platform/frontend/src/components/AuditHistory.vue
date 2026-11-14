<template>
  <section class="audit-card" aria-labelledby="audit-title">
    <header class="audit-card__head">
      <div>
        <h3 id="audit-title">{{ title || 'Interaction history' }}</h3>
        <p v-if="data" class="audit-card__meta">
          {{ data.user.username }} · {{ data.user.role }}
          · {{ data.event_count }} events
          · {{ data.impersonation_count }} impersonations
        </p>
      </div>
      <button type="button" class="btn btn--outline btn--sm" @click="$emit('close')">Close</button>
    </header>

    <p v-if="loading" class="audit-state">Loading history...</p>
    <p v-else-if="error" class="audit-state audit-state--error" role="alert">{{ error }}</p>

    <template v-else-if="data">
      <h4 class="audit-section-title">Impersonation sessions</h4>
      <div v-if="!data.impersonations.length" class="audit-empty">
        No impersonation sessions involve this user.
      </div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Actor → target</th>
              <th>Mode</th>
              <th>Started</th>
              <th>Ended / expires</th>
              <th>IP</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in data.impersonations" :key="row.session_id">
              <td>
                <span class="audit-status" :class="`audit-status--${row.status}`">{{ row.status }}</span>
              </td>
              <td>{{ row.actor_username }} → {{ row.target_username || 'role view' }}</td>
              <td>{{ row.mode }}</td>
              <td>{{ formatTime(row.started_at) }}</td>
              <td>{{ row.ended_at ? formatTime(row.ended_at) : `expires ${formatTime(row.expires_at)}` }}</td>
              <td class="audit-mono">{{ row.ip_address || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h4 class="audit-section-title">Activity timeline</h4>
      <div v-if="!data.events.length" class="audit-empty">No recorded activity for this user.</div>
      <ol v-else class="audit-timeline">
        <li v-for="event in data.events" :key="event.id">
          <span class="audit-timeline__time">{{ formatTime(event.created_at) }}</span>
          <div>
            <strong>{{ event.label }}</strong>
            <span v-if="event.actor_name" class="audit-timeline__actor">by {{ event.actor_name }}</span>
            <p v-if="event.target_label" class="audit-timeline__target">
              target: {{ event.target_label }}
            </p>
            <p v-if="event.ip_address" class="audit-timeline__ip">IP {{ event.ip_address }}</p>
            <details v-if="hasDetail(event)" class="audit-timeline__detail">
              <summary>Details</summary>
              <pre>{{ prettyDetail(event.detail) }}</pre>
            </details>
          </div>
        </li>
      </ol>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  endpoint: { type: String, required: true },
  title: { type: String, default: '' },
})
defineEmits(['close'])

const data = ref(null)
const loading = ref(true)
const error = ref('')

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get(props.endpoint)
    data.value = response.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load the audit history.'
  } finally {
    loading.value = false
  }
}

const formatTime = (value) => {
  if (!value) return '—'
  const date = new Date(value.endsWith?.('Z') ? value : `${value}Z`)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

const hasDetail = (event) =>
  event.detail && (typeof event.detail !== 'object' || Object.keys(event.detail).length > 0)

const prettyDetail = (detail) =>
  typeof detail === 'string' ? detail : JSON.stringify(detail, null, 2)

onMounted(load)
</script>

<style scoped>
.audit-card {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}
.audit-card__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}
.audit-card__head h3 { margin: 0; font-size: 1rem; }
.audit-card__meta { margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.8rem; }
.audit-state { color: var(--text-muted); }
.audit-state--error { color: var(--danger); }
.audit-section-title { margin: 1.1rem 0 0.5rem; font-size: 0.9rem; }
.audit-empty { color: var(--text-muted); font-size: 0.85rem; }
.audit-status {
  text-transform: capitalize;
  font-size: 0.75rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
}
.audit-status--live { color: var(--success); border-color: var(--success); }
.audit-status--ended { color: var(--text-muted); }
.audit-status--expired { color: var(--warning, #d97706); }
.audit-mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.75rem; }
.audit-timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-height: 32rem;
  overflow: auto;
}
.audit-timeline li {
  display: grid;
  grid-template-columns: 11rem 1fr;
  gap: 0.75rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--border-color);
}
.audit-timeline__time { color: var(--text-muted); font-size: 0.75rem; }
.audit-timeline__actor { margin-left: 0.4rem; color: var(--text-secondary); font-size: 0.8rem; }
.audit-timeline__target,
.audit-timeline__ip { margin: 0.15rem 0 0; color: var(--text-muted); font-size: 0.75rem; }
.audit-timeline__detail { margin-top: 0.25rem; }
.audit-timeline__detail pre {
  margin: 0.35rem 0 0;
  padding: 0.5rem;
  background: var(--bg-primary);
  border-radius: 6px;
  font-size: 0.72rem;
  overflow: auto;
}
@media (max-width: 720px) {
  .audit-timeline li { grid-template-columns: 1fr; gap: 0.25rem; }
}
</style>
