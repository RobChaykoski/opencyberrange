<template>
  <section class="readiness-panel">
    <div class="readiness-panel__head">
      <div>
        <p class="readiness-panel__eyebrow">Pilot instructor support</p>
        <h2 class="readiness-panel__title">Readiness and lab health</h2>
        <p class="readiness-panel__lead">
          A support prompt, not a grade. Every score is provisional until the
          rubric is calibrated. Platform-wide failures are excluded from learner
          risk and shown in lab health instead.
        </p>
      </div>
      <div class="readiness-panel__controls">
        <label class="readiness-panel__course">
          <span>Course</span>
          <select
            :value="courseId ?? ''"
            class="form-input form-input--sm"
            @change="selectCourse($event.target.value)"
          >
            <option value="">Select a course</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.code }} — {{ course.name }}
            </option>
          </select>
        </label>
        <button
          v-if="courseId"
          type="button"
          class="btn btn--secondary btn--sm"
          :disabled="loading"
          @click="fetchReadiness"
        >
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="!courseId" class="readiness-panel__empty">
      Select a course to see the support queue and lab health.
    </div>

    <div v-else-if="loading && !data" class="readiness-panel__empty" role="status">
      Loading readiness evidence...
    </div>

    <div v-else-if="error" class="readiness-panel__empty readiness-panel__empty--error" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary btn--sm" @click="fetchReadiness">
        Try again
      </button>
    </div>

    <template v-else-if="data">
      <div class="readiness-panel__tabs" role="tablist" aria-label="Readiness views">
        <button
          id="readiness-tab-queue"
          type="button"
          role="tab"
          class="readiness-panel__tab"
          :class="{ 'readiness-panel__tab--active': activeView === 'queue' }"
          :aria-selected="activeView === 'queue'"
          aria-controls="readiness-panel-queue"
          @click="activeView = 'queue'"
        >
          Support queue
          <span>{{ data.cohort.students }}</span>
        </button>
        <button
          id="readiness-tab-followups"
          type="button"
          role="tab"
          class="readiness-panel__tab"
          :class="{ 'readiness-panel__tab--active': activeView === 'followups' }"
          :aria-selected="activeView === 'followups'"
          aria-controls="readiness-panel-followups"
          @click="activeView = 'followups'"
        >
          Follow-ups
          <span>{{ data.case_summary?.open || 0 }} open</span>
        </button>
        <button
          id="readiness-tab-labs"
          type="button"
          role="tab"
          class="readiness-panel__tab"
          :class="{ 'readiness-panel__tab--active': activeView === 'labs' }"
          :aria-selected="activeView === 'labs'"
          aria-controls="readiness-panel-labs"
          @click="activeView = 'labs'"
        >
          Lab health
          <span>{{ data.lab_health.counts.degraded || 0 }} degraded</span>
        </button>
        <button
          id="readiness-tab-calibration"
          type="button"
          role="tab"
          class="readiness-panel__tab"
          :class="{ 'readiness-panel__tab--active': activeView === 'calibration' }"
          :aria-selected="activeView === 'calibration'"
          aria-controls="readiness-panel-calibration"
          @click="openCalibration"
        >
          Calibration
        </button>
      </div>

      <div
        v-if="activeView === 'queue'"
        id="readiness-panel-queue"
        role="tabpanel"
        aria-labelledby="readiness-tab-queue"
        class="readiness-panel__view"
      >
        <div class="readiness-panel__bands">
          <span
            v-for="band in bandSummary"
            :key="band.key"
            class="readiness-band"
            :class="`readiness-band--${band.key}`"
          >
            <strong>{{ band.count }}</strong>
            {{ band.label }}
          </span>
        </div>

        <p class="readiness-panel__meta">
          {{ data.cohort.students }} learners · {{ data.cohort.assigned_exercises }} assigned exercises ·
          median {{ data.cohort.median_completed }} completed ·
          formula {{ data.formula_version }}
        </p>

        <div v-if="!data.students.length" class="readiness-panel__empty">
          No learners with enough evidence yet.
        </div>

        <div v-else class="readiness-list">
          <article
            v-for="student in visibleStudents"
            :key="student.user_id"
            class="readiness-card"
            :class="`readiness-card--${student.band}`"
          >
            <button
              type="button"
              class="readiness-card__summary"
              :aria-expanded="expandedStudent === student.user_id"
              @click="toggleStudent(student)"
            >
              <span class="readiness-card__identity">
                <strong>{{ student.display_name }}</strong>
                <small>{{ student.username }}</small>
              </span>
              <span class="readiness-card__score">
                <strong>{{ student.cwrs }}</strong>
                <small>{{ student.band_label }}</small>
              </span>
              <span class="readiness-card__confidence">{{ student.confidence }}</span>
              <span class="readiness-card__flags">
                <span v-for="flag in student.flags.slice(0, 2)" :key="flag" class="readiness-flag">
                  {{ flagLabel(flag) }}
                </span>
              </span>
              <span class="readiness-card__caret" aria-hidden="true">
                {{ expandedStudent === student.user_id ? '−' : '+' }}
              </span>
            </button>

            <div v-if="expandedStudent === student.user_id" class="readiness-card__detail">
              <div class="readiness-card__components">
                <div v-for="(value, key) in student.components" :key="key" class="readiness-component">
                  <div class="readiness-component__head">
                    <span>{{ componentLabel(key) }}</span>
                    <strong>{{ value == null ? 'Not measured' : value }}</strong>
                  </div>
                  <div
                    class="readiness-component__bar"
                    role="progressbar"
                    :aria-valuenow="value ?? 0"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    :aria-label="`${componentLabel(key)} risk`"
                  >
                    <span
                      :style="{ width: `${value ?? 0}%` }"
                      :class="{ 'is-missing': value == null }"
                    ></span>
                  </div>
                </div>
              </div>

              <div class="readiness-card__facts">
                <span><strong>{{ student.completed_exercises }}</strong> of {{ student.assigned_exercises }} completed</span>
                <span><strong>{{ student.days_since_activity ?? '—' }}</strong> days since activity</span>
                <span v-if="student.provisional" class="readiness-panel__provisional">Provisional evidence</span>
              </div>

              <div class="readiness-case">
                <div class="readiness-workflow__head">
                  <h3>Case ownership</h3>
                  <span>{{ student.case?.is_open ? 'Open case' : 'No open case' }}</span>
                </div>
                <div class="readiness-workflow__row">
                  <select v-model="caseForm.owner_id" class="form-input form-input--sm">
                    <option value="">Unassigned</option>
                    <option :value="String(currentUserId)">Me</option>
                    <option
                      v-if="student.case?.owner_id && student.case.owner_id !== currentUserId"
                      :value="String(student.case.owner_id)"
                    >
                      {{ student.case.owner_name || 'Current owner' }}
                    </option>
                  </select>
                  <select v-model="caseForm.priority" class="form-input form-input--sm">
                    <option value="low">Low priority</option>
                    <option value="normal">Normal priority</option>
                    <option value="high">High priority</option>
                  </select>
                  <input
                    v-model="caseForm.follow_up_date"
                    class="form-input form-input--sm"
                    type="date"
                    aria-label="Next follow-up date"
                  />
                  <input
                    v-model="caseForm.note"
                    class="form-input form-input--sm readiness-workflow__note"
                    type="text"
                    placeholder="Case note (optional)"
                    maxlength="2000"
                  />
                  <button
                    type="button"
                    class="btn btn--secondary btn--sm"
                    :disabled="caseSaving"
                    @click="saveCase(student, 'open')"
                  >
                    {{ caseSaving ? 'Saving...' : 'Assign' }}
                  </button>
                  <button
                    v-if="student.case?.is_open"
                    type="button"
                    class="btn btn--secondary btn--sm"
                    :disabled="caseSaving"
                    @click="saveCase(student, 'closed')"
                  >
                    Close case
                  </button>
                </div>
                <p v-if="caseError" class="readiness-panel__provisional" role="alert">{{ caseError }}</p>
                <div v-if="student.case" class="readiness-workflow__existing">
                  <span>{{ student.case.owner_name || 'Unassigned' }}</span>
                  <span>{{ priorityLabel(student.case.priority) }}</span>
                  <span v-if="student.case.follow_up_at">Check-in {{ formatDate(student.case.follow_up_at) }}</span>
                  <span v-if="student.case.overdue" class="follow-up-state follow-up-state--overdue">Overdue</span>
                  <span v-else-if="student.case.due_soon" class="follow-up-state follow-up-state--due">Due soon</span>
                  <span v-if="student.case.note">· {{ student.case.note }}</span>
                </div>
              </div>

              <div class="readiness-workflow">
                <div class="readiness-workflow__head">
                  <h3>Support record</h3>
                  <span>Append-only, instructor-visible</span>
                </div>
                <div class="readiness-workflow__row">
                  <select v-model="workflow.kind" class="form-input form-input--sm" @change="onWorkflowKind">
                    <option value="context">Context flag</option>
                    <option value="action">Support action</option>
                    <option value="flag_state">Flag state</option>
                  </select>
                  <select v-model="workflow.key" class="form-input form-input--sm">
                    <option v-for="option in workflowOptions" :key="option.value" :value="option.value">
                      {{ option.label }}
                    </option>
                  </select>
                  <select
                    v-if="workflow.kind === 'flag_state'"
                    v-model="workflow.state"
                    class="form-input form-input--sm"
                  >
                    <option value="acknowledged">Acknowledged</option>
                    <option value="snoozed">Snoozed 7 days</option>
                    <option value="dismissed">Dismissed</option>
                  </select>
                  <input
                    v-model="workflow.note"
                    class="form-input form-input--sm readiness-workflow__note"
                    type="text"
                    placeholder="Note (optional)"
                    maxlength="2000"
                  />
                  <button
                    type="button"
                    class="btn btn--secondary btn--sm"
                    :disabled="workflowSaving || !workflow.key"
                    @click="saveWorkflow(student)"
                  >
                    {{ workflowSaving ? 'Saving...' : 'Save' }}
                  </button>
                </div>
                <p v-if="workflowError" class="readiness-panel__provisional" role="alert">{{ workflowError }}</p>
                <div v-if="student.context_flags?.length" class="readiness-workflow__existing">
                  <strong>Context:</strong>
                  <span v-for="flag in student.context_flags" :key="flag.id">
                    {{ contextLabel(flag.key) }}<template v-if="flag.end_at"> until {{ formatDate(flag.end_at) }}</template>
                  </span>
                </div>
                <div v-if="student.last_action" class="readiness-workflow__existing">
                  <strong>Last action:</strong>
                  <span>
                    {{ actionLabel(student.last_action.key) }}
                    <template v-if="student.last_action.outcome"> · {{ student.last_action.outcome }}</template>
                  </span>
                </div>
              </div>

              <div class="readiness-card__capabilities">
                <div class="readiness-card__capabilities-head">
                  <h3>Capability detail</h3>
                  <button
                    type="button"
                    class="btn btn--secondary btn--sm"
                    :disabled="capabilitiesLoading === student.user_id"
                    @click="loadCapabilities(student.user_id)"
                  >
                    {{ capabilitiesLoading === student.user_id ? 'Loading...' : 'Load capabilities' }}
                  </button>
                </div>
                <div v-if="capabilitiesError" class="readiness-panel__empty readiness-panel__empty--error" role="alert">
                  {{ capabilitiesError }}
                </div>
                <div v-else-if="capabilitiesFor === student.user_id && capabilities" class="capability-list">
                  <div v-for="axis in capabilities.axes" :key="axis.key" class="capability-row">
                    <span>{{ axis.label }}</span>
                    <div
                      class="capability-row__bar"
                      role="progressbar"
                      :aria-valuenow="axis.score ?? 0"
                      aria-valuemin="0"
                      aria-valuemax="100"
                      :aria-label="`${axis.label} capability`"
                    >
                      <span :style="{ width: `${axis.score ?? 0}%` }"></span>
                    </div>
                    <strong>{{ axis.score == null ? 'No evidence' : axis.score }}</strong>
                  </div>
                  <p class="readiness-panel__meta">{{ capabilities.disclaimer }}</p>
                </div>
              </div>
            </div>
          </article>

          <button
            v-if="data.students.length > defaultVisible"
            type="button"
            class="btn btn--secondary btn--sm readiness-panel__more"
            @click="showAllStudents = !showAllStudents"
          >
            {{ showAllStudents ? 'Show top 5' : `Show all ${data.students.length} learners` }}
          </button>
        </div>
      </div>

      <div
        v-else-if="activeView === 'followups'"
        id="readiness-panel-followups"
        role="tabpanel"
        aria-labelledby="readiness-tab-followups"
        class="readiness-panel__view"
      >
        <div class="readiness-panel__bands">
          <span class="readiness-band readiness-band--critical_intervention">
            <strong>{{ data.case_summary?.overdue || 0 }}</strong> overdue
          </span>
          <span class="readiness-band readiness-band--high_risk">
            <strong>{{ data.case_summary?.due_soon || 0 }}</strong> due in 7 days
          </span>
          <span class="readiness-band readiness-band--monitor">
            <strong>{{ data.case_summary?.unassigned || 0 }}</strong> unassigned
          </span>
          <span class="readiness-band readiness-band--healthy">
            <strong>{{ data.case_summary?.closed || 0 }}</strong> closed
          </span>
        </div>

        <p class="readiness-panel__meta">
          Open cases with an owner and a next check-in. Overdue follow-ups are
          support prompts, not compliance failures.
        </p>

        <label class="readiness-followup-filter">
          <input v-model="onlyMyCases" type="checkbox" />
          Only my cases
        </label>

        <div v-if="!visibleFollowUps.length" class="readiness-panel__empty">
          {{ onlyMyCases ? 'No open cases assigned to you.' : 'No open follow-ups. Assign a case from the support queue to start one.' }}
        </div>

        <div v-else class="table-wrapper">
          <table class="data-table readiness-table">
            <caption class="sr-only">Open readiness follow-ups for the selected course</caption>
            <thead>
              <tr>
                <th scope="col">Learner</th>
                <th scope="col">Priority</th>
                <th scope="col">Owner</th>
                <th scope="col">Next check-in</th>
                <th scope="col">Status</th>
                <th scope="col">Open</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="followUp in visibleFollowUps" :key="followUp.user_id">
                <td>
                  <strong>{{ followUp.display_name }}</strong>
                  <small>{{ followUp.username }} · CWRS {{ followUp.cwrs }} · {{ followUp.band_label }}</small>
                </td>
                <td>
                  <span class="case-priority" :class="`case-priority--${followUp.priority}`">
                    {{ priorityLabel(followUp.priority) }}
                  </span>
                </td>
                <td>{{ followUp.owner_name || 'Unassigned' }}</td>
                <td>{{ formatDate(followUp.follow_up_at) }}</td>
                <td>
                  <span v-if="followUp.overdue" class="follow-up-state follow-up-state--overdue">Overdue</span>
                  <span v-else-if="followUp.due_soon" class="follow-up-state follow-up-state--due">Due soon</span>
                  <span v-else class="follow-up-state">Scheduled</span>
                </td>
                <td>
                  <button type="button" class="btn btn--secondary btn--xs" @click="openStudentFromFollowUp(followUp)">
                    Open case
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div
        v-else-if="activeView === 'labs'"
        id="readiness-panel-labs"
        role="tabpanel"
        aria-labelledby="readiness-tab-labs"
        class="readiness-panel__view"
      >
        <div class="readiness-panel__bands">
          <span class="readiness-band readiness-band--critical_intervention">
            <strong>{{ data.lab_health.counts.degraded || 0 }}</strong> degraded
          </span>
          <span class="readiness-band readiness-band--high_risk">
            <strong>{{ data.lab_health.counts.warning || 0 }}</strong> warning
          </span>
          <span class="readiness-band readiness-band--monitor">
            <strong>{{ data.lab_health.counts.no_data || 0 }}</strong> no data
          </span>
          <span class="readiness-band readiness-band--healthy">
            <strong>{{ data.lab_health.counts.healthy || 0 }}</strong> healthy
          </span>
        </div>

        <p class="readiness-panel__meta">
          Low success is not automatically a defect. Review hints, abandonment,
          time, and the workbook before changing a lab.
        </p>

        <div v-if="!visibleLabs.length" class="readiness-panel__empty">
          No lab health issues in this view.
        </div>

        <div v-else class="table-wrapper">
          <table class="data-table readiness-table">
            <caption class="sr-only">Lab health for the selected course</caption>
            <thead>
              <tr>
                <th scope="col">Lab</th>
                <th scope="col">Status</th>
                <th scope="col">Started</th>
                <th scope="col">Success</th>
                <th scope="col">Abandon</th>
                <th scope="col">Hints</th>
                <th scope="col">Median time</th>
                <th scope="col">Review</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lab in visibleLabs" :key="lab.lab_id">
                <td>
                  <strong>{{ lab.name }}</strong>
                  <small>{{ lab.track || 'Uncategorized' }} · {{ lab.level || 'No level' }}</small>
                </td>
                <td>
                  <span class="lab-status" :class="`lab-status--${lab.status}`">
                    {{ labStatusLabel(lab.status) }}
                  </span>
                </td>
                <td>{{ lab.started }}</td>
                <td>{{ lab.success_rate == null ? '—' : `${lab.success_rate}%` }}</td>
                <td>{{ lab.abandonment_rate == null ? '—' : `${lab.abandonment_rate}%` }}</td>
                <td>{{ lab.median_hints ?? '—' }}</td>
                <td>{{ lab.median_minutes == null ? '—' : `${lab.median_minutes}m` }}</td>
                <td>
                  <button type="button" class="btn btn--secondary btn--xs" @click="openLabReview(lab)">
                    {{ lab.review ? 'Update' : 'Review' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="reviewLab" class="lab-review">
          <div class="readiness-workflow__head">
            <h3>Review {{ reviewLab.name }}</h3>
            <button type="button" class="btn btn--secondary btn--xs" @click="reviewLab = null">
              Close
            </button>
          </div>
          <div class="lab-review__row">
            <select v-model="labReview.status" class="form-input form-input--sm">
              <option value="healthy">Healthy challenge</option>
              <option value="warning">Warning</option>
              <option value="degraded">Degraded</option>
              <option value="no_data">No data</option>
            </select>
            <input v-model="labReview.finding" class="form-input form-input--sm" placeholder="Finding" maxlength="2000" />
            <input v-model="labReview.action" class="form-input form-input--sm" placeholder="Action or owner" maxlength="2000" />
            <input v-model="labReview.outcome" class="form-input form-input--sm" placeholder="Outcome" maxlength="500" />
            <button
              type="button"
              class="btn btn--primary btn--sm"
              :disabled="labReviewSaving"
              @click="saveLabReview"
            >
              {{ labReviewSaving ? 'Saving...' : 'Save review' }}
            </button>
          </div>
          <p v-if="labReviewError" class="readiness-panel__provisional" role="alert">{{ labReviewError }}</p>
          <p v-if="reviewLab.review" class="readiness-panel__meta">
            Last review: {{ reviewLab.review.outcome || reviewLab.review.status }} ·
            {{ formatDate(reviewLab.review.reviewed_at) }}
            <template v-if="reviewLab.review.finding"> · {{ reviewLab.review.finding }}</template>
          </p>
        </div>

        <button
          v-if="hasHealthyLabs"
          type="button"
          class="btn btn--secondary btn--sm readiness-panel__more"
          @click="showHealthy = !showHealthy"
        >
          {{ showHealthy ? 'Hide healthy labs' : 'Show healthy labs' }}
        </button>
      </div>

      <div
        v-else
        id="readiness-panel-calibration"
        role="tabpanel"
        aria-labelledby="readiness-tab-calibration"
        class="readiness-panel__view"
      >
        <div v-if="calibrationLoading" class="readiness-panel__empty" role="status">
          Loading calibration evidence...
        </div>
        <div v-else-if="calibrationError" class="readiness-panel__empty readiness-panel__empty--error" role="alert">
          {{ calibrationError }}
        </div>
        <template v-else-if="calibration">
          <p class="readiness-panel__meta">
            Calibration compares the pilot bands with the flags, support actions,
            outcomes, and lab reviews instructors actually record. It is not a
            model-accuracy claim.
          </p>
          <div class="calibration-grid">
            <section class="calibration-card">
              <h3>Band distribution</h3>
              <p v-for="(count, key) in calibration.band_counts" :key="key">
                <span>{{ bandLabel(key) }}</span><strong>{{ count }}</strong>
              </p>
            </section>
            <section class="calibration-card">
              <h3>Flags</h3>
              <p v-for="(count, key) in calibration.flag_counts" :key="key">
                <span>{{ flagLabel(key) }}</span><strong>{{ count }}</strong>
              </p>
              <p v-if="!Object.keys(calibration.flag_counts).length" class="muted">No flags recorded.</p>
            </section>
            <section class="calibration-card">
              <h3>Cases</h3>
              <p v-for="(count, key) in calibration.case_counts" :key="key">
                <span>{{ key }}</span><strong>{{ count }}</strong>
              </p>
            </section>
            <section class="calibration-card">
              <h3>Open case priority</h3>
              <p v-for="(count, key) in calibration.case_priority_counts" :key="key">
                <span>{{ priorityLabel(key) }}</span><strong>{{ count }}</strong>
              </p>
              <p v-if="!Object.keys(calibration.case_priority_counts).length" class="muted">No open cases.</p>
            </section>
            <section class="calibration-card">
              <h3>Support actions</h3>
              <p v-for="(count, key) in calibration.action_counts" :key="key">
                <span>{{ actionLabel(key) }}</span><strong>{{ count }}</strong>
              </p>
              <p v-if="!Object.keys(calibration.action_counts).length" class="muted">No actions logged.</p>
            </section>
            <section class="calibration-card">
              <h3>Outcomes</h3>
              <p v-for="(count, key) in calibration.outcome_counts" :key="key">
                <span>{{ key }}</span><strong>{{ count }}</strong>
              </p>
              <p v-if="!Object.keys(calibration.outcome_counts).length" class="muted">No outcomes recorded.</p>
            </section>
            <section class="calibration-card">
              <h3>Flag states</h3>
              <p v-for="(count, key) in calibration.flag_state_counts" :key="key">
                <span>{{ key }}</span><strong>{{ count }}</strong>
              </p>
              <p v-if="!Object.keys(calibration.flag_state_counts).length" class="muted">No dismissals or snoozes.</p>
            </section>
            <section class="calibration-card">
              <h3>Lab reviews</h3>
              <p v-for="(count, key) in calibration.lab_review_counts" :key="key">
                <span>{{ key }}</span><strong>{{ count }}</strong>
              </p>
              <p v-if="!Object.keys(calibration.lab_review_counts).length" class="muted">No lab reviews yet.</p>
            </section>
          </div>
        </template>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  courseId: { type: Number, default: null },
  courses: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:courseId'])

const data = ref(null)
const loading = ref(false)
const error = ref('')
const activeView = ref('queue')
const showAllStudents = ref(false)
const showHealthy = ref(false)
const expandedStudent = ref(null)
const capabilities = ref(null)
const capabilitiesFor = ref(null)
const capabilitiesLoading = ref(null)
const capabilitiesError = ref('')
const defaultVisible = 5
const calibration = ref(null)
const calibrationLoading = ref(false)
const calibrationError = ref('')
const workflow = ref({ kind: 'context', key: 'absence', state: 'acknowledged', note: '' })
const workflowSaving = ref(false)
const workflowError = ref('')
const reviewLab = ref(null)
const labReview = ref({ status: 'warning', finding: '', action: '', outcome: '' })
const labReviewSaving = ref(false)
const labReviewError = ref('')
const onlyMyCases = ref(false)
const caseForm = ref({ owner_id: '', priority: 'normal', follow_up_date: '', note: '' })
const caseSaving = ref(false)
const caseError = ref('')

function readCurrentUserId() {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return Number(user.id) || null
  } catch {
    return null
  }
}

const currentUserId = readCurrentUserId()

const expandedStudentData = computed(
  () => data.value?.students?.find((student) => student.user_id === expandedStudent.value) || null,
)

const CONTEXT_OPTIONS = [
  { value: 'absence', label: 'Planned absence' },
  { value: 'illness', label: 'Illness or recovery' },
  { value: 'bereavement', label: 'Bereavement' },
  { value: 'placement', label: 'Placement or work commitment' },
  { value: 'accommodation', label: 'Accommodation' },
  { value: 'other', label: 'Other context' },
]

const ACTION_OPTIONS = [
  { value: 'contacted', label: 'Contacted learner' },
  { value: 'guided_retry', label: 'Guided retry' },
  { value: 'extension', label: 'Extension' },
  { value: 'study_plan', label: 'Study plan' },
  { value: 'lab_reset', label: 'Lab reset or environment check' },
  { value: 'referral', label: 'Referral to support service' },
]

const workflowOptions = computed(() => {
  if (workflow.value.kind === 'action') return ACTION_OPTIONS
  if (workflow.value.kind === 'flag_state') {
    return (expandedStudentData.value?.flags || []).map((flag) => ({
      value: flag,
      label: flagLabel(flag),
    }))
  }
  return CONTEXT_OPTIONS
})

const bandSummary = computed(() => {
  const counts = data.value?.cohort?.band_counts || {}
  return [
    { key: 'critical_intervention', label: 'Critical', count: counts.critical_intervention || 0 },
    { key: 'high_risk', label: 'High', count: counts.high_risk || 0 },
    { key: 'elevated', label: 'Elevated', count: counts.elevated || 0 },
    { key: 'monitor', label: 'Monitor', count: counts.monitor || 0 },
    { key: 'healthy', label: 'Healthy', count: counts.healthy || 0 },
  ]
})

const visibleStudents = computed(() => {
  if (!data.value) return []
  return showAllStudents.value
    ? data.value.students
    : data.value.students.slice(0, defaultVisible)
})

const visibleFollowUps = computed(() => {
  const rows = data.value?.follow_ups || []
  if (!onlyMyCases.value) return rows
  if (!currentUserId) return []
  return rows.filter((row) => row.owner_id === currentUserId)
})

const visibleLabs = computed(() => {
  if (!data.value) return []
  const labs = data.value.lab_health.labs || []
  return showHealthy.value ? labs : labs.filter((lab) => lab.status !== 'healthy')
})

const hasHealthyLabs = computed(() => (data.value?.lab_health.labs || []).some((lab) => lab.status === 'healthy'))

const componentLabel = (key) => ({
  performance: 'Performance',
  engagement: 'Engagement',
  progression: 'Progression',
  competency: 'Competency',
  behavioural: 'Learning behaviour',
  infrastructure: 'Learner-specific infrastructure',
}[key] || key)

const flagLabel = (flag) => ({
  performance: 'Performance',
  engagement: 'Engagement',
  progression: 'Falling behind',
  competency: 'Capability gap',
  abandonment: 'Abandonment',
  inactive: 'Inactive',
  no_completions: 'No completions',
}[flag] || flag)

const contextLabel = (key) => ({
  absence: 'Planned absence',
  illness: 'Illness or recovery',
  bereavement: 'Bereavement',
  placement: 'Placement or work commitment',
  accommodation: 'Accommodation',
  other: 'Other context',
}[key] || key)

const actionLabel = (key) => ({
  contacted: 'Contacted learner',
  guided_retry: 'Guided retry',
  extension: 'Extension',
  study_plan: 'Study plan',
  lab_reset: 'Lab reset',
  referral: 'Referral',
}[key] || key)

const priorityLabel = (key) => ({
  low: 'Low priority',
  normal: 'Normal priority',
  high: 'High priority',
}[key] || key)

const toDateInput = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 10)
}

