<template>
  <figure class="lab-access" aria-labelledby="lab-access-title">
    <figcaption class="lab-access__head">
      <span class="lab-access__eyebrow">Lab setup</span>
      <strong id="lab-access-title">How you reach this exercise</strong>
    </figcaption>

    <div class="lab-access__entry">
      <div class="lab-access__node">
        <span class="lab-access__kicker">You</span>
        <strong>Browser</strong>
        <small>HTTPS</small>
      </div>
      <span class="lab-access__arrow" aria-hidden="true">&rarr;</span>
      <div class="lab-access__node lab-access__node--platform">
        <span class="lab-access__kicker">Platform</span>
        <strong>OpenCyberRange</strong>
        <small>Not a lab target</small>
      </div>
    </div>

    <div class="lab-access__split">
      <div class="lab-access__path" :class="{ 'lab-access__path--active': hasSession && rangeboxActive }">
        <span class="lab-access__badge">RangeBox</span>
        <strong>Browser desktop</strong>
        <small>Already on the lab network. Nothing to install.</small>
        <span class="lab-access__state">{{ pathState(true) }}</span>
      </div>
      <span class="lab-access__or">or</span>
      <div class="lab-access__path" :class="{ 'lab-access__path--active': hasSession && !rangeboxActive }">
        <span class="lab-access__badge">VPN</span>
        <strong>Your own Kali / Ubuntu VM</strong>
        <small>The tunnel puts your VM on the same lab network.</small>
        <span class="lab-access__state">{{ pathState(false) }}</span>
      </div>
    </div>

    <p class="lab-access__merge">Both paths land on the same isolated network</p>

    <div class="lab-access__network">
      <div class="lab-access__network-head">
        <strong>Lab network</strong>
        <code>{{ subnet }}</code>
      </div>
      <div v-if="targets.length" class="lab-access__targets">
        <div v-for="target in targets" :key="target.id || target.ip" class="lab-access__target">
          <span class="lab-access__device">{{ deviceLabel(target) }}</span>
          <strong>{{ target.label || target.id || 'Target' }}</strong>
          <code>{{ target.ip }}</code>
        </div>
      </div>
      <div v-else-if="devices.length" class="lab-access__targets">
        <div v-for="device in devices" :key="device.id || device.label" class="lab-access__target">
          <span class="lab-access__device">{{ deviceLabel(device) }}</span>
          <strong>{{ device.label || device.id || 'Device' }}</strong>
          <code>IP hidden in RangeBox</code>
        </div>
      </div>
      <p v-else class="lab-access__empty">
        <template v-if="rangeboxActive">
          Target IPs are hidden in RangeBox mode. Use the desktop or the target
          hostnames shown below.
        </template>
        <template v-else>
          Scan the lab subnet to discover the devices. Only the addresses shown
          by the platform are in scope.
        </template>
      </p>
    </div>

    <p class="lab-access__rule">
      Run commands inside RangeBox or your VPN-connected VM. The platform page
      and the platform host are not targets.
    </p>
  </figure>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  session: { type: Object, default: null },
  targets: { type: Array, default: () => [] },
  devices: { type: Array, default: () => [] },
})

const subnet = computed(() => props.session?.network_subnet || '10.100.x.0/24')
const rangeboxActive = computed(() => Boolean(props.session?.rangebox_enabled))
const hasSession = computed(() => Boolean(props.session))

function pathState(isRangebox) {
  if (!hasSession.value) return 'One of two paths'
  return isRangebox === rangeboxActive.value ? 'Active for this session' : 'Optional path'
}

const DEVICE_LABELS = {
  server: 'Server',
  workstation: 'Workstation',
  router: 'Router',
  firewall: 'Firewall',
  database: 'Database',
  sensor: 'Sensor',
}

function deviceLabel(target) {
  const type = String(target?.type || '').toLowerCase()
  return DEVICE_LABELS[type] || 'Device'
}
</script>

<style scoped>
.lab-access {
  margin: 0.75rem 0 1rem;
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.lab-access__head {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.lab-access__eyebrow {
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.lab-access__entry {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.lab-access__node {
  display: flex;
  min-width: 9rem;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  text-align: center;
}

.lab-access__node--platform {
  border-color: var(--accent);
}

.lab-access__kicker {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.lab-access__node strong {
  color: var(--text-primary);
  font-size: 0.82rem;
}

.lab-access__node small {
  color: var(--text-secondary);
  font-size: 0.7rem;
}

.lab-access__arrow {
  color: var(--accent);
  font-size: 1.2rem;
  font-weight: 800;
}

.lab-access__split {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: stretch;
  gap: 0.5rem;
  margin-top: 0.65rem;
}

.lab-access__path {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.65rem 0.7rem;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.lab-access__path--active {
  border-style: solid;
  border-color: var(--accent);
}

.lab-access__badge {
  align-self: flex-start;
  padding: 0.08rem 0.35rem;
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--accent);
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.lab-access__path strong {
  color: var(--text-primary);
  font-size: 0.8rem;
}

.lab-access__path small {
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.4;
}

.lab-access__state {
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 700;
}

.lab-access__or {
  align-self: center;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.lab-access__merge {
  margin: 0.55rem 0 0.35rem;
  color: var(--text-muted);
  font-size: 0.68rem;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.lab-access__network {
  padding: 0.65rem 0.7rem 0.75rem;
  border: 1px dashed var(--accent);
  border-radius: 8px;
  background: var(--bg-primary);
}

.lab-access__network-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.lab-access__network-head strong {
  color: var(--text-primary);
  font-size: 0.8rem;
}

.lab-access__network-head code,
.lab-access__target code {
  color: var(--text-secondary);
  font-size: 0.7rem;
}

.lab-access__targets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: 0.4rem;
}

.lab-access__target {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
}

.lab-access__target strong {
  color: var(--text-primary);
  font-size: 0.74rem;
}

.lab-access__device {
  color: var(--accent);
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.lab-access__empty {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.45;
}

.lab-access__rule {
  margin: 0.65rem 0 0;
  padding-top: 0.55rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .lab-access__split {
    grid-template-columns: 1fr;
  }

  .lab-access__or {
    display: none;
  }
}
</style>
