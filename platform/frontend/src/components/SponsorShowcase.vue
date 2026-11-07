<template>
  <section v-if="sponsors && sponsors.length" class="sponsor-showcase" aria-label="Event sponsors">
    <div class="sponsor-showcase__head">
      <span class="sponsor-showcase__eyebrow">Sponsored by</span>
      <span class="sponsor-showcase__count">
        {{ sponsors.length }} {{ sponsors.length === 1 ? 'partner' : 'partners' }}
      </span>
    </div>
    <div class="sponsor-grid">
      <article
        v-for="sponsor in sponsors"
        :key="sponsor.id || sponsor.name"
        class="sponsor-card"
        :class="`sponsor-card--${sponsor.tier || 'gold'}`"
      >
        <div class="sponsor-card__mark">
          <img v-if="sponsor.logo_data" :src="sponsor.logo_data" :alt="`${sponsor.name} logo`" />
          <span v-else aria-hidden="true">{{ initials(sponsor.name) }}</span>
        </div>
        <div class="sponsor-card__body">
          <span class="sponsor-card__tier">{{ tierLabel(sponsor.tier) }}</span>
          <strong class="sponsor-card__name">{{ sponsor.name }}</strong>
          <p v-if="sponsor.description" class="sponsor-card__description">
            {{ sponsor.description }}
          </p>
          <a
            v-if="sponsor.website_url"
            :href="sponsor.website_url"
            target="_blank"
            rel="noopener noreferrer"
            class="sponsor-card__link"
          >
            Visit website
            <span aria-hidden="true">↗</span>
          </a>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  sponsors: { type: Array, default: () => [] },
})

const tierLabel = (tier) => ({
  gold: 'Gold sponsor',
  silver: 'Silver sponsor',
  bronze: 'Bronze sponsor',
}[tier] || 'Sponsor')

const initials = (name) => {
  const words = String(name || '?').trim().split(/\s+/).filter(Boolean)
  if (!words.length) return '?'
  if (words.length === 1) return Array.from(words[0]).slice(0, 2).join('').toUpperCase()
  return `${Array.from(words[0])[0]}${Array.from(words[words.length - 1])[0]}`.toUpperCase()
}
</script>

<style scoped>
.sponsor-showcase {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background:
    radial-gradient(circle at 100% 0%, rgba(234, 179, 8, 0.1), transparent 55%),
    var(--bg-secondary);
}

.sponsor-showcase__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.7rem;
}

.sponsor-showcase__eyebrow {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.sponsor-showcase__count {
  color: var(--text-muted);
  font-size: 0.66rem;
}

.sponsor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 0.6rem;
}

.sponsor-card {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  padding: 0.75rem 0.85rem;
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.sponsor-card__mark {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-radius: 9px;
  background: var(--bg-secondary);
  color: var(--sponsor-accent, #d4a017);
  font-size: 0.78rem;
  font-weight: 800;
}

.sponsor-card__mark img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 3px;
}

.sponsor-card__body {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.15rem;
}

.sponsor-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--sponsor-accent, #d4a017);
}

.sponsor-card--gold { --sponsor-accent: #d4a017; }
.sponsor-card--silver { --sponsor-accent: #94a3b8; }
.sponsor-card--bronze { --sponsor-accent: #b87333; }

.sponsor-card__tier {
  color: var(--sponsor-accent, #d4a017);
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.sponsor-card__name {
  color: var(--text-primary);
  font-size: 0.9rem;
  line-height: 1.25;
}

.sponsor-card__description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
  line-height: 1.45;
}

.sponsor-card__link {
  margin-top: 0.15rem;
  color: var(--accent);
  font-size: 0.66rem;
  font-weight: 700;
  text-decoration: none;
}

.sponsor-card__link:hover {
  text-decoration: underline;
}
</style>
