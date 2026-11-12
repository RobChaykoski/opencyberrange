<template>
  <section class="readiness" aria-labelledby="readiness-title">
    <header class="readiness__head">
      <div>
        <p class="readiness__eyebrow">Cyber GPS readiness</p>
        <h2 id="readiness-title" class="readiness__title">I want to become a {{ selectedRoleTitle }}.</h2>
        <p class="readiness__intro">
          Pick a target role. OpenCyberRange will show the skills you already have,
          what to complete next, your readiness score, the capstone to attempt, the
          certifications that align, and the evidence you can show an employer.
        </p>
      </div>
      <label class="readiness__select">
        <span>Target role</span>
        <select v-model="selectedRole" @change="loadReadiness">
          <option v-for="role in roles" :key="role.id" :value="role.id">
            {{ role.title }}{{ role.flagship ? ' · flagship' : '' }}
          </option>
        </select>
      </label>
    </header>

    <p v-if="loading" class="readiness__state">Loading your pathway answer…</p>
    <p v-else-if="error" class="readiness__state readiness__state--error" role="alert">{{ error }}</p>

    <template v-else-if="data">
      <div class="readiness-hero">
        <div
          class="readiness-ring"
          :style="{ '--readiness': `${data.readiness.score}%` }"
          role="img"
          :aria-label="`${data.role.title} readiness: ${data.readiness.score} out of 100`"
        >
          <span>{{ data.readiness.score }}</span>
          <small>/100</small>
        </div>
        <div class="readiness-hero__body">
          <p class="readiness__eyebrow">{{ data.role.family }} pathway</p>
          <h3>{{ data.readiness.rating.label }}</h3>
          <p>{{ data.readiness.rating.description }}</p>
          <p class="readiness-hero__meta">
            Career-ready threshold {{ data.readiness.threshold }} ·
            no critical domain below {{ data.readiness.domain_floor }} ·
            {{ data.readiness.career_ready ? 'threshold met' : 'threshold not met yet' }}
          </p>
        </div>
        <div class="readiness-hero__next">
          <span>Next move</span>
          <p>{{ data.next_action }}</p>
        </div>
      </div>

      <div class="readiness-pipeline" aria-label="Evidence pipeline">
        <article
          v-for="stage in data.pipeline"
          :key="stage.key"
          class="readiness-stage"
          :class="`readiness-stage--${stage.state}`"
        >
          <span>{{ stage.label }}</span>
          <strong>{{ stage.value }}</strong>
          <small>{{ stage.detail }}</small>
        </article>
      </div>

      <div class="readiness-grid">
        <section class="readiness-panel" aria-labelledby="readiness-domains-title">
          <div class="readiness-panel__head">
            <div>
              <p class="readiness__eyebrow">Domain readiness</p>
              <h3 id="readiness-domains-title">Where the evidence is strong</h3>
            </div>
          </div>
          <div class="readiness-domains">
            <article
              v-for="domain in data.domains"
              :key="domain.domain"
              class="readiness-domain"
              :class="`readiness-domain--${domain.colour}`"
            >
              <div class="readiness-domain__head">
                <strong>
                  <i class="readiness-dot" :class="`readiness-dot--${domain.colour}`" aria-hidden="true"></i>
                  {{ domain.label }}
                </strong>
                <span>{{ domain.target_level }} · {{ domain.score }}%</span>
              </div>
              <div
                class="readiness-domain__bar"
                role="progressbar"
                :aria-valuenow="domain.score"
                aria-valuemin="0"
                aria-valuemax="100"
                :aria-label="`${domain.label}: ${domain.score} out of 100`"
              >
                <span :style="{ width: domain.score + '%' }"></span>
              </div>
              <p>{{ domain.have }} at target · {{ domain.building }} building · {{ domain.gap }} to build</p>
            </article>
          </div>
        </section>

        <section class="readiness-panel" aria-labelledby="readiness-gap-title">
          <div class="readiness-panel__head">
            <div>
              <p class="readiness__eyebrow">Skills gap</p>
              <h3 id="readiness-gap-title">What to build next</h3>
            </div>
          </div>
          <ul v-if="data.skills_gap.length" class="readiness-list">
            <li v-for="skill in data.skills_gap.slice(0, 6)" :key="skill.id">
              <div>
                <strong>{{ skill.name }}</strong>
                <span>{{ skill.id }} · {{ skill.domain_label }} · target {{ skill.target_level }}</span>
              </div>
              <span class="readiness-chip" :class="`readiness-chip--${skill.status}`">
                {{ skill.status.replace('_', ' ') }}
              </span>
            </li>
          </ul>
          <p v-else class="readiness-empty">No critical gaps in this pathway. Keep the evidence current.</p>
        </section>
      </div>

      <section class="readiness-panel" aria-labelledby="readiness-workbooks-title">
        <div class="readiness-panel__head">
          <div>
            <p class="readiness__eyebrow">Next workbooks</p>
            <h3 id="readiness-workbooks-title">The shortest route through the gap</h3>
          </div>
        </div>
        <div v-if="data.next_workbooks.length" class="readiness-workbooks">
          <router-link
            v-for="item in data.next_workbooks"
            :key="item.slug"
            :to="`/exercises/${item.track_slug}`"
            class="readiness-workbook"
            :class="`readiness-workbook--${item.readiness?.colour || 'grey'}`"
          >
            <span class="readiness-workbook__top">
              <span class="readiness-workbook__track">{{ item.track }}</span>
              <span
                v-if="item.readiness"
                class="readiness-chip"
                :class="`readiness-chip--${item.readiness.colour}`"
              >
                {{ item.readiness.label }}
              </span>
            </span>
            <strong>{{ item.name }}</strong>
            <span>{{ item.difficulty }} · {{ item.competencies.join(' · ') }}</span>
            <span v-if="item.readiness" class="readiness-workbook__reason">
              {{ item.readiness.reason }}
            </span>
          </router-link>
        </div>
        <p v-else class="readiness-empty">No uncompleted workbook matches the current gaps.</p>
      </section>

      <div class="readiness-grid">
        <section class="readiness-panel readiness-panel--accent" aria-labelledby="readiness-capstone-title">
          <div class="readiness-panel__head">
            <div>
              <p class="readiness__eyebrow">Capstone</p>
              <h3 id="readiness-capstone-title">{{ data.capstone.title }}</h3>
            </div>
            <span class="readiness-chip" :class="data.capstone.completed ? 'readiness-chip--have' : 'readiness-chip--building'">
              {{ data.capstone.completed ? 'Completed' : 'Next' }}
            </span>
          </div>
          <p>{{ data.capstone.description }}</p>
          <ul v-if="data.capstone.deliverables?.length" class="readiness-deliverables">
            <li v-for="item in data.capstone.deliverables" :key="item">{{ item }}</li>
          </ul>
          <router-link
            v-if="data.capstone.lab?.track_slug"
            :to="`/exercises/${data.capstone.lab.track_slug}`"
            class="btn btn--secondary btn--sm"
          >
            {{ data.capstone.completed ? 'Review capstone' : 'Open capstone track' }}
          </router-link>
        </section>

        <section class="readiness-panel" aria-labelledby="readiness-certs-title">
          <div class="readiness-panel__head">
            <div>
              <p class="readiness__eyebrow">Certifications</p>
              <h3 id="readiness-certs-title">Aligned pathways</h3>
            </div>
          </div>
          <div class="readiness-certs">
            <div>
              <span>Start here</span>
              <p>{{ (data.certifications.entry || []).join(' · ') || '—' }}</p>
            </div>
            <div>
              <span>Build on it</span>
              <p>{{ (data.certifications.core || []).join(' · ') || '—' }}</p>
            </div>
            <div>
              <span>Go further</span>
              <p>{{ (data.certifications.advanced || []).join(' · ') || '—' }}</p>
            </div>
          </div>
          <p class="readiness-note">
            Certification names and requirements change. Verify them with the vendor.
          </p>
        </section>
      </div>

      <section class="readiness-panel" aria-labelledby="readiness-evidence-title">
        <div class="readiness-panel__head">
          <div>
            <p class="readiness__eyebrow">Employer evidence</p>
            <h3 id="readiness-evidence-title">What you can show</h3>
          </div>
        </div>
        <div class="readiness-evidence">
          <div><strong>{{ data.evidence.completed_role_labs }}</strong><span>role labs</span></div>
          <div><strong>{{ data.evidence.clean_solves }}</strong><span>clean solves</span></div>
          <div><strong>{{ data.evidence.capstones_completed }}</strong><span>capstones</span></div>
          <div><strong>{{ data.evidence.certificates }}</strong><span>certificates</span></div>
        </div>
        <ul v-if="data.evidence.work_samples?.length" class="readiness-samples">
          <li v-for="sample in data.evidence.work_samples" :key="sample.name + sample.completed_at">
            <strong>{{ sample.name }}</strong>
            <span>{{ sample.track }} · {{ sample.difficulty }}</span>
          </li>
        </ul>
        <p class="readiness-note">{{ data.disclaimer }}</p>
      </section>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import axios from '../api/axios'
