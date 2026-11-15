<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <template v-if="name === 'building'">
      <polyline points="16 18 22 12 16 6" />
      <polyline points="8 6 2 12 8 18" />
    </template>
    <template v-else-if="name === 'investigating'">
      <circle cx="11" cy="11" r="7" />
      <line x1="21" y1="21" x2="16.5" y2="16.5" />
    </template>
    <template v-else-if="name === 'breaking'">
      <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8z" />
    </template>
    <template v-else-if="name === 'defending'">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </template>
    <template v-else>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.5 9a2.5 2.5 0 1 1 4 2c-.9.7-1.5 1.2-1.5 2.5" />
      <line x1="12" y1="17" x2="12" y2="17.01" />
    </template>
  </svg>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
})
</script>
