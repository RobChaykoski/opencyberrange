<template>
  <nav class="mobile-tabbar" aria-label="Student navigation">
    <router-link
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="mobile-tabbar__item"
      :class="{ 'mobile-tabbar__item--active': isActive(item) }"
      :aria-current="isActive(item) ? 'page' : undefined"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <template v-if="item.icon === 'dashboard'">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
        </template>
        <template v-else-if="item.icon === 'exercises'">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20V22H6.5A2.5 2.5 0 0 1 4 19.5V4.5A2.5 2.5 0 0 1 6.5 2Z" />
        </template>
        <template v-else-if="item.icon === 'rangebox'">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
          <line x1="8" y1="21" x2="16" y2="21" />
          <line x1="12" y1="17" x2="12" y2="21" />
        </template>
        <template v-else-if="item.icon === 'courses'">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
        </template>
        <template v-else-if="item.icon === 'profile'">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </template>
      </svg>
      <span>{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { to: '/dashboard', label: 'Home', icon: 'dashboard' },
  { to: '/exercises', label: 'Exercises', icon: 'exercises' },
  { to: '/rangebox', label: 'RangeBox', icon: 'rangebox' },
  { to: '/courses', label: 'Courses', icon: 'courses' },
  { to: '/profile', label: 'Profile', icon: 'profile' },
]

const isActive = (item) => {
  if (item.to === '/dashboard') return route.path === '/dashboard'
  return route.path === item.to || route.path.startsWith(`${item.to}/`)
}
</script>

<style scoped>
.mobile-tabbar {
  display: none;
}

@media (max-width: 768px) {
  .mobile-tabbar {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 180;
    display: flex;
    align-items: stretch;
    justify-content: space-around;
    gap: 0.25rem;
    padding: 0.3rem 0.35rem calc(0.3rem + env(safe-area-inset-bottom));
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    box-shadow: 0 -8px 24px rgba(2, 6, 23, 0.18);
  }

  .mobile-tabbar__item {
    flex: 1 1 0;
    min-width: 0;
    min-height: 44px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.15rem;
    padding: 0.3rem 0.2rem;
    border-radius: 10px;
    color: var(--text-muted);
    text-decoration: none;
    font-size: 0.68rem;
    font-weight: 600;
    line-height: 1.1;
  }

  .mobile-tabbar__item svg {
    width: 20px;
    height: 20px;
  }

  .mobile-tabbar__item--active {
    color: var(--accent);
    background: var(--accent-bg);
  }

  .mobile-tabbar__item:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
}
</style>
