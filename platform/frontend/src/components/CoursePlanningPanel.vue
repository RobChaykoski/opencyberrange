<template>
  <section class="planning">
    <div class="section-header">
      <div>
        <h3 class="section-title">Exercise plan</h3>
        <p class="section-desc">
          Group learners into cohorts, define exercise sets, and attach a completion
          requirement to each cohort. Coverage is calculated from completions; this
          view is course-scoped and does not affect platform-wide exercise access.
        </p>
      </div>
      <button class="btn btn--outline btn--sm" :disabled="loading" @click="load">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="message" class="success-message">{{ message }}</p>

    <!-- Cohorts -->
    <div class="planning-block">
      <h4>Cohorts</h4>
      <form class="planning-form" @submit.prevent="createCohort">
        <input v-model="cohortForm.name" class="form-input form-input--sm" placeholder="Cohort name (e.g. Grade 9)" required>
        <input v-model="cohortForm.description" class="form-input form-input--sm" placeholder="Description (optional)">
        <button class="btn btn--primary btn--sm" :disabled="saving">Add cohort</button>
      </form>

      <div v-if="!planning?.cohorts?.length" class="empty-state">No cohorts yet.</div>
      <article v-for="cohort in planning?.cohorts" :key="cohort.id" class="planning-card">
        <div class="planning-card__head">
          <div>
            <strong>{{ cohort.name }}</strong>
            <span class="cell-muted"> · {{ cohort.members.length }} member(s)</span>
            <p v-if="cohort.description" class="cell-muted">{{ cohort.description }}</p>
          </div>
          <button class="btn btn--danger btn--xs" @click="deleteCohort(cohort)">Delete</button>
        </div>
        <details>
          <summary>Members</summary>
          <div class="planning-members">
            <label v-for="student in students" :key="student.id" class="planning-member">
              <input
                type="checkbox"
                :value="student.id"
                v-model="memberSelections[cohort.id]"
              >
              <PrivacyText :value="student.username" fallback="Deleted learner" />
            </label>
          </div>
          <button class="btn btn--secondary btn--xs" @click="saveMembers(cohort)">Save members</button>
        </details>
      </article>
    </div>

    <!-- Exercise sets -->
    <div class="planning-block">
      <h4>Exercise sets</h4>
      <form class="planning-form" @submit.prevent="createSet">
        <input v-model="setForm.name" class="form-input form-input--sm" placeholder="Set name (e.g. Core skills)" required>
        <input v-model="setForm.description" class="form-input form-input--sm" placeholder="Description (optional)">
        <button class="btn btn--primary btn--sm" :disabled="saving">Add set</button>
      </form>

      <div v-if="!planning?.exercise_sets?.length" class="empty-state">No exercise sets yet.</div>
      <article v-for="set in planning?.exercise_sets" :key="set.id" class="planning-card">
        <div class="planning-card__head">
          <div>
            <strong>{{ set.name }}</strong>
            <span class="cell-muted"> · {{ set.items.length }} exercise(s)</span>
          </div>
          <button class="btn btn--danger btn--xs" @click="deleteSet(set)">Delete</button>
        </div>
        <ul class="planning-items">
          <li v-for="item in set.items" :key="item.lab_id">
            {{ item.lab_name }}
            <span v-if="!item.required" class="cell-muted">(optional)</span>
            <button class="btn btn--outline btn--xs" @click="removeSetItem(set, item)">Remove</button>
          </li>
        </ul>
        <div class="planning-form">
          <select v-model.number="setAddLab[set.id]" class="form-input form-input--sm">
            <option :value="null">Add an exercise…</option>
            <option v-for="lab in labsNotInSet(set)" :key="lab.id" :value="lab.id">{{ lab.name }}</option>
          </select>
          <button class="btn btn--secondary btn--xs" :disabled="!setAddLab[set.id]" @click="addSetItem(set)">Add</button>
        </div>
      </article>
    </div>

    <!-- Requirements -->
    <div class="planning-block">
      <h4>Requirements and coverage</h4>
      <form class="planning-form planning-form--wrap" @submit.prevent="createRequirement">
        <select v-model.number="requirementForm.cohort_id" class="form-input form-input--sm" required>
          <option :value="null">Cohort…</option>
          <option v-for="cohort in planning?.cohorts" :key="cohort.id" :value="cohort.id">{{ cohort.name }}</option>
        </select>
        <select v-model.number="requirementForm.set_id" class="form-input form-input--sm" required>
          <option :value="null">Exercise set…</option>
          <option v-for="set in planning?.exercise_sets" :key="set.id" :value="set.id">{{ set.name }}</option>
        </select>
        <select v-model="requirementForm.rule_type" class="form-input form-input--sm">
          <option value="complete_all">Complete all</option>
          <option value="complete_percent">Complete percent</option>
          <option value="complete_count">Complete count</option>
        </select>
        <input
          v-if="requirementForm.rule_type !== 'complete_all'"
          v-model.number="requirementForm.threshold"
          type="number"
          min="1"
          class="form-input form-input--sm"
          :placeholder="requirementForm.rule_type === 'complete_percent' ? 'Percent' : 'Count'"
        >
        <input v-model="requirementForm.due_at" type="date" class="form-input form-input--sm">
        <input v-model="requirementForm.note" class="form-input form-input--sm" placeholder="Note (optional)">
        <button class="btn btn--primary btn--sm" :disabled="saving">Add requirement</button>
      </form>

      <div v-if="!planning?.coverage?.length" class="empty-state">No requirements yet.</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Cohort</th>
              <th>Exercise set</th>
              <th>Rule</th>
              <th>Due</th>
              <th>Learners</th>
              <th>Met</th>
              <th>Missing</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="row in planning.coverage" :key="row.id">
              <tr>
                <td class="cell-primary">{{ row.cohort_name }}</td>
                <td>{{ row.set_name }}</td>
                <td>{{ ruleLabel(row) }}</td>
                <td>{{ row.due_at ? row.due_at.slice(0, 10) : '—' }}</td>
                <td>{{ row.learners }}</td>
                <td>{{ row.met }}</td>
                <td>{{ row.missing }}</td>
                <td>
                  <span :class="['overview-pill', row.overdue ? 'overview-pill--bad' : row.missing ? 'overview-pill--warn' : 'overview-pill--good']">
                    {{ row.overdue ? 'Overdue' : row.missing ? 'In progress' : 'Met' }}
                  </span>
                </td>
                <td class="cell-actions">
                  <button class="btn btn--outline btn--xs" @click="toggleCoverage(row.id)">
                    {{ expandedCoverage === row.id ? 'Hide' : 'Learners' }}
                  </button>
                  <button class="btn btn--danger btn--xs" @click="deleteRequirement(row.id)">Delete</button>
                </td>
              </tr>
              <tr v-if="expandedCoverage === row.id">
                <td colspan="9">
                  <div class="planning-students">
                    <span
                      v-for="student in row.students"
                      :key="student.id"
                      :class="['planning-student', student.met ? 'planning-student--met' : 'planning-student--missing']"
                    >
                      <PrivacyText :value="student.username" fallback="Deleted learner" />
                      {{ student.completed }}/{{ student.required }}
                    </span>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import axios from '../api/axios'
