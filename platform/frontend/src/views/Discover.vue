<template>
  <div class="discover">
    <div class="discover__panel">
      <header class="discover__head">
        <p class="discover__eyebrow">New to the range?</p>
        <h1 class="discover__title">Discover your Cyber DNA</h1>
        <p class="discover__lede">
          You do not need to know which certification to chase. Pick what you
          naturally enjoy; we will start you with three short exercises and
          build the rest from your evidence.
        </p>
      </header>

      <div class="discover__layout">
      <section v-if="step === 'choose'" aria-labelledby="interest-heading">
        <h2 id="interest-heading" class="discover__section-title">What do you enjoy doing?</h2>
        <div class="interest-grid">
          <button
            v-for="interest in interests"
            :key="interest.key"
            type="button"
            class="interest"
            :class="{ 'interest--selected': selectedKey === interest.key }"
            @click="choose(interest)"
          >
            <span class="interest__icon" aria-hidden="true"><DiscoverIcon :name="interest.key" /></span>
            <span class="interest__body">
              <span class="interest__title">{{ interest.title }}</span>
              <span class="interest__copy">{{ interest.copy }}</span>
            </span>
          </button>
        </div>
        <button type="button" class="discover__skip" @click="skip">
          I would rather explore on my own
        </button>
      </section>

      <section v-else aria-labelledby="path-heading">
        <div class="discover__path-head">
          <div>
            <p class="discover__eyebrow">Your starter path</p>
            <h2 id="path-heading" class="discover__section-title">{{ selected.title }}</h2>
            <p class="discover__copy">{{ selected.pathCopy }}</p>
          </div>
          <button type="button" class="btn btn--outline btn--sm" @click="step = 'choose'">
            Change
          </button>
        </div>

        <ol class="starter-list">
          <li v-for="(lab, index) in selected.labs" :key="lab.slug" class="starter">
            <span class="starter__index" aria-hidden="true">{{ index + 1 }}</span>
            <div class="starter__body">
              <p class="starter__track">{{ lab.trackName }}</p>
              <h3 class="starter__title">{{ lab.title }}</h3>
              <p class="starter__meta">{{ lab.minutes }} min · beginner · workbook included</p>
            </div>
            <router-link :to="`/exercises/${lab.trackSlug}`" class="btn btn--primary btn--sm">
              Open track
            </router-link>
          </li>
        </ol>

        <div class="discover__note">
          <strong>Why three?</strong>
          One completion is an accident, three is a pattern. After three
          exercises you unlock the Cyber DNA report, Career GPS confidence, and
          the growth-velocity view.
        </div>

        <div class="discover__actions">
          <router-link :to="`/exercises/${selected.labs[0].trackSlug}`" class="btn btn--primary">
            Start challenge 1
          </router-link>
          <button type="button" class="btn btn--ghost" @click="skip">Skip for now</button>
        </div>
      </section>

      <aside class="discover__why" aria-labelledby="why-heading">
        <p class="discover__eyebrow">The path</p>
        <h2 id="why-heading" class="discover__why-title">What you unlock</h2>
        <ol class="why-list">
          <li>
            <strong>Three starter challenges</strong>
            <span>Short exercises from different tracks, so the evidence is not one-note.</span>
          </li>
          <li>
            <strong>Cyber DNA report</strong>
            <span>Six practice traits, a class, and your strongest branch. Unlocks at three completions.</span>
          </li>
          <li>
            <strong>Career GPS</strong>
            <span>Directions, not verdicts. Named roles appear only after eight pieces of evidence.</span>
          </li>
          <li>
            <strong>Pathway and transcript</strong>
            <span>A recommended track, achievements with evidence, and an export you can show an employer.</span>
          </li>
        </ol>
        <p class="discover__why-note">
          Your profile is private. It is never ranked, and instructors see aggregates, not your
          individual growth.
        </p>
      </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import DiscoverIcon from '../components/DiscoverIcon.vue'

const router = useRouter()
const step = ref('choose')
const selectedKey = ref('')
const selected = ref(null)