const bandLabel = (key) => ({
  critical_intervention: 'Critical intervention',
  high_risk: 'High risk',
  elevated: 'Elevated',
  monitor: 'Monitor',
  healthy: 'Healthy',
}[key] || key)

const formatDate = (value) => {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString()
}

const labStatusLabel = (status) => ({
  degraded: 'Degraded',
  warning: 'Warning',
  no_data: 'No data',
  healthy: 'Healthy',
}[status] || status)

function selectCourse(value) {
  emit('update:courseId', value ? Number(value) : null)
}

async function fetchReadiness() {
  if (!props.courseId) {
    data.value = null
    return
  }
  loading.value = true
  error.value = ''
  try {
    const { data: payload } = await axios.get(`/analytics/courses/${props.courseId}/readiness`)
    data.value = payload
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load readiness evidence.'
  } finally {
    loading.value = false
  }
}

async function toggleStudent(student) {
  if (expandedStudent.value === student.user_id) {
    expandedStudent.value = null
    return
  }
  expandedStudent.value = student.user_id
  syncCaseForm(student)
  capabilities.value = null
  capabilitiesFor.value = null
  capabilitiesError.value = ''
  await loadCapabilities(student.user_id)
}

function syncCaseForm(student) {
  caseError.value = ''
  caseForm.value = {
    owner_id: student.case?.owner_id ? String(student.case.owner_id) : '',
    priority: student.case?.priority || 'normal',
    follow_up_date: toDateInput(student.case?.follow_up_at),
    note: '',
  }
}

