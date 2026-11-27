<template>
  <div class="capstone">
    <header class="capstone__head">
      <div>
        <p class="capstone__eyebrow">Release 6.1</p>
        <h1>Capstone Builder</h1>
        <p class="capstone__intro">
          Turn a role profile into a teachable capstone. The planner proposes
          objectives, labs, assessments, and deliverables from the competency
          model; you review, waive gaps with a reason, and approve. Nothing is
          published or graded here.
        </p>
      </div>
      <button type="button" class="btn btn--secondary btn--sm" :disabled="loadingPlans" @click="loadPlans">
        {{ loadingPlans ? 'Loading...' : 'Refresh plans' }}
      </button>
    </header>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="message" class="capstone__message" role="status">{{ message }}</p>

    <div class="capstone__layout">
      <aside class="capstone__plans" aria-label="Saved capstone plans">
        <div class="capstone__plans-head">
          <h2>Saved plans</h2>
          <button type="button" class="btn btn--secondary btn--xs" @click="newPlan">New</button>
        </div>
        <p v-if="!plans.length" class="capstone__empty">No saved plans yet.</p>
        <ul v-else class="capstone__plan-list">
          <li v-for="row in plans" :key="row.id">
            <button
              type="button"
              class="capstone__plan"
              :class="{ 'capstone__plan--active': savedPlan && savedPlan.id === row.id }"
              :aria-current="savedPlan && savedPlan.id === row.id ? 'true' : undefined"
              @click="loadPlan(row.id)"
            >
              <span class="capstone__plan-top">
                <strong>{{ row.title }}</strong>
                <span class="capstone__status" :class="`capstone__status--${row.status}`">{{ row.status }}</span>
              </span>
              <span class="capstone__plan-meta">
                {{ row.profile_id }} · v{{ row.version }}
                <template v-if="row.approved_at"> · approved</template>
              </span>
            </button>
          </li>
        </ul>
      </aside>

      <section class="capstone__main" aria-labelledby="capstone-build-title">
        <h2 id="capstone-build-title" class="sr-only">Build a capstone</h2>

        <form class="capstone__form" @submit.prevent="generate">
          <label class="capstone__field">
            <span>Role profile</span>
            <select v-model="form.profile_id" class="form-input" required>
              <option disabled value="">Choose a profile</option>
              <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
                {{ profile.title }} ({{ profile.critical_competency_count }} critical)
              </option>
            </select>
          </label>
          <label class="capstone__field capstone__field--narrow">
            <span>Duration (hours)</span>
            <input v-model.number="form.duration_hours" class="form-input" type="number" min="4" max="200" step="1" />
          </label>
          <label class="capstone__field capstone__field--narrow">
            <span>Max labs</span>
            <input v-model.number="form.max_labs" class="form-input" type="number" min="1" max="20" step="1" />
          </label>
          <label class="capstone__check">
            <input v-model="form.assume_entry_level" type="checkbox" />
            <span>Assume entry level for missing prerequisites</span>
          </label>
          <button type="submit" class="btn btn--primary btn--sm" :disabled="generating || !form.profile_id">
            {{ generating ? 'Building...' : 'Generate proposal' }}
          </button>        </form>

        <p v-if="!plan" class="capstone__empty">
          Choose a profile and generate a proposal. The planner is deterministic;
          the same inputs and catalogue produce the same plan.
        </p>

        <template v-else>
          <section class="capstone__validation" aria-label="Validation gate">
            <div class="capstone__validation-head">
              <div>
                <p class="capstone__eyebrow">Validation gate</p>
                <h2>{{ plan.profile.title }} · {{ plan.profile.capstone.title }}</h2>
                <p class="capstone__muted">{{ plan.profile.capstone.description }}</p>
              </div>
              <span class="capstone__gate" :class="publishable ? 'capstone__gate--pass' : 'capstone__gate--fail'">
                {{ publishable ? 'Publishable' : 'Needs review' }}
              </span>
            </div>

            <dl class="capstone__metrics">
              <div>
                <dt>Coverage</dt>
                <dd>{{ formatPercent(validation.coverage_percent) }} of {{ formatPercent(validation.target_coverage_percent) }}</dd>
              </div>
              <div>
                <dt>Workload</dt>
                <dd>{{ formatHours(validation.workload_hours) }} of {{ formatHours(validation.target_hours) }}</dd>
              </div>
              <div>
                <dt>Assessment weights</dt>
                <dd>{{ formatPercent(validation.assessment_weights_total * 100) }}</dd>
              </div>
              <div>
                <dt>Prerequisites</dt>
                <dd>{{ validation.prerequisites_satisfied ? 'Satisfied' : 'Gaps' }}</dd>
              </div>
            </dl>

            <div v-if="gaps.length" class="capstone__gaps">
              <h3>Uncovered critical competencies</h3>
              <p class="capstone__muted">
                Coverage is below target. Waive a gap only with a written reason;
                the plan can then be approved with the waiver on record.
              </p>
              <ul class="capstone__gap-list">
                <li v-for="gap in gaps" :key="gap.competency_id">
                  <label class="capstone__check">
                    <input v-model="waivers[gap.competency_id]" type="checkbox" />
                    <span><strong>{{ gap.competency_id }}</strong> {{ gap.name }}</span>
                  </label>
                  <span v-if="gap.alternatives && gap.alternatives.length" class="capstone__muted">
                    Alternatives: {{ alternativeLabels(gap) }}
                  </span>
                </li>
              </ul>
              <label class="capstone__field">
                <span>Waiver reason</span>
                <textarea v-model="waiverReason" class="form-input" rows="2" placeholder="Why is this gap acceptable for this cohort?"></textarea>
              </label>
              <button type="button" class="btn btn--secondary btn--sm" :disabled="generating || !waivedCompetencies.length || !waiverReason.trim()" @click="generate(true)">
                Re-run validation with waivers
              </button>
            </div>

            <p v-if="validation.workload_note" class="capstone__muted">{{ validation.workload_note }}</p>
            <p v-if="validation.prerequisite_assumed" class="capstone__muted">
              Missing prerequisites are treated as an assumed entry level.
            </p>
          </section>

          <section class="capstone__block" aria-labelledby="capstone-objectives">
            <h3 id="capstone-objectives">Objectives</h3>
            <ol class="capstone__objectives">
              <li v-for="objective in plan.objectives" :key="objective.number">
                <p>{{ objective.statement }}</p>
                <p class="capstone__chips">
                  <span v-for="competency in objective.competencies" :key="competency.id" class="capstone__chip">
                    {{ competency.id }} {{ competency.name }}
                  </span>
                </p>
                <p class="capstone__muted">Evidence: {{ objective.evidence_types.join(', ') }}</p>
              </li>
            </ol>
          </section>

          <section class="capstone__block" aria-labelledby="capstone-labs">
            <h3 id="capstone-labs">Lab sequence</h3>
            <table class="capstone__table">
              <caption class="sr-only">Selected labs in delivery order</caption>
              <thead>
                <tr><th scope="col">#</th><th scope="col">Lab</th><th scope="col">Track</th><th scope="col">Level</th><th scope="col">Hours</th><th scope="col">Contract</th></tr>
              </thead>
              <tbody>
                <tr v-for="lab in plan.labs" :key="lab.slug">
                  <td>{{ lab.order }}</td>
                  <td>
                    <strong>{{ lab.title }}</strong>
                    <span class="capstone__muted">{{ lab.slug }}</span>
                  </td>
                  <td>{{ lab.track }}</td>
                  <td>{{ lab.difficulty }}</td>
                  <td>{{ formatHours(lab.hours) }}</td>
                  <td>{{ lab.reviewed ? 'Reviewed' : 'Baseline' }}</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section class="capstone__block" aria-labelledby="capstone-assessments">
            <h3 id="capstone-assessments">Assessments</h3>
            <table class="capstone__table">
              <caption class="sr-only">Assessment tasks, weights, rubrics, and evidence types</caption>
              <thead>
                <tr><th scope="col">Type</th><th scope="col">Task</th><th scope="col">Weight</th><th scope="col">Rubric</th><th scope="col">Evidence</th></tr>
              </thead>
              <tbody>
                <tr v-for="(assessment, index) in plan.assessments" :key="index">
                  <td>{{ assessment.type }}</td>
                  <td>
                    <strong>{{ assessment.title }}</strong>
                    <span class="capstone__muted">{{ assessment.description }}</span>
                  </td>
                  <td>{{ formatPercent(assessment.weight * 100) }}</td>
                  <td>{{ assessment.rubric }}</td>
                  <td>{{ assessment.evidence_type }}</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section class="capstone__block" aria-labelledby="capstone-deliverables">
            <h3 id="capstone-deliverables">Deliverables</h3>
            <table class="capstone__table">
              <caption class="sr-only">Deliverables, evidence types, and reviewers</caption>
              <thead>
                <tr><th scope="col">#</th><th scope="col">Deliverable</th><th scope="col">Evidence</th><th scope="col">Reviewer</th></tr>
              </thead>
              <tbody>
                <tr v-for="item in plan.deliverables" :key="item.number">
                  <td>{{ item.number }}</td>
                  <td><strong>{{ item.title }}</strong><span class="capstone__muted">{{ item.description }}</span></td>
                  <td>{{ item.evidence_type }}</td>
                  <td>{{ item.reviewer }}</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section class="capstone__block" aria-labelledby="capstone-evidence">
            <h3 id="capstone-evidence">Evidence map</h3>
            <ul class="capstone__evidence">
              <li v-for="row in plan.evidence_map" :key="row.competency_id">
                <strong>{{ row.competency_id }}</strong> {{ row.name }}
                <span class="capstone__muted">via {{ row.labs.join(', ') }}</span>
              </li>
            </ul>
          </section>

          <section class="capstone__actions" aria-label="Save, approve, or archive the plan">
            <label class="capstone__field">
              <span>Plan title</span>
              <input v-model="title" class="form-input" type="text" maxlength="200" />
            </label>
            <label class="capstone__field">
              <span>Notes</span>
              <textarea v-model="notes" class="form-input" rows="2" maxlength="4000" placeholder="Cohort, local adaptations, or reviewer notes"></textarea>
            </label>
            <div class="capstone__buttons">
              <button v-if="!savedPlan" type="button" class="btn btn--primary btn--sm" :disabled="saving" @click="saveDraft">
                {{ saving ? 'Saving...' : 'Save draft' }}
              </button>
              <button v-else type="button" class="btn btn--primary btn--sm" :disabled="saving" @click="updateDraft">
                {{ saving ? 'Saving...' : 'Save new version' }}
              </button>
              <button v-if="savedPlan && savedPlan.status === 'draft'" type="button" class="btn btn--primary btn--sm" :disabled="!publishable || approving" @click="approve">
                {{ approving ? 'Approving...' : 'Approve plan' }}
              </button>
              <button v-if="savedPlan && savedPlan.status !== 'archived'" type="button" class="btn btn--secondary btn--sm" :disabled="archiving" @click="archive">
                Archive
              </button>
            </div>
            <p v-if="savedPlan" class="capstone__muted">
              Saved as {{ savedPlan.title }} · v{{ savedPlan.version }} · {{ savedPlan.status }}
            </p>
          </section>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const profiles = ref([])