const interests = [
  {
    key: 'building',
    title: 'I like building things',
    copy: 'Code, automation, secure design, and making something work.',
    pathCopy: 'Start with code and design, then see how applications fail.',
    labs: [
      { slug: 'software-security-1-1-hidden-export-route', title: 'Hidden Export Route', trackName: 'Software Security', trackSlug: 'software-security', minutes: 15 },
      { slug: 'web-1-1-basic-directory-enumeration', title: 'Basic Directory Enumeration', trackName: 'Web Application Security', trackSlug: 'web', minutes: 120 },
      { slug: 'ai-1-1-prompt-injection-basics', title: 'Prompt Injection Basics', trackName: 'AI Hacking', trackSlug: 'ai', minutes: 35 },
    ],
  },
  {
    key: 'investigating',
    title: 'I like investigating',
    copy: 'Following evidence, reading logs, and piecing together what happened.',
    pathCopy: 'Start with evidence: memory, public footprint, and a suspicious file.',
    labs: [
      { slug: 'forensics-1-1-windows-memory-volatility', title: 'Windows Memory Analysis with Volatility', trackName: 'Digital Forensics', trackSlug: 'forensics', minutes: 50 },
      { slug: 'osint-1-1-public-footprint', title: 'The Public Footprint', trackName: 'OSINT', trackSlug: 'osint', minutes: 35 },
      { slug: 'malware-1-1-eicar-triage', title: 'Suspicious Attachment Triage', trackName: 'Malware Analysis', trackSlug: 'malware', minutes: 45 },
    ],
  },
  {
    key: 'breaking',
    title: 'I like breaking things',
    copy: 'Finding the weak path, proving impact, and documenting the route.',
    pathCopy: 'Start with the classic offensive path across web, Linux, and Windows.',
    labs: [
      { slug: 'web-1-1-basic-directory-enumeration', title: 'Basic Directory Enumeration', trackName: 'Web Application Security', trackSlug: 'web', minutes: 120 },
      { slug: 'linux-1-1-ssh-service-detection', title: 'SSH Service Detection', trackName: 'Linux Fundamentals', trackSlug: 'linux', minutes: 120 },
      { slug: 'windows-1-1-basic-port-scan', title: 'Basic Windows Port Scan', trackName: 'Windows Penetration Testing', trackSlug: 'windows', minutes: 120 },
    ],
  },
  {
    key: 'defending',
    title: 'I like defending systems',
    copy: 'Detection, hardening, identity, and keeping the range healthy.',
    pathCopy: 'Start with traffic, authentication, and the evidence defenders use.',
    labs: [
      { slug: 'network-1-1-packet-capture-analysis', title: 'Suspicious Traffic Analysis', trackName: 'Network Security', trackSlug: 'network', minutes: 60 },
      { slug: 'identity-1-1-secure-authentication', title: 'Secure Authentication', trackName: 'Identity & Access', trackSlug: 'identity', minutes: 45 },
      { slug: 'forensics-1-1-windows-memory-volatility', title: 'Windows Memory Analysis with Volatility', trackName: 'Digital Forensics', trackSlug: 'forensics', minutes: 50 },
    ],
  },
  {
    key: 'unsure',
    title: 'I do not know yet',
    copy: 'That is normal. Try one exercise from three different worlds.',
    pathCopy: 'Sample a broad set and let the evidence point to a direction.',
    labs: [
      { slug: 'linux-1-1-ssh-service-detection', title: 'SSH Service Detection', trackName: 'Linux Fundamentals', trackSlug: 'linux', minutes: 120 },
      { slug: 'network-1-1-packet-capture-analysis', title: 'Suspicious Traffic Analysis', trackName: 'Network Security', trackSlug: 'network', minutes: 60 },
      { slug: 'web-1-1-basic-directory-enumeration', title: 'Basic Directory Enumeration', trackName: 'Web Application Security', trackSlug: 'web', minutes: 120 },
    ],
  },
]

async function save(payload) {
  try {
    const { data } = await api.get('/auth/settings')
    const prefs = {
      ...(data?.notification_prefs || {}),
      dna_onboarding_v1: {
        schema: 1,
        ...payload,
        chosen_at: new Date().toISOString(),
      },
    }
    await api.put('/auth/settings', { notification_prefs: prefs })
  } catch {
    // The flow still works if the preference cannot be stored; the dashboard
    // will offer the same entry point.
  }
}

