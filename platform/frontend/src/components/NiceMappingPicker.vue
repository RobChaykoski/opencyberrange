<template>
  <section class="nice-picker" aria-labelledby="nice-picker-title">
    <div class="nice-picker__head">
      <div>
        <h4 id="nice-picker-title">NICE Framework mapping</h4>
        <p>
          Select the work roles, tasks, knowledge, and skills this lab exercises.
          Codes come from the installed NICE Framework and are validated on save.
        </p>
      </div>
      <span v-if="framework.version" class="nice-picker__version">
        NICE {{ framework.version }}
      </span>
    </div>

    <p v-if="error" class="nice-picker__error" role="alert">{{ error }}</p>

    <div v-for="config in configs" :key="config.type" class="nice-picker__group">
      <label :for="`nice-search-${config.type}`">{{ config.label }}</label>
      <div v-if="selected[config.type].length" class="nice-picker__chips">
        <span v-for="code in selected[config.type]" :key="code" class="nice-picker__chip">
          <code>{{ code }}</code>
          <span>{{ detailFor(code) }}</span>
          <button type="button" :aria-label="`Remove ${code}`" @click="remove(config.type, code)">×</button>
        </span>
      </div>
      <input
        :id="`nice-search-${config.type}`"
        v-model="search[config.type]"
        class="form-input form-input--sm"
        type="search"
        :placeholder="config.placeholder"
        autocomplete="off"
        @input="onSearch(config.type)"
      />
      <p v-if="loading[config.type]" class="nice-picker__hint">Searching…</p>
      <p v-else-if="!results[config.type].length && search[config.type].trim()" class="nice-picker__hint">
        No matches.
      </p>
      <p v-else-if="!results[config.type].length && config.type !== 'work_role' && !selected.work_role.length" class="nice-picker__hint">
        Choose a work role first, or type at least two characters.
      </p>
      <ul v-if="results[config.type].length" class="nice-picker__results">
        <li v-for="item in results[config.type]" :key="`${item.type}-${item.code}`">
          <button type="button" @click="add(config.type, item)">
            <code>{{ item.code }}</code>
            <span>{{ item.name || item.statement }}</span>
          </button>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ work_role: [], task: [], knowledge: [], skill: [] }),
  },
})
const emit = defineEmits(['update:modelValue'])

const configs = [
  {
    type: 'work_role',
    label: 'Work roles',
    placeholder: 'Search work roles, e.g. defensive',
  },
  {
    type: 'task',
    label: 'Tasks',
    placeholder: 'Search tasks, e.g. analyze alerts',
  },
  {
    type: 'knowledge',
    label: 'Knowledge',
    placeholder: 'Search knowledge statements',
  },
  {
    type: 'skill',
    label: 'Skills',
    placeholder: 'Search skill statements',
  },
]

const framework = reactive({ version: '', error: '' })
const error = ref('')
const search = reactive({ work_role: '', task: '', knowledge: '', skill: '' })
const results = reactive({ work_role: [], task: [], knowledge: [], skill: [] })
const loading = reactive({ work_role: false, task: false, knowledge: false, skill: false })
const details = reactive({})
const timers = {}

const selected = reactive({
  work_role: [...(props.modelValue?.work_role || [])],
  task: [...(props.modelValue?.task || [])],
  knowledge: [...(props.modelValue?.knowledge || [])],
  skill: [...(props.modelValue?.skill || [])],
})

const detailFor = (code) => details[code]?.name || details[code]?.statement || ''

const emitSelection = () => {
  emit('update:modelValue', {
    work_role: [...selected.work_role],
    task: [...selected.task],
    knowledge: [...selected.knowledge],
    skill: [...selected.skill],
  })
}

const load = async (type) => {
  const text = search[type].trim()
  if (type !== 'work_role' && !text && !selected.work_role.length) {
    results[type] = []
    return
  }
  loading[type] = true
  try {
    const params = { component_type: type, limit: 20 }
    if (text) params.q = text
    if (type !== 'work_role' && selected.work_role.length) {
      params.work_role = selected.work_role[0]
    }
    const { data } = await axios.get('/nice/components', { params })
    results[type] = data.items || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load NICE components.'
  } finally {
    loading[type] = false
  }
}

const onSearch = (type) => {
  clearTimeout(timers[type])
  timers[type] = setTimeout(() => load(type), 250)
}

const add = (type, item) => {
  if (!selected[type].includes(item.code)) {
    selected[type].push(item.code)
    details[item.code] = item
    emitSelection()
    if (type === 'work_role') {
      for (const linked of ['task', 'knowledge', 'skill']) load(linked)
    }
  }
}

const remove = (type, code) => {
  selected[type] = selected[type].filter((item) => item !== code)
  delete details[code]
  emitSelection()
  if (type === 'work_role') {
    for (const linked of ['task', 'knowledge', 'skill']) load(linked)
  }
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/nice/status')
    framework.version = data.version || ''
    framework.error = data.installed ? '' : 'NICE data is not installed yet.'
    if (!data.installed) error.value = framework.error
  } catch {
    error.value = 'NICE status is unavailable.'
  }
  await load('work_role')
})
</script>

<style scoped>
.nice-picker {
  margin-top: 0.85rem;
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.nice-picker__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.nice-picker__head h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.86rem;
}

.nice-picker__head p {
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.45;
}

.nice-picker__version {
  flex: 0 0 auto;
  padding: 0.15rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
}

.nice-picker__group {
  display: grid;
  gap: 0.3rem;
  margin-top: 0.6rem;
}

.nice-picker__group > label {
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 700;
}

.nice-picker__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.nice-picker__chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  max-width: 100%;
  padding: 0.15rem 0.35rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.68rem;
}

.nice-picker__chip code {
  color: var(--accent-text);
  font-size: 0.66rem;
}

.nice-picker__chip span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nice-picker__chip button {
  border: 0;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.9rem;
  line-height: 1;
}

.nice-picker__results {
  display: grid;
  gap: 0.15rem;
  max-height: 11rem;
  margin: 0.1rem 0 0;
  padding: 0;
  overflow-y: auto;
  list-style: none;
}

.nice-picker__results button {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  width: 100%;
  padding: 0.25rem 0.35rem;
  border: 0;
  border-radius: 5px;
  background: transparent;
  color: var(--text-secondary);
  text-align: left;
  cursor: pointer;
  font-size: 0.7rem;
}

.nice-picker__results button:hover {
  background: var(--hover-bg);
}

.nice-picker__results code {
  flex: 0 0 auto;
  color: var(--accent-text);
  font-size: 0.66rem;
}

.nice-picker__hint,
.nice-picker__error {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.nice-picker__error {
  color: var(--danger);
}
</style>