async function openStudentFromFollowUp(followUp) {
  activeView.value = 'queue'
  showAllStudents.value = true
  const student = data.value?.students?.find((row) => row.user_id === followUp.user_id)
  if (!student) return
  expandedStudent.value = student.user_id
  syncCaseForm(student)
  capabilities.value = null
  capabilitiesFor.value = null
  capabilitiesError.value = ''
  await loadCapabilities(student.user_id)
}

async function saveCase(student, state) {
  if (!props.courseId) return
  caseSaving.value = true
  caseError.value = ''
  try {
    const body = {
      kind: 'case',
      key: 'ownership',
      state,
      priority: caseForm.value.priority,
      note: caseForm.value.note || null,
    }
    if (caseForm.value.owner_id) {
      body.owner_id = Number(caseForm.value.owner_id)
    }
    if (state === 'open' && caseForm.value.follow_up_date) {
      body.follow_up_at = new Date(`${caseForm.value.follow_up_date}T12:00:00`).toISOString()
    }
    await axios.post(
      `/analytics/courses/${props.courseId}/students/${student.user_id}/notes`,
      body,
    )
    calibration.value = null
    await fetchReadiness()
    const refreshed = data.value?.students?.find((row) => row.user_id === student.user_id)
    if (refreshed) syncCaseForm(refreshed)
  } catch (e) {
    caseError.value = e.response?.data?.detail || 'Could not save the case.'
  } finally {
    caseSaving.value = false
  }
}