const plans = ref([])
const plan = ref(null)
const savedPlan = ref(null)
const loadingPlans = ref(false)
const generating = ref(false)
const saving = ref(false)
const approving = ref(false)
const archiving = ref(false)
const error = ref('')
const message = ref('')

const form = reactive({
  profile_id: '',
  duration_hours: 40,
  max_labs: 10,
  assume_entry_level: true,
})
const waivers = reactive({})
const waiverReason = ref('')
const title = ref('')
const notes = ref('')

const validation = computed(() => plan.value?.validation || {})
const gaps = computed(() => validation.value.gaps || [])
const publishable = computed(() => Boolean(validation.value.publishable))
const waivedCompetencies = computed(() => Object.keys(waivers).filter((key) => waivers[key]))

function apiError(err) {
  return err?.response?.data?.detail || err?.message || 'Request failed'
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`
}

function formatHours(value) {
  const hours = Number(value || 0)
  return `${hours.toFixed(1)}h`
}

function resetWaivers() {
  for (const key of Object.keys(waivers)) delete waivers[key]
  waiverReason.value = ''
}

function applyPlan(payload) {
  plan.value = payload
  resetWaivers()
  for (const gap of payload.validation?.gaps || []) waivers[gap.competency_id] = false
  waiverReason.value = payload.validation?.waiver_reason || ''
  if (!title.value) {
    title.value = payload.profile?.capstone?.title || `${payload.profile?.title || 'Capstone'} capstone`
  }
}

async function loadProfiles() {
  try {
    const { data } = await axios.get('/capstones/profiles')
    profiles.value = data.profiles || []
    if (!form.profile_id && profiles.value.length) form.profile_id = profiles.value[0].id
  } catch (err) {
    error.value = apiError(err)
  }
}

async function loadPlans() {
  loadingPlans.value = true
  try {
    const { data } = await axios.get('/capstones/plans')
    plans.value = data.plans || []
  } catch (err) {
    error.value = apiError(err)
  } finally {
    loadingPlans.value = false
  }
}

async function generate(keepSaved = false) {
  if (keepSaved instanceof Event) keepSaved = false
  error.value = ''
  message.value = ''
  generating.value = true
  try {
    const { data } = await axios.post('/capstones/plan', {
      profile_id: form.profile_id,
      duration_hours: form.duration_hours,
      max_labs: form.max_labs,
      waived_competencies: waivedCompetencies.value,
      waiver_reason: waiverReason.value.trim() || null,
      assume_entry_level: form.assume_entry_level,
    })
    if (!keepSaved) {
      savedPlan.value = null
      title.value = ''
      notes.value = ''
    }
    applyPlan(data)
    message.value = 'Proposal generated. Review the gate before saving or approving.'
  } catch (err) {
    error.value = apiError(err)
  } finally {
    generating.value = false
  }
}

function alternativeLabels(gap) {
  return (gap.alternatives || [])
    .map((item) => (typeof item === 'string' ? item : item.title || item.slug || ''))
    .filter(Boolean)
    .join(', ')
}

function planPayload() {
  return {
    profile_id: form.profile_id,
    duration_hours: form.duration_hours,
    max_labs: form.max_labs,
    waived_competencies: waivedCompetencies.value,
    waiver_reason: waiverReason.value.trim() || null,
    assume_entry_level: form.assume_entry_level,
    title: title.value.trim() || null,
    notes: notes.value.trim() || null,
  }
}

async function saveDraft() {
  error.value = ''
  message.value = ''
  saving.value = true
  try {
    const { data } = await axios.post('/capstones/plans', planPayload())
    savedPlan.value = data
    applyPlan(data.plan)
    title.value = data.title
    notes.value = data.notes || ''
    await loadPlans()
    message.value = `Draft saved as ${data.title} (v${data.version}).`
  } catch (err) {
    error.value = apiError(err)
  } finally {
    saving.value = false
  }
}

async function updateDraft() {
  if (!savedPlan.value) return
  error.value = ''
  message.value = ''
  saving.value = true
  try {
    const { data } = await axios.put(`/capstones/plans/${savedPlan.value.id}`, planPayload())
    savedPlan.value = data
    applyPlan(data.plan)
    title.value = data.title
    notes.value = data.notes || ''
    await loadPlans()
    message.value = `Saved version ${data.version}; approval cleared.`
  } catch (err) {
    error.value = apiError(err)
  } finally {
    saving.value = false
  }
}

async function approve() {
  if (!savedPlan.value) return
  error.value = ''
  message.value = ''
  approving.value = true
  try {
    const { data } = await axios.post(`/capstones/plans/${savedPlan.value.id}/approve`)
    savedPlan.value = data
    await loadPlans()
    message.value = 'Plan approved. Publication to a course is still a later step.'
  } catch (err) {
    error.value = apiError(err)
  } finally {
    approving.value = false
  }
}

async function archive() {
  if (!savedPlan.value) return
  error.value = ''
  message.value = ''
  archiving.value = true
  try {
    const { data } = await axios.post(`/capstones/plans/${savedPlan.value.id}/archive`)
    savedPlan.value = data
    await loadPlans()
    message.value = 'Plan archived.'
  } catch (err) {
    error.value = apiError(err)
  } finally {
    archiving.value = false
  }
}

async function loadPlan(id) {
  error.value = ''
  message.value = ''
  try {
    const { data } = await axios.get(`/capstones/plans/${id}`)
    savedPlan.value = data
    form.profile_id = data.request?.profile_id || data.profile_id || form.profile_id
    form.duration_hours = data.request?.duration_hours ?? form.duration_hours
    form.max_labs = data.request?.max_labs ?? form.max_labs
    form.assume_entry_level = data.request?.assume_entry_level ?? true
    title.value = data.title
    notes.value = data.notes || ''
    applyPlan(data.plan)
    waiverReason.value = data.request?.waiver_reason || ''
    for (const key of data.request?.waived_competencies || []) waivers[key] = true
  } catch (err) {
    error.value = apiError(err)
  }
}

function newPlan() {
  savedPlan.value = null
  plan.value = null
  title.value = ''
  notes.value = ''
  resetWaivers()
  message.value = 'Choose a profile and generate a proposal.'
}

onMounted(async () => {
  await Promise.all([loadProfiles(), loadPlans()])
})
</script>

<style scoped>
.capstone {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.5rem;
}
.capstone__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.capstone__head h1 {
  margin: 0.15rem 0 0.35rem;
}
.capstone__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted, #64748b);
}
.capstone__intro {
  max-width: 60ch;
  margin: 0;
  color: var(--text-muted, #475569);
}
.capstone__message {
  margin: 0;
  color: var(--success, #15803d);
}
.capstone__layout {
  display: grid;
  grid-template-columns: minmax(14rem, 18rem) minmax(0, 1fr);
  gap: 1.25rem;
  align-items: start;
}
.capstone__plans,
.capstone__validation,
.capstone__block,
.capstone__actions,
.capstone__form {
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 0.75rem;
  background: var(--surface, #fff);
  padding: 1rem;
}
.capstone__plans-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.capstone__plans-head h2 {
  margin: 0;
  font-size: 1rem;
}
.capstone__plan-list {
  list-style: none;
  margin: 0.75rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.capstone__plan {
  width: 100%;
  text-align: left;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  background: var(--surface-alt, #f8fafc);
  padding: 0.5rem 0.6rem;
  cursor: pointer;
}
.capstone__plan--active {
  border-color: var(--accent, #2563eb);
}
.capstone__plan-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.capstone__plan-meta {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.8rem;
  color: var(--text-muted, #64748b);
}
.capstone__status {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #64748b);
}
.capstone__status--approved {
  color: var(--success, #15803d);
}
.capstone__form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-end;
}
.capstone__field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1 1 14rem;
}
.capstone__field--narrow {
  flex: 0 1 8rem;
}
.capstone__field span {
  font-size: 0.8rem;
  color: var(--text-muted, #475569);
}
.capstone__check {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  flex: 1 1 100%;
}
.capstone__main {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}
.capstone__validation-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}
.capstone__validation-head h2 {
  margin: 0.15rem 0 0.25rem;
  font-size: 1.1rem;
}
.capstone__gate {
  border-radius: 999px;
  padding: 0.2rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}
.capstone__gate--pass {
  background: #dcfce7;
  color: #166534;
}
.capstone__gate--fail {
  background: #fef3c7;
  color: #92400e;
}
.capstone__metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
  gap: 0.75rem;
  margin: 1rem 0;
}
.capstone__metrics dt {
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
}
.capstone__metrics dd {
  margin: 0.15rem 0 0;
  font-weight: 600;
}
.capstone__gaps {
  border-top: 1px solid var(--border, #e2e8f0);
  padding-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.capstone__gaps h3 {
  margin: 0;
  font-size: 0.95rem;
}
.capstone__gap-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-height: 16rem;
  overflow: auto;
}
.capstone__muted {
  color: var(--text-muted, #64748b);
  font-size: 0.85rem;
}
.capstone__block h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
}
.capstone__objectives {
  margin: 0;
  padding-left: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.capstone__objectives p {
  margin: 0.15rem 0;
}
.capstone__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}
.capstone__chip {
  background: var(--surface-alt, #f1f5f9);
  border-radius: 999px;
  padding: 0.1rem 0.5rem;
  font-size: 0.75rem;
}
.capstone__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}
.capstone__table th,
.capstone__table td {
  text-align: left;
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid var(--border, #e2e8f0);
  vertical-align: top;
}
.capstone__table th {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted, #64748b);
}
.capstone__table td .capstone__muted {
  display: block;
}
.capstone__evidence {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-height: 18rem;
  overflow: auto;
}
.capstone__actions {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.capstone__buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.capstone__empty {
  color: var(--text-muted, #64748b);
}
@media (max-width: 900px) {
  .capstone__layout {
    grid-template-columns: 1fr;
  }
}
</style>