import { useCareerGoal } from '../composables/useCareerGoal'

const { selectedRole, setGoal } = useCareerGoal()
const roles = ref([])
const data = ref(null)
const loading = ref(true)
const error = ref('')

const selectedRoleTitle = computed(() => {
  const role = roles.value.find((item) => item.id === selectedRole.value)
  return role?.title || data.value?.role?.title || 'target role'
})

watch(selectedRole, () => {
  loadReadiness()
})

async function loadRoles() {
  try {
    const response = await axios.get('/profile/roles')
    roles.value = response.data.roles || []
    const preferred =
      roles.value.find((role) => role.id === selectedRole.value) ||
      roles.value.find((role) => role.id === 'soc-analyst') ||
      roles.value.find((role) => role.flagship) ||
      roles.value[0]
    if (preferred && preferred.id !== selectedRole.value) setGoal(preferred.id)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load the pathway catalogue.'
  }
}

async function loadReadiness() {
  if (!selectedRole.value) return
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/profile/role-readiness', {
      params: { role: selectedRole.value },
    })
    data.value = response.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load role readiness.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadRoles()
  await loadReadiness()
})
</script>

<style scoped>
.readiness {
  display: grid;
  gap: 0.9rem;
  margin-bottom: 1rem;
}

.readiness__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    radial-gradient(circle at 0% 0%, var(--accent-bg), transparent 55%),
    var(--bg-secondary);
}