async function loadCapabilities(userId) {
  capabilitiesLoading.value = userId
  capabilitiesError.value = ''
  try {
    const { data: payload } = await axios.get(
      `/analytics/courses/${props.courseId}/students/${userId}/capabilities`,
    )
    capabilities.value = payload
    capabilitiesFor.value = userId
  } catch (e) {
    capabilitiesError.value = e.response?.data?.detail || 'Could not load capability detail.'
  } finally {
    capabilitiesLoading.value = null
  }
}

function onWorkflowKind() {
  const options = workflowOptions.value
  workflow.value.key = options[0]?.value || ''
  workflow.value.state = 'acknowledged'
  workflowError.value = ''
}

async function saveWorkflow(student) {
  if (!props.courseId || !workflow.value.key) return
  workflowSaving.value = true
  workflowError.value = ''
  try {
    const body = {
      kind: workflow.value.kind,
      key: workflow.value.key,
      note: workflow.value.note || null,
    }
    if (workflow.value.kind === 'flag_state') {
      body.state = workflow.value.state
      if (workflow.value.state === 'snoozed') {
        body.end_at = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      }
    }
    await axios.post(`/analytics/courses/${props.courseId}/students/${student.user_id}/notes`, body)
    workflow.value.note = ''
    calibration.value = null
    await fetchReadiness()
  } catch (e) {
    workflowError.value = e.response?.data?.detail || 'Could not save the support record.'
  } finally {
    workflowSaving.value = false
  }
}

