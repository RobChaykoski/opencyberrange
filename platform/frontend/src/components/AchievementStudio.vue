<template>
  <section class="studio" aria-labelledby="achievement-studio-title">
    <header class="studio__head">
      <div>
        <p class="studio__eyebrow">Achievement studio</p>
        <h2 id="achievement-studio-title">Group, filter, and value every badge</h2>
        <p class="studio__intro">
          Built-in badges and your own goals live in one catalogue. Tier and
          difficulty set the point value, so a platinum expert badge is worth
          more than a bronze starter badge.
        </p>
      </div>
      <button type="button" class="btn btn--primary btn--sm" @click="startCreate">
        New achievement
      </button>
    </header>

    <p v-if="loading" class="studio-state">Loading the achievement catalogue…</p>
    <p v-else-if="error" class="studio-state studio-state--error" role="alert">{{ error }}</p>

    <template v-else-if="data">
      <div class="studio-summary">
        <article class="studio-stat">
          <span>Total</span>
          <strong>{{ data.summary.total }}</strong>
          <small>{{ data.summary.builtin }} built-in · {{ data.summary.custom }} custom</small>
        </article>
        <article class="studio-stat studio-stat--green">
          <span>Active</span>
          <strong>{{ data.summary.active }}</strong>
          <small>{{ data.summary.inactive }} disabled</small>
        </article>
        <article class="studio-stat studio-stat--amber">
          <span>Hidden</span>
          <strong>{{ data.summary.hidden }}</strong>
          <small>shown after they are earned</small>
        </article>
        <article class="studio-stat studio-stat--accent">
          <span>Points available</span>
          <strong>{{ data.summary.total_points }}</strong>
          <small>across the catalogue</small>
        </article>
        <article v-for="tier in data.tiers" :key="tier.key" class="studio-stat" :class="`studio-stat--${tier.key}`">
          <span>{{ tier.label }}</span>
          <strong>{{ data.summary.by_tier[tier.key] || 0 }}</strong>
          <small>{{ tier.points }} base points</small>
        </article>
      </div>

      <p v-if="message" class="studio-message" :class="messageKind === 'error' ? 'studio-message--error' : 'studio-message--ok'" role="status">
        {{ message }}
      </p>

      <form v-if="showForm" class="studio-form" @submit.prevent="saveDraft">
        <div class="studio-form__head">
          <div>
            <p class="studio__eyebrow">{{ editingId ? 'Edit achievement' : 'New achievement' }}</p>
            <h3>{{ editingId ? 'Update the goal' : 'Create a goal for your programme' }}</h3>
          </div>
          <button type="button" class="btn btn--outline btn--xs" @click="cancelForm">Cancel</button>
        </div>

        <div class="studio-form__grid">
          <label class="studio-field studio-field--icon">
            <span>Icon</span>
            <input v-model="draft.icon" type="text" maxlength="4" aria-label="Achievement icon" />
          </label>
          <label class="studio-field studio-field--wide">
            <span>Name</span>
            <input v-model="draft.name" type="text" maxlength="80" required placeholder="e.g. Night Owl" />
          </label>
          <label class="studio-field studio-field--full">
            <span>Description</span>
            <textarea v-model="draft.description" rows="2" maxlength="500" placeholder="What the learner did, in plain language."></textarea>
          </label>
          <label class="studio-field">
            <span>Group</span>
            <select v-model="draft.group_key">
              <option v-for="group in data.groups" :key="group.key" :value="group.key">{{ group.label }}</option>
            </select>
          </label>
          <label class="studio-field">
            <span>Tier</span>
            <select v-model="draft.tier">
              <option v-for="tier in data.tiers" :key="tier.key" :value="tier.key">{{ tier.label }}</option>
            </select>
          </label>
          <label class="studio-field">
            <span>Difficulty</span>
            <select v-model="draft.difficulty">
              <option v-for="item in data.difficulties" :key="item.key" :value="item.key">{{ item.label }}</option>
            </select>
          </label>
          <label class="studio-field">
            <span>Trigger</span>
            <select v-model="draft.trigger">
              <option v-for="trigger in data.triggers" :key="trigger.value" :value="trigger.value">{{ trigger.label }}</option>
            </select>
          </label>
          <label class="studio-field">
            <span>Threshold</span>
            <input v-model.number="draft.threshold" type="number" min="1" max="10000" :disabled="thresholdDisabled" />
            <small v-if="thresholdDisabled">This trigger does not use a count.</small>
          </label>
          <label class="studio-field studio-field--check">
            <input v-model="draft.is_active" type="checkbox" />
            <span>Active immediately</span>
          </label>
        </div>

        <div class="studio-preview" aria-live="polite">
          <span class="studio-preview__icon" aria-hidden="true">{{ draft.icon || '🏅' }}</span>
          <div>
            <strong>{{ draft.name || 'Untitled achievement' }}</strong>
            <p>{{ draft.description || 'Add a short description so learners know what they earned.' }}</p>
          </div>
          <div class="studio-preview__value">
            <span class="studio-tier" :class="`studio-tier--${draft.tier}`">{{ tierLabel(draft.tier) }}</span>
            <span>{{ difficultyLabel(draft.difficulty) }}</span>
            <strong>{{ previewPoints }} pts</strong>
          </div>
        </div>

        <div class="studio-form__actions">
          <button type="submit" class="btn btn--primary btn--sm" :disabled="saving || !draft.name.trim()">
            {{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Create achievement' }}
          </button>
          <button type="button" class="btn btn--outline btn--sm" @click="cancelForm">Cancel</button>
        </div>
      </form>

      <div class="studio-toolbar" role="search">
        <label class="studio-search">
          <span class="sr-only">Search achievements</span>
          <input v-model="filters.search" type="search" placeholder="Search name, description, or type" />
        </label>
        <label class="studio-filter">
          <span>Group</span>
          <select v-model="filters.group">
            <option value="all">All groups</option>
            <option v-for="group in data.groups" :key="group.key" :value="group.key">{{ group.label }}</option>
          </select>
        </label>
        <label class="studio-filter">
          <span>Tier</span>
          <select v-model="filters.tier">
            <option value="all">All tiers</option>
            <option v-for="tier in data.tiers" :key="tier.key" :value="tier.key">{{ tier.label }}</option>
          </select>
        </label>
        <label class="studio-filter">
          <span>Source</span>
          <select v-model="filters.source">
            <option value="all">All sources</option>
            <option value="builtin">Built-in</option>
            <option value="custom">Custom</option>
          </select>
        </label>
        <label class="studio-filter">
          <span>State</span>
          <select v-model="filters.state">
            <option value="all">All states</option>
            <option value="active">Active</option>
            <option value="inactive">Disabled</option>
          </select>
        </label>
        <button type="button" class="btn btn--outline btn--xs" @click="resetFilters">Reset</button>
      </div>

      <p class="studio-count" aria-live="polite">
        Showing {{ filtered.length }} of {{ data.achievements.length }} achievements.
      </p>

      <p v-if="!filtered.length" class="studio-empty">
        No achievements match these filters. Clear the search or choose a different group.
      </p>

      <div v-else class="studio-groups">
        <details
          v-for="group in visibleGroups"
          :key="group.key"
          class="studio-group"
          :open="group.key !== 'hidden'"
        >
          <summary class="studio-group__summary">
            <span class="studio-group__label">{{ group.label }}</span>
            <span class="studio-group__count">{{ grouped[group.key].length }}</span>
            <span class="studio-group__desc">{{ group.description }}</span>
          </summary>

          <div class="studio-cards">
            <article
              v-for="item in grouped[group.key]"
              :key="item.id"
              class="studio-card"
              :class="[`studio-card--${item.tier}`, { 'studio-card--inactive': !item.is_active }]"
            >
              <div class="studio-card__head">
                <span class="studio-card__icon" aria-hidden="true">{{ item.icon }}</span>
                <div class="studio-card__title">
                  <h4>{{ item.name }}</h4>
                  <span class="studio-card__type">{{ item.source === 'builtin' ? 'Built-in' : 'Custom' }}</span>
                </div>
                <span class="studio-tier" :class="`studio-tier--${item.tier}`">{{ tierLabel(item.tier) }}</span>
              </div>

              <p class="studio-card__desc">{{ item.description || 'No description yet.' }}</p>

              <div class="studio-card__meta">
                <span>{{ difficultyLabel(item.difficulty) }}</span>
                <span><strong>{{ item.points }}</strong> pts</span>
                <span v-if="item.hidden" class="studio-chip studio-chip--hidden">Hidden</span>
                <span v-if="!item.is_active" class="studio-chip studio-chip--inactive">Disabled</span>
              </div>

              <p v-if="item.trigger" class="studio-card__trigger">
                {{ triggerLabel(item.trigger) }}
                <template v-if="!thresholdDisabledFor(item.trigger)"> · {{ item.threshold }}</template>
              </p>

              <div v-if="item.editable" class="studio-card__actions">
                <button type="button" class="btn btn--outline btn--xs" @click="startEdit(item)">Edit</button>
                <button type="button" class="btn btn--outline btn--xs" @click="toggleActive(item)">
                  {{ item.is_active ? 'Disable' : 'Enable' }}
                </button>
                <button
                  type="button"
                  class="btn btn--danger btn--xs"
                  :class="{ 'btn--confirm': confirmingId === item.id }"
                  @click="deleteAchievement(item)"
                >
                  {{ confirmingId === item.id ? 'Confirm delete' : 'Delete' }}
                </button>
              </div>
              <p v-else class="studio-card__readonly">Built-in achievement. It runs in code and cannot be edited here.</p>
            </article>
          </div>
        </details>
      </div>

      <p class="studio-note">{{ data.note }}</p>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const data = ref(null)
const loading = ref(true)
const error = ref('')
const message = ref('')
const messageKind = ref('ok')
const saving = ref(false)
const showForm = ref(false)
const editingId = ref(null)
const confirmingId = ref(null)

const filters = reactive({
  search: '',
  group: 'all',
  tier: 'all',
  source: 'all',
  state: 'all',
})

const emptyDraft = () => ({
  icon: '🏅',
  name: '',
  description: '',
  group_key: 'custom',
  tier: 'bronze',
  difficulty: 'standard',
  trigger: 'labs_completed',
  threshold: 1,
  is_active: true,
})

const draft = reactive(emptyDraft())

const tierBase = { bronze: 10, silver: 25, gold: 50, platinum: 100 }
const difficultyMultiplier = { starter: 0.75, standard: 1, advanced: 1.5, expert: 2 }

const previewPoints = computed(() => {
  const base = tierBase[draft.tier] || 10
  const multiplier = difficultyMultiplier[draft.difficulty] || 1
  return Math.max(5, Math.round(base * multiplier))
})

const thresholdDisabled = computed(() =>
  ['course_completed', 'osint_track_completed', 'all_tracks_completed'].includes(draft.trigger)
)

const filtered = computed(() => {
  const items = data.value?.achievements || []
  const search = filters.search.trim().toLowerCase()
  return items.filter((item) => {
    if (filters.group !== 'all' && item.group_key !== filters.group) return false
    if (filters.tier !== 'all' && item.tier !== filters.tier) return false
    if (filters.source !== 'all' && item.source !== filters.source) return false
    if (filters.state === 'active' && !item.is_active) return false
    if (filters.state === 'inactive' && item.is_active) return false
    if (!search) return true
    return [item.name, item.description, item.type, item.trigger]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(search))
  })
})

const grouped = computed(() => {
  const buckets = {}
  for (const item of filtered.value) {
    buckets[item.group_key] = buckets[item.group_key] || []
    buckets[item.group_key].push(item)
  }
  return buckets
})

const visibleGroups = computed(() =>
  (data.value?.groups || []).filter((group) => grouped.value[group.key]?.length)
)

function tierLabel(key) {
  return data.value?.tiers.find((tier) => tier.key === key)?.label || key
}

function difficultyLabel(key) {
  return data.value?.difficulties.find((item) => item.key === key)?.label || key
}

function triggerLabel(key) {
  return data.value?.triggers.find((item) => item.value === key)?.label || key
}

function thresholdDisabledFor(key) {
  return ['course_completed', 'osint_track_completed', 'all_tracks_completed'].includes(key)
}

function flash(text, kind = 'ok') {
  message.value = text
  messageKind.value = kind
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/settings/achievement-catalogue')
    data.value = response.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load the achievement catalogue.'
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.search = ''
  filters.group = 'all'
  filters.tier = 'all'
  filters.source = 'all'
  filters.state = 'all'
}

function startCreate() {
  Object.assign(draft, emptyDraft())
  editingId.value = null
  showForm.value = true
  message.value = ''
}

function startEdit(item) {
  if (!item.editable) return
  Object.assign(draft, {
    icon: item.icon || '🏅',
    name: item.name,
    description: item.description || '',
    group_key: item.group_key,
    tier: item.tier,
    difficulty: item.difficulty,
    trigger: item.trigger || 'labs_completed',
    threshold: item.threshold || 1,
    is_active: item.is_active,
  })
  editingId.value = item.custom_id
  showForm.value = true
  message.value = ''
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  Object.assign(draft, emptyDraft())
}

async function saveDraft() {
  if (!draft.name.trim()) return
  saving.value = true
  const payload = {
    icon: draft.icon || '🏅',
    name: draft.name.trim(),
    description: draft.description.trim(),
    group_key: draft.group_key,
    tier: draft.tier,
    difficulty: draft.difficulty,
    trigger: draft.trigger,
    threshold: thresholdDisabled.value ? 1 : draft.threshold || 1,
    is_active: draft.is_active,
  }
  try {
    if (editingId.value) {
      await axios.put(`/settings/custom-achievements/${editingId.value}`, payload)
      flash('Achievement updated.')
    } else {
      await axios.post('/settings/custom-achievements', payload)
      flash('Achievement created.')
    }
    cancelForm()
    await load()
  } catch (e) {
    flash(e.response?.data?.detail || 'Could not save the achievement.', 'error')
  } finally {
    saving.value = false
  }
}

async function toggleActive(item) {
  try {
    await axios.put(`/settings/custom-achievements/${item.custom_id}`, {
      is_active: !item.is_active,
    })
    flash(item.is_active ? 'Achievement disabled.' : 'Achievement enabled.')
    await load()
  } catch (e) {
    flash(e.response?.data?.detail || 'Could not update the achievement.', 'error')
  }
}

async function deleteAchievement(item) {
  if (confirmingId.value !== item.id) {
    confirmingId.value = item.id
    return
  }
  try {
    await axios.delete(`/settings/custom-achievements/${item.custom_id}`)
    confirmingId.value = null
    flash('Achievement deleted. Awards already earned are kept.')
    await load()
  } catch (e) {
    flash(e.response?.data?.detail || 'Could not delete the achievement.', 'error')
  }
}

onMounted(load)
</script>

<style scoped>
.studio {
  display: grid;
  gap: 0.85rem;
}

.studio__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    radial-gradient(circle at 100% 0%, var(--accent-bg), transparent 55%),
    var(--bg-secondary);
}