.readiness__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.readiness__title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 750;
}

.readiness__intro {
  max-width: 58rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.readiness__select {
  display: grid;
  gap: 0.25rem;
  flex: 0 0 auto;
  min-width: 220px;
  color: var(--text-muted);
  font-size: 0.66rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.readiness__select select {
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
  font-size: 0.8rem;
  text-transform: none;
  letter-spacing: normal;
}

.readiness__state {
  margin: 0;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.readiness__state--error {
  border-color: var(--danger);
  color: var(--danger);
}

.readiness-hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) minmax(220px, 0.7fr);
  gap: 1rem;
  align-items: center;
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.readiness-ring {
  display: grid;
  place-items: center;
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: conic-gradient(var(--accent) var(--readiness), var(--bg-tertiary) 0);
  position: relative;
}

.readiness-ring::after {
  content: '';
  position: absolute;
  inset: 8px;
  border-radius: 50%;
  background: var(--bg-secondary);
}

.readiness-ring span,
.readiness-ring small {
  position: relative;
  z-index: 1;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.readiness-ring span {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1;
}

.readiness-ring small {
  margin-top: -1.7rem;
  color: var(--text-muted);
  font-size: 0.6rem;
}

.readiness-hero__body h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.05rem;
  font-weight: 700;
}

.readiness-hero__body p {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.45;
}

.readiness-hero__meta {
  color: var(--text-muted) !important;
  font-size: 0.68rem !important;
}

.readiness-hero__next {
  padding: 0.65rem 0.75rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  background: var(--accent-bg);
}

.readiness-hero__next span {
  color: var(--accent-text);
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.readiness-hero__next p {
  margin: 0.2rem 0 0;
  color: var(--text-primary);
  font-size: 0.78rem;
  line-height: 1.45;
}

.readiness-pipeline {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.55rem;
}

.readiness-stage {
  padding: 0.65rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.readiness-stage--complete {
  border-left: 3px solid var(--success);
}

.readiness-stage--in_progress {
  border-left: 3px solid var(--warning);
}

.readiness-stage span {
  display: block;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.readiness-stage strong {
  display: block;
  margin-top: 0.1rem;
  color: var(--text-primary);
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.readiness-stage small {
  display: block;
  color: var(--text-muted);
  font-size: 0.62rem;
  line-height: 1.4;
}

.readiness-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 0.75rem;
}

.readiness-panel {
  padding: 0.9rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.readiness-panel--accent {
  border-left: 3px solid var(--accent);
}

.readiness-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.readiness-panel__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 700;
}

.readiness-panel p {
  color: var(--text-secondary);
  font-size: 0.74rem;
  line-height: 1.45;
}

.readiness-domains {
  display: grid;
  gap: 0.55rem;
}

.readiness-domain {
  padding: 0.55rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.readiness-domain--green { border-left: 3px solid var(--success); }
.readiness-domain--amber { border-left: 3px solid var(--warning); }
.readiness-domain--red { border-left: 3px solid var(--danger); }
.readiness-domain--grey { border-left: 3px solid var(--text-muted); }

.readiness-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  margin-right: 0.35rem;
  border-radius: 50%;
  background: var(--text-muted);
}

.readiness-dot--green { background: var(--success); }
.readiness-dot--amber { background: var(--warning); }
.readiness-dot--red { background: var(--danger); }
.readiness-dot--grey { background: var(--text-muted); }

.readiness-domain__head {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  color: var(--text-primary);
  font-size: 0.74rem;
}

.readiness-domain__head span {
  color: var(--text-muted);
  font-size: 0.64rem;
  white-space: nowrap;
}

.readiness-domain__bar {
  height: 6px;
  margin: 0.35rem 0;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.readiness-domain__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--success));
}

.readiness-domain p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.64rem;
}

.readiness-list,
.readiness-samples,
.readiness-deliverables {
  margin: 0;
  padding: 0;
  list-style: none;
}

.readiness-list li {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.45rem 0;
  border-top: 1px solid var(--border-color);
}

.readiness-list li:first-child {
  border-top: 0;
}

.readiness-list strong {
  display: block;
  color: var(--text-primary);
  font-size: 0.74rem;
}

.readiness-list div span {
  display: block;
  color: var(--text-muted);
  font-size: 0.62rem;
}

.readiness-chip {
  flex: 0 0 auto;
  padding: 0.12rem 0.4rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.readiness-chip--have {
  background: var(--success-bg);
  color: var(--success);
}

.readiness-chip--building {
  background: var(--warning-bg);
  color: var(--warning);
}

.readiness-chip--gap,
.readiness-chip--no_evidence {
  background: var(--danger-bg);
  color: var(--danger);
}

.readiness-chip--green {
  background: var(--success-bg);
  color: var(--success);
}

.readiness-chip--amber {
  background: var(--warning-bg);
  color: var(--warning);
}

.readiness-chip--red {
  background: var(--danger-bg);
  color: var(--danger);
}

.readiness-chip--grey {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.readiness-workbooks {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.55rem;
}

.readiness-workbook {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: inherit;
  text-decoration: none;
}

.readiness-workbook:hover {
  border-color: var(--accent);
}

.readiness-workbook--green { border-left: 3px solid var(--success); }
.readiness-workbook--amber { border-left: 3px solid var(--warning); }
.readiness-workbook--red { border-left: 3px solid var(--danger); }
.readiness-workbook--grey { border-left: 3px solid var(--text-muted); }

.readiness-workbook:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.readiness-workbook__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.4rem;
}

.readiness-workbook__track {
  color: var(--accent-text);
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.readiness-workbook strong {
  color: var(--text-primary);
  font-size: 0.76rem;
}

.readiness-workbook span:last-child {
  color: var(--text-muted);
  font-size: 0.62rem;
}

.readiness-workbook__reason {
  margin-top: 0.2rem;
  color: var(--text-secondary) !important;
  font-size: 0.64rem !important;
  line-height: 1.4;
}

.readiness-deliverables {
  margin: 0.5rem 0;
  padding-left: 1.1rem;
  list-style: disc;
}

.readiness-deliverables li {
  margin: 0.2rem 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.readiness-certs {
  display: grid;
  gap: 0.45rem;
}

.readiness-certs span {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
}

.readiness-certs p {
  margin: 0.1rem 0 0;
}

.readiness-note {
  margin: 0.5rem 0 0;
  color: var(--text-muted) !important;
  font-size: 0.64rem !important;
}

.readiness-evidence {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.readiness-evidence div {
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.readiness-evidence strong {
  display: block;
  color: var(--text-primary);
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.readiness-evidence span {
  color: var(--text-muted);
  font-size: 0.62rem;
}

.readiness-samples li {
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
  padding: 0.35rem 0;
  border-top: 1px solid var(--border-color);
  font-size: 0.7rem;
}

.readiness-samples strong {
  color: var(--text-primary);
}

.readiness-samples span {
  color: var(--text-muted);
  font-size: 0.64rem;
}

.readiness-empty {
  margin: 0;
  color: var(--text-muted) !important;
  font-size: 0.72rem !important;
}

@media (max-width: 900px) {
  .readiness__head,
  .readiness-hero {
    grid-template-columns: minmax(0, 1fr);
  }

  .readiness__head {
    flex-direction: column;
  }

  .readiness__select {
    width: 100%;
  }

  .readiness-ring {
    width: 72px;
    height: 72px;
  }
}

@media (max-width: 640px) {
  .readiness-hero {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .readiness-list li,
  .readiness-samples li {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