import PrivacyText from './PrivacyText.vue'

const props = defineProps({
  courseId: { type: Number, required: true },
  students: { type: Array, default: () => [] },
  labs: { type: Array, default: () => [] },
})

const planning = ref(null)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const message = ref('')
const expandedCoverage = ref(null)
const memberSelections = reactive({})
const setAddLab = reactive({})
const cohortForm = reactive({ name: '', description: '' })
const setForm = reactive({ name: '', description: '' })
const requirementForm = reactive({
  cohort_id: null,
  set_id: null,
  rule_type: 'complete_all',
  threshold: null,
  due_at: '',
  note: '',
})

const load = async () => {
  if (!props.courseId) return
  loading.value = true
  error.value = ''
  try {
    const { data } = await axios.get(`/courses/${props.courseId}/planning`)
    planning.value = data
    for (const cohort of data.cohorts || []) {
      memberSelections[cohort.id] = cohort.members.map((member) => member.id)
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load the exercise plan.'
  } finally {
    loading.value = false
  }
}

const run = async (action, success) => {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await action()
    message.value = success
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'The change could not be saved.'
  } finally {
    saving.value = false
  }
}

const createCohort = () =>
  run(async () => {
    await axios.post(`/courses/${props.courseId}/cohorts`, {
      name: cohortForm.name,
      description: cohortForm.description || null,
    })
    cohortForm.name = ''
    cohortForm.description = ''
  }, 'Cohort created.')

