<template>
  <section
    v-if="roles.length"
    class="target-role"
    :class="`target-role--${variant}`"
    aria-labelledby="target-role-title"
  >
    <div class="target-role__copy">
      <p class="target-role__eyebrow">Career target</p>
      <h2 id="target-role-title" class="target-role__title">
        Aiming for {{ selectedTitle }}
      </h2>
      <p class="target-role__help">
        Readiness, the skills gap, and aligned evidence follow this role. Change it
        whenever your direction changes.
      </p>
    </div>
    <div class="target-role__controls">
      <label class="target-role__label" for="target-role-select">Target role</label>
      <select
        id="target-role-select"
        v-model="selectedRole"
        class="target-role__select"
        @change="setGoal(selectedRole)"
      >
        <option v-for="role in roles" :key="role.id" :value="role.id">
          {{ role.title }}{{ role.flagship ? ' (flagship)' : '' }}
        </option>
      </select>
      <router-link v-if="variant === 'band'" to="/profile?tab=careers" class="target-role__link">
        Open readiness &rarr;
      </router-link>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useCareerGoal } from '../composables/useCareerGoal'
import { useCareerRoles } from '../composables/useCareerRoles'

defineProps({
  variant: {
    type: String,
    default: 'band',
    validator: (value) => ['band', 'inline'].includes(value),
  },
})

const { selectedRole, setGoal } = useCareerGoal()
const { roles, load } = useCareerRoles()

const selectedTitle = computed(
  () => roles.value.find((role) => role.id === selectedRole.value)?.title || 'your target role'
)

function choosePreferredRole() {
  const preferred =
    roles.value.find((role) => role.id === selectedRole.value) ||
    roles.value.find((role) => role.id === 'soc-analyst') ||
    roles.value.find((role) => role.flagship) ||
    roles.value[0]
  if (preferred && preferred.id !== selectedRole.value) setGoal(preferred.id)
}

onMounted(async () => {
  try {
    await load()
    choosePreferredRole()
  } catch {
    // The pathway catalogue is optional. Hide the switcher rather than show a
    // broken control when the deployment has the portfolio feature disabled.
    roles.value = []
  }
})
</script>

<style scoped>
.target-role {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.9rem 1.25rem;
  border: 1px solid var(--border-color);
  background:
    radial-gradient(circle at 0% 0%, var(--accent-bg), transparent 60%),
    var(--bg-secondary);
}

.target-role--band {
  margin: 1rem 0;
  padding: 0.9rem 1.1rem;
  border-radius: 12px;
}

.target-role--inline {
  margin: 0 0 1rem;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
}

.target-role__copy {
  min-width: 0;
}

.target-role__eyebrow {
  margin: 0 0 0.15rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.target-role__title {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.98rem;
  line-height: 1.3;
}

.target-role__help {
  margin: 0.2rem 0 0;
  max-width: 46rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.45;
}

.target-role__controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 0 0 auto;
}

.target-role__label {
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}

.target-role__select {
  min-height: 34px;
  max-width: 16rem;
  padding: 0.3rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.82rem;
}

.target-role__select:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.target-role__link {
  color: var(--accent-text);
  font-size: 0.78rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
}

.target-role__link:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .target-role__controls {
    width: 100%;
    flex-wrap: wrap;
  }

  .target-role__select {
    flex: 1 1 12rem;
    max-width: none;
  }
}
</style>