async function openCalibration() {
  activeView.value = 'calibration'
  if (calibration.value || !props.courseId) return
  calibrationLoading.value = true
  calibrationError.value = ''
  try {
    const { data: payload } = await axios.get(
      `/analytics/courses/${props.courseId}/readiness/calibration`,
    )
    calibration.value = payload
  } catch (e) {
    calibrationError.value = e.response?.data?.detail || 'Could not load calibration evidence.'
  } finally {
    calibrationLoading.value = false
  }
}

function openLabReview(lab) {
  reviewLab.value = lab
  labReviewError.value = ''
  labReview.value = {
    status: lab.review?.status || lab.status || 'warning',
    finding: lab.review?.finding || '',
    action: lab.review?.action || '',
    outcome: lab.review?.outcome || '',
  }
}

async function saveLabReview() {
  if (!props.courseId || !reviewLab.value) return
  labReviewSaving.value = true
  labReviewError.value = ''
  try {
    await axios.post(
      `/analytics/courses/${props.courseId}/labs/${reviewLab.value.lab_id}/reviews`,
      labReview.value,
    )
    reviewLab.value = null
    calibration.value = null
    await fetchReadiness()
  } catch (e) {
    labReviewError.value = e.response?.data?.detail || 'Could not save the lab review.'
  } finally {
    labReviewSaving.value = false
  }
}