.studio__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.studio__head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.15rem;
  font-weight: 750;
}

.studio__intro {
  max-width: 58rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.5;
}

.studio-state {
  margin: 0;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.studio-state--error {
  border-color: var(--danger);
  color: var(--danger);
}

.studio-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
}

.studio-stat {
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.studio-stat--green { border-left: 3px solid var(--success); }
.studio-stat--amber { border-left: 3px solid var(--warning); }
.studio-stat--accent { border-left: 3px solid var(--accent); }
.studio-stat--bronze { border-left: 3px solid #b45309; }
.studio-stat--silver { border-left: 3px solid #94a3b8; }
.studio-stat--gold { border-left: 3px solid #d97706; }
.studio-stat--platinum { border-left: 3px solid #7c3aed; }

.studio-stat span {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.studio-stat strong {
  display: block;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-variant-numeric: tabular-nums;
}

.studio-stat small {
  display: block;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.studio-message {
  margin: 0;
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  font-size: 0.72rem;
}

.studio-message--ok {
  border: 1px solid var(--success);
  background: var(--success-bg);
  color: var(--text-primary);
}

.studio-message--error {
  border: 1px solid var(--danger);
  background: var(--danger-bg);
  color: var(--text-primary);
}

.studio-form {
  padding: 0.9rem 1rem;
  border: 1px solid var(--accent);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.studio-form__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.65rem;
}

.studio-form__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 700;
}

.studio-form__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.55rem;
}

.studio-field {
  display: grid;
  gap: 0.2rem;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.studio-field--wide { grid-column: span 2; }
.studio-field--full { grid-column: 1 / -1; }
.studio-field--icon input { max-width: 5rem; text-align: center; }

.studio-field input,
.studio-field select,
.studio-field textarea {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
  font-size: 0.76rem;
  text-transform: none;
  letter-spacing: normal;
}

.studio-field input:focus-visible,
.studio-field select:focus-visible,
.studio-field textarea:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.studio-field small {
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 400;
  text-transform: none;
  letter-spacing: normal;
}

.studio-field--check {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  align-self: end;
  padding-bottom: 0.35rem;
  text-transform: none;
  letter-spacing: normal;
  font-size: 0.7rem;
}

.studio-field--check input {
  width: auto;
}

.studio-preview {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  margin-top: 0.7rem;
  padding: 0.6rem 0.7rem;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.studio-preview__icon {
  font-size: 1.4rem;
  line-height: 1;
}

.studio-preview strong {
  color: var(--text-primary);
  font-size: 0.8rem;
}

.studio-preview p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.68rem;
  line-height: 1.4;
}

.studio-preview__value {
  display: grid;
  justify-items: end;
  gap: 0.15rem;
  margin-left: auto;
  color: var(--text-muted);
  font-size: 0.62rem;
  white-space: nowrap;
}

.studio-preview__value strong {
  color: var(--accent-text);
  font-size: 0.8rem;
}

.studio-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.65rem;
}

.studio-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.45rem;
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.studio-search {
  flex: 1 1 220px;
  min-width: 180px;
}

.studio-search input {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
  font-size: 0.74rem;
}

.studio-filter {
  display: grid;
  gap: 0.15rem;
  color: var(--text-muted);
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.studio-filter select {
  padding: 0.35rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
  font-size: 0.72rem;
  text-transform: none;
  letter-spacing: normal;
}

.studio-search input:focus-visible,
.studio-filter select:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.studio-count {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.66rem;
}

.studio-empty {
  margin: 0;
  padding: 1rem;
  border: 1px dashed var(--border-color);
  border-radius: 10px;
  color: var(--text-muted);
  font-size: 0.74rem;
  text-align: center;
}

.studio-groups {
  display: grid;
  gap: 0.6rem;
}

.studio-group {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.studio-group__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 0.7rem;
  cursor: pointer;
}

.studio-group__label {
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 700;
}

.studio-group__count {
  padding: 0.08rem 0.35rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.58rem;
  font-weight: 700;
}

.studio-group__desc {
  flex: 1 1 240px;
  color: var(--text-muted);
  font-size: 0.64rem;
}

.studio-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.5rem;
  padding: 0 0.7rem 0.7rem;
}

.studio-card {
  display: flex;
  flex-direction: column;
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.studio-card--bronze { border-top: 3px solid #b45309; }
.studio-card--silver { border-top: 3px solid #94a3b8; }
.studio-card--gold { border-top: 3px solid #d97706; }
.studio-card--platinum { border-top: 3px solid #7c3aed; }

.studio-card--inactive {
  opacity: 0.7;
}

.studio-card__head {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
}

.studio-card__icon {
  font-size: 1.2rem;
  line-height: 1;
}

.studio-card__title {
  flex: 1;
  min-width: 0;
}

.studio-card__title h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.78rem;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.studio-card__type {
  color: var(--text-muted);
  font-size: 0.56rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.studio-tier {
  flex: 0 0 auto;
  padding: 0.1rem 0.35rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.54rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.studio-tier--bronze { background: rgba(180, 83, 9, 0.18); color: #d97706; }
.studio-tier--silver { background: rgba(148, 163, 184, 0.2); color: #94a3b8; }
.studio-tier--gold { background: rgba(217, 119, 6, 0.18); color: #f59e0b; }
.studio-tier--platinum { background: rgba(124, 58, 237, 0.18); color: #a78bfa; }

.studio-card__desc {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.68rem;
  line-height: 1.4;
}

.studio-card__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.3rem 0.55rem;
  margin-top: 0.4rem;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.studio-card__meta strong {
  color: var(--accent-text);
}

.studio-chip {
  padding: 0.06rem 0.3rem;
  border-radius: 999px;
  font-size: 0.54rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.studio-chip--hidden { background: var(--warning-bg); color: var(--warning); }
.studio-chip--inactive { background: var(--danger-bg); color: var(--danger); }

.studio-card__trigger {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.6rem;
  line-height: 1.4;
}

.studio-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.55rem;
  padding-top: 0.45rem;
  border-top: 1px solid var(--border-color);
}

.btn--confirm {
  background: var(--danger-bg);
  border-color: var(--danger);
  color: var(--danger);
}

.studio-card__readonly {
  margin: 0.5rem 0 0;
  color: var(--text-muted);
  font-size: 0.58rem;
  line-height: 1.4;
}

.studio-note {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.64rem;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .studio__head,
  .studio-form__head {
    flex-direction: column;
  }

  .studio-field--wide {
    grid-column: span 1;
  }
}
</style>