async function choose(interest) {
  selectedKey.value = interest.key
  selected.value = interest
  await save({
    interest: interest.key,
    tracks: interest.labs.map((lab) => lab.trackSlug),
    labs: interest.labs.map((lab) => ({ slug: lab.slug, track: lab.trackSlug, title: lab.title })),
    skipped: false,
  })
  step.value = 'path'
}

async function skip() {
  await save({ interest: 'unsure', tracks: [], labs: [], skipped: true })
  router.push('/dashboard')
}
</script>

<style scoped>
.discover {
  min-height: 100vh;
  padding: 3rem 1.25rem 4rem;
  background:
    radial-gradient(1100px 500px at 50% -10%, rgba(37, 99, 235, 0.18), transparent 70%),
    var(--bg-primary);
  color: var(--text-primary);
}
.discover__panel {
  max-width: 980px;
  margin: 0 auto;
}
.discover__head {
  max-width: 720px;
  margin-bottom: 2rem;
}
.discover__eyebrow {
  margin: 0 0 0.5rem;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
}
.discover__title {
  margin: 0 0 0.75rem;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.1;
}
.discover__lede,
.discover__copy {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 70ch;
}
.discover__section-title {
  margin: 1.5rem 0 1rem;
  font-size: 1.1rem;
  letter-spacing: 0.01em;
}
.interest-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.75rem;
}
.interest {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  text-align: left;
  padding: 1rem;
  border-radius: 0.6rem;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: inherit;
  cursor: pointer;
  transition: border-color 120ms, transform 120ms, background 120ms;
}
.interest:hover,
.interest:focus-visible {
  border-color: var(--accent);
  transform: translateY(-1px);
  outline: none;
}
.interest--selected {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent) inset;
}
.interest__icon {
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 0.5rem;
  background: var(--accent-bg);
  color: var(--accent);
}
.interest__icon :deep(svg) {
  width: 22px;
  height: 22px;
}
.interest__body {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.interest__title {
  font-weight: 700;
}
.interest__copy {
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.45;
}
.discover__skip {
  margin-top: 1.25rem;
  background: none;
  border: 0;
  padding: 0;
  color: var(--text-secondary);
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.85rem;
}
.discover__path-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}
.starter-list {
  list-style: none;
  margin: 1.25rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.starter {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 0.6rem;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
}
.starter__index {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 700;
  flex: 0 0 2rem;
}
.starter__body {
  flex: 1;
  min-width: 0;
}
.starter__track {
  margin: 0;
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.starter__title {
  margin: 0.15rem 0;
  font-size: 1rem;
}
.starter__meta {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-secondary);
}
.discover__note {
  margin-top: 1.25rem;
  padding: 0.9rem 1rem;
  border-left: 3px solid var(--accent);
  background: var(--bg-secondary);
  border-radius: 0 0.4rem 0.4rem 0;
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.5;
}
.discover__note strong {
  color: var(--text-primary);
}
.discover__actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}
.discover__layout {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(0, 1fr);
  gap: 2rem;
  align-items: start;
}
.discover__why {
  padding: 1.1rem 1.2rem;
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  background: var(--bg-secondary);
}
.discover__why-title {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
}
.why-list {
  list-style: none;
  counter-reset: why;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.why-list li {
  counter-increment: why;
  position: relative;
  padding-left: 2.25rem;
  font-size: 0.85rem;
}
.why-list li::before {
  content: counter(why);
  position: absolute;
  left: 0;
  top: 0;
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 700;
  font-size: 0.75rem;
}
.why-list strong {
  display: block;
  margin-bottom: 0.15rem;
}
.why-list span {
  color: var(--text-secondary);
  line-height: 1.45;
}
.discover__why-note {
  margin: 1rem 0 0;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.76rem;
  line-height: 1.45;
}
@media (max-width: 900px) {
  .discover__layout {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .starter {
    flex-wrap: wrap;
  }
  .starter .btn {
    width: 100%;
  }
}
</style>