const deleteCohort = (cohort) => {
  if (!window.confirm(`Delete cohort “${cohort.name}” and its requirements?`)) return
  run(
    () => axios.delete(`/courses/${props.courseId}/cohorts/${cohort.id}`),
    'Cohort deleted.'
  )
}

const saveMembers = (cohort) =>
  run(
    () =>
      axios.put(`/courses/${props.courseId}/cohorts/${cohort.id}/members`, {
        user_ids: memberSelections[cohort.id] || [],
      }),
    'Cohort members saved.'
  )

const createSet = () =>
  run(async () => {
    await axios.post(`/courses/${props.courseId}/exercise-sets`, {
      name: setForm.name,
      description: setForm.description || null,
    })
    setForm.name = ''
    setForm.description = ''
  }, 'Exercise set created.')

const deleteSet = (set) => {
  if (!window.confirm(`Delete exercise set “${set.name}”?`)) return
  run(
    () => axios.delete(`/courses/${props.courseId}/exercise-sets/${set.id}`),
    'Exercise set deleted.'
  )
}

const labsNotInSet = (set) => {
  const used = new Set(set.items.map((item) => item.lab_id))
  return props.labs.filter((lab) => !used.has(lab.id))
}

const saveSetItems = (set, items) =>
  run(
    () =>
      axios.put(`/courses/${props.courseId}/exercise-sets/${set.id}/items`, {
        items: items.map((item, index) => ({
          lab_id: item.lab_id,
          required: item.required !== false,
          sort_order: index,
        })),
      }),
    'Exercise set saved.'
  )

const addSetItem = (set) => {
  const labId = setAddLab[set.id]
  if (!labId) return
  const items = [...set.items, { lab_id: labId, required: true }]
  setAddLab[set.id] = null
  saveSetItems(set, items)
}

const removeSetItem = (set, item) => {
  saveSetItems(set, set.items.filter((row) => row.lab_id !== item.lab_id))
}

const createRequirement = () =>
  run(async () => {
    await axios.post(`/courses/${props.courseId}/requirements`, {
      cohort_id: requirementForm.cohort_id,
      set_id: requirementForm.set_id,
      rule_type: requirementForm.rule_type,
      threshold: requirementForm.threshold,
      due_at: requirementForm.due_at ? `${requirementForm.due_at}T23:59:59` : null,
      note: requirementForm.note || null,
    })
    requirementForm.note = ''
  }, 'Requirement created.')

const deleteRequirement = (id) => {
  if (!window.confirm('Delete this requirement?')) return
  run(
    () => axios.delete(`/courses/${props.courseId}/requirements/${id}`),
    'Requirement deleted.'
  )
}

const ruleLabel = (row) => {
  if (row.rule_type === 'complete_all') return `All ${row.total_items}`
  if (row.rule_type === 'complete_percent') return `${row.threshold}%`
  return `${row.threshold} exercise(s)`
}

const toggleCoverage = (id) => {
  expandedCoverage.value = expandedCoverage.value === id ? null : id
}

watch(() => props.courseId, load)
onMounted(load)
</script>

<style scoped>
.planning { display: flex; flex-direction: column; gap: 1rem; }
.planning-block { border-top: 1px solid var(--border-color); padding-top: 1rem; }
.planning-block h4 { margin: 0 0 0.6rem; font-size: 0.95rem; }
.planning-form { display: flex; gap: 0.5rem; align-items: center; margin: 0.5rem 0; }
.planning-form--wrap { flex-wrap: wrap; }
.planning-card {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem;
  margin: 0.6rem 0;
  background: var(--bg-secondary);
}
.planning-card__head { display: flex; justify-content: space-between; gap: 1rem; }
.planning-card__head p { margin: 0.2rem 0 0; }
.planning-items { list-style: none; margin: 0.5rem 0; padding: 0; display: flex; flex-direction: column; gap: 0.25rem; }
.planning-members { display: flex; flex-wrap: wrap; gap: 0.75rem; margin: 0.5rem 0; max-height: 14rem; overflow: auto; }
.planning-member { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.82rem; }
.planning-students { display: flex; flex-wrap: wrap; gap: 0.4rem; padding: 0.4rem 0; }
.planning-student {
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  font-size: 0.75rem;
}
.planning-student--met { color: var(--success); border-color: var(--success); }
.planning-student--missing { color: var(--text-muted); }
</style>
