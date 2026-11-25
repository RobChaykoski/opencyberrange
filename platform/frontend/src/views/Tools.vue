<template>
  <div class="tools-page">
    <header class="tools-head">
      <p class="tools-head__eyebrow">One allow-list, one panel</p>
      <h1>Tools</h1>
      <p class="tools-head__lede">
        Every tool below opens in the same sandboxed panel, whether you start
        here, from the sidebar, or from an active lab. A tool never receives your
        platform session. Tools that need the internet say so; the rest work on
        an isolated range.
      </p>
    </header>

    <section class="tools-grid" aria-label="Tool catalogue">
      <article v-for="tool in toolList" :key="tool.key" class="tool-card">
        <div class="tool-card__top">
          <span class="tool-card__icon"><ToolIcon :name="tool.key" /></span>
          <div>
            <p class="tool-card__category">{{ tool.category }}</p>
            <h2>{{ tool.title }}</h2>
          </div>
        </div>

        <p class="tool-card__description">{{ tool.description }}</p>

        <ul class="tool-card__tags" aria-label="Tool properties">
          <li v-for="tag in tool.tags" :key="tag">{{ tag }}</li>
        </ul>

        <p class="tool-card__attribution">{{ tool.attribution }}</p>

        <div class="tool-card__actions">
          <button
            type="button"
            class="btn btn--primary btn--sm"
            :aria-label="`Open ${tool.title} in a panel`"
            @click="openTool(tool.key)"
          >
            Open in panel
          </button>
          <a
            v-if="tool.downloadUrl"
            :href="tool.downloadUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn--secondary btn--sm"
          >
            {{ tool.downloadLabel || 'Open vendor page' }}
          </a>
        </div>
      </article>
    </section>

    <section v-if="zap" class="zap-note" aria-labelledby="zap-note-title">
      <div>
        <p class="tools-head__eyebrow">Web application security</p>
        <h2 id="zap-note-title">ZAP is a desktop scanner, so the panel plans the scan</h2>
        <p>
          The ZAP planner writes a baseline or full-scan command, a report path,
          and a triage checklist. It does not run a scan. Download ZAP for the
          scanner, then run the command against a practice target you are
          authorised to test. A dedicated ZAP lab is the next step in the Web
          application security track; the planner is usable now.
        </p>
      </div>
      <button type="button" class="btn btn--secondary btn--sm" @click="openTool('zap')">
        Open the ZAP planner
      </button>
    </section>

    <section class="tools-how" aria-labelledby="tools-how-title">
      <h2 id="tools-how-title">How tools work here</h2>
      <ul>
        <li>
          <strong>Allow-listed only.</strong> The platform opens a fixed key from
          this catalogue. A route, query string, or learner input cannot supply a
          tool URL.
        </li>
        <li>
          <strong>Sandboxed.</strong> The panel uses a restricted iframe. A
          cross-origin tool gets its own origin; it cannot read the platform
          session or your evidence.
        </li>
        <li>
          <strong>Safe fallback.</strong> If a tool is slow or blocked, the panel
          offers <em>Open in new tab</em>. The exercise stays open behind the
          panel, and closing the panel returns you to it.
        </li>
        <li>
          <strong>Same shortcuts everywhere.</strong> The active-lab toolbar uses
          the same tool keys: CyberChef, OT scan, ATT&amp;CK, and ZAP. One
          behaviour, one set of permissions.
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import ToolIcon from '../components/ToolIcon.vue'
import { useToolPanel } from '../composables/useToolPanel'

const { openTool, toolList } = useToolPanel()
const zap = computed(() => toolList.value.find((tool) => tool.key === 'zap'))
</script>

<style scoped>
.tools-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
  display: grid;
  gap: 1.5rem;
}

.tools-head {
  display: grid;
  gap: 0.35rem;
}

.tools-head__eyebrow {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent-text);
}

.tools-head h1 {
  margin: 0;
  font-size: 2rem;
  color: var(--text-primary);
}

.tools-head__lede {
  margin: 0;
  max-width: 78ch;
  color: var(--text-secondary);
  line-height: 1.6;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.tool-card {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  min-width: 0;
}

.tool-card__top {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
}

.tool-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: var(--accent-bg);
  color: var(--accent-text);
  flex-shrink: 0;
}

.tool-card__category {
  margin: 0 0 0.15rem;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.tool-card h2 {
  margin: 0;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.tool-card__description {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.55;
  color: var(--text-secondary);
}

.tool-card__tags {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.tool-card__tags li {
  padding: 0.12rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.66rem;
  font-weight: 600;
  color: var(--text-muted);
}

.tool-card__attribution {
  margin: 0;
  font-size: 0.72rem;
  line-height: 1.5;
  color: var(--text-muted);
  flex: 1;
}

.tool-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.1rem;
}

.zap-note {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1.1rem 1.25rem;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--accent);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.zap-note h2 {
  margin: 0.2rem 0 0.35rem;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.zap-note p:not(.tools-head__eyebrow) {
  margin: 0;
  max-width: 78ch;
  font-size: 0.86rem;
  line-height: 1.55;
  color: var(--text-secondary);
}

.tools-how {
  padding: 1.1rem 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.tools-how h2 {
  margin: 0 0 0.6rem;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.tools-how ul {
  margin: 0;
  padding-left: 1.1rem;
  display: grid;
  gap: 0.45rem;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.tools-how strong {
  color: var(--text-primary);
}

@media (max-width: 640px) {
  .tools-page {
    padding: 1rem 1rem 2rem;
  }
  .tools-head h1 {
    font-size: 1.65rem;
  }
  .zap-note {
    align-items: flex-start;
  }
}
</style>