watch(
  () => props.courseId,
  () => {
    showAllStudents.value = false
    showHealthy.value = false
    onlyMyCases.value = false
    expandedStudent.value = null
    capabilities.value = null
    capabilitiesFor.value = null
    calibration.value = null
    calibrationError.value = ''
    activeView.value = 'queue'
    fetchReadiness()
  },
  { immediate: true },
)
</script>

<style scoped>
.readiness-panel {
  margin-top: 1.5rem;
  padding: 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.readiness-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.readiness-panel__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent-text);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.readiness-panel__title {
  margin: 0 0 0.3rem;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.readiness-panel__lead,
.readiness-panel__meta {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.6;
}

.readiness-panel__controls {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.readiness-panel__course {
  display: grid;
  gap: 0.2rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 600;
}

.readiness-panel__tabs {
  display: flex;
  gap: 0.35rem;
  margin: 1rem 0 0.75rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.readiness-panel__tab {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.7rem;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.readiness-panel__tab:hover,
.readiness-panel__tab--active {
  border-color: var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
}

.readiness-panel__tab span {
  color: var(--text-muted);
  font-size: 0.68rem;
}

.readiness-panel__view {
  display: grid;
  gap: 0.8rem;
}

.readiness-panel__bands {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.readiness-band {
  display: inline-flex;
  align-items: baseline;
  gap: 0.3rem;
  padding: 0.3rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 0.7rem;
}

.readiness-band strong {
  color: var(--text-primary);
  font-size: 0.85rem;
}

.readiness-band--critical_intervention {
  border-color: var(--danger);
  background: var(--danger-bg);
  color: var(--danger);
}

.readiness-band--high_risk {
  border-color: var(--warning);
  background: var(--warning-bg);
  color: var(--warning);
}

.readiness-band--elevated,
.readiness-band--monitor {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.readiness-band--healthy {
  border-color: var(--success);
  background: var(--success-bg);
  color: var(--success);
}

.readiness-list {
  display: grid;
  gap: 0.55rem;
}

.readiness-card {
  border: 1px solid var(--border-color);
  border-radius: 9px;
  background: var(--bg-primary);
  overflow: hidden;
}

.readiness-card--critical_intervention {
  border-left: 3px solid var(--danger);
}

.readiness-card--high_risk {
  border-left: 3px solid var(--warning);
}

.readiness-card--elevated,
.readiness-card--monitor {
  border-left: 3px solid var(--accent);
}

.readiness-card--healthy {
  border-left: 3px solid var(--success);
}

.readiness-card__summary {
  display: grid;
  grid-template-columns: minmax(10rem, 1.4fr) auto auto minmax(8rem, 1fr) auto;
  align-items: center;
  gap: 0.7rem;
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 0;
  background: transparent;
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
}

.readiness-card__summary:hover {
  background: var(--hover-bg);
}

.readiness-card__identity,
.readiness-card__score {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.readiness-card__identity small,
.readiness-card__score small {
  color: var(--text-muted);
  font-size: 0.68rem;
}

.readiness-card__score {
  text-align: right;
}

.readiness-card__score strong {
  font-size: 1.15rem;
}

.readiness-card__confidence {
  color: var(--text-muted);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.readiness-card__flags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.readiness-flag {
  padding: 0.1rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 0.64rem;
}

.readiness-card__caret {
  color: var(--text-muted);
  font-size: 1rem;
}

.readiness-card__detail {
  display: grid;
  gap: 0.75rem;
  padding: 0 0.75rem 0.8rem;
}

.readiness-card__components {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
  gap: 0.5rem 0.8rem;
}

.readiness-component {
  display: grid;
  gap: 0.25rem;
}

.readiness-component__head {
  display: flex;
  justify-content: space-between;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.readiness-component__head strong {
  color: var(--text-primary);
}

.readiness-component__bar,
.capability-row__bar {
  height: 5px;
  border-radius: 999px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.readiness-component__bar span,
.capability-row__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--purple));
}

.readiness-component__bar span.is-missing {
  width: 0 !important;
}

.readiness-card__facts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.9rem;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.readiness-panel__provisional {
  color: var(--warning);
}

.readiness-card__capabilities {
  padding-top: 0.6rem;
  border-top: 1px solid var(--border-color);
}

.readiness-card__capabilities-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.readiness-card__capabilities-head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.82rem;
}

.capability-list {
  display: grid;
  gap: 0.35rem;
  margin-top: 0.5rem;
}

.capability-row {
  display: grid;
  grid-template-columns: minmax(8rem, 1fr) minmax(6rem, 1.5fr) 3rem;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.capability-row strong {
  color: var(--text-primary);
  text-align: right;
}

.readiness-table td small {
  display: block;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.lab-status {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
}

.lab-status--degraded {
  background: var(--danger-bg);
  color: var(--danger);
}

.lab-status--warning {
  background: var(--warning-bg);
  color: var(--warning);
}

.lab-status--no_data {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.lab-status--healthy {
  background: var(--success-bg);
  color: var(--success);
}

.readiness-panel__empty {
  padding: 1rem;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.readiness-panel__empty--error {
  border-color: var(--danger);
  color: var(--danger);
}

.readiness-panel__more {
  justify-self: start;
}

.readiness-workflow,
.readiness-case,
.lab-review {
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.readiness-case {
  border-left: 3px solid var(--accent);
}

.readiness-followup-filter {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.74rem;
}

.case-priority,
.follow-up-state {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 0.66rem;
  font-weight: 600;
}

.case-priority--high,
.follow-up-state--overdue {
  border-color: var(--danger);
  background: var(--danger-bg);
  color: var(--danger);
}

.case-priority--normal,
.follow-up-state--due {
  border-color: var(--warning);
  background: var(--warning-bg);
  color: var(--warning);
}

.case-priority--low {
  border-color: var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.readiness-workflow__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}

.readiness-workflow__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.82rem;
}

.readiness-workflow__head span {
  color: var(--text-muted);
  font-size: 0.68rem;
}

.readiness-workflow__row,
.lab-review__row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.readiness-workflow__note {
  flex: 1 1 12rem;
  min-width: 8rem;
}

.readiness-workflow__existing {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem 0.6rem;
  margin-top: 0.4rem;
  color: var(--text-muted);
  font-size: 0.7rem;
}

.readiness-workflow__existing strong {
  color: var(--text-secondary);
}

.calibration-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
  gap: 0.6rem;
}

.calibration-card {
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.calibration-card h3 {
  margin: 0 0 0.45rem;
  color: var(--text-primary);
  font-size: 0.8rem;
}

.calibration-card p {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin: 0.2rem 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.calibration-card p strong {
  color: var(--text-primary);
}

.calibration-card p.muted {
  color: var(--text-muted);
  justify-content: flex-start;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 720px) {
  .readiness-card__summary {
    grid-template-columns: 1fr auto auto;
  }

  .readiness-card__confidence,
  .readiness-card__flags {
    display: none;
  }
}
</style>
